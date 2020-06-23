import os

from qtpy import QtCore
from qtpy import QtWidgets
import pytest
import trio


import qtrio
import qtrio._core
import qtrio._dialogs


@qtrio.host
async def test_get_integer_gets_value(request, qtbot):
    dialog = qtrio._dialogs.IntegerDialog.build()

    async def user(task_status):
        async with qtrio.wait_signal_context(dialog.shown):
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
        async with qtrio.wait_signal_context(dialog.shown):
            task_status.started()

        qtbot.keyClicks(dialog.edit_widget, "abc")
        qtbot.mouseClick(dialog.cancel_button, QtCore.Qt.LeftButton)

    async with trio.open_nursery() as nursery:
        await nursery.start(user)
        with pytest.raises(qtrio.UserCancelledError):
            with qtrio._qt.connection(signal=dialog.shown, slot=qtbot.addWidget):
                await dialog.wait()


@qtrio.host
async def test_get_integer_gets_value_after_retry(request, qtbot):
    dialog = qtrio._dialogs.IntegerDialog.build()

    test_value = 928

    async def user(task_status):
        async with qtrio.wait_signal_context(dialog.shown):
            task_status.started()

        qtbot.keyClicks(dialog.edit_widget, "abc")

        async with qtrio.wait_signal_context(dialog.shown):
            qtbot.mouseClick(dialog.ok_button, QtCore.Qt.LeftButton)

        qtbot.keyClicks(dialog.edit_widget, str(test_value))
        qtbot.mouseClick(dialog.ok_button, QtCore.Qt.LeftButton)

    async with trio.open_nursery() as nursery:
        await nursery.start(user)
        with qtrio._qt.connection(signal=dialog.shown, slot=qtbot.addWidget):
            integer = await dialog.wait()

    assert integer == test_value


@qtrio.host
async def test_file_save(request, qtbot, tmp_path):
    path_to_select = tmp_path / "something.new"

    dialog = qtrio._dialogs.create_file_save_dialog(default_path=path_to_select)

    async def user(task_status):
        async with qtrio.wait_signal_context(dialog.shown):
            task_status.started()

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

    dialog = qtrio._dialogs.create_information_message_box(
        icon=QtWidgets.QMessageBox.Information, title="Information", text=text,
    )

    async def user(task_status):
        nonlocal queried_text

        async with qtrio.wait_signal_context(dialog.shown):
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
    dialog = qtrio._dialogs.create_text_input_dialog()

    entered_text = "etcetera"

    async def user(task_status):
        async with qtrio.wait_signal_context(dialog.shown):
            task_status.started()

        qtbot.keyClicks(dialog.line_edit, entered_text)
        dialog.dialog.accept()

    async with trio.open_nursery() as nursery:
        await nursery.start(user)
        with qtrio._qt.connection(signal=dialog.shown, slot=qtbot.addWidget):
            returned_text = await dialog.wait()

    assert returned_text == entered_text
