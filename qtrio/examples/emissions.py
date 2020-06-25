import attr
from qtpy import QtCore
from qtpy import QtWidgets
import trio

import qtrio
import qtrio._qt


class QSignalsWidget(QtWidgets.QWidget):
    closed = QtCore.Signal()

    def closeEvent(self, event):
        self.closed.emit()


@attr.s(auto_attribs=True)
class Window:
    widget: QSignalsWidget
    increment: QtWidgets.QPushButton
    decrement: QtWidgets.QPushButton
    label: QtWidgets.QLabel
    layout: QtWidgets.QHBoxLayout
    count: int = 0

    shown = qtrio._qt.Signal()

    @classmethod
    def build(cls, title="QTrio Emissions Example", parent=None):
        self = cls(
            widget=QSignalsWidget(),
            layout=QtWidgets.QHBoxLayout(),
            increment=QtWidgets.QPushButton(),
            decrement=QtWidgets.QPushButton(),
            label=QtWidgets.QLabel(),
        )

        self.widget.setWindowTitle(title)
        self.widget.setLayout(self.layout)

        self.increment.setText("+")
        self.decrement.setText("-")

        self.label.setText(str(self.count))

        self.layout.addWidget(self.decrement)
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.increment)

        return self

    def increment_count(self):
        self.count += 1
        self.label.setText(str(self.count))

    def decrement_count(self):
        self.count -= 1
        self.label.setText(str(self.count))

    def show(self):
        self.widget.show()
        self.shown.emit()


async def main(window=None):
    if window is None:
        window = Window.build()  # pragma: no cover

    signals = [
        window.decrement.clicked,
        window.increment.clicked,
        window.widget.closed,
    ]

    async with qtrio.open_emissions_channel(signals=signals) as emissions:
        window.show()

        async with emissions.channel:
            async for emission in emissions.channel:
                if emission.is_from(window.decrement.clicked):
                    window.decrement_count()
                elif emission.is_from(window.increment.clicked):
                    window.increment_count()
                elif emission.is_from(window.widget.closed):
                    break
