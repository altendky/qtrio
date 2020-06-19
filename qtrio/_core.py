import sys
import traceback
import typing

import async_generator
import attr
import outcome
from qtpy import QtCore
from qtpy import QtGui
from qtpy import QtWidgets
import trio

import qtrio
import qtrio._qt


# https://github.com/spyder-ide/qtpy/pull/214
import qtpy
if qtpy.API in qtpy.PYQT5_API and not hasattr(QtCore, 'SignalInstance'):
    SignalInstance = QtCore.pyqtBoundSignal
else:
    SignalInstance = QtCore.SignalInstance
del qtpy


REENTER_EVENT = QtCore.QEvent.Type(QtCore.QEvent.registerEventType(),)


class ReenterEvent(QtCore.QEvent):
    pass


class Reenter(QtCore.QObject):
    def event(self, event: QtCore.QEvent) -> bool:
        event.fn()
        return False


async def wait_signal(signal: SignalInstance) -> typing.Any:
    event = trio.Event()
    result = None

    def slot(*args):
        nonlocal result
        result = args
        event.set()

    connection = signal.connect(slot)

    try:
        await event.wait()
    finally:
        signal.disconnect(connection)

    return result


@attr.s(auto_attribs=True, frozen=True, slots=True)
class Outcomes:
    """This class holds the :class:`outcomes.Outcome`s of both the Trio and the Qt
    application execution.

    Args:
        qt: The Qt application :class:`outcomes.Outcome`
        trio: The Trio async function :class:`outcomes.Outcome`
    """

    qt: typing.Optional[outcome.Outcome] = None
    trio: typing.Optional[outcome.Outcome] = None

    def unwrap(self):
        """Unwrap either the Trio or Qt outcome.  First, errors are given priority over
        success values.  Second, the Trio outcome gets priority over the Qt outcome.  If
        both are still None a :class:`NoOutcomesError` is raised.
        """

        if self.trio is not None:
            # highest priority to the Trio outcome, if it is an error we are done
            result = self.trio.unwrap()

            # since a Trio result is higher priority, we only care if Qt gave an error
            if self.qt is not None:
                self.qt.unwrap()

            # no Qt error so go ahead and return the Trio result
            return result
        elif self.qt is not None:
            # either it is a value that gets returned or an error that gets raised
            return self.qt.unwrap()

        # neither Trio nor Qt outcomes have been set so we have nothing to unwrap()
        raise qtrio.NoOutcomesError()


def run(async_fn, done_callback=None) -> Outcomes:
    """Run a Trio-flavored async function in guest mode on a Qt host application, and
    return the outcomes.

    Returns:
        The :class:`Outcomes` with both the Trio and Qt outcomes.
    """
    runner = Runner(done_callback=done_callback)
    runner.run(async_fn)

    return runner.outcomes


def outcome_from_application_return_code(return_code: int) -> outcome.Outcome:
    """Create either an :class:`outcome.Value` in the case of a 0 `return_code` or an
    :class:`outcome.Error` with a :class:`ReturnCodeError` otherwise.

    Args:
        return_code: The return code to be processed.
    """

    if return_code == 0:
        return outcome.Value(return_code)

    return outcome.Error(qtrio.ReturnCodeError(return_code))


@attr.s(auto_attribs=True, slots=True)
class Runner:
    """This class helps run Trio in guest mode on a Qt host application.

    Args:

        application: The Qt application object to run as the host.
        quit_application: When true, the builtin :meth:`done_callback` method will quit
            the application when the async function passed to :meth:`run` has completed.
        reenter: The `QObject` instance which will receive the events requesting
            execution of the needed Trio and user code in the host's event loop and
            thread.
        done_callback: The builtin :meth:`done_callback` will be passed to
            :func:`trio.lowlevel.start_guest_run` but will call the callback passed here
            before (maybe) quitting the application.  The :class:`outcome.Outcome` from
            the completion of the async function passed to :meth:`run` will be passed to
            this callback.
    """

    application: QtGui.QGuiApplication = attr.ib(
        factory=lambda: QtWidgets.QApplication(sys.argv),
    )
    quit_application: bool = True

    reenter: Reenter = attr.ib(factory=Reenter)

    done_callback: typing.Optional[typing.Callable[[Outcomes], None]] = attr.ib(
        default=None
    )

    outcomes: Outcomes = attr.ib(factory=Outcomes, init=False)
    cancel_scope: trio.CancelScope = attr.ib(default=None, init=False)

    def run(
        self,
        async_fn: typing.Callable[
            [QtWidgets.QApplication], typing.Awaitable[None],
        ],
        *args,
        execute_application: bool = True,
    ):
        trio.lowlevel.start_guest_run(
            self.trio_main,
            async_fn,
            args,
            run_sync_soon_threadsafe=self.run_sync_soon_threadsafe,
            done_callback=self.trio_done,
        )

        if execute_application:
            return_code = self.application.exec_()

            self.outcomes = attr.evolve(
                self.outcomes, qt=outcome_from_application_return_code(return_code),
            )

        return self.outcomes

    def run_sync_soon_threadsafe(self, fn):
        event = ReenterEvent(REENTER_EVENT)
        event.fn = fn
        self.application.postEvent(self.reenter, event)

    async def trio_main(self, async_fn, args):
        with trio.CancelScope() as self.cancel_scope:
            with qtrio._qt.connection(
                signal=self.application.lastWindowClosed, slot=self.cancel_scope.cancel,
            ):
                return await async_fn(*args)

    def trio_done(self, run_outcome):
        self.outcomes = attr.evolve(self.outcomes, trio=run_outcome)

        # TODO: should stuff be reported here?  configurable by caller?
        print("---", repr(run_outcome))
        if isinstance(run_outcome, outcome.Error):
            exc = run_outcome.error
            traceback.print_exception(type(exc), exc, exc.__traceback__)

        if self.done_callback is not None:
            self.done_callback(self.outcomes)

        if self.quit_application:
            self.application.quit()


def signal_event(signal: SignalInstance) -> trio.Event:
    # TODO: does this leave these pairs laying around uncollectable?
    event = trio.Event()

    def event_set(*args, **kwargs):
        event.set()

    signal.connect(event_set)
    return event


@async_generator.asynccontextmanager
async def signal_event_manager(signal: SignalInstance):
    event = signal_event(signal)
    yield event
    await event.wait()
