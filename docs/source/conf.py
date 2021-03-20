#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Documentation build configuration file, created by
# sphinx-quickstart on Sat Jan 21 19:11:14 2017.
#
# This file is execfile()d with the current directory set to its
# containing dir.
#
# Note that not all possible configuration values are present in this
# autogenerated file.
#
# All configuration values have a default; values that are commented out
# serve to show the default.

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys

import sphinx.locale
import sphinx.util

# So autodoc can import our package
sys.path.insert(0, os.path.abspath("../.."))

# Warn about all references to unknown targets
nitpicky = True
# Except for these ones, which we expect to point to unknown targets:
nitpick_ignore = [
    # Format is ("sphinx reference type", "string"), e.g.:
    ("py:obj", "bytes-like"),
    # https://github.com/sphinx-doc/sphinx/issues/8127
    ("py:class", ".."),
    # https://github.com/sphinx-doc/sphinx/issues/7493
    ("py:class", "qtrio._core.Emissions"),
    ("py:class", "qtrio._core.EmissionsNursery"),
    ("py:class", "qtrio._core.Outcomes"),
    ("py:class", "qtrio._core.Reenter"),
    ("py:class", "qtrio._qt.Signal"),
    # https://github.com/Czaki/sphinx-qt-documentation/issues/10
    ("py:class", "<class 'PySide2.QtCore.QEvent.Type'>"),
    ("py:class", "<class 'PySide2.QtWidgets.QFileDialog.FileMode'>"),
    ("py:class", "<class 'PySide2.QtWidgets.QFileDialog.AcceptMode'>"),
    ("py:class", "<class 'PySide2.QtWidgets.QFileDialog.Option'>"),
    ("py:class", "<class 'PySide2.QtWidgets.QMessageBox.Icon'>"),
    # https://github.com/sphinx-doc/sphinx/issues/8136
    ("py:class", "typing.AbstractAsyncContextManager"),
]

# -- General configuration ------------------------------------------------

# If your documentation needs a minimal Sphinx version, state it here.
#
# needs_sphinx = '1.0'

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.coverage",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx_autodoc_typehints",
    "sphinx_qt_documentation",
    "sphinxcontrib_trio",
    "sphinxcontrib.restbuilder",
]

intersphinx_mapping = {
    "outcome": ("https://outcome.readthedocs.io/en/stable", None),
    "python": ("https://docs.python.org/3", None),
    "PyQt5": ("https://www.riverbankcomputing.com/static/Docs/PyQt5", None),
    "pytest": ("https://docs.pytest.org/en/stable", None),
    "pytest-trio": ("https://pytest-trio.readthedocs.io/en/stable", None),
    "trio": ("https://trio.readthedocs.io/en/stable", None),
}

qt_documentation = "Qt5"

autodoc_default_options = {
    "member-order": "bysource",
    "members": True,
    "show-inheritance": True,
    "undoc-members": True,
}

logger = sphinx.util.logging.getLogger(__name__)

set_type_checking_flag = True
typehints_fully_qualified = False
always_document_param_types = False
typehints_document_rtype = True


def warn_undocumented_members(app, what, name, obj, options, lines):
    if len(lines) == 0:
        logger.warning(sphinx.locale.__(f"{what} {name} is undocumented"))
        lines.append(f".. Warning:: {what} ``{name}`` undocumented")


# Add any paths that contain templates here, relative to this directory.
templates_path = []

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
#
# source_suffix = ['.rst', '.md']
source_suffix = ".rst"

# The master toctree document.
master_doc = "index"

# General information about the project.
project = "QTrio"
copyright = "The QTrio authors"
author = "The QTrio authors"

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#
# The short X.Y version.
import qtrio

version = qtrio.__version__
# The full version, including alpha/beta/rc tags.
release = version


def process_newsfragments():
    import pathlib
    import subprocess
    import sysconfig

    # TODO: needs released https://github.com/twisted/towncrier/commit/5c431028a3b699c74b162014e907272cbea8ac81
    bin = pathlib.Path(sysconfig.get_path("scripts"))
    subprocess.run(
        [bin / "towncrier", "build", "--yes", "--name", "QTrio"],
        check=True,
        cwd="../..",
    )


if "+dev" in version and os.environ.get("READTHEDOCS") is not None:
    process_newsfragments()

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = None

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This patterns also effect to html_static_path and html_extra_path
exclude_patterns = []

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = "sphinx"

# The default language for :: blocks
highlight_language = "python3"

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = False


# -- Options for HTML output ----------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
# html_theme = 'alabaster'

# We have to set this ourselves, not only because it's useful for local
# testing, but also because if we don't then RTD will throw away our
# html_theme_options.
import sphinx_rtd_theme

html_theme = "sphinx_rtd_theme"
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
#
html_theme_options = {
    # default is 2
    # show deeper nesting in the RTD theme's sidebar TOC
    # https://stackoverflow.com/questions/27669376/
    # I'm not 100% sure this actually does anything with our current
    # versions/settings...
    "navigation_depth": 4,
    "logo_only": True,
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]


# -- Options for HTMLHelp output ------------------------------------------

# Output file base name for HTML help builder.
htmlhelp_basename = "qtriodoc"


# -- Options for LaTeX output ---------------------------------------------

latex_elements = {
    # The paper size ('letterpaper' or 'a4paper').
    #
    # 'papersize': 'letterpaper',
    # The font size ('10pt', '11pt' or '12pt').
    #
    # 'pointsize': '10pt',
    # Additional stuff for the LaTeX preamble.
    #
    # 'preamble': '',
    # Latex figure (float) alignment
    #
    # 'figure_align': 'htbp',
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
    (master_doc, "qtrio.tex", "Trio Documentation", author, "manual"),
]


# -- Options for manual page output ---------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [(master_doc, "qtrio", "QTrio Documentation", [author], 1)]


# -- Options for Texinfo output -------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (
        master_doc,
        "qtrio",
        "QTrio Documentation",
        author,
        "QTrio",
        "a library bringing Qt GUIs together with ``async`` and ``await`` via Trio",
        "Miscellaneous",
    ),
]


def setup(app: "sphinx.application.Sphinx") -> None:
    app.add_crossref_type(
        "fixture",
        "fixture",
        objname="built-in fixture",
        indextemplate="pair: %s; fixture",
    )
    app.connect("autodoc-process-docstring", warn_undocumented_members)
