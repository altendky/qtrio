.. include:: use_latest_docs.rst

Testing
=======

While developing it is important to make certain that the existing tests continue to
pass and that any changes you make also have passing tests that exercise them.  This
will be done in it's entirety for you when you submit PR.  These runs will cover
multiple operating systems, Python versions, and Qt libraries.  They will also check
formatting, the documentation build, and more.

Still, sometimes you would rather run the tests locally for potentially quicker
feedback, the opportunity to debug, and less public observation of your every commit.
You can run ``pytest``, ``black``, and ``sphinx`` directly from your own installation.

.. code-block:: bash

   python -m venv testvenv
   testvenv/bin/python -m pip install --upgrade pip setuptools wheel
   testvenv/bin/python -m pip install --editable .[pyside2,p_checks,p_docs,p_tests]
   testvenv/bin/pytest --pyargs qtrio

The CI test script, ``ci.sh``, in the project root will run ``pytest`` with ``coverage``
(and fail to upload the coverage results, which is ok).  Note that the ``ci.sh`` script
builds the package into ``dist/`` and then installs whatever is in that directory.  As
such you will generally want to delete the contents of ``dist/`` prior to running
``ci.sh``.

.. code-block:: bash

   python -m venv testvenv
   source testvenv/bin/activate
   ./ci.sh

Automatic code reformatting is handled by ``black``.

.. code-block:: bash

   python -m venv testvenv
   testvenv/bin/python -m pip install --upgrade pip setuptools wheel
   testvenv/bin/python -m pip install black
   testvenv/bin/black .

Linting is handled by ``flake8``.

.. code-block:: bash

   python -m venv testvenv
   testvenv/bin/python -m pip install --upgrade pip setuptools wheel
   testvenv/bin/python -m pip install flake8
   testvenv/bin/flake8 setup.py docs/ qtrio/

The documentation can be built with ``sphinx``.

.. code-block:: bash

   python -m venv testvenv
   testvenv/bin/python -m pip install --upgrade pip setuptools wheel
   testvenv/bin/python -m pip install --editable .[pyside2,p_docs]
   source testenv/bin/activate
   cd docs/
   make html --always-make

I don't like to write the hazardous command that does it, but it is good to remove the
entire ``docs/build/`` directory prior to each build of the documentation.  After
building the documentation it can be loaded in your browser at
``file:///path/to/qtrio/docs/build/html/index.html``.
