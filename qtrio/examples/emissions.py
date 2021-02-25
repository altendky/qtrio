import typing

import attr
from qtpy import QtCore
from qtpy import QtGui
from qtpy import QtWidgets
import qtrio
import trio
import trio_typing


class QSignaledWidget(QtWidgets.QWidget):
    """A :class:`QtWidgets.QWidget` with extra signals for events of interest.

    Attributes:
        closed: A signal that will be emitted after a close event.
    """

    closed = QtCore.Signal()
    shown = QtCore.Signal()

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        """Detect close events and emit the ``closed`` signal."""

        super().closeEvent(event)
        if event.isAccepted():
            self.closed.emit()
        else:  # pragma: no cover
            pass

    def showEvent(self, event: QtGui.QShowEvent) -> None:
        """Detect show events and emit the ``shown`` signal."""

        super().showEvent(event)
        if event.isAccepted():
            self.shown.emit()
        else:  # pragma: no cover
            pass


@attr.s(auto_attribs=True)
class Widget:
    """A manager for a simple window with increment and decrement buttons to change a
    counter which is displayed via a widget in the center.
    """

    widget: QSignaledWidget = attr.ib(factory=QSignaledWidget)
    increment: QtWidgets.QPushButton = attr.ib(factory=QtWidgets.QPushButton)
    decrement: QtWidgets.QPushButton = attr.ib(factory=QtWidgets.QPushButton)
    label: QtWidgets.QLabel = attr.ib(factory=QtWidgets.QLabel)
    layout: QtWidgets.QHBoxLayout = attr.ib(factory=QtWidgets.QHBoxLayout)
    count: int = 0
    serving_event: trio.Event = attr.ib(factory=trio.Event)

    def setup(self, title: str, parent: typing.Optional[QtWidgets.QWidget]) -> None:
        self.widget.setParent(parent)

        self.widget.setWindowTitle(title)
        self.widget.setLayout(self.layout)

        self.increment.setText("+")
        self.decrement.setText("-")

        self.label.setText(str(self.count))

        self.layout.addWidget(self.decrement)
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.increment)

    def increment_count(self) -> None:
        """Increment the counter and update the label."""

        self.count += 1
        self.label.setText(str(self.count))

    def decrement_count(self) -> None:
        """Decrement the counter and update the label."""

        self.count -= 1
        self.label.setText(str(self.count))

    async def show(self) -> None:
        """Show the primary widget for this window."""

        self.widget.show()

    async def serve(
        self,
        *,
        task_status: trio_typing.TaskStatus[None] = trio.TASK_STATUS_IGNORED,
    ) -> None:
        signals = [
            self.decrement.clicked,
            self.increment.clicked,
            self.widget.closed,
        ]

        async with qtrio.enter_emissions_channel(signals=signals) as emissions:
            await self.show()
            task_status.started()
            self.serving_event.set()

            async for emission in emissions.channel:
                if emission.is_from(self.decrement.clicked):
                    self.decrement_count()
                elif emission.is_from(self.increment.clicked):
                    self.increment_count()
                elif emission.is_from(self.widget.closed):
                    break
                else:  # pragma: no cover
                    raise qtrio.QTrioException(f"Unexpected emission: {emission}")

    @classmethod
    async def start(
        cls,
        title: str = "QTrio Emissions Example",
        parent: typing.Optional[QtWidgets.QWidget] = None,
        hold_event: typing.Optional[trio.Event] = None,
        *,
        task_status: trio_typing.TaskStatus["Widget"] = trio.TASK_STATUS_IGNORED,
    ) -> None:
        self = cls()
        self.setup(title=title, parent=parent)

        task_status.started(self)

        if hold_event is not None:
            await hold_event.wait()

        await self.serve()
