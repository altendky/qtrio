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
