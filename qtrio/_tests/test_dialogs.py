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
        try:
            print('+++++', 'test user', 0, threading.get_ident())
            nonlocal queried_text

            print('+++++', 'test user', 1, threading.get_ident())
            async with qtrio._core.wait_signal_context(dialog.shown):
                print('+++++', 'test user', 2, threading.get_ident())
                task_status.started()
                print('+++++', 'test user', 3, threading.get_ident())
            print('+++++', 'test user', 4, threading.get_ident())

            queried_text = dialog.dialog.text()
            print('+++++', 'test user', 5, threading.get_ident())
            dialog.dialog.accept()
            print('+++++', 'test user', 6, threading.get_ident())
        finally:
            print('+++++', 'test user finally', threading.get_ident())

    async with trio.open_nursery() as nursery:
        print('+++++', 'test', 0, threading.get_ident())
        await nursery.start(user)
        print('+++++', 'test', 1, threading.get_ident())
        with qtrio._qt.connection(signal=dialog.shown, slot=qtbot.addWidget):
            print('+++++', 'test', 2, threading.get_ident())
            await dialog.wait()

        print('+++++', 'test', 3, threading.get_ident())

    print('+++++', 'test', 4, threading.get_ident())

    assert queried_text == text
