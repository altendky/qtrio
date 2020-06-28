Set-PSDebug -Trace 1
python -c "import os; import sys; print(os.getcwd()); print(sys.executable); print(sys.version_info)"
python -m venv venv
venv/scripts/python -m pip install --upgrade pip setuptools wheel
venv/scripts/pip install ".$Env:INSTALL_EXTRAS"
mkdir empty
cd empty
../venv/scripts/pytest qtrio --pyargs
$Env:INSTALLDIR=$(python -c "import os, ${PACKAGE_NAME}; print(os.path.dirname(${PACKAGE_NAME}.__file__))")
cp ../setup.cfg $Env:INSTALLDIR
if ()pytest -W error -r a --junitxml=../test-results.xml $Env:INSTALLDIR --cov="$Env:INSTALLDIR" --cov-config=../.coveragerc --verbose --capture=no --no-qt-log){
    $Env:PASSED = 0
} else {
    $Env:PASSED = 1
}

# https://github.com/codecov/codecov-exe#introduction
(New-Object System.Net.WebClient).DownloadFile("https://github.com/codecov/codecov-exe/releases/download/1.12.0/codecov-win7-x64.zip", (Join-Path $pwd "Codecov.zip"))
Expand-Archive .\Codecov.zip -DestinationPath .
.\Codecov\codecov.exe -n "$Env:JOB_NAME"

exit $Env:PASSED
