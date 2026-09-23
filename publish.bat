@echo off
REM FastAPI Payload Shield - PyPI Publishing Script
REM This script builds and publishes the package to PyPI
REM GitHub: https://github.com/PayloadShield/FastAPIPS

setlocal enabledelayedexpansion

echo.
echo ========================================
echo FastAPI Payload Shield - PyPI Publisher
echo ========================================
echo.

REM Check if running from the correct directory
if not exist "setup.py" (
    echo Error: setup.py not found. Please run this script from the project root directory.
    exit /b 1
)

REM Check Python installation
python --version > nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    exit /b 1
)

echo [1/5] Checking dependencies...
python -m pip list | findstr /R "build twine" > nul
if errorlevel 1 (
    echo Installing required packages...
    python -m pip install --upgrade build twine
    if errorlevel 1 (
        echo Error: Failed to install build tools
        exit /b 1
    )
)

echo [2/5] Cleaning previous builds...
if exist "build\" (
    rmdir /s /q build
)
if exist "dist\" (
    rmdir /s /q dist
)
if exist "*.egg-info\" (
    for /d %%X in (*.egg-info) do rmdir /s /q "%%X"
)

echo [3/5] Building distribution packages...
python -m build
if errorlevel 1 (
    echo Error: Build failed
    exit /b 1
)

echo [4/5] Verifying package contents...
python -m twine check dist/*
if errorlevel 1 (
    echo Error: Package verification failed
    exit /b 1
)

echo.
echo [5/5] Publishing to PyPI...
echo.
echo ========================================
echo Package Information:
echo ========================================
python -c "
import re
with open('setup.py', 'r') as f:
    content = f.read()
    name = re.search(r'name=\"([^\"]+)\"', content)
    version = re.search(r'version=\"([^\"]+)\"', content)
    if name:
        print(f'Package Name: {name.group(1)}')
    if version:
        print(f'Version: {version.group(1)}')
print('Repository: https://github.com/PayloadShield/FastAPIPS')
print('License: Apache-2.0')
"
echo ========================================
echo.
echo Note: You will be prompted for PyPI credentials
echo If you don't have a PyPI account, create one at: https://pypi.org/account/register/
echo.

REM Publish to PyPI
python -m twine upload dist/* --verbose
if errorlevel 1 (
    echo Error: Upload to PyPI failed
    echo.
    echo Troubleshooting tips:
    echo - Make sure you have a PyPI account: https://pypi.org/account/register/
    echo - Check your credentials and try again
    echo - If using 2FA, you may need to use an API token
    echo.
    exit /b 1
)

echo.
echo ========================================
echo Success! Package published to PyPI
echo ========================================
echo.
echo Published at: https://pypi.org/project/fastapi_payloadshield/
echo GitHub Repository: https://github.com/PayloadShield/FastAPIPS
echo Documentation: https://github.com/PayloadShield/FastAPIPS#readme
echo.
echo Install with: pip install fastapi_payloadshield
echo.

endlocal
exit /b 0
