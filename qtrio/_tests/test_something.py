import qtrio._pytest


def test_overrunning_test_times_out_01(testdir):
    """The overrunning test is timed out."""

    # Be really sure this is longer than the intended test timeout plus some extra
    # to account for random process startup variations in CI.
    subprocess_timeout = (2 * qtrio._pytest.timeout) + 10

    test_file = r"""
    import time
    print("blueredgreen ----------", time.monotonic(), flush=True)

    import faulthandler
    faulthandler.enable()
    faulthandler.dump_traceback()
    faulthandler.dump_traceback_later(3 + 1)
    # faulthandler.dump_traceback_later(qtrio._pytest.timeout + 1)

    import qtrio
    import qtrio._pytest
    import trio


    @qtrio.host
    async def test(request):
        while True:
            print("blueredgreen ----------", time.monotonic(), flush=True)
            await trio.sleep(0.1)
    """
    testdir.makepyfile(test_file)

    timeout = qtrio._pytest.timeout

    result = testdir.runpytest_subprocess("--capture", "no", timeout=subprocess_timeout)
    result.assert_outcomes(failed=1)
    result.stdout.re_match_lines(
        lines2=[rf"E\s+AssertionError: test not finished within {timeout} seconds"],
    )


def test_overrunning_test_times_out_02(testdir):
    """The overrunning test is timed out."""

    # Be really sure this is longer than the intended test timeout plus some extra
    # to account for random process startup variations in CI.
    subprocess_timeout = (2 * qtrio._pytest.timeout) + 10

    test_file = r"""
    import time
    print("blueredgreen ----------", time.monotonic(), flush=True)

    import faulthandler
    faulthandler.enable()
    faulthandler.dump_traceback()
    faulthandler.dump_traceback_later(3 + 1)
    # faulthandler.dump_traceback_later(qtrio._pytest.timeout + 1)

    import qtrio
    import qtrio._pytest
    import trio


    @qtrio.host
    async def test(request):
        while True:
            print("blueredgreen ----------", time.monotonic(), flush=True)
            await trio.sleep(0.1)
    """
    testdir.makepyfile(test_file)

    timeout = qtrio._pytest.timeout

    result = testdir.runpytest_subprocess("--capture", "no", timeout=subprocess_timeout)
    result.assert_outcomes(failed=1)
    result.stdout.re_match_lines(
        lines2=[rf"E\s+AssertionError: test not finished within {timeout} seconds"],
    )


def test_overrunning_test_times_out_03(testdir):
    """The overrunning test is timed out."""

    # Be really sure this is longer than the intended test timeout plus some extra
    # to account for random process startup variations in CI.
    subprocess_timeout = (2 * qtrio._pytest.timeout) + 10

    test_file = r"""
    import functools
    import time
    print("blueredgreen ----------", time.monotonic(), flush=True)

    import faulthandler
    faulthandler.enable()
    faulthandler.dump_traceback()
    faulthandler.dump_traceback_later(3 + 1)
    # faulthandler.dump_traceback_later(qtrio._pytest.timeout + 1)

    import outcome
    import pytest
    import qtrio
    import qtrio._pytest
    import trio

    timeout = 3

    async def cut(request):
        while True:
            print("blueredgreen ----------", time.monotonic(), flush=True)
            await trio.sleep(0.1)


    @pytest.mark.usefixtures("request", "qapp", "qtbot")
    @functools.wraps(cut)
    def test(*args, **kwargs):
        request = kwargs["request"]

        qapp = request.getfixturevalue("qapp")
        qtbot = request.getfixturevalue("qtbot")

        test_outcomes_sentinel = qtrio.Outcomes(
            qt=outcome.Value(0), trio=outcome.Value(29),
        )
        test_outcomes = test_outcomes_sentinel

        def done_callback(outcomes):
            nonlocal test_outcomes
            test_outcomes = outcomes

        runner = qtrio._core.Runner(
            application=qapp, done_callback=done_callback, quit_application=False,
        )

        runner.run(
            functools.partial(cut, **kwargs),
            *args,
            execute_application=False,
        )

        def result_ready():
            message = f"test not finished within {timeout} seconds"
            assert test_outcomes is not test_outcomes_sentinel, message

        # TODO: probably increases runtime of fast tests a lot due to polling
        try:
            qtbot.wait_until(result_ready, timeout=timeout * 1000)
        except AssertionError:
            runner.cancel_scope.cancel()
            qtbot.wait_until(result_ready)
            raise
    """
    testdir.makepyfile(test_file)

    timeout = qtrio._pytest.timeout

    result = testdir.runpytest_subprocess("--capture", "no", timeout=subprocess_timeout)
    result.assert_outcomes(failed=1)
    result.stdout.re_match_lines(
        lines2=[rf"E\s+AssertionError: test not finished within {timeout} seconds"],
    )


def test_overrunning_test_times_out_04(testdir):
    """The overrunning test is timed out."""

    # Be really sure this is longer than the intended test timeout plus some extra
    # to account for random process startup variations in CI.
    subprocess_timeout = (2 * qtrio._pytest.timeout) + 10

    test_file = r"""
    import time
    print("blueredgreen ----------", time.monotonic(), flush=True)

    import faulthandler
    faulthandler.enable()
    faulthandler.dump_traceback()
    faulthandler.dump_traceback_later(3 + 1)
    # faulthandler.dump_traceback_later(qtrio._pytest.timeout + 1)

    def test():
        time.sleep(3)
        assert False, "test not finished within 3 seconds"
    """
    testdir.makepyfile(test_file)

    timeout = qtrio._pytest.timeout

    result = testdir.runpytest_subprocess("--capture", "no", timeout=subprocess_timeout)
    result.assert_outcomes(failed=1)
    result.stdout.re_match_lines(
        lines2=[rf"E\s+AssertionError: test not finished within {timeout} seconds"],
    )
