"""Top-level package for QTrio."""

from ._version import __version__

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
    DialogNotActiveError,
    QTrioWarning,
    ApplicationQuitWarning,
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
)

from ._qt import Signal
