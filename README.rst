.. image:: https://img.shields.io/badge/chat-join%20now-blue.svg
   :target: https://gitter.im/python-trio/general
   :alt: Join chatroom

.. image:: https://img.shields.io/badge/forum-join%20now-blue.svg
   :target: https://trio.discourse.group
   :alt: Join forum

.. image:: https://img.shields.io/badge/docs-read%20now-blue.svg
   :target: https://qtrio.readthedocs.io
   :alt: Documentation

.. image:: https://img.shields.io/pypi/v/qtrio.svg
   :target: https://pypi.org/project/qtrio
   :alt: Latest PyPi version

.. image:: https://img.shields.io/github/last-commit/altendky/qtrio.svg
   :target: https://github.com/altendky/qtrio
   :alt: Repository

.. image:: https://codecov.io/gh/altendky/qtrio/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/altendky/qtrio
   :alt: Test coverage


QTrio - a library bringing Qt GUIs together with ``async`` and ``await`` via Trio
=================================================================================

Note:
    This library is in early development.  It works.  It has tests.  It has
    documentation.  Expect breaking changes as we explore a clean API.  By paying this
    price you get the privilege to provide feedback via
    `GitHub issues <https://github.com/altendky/qtrio/issues>`__ to help shape our
    future.  ``:]``

The QTrio project's goal is to bring the friendly concurrency of Trio using Python's
``async`` and ``await`` syntax together with the GUI features of Qt to enable more
correct code and a more pleasant developer experience.  QTrio is `permissively licensed
<https://github.com/altendky/qtrio/blob/master/LICENSE>`__ to avoid introducing
restrictions beyond those of the underlying Python Qt library you choose.  Both PySide2
and PyQt5 are supported.

By enabling use of ``async`` and ``await`` it is possible in some cases to write related
code more concisely and clearly than you would get with the signal and slot mechanisms
of Qt concurrency.

.. code-block:: python

    class TwoStep:
        def __init__(self, a_signal, some_path):
            self.signal = a_signal
            self.file = None
            self.some_path = some_path

        def before(self):
            self.file = open(some_path, 'w')
            self.signal.connect(self.after)
            self.file.write('before')

        def after(self, value):
            self.signal.disconnect(self.after)
            self.file.write(f'after {value!r}')
            self.file.close()

.. code-block:: python

    async def together(a_signal):
        with open(self.some_path, 'w') as file:
            async with qtrio.enter_emissions_channel(signals=[a_signal]) as emissions:
                file.write('before')
                emission = await emissions.channel.receive()
                [value] = emission.args
                file.write(f'after {value!r}')

Note how by using ``async`` and ``await`` we are not only able to more clearly and
concisely describe the sequenced activity, we also get to use ``with`` to manage the
context of the open file to be sure it gets closed.
