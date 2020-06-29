import os
import pathlib
import subprocess
import sysconfig


def test_emissions_help():
    """The console script doesn't fail when asked for --help for the emissions
    example.
    """
    scripts = pathlib.Path(sysconfig.get_path("scripts"))
    subprocess.run(
        [os.fspath(scripts / "qtrio"), "examples", "emissions", "--help"], check=True
    )
