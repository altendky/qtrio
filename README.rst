|documentation badge|
|chat badge|
|forum badge|
|distribution badge|
|repository badge|
|tests badge|
|coverage badge|

QTrio - a library bringing Qt GUIs together with ``async`` and ``await`` via Trio
=================================================================================

Resources (option 1)
--------------------

=================================  =================================  =====================
`Documentation <documentation_>`_  `Read the Docs <documentation_>`_  |documentation badge|
=================================  =================================  =====================

=============  ==============  =====================
Documentation  Read The Docs   |documentation badge|
Repository     GitHub          |repository badge|
Distribution   PyPI            |distribution badge|
Tests          GitHub Actions  |tests badge|
Coverage       Codecov         |coverage badge|
Chat           Gitter          |chat badge|
Forum          Discourse       |forum badge|

=============  ==============  =====================


Resources (option 2)
--------------------

|documentation badge| `Documentation is provided on Read the Docs. <documentation>`__

|repository badge| `The repository is hosted at GitHub. <repository>`__

|distribution badge| `Releases are distributed on PyPI. <distribution>`__

|tests badge| `Tests are run with GitHub Actions. <tests>`__

|coverage badge| `Code coverage by tests is tracked with Codecov. <coverage>`__

|chat badge| `Interactive chat is available on Gitter. <chat>`__

|forum badge| `Forum posts can be made on Discourse. <forum>`__


Resources (option 3)
--------------------

- Documentation is provided on `Read the Docs <documentation>`__.
- The repository is hosted at `GitHub <repository>`__.
- Releases are distributed on `PyPI <distribution>`__.
- Tests are run with GitHub `Actions <tests>`__.
- Code coverage is tracked with `Codecov <coverage>`__.
- Interactive chat is available on `Gitter <chat>`__.
- Forum posts can be made on `Discourse <forum>`__.


Introduction
------------

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

.. |chat badge| image:: https://img.shields.io/badge/chat-join%20now-blue.svg
   :target: https://gitter.im/python-trio/general
   :alt: Support chatroom

.. |forum badge| image:: https://img.shields.io/badge/forum-join%20now-blue.svg
   :target: https://trio.discourse.group
   :alt: Support forum

.. _documentation: https://qtrio.readthedocs.io
.. |documentation badge| image:: https://img.shields.io/badge/docs-read%20now-blue.svg
   :target: documentation_
   :alt: Documentation

.. |distribution badge| image:: https://img.shields.io/pypi/v/qtrio.svg
   :target: https://pypi.org/project/qtrio
   :alt: Latest distribution version

.. |repository badge| image:: https://img.shields.io/github/last-commit/altendky/qtrio.svg
   :target: https://github.com/altendky/qtrio
   :alt: Repository

.. |tests badge| image:: https://github.com/altendky/qtrio/workflows/CI/badge.svg?branch=master
   :target: https://github.com/altendky/qtrio/actions?query=branch%3Amaster
   :alt: Tests

.. |coverage badge| image:: https://codecov.io/gh/altendky/qtrio/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/altendky/qtrio
   :alt: Test coverage
