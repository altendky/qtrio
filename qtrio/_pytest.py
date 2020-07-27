"""Tools to help working with QTrio in pytest."""

import functools
import itertools
import typing

import decorator
import outcome
import _pytest.fixtures
import pytest

import qtrio


async_def = typing.Callable[..., typing.Awaitable[object]]
sync_def = typing.Callable[..., object]


@typing.overload
def host(func: async_def,) -> sync_def:
    ...


@typing.overload
def host(*, timeout: float = 3) -> typing.Callable[[async_def], sync_def]:
    ...


# TODO: not really sure...
# qtrio/_pytest.py:37: error: Overloaded function implementation does not accept all possible arguments of signature 1
# qtrio/_pytest.py:37: error: Overloaded function implementation does not accept all possible arguments of signature 2
@decorator.decorator  # type: ignore
@pytest.mark.usefixtures("qapp", "qtbot")
def host(
    func, timeout=3, *args, **kwargs,
):
    """
    Decorate your tests that you want run in a Trio guest and a Qt Host.  This decorator
    can be used in any of the following forms.  Positional arguments other than a call
    with only the test function are not supported.

    .. literalinclude:: ../../qtrio/examples/_tests/docs/test_qtrio_host.py

    Note:
        Presently the test is required to specify the
        :class:`request <_pytest.fixtures.FixtureRequest>` fixture so this decorator can
        intercept and use it.

    Warning:
        The interface for specifying tests to run in this way will likely change a lot.
        Try to keep up.  ``:|``

    Args:
        func: The test function to be run via QTrio.
        timeout: The timeout to be applied to the test via :func:`trio.move_on_after`.
    """

    # TODO: https://github.com/micheles/decorator/issues/39
    [request] = (
        arg
        for arg in itertools.chain(args, kwargs.values())
        if isinstance(arg, _pytest.fixtures.FixtureRequest)
    )

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
        application=qapp,
        done_callback=done_callback,
        quit_application=False,
        timeout=timeout,
    )

    runner.run(
        functools.partial(func, **kwargs), *args, execute_application=False,
    )

    # TODO: probably increases runtime of fast tests a lot due to polling
    qtbot.wait_until(
        lambda: test_outcomes is not test_outcomes_sentinel, timeout=3.14e8
    )
    test_outcomes.unwrap()
