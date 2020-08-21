import pytest

import qtrio._pytest


timeout = 40


@pytest.mark.parametrize(
    argnames=["decorator_format"],
    argvalues=[["qtrio.host"], ["qtrio.host()"], ["qtrio.host(timeout={timeout})"]],
)
def test_host_decoration_options(testdir, decorator_format):
    """The several decoration modes all work."""

    decorator_string = decorator_format.format(timeout=20)

    test_file = rf"""
    import qtrio

    @{decorator_string}
    async def test(request):
        pass
    """
    testdir.makepyfile(test_file)

    result = testdir.runpytest_subprocess(timeout=timeout)
    result.assert_outcomes(passed=1)


def test_overrunning_test_times_out(testdir):
    """The overrunning test is timed out."""

    test_file = rf"""
    import qtrio
    import trio
    import trio.testing

    @qtrio.host(clock=trio.testing.MockClock(autojump_threshold=0))
    async def test(request):
        await trio.sleep({4 * timeout})
    """
    testdir.makepyfile(test_file)

    result = testdir.runpytest_subprocess(timeout=timeout)
    result.assert_outcomes(failed=1)
    result.stdout.re_match_lines(lines2=[r"E\s+qtrio\.RunnerTimedOutError"])


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

    result = testdir.runpytest_subprocess(timeout=timeout)
    result.assert_outcomes(failed=1)
