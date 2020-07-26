import pytest


@pytest.mark.parametrize(
    argnames=["decorator_format"],
    argvalues=[["qtrio.host"], ["qtrio.host()"], ["qtrio.host(timeout={timeout})"]],
)
def test_overrunning_test_times_out(preshow_testdir, decorator_format):
    """The overrunning test is timed out."""

    timeout = 3

    decorator_string = decorator_format.format(timeout=timeout)

    test_file = rf"""
    import qtrio
    import trio

    @{decorator_string}
    async def test(request):
        await trio.sleep({2 * timeout})
    """
    preshow_testdir.makepyfile(test_file)

    result = preshow_testdir.runpytest_subprocess(timeout=2 * timeout)
    result.assert_outcomes(failed=1)
    result.stdout.re_match_lines(
        lines2=[r"E\s+qtrio\._exceptions\.RunnerTimedOutError"]
    )


# TODO: test that the timeout case doesn't leave trio active...  like
#       it was doing five minutes ago.


def test_hosted_assertion_failure_fails(preshow_testdir):
    """QTrio hosted test which fails an assertion fails the test."""

    test_file = r"""
    import qtrio

    @qtrio.host
    async def test(request):
        assert False
    """
    preshow_testdir.makepyfile(test_file)

    result = preshow_testdir.runpytest_subprocess(timeout=10)
    result.assert_outcomes(failed=1)
