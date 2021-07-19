import pathlib

from setuptools import setup, find_packages


here = pathlib.Path(__file__).parent

exec((here / "qtrio" / "_version.py").read_text(encoding="utf-8"))

LONG_DESC = (here / "README.rst").read_text(encoding="utf-8")

# >= 21.3.0 for https://github.com/twisted/towncrier/pull/170
towncrier = "towncrier >= 21.3.0"

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
        "pytest",
        "qtpy",
        "trio>=0.16",
    ],
    extras_require={
        "checks": ["black", "flake8", "mypy", towncrier],
        "docs": [
            "sphinx >= 1.7.0",
            "sphinx-autodoc-typehints",
            "sphinx-qt-documentation>=0.3",
            "sphinx_rtd_theme",
            "sphinxcontrib-trio",
            towncrier,
        ],
        "examples": ["click"],
        "pyqt5": ["pyqt5", "pyqt5-stubs"],
        "pyside2": ["pyside2"],
        "tests": [
            "click",
            "coverage",
            "pytest",
            "pytest-cov",
            "pytest-faulthandler",
            "pytest-qt",
            'pytest-xvfb; sys_platform == "linux"',
        ],
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
