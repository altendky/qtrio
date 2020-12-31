"""A central location to define QTrio specific exceptions and avoid introducing
inter-module dependency issues."""
import typing
from qtpy import QtCore


class QTrioException(Exception):
    """Base exception for all QTrio exceptions."""

    # https://github.com/sphinx-doc/sphinx/issues/7493
    __module__ = "qtrio"


class NoOutcomesError(QTrioException):
    """Raised if you try to unwrap a :class:`qtrio.Outcomes` which has no outcomes."""

    # https://github.com/sphinx-doc/sphinx/issues/7493
    __module__ = "qtrio"


class EventTypeRegistrationError(QTrioException):
    """Base class for various event type registration exceptions to inherit from."""

    # https://github.com/sphinx-doc/sphinx/issues/7493
    __module__ = "qtrio"


class EventTypeRegistrationFailedError(EventTypeRegistrationError):
    """Raised if the attempt to register a new event type fails."""

    # https://github.com/sphinx-doc/sphinx/issues/7493
    __module__ = "qtrio"

    def __init__(self) -> None:
        super().__init__(
            "Failed to register the event hint, either no available hints remain or the"
            + " program is shutting down."
        )


class RequestedEventTypeUnavailableError(EventTypeRegistrationError):
    """Raised if the requested event type is unavailable."""

    # https://github.com/sphinx-doc/sphinx/issues/7493
    __module__ = "qtrio"

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

    # https://github.com/sphinx-doc/sphinx/issues/7493
    __module__ = "qtrio"

    def __init__(self) -> None:
        super().__init__(
            "An event type has already been registered, this must only happen once."
        )


class ReturnCodeError(QTrioException):
    """Wraps a QApplication return code as an exception."""

    # https://github.com/sphinx-doc/sphinx/issues/7493
    __module__ = "qtrio"

    def __eq__(self, other: object) -> bool:
        if type(self) != type(other):
            return False

        # TODO: workaround for https://github.com/python/mypy/issues/4445
        if not isinstance(other, type(self)):  # pragma: no cover
            return False

        return self.args == other.args


class InternalError(QTrioException):
    """Raised when an internal state is inconsistent."""

    # https://github.com/sphinx-doc/sphinx/issues/7493
    __module__ = "qtrio"


class UserCancelledError(QTrioException):
    """Raised when a user requested cancellation of an operation."""

    # https://github.com/sphinx-doc/sphinx/issues/7493
    __module__ = "qtrio"


class RunnerTimedOutError(QTrioException):
    """Raised when a :class:`qtrio.Runner` times out the run."""

    # https://github.com/sphinx-doc/sphinx/issues/7493
    __module__ = "qtrio"


class InvalidInputError(QTrioException):
    """Raised when invalid input is provided such as via a dialog."""

    # https://github.com/sphinx-doc/sphinx/issues/7493
    __module__ = "qtrio"


class DialogNotActiveError(QTrioException):
    """Raised when attempting to interact with a dialog while it is not actually
    available.
    """

    # https://github.com/sphinx-doc/sphinx/issues/7493
    __module__ = "qtrio"
