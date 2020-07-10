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

   + bump version number

      - increment as per `Semantic Versioning <https://semver.org/>`_ rules

      - remove ``+dev`` tag from version number

   + run ``towncrier``

      - review history change

      - ``git rm`` changes

   + fixup `docs/source/history.rst`

      - correct QTrio capitalization

      - remove empty misc changelog entries from the history

   + commit

* push to your personal repository

* create pull request to `altendky/qtrio <https://github.com/altendky/qtrio/pulls>`_'s
  "master" branch

* verify that all checks succeeded

* tag with vX.Y.Z, push tag

* download wheel and sdist from build artifacts and unpack

* push to PyPI::

    twine upload dist/*

* update version number in the same pull request

   + add ``+dev`` tag to the end

* merge the release pull request
