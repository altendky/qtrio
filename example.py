import qtrio

from qtpy import QtWidgets


async def main():
    widget = QtWidgets.QWidget()
    layout = QtWidgets.QHBoxLayout()
    widget.setLayout(layout)

    increment = QtWidgets.QPushButton()
    increment.setText("+")

    decrement = QtWidgets.QPushButton()
    decrement.setText("-")

    count = 0
    label = QtWidgets.QLabel()
    label.setText(str(count))

    layout.addWidget(decrement)
    layout.addWidget(label)
    layout.addWidget(increment)

    widget.show()

    async for emission in qtrio.emissions([decrement.clicked, increment.clicked]):
        if emission.is_from(decrement.clicked):
            count -= 1
        elif emission.is_from(increment.clicked):
            count += 1

        label.setText(str(count))


qtrio.run(main)
