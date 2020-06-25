import pathlib
import subprocess
import sysconfig


def test_emissions_help():
    scripts = pathlib.Path(sysconfig.get_path("scripts"))
    subprocess.run([scripts / "qtrio", "examples", "emissions", "--help"], check=True)
