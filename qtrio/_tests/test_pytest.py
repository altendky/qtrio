import pytest


timeout = 40


def test_assertion_failure_fails(testdir):
    """QTrio hosted test which fails an assertion fails the test."""

    test_file = r"""
    import trio

    async def test():
        await trio.sleep(0)
        assert False
    """
    testdir.makepyfile(test_file)

    result = testdir.runpytest_subprocess(timeout=timeout)
    result.assert_outcomes(failed=1)


def test_assertion_pass_passes(testdir):
    """QTrio hosted test which passes an assertion passes the test."""

    test_file = r"""
    import trio

    async def test():
        await trio.sleep(0)
        assert True
    """
    testdir.makepyfile(test_file)

    result = testdir.runpytest_subprocess(timeout=timeout)
    result.assert_outcomes(passed=1)
