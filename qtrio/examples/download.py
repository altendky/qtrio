"""Thanks to njsmith for developing Trio guest mode and sharing the first example
integration with Qt.
"""
import contextlib
import functools
import math
import os
import time
import typing

import attr
import httpcore._async.http11
import httpx
import hyperlink
import trio
import trio_typing

import qtrio
import qtrio.dialogs


# Default is 4096
httpcore._async.http11.AsyncHTTP11Connection.READ_NUM_BYTES = 100_000

default_fps: int = 60


def create_title(specific: str) -> str:
    return f"QTrio Download Example - {specific}"


@attr.s(auto_attribs=True, frozen=True)
class Progress:
    downloaded: int
    first: bool
    total: typing.Optional[int] = None


@attr.s(auto_attribs=True, eq=False)
class Downloader:
    text_input_dialog: typing.Optional[qtrio.dialogs.TextInputDialog] = None
    file_dialog: typing.Optional[qtrio.dialogs.FileDialog] = None
    get_dialog: typing.Optional["GetDialog"] = None

    text_input_shown_event: trio.Event = attr.ib(factory=trio.Event)
    file_dialog_shown_event: trio.Event = attr.ib(factory=trio.Event)
    get_dialog_created_event: trio.Event = attr.ib(factory=trio.Event)

    async def serve(
        self,
        url: typing.Optional[typing.Union[str, hyperlink.URL]] = None,
        destination: typing.Optional[typing.Union[str, os.PathLike]] = None,
        fps: float = default_fps,
        http_application: typing.Optional[typing.Callable[..., typing.Any]] = None,
        *,
        task_status: trio_typing.TaskStatus[None] = trio.TASK_STATUS_IGNORED,
    ) -> None:
        task_status.started()

        converted_url: hyperlink.URL
        converted_destination: trio.Path

        with contextlib.suppress(qtrio.UserCancelledError):
            if url is None:
                # async with trio.open_nursery() as nursery:
                #     start = functools.partial(
                #         qtrio.dialogs.TextInputDialog.serve,
                #         title=create_title("Enter URL"),
                #         label="URL to download:",
                #     )
                #     self.text_input_dialog = await nursery.start(start)

                self.text_input_dialog = qtrio.dialogs.create_text_input_dialog()

                self.text_input_dialog.title = create_title("Enter URL")
                self.text_input_dialog.label = "URL to download:"

                url = await self.text_input_dialog.wait(
                    shown_event=self.text_input_shown_event,
                )
                self.text_input_dialog = None

            if isinstance(url, str):
                converted_url = hyperlink.URL.from_text(url)
            else:
                converted_url = url

            if destination is None:
                self.file_dialog = qtrio.dialogs.create_file_save_dialog()

                default_file: str = ""
                if len(converted_url.path) > 0:
                    default_file = converted_url.path[-1]

                self.file_dialog.default_file = trio.Path(default_file)

                destination = await self.file_dialog.wait(
                    shown_event=self.file_dialog_shown_event,
                )
                self.file_dialog = None

            converted_destination = trio.Path(destination)

            async with trio.open_nursery() as nursery:
                start = functools.partial(
                    start_get_dialog,
                    url=converted_url,
                    destination=converted_destination,
                    fps=fps,
                    http_application=http_application,
                )
                self.get_dialog = await nursery.start(start)
                self.get_dialog_created_event.set()


async def start_downloader(
    url: typing.Optional[hyperlink.URL] = None,
    destination: typing.Optional[trio.Path] = None,
    fps: float = default_fps,
    http_application: typing.Optional[typing.Callable[..., typing.Any]] = None,
    hold_event: typing.Optional[trio.Event] = None,
    *,
    cls: typing.Type[Downloader] = Downloader,
    task_status: trio_typing.TaskStatus[Downloader] = trio.TASK_STATUS_IGNORED,
) -> None:
    self = cls()

    task_status.started(self)

    if hold_event is not None:
        await hold_event.wait()

    await self.serve(
        url=url, destination=destination, fps=fps, http_application=http_application
    )


@attr.s(auto_attribs=True, eq=False)
class GetDialog:
    fps: float = default_fps
    clock: typing.Callable[[], float] = time.monotonic
    http_application: typing.Optional[typing.Callable[..., typing.Any]] = None

    progress_dialog: typing.Optional[qtrio.dialogs.ProgressDialog] = None
    message_box: typing.Optional[qtrio.dialogs.MessageBox] = None

    progress_dialog_shown_event: trio.Event = attr.ib(factory=trio.Event)
    message_box_shown_event: trio.Event = attr.ib(factory=trio.Event)

    async def serve(
        self,
        url: hyperlink.URL,
        destination: trio.Path,
    ) -> None:
        self.progress_dialog = qtrio.dialogs.create_progress_dialog()

        self.progress_dialog.title = create_title("Fetching")
        self.progress_dialog.text = f"Fetching {url}..."

        async with self.progress_dialog.manage():
            if self.progress_dialog.dialog is None:  # pragma: no cover
                raise qtrio.InternalError(
                    "Dialog not assigned while it is being managed."
                )

            # Always show the dialog
            self.progress_dialog.dialog.setMinimumDuration(0)
            self.progress_dialog_shown_event.set()

            start = self.clock()

            async for progress in get(
                url=url,
                destination=destination,
                update_period=1 / self.fps,
                clock=self.clock,
                http_application=self.http_application,
            ):
                if progress.first:
                    if progress.total is None:
                        maximum = 0
                    else:
                        maximum = progress.total

                    self.progress_dialog.dialog.setMaximum(maximum)
                    self.progress_dialog.dialog.setValue(0)

                if progress.total is not None:
                    self.progress_dialog.dialog.setValue(progress.downloaded)

            end = self.clock()

        self.progress_dialog = None

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

        self.message_box = qtrio.dialogs.create_message_box()

        self.message_box.title = create_title("Download Summary")
        self.message_box.text = summary

        await self.message_box.wait(shown_event=self.message_box_shown_event)

        self.message_box = None


async def start_get_dialog(
    url: hyperlink.URL,
    destination: trio.Path,
    fps: float = default_fps,
    http_application: typing.Optional[typing.Callable[..., typing.Any]] = None,
    hold_event: typing.Optional[trio.Event] = None,
    *,
    cls: typing.Type[GetDialog] = GetDialog,
    task_status: trio_typing.TaskStatus[GetDialog] = trio.TASK_STATUS_IGNORED,
) -> None:
    self = cls(fps=fps, http_application=http_application)

    task_status.started(self)

    if hold_event is not None:
        await hold_event.wait()

    await self.serve(url=url, destination=destination)


async def get(
    url: hyperlink.URL,
    destination: trio.Path,
    update_period: float = 0.2,
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


if __name__ == "__main__":  # pragma: no cover
    qtrio.run(start_downloader)
