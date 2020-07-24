import time

import pytest
from qtpy import QtWidgets

pytest_plugins = "pytester"


@pytest.fixture(name='preshow', scope='session', autouse=True)
def preshow_fixture(qapp):
    clock = time.monotonic
    start = clock()

    def delta():
        return f'{clock() - start:0.3f}'

    print('+++++', 'test_show about to create the button', delta())
    button = QtWidgets.QPushButton()
    print('+++++', 'test_show before button.show()', delta())
    button.show()
    print('+++++', 'test_show after button.show()', delta())
