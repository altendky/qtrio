import attr
from qtpy import QtCore
from qtpy import QtWidgets

import qtrio


class QSignaledWidget(QtWidgets.QWidget):
    """A :class:`QtWidgets.QWidget` with extra signals for events of interest.

    Attributes:
        closed: A signal that will be emitted after a close event.
    """

    closed = QtCore.Signal()
    shown = QtCore.Signal()

    def closeEvent(self, event):
        """Detect close events and emit the `closed` signal."""

        super().closeEvent(event)
        if event.isAccepted():
            self.closed.emit()
        else:  # pragma: no cover
            pass

    def showEvent(self, event):
        """Detect show events and emit the `shown` signal."""

        super().showEvent(event)
        if event.isAccepted():
            self.shown.emit()
        else:  # pragma: no cover
            pass


@attr.s(auto_attribs=True)
class Window:
    """A manager for a simple window with increment and decrement buttons to change a
    counter which is displayed via a widget in the center.
    """

    widget: QSignaledWidget
    increment: QtWidgets.QPushButton
    decrement: QtWidgets.QPushButton
    label: QtWidgets.QLabel
    layout: QtWidgets.QHBoxLayout
    count: int = 0

    @classmethod
    def build(cls, title="QTrio Emissions Example", parent=None):
        """Build and lay out the widgets that make up this window."""

        self = cls(
            widget=QSignaledWidget(parent),
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
        """Increment the counter and update the label."""

        self.count += 1
        self.label.setText(str(self.count))

    def decrement_count(self):
        """Decrement the counter and update the label."""

        self.count -= 1
        self.label.setText(str(self.count))

    def show(self):
        """Show the primary widget for this window."""

        self.widget.show()


async def main(window=None):
    """Show the example window and iterate over the relevant signal emissions to respond
    to user interactions with the GUI.
    """
    if window is None:  # pragma: no cover
        window = Window.build()

    signals = [
        window.decrement.clicked,
        window.increment.clicked,
        window.widget.closed,
    ]

    async with qtrio.enter_emissions_channel(signals=signals) as emissions:
        window.show()

        async for emission in emissions.channel:
            if emission.is_from(window.decrement.clicked):
                window.decrement_count()
            elif emission.is_from(window.increment.clicked):
                window.increment_count()
            elif emission.is_from(window.widget.closed):
                break
            else:  # pragma: no cover
                raise qtrio.QTrioException(f"Unexpected emission: {emission}")
