import os
import pathlib
import subprocess
import sys
import sysconfig


def test_emissions_help_entry_point():
    """The console script entry point doesn't fail when asked for --help for the
    emissions example.
    """
    scripts = pathlib.Path(sysconfig.get_path("scripts"))
    subprocess.run(
        [os.fspath(scripts / "qtrio"), "examples", "emissions", "--help"], check=True
    )


def test_emissions_help_dash_m():
    """The CLI run via ``python -m qtrio`` doesn't fail when asked for --help for the
    emissions example.
    """
    subprocess.run(
        [sys.executable, "-m", "qtrio", "examples", "emissions", "--help"], check=True
    )
