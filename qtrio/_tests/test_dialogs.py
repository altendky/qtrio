import threading

from qtpy import QtWidgets
import trio


import qtrio
import qtrio._core
import qtrio._dialogs
import qtrio._qt


@qtrio.host
async def test_information_message_box(request, qtbot):
    text = "Consider yourself informed."
    queried_text = None

    dialog = qtrio._dialogs.create_information_message_box(
        icon=QtWidgets.QMessageBox.Information, title="Information", text=text,
    )

    async def user(task_status):
        print('+++++ 1', threading.get_ident())
        nonlocal queried_text

        print('+++++ 2', threading.get_ident())
        async with qtrio._core.wait_signal_context(dialog.shown):
            print('+++++ 3', threading.get_ident())
            task_status.started()
            print('+++++ 4', threading.get_ident())
        print('+++++ 5', threading.get_ident())

        queried_text = dialog.dialog.text()
        print('+++++ 6', threading.get_ident())
        dialog.dialog.accept()
        print('+++++ 7', threading.get_ident())

    async with trio.open_nursery() as nursery:
        print('+++++ A', threading.get_ident())
        await nursery.start(user)
        print('+++++ B', threading.get_ident())
        with qtrio._qt.connection(signal=dialog.shown, slot=qtbot.addWidget):
            print('+++++ C', threading.get_ident())
            await dialog.wait()
            print('+++++ D', threading.get_ident())

    print('+++++ E', threading.get_ident())

    assert queried_text == text
