"""A central location to define QTrio specific exceptions and avoid introducing
inter-module dependency issues."""


class QTrioException(Exception):
    """Base exception for all QTrio exceptions."""

    pass


class NoOutcomesError(QTrioException):
    """Raised if you try to unwrap a :class:`qtrio.Outcomes` which has no outcomes."""

    pass


class RegisterEventTypeError(QTrioException):
    """Raised if the attempt to register a new event type fails."""

    pass


class ReturnCodeError(QTrioException):
    """Wraps a QApplication return code as an exception."""

    def __eq__(self, other):
        return type(self) == type(other) and self.args == other.args


class UserCancelledError(QTrioException):
    """Raised when a user requested cancellation of an operation."""

    pass


class RunnerTimedOutError(QTrioException):
    """Raised when a :class:`qtrio.Runner` times out the run."""

    pass
