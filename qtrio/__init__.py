"""Top-level package for QTrio."""

from ._version import get_versions

__version__ = get_versions()["version"]
del get_versions

from ._exceptions import (
    QTrioException,
    NoOutcomesError,
    EventTypeRegistrationError,
    EventTypeRegistrationFailedError,
    RequestedEventTypeUnavailableError,
    EventTypeAlreadyRegisteredError,
    ReturnCodeError,
    RunnerTimedOutError,
    UserCancelledError,
    InvalidInputError,
    InternalError,
)

from ._core import (
    enter_emissions_channel,
    open_emissions_nursery,
    Emissions,
    Emission,
    EmissionsNursery,
    Outcomes,
    run,
    Runner,
    registered_event_type,
    register_event_type,
    register_requested_event_type,
    Reenter,
)

from ._qt import Signal
from ._pytest import host
