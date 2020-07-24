import time

from qtpy import QtWidgets


clock = time.monotonic


def test_example(qtbot):
    start = clock()

    def delta():
        return f'{clock() - start:0.3f}'

    def show_button(message):
        print(f'+++++ {message} - before button creation', delta())
        button = QtWidgets.QPushButton()
        print(f'+++++ {message} - before qtbot addition', delta())
        qtbot.addWidget(button)
        print(f'+++++ {message} - before button.show()', delta())
        button.show()
        print(f'+++++ {message} - after button.show()', delta())

    show_button('before nursery')
