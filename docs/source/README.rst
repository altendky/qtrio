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

By enabling use of ``async`` and ``await`` it is possible in some cases to write
related code more concisely and clearly than you would get with the signal and slot
mechanisms of Qt concurrency.  In this set of small examples we will allow the user to
input their name then use that input to generate an output message.  The user will be
able to cancel the input to terminate the program early.  In the first example we will
do it in the form of a classic "hello" console program.  Well, classic plus a bit of
boilerplate to allow explicit testing without using special external tooling.  Then
second, the form of a general Qt program implementing this same activity.  And finally,
the QTrio way.

.. literalinclude:: ../../qtrio/examples/readme/console.py

Nice and concise, including the cancellation via ``ctrl+c``.  This is because we can
stay in one scope thus using both local variables and a ``try``/``except`` block.  This
kind of explodes when you shift into a classic Qt GUI setup.

.. literalinclude:: ../../qtrio/examples/readme/qt.py

The third example, below, shows how using ``async`` and ``await`` allows us to
return to the more concise and clear description of the sequenced activity.
Most of the code is just setup for testability with only the last four lines
really containing the activity.

.. literalinclude:: ../../qtrio/examples/readme/qtrio.py


.. _chat: https://gitter.im/python-trio/general
.. |chat badge| image:: https://img.shields.io/badge/chat-join%20now-blue.svg?color=royalblue&logo=Gitter&logoColor=whitesmoke
   :target: `chat`_
   :alt: Support chatroom

.. _forum: https://trio.discourse.group
.. |forum badge| image:: https://img.shields.io/badge/forum-join%20now-blue.svg?color=royalblue&logo=Discourse&logoColor=whitesmoke
   :target: `forum`_
   :alt: Support forum

.. _documentation: https://qtrio.readthedocs.io
.. |documentation badge| image:: https://img.shields.io/badge/docs-read%20now-blue.svg?color=royalblue&logo=Read-the-Docs&logoColor=whitesmoke
   :target: `documentation`_
   :alt: Documentation

.. _distribution: https://pypi.org/project/qtrio
.. |version badge| image:: https://img.shields.io/pypi/v/qtrio.svg?color=indianred&logo=PyPI&logoColor=whitesmoke
   :target: `distribution`_
   :alt: Latest distribution version

.. |python versions badge| image:: https://img.shields.io/pypi/pyversions/qtrio.svg?color=indianred&logo=PyPI&logoColor=whitesmoke
   :alt: Supported Python versions
   :target: `distribution`_

.. |python interpreters badge| image:: https://img.shields.io/pypi/implementation/qtrio.svg?color=indianred&logo=PyPI&logoColor=whitesmoke
   :alt: Supported Python interpreters
   :target: `distribution`_

.. _issues: https://github.com/altendky/qtrio/issues
.. |issues badge| image:: https://img.shields.io/github/issues/altendky/qtrio?color=royalblue&logo=GitHub&logoColor=whitesmoke
   :target: `issues`_
   :alt: Issues

.. _repository: https://github.com/altendky/qtrio
.. |repository badge| image:: https://img.shields.io/github/last-commit/altendky/qtrio.svg?color=seagreen&logo=GitHub&logoColor=whitesmoke
   :target: `repository`_
   :alt: Repository

.. _tests: https://github.com/altendky/qtrio/actions?query=branch%3Amaster
.. |tests badge| image:: https://img.shields.io/github/workflow/status/altendky/qtrio/CI/master?color=seagreen&logo=GitHub-Actions&logoColor=whitesmoke
   :target: `tests`_
   :alt: Tests

.. _coverage: https://codecov.io/gh/altendky/qtrio
.. |coverage badge| image:: https://img.shields.io/codecov/c/github/altendky/qtrio/master?color=seagreen&logo=Codecov&logoColor=whitesmoke
   :target: `coverage`_
   :alt: Test coverage
