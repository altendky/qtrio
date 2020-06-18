import PyQt5.QtCore
import pytest
import trio


import qtrio
import qtrio._core
import qtrio._dialogs


@qtrio.host
async def test_get_integer_gets_value(request, qtbot):
    dialog = qtrio._dialogs.IntegerDialog.build()
    dialog.shown.connect(qtbot.addWidget)

    async def user(task_status):
        async with qtrio._core.signal_event_manager(dialog.shown):
            task_status.started()

        qtbot.keyClicks(dialog.edit_widget, str(test_value))
        qtbot.mouseClick(dialog.ok_button, PyQt5.QtCore.Qt.LeftButton)

    test_value = 928

    async with trio.open_nursery() as nursery:
        await nursery.start(user)
        integer = await dialog.wait()

    assert integer == test_value


@qtrio.host
async def test_get_integer_raises_cancel_when_canceled(request, qtbot):
    dialog = qtrio._dialogs.IntegerDialog.build()
    dialog.shown.connect(qtbot.addWidget)

    async def user(task_status):
        async with qtrio._core.signal_event_manager(dialog.shown):
            task_status.started()

        qtbot.keyClicks(dialog.edit_widget, "abc")
        qtbot.mouseClick(dialog.cancel_button, PyQt5.QtCore.Qt.LeftButton)

    async with trio.open_nursery() as nursery:
        await nursery.start(user)
        with pytest.raises(qtrio.UserCancelledError):
            await dialog.wait()


@qtrio.host
async def test_get_integer_gets_value_after_retry(request, qtbot):
    dialog = qtrio._dialogs.IntegerDialog.build()
    dialog.shown.connect(qtbot.addWidget)

    test_value = 928

    async def user(task_status):
        async with qtrio._core.signal_event_manager(dialog.shown):
            task_status.started()

        qtbot.keyClicks(dialog.edit_widget, "abc")

        async with qtrio._core.signal_event_manager(dialog.shown):
            qtbot.mouseClick(dialog.ok_button, PyQt5.QtCore.Qt.LeftButton)

        qtbot.keyClicks(dialog.edit_widget, str(test_value))
        qtbot.mouseClick(dialog.ok_button, PyQt5.QtCore.Qt.LeftButton)

    async with trio.open_nursery() as nursery:
        await nursery.start(user)
        integer = await dialog.wait()

    assert integer == test_value
