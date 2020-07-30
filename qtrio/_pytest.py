"""Tools to help working with QTrio in pytest."""

import functools
import typing

import outcome
import pytest

import qtrio


timeout = 3


def host(test_function: typing.Callable[..., typing.Awaitable[None]]):
    """
    Decorate your tests that you want run with a Trio guest and a Qt Host.

    Note:
        Presently the test is required to specify the
        :class:`request <_pytest.fixtures.FixtureRequest>` fixture so this decorator can
        intercept and use it.

    Warning:
        The interface for specifying tests to run in this way will likely change a lot.
        Try to keep up.  ``:|``

    Args:
        test_function: The pytest function to be tested.
    """

    @pytest.mark.usefixtures("qapp")
    @functools.wraps(test_function)
    def wrapper(*args, **kwargs):
        request = kwargs["request"]

        qapp = request.getfixturevalue("qapp")
        qapp.setQuitOnLastWindowClosed(False)

        runner = qtrio._core.Runner(application=qapp, timeout=timeout)

        async_fn = functools.partial(test_function, *args, **kwargs)
        test_outcomes = runner.run(async_fn=async_fn)

        test_outcomes.unwrap()

    return wrapper
