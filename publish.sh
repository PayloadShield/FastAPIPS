#!/bin/bash

# FastAPI Payload Shield - PyPI Publishing Script
# This script builds and publishes the package to PyPI
# GitHub: https://github.com/PayloadShield/FastAPIPS
#
# Authentication (in priority order):
#   1. PYPI_TOKEN environment variable  (export PYPI_TOKEN=pypi-xxxx)
#   2. ~/.pypirc file
#   3. Interactive prompt (asks for token at runtime)

set -e

echo ""
echo "========================================"
echo "FastAPI Payload Shield - PyPI Publisher"
echo "========================================"
echo ""

# Check if running from the correct directory
if [ ! -f "pyproject.toml" ]; then
    echo "Error: pyproject.toml not found. Please run this script from the project root directory."
    exit 1
fi

# Check Python installation
if ! command -v python &> /dev/null; then
    echo "Error: Python is not installed or not in PATH"
    exit 1
fi

# -------------------------------------------------------
# [1/6] Install / upgrade build tools
# -------------------------------------------------------
echo "[1/6] Ensuring build tools are installed..."
python -m pip install --upgrade pip build twine > /dev/null 2>&1
echo "     Done."

# -------------------------------------------------------
# [2/6] Resolve PyPI credentials
# -------------------------------------------------------
echo "[2/6] Resolving PyPI credentials..."

CRED_SOURCE=""

# Priority 1: PYPI_TOKEN environment variable
if [ -n "$PYPI_TOKEN" ]; then
    echo "     Using PYPI_TOKEN environment variable."
    export TWINE_USERNAME="__token__"
    export TWINE_PASSWORD="$PYPI_TOKEN"
    CRED_SOURCE="env"

# Priority 2: Existing .pypirc
elif [ -f "$HOME/.pypirc" ]; then
    echo "     Using existing ~/.pypirc"
    CRED_SOURCE="pypirc"

# Priority 3: Ask the user for a token interactively
else
    echo ""
    echo "     No credentials found. You need a PyPI API token to publish."
    echo "     Get one at: https://pypi.org/manage/account/token/"
    echo ""
    read -rp "     Paste your PyPI API token (pypi-...): " USER_TOKEN

    if [ -z "$USER_TOKEN" ]; then
        echo "Error: No token provided. Cannot publish without credentials."
        echo ""
        echo "To avoid this prompt, do ONE of the following:"
        echo "  a) Set environment variable:  export PYPI_TOKEN=pypi-xxxx"
        echo "  b) Create ~/.pypirc  (see below)"
        echo ""
        echo "~/.pypirc contents:"
        echo "  [distutils]"
        echo "  index-servers = pypi"
        echo ""
        echo "  [pypi]"
        echo "  username = __token__"
        echo "  password = pypi-YOUR-TOKEN-HERE"
        echo ""
        exit 1
    fi

    # Validate token prefix
    if [[ ! "$USER_TOKEN" == pypi-* ]]; then
        echo ""
        echo "Warning: Token does not start with 'pypi-'. PyPI API tokens should start with 'pypi-'."
        echo "         Proceeding anyway, but upload may fail."
        echo ""
    fi

    export TWINE_USERNAME="__token__"
    export TWINE_PASSWORD="$USER_TOKEN"
    CRED_SOURCE="prompt"

    # Offer to save token to .pypirc for next time
    echo ""
    read -rp "     Save token to ~/.pypirc for future use? (y/N): " SAVE_TOKEN
    if [[ "$SAVE_TOKEN" =~ ^[Yy]$ ]]; then
        cat > "$HOME/.pypirc" <<PYPIRC
[distutils]
index-servers = pypi

[pypi]
username = __token__
password = $USER_TOKEN
PYPIRC
        chmod 600 "$HOME/.pypirc"
        echo "     Saved! Future publishes will use .pypirc automatically."
    fi
fi

echo "     Credentials ready [source: $CRED_SOURCE]"

# -------------------------------------------------------
# [3/6] Clean previous builds
# -------------------------------------------------------
echo "[3/6] Cleaning previous builds..."
rm -rf build dist *.egg-info
echo "     Done."

# -------------------------------------------------------
# [4/6] Build distribution packages
# -------------------------------------------------------
echo "[4/6] Building distribution packages..."
python -m build
echo "     Build successful."

# -------------------------------------------------------
# [5/6] Verify package
# -------------------------------------------------------
echo "[5/6] Verifying package with twine check..."
python -m twine check dist/*
echo "     Package OK."

# -------------------------------------------------------
# [6/6] Upload to PyPI
# -------------------------------------------------------
echo ""
echo "[6/6] Publishing to PyPI..."
echo ""
echo "========================================"
echo "Package Information:"
echo "========================================"
python -c "
import re
content = open('pyproject.toml').read()
name = re.search(r'name = \"([^\"]+)\"', content)
version = re.search(r'version = \"([^\"]+)\"', content)
if name: print(f'  Name:    {name.group(1)}')
if version: print(f'  Version: {version.group(1)}')
print(f'  Repo:    https://github.com/PayloadShield/FastAPIPS')
"
echo "========================================"
echo ""

# Upload with --non-interactive to prevent hanging on missing creds
if python -m twine upload dist/* --non-interactive --skip-existing --verbose; then
    echo ""
    echo "========================================"
    echo "  SUCCESS - Package published to PyPI!"
    echo "========================================"
    echo ""
    echo "  View:    https://pypi.org/project/fastapi_payloadshield/"
    echo "  Install: pip install fastapi_payloadshield"
    echo "  GitHub:  https://github.com/PayloadShield/FastAPIPS"
    echo ""
else
    echo ""
    echo "========================================"
    echo "  Upload FAILED"
    echo "========================================"
    echo ""
    echo "Troubleshooting:"
    echo "  1. Make sure your PyPI API token is valid"
    echo "     Get a new one: https://pypi.org/manage/account/token/"
    echo "  2. If this version already exists on PyPI, bump the version"
    echo "     in pyproject.toml and re-run this script"
    echo "  3. Check your internet connection"
    echo ""
    exit 1
fi
