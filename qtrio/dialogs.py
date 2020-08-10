import abc
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


class AbstractDialog:
    """The common interface used for working with QTrio dialogs.  To minimize the
    involvement of inheritance this class does not use :class:`abc.ABC` or
    :class:`abc.ABCMeta`.  Also note that ``@property`` is used for instance attributes.
    While only using :func:`abc.abstractmethod` means there is no runtime check made,
    ``mypy`` is able to check for instantiation of abstract classes.
    """
    @property
    @abc.abstractmethod
    def finished(self) -> qtrio._qt.Signal:
        """The signal emitted when the dialog is finished."""
        # should really be QtWidgets.QDialog.DialogCode not int

    @abc.abstractmethod
    def setup(self) -> None:
        """Setup and show the dialog."""

    @abc.abstractmethod
    def teardown(self) -> None:
        """Teardown and hide the dialog."""

    @abc.abstractmethod
    async def wait(self) -> object:
        """Show the dialog, wait for the user interction, and return the result.  Raises
        :class:`qtrio.UserCancelledError` if the user cancels the dialog."""


@contextlib.contextmanager
def _manage(dialog: AbstractDialog) -> typing.Generator[trio.Event, None, None]:
    finished_event = trio.Event()

    def slot(*args: object, **kwargs: object) -> None:
        finished_event.set()

    with qtrio._qt.connection(signal=dialog.finished, slot=slot):
        try:
            dialog.setup()
            yield finished_event
        finally:
            dialog.teardown()


def _dialog_button_box_buttons_by_role(
    dialog: QtWidgets.QDialog,
) -> typing.Mapping[QtWidgets.QDialogButtonBox.ButtonRole, QtWidgets.QAbstractButton]:
    hits = dialog.findChildren(QtWidgets.QDialogButtonBox)

    if len(hits) == 0:
        return {}

    [button_box] = hits
    return {button_box.buttonRole(button): button for button in button_box.buttons()}


@attr.s(auto_attribs=True)
class IntegerDialog(AbstractDialog):
    """Manage a dialog for inputting an integer from the user.

    Attributes:
        parent: The parent widget for the dialog.
        dialog: The actual dialog widget instance.
        edit_widget: The line edit that the user will enter the input into.
        ok_button: The entry confirmation button.
        cancel_button: The input cancellation button.
        result: The result of parsing the user input.
        shown: The signal emitted when the dialog is shown.
        finished: The signal emitted when the dialog is finished.
    """

    parent: QtWidgets.QWidget

    dialog: typing.Optional[QtWidgets.QInputDialog] = None
    edit_widget: typing.Optional[QtWidgets.QLineEdit] = None
    ok_button: typing.Optional[QtWidgets.QPushButton] = None
    cancel_button: typing.Optional[QtWidgets.QPushButton] = None

    result: typing.Optional[int] = None

    shown = qtrio._qt.Signal(QtWidgets.QInputDialog)
    finished = qtrio._qt.Signal(int)  # QtWidgets.QDialog.DialogCode

    def setup(self) -> None:
        """Create the actual dialog widget and perform related setup activities
        including showing the widget and emitting
        :attr:`qtrio.dialogs.IntegerDialog.shown` when done.
        """
        self.result = None

        self.dialog = QtWidgets.QInputDialog(self.parent)

        # TODO: adjust so we can use a context manager?
        self.dialog.finished.connect(self.finished)

        self.dialog.show()

        buttons = _dialog_button_box_buttons_by_role(dialog=self.dialog)
        self.ok_button = buttons.get(QtWidgets.QDialogButtonBox.AcceptRole)
        self.cancel_button = buttons.get(QtWidgets.QDialogButtonBox.RejectRole)

        [self.edit_widget] = self.dialog.findChildren(QtWidgets.QLineEdit)

        self.shown.emit(self.dialog)

    def teardown(self) -> None:
        """Teardown the dialog, signal and slot connections, widget references, etc."""
        if self.dialog is not None:
            self.dialog.close()
            self.dialog.finished.disconnect(self.finished)
        self.dialog = None
        self.ok_button = None
        self.cancel_button = None
        self.edit_widget = None

    async def wait(self) -> int:
        """Setup the dialog, wait for the user input, teardown, and return the user
        input.  Raises :class:`qtrio.UserCancelledError` if the user cancels the dialog.
        Raises :class:`qtrio.InvalidInputError` if the input can't be parsed as an
        integer.
        """
        with _manage(dialog=self) as finished_event:
            if self.dialog is None:
                raise qtrio.InternalError(
                    "Dialog not assigned while it is being managed."
                )

            await finished_event.wait()

            if self.dialog.result() != QtWidgets.QDialog.Accepted:
                raise qtrio.UserCancelledError()

            try:
                self.result = int(self.dialog.textValue())
            except ValueError:
                raise qtrio.InvalidInputError()

            return self.result


def create_integer_dialog(parent: QtCore.QObject = None,) -> IntegerDialog:
    return IntegerDialog(parent=parent)


@attr.s(auto_attribs=True)
class TextInputDialog(AbstractDialog):
    """Manage a dialog for inputting an integer from the user.

    Attributes:
        title: The title of the dialog.
        label: The label for the input widget.
        parent: The parent widget for the dialog.

        dialog: The actual dialog widget instance.
        edit_widget: The line edit that the user will enter the input into.
        ok_button: The entry confirmation button.
        cancel_button: The input cancellation button.
        result: The result of parsing the user input.
        shown: The signal emitted when the dialog is shown.
        finished: The signal emitted when the dialog is finished.
    """

    title: typing.Optional[str] = None
    label: typing.Optional[str] = None
    parent: typing.Optional[QtCore.QObject] = None

    dialog: typing.Optional[QtWidgets.QInputDialog] = None
    accept_button: typing.Optional[QtWidgets.QPushButton] = None
    reject_button: typing.Optional[QtWidgets.QPushButton] = None
    line_edit: typing.Optional[QtWidgets.QLineEdit] = None

    result: typing.Optional[str] = None

    shown = qtrio._qt.Signal(QtWidgets.QInputDialog)
    finished = qtrio._qt.Signal(int)  # QtWidgets.QDialog.DialogCode

    def setup(self) -> None:
        self.result = None

        self.dialog = QtWidgets.QInputDialog(parent=self.parent)
        if self.label is not None:
            self.dialog.setLabelText(self.label)
        if self.title is not None:
            self.dialog.setWindowTitle(self.title)

        # TODO: adjust so we can use a context manager?
        self.dialog.finished.connect(self.finished)
        self.dialog.show()

        buttons = _dialog_button_box_buttons_by_role(dialog=self.dialog)
        self.accept_button = buttons[QtWidgets.QDialogButtonBox.AcceptRole]
        self.reject_button = buttons[QtWidgets.QDialogButtonBox.RejectRole]

        [self.line_edit] = self.dialog.findChildren(QtWidgets.QLineEdit)

        self.shown.emit(self.dialog)

    def teardown(self) -> None:
        if self.dialog is not None:
            self.dialog.close()
            self.dialog.finished.disconnect(self.finished)
        self.dialog = None
        self.accept_button = None
        self.reject_button = None

    async def wait(self) -> str:
        with _manage(dialog=self) as finished_event:
            if self.dialog is None:
                raise qtrio.InternalError(
                    "Dialog not assigned while it is being managed."
                )

            await finished_event.wait()

            dialog_result = self.dialog.result()

            if dialog_result == QtWidgets.QDialog.Rejected:
                raise qtrio.UserCancelledError()

            # TODO: `: str` is a workaround for
            #       https://github.com/spyder-ide/qtpy/pull/217
            text_result: str = self.dialog.textValue()

            self.result = text_result

            return text_result


def create_text_input_dialog(
    title: typing.Optional[str] = None,
    label: typing.Optional[str] = None,
    parent: typing.Optional[QtCore.QObject] = None,
) -> TextInputDialog:
    return TextInputDialog(title=title, label=label, parent=parent)


@attr.s(auto_attribs=True)
class FileDialog(AbstractDialog):
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

    def setup(self) -> None:
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

        buttons = _dialog_button_box_buttons_by_role(dialog=self.dialog)
        self.accept_button = buttons.get(QtWidgets.QDialogButtonBox.AcceptRole)
        self.reject_button = buttons.get(QtWidgets.QDialogButtonBox.RejectRole)

        self.shown.emit(self.dialog)

    def teardown(self) -> None:
        if self.dialog is not None:
            self.dialog.close()
            self.dialog.finished.disconnect(self.finished)
        self.dialog = None
        self.accept_button = None
        self.reject_button = None

    async def wait(self) -> trio.Path:
        with _manage(dialog=self) as finished_event:
            if self.dialog is None:
                raise qtrio.InternalError(
                    "Dialog not assigned while it is being managed."
                )

            await finished_event.wait()
            if self.dialog.result() != QtWidgets.QDialog.Accepted:
                raise qtrio.UserCancelledError()

            [path_string] = self.dialog.selectedFiles()
            self.result = trio.Path(path_string)

            return self.result


def create_file_save_dialog(
    parent: typing.Optional[QtCore.QObject] = None,
    default_directory: typing.Optional[trio.Path] = None,
    default_file: typing.Optional[trio.Path] = None,
    options: QtWidgets.QFileDialog.Options = QtWidgets.QFileDialog.Options(),
) -> FileDialog:
    return FileDialog(
        parent=parent,
        default_directory=default_directory,
        default_file=default_file,
        options=options,
        file_mode=QtWidgets.QFileDialog.AnyFile,
        accept_mode=QtWidgets.QFileDialog.AcceptSave,
    )


@attr.s(auto_attribs=True)
class MessageBox(AbstractDialog):
    icon: QtWidgets.QMessageBox.Icon
    title: str
    text: str
    buttons: QtWidgets.QMessageBox.StandardButtons

    parent: typing.Optional[QtCore.QObject] = None

    dialog: typing.Optional[QtWidgets.QMessageBox] = None
    accept_button: typing.Optional[QtWidgets.QPushButton] = None
    result: typing.Optional[trio.Path] = None

    shown = qtrio._qt.Signal(QtWidgets.QMessageBox)
    finished = qtrio._qt.Signal(int)  # QtWidgets.QDialog.DialogCode

    def setup(self) -> None:
        self.result = None

        self.dialog = QtWidgets.QMessageBox(
            self.icon, self.title, self.text, self.buttons, self.parent
        )

        # TODO: adjust so we can use a context manager?
        self.dialog.finished.connect(self.finished)

        self.dialog.show()

        buttons = _dialog_button_box_buttons_by_role(dialog=self.dialog)
        self.accept_button = buttons[QtWidgets.QDialogButtonBox.AcceptRole]

        self.shown.emit(self.dialog)

    def teardown(self) -> None:
        if self.dialog is not None:
            self.dialog.close()
        self.dialog = None
        self.accept_button = None

    async def wait(self) -> None:
        with _manage(dialog=self) as finished_event:
            if self.dialog is None:
                raise qtrio.InternalError(
                    "Dialog not assigned while it is being managed."
                )

            await finished_event.wait()

            result = self.dialog.result()

            if result == QtWidgets.QDialog.Rejected:
                raise qtrio.UserCancelledError()


def create_message_box(
    title: str,
    text: str,
    icon: QtWidgets.QMessageBox.Icon = QtWidgets.QMessageBox.Information,
    buttons: QtWidgets.QMessageBox.StandardButtons = QtWidgets.QMessageBox.Ok,
    parent: typing.Optional[QtCore.QObject] = None,
) -> MessageBox:
    return MessageBox(icon=icon, title=title, text=text, buttons=buttons, parent=parent)
