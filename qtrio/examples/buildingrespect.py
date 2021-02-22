import typing

import attr
import qtrio
from qtpy import QtWidgets


@attr.s(auto_attribs=True)
class Widget:
    widget: QtWidgets.QWidget = attr.ib(factory=QtWidgets.QWidget)
    layout: QtWidgets.QLayout = attr.ib(factory=QtWidgets.QVBoxLayout)
    button: QtWidgets.QPushButton = attr.ib(factory=QtWidgets.QPushButton)
    label: QtWidgets.QWidget = attr.ib(factory=QtWidgets.QLabel)

    def setup(self, message: str) -> None:
        self.button.setText("More")

        # start big enough to fit the whole message
        self.label.setText(message)

        self.layout.addWidget(self.button)
        self.layout.addWidget(self.label)
        self.widget.setLayout(self.layout)

    def show(self) -> None:
        self.widget.show()
        self.label.setText("")


async def main(
    widget: typing.Optional[Widget] = None,
    message: str = "Hello world.",
) -> None:
    if widget is None:  # pragma: no cover
        widget = Widget()

    widget.setup(message=message)

    async with qtrio.enter_emissions_channel(
        signals=[widget.button.clicked]
    ) as emissions:
        i = 1
        widget.show()

        async for _ in emissions.channel:  # pragma: no branch
            widget.label.setText(message[:i])
            i += 1

            if i > len(message):
                break

        # wait for another click to finish
        await emissions.channel.receive()


if __name__ == "__main__":  # pragma: no cover
    qtrio.run(main)
