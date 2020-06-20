def test_wait_signal_returns_the_value(testdir):
    """The overrunning test is timed out."""

    test_file = r"""
    import qtrio

    @qtrio.host
    async def test_times_out(request):
        await trio.sleep(10)
    """
    testdir.makepyfile(test_file)

    result = testdir.runpytest_subprocess(timeout=10)
    result.assert_outcomes(failed=1)


# TODO: test that the timeout case doesn't leave trio active...  like
#       it was doing five minutes ago.
