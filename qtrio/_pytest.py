"""Tools to help working with QTrio in pytest."""

import functools
import typing

import decorator
import _pytest.fixtures
import pytest
import trio.abc

import qtrio


@typing.overload
def host(
    func: typing.Callable[..., typing.Awaitable[object]]
) -> typing.Callable[..., object]:
    ...


@typing.overload
def host(
    *,
    timeout: float = 20,
    clock: trio.abc.Clock = None,
) -> typing.Callable[
    [typing.Callable[..., typing.Awaitable[object]]], typing.Callable[..., object]
]:
    ...


# TODO: not really sure...
# qtrio/_pytest.py:37: error: Overloaded function implementation does not accept all possible arguments of signature 1
# qtrio/_pytest.py:37: error: Overloaded function implementation does not accept all possible arguments of signature 2
@decorator.decorator  # type: ignore
@pytest.mark.usefixtures("qapp")  # type: ignore
def host(
    func: typing.Callable[..., typing.Awaitable[object]],
    timeout: float = 3,
    clock: trio.abc.Clock = None,
    *args: object,
    **kwargs: object,
) -> None:
    """
    Decorate your tests that you want run in a Trio guest and a Qt Host.  This decorator
    can be used in any of the following forms.  Positional arguments other than a call
    with only the test function are not supported.

    .. literalinclude:: ../../qtrio/_tests/examples/docs/test_qtrio_host.py

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
        clock: Usually used to speed up tests via :class:`trio.testing.MockClock`.  See
            :func:`trio.lowlevel.start_guest_run`.
    """

    # TODO: https://github.com/micheles/decorator/issues/39
    [request] = (
        arg
        for arg_sequence in [args, kwargs.values()]
        for arg in arg_sequence
        if isinstance(arg, _pytest.fixtures.FixtureRequest)
    )

    qapp = request.getfixturevalue("qapp")
    qapp.setQuitOnLastWindowClosed(False)

    runner = qtrio._core.Runner(application=qapp, timeout=timeout, clock=clock)

    async_fn = functools.partial(func, *args, **kwargs)
    test_outcomes = runner.run(async_fn=async_fn)

    test_outcomes.unwrap()
