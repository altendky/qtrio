import os
import sys

from qtpy import QtCore
from qtpy import QtWidgets
import pytest
import trio


import qtrio
import qtrio._core
import qtrio.dialogs
import qtrio._qt


def create_message_box_without_arguments():
    return qtrio.dialogs.create_message_box(title="", text="")


@pytest.fixture(
    name="builder",
    params=[
        qtrio.dialogs.create_integer_dialog,
        qtrio.dialogs.create_text_input_dialog,
        qtrio.dialogs.create_file_save_dialog,
        create_message_box_without_arguments,
    ],
)
def builder_fixture(request):
    yield request.param


@qtrio.host
async def test_get_integer_gets_value(request, qtbot):
    dialog = qtrio.dialogs.create_integer_dialog()

    async def user(task_status):
        async with qtrio._core.wait_signal_context(dialog.shown):
            task_status.started()

        qtbot.keyClicks(dialog.edit_widget, str(test_value))
        qtbot.mouseClick(dialog.accept_button, QtCore.Qt.LeftButton)

    test_value = 928

    async with trio.open_nursery() as nursery:
        await nursery.start(user)
        with qtrio._qt.connection(signal=dialog.shown, slot=qtbot.addWidget):
            integer = await dialog.wait()

    assert integer == test_value


@qtrio.host
async def test_get_integer_raises_cancel_when_canceled(request, qtbot):
    dialog = qtrio.dialogs.create_integer_dialog()

    async def user(task_status):
        async with qtrio._core.wait_signal_context(dialog.shown):
            task_status.started()

        qtbot.keyClicks(dialog.edit_widget, "abc")
        qtbot.mouseClick(dialog.reject_button, QtCore.Qt.LeftButton)

    async with trio.open_nursery() as nursery:
        await nursery.start(user)
        with qtrio._qt.connection(signal=dialog.shown, slot=qtbot.addWidget):
            with pytest.raises(qtrio.UserCancelledError):
                await dialog.wait()


@qtrio.host
async def test_get_integer_raises_for_invalid_input(request, qtbot):
    dialog = qtrio.dialogs.create_integer_dialog()

    async def user(task_status):
        async with qtrio._core.wait_signal_context(dialog.shown):
            task_status.started()

        qtbot.keyClicks(dialog.edit_widget, "abc")
        qtbot.mouseClick(dialog.accept_button, QtCore.Qt.LeftButton)

    async with trio.open_nursery() as nursery:
        await nursery.start(user)
        with qtrio._qt.connection(signal=dialog.shown, slot=qtbot.addWidget):
            with pytest.raises(qtrio.InvalidInputError):
                await dialog.wait()


def test_unused_dialog_teardown_ok(builder):
    dialog = builder()
    dialog.teardown()


@qtrio.host(timeout=30)
async def test_file_save(request, qtbot, tmp_path):
    path_to_select = trio.Path(tmp_path) / "something.new"

    dialog = qtrio.dialogs.create_file_save_dialog(
        default_directory=path_to_select.parent,
        default_file=path_to_select,
    )

    async def user(task_status):
        async with qtrio._core.wait_signal_context(dialog.shown):
            task_status.started()

        # allow cancellation to occur even if the signal was received before the
        # cancellation was requested.
        await trio.sleep(0)

        assert dialog.dialog is not None

        dialog.dialog.accept()

    async with trio.open_nursery() as nursery:
        await nursery.start(user)
        with qtrio._qt.connection(signal=dialog.shown, slot=qtbot.addWidget):
            selected_path = await dialog.wait()

    assert selected_path == path_to_select


@qtrio.host(timeout=30)
async def test_file_save_no_defaults(request, qtbot, tmp_path):
    path_to_select = trio.Path(tmp_path) / "another.thing"

    dialog = qtrio.dialogs.create_file_save_dialog()

    async def user(task_status):
        async with qtrio._core.wait_signal_context(dialog.shown):
            task_status.started()

        # allow cancellation to occur even if the signal was received before the
        # cancellation was requested.
        await trio.sleep(0)

        assert dialog.dialog is not None

        dialog.dialog.setDirectory(os.fspath(path_to_select.parent))
        [text_edit] = dialog.dialog.findChildren(QtWidgets.QLineEdit)
        text_edit.setText(path_to_select.name)
        dialog.dialog.accept()

    async with trio.open_nursery() as nursery:
        await nursery.start(user)
        with qtrio._qt.connection(signal=dialog.shown, slot=qtbot.addWidget):
            selected_path = await dialog.wait()

    assert selected_path == path_to_select


@qtrio.host(timeout=30)
async def test_file_save_cancelled(request, qtbot, tmp_path):
    dialog = qtrio.dialogs.create_file_save_dialog()

    async def user(task_status):
        async with qtrio._core.wait_signal_context(dialog.shown):
            task_status.started()

        # allow cancellation to occur even if the signal was received before the
        # cancellation was requested.
        await trio.sleep(0)

        assert dialog.dialog is not None

        dialog.dialog.reject()

    async with trio.open_nursery() as nursery:
        await nursery.start(user)
        with qtrio._qt.connection(signal=dialog.shown, slot=qtbot.addWidget):
            with pytest.raises(qtrio.UserCancelledError):
                await dialog.wait()


@qtrio.host
async def test_information_message_box(request, qtbot):
    text = "Consider yourself informed."
    queried_text = None

    dialog = qtrio.dialogs.create_message_box(
        title="Information",
        text=text,
        icon=QtWidgets.QMessageBox.Information,
    )

    async def user(task_status):
        nonlocal queried_text

        async with qtrio._core.wait_signal_context(dialog.shown):
            task_status.started()

        assert dialog.dialog is not None

        queried_text = dialog.dialog.text()
        dialog.dialog.accept()

    async with trio.open_nursery() as nursery:
        await nursery.start(user)
        with qtrio._qt.connection(signal=dialog.shown, slot=qtbot.addWidget):
            await dialog.wait()

    assert queried_text == text


@qtrio.host
async def test_information_message_box_cancel(request, qtbot):
    dialog = qtrio.dialogs.create_message_box(
        title="",
        text="",
        icon=QtWidgets.QMessageBox.Information,
        buttons=QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel,
    )

    async def user(task_status):
        async with qtrio._core.wait_signal_context(dialog.shown):
            task_status.started()

        assert dialog.dialog is not None

        dialog.dialog.reject()

    async with trio.open_nursery() as nursery:
        await nursery.start(user)
        with qtrio._qt.connection(signal=dialog.shown, slot=qtbot.addWidget):
            with pytest.raises(qtrio.UserCancelledError):
                await dialog.wait()


@qtrio.host
async def test_text_input_dialog(request, qtbot):
    dialog = qtrio.dialogs.create_text_input_dialog()

    entered_text = "etcetera"

    async def user(task_status):
        async with qtrio._core.wait_signal_context(dialog.shown):
            task_status.started()

        qtbot.keyClicks(dialog.line_edit, entered_text)

        assert dialog.dialog is not None

        dialog.dialog.accept()

    async with trio.open_nursery() as nursery:
        await nursery.start(user)
        with qtrio._qt.connection(signal=dialog.shown, slot=qtbot.addWidget):
            returned_text = await dialog.wait()

    assert returned_text == entered_text


def test_text_input_dialog_with_title():
    title_string = "abc123"
    dialog = qtrio.dialogs.create_text_input_dialog(title=title_string)
    with qtrio.dialogs._manage(dialog=dialog):
        assert dialog.dialog is not None

        assert dialog.dialog.windowTitle() == title_string


def test_text_input_dialog_with_label():
    label_string = "lmno789"
    dialog = qtrio.dialogs.create_text_input_dialog(label=label_string)
    with qtrio.dialogs._manage(dialog=dialog):
        assert dialog.dialog is not None

        [label] = dialog.dialog.findChildren(QtWidgets.QLabel)
        assert label.text() == label_string


@qtrio.host
async def test_text_input_dialog_cancel(request, qtbot):
    dialog = qtrio.dialogs.create_text_input_dialog()

    async def user(task_status):
        async with qtrio._core.wait_signal_context(dialog.shown):
            task_status.started()

        assert dialog.dialog is not None

        dialog.dialog.reject()

    async with trio.open_nursery() as nursery:
        await nursery.start(user)
        with qtrio._qt.connection(signal=dialog.shown, slot=qtbot.addWidget):
            with pytest.raises(qtrio.UserCancelledError):
                await dialog.wait()


def test_dialog_button_box_buttons_by_role_no_buttons(qtbot):
    dialog = QtWidgets.QDialog()
    assert qtrio.dialogs._dialog_button_box_buttons_by_role(dialog=dialog) == {}
