import time

import pytest
from qtpy import QtWidgets

pytest_plugins = "pytester"


@pytest.fixture(name='qtrio_preshow_workaround', scope='session', autouse=True)
def preshow_fixture(qapp):
    clock = time.monotonic

    def delta():
        return f'{clock() - start:0.3f}'

    widget = QtWidgets.QWidget()

    start = clock()
    widget.show()
    end = clock()

    show_time = end - start

    print(f'FYI, the qtrio_preshow_workaround fixture widget show time was {show_time:0.3f} seconds...')
