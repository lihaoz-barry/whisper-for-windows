@echo off
cd "%~dp0\python"
echo Running get-pip.py from the current directory...
python.exe get-pip.py
if %ERRORLEVEL% NEQ 0 (
    echo Failed to install pip
    pause
    exit /b 1
)
cd ..
echo Pip installed successfully
