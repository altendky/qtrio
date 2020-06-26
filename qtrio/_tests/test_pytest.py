def test_wait_signal_returns_the_value(testdir):
    """The overrunning test is timed out."""

    test_file = r"""
    import qtrio
    import trio

    @qtrio.host
    async def test(request):
        await trio.sleep(10)
    """
    testdir.makepyfile(test_file)

    result = testdir.runpytest_subprocess(timeout=10)
    result.assert_outcomes(failed=1)
    result.stdout.re_match_lines(
        lines2=["E       AssertionError: test not finished within 6.0 seconds"]
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
