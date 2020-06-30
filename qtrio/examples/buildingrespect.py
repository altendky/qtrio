import qtrio
from qtpy import QtWidgets


async def main():
    button = QtWidgets.QPushButton()
    button.setText("Exit")

    async with qtrio.open_emissions_channel(signals=[button.clicked]) as emissions:
        async with emissions.channel:
            button.show()

            await emissions.channel.receive()


qtrio.run(main)
