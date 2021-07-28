.. _lifetime:

Lifetimes
=========

In default usage, QTrio will automatically manage the lifetime of the Qt application.
For the Trio guest mode to function, including during cleanup, the Qt application must
be active and processing events.  If a program changes this process it can cause parts
of the system to not work correctly.  Trio's guest mode can't call any of your
code after the Qt application has quit.  This includes cleanup code such as in
``finally`` blocks.

The most direct way to cause this is by calling :meth:`QtCore.QCoreApplication.quit`.
Enabling :meth:`QtGui.QGuiApplication.setQuitOnLastWindowClosed` and closing all
windows will cause early event loop termination as well.  If manual termination of the
application is truly needed this can be enabled by setting
:attr:`qtrio.Runner.quit_application` to :data:`False`.

QTrio makes an effort to emit a :class:`qtrio.ApplicationQuitWarning`.  The message
includes a link to this page as a reminder.

.. code::

   .../qtrio/_core.py:751: ApplicationQuitWarning: The Qt application quit early.  See https://qtrio.readthedocs.io/en/stable/lifetimes.html

In some cases Trio will emit a warning.

.. code::

   .../trio/_core/_run.py:2221: RuntimeWarning: Trio guest run got abandoned without properly finishing... weird stuff might happen
