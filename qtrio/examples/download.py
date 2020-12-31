"""Thanks to njsmith for developing Trio guest mode and sharing the first example
integration with Qt.
"""
import contextlib
import math
import os
import time
import typing

import attr
import httpcore._async.http11
import httpx
import hyperlink
import qtrio
import trio

import qtrio.dialogs


# Default is 4096
httpcore._async.http11.AsyncHTTP11Connection.READ_NUM_BYTES = 100_000


def create_title(specific: str) -> str:
    return f"QTrio Download Example - {specific}"


@attr.s(auto_attribs=True, frozen=True)
class Progress:
    downloaded: int
    total: typing.Optional[int]
    first: bool


async def main(
    url: typing.Optional[typing.Union[str, hyperlink.URL]],
    destination: typing.Optional[typing.Union[str, os.PathLike]],
    fps: int = 60,
    text_input_dialog: typing.Optional[qtrio.dialogs.TextInputDialog] = None,
    file_dialog: typing.Optional[qtrio.dialogs.FileDialog] = None,
    progress_dialog: typing.Optional[qtrio.dialogs.ProgressDialog] = None,
    message_box: typing.Optional[qtrio.dialogs.MessageBox] = None,
    clock: typing.Callable[[], float] = time.monotonic,
    http_application: typing.Optional[typing.Callable[..., typing.Any]] = None,
) -> None:
    print("file dialog right inside", id(file_dialog), file_dialog, flush=True)
    converted_url: hyperlink.URL
    converted_destination: trio.Path

    with contextlib.suppress(qtrio.UserCancelledError):
        if url is None:
            if text_input_dialog is None:  # pragma: no cover
                text_input_dialog = qtrio.dialogs.create_text_input_dialog()

            text_input_dialog.title = create_title("Enter URL")
            text_input_dialog.label = "URL to download:"

            url = await text_input_dialog.wait()

        if isinstance(url, str):
            converted_url = hyperlink.URL.from_text(url)
        else:
            converted_url = url

        if destination is None:
            if file_dialog is None:  # pragma: no cover
                file_dialog = qtrio.dialogs.create_file_save_dialog()

            file_dialog.default_file = trio.Path(converted_url.path[-1])

            destination = await file_dialog.wait()

        converted_destination = trio.Path(destination)

        await get_dialog(
            url=converted_url,
            destination=converted_destination,
            fps=fps,
            progress_dialog=progress_dialog,
            message_box=message_box,
            clock=clock,
            http_application=http_application,
        )


async def get_dialog(
    url: hyperlink.URL,
    destination: trio.Path,
    fps: float,
    progress_dialog: typing.Optional[qtrio.dialogs.ProgressDialog] = None,
    message_box: typing.Optional[qtrio.dialogs.MessageBox] = None,
    clock: typing.Callable[[], float] = time.monotonic,
    http_application: typing.Optional[typing.Callable[..., typing.Any]] = None,
) -> None:
    if progress_dialog is None:  # pragma: no cover
        progress_dialog = qtrio.dialogs.create_progress_dialog()

    progress_dialog.title = create_title("Fetching")
    progress_dialog.text = f"Fetching {url}..."

    async with progress_dialog.manage():
        if progress_dialog.dialog is None:  # pragma: no cover
            raise qtrio.InternalError("Dialog not assigned while it is being managed.")

        # Always show the dialog
        progress_dialog.dialog.setMinimumDuration(0)

        start = clock()

        async for progress in get(
            url=url,
            destination=destination,
            update_period=1 / fps,
            http_application=http_application,
        ):
            if progress.first:
                if progress.total is None:
                    maximum = 0
                else:
                    maximum = progress.total

                progress_dialog.dialog.setMaximum(maximum)
                progress_dialog.dialog.setValue(0)

            if progress.total is not None:
                progress_dialog.dialog.setValue(progress.downloaded)

        end = clock()

    duration = end - start
    if duration == 0:
        # define this seems to happen when testing on Windows with an x86 Python
        if progress.downloaded > 0:
            bytes_per_second = math.inf
        else:  # pragma: no cover
            bytes_per_second = 0
    else:
        bytes_per_second = progress.downloaded / duration

    summary = "\n\n".join(
        [
            url.asText(),
            os.fspath(destination),
            f"Downloaded {progress.downloaded} bytes in {duration:.2f} seconds",
            f"{bytes_per_second:.2f} bytes/second",
        ]
    )

    if message_box is None:  # pragma: no cover
        message_box = qtrio.dialogs.create_message_box()

    message_box.title = create_title("Download Summary")
    message_box.text = summary

    await message_box.wait()


async def get(
    url: hyperlink.URL,
    destination: trio.Path,
    update_period: float,
    clock: typing.Callable[[], float] = time.monotonic,
    http_application: typing.Optional[typing.Callable[..., typing.Any]] = None,
) -> typing.AsyncIterable[Progress]:
    async with httpx.AsyncClient(app=http_application) as client:
        async with client.stream("GET", url.asText()) as response:
            raw_content_length = response.headers.get("content-length")
            if raw_content_length is None:
                content_length = None
            else:
                content_length = int(raw_content_length)

            progress = Progress(
                downloaded=0,
                total=content_length,
                first=True,
            )

            yield progress
            last_update = clock()

            progress = attr.evolve(progress, first=False)

            downloaded = 0

            async with (await destination.open("wb")) as file:
                async for chunk in response.aiter_raw():
                    downloaded += len(chunk)
                    await file.write(chunk)

                    if clock() - last_update > update_period:
                        progress = attr.evolve(progress, downloaded=downloaded)
                        yield progress
                        last_update = clock()

            if progress.downloaded != downloaded:
                progress = attr.evolve(progress, downloaded=downloaded)
                yield progress
