import os
import sys
import threading
import time
import typing

import outcome
import pytest
from qts import QtCore
import qtrio
import qtrio._core
import trio
import trio.testing


@pytest.fixture(
    name="emissions_channel",
    params=[
        qtrio._core.open_emissions_channel,
        qtrio.enter_emissions_channel,
    ],
    ids=["qtrio._core.open_emissions_channel", "qtrio.enter_emissions_channel"],
)
def emissions_channel_fixture(request):
    return request.param


def test_reenter_event_triggers_in_main_thread(qapp):
    """Reenter events posted in another thread result in the function being run in the
    main thread.
    """
    import qtrio.qt

    result = []

    reenter = qtrio.qt.Reenter()

    def post():
        qtrio.register_event_type()
        event = qtrio.qt.ReenterEvent(fn=handler)
        qapp.postEvent(reenter, event)

    def handler():
        result.append(threading.get_ident())

    thread = threading.Thread(target=post)
    thread.start()
    thread.join()

    qapp.processEvents()

    assert result == [threading.get_ident()]


timeout = 40


def test_reenter_event_raises_if_type_not_registered(testdir):
    test_file = r"""
    import pytest

    import qtrio
    import qtrio.qt

    def test():
        with pytest.raises(
            qtrio.InternalError,
            match="reenter event type must be registered",
        ):
            qtrio.qt.ReenterEvent(fn=lambda: None)
    """
    testdir.makepyfile(test_file)

    result = testdir.runpytest_subprocess(timeout=timeout)
    result.assert_outcomes(passed=1)


# TODO: debug further
@pytest.mark.xfail(
    condition=(
        sys.platform == "win32"
        and sys.version_info >= (3, 11)
        and os.environ.get("CI") == "true"
    ),
    reason="the stderr fails to be captured in PyCharm and GitHub Actions",
)
def test_reenter_event_writes_to_stderr_for_exception(capsys, testdir):
    test_file = r"""
    from qts import QtCore

    import qtrio
    import qtrio.qt


    qapp = QtCore.QCoreApplication([])
    qtrio.register_event_type()
    reenter = qtrio.qt.Reenter()
    event = qtrio.qt.ReenterEvent(fn=32)
    qapp.postEvent(reenter, event)
    qapp.processEvents()
    """
    test_path = testdir.makepyfile(test_file)

    result = testdir.runpython(test_path)
    # TODO: diagnostics to be removed
    print(repr(result.stderr.str()))
    print(result.stderr.str())
    result.stderr.re_match_lines(
        lines2=[
            r"^TypeError: 'int' object is not callable$",
            r"^qtrio\._exceptions\.InternalError: Exception while handling a reenter event$",
        ],
    )


def test_run_returns_value(testdir):
    """:func:`qtrio.run()` returns the result of the passed async function."""

    test_file = r"""
    import outcome

    import qtrio

    def test():
        async def main():
            return 29

        result = qtrio.run(main)

        assert result == 29
    """
    testdir.makepyfile(test_file)

    result = testdir.runpytest_subprocess(timeout=timeout)
    result.assert_outcomes(passed=1)


def test_run_passes_args(testdir):
    """:func:`qtrio.run()` passes *args to async function."""

    test_file = r"""
    import outcome

    import qtrio

    def test():
        result = []

        async def main(arg1, arg2):
            result.append(arg1)
            result.append(arg2)

        qtrio.run(main, 27, 32)

        assert result == [27, 32]
    """
    testdir.makepyfile(test_file)

    result = testdir.runpytest_subprocess(timeout=timeout)
    result.assert_outcomes(passed=1)


def test_qt_last_window_closed_does_not_quit_qt_or_cancel_trio(testdir):
    """When the last Qt window is closed, application and Trio both continue."""

    test_file = r"""
    import outcome
    from qts import QtCore
    import trio

    import qtrio


    def test():
        async def main():
            counter = 0

            def f():
                nonlocal counter
                application.lastWindowClosed.emit()
                counter = 1

            application = QtCore.QCoreApplication.instance()
            QtCore.QTimer.singleShot(100, f)

            while True:
                await trio.sleep(0.1)
                if counter == 1:
                    counter += 1
                elif counter > 1:
                    return counter

        result = qtrio.run(async_fn=main)

        assert result == 2
    """
    testdir.makepyfile(test_file)

    result = testdir.runpytest_subprocess(timeout=timeout)
    result.assert_outcomes(passed=1)


def test_qt_quit_cancels_trio_with_custom_application(testdir):
    """When a passed Qt application exits the main Trio function is cancelled."""

    test_file = r"""
    import outcome
    from qts import QtCore
    from qts import QtWidgets
    import trio

    import qtrio


    def test():
        async def main():
            QtCore.QTimer.singleShot(
                100,
                QtCore.QCoreApplication.instance().lastWindowClosed.emit,
            )

            while True:
                await trio.sleep(1)

        runner = qtrio.Runner(application=QtWidgets.QApplication([]))
        outcomes = runner.run(async_fn=main)

        assert outcomes.trio.unwrap() == None
    """
    testdir.makepyfile(test_file)

    result = testdir.runpytest_subprocess(timeout=timeout)
    result.assert_outcomes(passed=1)


def test_run_passes_internal_too_slow_error(testdir):
    """The async function run by :func:`qtrio.run` is executed in the Qt host thread."""

    test_file = r"""
    import math
    import pytest

    import qtrio
    import trio


    def test():
        async def main():
            with trio.fail_after(0):
                await trio.sleep(math.inf)

        with pytest.raises(trio.TooSlowError):
            qtrio.run(main)
    """
    testdir.makepyfile(test_file)

    result = testdir.runpytest_subprocess(timeout=timeout)
    result.assert_outcomes(passed=1)


def test_run_runs_in_main_thread(testdir):
    """The async function run by :func:`qtrio.run` is executed in the Qt host thread."""

    test_file = r"""
    import threading

    import qtrio


    def test():
        async def main():
            return threading.get_ident()

        result = qtrio.run(main)

        assert result == threading.get_ident()
    """
    testdir.makepyfile(test_file)

    result = testdir.runpytest_subprocess(timeout=timeout)
    result.assert_outcomes(passed=1)


def test_runner_runs_in_main_thread(testdir):
    """A directly used :class:`qtrio.Runner` runs the async function in the Qt host
    thread.
    """
    test_file = r"""
    import threading

    import qtrio


    def test():
        async def main():
            return threading.get_ident()

        runner = qtrio.Runner()
        outcomes = runner.run(main)

        assert outcomes.trio.unwrap() == threading.get_ident()
    """
    testdir.makepyfile(test_file)

    result = testdir.runpytest_subprocess(timeout=timeout)
    result.assert_outcomes(passed=1)


def test_done_callback_runs_in_main_thread(testdir):
    """The done callback run by the Trio guest when finished is run in the Qt host
    thread.
    """
    test_file = r"""
    import threading

    import qtrio


    def test():
        result = {}

        async def main():
            pass

        def done_callback(outcomes):
            result['thread_id'] = threading.get_ident()

        qtrio.run(async_fn=main, done_callback=done_callback)

        assert result['thread_id'] == threading.get_ident()
    """
    testdir.makepyfile(test_file)

    result = testdir.runpytest_subprocess(timeout=timeout)
    result.assert_outcomes(passed=1)


def test_done_callback_gets_outcomes(testdir):
    """The done callback is passed the outcomes with the Trio entry filled."""
    test_file = r"""
    import outcome

    import qtrio


    def test():
        result = {}

        async def main():
            return 93

        def done_callback(outcomes):
            result['outcomes'] = outcomes

        qtrio.run(async_fn=main, done_callback=done_callback)

        assert result['outcomes'] == qtrio.Outcomes(
            qt=None,
            trio=outcome.Value(93),
        )
    """
    testdir.makepyfile(test_file)

    result = testdir.runpytest_subprocess(timeout=timeout)
    result.assert_outcomes(passed=1)


def test_out_of_hints_raises(testdir):
    """If there are no available Qt event types remaining
    EventTypeRegistrationFailedError is raised when requesting a type without any
    specific requested value.
    """
    test_file = r"""
    import pytest
    from qts import QtCore
    import qtrio


    def test():
        while QtCore.QEvent.registerEventType() != -1:
            # use up all the event types
            pass

        with pytest.raises(qtrio.EventTypeRegistrationFailedError):
            qtrio.register_event_type()
    """
    testdir.makepyfile(test_file)

    result = testdir.runpytest_subprocess(timeout=timeout)
    result.assert_outcomes(passed=1)


def test_out_of_hints_raises_for_requested(testdir):
    """If there are no available Qt event types remaining
    EventTypeRegistrationFailedError is raised when requesting a type with a specific
    requested value.
    """
    test_file = r"""
    import pytest
    from qts import QtCore
    import qtrio


    def test():
        while QtCore.QEvent.registerEventType() != -1:
            # use up all the event types
            pass

        with pytest.raises(qtrio.EventTypeRegistrationFailedError):
            qtrio.register_requested_event_type(QtCore.QEvent.User)
    """
    testdir.makepyfile(test_file)

    result = testdir.runpytest_subprocess(timeout=timeout)
    result.assert_outcomes(passed=1)


def test_out_of_hints_raises_when_requesting_already_used_type(testdir):
    """An error is raised when a request is made to register an already used event
    type.
    """
    test_file = r"""
    import pytest
    from qts import QtCore
    import qtrio


    def test():
        already_used = QtCore.QEvent.registerEventType()

        with pytest.raises(qtrio.RequestedEventTypeUnavailableError):
            qtrio.register_requested_event_type(already_used)
    """
    testdir.makepyfile(test_file)

    result = testdir.runpytest_subprocess(timeout=timeout)
    result.assert_outcomes(passed=1)


def test_requesting_available_event_type_succeeds(testdir):
    """Requesting an available event type succeeds."""
    test_file = r"""
    from qts import QtCore
    import qtrio


    def test():
        qtrio.register_requested_event_type(QtCore.QEvent.User)

        assert qtrio.registered_event_type() == QtCore.QEvent.User
    """
    testdir.makepyfile(test_file)

    result = testdir.runpytest_subprocess(timeout=timeout)
    result.assert_outcomes(passed=1)


def test_registering_event_type_when_already_registered(testdir):
    """Requesting an available event type succeeds."""
    test_file = r"""
    import pytest
    import qtrio


    def test():
        qtrio.register_event_type()

        with pytest.raises(qtrio.EventTypeAlreadyRegisteredError):
            qtrio.register_event_type()
    """
    testdir.makepyfile(test_file)

    result = testdir.runpytest_subprocess(timeout=timeout)
    result.assert_outcomes(passed=1)


def test_registering_requested_event_type_when_already_registered(testdir):
    """Requesting an available event type succeeds."""
    test_file = r"""
    import pytest
    import qtrio


    def test():
        qtrio.register_event_type()

        with pytest.raises(qtrio.EventTypeAlreadyRegisteredError):
            qtrio.register_requested_event_type(qtrio.registered_event_type())
    """
    testdir.makepyfile(test_file)

    result = testdir.runpytest_subprocess(timeout=timeout)
    result.assert_outcomes(passed=1)


async def test_wait_signal_waits():
    """wait_signal() waits for the signal."""

    timer = QtCore.QTimer()
    timer.setSingleShot(True)

    start = time.monotonic()

    timer.start(100)

    await qtrio._core.wait_signal(timer.timeout)

    end = time.monotonic()

    assert end - start > 0.090


async def test_wait_signal_returns_the_value():
    """wait_signal() waits for the signal."""

    class MyQObject(QtCore.QObject):
        signal = QtCore.Signal(int)

    async def emit(signal, value):
        signal.emit(value)

    instance = MyQObject()

    async with trio.open_nursery() as nursery:
        nursery.start_soon(emit, instance.signal, 17)
        result = await qtrio._core.wait_signal(instance.signal)

    assert result == (17,)


async def test_wait_signal_context_waits():
    """wait_signal_context() waits for the signal."""

    timer = QtCore.QTimer()
    timer.setSingleShot(True)

    async with qtrio._core.wait_signal_context(signal=timer.timeout):
        start = time.monotonic()
        timer.start(100)

    end = time.monotonic()

    assert end - start > 0.090


def test_outcomes_unwrap_none():
    """Unwrapping an empty Outcomes raises NoOutcomesError."""
    this_outcome = qtrio.Outcomes()

    with pytest.raises(qtrio.NoOutcomesError):
        this_outcome.unwrap()


def test_outcomes_unwrap_returns_trio_value_over_qt_none():
    """Unwrapping an Outcomes prioritizes a Trio value over a Qt None."""
    this_outcome = qtrio.Outcomes(trio=outcome.Value(3))
    result = this_outcome.unwrap()

    assert result == 3


def test_outcomes_unwrap_returns_trio_value_over_qt_value():
    """Unwrapping an Outcomes prioritizes a Trio value over a Qt value."""
    this_outcome = qtrio.Outcomes(qt=outcome.Value(2), trio=outcome.Value(3))
    result = this_outcome.unwrap()

    assert result == 3


def test_outcomes_unwrap_raises_trio_error_over_qt_none():
    """Unwrapping an Outcomes prioritizes a Trio error over a Qt None."""

    class LocalUniqueException(Exception):
        pass

    this_outcome = qtrio.Outcomes(trio=outcome.Error(LocalUniqueException()))
    with pytest.raises(LocalUniqueException):
        this_outcome.unwrap()


def test_outcomes_unwrap_raises_trio_error_over_qt_value():
    """Unwrapping an Outcomes prioritizes a Trio error over a Qt value."""

    class LocalUniqueException(Exception):
        pass

    this_outcome = qtrio.Outcomes(
        qt=outcome.Value(9),
        trio=outcome.Error(LocalUniqueException()),
    )

    with pytest.raises(LocalUniqueException):
        this_outcome.unwrap()


def test_outcomes_unwrap_raises_trio_error_over_qt_error():
    """Unwrapping an Outcomes prioritizes a Trio error over a Qt error."""

    class LocalUniqueException(Exception):
        pass

    class AnotherUniqueException(Exception):
        pass

    this_outcome = qtrio.Outcomes(
        qt=outcome.Error(AnotherUniqueException()),
        trio=outcome.Error(LocalUniqueException()),
    )

    with pytest.raises(LocalUniqueException):
        this_outcome.unwrap()


def test_outcomes_unwrap_returns_qt_value_over_trio_none():
    """Unwrapping an Outcomes prioritizes a Qt value over a Trio None."""
    this_outcome = qtrio.Outcomes(qt=outcome.Value(3))
    result = this_outcome.unwrap()

    assert result == 3


def test_outcomes_unwrap_raises_qt_error_over_trio_none():
    """Unwrapping an Outcomes prioritizes a Qt error over a Trio None."""

    class LocalUniqueException(Exception):
        pass

    this_outcome = qtrio.Outcomes(qt=outcome.Error(LocalUniqueException()))
    with pytest.raises(LocalUniqueException):
        this_outcome.unwrap()


def test_outcomes_unwrap_raises_qt_error_over_trio_value():
    """Unwrapping an Outcomes prioritizes a Qt error over a Trio value."""

    class LocalUniqueException(Exception):
        pass

    this_outcome = qtrio.Outcomes(
        qt=outcome.Error(LocalUniqueException()),
        trio=outcome.Value(8),
    )

    with pytest.raises(LocalUniqueException):
        this_outcome.unwrap()


def test_outcome_from_application_return_code_value():
    """Zero return code results in outcome.Value."""
    result = qtrio._core.outcome_from_application_return_code(return_code=0)

    assert result == outcome.Value(0)


def test_outcome_from_application_return_code_error():
    """Non-zero return code result in outcome.Error"""
    result = qtrio._core.outcome_from_application_return_code(return_code=-1)

    assert result == outcome.Error(qtrio.ReturnCodeError(-1))


def test_failed_hosted_trio_exception_on_stdout(testdir):
    """Except is printed when main Trio function raises."""

    test_file = r"""
    from qts import QtCore
    import qtrio


    class UniqueLocalException(Exception):
        pass


    async def test():
        raise UniqueLocalException("with a message")
    """
    testdir.makepyfile(test_file)

    result = testdir.runpytest()
    result.assert_outcomes(failed=1)
    result.stdout.fnmatch_lines(
        lines2=[
            "*test_failed_hosted_trio_exception_on_stdout.UniqueLocalException: with a message*"
        ]
    )


def test_emissions_equal():
    """:class:`Emission` objects created from the same :class:`QtCore.Signal` instance
    and args are equal even if the attributes are different instances.
    """

    class C(QtCore.QObject):
        signal = QtCore.Signal()

    instance = C()

    assert qtrio._core.Emission(
        signal=instance.signal, args=(13,)
    ) == qtrio._core.Emission(signal=instance.signal, args=(13,))


def test_emissions_unequal_by_signal():
    """:class:`Emission` objects with the same arguments but different signals are
    unequal.
    """

    class C(QtCore.QObject):
        signal_a = QtCore.Signal()
        signal_b = QtCore.Signal()

    instance = C()

    assert qtrio._core.Emission(
        signal=instance.signal_a, args=(13,)
    ) != qtrio._core.Emission(signal=instance.signal_b, args=(13,))


def test_emissions_unequal_by_instance():
    """:class:`Emission` objects with the same signal but on different instances are
    unequal.
    """

    class C(QtCore.QObject):
        signal = QtCore.Signal()

    instance_a = C()
    instance_b = C()

    assert qtrio._core.Emission(
        signal=instance_a.signal, args=(13,)
    ) != qtrio._core.Emission(signal=instance_b.signal, args=(13,))


def test_emissions_unequal_by_type():
    """:class:`Emission` objects are not equal to integers"""

    class C(QtCore.QObject):
        signal = QtCore.Signal()

    instance = C()

    assert qtrio._core.Emission(signal=instance.signal, args=(13,)) != 13


def test_emissions_unequal_by_args():
    """:class:`Emission` objects with the same signal but different arguments are
    unequal.
    """

    class C(QtCore.QObject):
        signal = QtCore.Signal()

    instance = C()

    assert qtrio._core.Emission(
        signal=instance.signal, args=(13,)
    ) != qtrio._core.Emission(signal=instance.signal, args=(14,))


async def test_emissions_channel_iterates_one(emissions_channel):
    """Emissions channel yields one emission as expected."""

    class MyQObject(QtCore.QObject):
        signal = QtCore.Signal(int)

    instance = MyQObject()

    async with emissions_channel(signals=[instance.signal]) as emissions:
        instance.signal.emit(93)
        await trio.testing.wait_all_tasks_blocked(cushion=0.01)
        await emissions.aclose()

        async with emissions.channel:
            emissions = [result async for result in emissions.channel]

    assert emissions == [qtrio._core.Emission(signal=instance.signal, args=(93,))]


async def test_emissions_channel_iterates_three(emissions_channel):
    """Emissions channel yields three emissions as expected."""

    class MyQObject(QtCore.QObject):
        signal = QtCore.Signal(int)

    instance = MyQObject()

    async with emissions_channel(signals=[instance.signal]) as emissions:
        for v in [93, 56, 27]:
            instance.signal.emit(v)
            await trio.testing.wait_all_tasks_blocked(cushion=0.01)
        await emissions.aclose()

        async with emissions.channel:
            emissions = [result async for result in emissions.channel]

    assert emissions == [
        qtrio._core.Emission(signal=instance.signal, args=(v,)) for v in [93, 56, 27]
    ]


async def test_emissions_channel_with_three_receives_first(emissions_channel):
    """Emissions channel yields receives first item when requested."""

    class MyQObject(QtCore.QObject):
        signal = QtCore.Signal(int)

    instance = MyQObject()

    async with emissions_channel(signals=[instance.signal]) as emissions:
        for v in [93, 56, 27]:
            instance.signal.emit(v)
            await trio.testing.wait_all_tasks_blocked(cushion=0.01)
        await emissions.aclose()

        async with emissions.channel:
            emission = await emissions.channel.receive()

    assert emission == qtrio._core.Emission(signal=instance.signal, args=(93,))


async def test_emissions_channel_iterates_in_order(emissions_channel):
    """Emissions channel yields signal emissions in order (pretty probably...)."""

    class MyQObject(QtCore.QObject):
        signal = QtCore.Signal(int)

    instance = MyQObject()
    values = list(range(100))
    results = []

    async with emissions_channel(
        signals=[instance.signal],
        max_buffer_size=len(values),
    ) as emissions:
        for i, v in enumerate(values):
            if i % 2 == 0:
                await trio.testing.wait_all_tasks_blocked(cushion=0.001)

            instance.signal.emit(v)

        await emissions.aclose()

        async with emissions.channel:
            async for emission in emissions.channel:
                [value] = emission.args
                results.append(value)

    assert results == values


async def test_emissions_channel_limited_buffer(emissions_channel):
    """Emissions channel throws away beyond buffer limit."""

    class MyQObject(QtCore.QObject):
        signal = QtCore.Signal(int)

    instance = MyQObject()
    max_buffer_size = 10
    values = list(range(2 * max_buffer_size))
    results = []

    async with emissions_channel(
        signals=[instance.signal],
        max_buffer_size=max_buffer_size,
    ) as emissions:
        for v in values:
            instance.signal.emit(v)

        await emissions.aclose()

        async with emissions.channel:
            async for emission in emissions.channel:
                [value] = emission.args
                results.append(value)

    assert results == values[:max_buffer_size]


async def test_open_emissions_channel_does_not_close_read_channel():
    """Exiting open_emissions_channel() closes send channel and does not close
    read channel on exit.
    """

    class MyQObject(QtCore.QObject):
        signal = QtCore.Signal(int)

    instance = MyQObject()
    max_buffer_size = 10

    async with qtrio._core.open_emissions_channel(
        signals=[instance.signal],
        max_buffer_size=max_buffer_size,
    ) as emissions:
        pass

    with pytest.raises(trio.EndOfChannel):
        emissions.channel.receive_nowait()

    with pytest.raises(trio.ClosedResourceError):
        emissions.send_channel.send_nowait(None)


async def test_enter_emissions_channel_closes_both_channels():
    """Exiting enter_emissions_channel() closes send and receive channels on exit."""

    class MyQObject(QtCore.QObject):
        signal = QtCore.Signal(int)

    instance = MyQObject()
    max_buffer_size = 10

    async with qtrio.enter_emissions_channel(
        signals=[instance.signal],
        max_buffer_size=max_buffer_size,
    ) as emissions:
        pass

    with pytest.raises(trio.ClosedResourceError):
        emissions.channel.receive_nowait()

    with pytest.raises(trio.ClosedResourceError):
        emissions.send_channel.send_nowait(None)


def emissions_nursery_connect_maybe_async(
    is_async: bool,
    nursery: qtrio.EmissionsNursery,
    signal: "QtCore.SignalInstance",
    slot: typing.Callable[..., object],
) -> None:
    if is_async:

        async def async_slot(*args):
            return slot(*args)

        nursery.connect(signal, async_slot)
    else:
        nursery.connect_sync(signal, slot)


@pytest.fixture(name="is_async", params=[False, True], ids=["sync", "async"])
def is_async_fixture(request):
    yield request.param


async def test_emissions_nursery_runs_callbacks(is_async):
    """Callbacks connected to an emissions nursery get run."""

    class SignalHost(QtCore.QObject):
        signal = QtCore.Signal(int)

    results = set()
    event = trio.Event()

    def slot(number):
        results.add(number)
        if len(results) == 5:
            event.set()

    async with qtrio.open_emissions_nursery() as emissions_nursery:
        signal_host = SignalHost()

        emissions_nursery_connect_maybe_async(
            is_async=is_async,
            nursery=emissions_nursery,
            signal=signal_host.signal,
            slot=slot,
        )

        for i in range(5):
            signal_host.signal.emit(i)

        await event.wait()

    assert results == {0, 1, 2, 3, 4}


async def test_emissions_nursery_disconnects(is_async):
    """Callbacks are disconnected when exiting the context and aren't run for emissions
    after leaving.
    """

    class SignalHost(QtCore.QObject):
        signal = QtCore.Signal(int)

    results = set()

    def slot(number):
        results.add(number)  # pragma: no cover

    async with qtrio.open_emissions_nursery() as emissions_nursery:
        signal_host = SignalHost()

        emissions_nursery_connect_maybe_async(
            is_async=is_async,
            nursery=emissions_nursery,
            signal=signal_host.signal,
            slot=slot,
        )

    for i in range(5):
        signal_host.signal.emit(i)

    await trio.testing.wait_all_tasks_blocked(cushion=0.01)

    assert results == set()


async def test_emissions_nursery_cancellation_cancels_callbacks():
    """Callbacks are cancelled when the nursery is cancelled."""

    class SignalHost(QtCore.QObject):
        signal = QtCore.Signal(int)

    event = trio.Event()
    results = set()
    waiting = set()

    async def slot(number):
        try:
            waiting.add(number)

            if len(waiting) == 5:
                event.set()

            while True:
                await trio.sleep(1)
        except trio.Cancelled:
            results.add(number)
            raise

    async with qtrio.open_emissions_nursery() as emissions_nursery:
        signal_host = SignalHost()

        emissions_nursery.connect(signal_host.signal, slot)

        for i in range(5):
            signal_host.signal.emit(i)

        await event.wait()
        emissions_nursery.nursery.cancel_scope.cancel()

    assert results == {0, 1, 2, 3, 4}


async def test_emissions_nursery_receives_exceptions(is_async):
    """Callbacks that raise exceptions will feed them out to the nursery."""

    class SignalHost(QtCore.QObject):
        signal = QtCore.Signal()

    class LocalUniqueException(Exception):
        pass

    def slot():
        raise LocalUniqueException()

    with pytest.raises(LocalUniqueException):
        async with qtrio.open_emissions_nursery() as emissions_nursery:
            signal_host = SignalHost()

            emissions_nursery_connect_maybe_async(
                is_async=is_async,
                nursery=emissions_nursery,
                signal=signal_host.signal,
                slot=slot,
            )

            signal_host.signal.emit()


async def test_emissions_nursery_waits_for_until_signal():
    """Emissions nursery waits to exit until `until` signal is emitted."""

    class SignalHost(QtCore.QObject):
        signal = QtCore.Signal()

    results = []

    signal_host = SignalHost()

    async def emit_later():
        results.append(1)
        await trio.testing.wait_all_tasks_blocked(cushion=0.01)
        results.append(2)
        signal_host.signal.emit()

    async with trio.open_nursery() as nursery:
        async with qtrio.open_emissions_nursery(until=signal_host.signal):
            nursery.start_soon(emit_later)
            results.append(0)

        results.append(3)

    assert results == [0, 1, 2, 3]


async def test_emissions_nursery_wraps(is_async):
    """Emissions nursery wraps callbacks as requested."""

    class SignalHost(QtCore.QObject):
        signal = QtCore.Signal()

    class LocalUniqueException(Exception):
        pass

    result: outcome.Outcome

    event = trio.Event()
    signal_host = SignalHost()

    async def wrapper(asyncfn, *args):
        nonlocal result

        try:
            await asyncfn(*args)
        except Exception as e:
            result = outcome.Error(e)
            event.set()

    def slot():
        raise LocalUniqueException()

    async with qtrio.open_emissions_nursery(wrapper=wrapper) as emissions_nursery:
        emissions_nursery_connect_maybe_async(
            is_async=is_async,
            nursery=emissions_nursery,
            signal=signal_host.signal,
            slot=slot,
        )

        signal_host.signal.emit()
        await event.wait()

    with pytest.raises(LocalUniqueException):
        result.unwrap()


def test_run_without_executing_application(testdir):
    """Running without executing the application...  doesn't."""

    """Exiting enter_emissions_channel() closes send and receive channels on exit."""
    test_file = r"""
    import qtrio


    def test():
        ran = False

        async def async_fn():
            nonlocal ran
            ran = True

        runner = qtrio.Runner()
        runner.run(async_fn=async_fn, execute_application=False)

        assert not ran
    """

    testdir.makepyfile(test_file)

    result = testdir.runpytest_subprocess(timeout=timeout)
    result.assert_outcomes(passed=1)


def test_execute_manually(testdir):
    """Executing manually works."""

    test_file = r"""
    import qtrio


    def test():
        ran = False

        async def async_fn():
            nonlocal ran
            ran = True

        runner = qtrio.Runner()
        runner.run(async_fn=async_fn, execute_application=False)

        assert not ran

        runner.application.exec_()

        assert ran
    """

    testdir.makepyfile(test_file)

    result = testdir.runpytest_subprocess(timeout=timeout)
    result.assert_outcomes(passed=1)


def test_not_quitting_application_does_not(testdir):
    """Not quitting the application doesn't quit."""

    test_file = r"""
    from qts import QtCore
    import qtrio


    def test(qapp):
        results = []

        async def async_fn():
            pass

        def cycle():
            if runner._done and 'done' not in results:
                results.append('done')

                timer.stop()
                runner.application.quit()

        def about_to_quit():
            results.append('about to quit')

        timer = QtCore.QTimer()
        timer.setInterval(10)
        timer.timeout.connect(cycle)
        timer.start()

        runner = qtrio.Runner(application=qapp, quit_application=False)
        runner.application.aboutToQuit.connect(about_to_quit)
        runner.run(async_fn=async_fn)

        assert results == ['done', 'about to quit']
    """

    testdir.makepyfile(test_file)

    result = testdir.runpytest_subprocess(timeout=timeout)
    result.assert_outcomes(passed=1)


def test_warning_on_early_application_quit(testdir):
    """Emit a warning if the runner is supposed to handle quitting the application
    but the application is terminated early.
    """

    test_file = r"""
    import qtrio
    from qts import QtWidgets
    import trio


    async def quit():
        QtWidgets.QApplication.quit()


    async def main():
        async with trio.open_nursery() as nursery:
            nursery.start_soon(quit)
            await trio.sleep(9999)


    qtrio.run(main)
    """

    test_path = testdir.makepyfile(test_file)

    result = testdir.runpython(script=test_path)
    result.stderr.re_match_lines(lines2=[r".* ApplicationQuitWarning: .*"])
