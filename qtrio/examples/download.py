"""Thanks to njsmith for developing Trio guest mode and sharing the first example
integration with Qt.
"""
import os
import time
import typing

import attr
import async_generator
import httpcore._async.http11
import httpx
import hyperlink
import qtrio
import trio

from qtpy import QtCore
from qtpy import QtWidgets

import qtrio.dialogs


# Default is 4096
httpcore._async.http11.AsyncHTTP11Connection.READ_NUM_BYTES = 100_000


async def main(
    url: typing.Optional[typing.Union[str, hyperlink.URL]],
    destination: typing.Optional[typing.Union[str, os.PathLike]],
    fps: int = 60,
) -> None:
    converted_url: hyperlink.URL
    converted_destination: trio.Path

    try:
        if url is None:
            text_input_dialog = qtrio.dialogs.create_text_input_dialog(
                title=create_title("Enter URL"),
                label="URL to download:",
            )
            url_text = await text_input_dialog.wait()

            converted_url = hyperlink.URL.from_text(url_text)
        elif isinstance(url, str):
            converted_url = hyperlink.URL.from_text(url)
        else:
            converted_url = url

        if destination is None:
            destination = await get_save_file_path(
                default_filename=converted_url.path[-1]
            )

        converted_destination = trio.Path(destination)
    except qtrio.UserCancelledError:
        return

    await qtrio.examples.download.get_dialog(
        url=converted_url,
        destination=converted_destination,
        fps=fps,
    )

    return


async def get_dialog(url: hyperlink.URL, destination: trio.Path, fps: int) -> None:
    async with manage_progress_dialog(
        title=create_title("Fetching"), label=f"Fetching {url}..."
    ) as progress_dialog:
        # Always show the dialog
        progress_dialog.setMinimumDuration(0)

        with trio.CancelScope() as cscope:
            with qtrio.connection(signal=progress_dialog.canceled, slot=cscope.cancel):
                start = time.monotonic()

                async for progress in get(
                    url=url, destination=destination, update_period=1 / fps
                ):
                    progress_dialog.setMaximum(progress.total)
                    progress_dialog.setValue(progress.downloaded)

                end = time.monotonic()

        duration = end - start
        bytes_per_second = progress.downloaded / duration

        summary = "\n\n".join(
            [
                url.asText(),
                os.fspath(destination),
                f"Downloaded {progress.downloaded} bytes in {duration:.2f} seconds",
                f"{bytes_per_second:.2f} bytes/second",
            ]
        )

    await show_information_message_box(
        title=create_title("Download Summary"), message=summary
    )


@attr.s(auto_attribs=True, frozen=True)
class Progress:
    downloaded: int
    total: int


async def get(
    url: hyperlink.URL, destination: trio.Path, update_period: float
) -> typing.AsyncIterable[Progress]:
    async with httpx.AsyncClient() as client:
        async with client.stream("GET", url.asText()) as response:
            progress = Progress(
                downloaded=0,
                total=int(response.headers["content-length"]),
            )

            yield progress
            last_update = time.monotonic()

            async with (await destination.open("wb")) as file:
                async for chunk in response.aiter_raw():
                    progress = attr.evolve(
                        progress, downloaded=progress.downloaded + len(chunk)
                    )
                    await file.write(chunk)

                    if time.monotonic() - last_update > update_period:
                        yield progress
                        last_update = time.monotonic()


def create_title(specific: str) -> str:
    return f"QTrio Download Example - {specific}"


async def get_save_file_path(
    default_filename: str, parent: typing.Optional[QtWidgets.QWidget] = None
) -> trio.Path:
    dialog = QtWidgets.QFileDialog(parent)
    dialog.setFileMode(QtWidgets.QFileDialog.AnyFile)
    dialog.setAcceptMode(QtWidgets.QFileDialog.AcceptSave)
    dialog.setWindowTitle(create_title(dialog.windowTitle()))
    dialog.selectFile(default_filename)

    dialog.show()
    # TODO: is there technically a race here?
    [result] = await qtrio.wait_signal(dialog.finished)

    if result != QtWidgets.QFileDialog.Accepted:
        raise qtrio.UserCancelledError()

    [path] = dialog.selectedFiles()

    return trio.Path(path)


async def show_information_message_box(
    title: str, message: str, parent: typing.Optional[QtWidgets.QWidget] = None
) -> None:
    box = QtWidgets.QMessageBox(
        QtWidgets.QMessageBox.Information, title, message, QtWidgets.QMessageBox.Ok
    )
    box.show()
    # TODO: is there technically a race here?
    await qtrio.wait_signal(box.finished)


@async_generator.asynccontextmanager
async def manage_progress_dialog(
    title: str,
    label: str,
    minimum: int = 0,
    maximum: int = 0,
    cancel_button_text: str = "Cancel",
    parent: QtCore.QObject = None,
) -> typing.AsyncIterable[QtWidgets.QProgressDialog]:
    dialog = QtWidgets.QProgressDialog(
        label, cancel_button_text, minimum, maximum, parent
    )
    try:
        dialog.setWindowTitle(title)
        yield dialog
    finally:
        dialog.close()
