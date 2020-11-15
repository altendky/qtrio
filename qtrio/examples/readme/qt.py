import typing

from qtpy import QtCore
from qtpy import QtWidgets


def create_input():
    dialog = QtWidgets.QInputDialog()
    dialog.setWindowTitle("Hello")
    dialog.setLabelText("Enter your name:")

    return dialog


def create_output():
    return QtWidgets.QMessageBox(
        QtWidgets.QMessageBox.Icon.Question,
        "Hello",
        "",
        QtWidgets.QMessageBox.Ok,
    )


class Main:
    def __init__(
        self,
        input_dialog: typing.Optional[QtWidgets.QInputDialog] = None,
        output_dialog: typing.Optional[QtWidgets.QMessageBox] = None,
    ):
        self.input_dialog = input_dialog
        self.output_dialog = output_dialog

    def setup(self):
        if self.input_dialog is None:
            self.input_dialog = create_input()

        self.input_dialog.accepted.connect(self.input_accepted)
        self.input_dialog.rejected.connect(self.input_rejected)

        self.input_dialog.show()

    def input_accepted(self):
        name = self.input_dialog.textValue()

        if self.output_dialog is None:
            self.output_dialog = create_output()

        self.output_dialog.setText(f"Hi {name}, welcome to the team!")

        self.output_dialog.finished.connect(self.output_finished)
        self.output_dialog.show()

    def input_rejected(self):
        QtCore.QCoreApplication.instance().quit()

    def output_finished(self):
        QtCore.QCoreApplication.instance().quit()


def main():
    application = QtWidgets.QApplication([])
    application.setQuitOnLastWindowClosed(False)
    main_object = Main()
    main_object.setup()
    application.exec_()


if __name__ == "__main__":  # pragma: no cover
    main()
