import time

import pytest
from qtpy import QtWidgets

pytest_plugins = "pytester"


# @pytest.fixture(name='preshow', scope='session', autouse=True)
# def preshow_fixture(qapp):
#     clock = time.monotonic
#     start = clock()
#
#     def delta():
#         return f'{clock() - start:0.3f}'
#
#     print('+++++', 'preshow_fixture about to create the button', delta())
#     button = QtWidgets.QPushButton()
#     print('+++++', 'preshow_fixture before button.show()', delta())
#     button.show()
#     print('+++++', 'preshow_fixture after button.show()', delta())
