import os
import time
import typing

import qtrio
from qtpy import QtWidgets


clock = time.monotonic


async def main(button: typing.Optional[QtWidgets.QPushButton] = None):
    start = clock()

    def delta():
        return f'{clock() - start:0.3f}'

    if button is None:  # pragma: no cover
        button = QtWidgets.QPushButton()

    button.setText("Exit")

    async with qtrio.enter_emissions_channel(signals=[button.clicked]) as emissions:
        print(f'+++++ before button.show()', delta(), os.getpid())
        button.show()
        print(f'+++++ after button.show()', delta(), os.getpid())

        await emissions.channel.receive()


if __name__ == "__main__":  # pragma: no cover
    qtrio.run(main)
