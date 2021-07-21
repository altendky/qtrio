.. include:: use_latest_docs.rst

Reviewing
=========

Manual checks
-------------

* The change should happen
   * The bug is a bug
   * The feature is an improvement
   * The code belongs in QTrio, not another package
      * Unless it is a workaround in QTrio temporarily or because the proper library has
        declined to resolve the issue.

* Relevant bugs or features are being tested
   * The line coverage provided by automatic coverage checks are valuable but you are
     the only one that can decide if the proper functionality is being tested

* Documentation updates
   * Docstrings are present and accurate for all modules, classes, methods, and
     functions including private ones and tests.
   * For bug fixes consider if the docs should be updated to clarify proper behavior
   * For feature additions consider if prose in the docs should be updated in addition
     to the docstrings.

* The change is described for the user
   * If this is a change relevant to users, there should be a newsfragment file as follows
   * Newsfragment file name has the proper issue or PR number and change type
   * The contents describe the change well for users
   * Proper `Sphinx references <https://www.sphinx-doc.org/en/3.x/usage/restructuredtext/basics.html>`_
     are used where appropriate

Automatic checks
----------------

* Full test suite passes across:
   * operating systems
   * Python versions
   * Qt libraries

* All code and tests lines are fully covered when running tests
* Code is formatted per `Black <https://black.readthedocs.io/en/stable/>`_
* Code passes `flake8 <https://flake8.pycqa.org/en/latest/>`_ checks
* Docs build successfully including newsfragment, if present
* Branch is up to date with main
