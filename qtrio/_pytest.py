"""Tools to help working with QTrio in pytest."""

import functools
import time
import typing


import outcome
import pytest
from qtpy import QtWidgets

import qtrio


timeout = 3


@pytest.fixture(name="qtrio_preshow_workaround", scope="session", autouse=True)
def preshow_fixture(qapp):
    widget = QtWidgets.QWidget()

    clock = time.monotonic
    start = clock()
    widget.show()
    end = clock()

    show_time = end - start

    print(
        "FYI, the qtrio_preshow_workaround fixture widget show time was"
        + f" {show_time:0.3f} seconds..."
    )

    yield


def host(test_function: typing.Callable[..., typing.Awaitable[None]]):
    """
    Decorate your tests that you want run with a Trio guest and a Qt Host.

    Note:
        Presently the test is required to specify the `request` fixture so this
        decorator can intercept and use it.

    Warning:
        The interface for specifying tests to run in this way will likely change a lot.
        Try to keep up.  ``:|``

    Args:
        test_function: The pytest function to be tested.
    """

    @pytest.mark.usefixtures("qapp", "qtbot")
    @functools.wraps(test_function)
    def wrapper(*args, **kwargs):
        request = kwargs["request"]

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
            functools.partial(test_function, **kwargs),
            *args,
            execute_application=False,
        )

        # TODO: probably increases runtime of fast tests a lot due to polling
        qtbot.wait_until(
            lambda: test_outcomes is not test_outcomes_sentinel, timeout=3.14e8
        )
        test_outcomes.unwrap()

    return wrapper
