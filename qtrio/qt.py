import typing

from qts import QtCore

import qtrio._core


class ReenterEvent(QtCore.QEvent):
    """A proper ``ReenterEvent`` for reentering into the Qt host loop."""

    def __init__(self, fn: typing.Callable[[], object]):
        super().__init__(qtrio._core._reenter_event_type)
        self.fn = fn


class Reenter(QtCore.QObject):
    """A ``QtCore.QObject`` for handling reenter events."""

    def event(self, event: QtCore.QEvent) -> bool:
        """Qt calls this when the object receives an event."""

        reenter_event = typing.cast(Reenter, event)
        reenter_event.fn()
        return False
