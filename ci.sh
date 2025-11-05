#!/bin/bash

set -ex -o pipefail

# Log some general info about the environment
env | sort

function try-harder() {
    for BACKOFF in 0 1 2 4 8 15 15 15 15; do
        sleep $BACKOFF
        if "$@"; then
            return 0
        fi
    done
    return 1
}

# Curl's built-in retry system is not very robust; it gives up on lots of
# network errors that we want to retry on. Wget might work better, but it's
# not installed on azure pipelines's windows boxes. So... let's try some good
# old-fashioned brute force. (This is also a convenient place to put options
# we always want, like -f to tell curl to give an error if the server sends an
# error response, and -L to follow redirects.)
function curl-harder() {
    try-harder curl -fL --connect-timeout 5 "$@"
}

################################################################
# We have a Python environment!
################################################################

python -c "import sys, struct, ssl; print('#' * 70); print('executable:', sys.executable); print('python:', sys.version); print('version_info:', sys.version_info); print('bits:', struct.calcsize('P') * 8); print('openssl:', ssl.OPENSSL_VERSION, ssl.OPENSSL_VERSION_INFO); print('#' * 70)"

python -m pip install -U pip setuptools wheel pep517
python -m pip --version

python -m pep517.build --source --out-dir dist/ .
INSTALL_ARTIFACT=$(ls dist/*.tar.gz)
try-harder python -m pip install ${INSTALL_ARTIFACT}${INSTALL_EXTRAS}

python -m pip list
python -m pip freeze

if [ "$CHECK_DOCS" = "1" ]; then
    git fetch --deepen=100
    git fetch --depth=100 origin main
    towncrier build --yes  # catch errors in newsfragments
    cd docs
    # -n (nit-picky): warn on missing references
    # -W: turn warnings into errors
    sphinx-build -nW  -b html source build
elif [ "$CHECK_FORMATTING" = "1" ]; then
    source check.sh
elif [ "$CHECK_TYPE_HINTS" = "1" ]; then
    if [[ "${INSTALL_EXTRAS,,}" == *"pyside2"* ]]; then
        python -m pip install --upgrade pyside2
    fi
    mypy --package qtrio $(qts mypy args)
elif [ "$CHECK_MANIFEST" = "1" ]; then
    check-manifest
else
    # Actual tests

    # We run the tests from inside an empty directory, to make sure Python
    # doesn't pick up any .py files from our working dir. Might have been
    # pre-created by some of the code above.
    mkdir empty || true
    cd empty

    INSTALLDIR=$(python -c "import os, qtrio; print(os.path.dirname(qtrio.__file__))")
    cp ../setup.cfg $INSTALLDIR
    # We have to copy .coveragerc into this directory, rather than passing
    # --cov-config=../.coveragerc to pytest, because codecov.sh will run
    # 'coverage xml' to generate the report that it uses, and that will only
    # apply the ignore patterns in the current directory's .coveragerc.
    cp ../.coveragerc .
    if pytest -ra --junitxml=../test-results.xml --cov="$INSTALLDIR" --verbose --pyargs qtrio; then
        PASSED=true
    else
        PASSED=false
    fi

    # The codecov docs recommend something like 'bash <(curl ...)' to pipe the
    # script directly into bash as its being downloaded. But, the codecov
    # server is flaky, so we instead save to a temp file with retries, and
    # wait until we've successfully fetched the whole script before trying to
    # run it.
    curl-harder -o codecov.sh https://codecov.io/bash
    bash codecov.sh -n "${JOB_NAME}"

    $PASSED
fi
