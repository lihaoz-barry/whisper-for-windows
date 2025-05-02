@echo off
setlocal enabledelayedexpansion
cd "%~dp0"
echo Running Whisper Transcriber with embedded Python...

rem Check if the site-packages directory exists
if not exist site-packages (
    echo Site packages directory not found.
    echo Running install_deps.bat to set up the environment...
    call install_deps.bat
)

echo Setting PYTHONPATH to ensure modules can be found...
set PYTHONPATH=%cd%\site-packages
set PYTHONHOME=%cd%\python

echo Python paths:
.\python\python.exe -c "import sys; print('Python executable:', sys.executable); print('Python version:', sys.version); print('Python paths:'); [print(f'  {p}') for p in sys.path]"

echo Starting the application...
.\python\python.exe ..\src\run.py
if %ERRORLEVEL% NEQ 0 (
    echo Application exited with error code %ERRORLEVEL%
    pause
)
