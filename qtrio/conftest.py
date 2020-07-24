import inspect
import os
import sys
import time

import pytest
from qtpy import QtWidgets

pytest_plugins = "pytester"


@pytest.fixture(name="qtrio_preshow_workaround", scope="session", autouse=True)
def preshow_fixture(qapp):
    widget = QtWidgets.QPushButton()

    clock = time.monotonic
    start = clock()
    widget.show()
    end = clock()

    show_time = end - start

    print(
        "FYI, the qtrio_preshow_workaround fixture widget show time was"
        + f" {show_time:0.3f} seconds...  {os.getpid()}"
    )

    yield

    widget.hide()


@pytest.fixture(name="preshow_testdir")
def preshow_testdir_fixture(testdir):
    testdir.makeconftest(inspect.getsource(sys.modules[__name__]))

    return testdir
