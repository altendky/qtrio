import pathlib

from setuptools import setup, find_packages


here = pathlib.Path(__file__).parent

exec((here / "qtrio" / "_version.py").read_text(encoding="utf-8"))

LONG_DESC = (here / "README.rst").read_text(encoding="utf-8")

# >= 6 for type hints
pytest = "pytest >= 6"
# >= 19.9.0rc1 for https://github.com/twisted/towncrier/issues/144
towncrier = "towncrier >= 19.9.0rc1"

extras_cli = ["click"]
extras_examples = [*extras_cli]

setup(
    name="qtrio",
    version=__version__,
    description=(
        "a library bringing Qt GUIs together with ``async`` and ``await`` via Trio"
    ),
    url="https://github.com/altendky/qtrio",
    project_urls={
        "Documentation": "https://qtrio.readthedocs.io/",
        "Chat": "https://gitter.im/python-trio/general",
        "Forum": "https://trio.discourse.group/",
        "Issues": "https://github.com/altendky/qtrio/issues",
        "Repository": "https://github.com/altendky/qtrio",
        "Tests": "https://github.com/altendky/qtrio/actions?query=branch%3Amaster",
        "Coverage": "https://codecov.io/gh/altendky/qtrio",
        "Distribution": "https://pypi.org/project/qtrio",
    },
    long_description=LONG_DESC,
    author="Kyle Altendorf",
    author_email="sda@fstab.net",
    license="MIT -or- Apache License 2.0",
    packages=find_packages(),
    install_requires=[
        "async_generator",
        "attrs",
        "decorator",
        "outcome",
        "qtpy",
        # trio >= 0.16 for guest mode
        "trio >= 0.16",
        # python_version < '3.8' for `Protocol`
        "typing-extensions; python_version < '3.8'",
    ],
    extras_require={
        "p_checks": ["black", "flake8", "mypy", pytest, towncrier],
        "p_docs": [
            pytest,
            # >= 3.2: https://github.com/sphinx-doc/sphinx/issues/8008
            # >= 3.2.1: https://github.com/sphinx-doc/sphinx/issues/8124
            "sphinx >= 3.2.1",
            "sphinx-autodoc-typehints",
            "sphinx-qt-documentation>=0.3",
            "sphinx_rtd_theme",
            "sphinxcontrib-trio",
            towncrier,
        ],
        "p_tests": [
            *extras_cli,
            *extras_examples,
            "click",
            "coverage",
            pytest,
            "pytest-cov",
            "pytest-faulthandler",
            "pytest-qt",
            # > 0.6.0 for trio_run configuration support
            "pytest-trio",
            'pytest-xvfb; sys_platform == "linux"',
        ],
        "cli": extras_cli,
        "examples": extras_examples,
        "pyqt5": [
            # >= 5.15.1 for https://www.riverbankcomputing.com/pipermail/pyqt/2020-July/043064.html
            "pyqt5 >= 5.15.1",
            "pyqt5-stubs",
        ],
        "pyside2": ["pyside2"],
    },
    entry_points={"console_scripts": ["qtrio = qtrio._cli:cli"]},
    keywords=["async", "io", "Trio", "GUI", "Qt", "PyQt5", "PySide2"],
    python_requires=">=3.6",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "License :: OSI Approved :: Apache Software License",
        "Framework :: Trio",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: Implementation :: CPython",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: User Interfaces",
    ],
)
