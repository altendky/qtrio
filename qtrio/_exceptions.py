"""A central location to define QTrio specific exceptions and avoid introducing
inter-module dependency issues."""
import typing
from qtpy import QtCore


class QTrioException(Exception):
    """Base exception for all QTrio exceptions."""

    pass


class NoOutcomesError(QTrioException):
    """Raised if you try to unwrap a :class:`qtrio.Outcomes` which has no outcomes."""

    pass


class EventTypeRegistrationError(QTrioException):
    """Base class for various event type registration exceptions to inherit from."""


class EventTypeRegistrationFailedError(EventTypeRegistrationError):
    """Raised if the attempt to register a new event type fails."""

    def __init__(self) -> None:
        super().__init__(
            "Failed to register the event hint, either no available hints remain or the"
            + " program is shutting down."
        )


class RequestedEventTypeUnavailableError(EventTypeRegistrationError):
    """Raised if the requested event type is unavailable."""

    def __init__(
        self,
        requested_type: typing.Union[int, QtCore.QEvent.Type],
        returned_type: typing.Union[int, QtCore.QEvent.Type],
    ) -> None:
        super().__init__(
            f"Failed acquire the requested type ({requested_type}), got back"
            + f" ({returned_type}) instead."
        )


class EventTypeAlreadyRegisteredError(EventTypeRegistrationError):
    """Raised when a request is made to register an event type but a type has already
    been registered previously."""

    def __init__(self) -> None:
        super().__init__(
            "An event type has already been registered, this must only happen once."
        )


class ReturnCodeError(QTrioException):
    """Wraps a QApplication return code as an exception."""

    def __eq__(self, other: object) -> bool:
        if type(self) != type(other):
            return False

        # TODO: workaround for https://github.com/python/mypy/issues/4445
        if not isinstance(other, type(self)):  # pragma: no cover
            return False

        return self.args == other.args


class UserCancelledError(QTrioException):
    """Raised when a user requested cancellation of an operation."""

    pass


class RunnerTimedOutError(QTrioException):
    """Raised when a :class:`qtrio.Runner` times out the run."""

    pass


class InvalidInputError(QTrioException):
    """Raised when invalid input is provided such as via a dialog."""

    pass
