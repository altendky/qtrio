Getting Started
===============

This tutorial introduces usage of QTrio to enable integration of Qt into a Trio async
application.  For help with relevant async concepts and usage of Trio itself see
`the Trio tutorial <https://trio.readthedocs.io/en/stable/tutorial.html>`__.

I know, I know...  we are supposed to do one thing well.  But QTrio presently targets
three distinct development tools.  In time perhaps pieces will be spun off but for now
they provide increasing layers you can use or not as they interest you.

.. _installation:

Installation
------------

While the general aspects of installation using pip belong elsewhere, it is recommended
to work in a virtual environment such as you can create with the
:mod:`venv module <python:venv>` (see also
`Python Virtual Environments in Five Minutes <https://chriswarrick.com/blog/2018/09/04/python-virtual-environments/>`_
).

Somewhat more specific to QTrio, several
`extras <https://setuptools.readthedocs.io/en/stable/setuptools.html#declaring-extras-optional-features-with-their-own-dependencies>`_
are available for installing optional dependencies or applying version constraints.

- ``cli`` - For CLI usage, presently just examples.
- ``examples`` - For running examples.
- ``pyqt5`` - For running with PyQt5, primarily to apply any version constraints.
- ``pyside2`` - For running with PySide2, primarily to apply any version constraints.

A normal installation might look like:

.. code-block:: bash

    $ myenv/bin/pip install qtrio[pyside2]

Overview
--------

The first layer allows you to run Trio tasks in the same thread as the Qt event loop.
This is valuable as it let's the tasks safely interact directly with the Qt GUI objects.
It is a small wrapper around
`Trio's guest mode <https://trio.readthedocs.io/en/stable/reference-lowlevel.html#using-guest-mode-to-run-trio-on-top-of-other-event-loops>`__.
This layer is exposed directly under the ``qtrio`` package.

Now that Qt and Trio are friends we can focus on making the relationship smoother.  This
second layer of QTrio is also available directly in the ``qtrio`` package and allows for
awaiting signals and iterating over the emissions of signals.  This avoids the normal
callback design of GUI systems in favor of Trio's structured concurrency allowing GUI
responses to be handled where you want within the task tree.

Not everything Qt provides will be easily integrated into this structure.  The rest of
QTrio will grow to contain helpers and wrappers to address these cases.

In addition to the above three layers there is also adjacent support for testing.

Layer 1 - Crossing Paths
------------------------

With one extra character you can turn :func:`trio.run` into :func:`qtrio.run`.  This
gets you the Trio guest mode hosted by a Qt :class:`PyQt5.QtWidgets.QApplication`.  Note how
there is only one function and you are able to asynchronously sleep in it to avoid
blocking the GUI.  By default, when you leave your main function the Qt application will
be exited.

.. literalinclude:: ../../qtrio/examples/crossingpaths.py

.. _getting_started_layer_2:

Layer 2 - Building Respect
--------------------------

A good relationship goes both ways.  Above, Trio did all the talking and Qt just
listened.  Now let's have Trio listen to Qt.  Emissions from Qt signals can be made
available in a :class:`trio.MemoryReceiveChannel`.  You can either
:meth:`trio.MemoryReceiveChannel.receive` them one at a time or asynchronously iterate
over them for longer lasting activities.  The received object is a
:class:`qtrio.Emission` and contains both the originating signal and the arguments.

.. literalinclude:: ../../qtrio/examples/buildingrespect.py


Layer 3 - Best Friends
----------------------

This space intentionally left blank.

(for now... sorry)
