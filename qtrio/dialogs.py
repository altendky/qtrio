import contextlib
import os
import sys
import typing

import attr
from qtpy import QtWidgets
import trio

import qtrio
import qtrio._qt


if sys.version_info >= (3, 8):
    from typing import Protocol
else:
    from typing_extensions import Protocol


class DialogProtocol(Protocol):
    """The common interface used for working with QTrio dialogs.  To check that a class
    implements this protocol see :func:`qtrio.dialogs.check_dialog_protocol`.
    """

    shown: qtrio.Signal
    """The signal to be emitted when the dialog is shown."""
    finished: qtrio.Signal
    """The signal to be emitted when the dialog is finished."""

    def setup(self) -> None:
        """Setup and show the dialog.  Emit :attr:`qtrio.dialogs.DialogProtocol.shown`
        when done.
        """

    def teardown(self) -> None:
        """Hide and teardown the dialog."""

    async def wait(self) -> object:
        """Show the dialog, wait for the user interaction, and return the result.

        Raises:
            qtrio.InvalidInputError: If the input can't be parsed as an integer.
            qtrio.UserCancelledError: If the user cancels the dialog.
        """


DialogProtocolT = typing.TypeVar("DialogProtocolT", bound=DialogProtocol)


def check_dialog_protocol(
    cls: typing.Type[DialogProtocolT],
) -> typing.Type[DialogProtocolT]:
    """Decorate a class with this to verify it implements the
    :class:`qtrio.dialogs.DialogProtocol` when a type hint checker such as mypy is run
    against the code.  At runtime the passed class is cleanly returned.

    Arguments:
        cls: The class to verify.
    """
    return cls


@contextlib.contextmanager
def _manage(dialog: DialogProtocol) -> typing.Generator[trio.Event, None, None]:
    """Manage the setup and teardown of a dialog including yielding a
    :class:`trio.Event` that is set when the dialog is finished.

    Arguments:
        dialog: The dialog to be managed.
    """
    finished_event = trio.Event()

    def slot(*args: object, **kwargs: object) -> None:
        """Accept and ignore all arguments, then set the event."""
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
    """Create a mapping from button roles to their corresponding buttons."""

    hits = dialog.findChildren(QtWidgets.QDialogButtonBox)

    if len(hits) == 0:
        return {}

    [button_box] = hits
    return {button_box.buttonRole(button): button for button in button_box.buttons()}


@check_dialog_protocol
@attr.s(auto_attribs=True)
class IntegerDialog:
    """Manage a dialog for inputting an integer from the user.  Generally instances
    should be built via :func:`qtrio.dialogs.create_integer_dialog`."""

    parent: typing.Optional[QtWidgets.QWidget] = None
    """The parent widget for the dialog."""

    dialog: typing.Optional[QtWidgets.QInputDialog] = None
    """The actual dialog widget instance."""
    edit_widget: typing.Optional[QtWidgets.QLineEdit] = None
    """The line edit that the user will enter the input into."""
    accept_button: typing.Optional[QtWidgets.QPushButton] = None
    """The entry confirmation button."""
    reject_button: typing.Optional[QtWidgets.QPushButton] = None
    """The input cancellation button."""

    result: typing.Optional[int] = None
    """The result of parsing the user input."""

    shown = qtrio.Signal(QtWidgets.QInputDialog)
    """See :attr:`qtrio.dialogs.DialogProtocol.shown`."""
    finished = qtrio.Signal(int)  # QtWidgets.QDialog.DialogCode
    """See :attr:`qtrio.dialogs.DialogProtocol.finished`."""

    def setup(self) -> None:
        """See :meth:`qtrio.dialogs.DialogProtocol.setup`."""

        self.result = None

        self.dialog = QtWidgets.QInputDialog(self.parent)

        # TODO: adjust so we can use a context manager?
        self.dialog.finished.connect(self.finished)

        self.dialog.show()

        buttons = _dialog_button_box_buttons_by_role(dialog=self.dialog)
        self.accept_button = buttons.get(QtWidgets.QDialogButtonBox.AcceptRole)
        self.reject_button = buttons.get(QtWidgets.QDialogButtonBox.RejectRole)

        [self.edit_widget] = self.dialog.findChildren(QtWidgets.QLineEdit)

        self.shown.emit(self.dialog)

    def teardown(self) -> None:
        """See :meth:`qtrio.dialogs.DialogProtocol.teardown`."""

        if self.dialog is not None:
            self.dialog.close()
            self.dialog.finished.disconnect(self.finished)
        self.dialog = None
        self.accept_button = None
        self.reject_button = None
        self.edit_widget = None

    async def wait(self) -> int:
        """See :meth:`qtrio.dialogs.DialogProtocol.wait`."""
        with _manage(dialog=self) as finished_event:
            if self.dialog is None:  # pragma: no cover
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


def create_integer_dialog(
    parent: typing.Optional[QtWidgets.QWidget] = None,
) -> IntegerDialog:
    """Create an integer input dialog.

    Arguments:
        parent: See :attr:`qtrio.dialogs.IntegerDialog.parent`.

    Returns:
        The dialog manager.
    """
    return IntegerDialog(parent=parent)


@check_dialog_protocol
@attr.s(auto_attribs=True)
class TextInputDialog:
    """Manage a dialog for inputting an integer from the user.  Generally instances
    should be built via :func:`qtrio.dialogs.create_text_input_dialog`."""

    title: typing.Optional[str] = None
    """The title of the dialog."""
    label: typing.Optional[str] = None
    """The label for the input widget."""
    parent: typing.Optional[QtWidgets.QWidget] = None
    """The parent widget for the dialog."""

    dialog: typing.Optional[QtWidgets.QInputDialog] = None
    """The actual dialog widget instance."""
    accept_button: typing.Optional[QtWidgets.QPushButton] = None
    """The entry confirmation button."""
    reject_button: typing.Optional[QtWidgets.QPushButton] = None
    """The input cancellation button."""
    line_edit: typing.Optional[QtWidgets.QLineEdit] = None
    """The line edit that the user will enter the input into."""

    result: typing.Optional[str] = None
    """The result of parsing the user input."""

    shown = qtrio.Signal(QtWidgets.QInputDialog)
    """See :attr:`qtrio.dialogs.DialogProtocol.shown`."""
    finished = qtrio.Signal(int)  # QtWidgets.QDialog.DialogCode
    """See :attr:`qtrio.dialogs.DialogProtocol.finished`."""

    def setup(self) -> None:
        """See :meth:`qtrio.dialogs.DialogProtocol.setup`."""

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
        """See :meth:`qtrio.dialogs.DialogProtocol.teardown`."""

        if self.dialog is not None:
            self.dialog.close()
            self.dialog.finished.disconnect(self.finished)
        self.dialog = None
        self.accept_button = None
        self.reject_button = None

    async def wait(self) -> str:
        """See :meth:`qtrio.dialogs.DialogProtocol.wait`."""

        with _manage(dialog=self) as finished_event:
            if self.dialog is None:  # pragma: no cover
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
    parent: typing.Optional[QtWidgets.QWidget] = None,
) -> TextInputDialog:
    """Create a text input dialog.

    Arguments:
        title: The text to use for the input dialog title bar.
        label: The text to use for the input text box label.
        parent: See :attr:`qtrio.dialogs.IntegerDialog.parent`.

    Returns:
        The dialog manager.
    """
    return TextInputDialog(title=title, label=label, parent=parent)


@check_dialog_protocol
@attr.s(auto_attribs=True)
class FileDialog:
    """Manage a dialog for allowing the user to select a file or directory.  Generally
    instances should be built via :func:`qtrio.dialogs.create_file_save_dialog`."""

    file_mode: QtWidgets.QFileDialog.FileMode
    """Controls whether the dialog is for picking an existing vs. new file or directory,
    etc.
    """
    accept_mode: QtWidgets.QFileDialog.AcceptMode
    """Specify an open vs. a save dialog."""
    default_directory: typing.Optional[trio.Path] = None
    """The directory to be initially presented in the dialog."""
    default_file: typing.Optional[trio.Path] = None
    """The file to be initially selected in the dialog."""
    options: QtWidgets.QFileDialog.Option = QtWidgets.QFileDialog.Option()
    """Miscellaneous options.  See the Qt documentation."""
    parent: typing.Optional[QtWidgets.QWidget] = None
    """The parent widget for the dialog."""

    dialog: typing.Optional[QtWidgets.QFileDialog] = None
    """The actual dialog widget instance."""
    accept_button: typing.Optional[QtWidgets.QPushButton] = None
    """The confirmation button."""
    reject_button: typing.Optional[QtWidgets.QPushButton] = None
    """The cancellation button."""

    result: typing.Optional[trio.Path] = None
    """The path selected by the user."""

    shown = qtrio.Signal(QtWidgets.QFileDialog)
    """See :attr:`qtrio.dialogs.DialogProtocol.shown`."""
    finished = qtrio.Signal(int)  # QtWidgets.QDialog.DialogCode
    """See :attr:`qtrio.dialogs.DialogProtocol.finished`."""

    def setup(self) -> None:
        """See :meth:`qtrio.dialogs.DialogProtocol.setup`."""

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
        """See :meth:`qtrio.dialogs.DialogProtocol.teardown`."""

        if self.dialog is not None:
            self.dialog.close()
            self.dialog.finished.disconnect(self.finished)
        self.dialog = None
        self.accept_button = None
        self.reject_button = None

    async def wait(self) -> trio.Path:
        """See :meth:`qtrio.dialogs.DialogProtocol.wait`."""

        with _manage(dialog=self) as finished_event:
            if self.dialog is None:  # pragma: no cover
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
    parent: typing.Optional[QtWidgets.QWidget] = None,
    default_directory: typing.Optional[trio.Path] = None,
    default_file: typing.Optional[trio.Path] = None,
    options: QtWidgets.QFileDialog.Option = QtWidgets.QFileDialog.Option(),
) -> FileDialog:
    """Create an open or save dialog.

    Arguments:
        parent: See :attr:`qtrio.dialogs.FileDialog.parent`.
        default_directory: See :attr:`qtrio.dialogs.FileDialog.default_directory`.
        default_file: See :attr:`qtrio.dialogs.FileDialog.default_file`.
        options: See :attr:`qtrio.dialogs.FileDialog.options`.
    """
    return FileDialog(
        parent=parent,
        default_directory=default_directory,
        default_file=default_file,
        options=options,
        file_mode=QtWidgets.QFileDialog.AnyFile,
        accept_mode=QtWidgets.QFileDialog.AcceptSave,
    )


@check_dialog_protocol
@attr.s(auto_attribs=True)
class MessageBox:
    """Manage a message box for notifying the user.  Generally instances should be built
    via :func:`qtrio.dialogs.create_message_box`.
    """

    title: str
    """The message box title."""
    text: str
    """The message text shown inside the dialog."""
    icon: QtWidgets.QMessageBox.Icon
    """The icon shown inside the dialog."""
    buttons: QtWidgets.QMessageBox.StandardButtons
    """The buttons to be shown in the dialog."""
    parent: typing.Optional[QtWidgets.QWidget] = None
    """The parent widget for the dialog."""

    dialog: typing.Optional[QtWidgets.QMessageBox] = None
    """The actual dialog widget instance."""
    accept_button: typing.Optional[QtWidgets.QPushButton] = None
    """The button to accept the dialog."""

    result: typing.Optional[trio.Path] = None
    """Not generally relevant for a message box."""

    shown = qtrio.Signal(QtWidgets.QMessageBox)
    """See :attr:`qtrio.dialogs.DialogProtocol.shown`."""
    finished = qtrio.Signal(int)  # QtWidgets.QDialog.DialogCode
    """See :attr:`qtrio.dialogs.DialogProtocol.finished`."""

    def setup(self) -> None:
        """See :meth:`qtrio.dialogs.DialogProtocol.setup`."""

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
        """See :meth:`qtrio.dialogs.DialogProtocol.teardown`."""

        if self.dialog is not None:
            self.dialog.close()
        self.dialog = None
        self.accept_button = None

    async def wait(self) -> None:
        """See :meth:`qtrio.dialogs.DialogProtocol.wait`."""

        with _manage(dialog=self) as finished_event:
            if self.dialog is None:  # pragma: no cover
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
    parent: typing.Optional[QtWidgets.QWidget] = None,
) -> MessageBox:
    """Create a message box.

    Arguments:
        title: See :attr:`qtrio.dialogs.MessageBox.title`.
        text: See :attr:`qtrio.dialogs.MessageBox.text`.
        icon: See :attr:`qtrio.dialogs.MessageBox.icon`.
        buttons: See :attr:`qtrio.dialogs.MessageBox.buttons`.
        parent: See :attr:`qtrio.dialogs.MessageBox.parent`.
    """
    return MessageBox(icon=icon, title=title, text=text, buttons=buttons, parent=parent)
