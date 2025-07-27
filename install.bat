@echo off
SETLOCAL

echo Checking for Python...
py --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python is not installed or not in your PATH.
    EXIT /B 1
)

echo Creating virtual environment...
if NOT exist .venv (
    py -m venv .venv
    echo Virtual environment created.
) else (
    echo Virtual environment already exists.
)

echo Activating virtual environment...
call .venv\Scripts\activate.bat

echo Upgrading pip to the latest version...
py -m pip install --upgrade pip

echo Installing dependencies from requirements.txt...
py -m pip install -r requirements.txt

echo All dependencies installed successfully in virtual environment.

set /p DISCORD_TOKEN="Enter your Discord bot token: "
echo DISCORD_TOKEN=%DISCORD_TOKEN% > .env
echo .env file created with your bot token.

ENDLOCAL
pause