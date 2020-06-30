import typing

import qtrio
from qtpy import QtWidgets


async def main(button: typing.Optional[QtWidgets.QPushButton] = None):
    if button is None:
        button = QtWidgets.QPushButton()

    button.setText("Exit")

    async with qtrio.open_emissions_channel(signals=[button.clicked]) as emissions:
        async with emissions.channel:
            button.show()

            await emissions.channel.receive()


if __name__ == "__main__":
    qtrio.run(main)
