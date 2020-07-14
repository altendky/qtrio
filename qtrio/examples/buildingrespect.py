import typing

import qtrio
from qtpy import QtWidgets


async def main(button: typing.Optional[QtWidgets.QPushButton] = None):
    if button is None:  # pragma: no cover
        button = QtWidgets.QPushButton()

    button.setText("Exit")

    async with qtrio.enter_emissions_channel(signals=[button.clicked]) as emissions:
        button.show()

        await emissions.channel.receive()


if __name__ == "__main__":  # pragma: no cover
    qtrio.run(main)
