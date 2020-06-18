#!/bin/bash

set -ex -o pipefail

# Log some general info about the environment
env | sort

# Curl's built-in retry system is not very robust; it gives up on lots of
# network errors that we want to retry on. Wget might work better, but it's
# not installed on azure pipelines's windows boxes. So... let's try some good
# old-fashioned brute force. (This is also a convenient place to put options
# we always want, like -f to tell curl to give an error if the server sends an
# error response, and -L to follow redirects.)
function curl-harder() {
    for BACKOFF in 0 1 2 4 8 15 15 15 15; do
        sleep $BACKOFF
        if curl -fL --connect-timeout 5 "$@"; then
            return 0
        fi
    done
    return 1
}

################################################################
# We have a Python environment!
################################################################

python -c "import sys, struct, ssl; print('#' * 70); print('python:', sys.version); print('version_info:', sys.version_info); print('bits:', struct.calcsize('P') * 8); print('openssl:', ssl.OPENSSL_VERSION, ssl.OPENSSL_VERSION_INFO); print('#' * 70)"

python -m pip install -U pip setuptools wheel
python -m pip --version

python setup.py sdist --formats=zip
INSTALL_ARTIFACT=$(ls dist/*.zip)
python -m pip install ${INSTALL_ARTIFACT}${INSTALL_EXTRAS}

if [ "$CHECK_DOCS" = "1" ]; then
    python -m pip install -r docs-requirements.txt
    towncrier --yes  # catch errors in newsfragments
    cd docs
    # -n (nit-picky): warn on missing references
    # -W: turn warnings into errors
    sphinx-build -nW  -b html source build
elif [ "$CHECK_FORMATTING" = "1" ]; then
    python -m pip install -r test-requirements.txt
    source check.sh
else
    # Actual tests
    python -m pip install -r test-requirements.txt

    # We run the tests from inside an empty directory, to make sure Python
    # doesn't pick up any .py files from our working dir. Might have been
    # pre-created by some of the code above.
    mkdir empty || true
    cd empty

    INSTALLDIR=$(python -c "import os, ${PACKAGE_NAME}; print(os.path.dirname(${PACKAGE_NAME}.__file__))")
    cp ../setup.cfg $INSTALLDIR

    # Diagnostic...
    ldd $(python -c 'import PyQt5; import os.path; print(os.path.join(os.path.dirname(PyQt5.__file__), "Qt", "plugins", "platforms", "libqxcb.so"))')

    if pytest -W error -r a --junitxml=../test-results.xml ${INSTALLDIR} --cov="$INSTALLDIR" --cov-config=../.coveragerc --verbose --capture=no --no-qt-log; then
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
