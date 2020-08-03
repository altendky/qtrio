import sys

from qtpy import QtCore
from qtpy import QtWidgets
import pytest
import trio


import qtrio
import qtrio._core
import qtrio._dialogs
import qtrio._qt


@qtrio.host
async def test_get_integer_gets_value(request, qtbot):
    dialog = qtrio._dialogs.IntegerDialog.build()

    async def user(task_status):
        async with qtrio._core.wait_signal_context(dialog.shown):
            task_status.started()

        qtbot.keyClicks(dialog.edit_widget, str(test_value))
        qtbot.mouseClick(dialog.ok_button, QtCore.Qt.LeftButton)

    test_value = 928

    async with trio.open_nursery() as nursery:
        await nursery.start(user)
        with qtrio._qt.connection(signal=dialog.shown, slot=qtbot.addWidget):
            integer = await dialog.wait()

    assert integer == test_value


@qtrio.host
async def test_get_integer_raises_cancel_when_canceled(request, qtbot):
    dialog = qtrio._dialogs.IntegerDialog.build()

    async def user(task_status):
        async with qtrio._core.wait_signal_context(dialog.shown):
            task_status.started()

        qtbot.keyClicks(dialog.edit_widget, "abc")
        qtbot.mouseClick(dialog.cancel_button, QtCore.Qt.LeftButton)

    async with trio.open_nursery() as nursery:
        await nursery.start(user)
        with qtrio._qt.connection(signal=dialog.shown, slot=qtbot.addWidget):
            with pytest.raises(qtrio.UserCancelledError):
                await dialog.wait()


@qtrio.host
async def test_get_integer_gets_value_after_retry(request, qtbot):
    dialog = qtrio._dialogs.IntegerDialog.build()

    test_value = 928

    async def user(task_status):
        async with qtrio._core.wait_signal_context(dialog.shown):
            task_status.started()

        qtbot.keyClicks(dialog.edit_widget, "abc")

        async with qtrio._core.wait_signal_context(dialog.shown):
            qtbot.mouseClick(dialog.ok_button, QtCore.Qt.LeftButton)

        qtbot.keyClicks(dialog.edit_widget, str(test_value))
        qtbot.mouseClick(dialog.ok_button, QtCore.Qt.LeftButton)

    async with trio.open_nursery() as nursery:
        await nursery.start(user)
        with qtrio._qt.connection(signal=dialog.shown, slot=qtbot.addWidget):
            integer = await dialog.wait()

    assert integer == test_value


@pytest.mark.parametrize(
    argnames=["builder"],
    argvalues=[
        [qtrio._dialogs.IntegerDialog.build],
        [qtrio._dialogs.TextInputDialog.build],
        [qtrio._dialogs.FileDialog.build],
        [lambda: qtrio._dialogs.MessageBox.build_information(title="", text="")],
    ],
)
def test_unused_dialog_teardown_ok(builder):
    dialog = builder()
    dialog.teardown()


@qtrio.host(timeout=10)
async def test_file_save(request, qtbot, tmp_path):
    assert tmp_path.is_dir()
    path_to_select = trio.Path(tmp_path) / "something.new"

    dialog = qtrio._dialogs.FileDialog.build(
        default_directory=path_to_select.parent, default_file=path_to_select,
    )

    async def user(task_status):
        async with qtrio._core.wait_signal_context(dialog.shown):
            task_status.started()

        # allow cancellation to occur even if the signal was received before the
        # cancellation was requested.
        await trio.sleep(0)

        dialog.dialog.accept()

    async with trio.open_nursery() as nursery:
        await nursery.start(user)
        with qtrio._qt.connection(signal=dialog.shown, slot=qtbot.addWidget):
            selected_path = await dialog.wait()

    assert selected_path == path_to_select


@qtrio.host
async def test_information_message_box(request, qtbot):
    text = "Consider yourself informed."
    queried_text = None

    dialog = qtrio._dialogs.MessageBox.build_information(
        title="Information", text=text, icon=QtWidgets.QMessageBox.Information,
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


@qtrio.host
async def test_text_input_dialog(request, qtbot):
    dialog = qtrio._dialogs.TextInputDialog.build()

    entered_text = "etcetera"

    async def user(task_status):
        async with qtrio._core.wait_signal_context(dialog.shown):
            task_status.started()

        qtbot.keyClicks(dialog.line_edit, entered_text)
        dialog.dialog.accept()

    async with trio.open_nursery() as nursery:
        await nursery.start(user)
        with qtrio._qt.connection(signal=dialog.shown, slot=qtbot.addWidget):
            returned_text = await dialog.wait()

    assert returned_text == entered_text
