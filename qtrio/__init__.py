"""Top-level package for QTrio."""

from ._version import __version__

from ._exceptions import (
    QTrioException,
    NoOutcomesError,
    RegisterEventTypeError,
    ReturnCodeError,
    UserCancelledError,
)

from ._core import (
    wait_signal,
    emissions,
    Outcomes,
    run,
    Runner,
)

from ._pytest import host
