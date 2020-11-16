import contextlib
import typing

from qtpy import QtWidgets

import qtrio
import qtrio.dialogs


def create_input() -> qtrio.dialogs.TextInputDialog:
    return qtrio.dialogs.create_text_input_dialog(
        title="Hello",
        label="Enter your name:",
    )


def create_output() -> qtrio.dialogs.MessageBox:
    return qtrio.dialogs.create_message_box(
        title="Hello",
        text="",
        icon=QtWidgets.QMessageBox.Icon.Question,
        buttons=QtWidgets.QMessageBox.Ok,
    )


async def main(
    input_dialog: typing.Optional[qtrio.dialogs.TextInputDialog] = None,
    output_dialog: typing.Optional[qtrio.dialogs.MessageBox] = None,
) -> None:
    if input_dialog is None:  # pragma: no cover
        input_dialog = create_input()

    if output_dialog is None:  # pragma: no cover
        output_dialog = create_output()

    with contextlib.suppress(qtrio.UserCancelledError):
        name = await input_dialog.wait()

        output_dialog.text = f"Hi {name}, welcome to the team!"

        await output_dialog.wait()


if __name__ == "__main__":  # pragma: no cover
    qtrio.run(main)
