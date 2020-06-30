import qtrio
from qtpy import QtWidgets
import trio


async def main():
    message = "Hello world."

    label = QtWidgets.QLabel()
    # start big enough to fit the whole message
    label.setText(message)
    label.show()
    label.setText("")

    for i in range(len(message)):
        await trio.sleep(0.5)
        label.setText(message[: i + 1])

    await trio.sleep(3)


qtrio.run(main)
