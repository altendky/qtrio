"""A central location to define QTrio specific exceptions and avoid introducing
inter-module dependency issues."""
import sys
import typing

if typing.TYPE_CHECKING or "sphinx_autodoc_typehints" in sys.modules:
    from qts import QtCore


class QTrioException(Exception):
    """Base exception for all QTrio exceptions."""


class NoOutcomesError(QTrioException):
    """Raised if you try to unwrap a :class:`qtrio.Outcomes` which has no outcomes."""


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
        requested_type: typing.Union[int, "QtCore.QEvent.Type"],
        returned_type: typing.Union[int, "QtCore.QEvent.Type"],
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


class InternalError(QTrioException):
    """Raised when an internal state is inconsistent."""


class UserCancelledError(QTrioException):
    """Raised when a user requested cancellation of an operation."""


class RunnerTimedOutError(QTrioException):
    """Raised when a :class:`qtrio.Runner` times out the run."""


class InvalidInputError(QTrioException):
    """Raised when invalid input is provided such as via a dialog."""


class DialogNotActiveError(QTrioException):
    """Raised when attempting to interact with a dialog while it is not actually
    available.
    """


class QTrioWarning(UserWarning):
    """Base warning for all QTrio warnings."""


class ApplicationQuitWarning(QTrioWarning):
    """Emitted when the Qt application quits but QTrio is expecting to manage the
    application lifetime.  See the documentation on
    :ref:`the application lifetime <lifetime>` for more information.
    """
