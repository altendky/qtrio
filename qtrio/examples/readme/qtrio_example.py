import contextlib

import attr
from qts import QtWidgets
import trio
import trio_typing

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


@attr.s
class Dialogs:
    input: qtrio.dialogs.TextInputDialog = attr.ib(factory=create_input)
    output: qtrio.dialogs.MessageBox = attr.ib(factory=create_output)


async def main(
    *,
    task_status: trio_typing.TaskStatus[Dialogs] = trio.TASK_STATUS_IGNORED,
) -> None:
    dialogs = Dialogs()
    task_status.started(dialogs)

    with contextlib.suppress(qtrio.UserCancelledError):
        name = await dialogs.input.wait()
        dialogs.output.text = f"Hi {name}, welcome to the team!"
        await dialogs.output.wait()


if __name__ == "__main__":  # pragma: no cover
    qtrio.run(main)
