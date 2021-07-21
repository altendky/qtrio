import typing

import attr
import qtrio
from qts import QtWidgets
import trio
import trio_typing


@attr.s(auto_attribs=True, eq=False)
class Widget:
    message: str
    change_delay: float = 0.5
    close_delay: float = 3
    label: QtWidgets.QLabel = attr.ib(factory=QtWidgets.QLabel)

    text_changed = qtrio.Signal(str)

    done_event: trio.Event = attr.ib(factory=trio.Event)

    def setup(self) -> None:
        self.label.setText(self.message)
        self.label.setText("")

    async def show(self) -> None:
        # TODO: maybe raise if already started?
        # start big enough to fit the whole message
        self.label.setText(self.message)
        self.label.show()
        self.label.setText("")

    def set_text(self, text: str) -> None:
        self.label.setText(text)
        self.text_changed.emit(text)

    async def serve(
        self,
        *,
        task_status: trio_typing.TaskStatus[None] = trio.TASK_STATUS_IGNORED,
    ) -> None:
        await self.show()
        task_status.started()
        partial_message = ""
        for character in self.message:
            partial_message += character

            await trio.sleep(self.change_delay)
            self.set_text(partial_message)

        await trio.sleep(self.close_delay)
        self.done_event.set()


async def start_widget(
    message: str,
    change_delay: float = 0.5,
    close_delay: float = 3,
    hold_event: typing.Optional[trio.Event] = None,
    *,
    cls: typing.Type[Widget] = Widget,
    task_status: trio_typing.TaskStatus[Widget] = trio.TASK_STATUS_IGNORED,
) -> None:
    self = cls(message=message, change_delay=change_delay, close_delay=close_delay)
    self.setup()

    task_status.started(self)

    if hold_event is not None:
        await hold_event.wait()

    await self.serve()


if __name__ == "__main__":  # pragma: no cover
    qtrio.run(start_widget, "Hello world.")
