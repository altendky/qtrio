import inspect
import sys

import pytest
from qtpy import QtWidgets

pytest_plugins = "pytester"


@pytest.fixture(name="qtrio_preshow_workaround", scope="session", autouse=True)
def preshow_fixture(qapp):
    widget = QtWidgets.QPushButton()

    widget.show()
    widget.hide()


@pytest.fixture(name="preshow_testdir")
def preshow_testdir_fixture(testdir):
    testdir.makeconftest(inspect.getsource(sys.modules[__name__]))

    return testdir
