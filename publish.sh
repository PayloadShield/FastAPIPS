#!/bin/bash

# FastAPI Payload Shield - PyPI Publishing Script
# This script builds and publishes the package to PyPI
# GitHub: https://github.com/PayloadShield/FastAPIPS

set -e

echo ""
echo "========================================"
echo "FastAPI Payload Shield - PyPI Publisher"
echo "========================================"
echo ""

# Check if running from the correct directory
if [ ! -f "setup.py" ]; then
    echo "Error: setup.py not found. Please run this script from the project root directory."
    exit 1
fi

# Check Python installation
if ! command -v python &> /dev/null; then
    echo "Error: Python is not installed or not in PATH"
    exit 1
fi

echo "[1/5] Checking dependencies..."
if ! python -m pip list | grep -E "build|twine" &> /dev/null; then
    echo "Installing required packages..."
    python -m pip install --upgrade build twine
fi

echo "[2/5] Cleaning previous builds..."
rm -rf build dist *.egg-info

echo "[3/5] Building distribution packages..."
python -m build

echo "[4/5] Verifying package contents..."
python -m twine check dist/*

echo ""
echo "[5/5] Publishing to PyPI..."
echo ""
echo "========================================"
echo "Package Information:"
echo "========================================"
python << 'EOF'
import re
with open('setup.py', 'r') as f:
    content = f.read()
    name = re.search(r'name="([^"]+)"', content)
    version = re.search(r'version="([^"]+)"', content)
    if name:
        print(f'Package Name: {name.group(1)}')
    if version:
        print(f'Version: {version.group(1)}')
print('Repository: https://github.com/PayloadShield/FastAPIPS')
print('License: Apache-2.0')
EOF
echo "========================================"
echo ""
echo "Note: You will be prompted for PyPI credentials"
echo "If you don't have a PyPI account, create one at: https://pypi.org/account/register/"
echo ""

# Publish to PyPI
if python -m twine upload dist/* --verbose; then
    echo ""
    echo "========================================"
    echo "Success! Package published to PyPI"
    echo "========================================"
    echo ""
    echo "Published at: https://pypi.org/project/fastapi_payloadshield/"
    echo "GitHub Repository: https://github.com/PayloadShield/FastAPIPS"
    echo "Documentation: https://github.com/PayloadShield/FastAPIPS#readme"
    echo ""
    echo "Install with: pip install fastapi_payloadshield"
    echo ""
else
    echo "Error: Upload to PyPI failed"
    echo ""
    echo "Troubleshooting tips:"
    echo "- Make sure you have a PyPI account: https://pypi.org/account/register/"
    echo "- Check your credentials and try again"
    echo "- If using 2FA, you may need to use an API token"
    echo ""
    exit 1
fi
