import threading

import outcome
import pytest
import qtrio._core


def test_reenter_event_triggers_in_main_thread(qapp):
    """Reenter events posted in another thread result in the function being run in the
    main thread.
    """
    result = []

    reenter = qtrio._core.Reenter()

    def post():
        event = qtrio._core.create_reenter_event(fn=handler)
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


def test_qt_quit_cancels_trio(testdir):
    """When the Qt application exits the main Trio function is cancelled."""

    test_file = r"""
    import outcome
    from qtpy import QtCore
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

        outcomes = qtrio.run(async_fn=main)

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
    import qtrio


    @qtrio.host
    async def test(request):
        timer = QtCore.QTimer()
        timer.setSingleShot(True)
        
        start = time.monotonic()

        timer.start(100)
        
        await qtrio.wait_signal(timer.timeout)

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
    import qtrio
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
            result = await qtrio.wait_signal(instance.signal)

        assert result == (17,)
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
