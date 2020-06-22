import contextlib
import typing

import attr
from qtpy import QtCore
from qtpy import QtWidgets

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

    @classmethod
    def build(cls, parent: QtCore.QObject = None,) -> "IntegerDialog":
        return cls(parent=parent)

    def setup(self):
        self.dialog = QtWidgets.QInputDialog(self.parent)

        # TODO: find a better way to trigger population of widgets
        self.dialog.show()

        for widget in self.dialog.findChildren(QtWidgets.QWidget):
            if isinstance(widget, QtWidgets.QLineEdit):
                self.edit_widget = widget
            elif isinstance(widget, QtWidgets.QPushButton):
                if widget.text() == self.dialog.okButtonText():
                    self.ok_button = widget
                elif widget.text() == self.dialog.cancelButtonText():
                    self.cancel_button = widget

            widgets = {self.edit_widget, self.ok_button, self.cancel_button}
            if None not in widgets:
                break
        else:
            raise qtrio._qt.QTrioException("not all widgets found")

        if self.attempt is None:
            self.attempt = 0
        else:
            self.attempt += 1

        self.shown.emit(self.dialog)

    def teardown(self):
        self.edit_widget = None
        self.ok_button = None
        self.cancel_button = None

        if self.dialog is not None:
            self.dialog.hide()
            self.dialog = None
            self.hidden.emit()

    @contextlib.contextmanager
    def manager(self):
        try:
            self.setup()
            yield
        finally:
            self.teardown()

    async def wait(self) -> int:
        while True:
            with self.manager():
                [result] = await qtrio._core.wait_signal(self.dialog.finished)

                if result == QtWidgets.QDialog.Rejected:
                    raise qtrio.UserCancelledError()

                try:
                    self.result = int(self.dialog.textValue())
                except ValueError:
                    continue

            return self.result
