"""Thanks to njsmith for developing Trio guest mode and sharing the first example
integration with Qt.
"""
import os
import time

import async_generator
import httpcore._async.http11
import httpx
import hyperlink
import qtrio
import trio

from qtpy import QtCore
from qtpy import QtWidgets


# Default is 4096
httpcore._async.http11.AsyncHTTP11Connection.READ_NUM_BYTES = 100_000


async def main(url, destination, fps):
    try:
        if url is None:
            url = await get_text(
                title=create_title("Enter URL"), label="URL to download:"
            )

        url = hyperlink.URL.from_text(url)

        if destination is None:
            destination = await get_save_file_path(default_filename=url.path[-1])

        destination = trio.Path(destination)
    except qtrio.UserCancelledError:
        return

    await qtrio.examples.download.get_dialog(url, destination, fps=fps)


async def get_dialog(url: hyperlink.URL, destination: trio.Path, fps: int):
    async with manage_progress_dialog(
        title=create_title("Fetching"), label=f"Fetching {url}..."
    ) as progress_dialog:
        # Always show the dialog
        progress_dialog.setMinimumDuration(0)

        with trio.CancelScope() as cscope:
            with qtrio.connection(signal=progress_dialog.canceled, slot=cscope.cancel):
                start = time.monotonic()

                async for downloaded, total in get(
                    url=url, destination=destination, update_period=1 / fps
                ):
                    progress_dialog.setMaximum(total)
                    progress_dialog.setValue(downloaded)

                end = time.monotonic()

        duration = end - start
        bytes_per_second = downloaded / duration

        summary = "\n\n".join(
            [
                url.asText(),
                os.fspath(destination),
                f"Downloaded {downloaded} bytes in {duration:.2f} seconds",
                f"{bytes_per_second:.2f} bytes/second",
            ]
        )

    await show_information_message_box(
        title=create_title("Download Summary"), message=summary
    )


async def get(url: hyperlink.URL, destination: trio.Path, update_period: float):
    async with httpx.AsyncClient() as client:
        async with client.stream("GET", url.asText()) as response:
            downloaded = 0
            total = int(response.headers["content-length"])

            yield downloaded, total
            last_update = time.monotonic()

            async with (await destination.open("wb")) as file:
                async for chunk in response.aiter_raw():
                    downloaded += len(chunk)
                    await file.write(chunk)

                    if time.monotonic() - last_update > update_period:
                        yield downloaded, total
                        last_update = time.monotonic()


def create_title(specific):
    return f"QTrio Download Example - {specific}"


async def get_text(title, label, parent=None):
    dialog = QtWidgets.QInputDialog(parent)
    dialog.setWindowTitle(title)
    dialog.setLabelText(label)

    dialog.show()
    # TODO: is there technically a race here?
    [result] = await qtrio.wait_signal(dialog.finished)

    if result != QtWidgets.QInputDialog.Accepted:
        raise qtrio.UserCancelledError()

    text = dialog.textValue()

    return text


async def get_save_file_path(default_filename, parent=None):
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


async def show_information_message_box(title, message, parent=None):
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
):
    dialog = QtWidgets.QProgressDialog(
        label, cancel_button_text, minimum, maximum, parent
    )
    try:
        dialog.setWindowTitle(title)
        yield dialog
    finally:
        dialog.close()
