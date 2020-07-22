from qtpy import QtWidgets
import trio


import qtrio
import qtrio._core
import qtrio._dialogs
import qtrio._qt


@qtrio.host
async def test_information_message_box(request, qtbot):
    import faulthandler
    faulthandler.dump_traceback_later(2.5)
    text = "Consider yourself informed."
    queried_text = None

    dialog = qtrio._dialogs.create_information_message_box(
        icon=QtWidgets.QMessageBox.Information, title="Information", text=text,
    )

    async def user(task_status):
        nonlocal queried_text

        async with qtrio._core.wait_signal_context(dialog.shown):
            task_status.started()

        queried_text = dialog.dialog.text()
        dialog.dialog.accept()

    async with trio.open_nursery() as nursery:
        await nursery.start(user)
        with qtrio._qt.connection(signal=dialog.shown, slot=qtbot.addWidget):
            await dialog.wait()

    assert queried_text == text
