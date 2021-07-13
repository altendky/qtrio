import math
import os
import pathlib
import typing

import pytestqt.qtbot
from qts import QtCore
from qts import QtWidgets
import pytest
import trio


import qtrio
import qtrio._core
import qtrio.dialogs
import qtrio._qt


@pytest.fixture(
    name="builder",
    params=[
        qtrio.dialogs.create_integer_dialog,
        qtrio.dialogs.create_text_input_dialog,
        qtrio.dialogs.create_file_save_dialog,
        qtrio.dialogs.create_file_open_dialog,
        qtrio.dialogs.create_message_box,
        qtrio.dialogs.create_progress_dialog,
    ],
)
def builder_fixture(request):
    yield request.param


@pytest.fixture(
    name="optional_parent",
    params=[False, True],
    ids=["No parent", "Widget parent"],
)
def optional_parent_fixture(request, qapp):
    if request.param:
        return QtWidgets.QWidget()

    return None


async def test_get_integer_gets_value(qtbot: pytestqt.qtbot.QtBot) -> None:
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


async def test_get_integer_raises_cancel_when_canceled(
    qtbot: pytestqt.qtbot.QtBot,
) -> None:
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


async def test_get_integer_raises_for_invalid_input(
    qtbot: pytestqt.qtbot.QtBot,
) -> None:
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


async def test_file_save(qtbot: pytestqt.qtbot.QtBot, tmp_path: pathlib.Path) -> None:
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


async def test_file_save_no_defaults(
    qtbot: pytestqt.qtbot.QtBot, tmp_path: pathlib.Path
) -> None:
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


async def test_file_save_cancelled(
    qtbot: pytestqt.qtbot.QtBot, tmp_path: pathlib.Path
) -> None:
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


async def test_file_open_set_path(tmp_path: pathlib.Path) -> None:
    file_path = tmp_path.joinpath("some_file")
    file_path.touch()

    dialog = qtrio.dialogs.create_file_open_dialog()

    trio_file_path = trio.Path(file_path)

    async def user():
        await emissions.channel.receive()

        await dialog.set_path(path=trio_file_path)

        assert dialog.accept_button is not None
        dialog.accept_button.click()

    async with qtrio.enter_emissions_channel(signals=[dialog.shown]) as emissions:
        async with trio.open_nursery() as nursery:
            nursery.start_soon(user)

            selected_path = await dialog.wait()

    assert selected_path == trio_file_path


async def test_file_save_raises_for_path_selection_when_not_active(
    qtbot: pytestqt.qtbot.QtBot,
) -> None:
    dialog = qtrio.dialogs.create_file_save_dialog()

    with pytest.raises(qtrio.DialogNotActiveError):
        await dialog.set_path(path=trio.Path())


async def test_information_message_box(qtbot: pytestqt.qtbot.QtBot) -> None:
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


async def test_information_message_box_cancel(qtbot: pytestqt.qtbot.QtBot) -> None:
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


async def test_text_input_dialog(qtbot: pytestqt.qtbot.QtBot) -> None:
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


async def test_text_input_dialog_cancel(qtbot: pytestqt.qtbot.QtBot) -> None:
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


async def test_progress_dialog_dot_dot_dot(
    qtbot: pytestqt.qtbot.QtBot, optional_parent: typing.Optional[QtWidgets.QWidget]
) -> None:
    dialog = qtrio.dialogs.create_progress_dialog(parent=optional_parent)

    with qtrio._qt.connection(signal=dialog.shown, slot=qtbot.addWidget):
        async with dialog.manage():
            pass


async def test_progress_dialog_cancel_raises(
    qtbot: pytestqt.qtbot.QtBot, optional_parent: typing.Optional[QtWidgets.QWidget]
) -> None:
    dialog = qtrio.dialogs.create_progress_dialog(
        cancel_button_text="cancel here",
        parent=optional_parent,
    )

    with qtrio._qt.connection(signal=dialog.shown, slot=qtbot.addWidget):
        with pytest.raises(qtrio.UserCancelledError):
            async with dialog.manage():
                assert dialog.dialog is not None
                dialog.dialog.cancel()


async def test_progress_dialog_cancel_cancels_context(
    qtbot: pytestqt.qtbot.QtBot,
    optional_parent: typing.Optional[QtWidgets.QWidget],
) -> None:
    dialog = qtrio.dialogs.create_progress_dialog(
        cancel_button_text="cancel here",
        parent=optional_parent,
    )

    cancelled = False

    with pytest.raises(qtrio.UserCancelledError):
        with qtrio._qt.connection(signal=dialog.shown, slot=qtbot.addWidget):
            async with dialog.manage():
                try:
                    assert dialog.cancel_button is not None
                    dialog.cancel_button.click()
                    await trio.sleep(math.inf)
                except trio.Cancelled:
                    cancelled = True
                    raise

    assert cancelled


def test_dialog_button_box_buttons_by_role_no_buttons(
    qtbot: pytestqt.qtbot.QtBot,
) -> None:
    dialog = QtWidgets.QDialog()
    assert qtrio.dialogs._dialog_button_box_buttons_by_role(dialog=dialog) == {}
