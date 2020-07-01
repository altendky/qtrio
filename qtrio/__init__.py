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
    wait_signal_context,
    open_emissions_channel,
    Emissions,
    Emission,
    Outcomes,
    run,
    Runner,
)

from ._pytest import host
from ._qt import connection
