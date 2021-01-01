"""Top-level package for QTrio."""

from qtrio._version import get_versions

__version__: str = get_versions()["version"]  # type: ignore[no-untyped-call]
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
    DialogNotActiveError,
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
