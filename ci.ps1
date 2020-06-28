python -c "import os; import sys; print(os.getcwd()); print(sys.executable); print(sys.version_info)"
python -m venv venv
venv/scripts/python -m pip install --upgrade pip setuptools wheel
venv/scripts/pip install .${INSTALL_EXTRAS}
mkdir empty
cd empty
../venv/scripts/pytest qtrio --pyargs
