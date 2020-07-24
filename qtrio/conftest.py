import time

import pytest
from qtpy import QtWidgets

pytest_plugins = "pytester"


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
