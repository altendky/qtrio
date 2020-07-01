import typing

import qtrio
from qtpy import QtWidgets
import trio


async def main(
    label: typing.Optional[QtWidgets.QWidget] = None,
    message: str = "Hello world.",
    change_delay=0.5,
    close_delay=3,
):
    if label is None:  # pragma: no cover
        label = QtWidgets.QLabel()
    # start big enough to fit the whole message
    label.setText(message)
    label.show()
    label.setText("")

    for i in range(len(message)):
        await trio.sleep(change_delay)
        label.setText(message[: i + 1])

    await trio.sleep(close_delay)


if __name__ == "__main__":  # pragma: no cover
    qtrio.run(main)
