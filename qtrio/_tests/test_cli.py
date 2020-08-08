import os
import pathlib
import subprocess
import sys
import sysconfig


def test_emissions_help_entry_point():
    """The console script entry point doesn't fail when asked for --help for the
    emissions example.
    """
    scripts_string = sysconfig.get_path("scripts")

    if scripts_string is None:  # pragma: no cover
        assert False, "No scripts path found in sysconfig paths"

    scripts = pathlib.Path(scripts_string)
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
