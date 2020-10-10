.. _releasing:

Preparing a release
-------------------

Things to do for releasing:

* check for open issues / pull requests that really should be in the release

   + come back when these are done

   + … or ignore them and do another release next week

* check for deprecations "long enough ago" (two months or two releases, whichever is longer)

   + remove affected code

* tag the existing release changeset on master

   + Pick new version vX.Y.Z

      - increment as per `Semantic Versioning <https://semver.org/>`_ rules

   + ``git tag vX.Y.Z``

   + ``git push --tags``

* download wheel and sdist from build artifacts and unpack

* push to PyPI::

    twine upload dist/*

* create a post-release cleanup branch

   + ``git checkout -b cleanup_vX.Y.Z``

..
   https://github.com/twisted/towncrier/pull/271

   + ``towncrier build --yes --name QTrio``

   + ``git commit -m 'Cleanup for release vX.Y.Z'``

* push to your personal repository

* create pull request to `altendky/qtrio <https://github.com/altendky/qtrio/pulls>`_'s
  ``master`` branch

* merge the cleanup pull request
