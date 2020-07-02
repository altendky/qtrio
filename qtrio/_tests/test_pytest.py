import qtrio._pytest


def test_overrunning_test_times_out(testdir):
    """The overrunning test is timed out."""

    # Be really sure this is longer than the intended test timeout plus some extra
    # to account for random process startup variations in CI.
    subprocess_timeout = (2 * qtrio._pytest.timeout) + 10

    test_file = r"""
    import faulthandler

    import qtrio
    import qtrio._pytest
    import trio


    faulthandler.dump_traceback_later(qtrio._pytest.timeout + 1)


    @qtrio.host
    async def test(request):
        while True:
            await trio.sleep(1)
    """
    testdir.makepyfile(test_file)

    timeout = qtrio._pytest.timeout

    result = testdir.runpytest_subprocess(timeout=subprocess_timeout)
    result.assert_outcomes(failed=1)
    result.stdout.re_match_lines(
        lines2=[f"E       AssertionError: test not finished within {timeout} seconds"],
    )


# TODO: test that the timeout case doesn't leave trio active...  like
#       it was doing five minutes ago.


def test_hosted_assertion_failure_fails(testdir):
    """QTrio hosted test which fails an assertion fails the test."""

    test_file = r"""
    import qtrio

    @qtrio.host
    async def test(request):
        assert False
    """
    testdir.makepyfile(test_file)

    result = testdir.runpytest_subprocess(timeout=10)
    result.assert_outcomes(failed=1)
