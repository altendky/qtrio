import qtrio._pytest


def test_overrunning_test_times_out(testdir):
    """The overrunning test is timed out."""

    test_file = rf"""
    import qtrio
    import trio

    @qtrio.host
    async def test(request):
        await trio.sleep({2 * qtrio._pytest.timeout})
    """
    testdir.makepyfile(test_file)

    result = testdir.runpytest_subprocess(timeout=2 * qtrio._pytest.timeout)
    result.assert_outcomes(failed=1)
    result.stdout.re_match_lines(
        lines2=[r"E\s+qtrio\._exceptions\.RunnerTimedOutError"]
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
