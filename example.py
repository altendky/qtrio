import qtrio
import qtrio._qt
import trio

from qtpy import QtWidgets


async def main():
    application = QtWidgets.QApplication.instance()

    with trio.CancelScope() as cancel_scope:
        with qtrio._qt.connection(signal=application.lastWindowClosed, slot=cancel_scope.cancel):
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

            signals = [decrement.clicked, increment.clicked]

            async with qtrio.open_emissions_channel(signals=signals) as emissions:
                widget.show()

                async with emissions.channel:
                    async for emission in emissions.channel:
                        if emission.is_from(decrement.clicked):
                            count -= 1
                        elif emission.is_from(increment.clicked):
                            count += 1

                        label.setText(str(count))


qtrio.run(main)
