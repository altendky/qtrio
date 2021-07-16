.. _testing:

Testing
=======

pytest-trio provides for using
:ref:`an alternative runner <pytest-trio:trio-run-config>` specified via the
``trio_run`` configuration option.  QTrio is enabled with a value of ``qtrio``.  The
example ``pytest.ini`` below will be common for QTrio test suites.

.. code-block:: ini

   # pytest.ini
   [pytest]
   trio_mode = true
   trio_run = qtrio
