import typing

from qts import QtWidgets


def create_input() -> QtWidgets.QInputDialog:
    dialog = QtWidgets.QInputDialog()
    dialog.setWindowTitle("Hello")
    dialog.setLabelText("Enter your name:")

    return dialog


def create_output() -> QtWidgets.QMessageBox:
    return QtWidgets.QMessageBox(
        QtWidgets.QMessageBox.Icon.Question,
        "Hello",
        "",
        QtWidgets.QMessageBox.Ok,
    )


class Main:
    def __init__(
        self,
        application: QtWidgets.QApplication,
        input_dialog: typing.Optional[QtWidgets.QInputDialog] = None,
        output_dialog: typing.Optional[QtWidgets.QMessageBox] = None,
    ):
        self.application = application

        if input_dialog is None:  # pragma: no cover
            input_dialog = create_input()

        if output_dialog is None:  # pragma: no cover
            output_dialog = create_output()

        self.input_dialog = input_dialog
        self.output_dialog = output_dialog

    def setup(self) -> None:
        self.input_dialog.accepted.connect(self.input_accepted)
        self.input_dialog.rejected.connect(self.input_rejected)

        self.input_dialog.show()

    def input_accepted(self) -> None:
        name = self.input_dialog.textValue()

        self.output_dialog.setText(f"Hi {name}, welcome to the team!")

        self.output_dialog.finished.connect(self.output_finished)
        self.output_dialog.show()

    def input_rejected(self) -> None:
        self.application.quit()

    def output_finished(self) -> None:
        self.application.quit()


def main() -> None:  # pragma: no cover
    application = QtWidgets.QApplication([])
    application.setQuitOnLastWindowClosed(False)
    main_object = Main(application=application)
    main_object.setup()
    application.exec_()


if __name__ == "__main__":  # pragma: no cover
    main()
