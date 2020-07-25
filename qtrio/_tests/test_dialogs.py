import threading

from qtpy import QtWidgets
import trio


import qtrio
import qtrio._core
import qtrio._dialogs
import qtrio._qt


@qtrio.host
        # allow cancellation to occur even if the signal was received before the
        # cancellation was requested.
        await trio.sleep(0)

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
            # add a checkpoint to allow cancellation even if the signal was sent before
            # the cancellation was initiated.
            await trio.sleep(0)
            print('+++++', 'test user', 4, threading.get_ident())

            queried_text = dialog.dialog.text()
            print('+++++', 'test user', 5, threading.get_ident())
            dialog.dialog.accept()
            print('+++++', 'test user', 6, threading.get_ident())
        except trio.Cancelled:
            print('+++++', 'test user cancelled', threading.get_ident())
            raise
        finally:
            print('+++++', 'test user finally', threading.get_ident())

    async with trio.open_nursery() as nursery:
        print('+++++', 'test', 0, threading.get_ident())
        await nursery.start(user)
        print('+++++', 'test', 1, threading.get_ident())
        with qtrio._qt.connection(signal=dialog.shown, slot=qtbot.addWidget):
            print('+++++', 'test', 2, threading.get_ident())
            try:
                await dialog.wait()
            except trio.Cancelled:
                print('+++++', 'test cancelled', threading.get_ident())
                raise

        print('+++++', 'test', 3, threading.get_ident())

    print('+++++', 'test', 4, threading.get_ident())

    assert queried_text == text
