@echo off
REM ============================================================================
REM Windows Cleanup Tool - Setup and Run Script
REM This batch file helps install dependencies and run the app
REM ============================================================================

REM Change to the script directory
cd /d "%~dp0"

REM Check if running as Administrator
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo.
    echo ============================================================
    echo ERROR: This script must run as Administrator!
    echo ============================================================
    echo.
    echo Right-click this file and select "Run as administrator"
    echo.
    pause
    exit /b 1
)

REM ============================================================================
REM MENU - Ask user what to do
REM ============================================================================
:menu
cls
echo.
echo ============================================================
echo    Windows Cleanup Tool - Setup
echo ============================================================
echo.
echo What would you like to do?
echo.
echo 1. Install dependencies (first time only)
echo 2. Run the cleanup app
echo 3. Build standalone .exe
echo 4. Exit
echo.
set /p choice="Enter your choice (1-4): "

if "%choice%"=="1" goto install
if "%choice%"=="2" goto run
if "%choice%"=="3" goto build
if "%choice%"=="4" goto end
echo Invalid choice. Please try again.
timeout /t 2 >nul
goto menu

REM ============================================================================
REM OPTION 1: Install Dependencies
REM ============================================================================
:install
cls
echo.
echo Installing required Python packages...
echo.

REM Check if pip is available
python -m pip --version >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    goto menu
)

REM Install packages from requirements.txt
python -m pip install -r requirements.txt

if %errorLevel% equ 0 (
    echo.
    echo ============================================================
    echo SUCCESS: All dependencies installed!
    echo ============================================================
    echo.
) else (
    echo.
    echo ERROR: Failed to install dependencies
    echo.
)

pause
goto menu

REM ============================================================================
REM OPTION 2: Run the Cleanup App
REM ============================================================================
:run
cls
echo.
echo Starting Windows Cleanup Tool...
echo.

REM Run the Python app
python cleanup_app.py

if %errorLevel% neq 0 (
    echo.
    echo ERROR: Failed to run the app
    echo Make sure all dependencies are installed (choose option 1)
    echo.
    pause
)

goto menu

REM ============================================================================
REM OPTION 3: Build Standalone .exe
REM ============================================================================
:build
cls
echo.
echo Building standalone .exe file...
echo This may take a few minutes...
echo.

REM Check if PyInstaller is installed
python -m PyInstaller --version >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: PyInstaller not installed
    echo Please run option 1 to install dependencies first
    echo.
    pause
    goto menu
)

REM Build the .exe
python -m PyInstaller --onefile --windowed cleanup_app.py

if %errorLevel% equ 0 (
    echo.
    echo ============================================================
    echo SUCCESS: .exe file created!
    echo ============================================================
    echo.
    echo Location: dist\cleanup_app.exe
    echo.
    echo You can now double-click cleanup_app.exe to run the app
    echo No Python installation needed!
    echo.
) else (
    echo.
    echo ERROR: Failed to build .exe
    echo.
)

pause
goto menu

REM ============================================================================
REM EXIT
REM ============================================================================
:end
echo.
echo Goodbye!
echo.
