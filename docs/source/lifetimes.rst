Lifetimes
=========

In default usage QTrio will automatically manage the lifetime of the Qt application.
For the Trio guest mode to function, including during cleanup, the Qt application must
be active and processing events.  QTrio will automatically launch and terminate the
application as needed.  If you change this process, such as by calling
:meth:`QtCore.QCoreApplication.quit <QtCore.QCoreApplication.quit>`, you can cause
parts of the system to not work correctly.  Trio's guest mode can't call any of your
code after the application has quit.  This includes cleanup code such as in ``finally``
blocks.  In some cases Trio will emit a warning.

.. code::

   .../trio/_core/_run.py:2221: RuntimeWarning: Trio guest run got abandoned without properly finishing... weird stuff might happen

QTrio will make an effort to warn you as well including directing you to this page.

.. code::

   .../qtrio/_core.py:751: ApplicationQuitWarning: The Qt application quit early.  See https://qtrio.readthedocs.io/en/stable/lifetimes.html
