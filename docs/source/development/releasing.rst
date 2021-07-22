.. include:: use_latest_docs.rst

.. _releasing:

Preparing a release
-------------------

Things to do for releasing:

* check for open issues / pull requests that really should be in the release

   + come back when these are done

   + … or ignore them and do another release next week

* check for deprecations "long enough ago" (two months or two releases, whichever is longer)

   + remove affected code

* do the actual release changeset

   + select new version number

      - increment as per `Semantic Versioning <https://semver.org/>`_ rules

   + checkout a new branch ``release-vX.Y.Z``

   + bump version number in ``qtrio/_version.py``

      - remove ``+dev`` tag from version number

   + run ``towncrier``

..
   https://github.com/twisted/towncrier/pull/271

      - ``towncrier build --yes``

      - review history change

      - ``git rm`` changes

   + fixup `docs/source/history.rst`

      - correct QTrio capitalization

      - remove empty misc changelog entries from the history

   + commit such as ``Bump version and run towncrier for vX.Y.Z release``

* push to the primary repository

  + a tag will be created on the branch and the tag should be in the primary repository

* create pull request to `altendky/qtrio <https://github.com/altendky/qtrio/pulls>`_'s
  "main" branch

* verify that all checks succeeded

* get a review

* tag with ``vX.Y.Z``, push tag

* download wheel and sdist from build artifacts and unpack

* push to PyPI::

    twine upload dist/*

* replace the ``+dev`` version tag in the same pull request as ``vX.Y.Z+dev``

* merge the release pull request
