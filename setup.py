from setuptools import setup, find_packages

exec(open("qtrio/_version.py", encoding="utf-8").read())

LONG_DESC = open("README.rst", encoding="utf-8").read()

setup(
    name="qtrio",
    version=__version__,
    description="A Qt host for running Trio in guest mode",
    url="https://github.com/python-trio/qtrio",
    long_description=LONG_DESC,
    author="Kyle Altendorf",
    author_email="sda@fstab.net",
    license="MIT -or- Apache License 2.0",
    packages=find_packages(),
    install_requires=["async_generator", "outcome", "trio"],
    extras_require={"pyqt5": ["pyqt5"]},
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
        "Programming Language :: Python :: Implementation :: CPython",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: User Interfaces",
    ],
)
