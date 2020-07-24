import time

import qtrio
from qtpy import QtCore
from qtpy import QtWidgets
import trio
import trio.testing

import qtrio.examples.buildingrespect


clock = time.monotonic


@qtrio.host
async def test_example(request, qtbot):
    start = clock()

    def delta():
        return f'{clock() - start:0.3f}'

    async def user():
        print('+++++', 'test_example user() before sleep', delta())
        await trio.sleep(0)
        print('+++++', 'test_example user() after sleep', delta())

    def show_button(message):
        print(f'+++++ {message} - before button creation', delta())
        button = QtWidgets.QPushButton()
        print(f'+++++ {message} - before qtbot addition', delta())
        qtbot.addWidget(button)
        print(f'+++++ {message} - before button.show()', delta())
        button.show()
        print(f'+++++ {message} - after button.show()', delta())

    print('+++++', 'test_example before nursery', delta())

    try:
        show_button('before nursery')

        async with trio.open_nursery() as nursery:
            show_button('in nursery')

            nursery.start_soon(user)

            show_button('after start_soon')
    finally:
        print('+++++', 'test_example finally', delta())
