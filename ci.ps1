Set-PSDebug -Trace 1

Get-ChildItem Env:* | Sort-Object name

python -m venv venv
venv/scripts/python -c "import os; import sys; print(os.getcwd()); print(sys.executable); print(sys.version_info)"
venv/scripts/python -m pip install --upgrade pip setuptools wheel
venv/scripts/pip install ".$Env:INSTALL_EXTRAS"
mkdir empty
cd empty
$Env:INSTALLDIR = ((../venv/scripts/python -c "import os, $Env:PACKAGE_NAME; print(os.path.dirname($Env:PACKAGE_NAME.__file__))") | Out-String).trim()
cp ../setup.cfg "$Env:INSTALLDIR"
../venv/scripts/pytest -W error -r a --junitxml=../test-results.xml $Env:INSTALLDIR --cov="$Env:INSTALLDIR" --cov-config=../.coveragerc --verbose --capture=no --no-qt-log
$Env:PASSED = $LastExitCode

# https://github.com/codecov/codecov-exe#introduction
Set-PSDebug -Trace 0
(New-Object System.Net.WebClient).DownloadFile("https://github.com/codecov/codecov-exe/releases/download/1.12.0/codecov-win7-x64.zip", (Join-Path $pwd "Codecov.zip"))
Expand-Archive Codecov.zip -DestinationPath .
Set-PSDebug -Trace 1

./codecov.exe -n "$Env:JOB_NAME"

exit $Env:PASSED
