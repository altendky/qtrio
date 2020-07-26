QTrio - a library bringing Qt GUIs together with ``async`` and ``await`` via Trio
=================================================================================

Resources
---------

=================================  =================================  =============================

`Documentation <documentation_>`_  `Read the Docs <documentation_>`_  |documentation badge|
`Chat <chat_>`_                    `Gitter <chat_>`_                  |chat badge|
`Forum <forum_>`_                  `Discourse <forum_>`_              |forum badge|
`Issues <issues_>`_                `GitHub <issues_>`_                |issues badge|

`Repository <repository_>`_        `GitHub <repository_>`_            |repository badge|
`Tests <tests_>`_                  `GitHub Actions <tests_>`_         |tests badge|
`Coverage <coverage_>`_            `Codecov <coverage_>`_             |coverage badge|

`Distribution <distribution_>`_    `PyPI <distribution_>`_            | |version badge|
                                                                      | |python versions badge|
                                                                      | |python interpreters badge|

=================================  =================================  =============================


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

.. _chat: https://gitter.im/python-trio/general
.. |chat badge| image:: https://img.shields.io/badge/chat-join%20now-blue.svg?color=RoyalBlue&logo=Gitter&logoColor=WhiteSmoke
   :target: `chat`_
   :alt: Support chatroom

.. _forum: https://trio.discourse.group
.. |forum badge| image:: https://img.shields.io/badge/forum-join%20now-blue.svg?color=RoyalBlue&logo=Discourse&logoColor=WhiteSmoke
   :target: `forum`_
   :alt: Support forum

.. _documentation: https://qtrio.readthedocs.io
.. |documentation badge| image:: https://img.shields.io/badge/docs-read%20now-blue.svg?color=RoyalBlue&logo=Read-the-Docs&logoColor=WhiteSmoke
   :target: `documentation`_
   :alt: Documentation

.. _distribution: https://pypi.org/project/qtrio
.. |version badge| image:: https://img.shields.io/pypi/v/qtrio.svg?color=IndianRed&logo=PyPI&logoColor=WhiteSmoke
   :target: `distribution`_
   :alt: Latest distribution version

.. |python versions badge| image:: https://img.shields.io/pypi/pyversions/qtrio.svg?color=IndianRed&logo=PyPI&logoColor=WhiteSmoke
   :alt: Supported Python versions
   :target: `distribution`_

.. |python interpreters badge| image:: https://img.shields.io/pypi/implementation/qtrio.svg?color=IndianRed&logo=PyPI&logoColor=WhiteSmoke
   :alt: Supported Python interpreters
   :target: `distribution`_

.. _issues: https://github.com/altendky/qtrio/issues
.. |issues badge| image:: https://img.shields.io/github/issues/altendky/qtrio?color=RoyalBlue&logo=GitHub&logoColor=WhiteSmoke
   :target: `issues`_
   :alt: Issues

.. _repository: https://github.com/altendky/qtrio
.. |repository badge| image:: https://img.shields.io/github/last-commit/altendky/qtrio.svg?color=SeaGreen&logo=GitHub&logoColor=WhiteSmoke
   :target: `repository`_
   :alt: Repository

.. _tests: https://github.com/altendky/qtrio/actions?query=branch%3Amaster
.. |tests badge| image:: https://img.shields.io/github/workflow/status/altendky/qtrio/CI/master?color=SeaGreen&logo=GitHub-Actions&logoColor=WhiteSmoke
   :target: `tests`_
   :alt: Tests

.. _coverage: https://codecov.io/gh/altendky/qtrio
.. |coverage badge| image:: https://img.shields.io/codecov/c/github/altendky/qtrio/master?color=SeaGreen&logo=Codecov&logoColor=WhiteSmoke
   :target: `coverage`_
   :alt: Test coverage
