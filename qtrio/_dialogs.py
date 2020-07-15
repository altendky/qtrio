import contextlib
import os
import sys
import typing

import async_generator
import attr
from qtpy import QtCore
from qtpy import QtWidgets
import trio

import qtrio._qt


@attr.s(auto_attribs=True)
class IntegerDialog:
    parent: QtWidgets.QWidget
    dialog: typing.Optional[QtWidgets.QInputDialog] = None
    edit_widget: typing.Optional[QtWidgets.QWidget] = None
    ok_button: typing.Optional[QtWidgets.QPushButton] = None
    cancel_button: typing.Optional[QtWidgets.QPushButton] = None
    attempt: typing.Optional[int] = None
    result: typing.Optional[int] = None

    shown = qtrio._qt.Signal(QtWidgets.QInputDialog)
    hidden = qtrio._qt.Signal()
    finished = qtrio._qt.Signal(int)  # QtWidgets.QDialog.DialogCode

    @classmethod
    def build(cls, parent: QtCore.QObject = None,) -> "IntegerDialog":
        return cls(parent=parent)

    def setup(self):
        self.result = None

        self.dialog = QtWidgets.QInputDialog(self.parent)

        # TODO: adjust so we can use a context manager?
        self.dialog.finished.connect(self.finished)

        self.dialog.show()

        buttons = dialog_button_box_buttons_by_role(dialog=self.dialog)
        self.ok_button = buttons.get(QtWidgets.QDialogButtonBox.AcceptRole)
        self.cancel_button = buttons.get(QtWidgets.QDialogButtonBox.RejectRole)

        [self.edit_widget] = self.dialog.findChildren(QtWidgets.QLineEdit)

        if self.attempt is None:
            self.attempt = 0
        else:
            self.attempt += 1

        self.shown.emit(self.dialog)

    def teardown(self):
        if self.dialog is not None:
            self.dialog.close()
        self.dialog.finished.disconnect(self.finished)
        self.dialog = None
        self.ok_button = None
        self.cancel_button = None
        self.edit_widget = None

    @contextlib.contextmanager
    def manage(self, finished_event=None):
        with contextlib.ExitStack() as exit_stack:
            if finished_event is not None:
                exit_stack.enter_context(
                    qtrio._qt.connection(
                        signal=self.finished,
                        slot=lambda *args, **kwargs: finished_event.set(),
                    )
                )
            try:
                self.setup()
                yield self
            finally:
                self.teardown()

    async def wait(self):
        while True:
            finished_event = trio.Event()
            with self.manage(finished_event=finished_event):
                await finished_event.wait()
                if self.dialog.result() != QtWidgets.QDialog.Accepted:
                    self.result = None
                else:
                    try:
                        self.result = int(self.dialog.textValue())
                    except ValueError:
                        continue

                return self.result


@attr.s(auto_attribs=True)
class TextInputDialog:
    title: typing.Optional[str] = None
    label: typing.Optional[str] = None
    parent: typing.Optional[QtCore.QObject] = None

    dialog: typing.Optional[QtWidgets.QInputDialog] = None
    accept_button: typing.Optional[QtWidgets.QPushButton] = None
    reject_button: typing.Optional[QtWidgets.QPushButton] = None
    line_edit: typing.Optional[QtWidgets.QLineEdit] = None
    result: typing.Optional[trio.Path] = None

    shown = qtrio._qt.Signal(QtWidgets.QInputDialog)

    def setup(self):
        self.result = None

        self.dialog = QtWidgets.QInputDialog(parent=self.parent)
        if self.label is not None:
            self.dialog.setLabelText(self.label)
        if self.title is not None:
            self.dialog.setWindowTitle(self.title)

        self.dialog.show()

        buttons = dialog_button_box_buttons_by_role(dialog=self.dialog)
        self.accept_button = buttons[QtWidgets.QDialogButtonBox.AcceptRole]
        self.reject_button = buttons[QtWidgets.QDialogButtonBox.RejectRole]

        [self.line_edit] = self.dialog.findChildren(QtWidgets.QLineEdit)

        self.shown.emit(self.dialog)

    def teardown(self):
        if self.dialog is not None:
            self.dialog.close()
        self.dialog = None
        self.accept_button = None
        self.reject_button = None

    @contextlib.contextmanager
    def manage(self):
        try:
            self.setup()
            yield self
        finally:
            self.teardown()

    async def wait(self):
        with self.manage():
            [result] = await qtrio._core.wait_signal(self.dialog.finished)

            if result == QtWidgets.QDialog.Rejected:
                raise qtrio.UserCancelledError()

            self.result = self.dialog.textValue()

            return self.result


def create_text_input_dialog(
    title: typing.Optional[str] = None,
    label: typing.Optional[str] = None,
    parent: typing.Optional[QtCore.QObject] = None,
):
    return TextInputDialog(title=title, label=label, parent=parent)


def dialog_button_box_buttons_by_role(
    dialog: QtWidgets.QDialog,
) -> typing.Mapping[QtWidgets.QDialogButtonBox.ButtonRole, QtWidgets.QAbstractButton]:
    hits = dialog.findChildren(QtWidgets.QDialogButtonBox)

    if len(hits) == 0:
        return {}

    [button_box] = hits
    return {button_box.buttonRole(button): button for button in button_box.buttons()}


@attr.s(auto_attribs=True)
class FileDialog:
    file_mode: QtWidgets.QFileDialog.FileMode
    accept_mode: QtWidgets.QFileDialog.AcceptMode
    dialog: typing.Optional[QtWidgets.QFileDialog] = None
    parent: typing.Optional[QtCore.QObject] = None
    default_directory: typing.Optional[trio.Path] = None
    default_file: typing.Optional[trio.Path] = None
    options: QtWidgets.QFileDialog.Options = QtWidgets.QFileDialog.Options()
    accept_button: typing.Optional[QtWidgets.QPushButton] = None
    reject_button: typing.Optional[QtWidgets.QPushButton] = None
    result: typing.Optional[trio.Path] = None

    shown = qtrio._qt.Signal(QtWidgets.QFileDialog)
    finished = qtrio._qt.Signal(int)  # QtWidgets.QDialog.DialogCode

    def setup(self):
        self.result = None

        extras = {}

        if self.default_directory is not None:
            extras["directory"] = os.fspath(self.default_directory)

        options = self.options
        if sys.platform == "darwin":
            # https://github.com/altendky/qtrio/issues/28
            options |= QtWidgets.QFileDialog.DontUseNativeDialog

        self.dialog = QtWidgets.QFileDialog(
            parent=self.parent, options=options, **extras
        )

        if self.default_file is not None:
            self.dialog.selectFile(os.fspath(self.default_file))

        self.dialog.setFileMode(self.file_mode)
        self.dialog.setAcceptMode(self.accept_mode)

        # TODO: adjust so we can use a context manager?
        self.dialog.finished.connect(self.finished)

        self.dialog.show()

        buttons = dialog_button_box_buttons_by_role(dialog=self.dialog)
        self.accept_button = buttons.get(QtWidgets.QDialogButtonBox.AcceptRole)
        self.reject_button = buttons.get(QtWidgets.QDialogButtonBox.RejectRole)

        self.shown.emit(self.dialog)

    def teardown(self):
        if self.dialog is not None:
            self.dialog.close()
        self.dialog.finished.disconnect(self.finished)
        self.dialog = None
        self.accept_button = None
        self.reject_button = None

    @contextlib.contextmanager
    def manage(self, finished_event=None):
        with contextlib.ExitStack() as exit_stack:
            if finished_event is not None:
                exit_stack.enter_context(
                    qtrio._qt.connection(
                        signal=self.finished,
                        slot=lambda *args, **kwargs: finished_event.set(),
                    )
                )
            try:
                self.setup()
                yield self
            finally:
                self.teardown()

    async def wait(self):
        finished_event = trio.Event()
        with self.manage(finished_event=finished_event):
            await finished_event.wait()
            if self.dialog.result() != QtWidgets.QDialog.Accepted:
                self.result = None
            else:
                [path_string] = self.dialog.selectedFiles()
                self.result = trio.Path(path_string)

            return self.result


def create_file_save_dialog(
    parent: typing.Optional[QtCore.QObject] = None,
    default_directory: typing.Optional[trio.Path] = None,
    default_file: typing.Optional[trio.Path] = None,
    options: QtWidgets.QFileDialog.Options = QtWidgets.QFileDialog.Options(),
):
    return FileDialog(
        parent=parent,
        default_directory=default_directory,
        default_file=default_file,
        options=options,
        file_mode=QtWidgets.QFileDialog.AnyFile,
        accept_mode=QtWidgets.QFileDialog.AcceptSave,
    )


@attr.s(auto_attribs=True)
class MessageBox:
    icon: QtWidgets.QMessageBox.Icon
    title: str
    text: str
    buttons: QtWidgets.QMessageBox.StandardButtons

    parent: typing.Optional[QtCore.QObject] = None

    dialog: typing.Optional[QtWidgets.QMessageBox] = None
    accept_button: typing.Optional[QtWidgets.QPushButton] = None
    result: typing.Optional[trio.Path] = None

    shown = qtrio._qt.Signal(QtWidgets.QMessageBox)

    def setup(self):
        self.result = None

        self.dialog = QtWidgets.QMessageBox(
            self.icon, self.title, self.text, self.buttons, self.parent
        )

        self.dialog.show()

        buttons = dialog_button_box_buttons_by_role(dialog=self.dialog)
        self.accept_button = buttons[QtWidgets.QDialogButtonBox.AcceptRole]

        self.shown.emit(self.dialog)

    def teardown(self):
        if self.dialog is not None:
            self.dialog.close()
        self.dialog = None
        self.accept_button = None

    @contextlib.contextmanager
    def manage(self):
        try:
            self.setup()
            yield self
        finally:
            self.teardown()

    async def wait(self):
        with self.manage():
            [result] = await qtrio._core.wait_signal(self.dialog.finished)

            if result == QtWidgets.QDialog.Rejected:
                raise qtrio.UserCancelledError()


def create_information_message_box(
    icon: QtWidgets.QMessageBox.Icon,
    title: str,
    text: str,
    buttons: QtWidgets.QMessageBox.StandardButtons = QtWidgets.QMessageBox.Ok,
    parent: typing.Optional[QtCore.QObject] = None,
):
    return MessageBox(icon=icon, title=title, text=text, buttons=buttons, parent=parent)


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
