import typing

import attr
import qtrio
from qtpy import QtWidgets
import trio
import trio_typing


@attr.s(auto_attribs=True, eq=False)
class Widget:
    message: str
    widget: QtWidgets.QWidget = attr.ib(factory=QtWidgets.QWidget)
    layout: QtWidgets.QLayout = attr.ib(factory=QtWidgets.QVBoxLayout)
    button: QtWidgets.QPushButton = attr.ib(factory=QtWidgets.QPushButton)
    label: QtWidgets.QWidget = attr.ib(factory=QtWidgets.QLabel)

    shown_event: trio.Event = attr.ib(factory=trio.Event)

    text_changed = qtrio.Signal(str)

    def setup(self) -> None:
        self.button.setText("More")

        self.layout.addWidget(self.button)
        self.layout.addWidget(self.label)
        self.widget.setLayout(self.layout)

    async def show(self) -> None:
        # TODO: maybe raise if already started?
        # start big enough to fit the whole message
        self.label.setText(self.message)
        self.widget.show()
        self.label.setText("")
        self.shown_event.set()

    def set_text(self, text: str) -> None:
        self.label.setText(text)
        self.text_changed.emit(text)

    async def serve(
        self,
        *,
        task_status: trio_typing.TaskStatus["Widget"] = trio.TASK_STATUS_IGNORED,
    ) -> None:
        async with qtrio.enter_emissions_channel(
            signals=[self.button.clicked]
        ) as emissions:
            i = 1
            task_status.started(self)

            async for _ in emissions.channel:  # pragma: no branch
                self.set_text(self.message[:i])
                i += 1

                if i > len(self.message):
                    break

            # wait for another click to finish
            await emissions.channel.receive()

    @classmethod
    async def create(
        cls,
        message: str,
    ) -> "Widget":
        self = cls(message=message)
        self.setup()

        return self

    @classmethod
    async def start(
        cls,
        message: str,
        *,
        task_status: trio_typing.TaskStatus["Widget"] = trio.TASK_STATUS_IGNORED,
    ) -> None:
        self = await cls.create(message=message)

        await self.show()
        task_status.started(self)

        await self.serve()


if __name__ == "__main__":  # pragma: no cover
    qtrio.run(Widget.start)
