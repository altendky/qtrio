import threading

import outcome
import pytest
from qtpy import QtCore
import qtrio._core


@pytest.fixture(
    name="emissions_channel_string",
    params=["qtrio._core.open_emissions_channel", "qtrio.enter_emissions_channel",],
    ids=["qtrio._core.open_emissions_channel", "qtrio.enter_emissions_channel"],
)
def emissions_channel_string_fixture(request):
    return request.param


def test_reenter_event_triggers_in_main_thread(qapp):
    """Reenter events posted in another thread result in the function being run in the
    main thread.
    """
    result = []

    reenter = qtrio._core.Reenter()

    def post():
        event = qtrio._core.ReenterEvent(fn=handler)
        qapp.postEvent(reenter, event)

    def handler():
        result.append(threading.get_ident())

    thread = threading.Thread(target=post)
    thread.start()
    thread.join()

    qapp.processEvents()

    assert result == [threading.get_ident()]


timeout = 10


def test_run_returns_value(testdir):
    """:func:`qtrio.run()` returns the result of the passed async function."""

    test_file = r"""
    import outcome

    import qtrio

    def test():
        async def main():
            return 29

        result = qtrio.run(main)

        assert result == qtrio.Outcomes(
            qt=outcome.Value(0),
            trio=outcome.Value(29),
        )
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
    from qtpy import QtCore
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

        outcomes = qtrio.run(async_fn=main)

        assert outcomes.trio.value == 2
    """
    testdir.makepyfile(test_file)

    result = testdir.runpytest_subprocess(timeout=timeout)
    result.assert_outcomes(passed=1)


def test_qt_quit_cancels_trio_with_custom_application(testdir):
    """When a passed Qt application exits the main Trio function is cancelled."""

    test_file = r"""
    import outcome
    from qtpy import QtCore
    from qtpy import QtWidgets
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

        assert outcomes.trio.value == None
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

        outcomes = qtrio.run(main)

        assert outcomes.trio.value == threading.get_ident()
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

        assert outcomes.trio.value == threading.get_ident()
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
    """If there are no available Qt event types remaining RegisterEventTypeError is
    raised.
    """
    test_file = r"""
    from qtpy import QtCore
    # Must pre-import Trio to avoid triggering another error
    # https://github.com/python-trio/trio/issues/1630
    import trio


    def test():
        while QtCore.QEvent.registerEventType() != -1:
            # use up all the event types
            pass

        exception = None

        try:
            import qtrio._exceptions
        except Exception as e:
            exception = e

        assert exception is not None
        assert type(exception).__name__ == "RegisterEventTypeError"
    """
    testdir.makepyfile(test_file)

    result = testdir.runpytest_subprocess(timeout=timeout)
    result.assert_outcomes(passed=1)


def test_wait_signal_waits(testdir):
    """wait_signal() waits for the signal.
    """
    test_file = r"""
    import time

    from qtpy import QtCore
    import qtrio._core


    @qtrio.host
    async def test(request):
        timer = QtCore.QTimer()
        timer.setSingleShot(True)
        
        start = time.monotonic()

        timer.start(100)
        
        await qtrio._core.wait_signal(timer.timeout)

        end = time.monotonic()
        
        assert end - start > 0.090
    """
    testdir.makepyfile(test_file)

    result = testdir.runpytest_subprocess(timeout=timeout)
    result.assert_outcomes(passed=1)


def test_wait_signal_returns_the_value(testdir):
    """wait_signal() waits for the signal."""
    test_file = r"""
    from qtpy import QtCore
    import qtrio._core
    import trio


    class MyQObject(QtCore.QObject):
        signal = QtCore.Signal(int)


    async def emit(signal, value):
        signal.emit(value)

    @qtrio.host
    async def test(request):
        instance = MyQObject()

        async with trio.open_nursery() as nursery:
            nursery.start_soon(emit, instance.signal, 17)
            result = await qtrio._core.wait_signal(instance.signal)

        assert result == (17,)
    """
    testdir.makepyfile(test_file)

    result = testdir.runpytest_subprocess(timeout=timeout)
    result.assert_outcomes(passed=1)


def test_wait_signal_context_waits(testdir):
    """wait_signal_context() waits for the signal.
    """
    test_file = r"""
    import time

    from qtpy import QtCore
    import qtrio._core


    @qtrio.host
    async def test(request):
        timer = QtCore.QTimer()
        timer.setSingleShot(True)

        async with qtrio._core.wait_signal_context(signal=timer.timeout):
            start = time.monotonic()
            timer.start(100)

        end = time.monotonic()

        assert end - start > 0.090
    """
    testdir.makepyfile(test_file)

    result = testdir.runpytest_subprocess(timeout=timeout)
    result.assert_outcomes(passed=1)


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
        qt=outcome.Value(9), trio=outcome.Error(LocalUniqueException()),
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
        qt=outcome.Error(LocalUniqueException()), trio=outcome.Value(8),
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


def test_failed_hosted_trio_prints_exception(testdir):
    """Except is printed when main Trio function raises."""
    test_file = r"""
    from qtpy import QtCore
    import qtrio


    class UniqueLocalException(Exception):
        pass


    @qtrio.host
    async def test(request):
        raise UniqueLocalException()
    """
    testdir.makepyfile(test_file)

    result = testdir.runpytest_subprocess(timeout=timeout)
    result.assert_outcomes(failed=1)
    result.stdout.re_match_lines(lines2=["--- Error(UniqueLocalException())"])


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


def test_emissions_channel_iterates_one(testdir, emissions_channel_string):
    """Emissions channel yields one emission as expected."""
    test_file = rf"""
    from qtpy import QtCore
    import qtrio
    import trio.testing


    class MyQObject(QtCore.QObject):
        signal = QtCore.Signal(int)


    @qtrio.host
    async def test(request):
        instance = MyQObject()

        async with {emissions_channel_string}(signals=[instance.signal]) as emissions:
            instance.signal.emit(93)
            await trio.testing.wait_all_tasks_blocked(cushion=0.01)
            await emissions.aclose()
            
            async with emissions.channel:
                emissions = [result async for result in emissions.channel] 

        assert emissions == [qtrio._core.Emission(signal=instance.signal, args=(93,))]
    """
    testdir.makepyfile(test_file)

    result = testdir.runpytest_subprocess(timeout=timeout)
    result.assert_outcomes(passed=1)


def test_emissions_channel_iterates_three(testdir, emissions_channel_string):
    """Emissions channel yields three emissions as expected."""
    test_file = rf"""
    from qtpy import QtCore
    import qtrio
    import trio.testing


    class MyQObject(QtCore.QObject):
        signal = QtCore.Signal(int)


    @qtrio.host
    async def test(request):
        instance = MyQObject()

        async with {emissions_channel_string}(signals=[instance.signal]) as emissions:
            for v in [93, 56, 27]:
                instance.signal.emit(v)
                await trio.testing.wait_all_tasks_blocked(cushion=0.01)
            await emissions.aclose()

            async with emissions.channel:
                emissions = [result async for result in emissions.channel] 

        assert emissions == [
            qtrio._core.Emission(signal=instance.signal, args=(v,))
            for v in [93, 56, 27]
        ]
    """
    testdir.makepyfile(test_file)

    result = testdir.runpytest_subprocess(timeout=timeout)
    result.assert_outcomes(passed=1)


def test_emissions_channel_with_three_receives_first(testdir, emissions_channel_string):
    """Emissions channel yields receives first item when requested."""
    test_file = rf"""
    from qtpy import QtCore
    import qtrio
    import trio.testing


    class MyQObject(QtCore.QObject):
        signal = QtCore.Signal(int)


    @qtrio.host
    async def test(request):
        instance = MyQObject()

        async with {emissions_channel_string}(signals=[instance.signal]) as emissions:
            for v in [93, 56, 27]:
                instance.signal.emit(v)
                await trio.testing.wait_all_tasks_blocked(cushion=0.01)
            await emissions.aclose()

            async with emissions.channel:
                emission = await emissions.channel.receive() 

        assert emission == qtrio._core.Emission(signal=instance.signal, args=(93,))
    """
    testdir.makepyfile(test_file)

    result = testdir.runpytest_subprocess(timeout=timeout)
    result.assert_outcomes(passed=1)


def test_emissions_channel_iterates_in_order(testdir, emissions_channel_string):
    """Emissions channel yields signal emissions in order (pretty probably...)."""
    test_file = rf"""
    from qtpy import QtCore
    import qtrio
    import trio.testing


    class MyQObject(QtCore.QObject):
        signal = QtCore.Signal(int)


    @qtrio.host
    async def test(request):
        instance = MyQObject()
        values = list(range(100))
        results = []

        async with {emissions_channel_string}(
            signals=[instance.signal], max_buffer_size=len(values),
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
    """
    testdir.makepyfile(test_file)

    result = testdir.runpytest_subprocess(timeout=timeout)
    result.assert_outcomes(passed=1)


def test_emissions_channel_limited_buffer(testdir, emissions_channel_string):
    """Emissions channel throws away beyond buffer limit."""
    test_file = rf"""
    from qtpy import QtCore
    import qtrio


    class MyQObject(QtCore.QObject):
        signal = QtCore.Signal(int)


    @qtrio.host
    async def test(request):
        instance = MyQObject()
        max_buffer_size = 10
        values = list(range(2 * max_buffer_size))
        results = []

        async with {emissions_channel_string}(
            signals=[instance.signal], max_buffer_size=max_buffer_size,
        ) as emissions:
            for v in values:
                instance.signal.emit(v)

            await emissions.aclose()

            async with emissions.channel:
                async for emission in emissions.channel:
                    [value] = emission.args
                    results.append(value)

        assert results == values[:max_buffer_size]
    """
    testdir.makepyfile(test_file)

    result = testdir.runpytest_subprocess(timeout=timeout)
    result.assert_outcomes(passed=1)


def test_open_emissions_channel_does_not_close_read_channel(testdir):
    """Exiting open_emissions_channel() closes send channel and does not close
    read channel on exit.
    """
    test_file = r"""
    import pytest
    from qtpy import QtCore
    import qtrio._core
    import trio


    class MyQObject(QtCore.QObject):
        signal = QtCore.Signal(int)


    @qtrio.host
    async def test(request):
        instance = MyQObject()
        max_buffer_size = 10
        values = list(range(2 * max_buffer_size))
        results = []

        async with qtrio._core.open_emissions_channel(
            signals=[instance.signal], max_buffer_size=max_buffer_size,
        ) as emissions:
            pass
            
        with pytest.raises(trio.EndOfChannel):
            emissions.channel.receive_nowait()
            
        with pytest.raises(trio.ClosedResourceError):
            emissions.send_channel.send_nowait(None)
    """
    testdir.makepyfile(test_file)

    result = testdir.runpytest_subprocess(timeout=timeout)
    result.assert_outcomes(passed=1)


def test_enter_emissions_channel_closes_both_channels(testdir):
    """Exiting enter_emissions_channel() closes send and receive channels on exit."""
    test_file = r"""
    import pytest
    from qtpy import QtCore
    import qtrio
    import trio


    class MyQObject(QtCore.QObject):
        signal = QtCore.Signal(int)


    @qtrio.host
    async def test(request):
        instance = MyQObject()
        max_buffer_size = 10
        values = list(range(2 * max_buffer_size))
        results = []

        async with qtrio.enter_emissions_channel(
            signals=[instance.signal], max_buffer_size=max_buffer_size,
        ) as emissions:
            pass

        with pytest.raises(trio.ClosedResourceError):
            emissions.channel.receive_nowait()

        with pytest.raises(trio.ClosedResourceError):
            emissions.send_channel.send_nowait(None)
    """
    testdir.makepyfile(test_file)

    result = testdir.runpytest_subprocess(timeout=timeout)
    result.assert_outcomes(passed=1)
