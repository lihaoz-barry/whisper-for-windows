@echo off
setlocal enabledelayedexpansion
cd "%~dp0"
echo Installing dependencies for development...

rem Check if pip is installed, if not install it
if not exist "python\Scripts\pip.exe" (
    echo Pip not found, installing it first...
    call install_pip.bat
)

rem Check CUDA capability
echo Checking for CUDA-capable GPU...
python\python.exe ..\cuda_detector.py > cuda_version.txt
set /p CUDA_VERSION=<cuda_version.txt
del cuda_version.txt
echo Detected CUDA Version: !CUDA_VERSION!

rem Create site-packages directory if it doesn't exist
if not exist "site-packages" mkdir site-packages

rem Set PYTHONPATH environment variable
set PYTHONPATH=%~dp0site-packages

rem Install base dependencies excluding whisper and torch first
echo Installing base dependencies...
python\Scripts\pip.exe install --target=site-packages PyQt6 PyQt6-Qt6 PyQt6-sip numpy>=1.24.0 librosa>=0.10.0 soundfile>=0.12.1 --no-warn-script-location

rem Install openai-whisper directly, not from requirements
echo Installing openai-whisper...
python\Scripts\pip.exe install --target=site-packages openai-whisper --no-warn-script-location
if %ERRORLEVEL% NEQ 0 (
    echo First attempt failed, trying with specific version...
    python\Scripts\pip.exe install --target=site-packages git+https://github.com/openai/whisper.git@v20231117
    if %ERRORLEVEL% NEQ 0 (
        echo Direct install also failed, trying alternative methods...
        python\Scripts\pip.exe install --target=site-packages git+https://github.com/openai/whisper.git
    )
)

rem PyTorch installation based on detected CUDA version
if "!CUDA_VERSION!"=="12.6" (
    echo CUDA 12.6 detected, installing compatible PyTorch...
    python\Scripts\pip.exe install --target=site-packages --extra-index-url https://download.pytorch.org/whl/cu126 torch==2.6.0+cu126 --no-warn-script-location
) else if "!CUDA_VERSION!"=="12.4" (
    echo CUDA 12.4 detected, installing compatible PyTorch...
    python\Scripts\pip.exe install --target=site-packages --extra-index-url https://download.pytorch.org/whl/cu124 torch==2.6.0+cu124 --no-warn-script-location
) else if "!CUDA_VERSION!"=="11.8" (
    echo CUDA 11.8 detected, installing compatible PyTorch...
    python\Scripts\pip.exe install --target=site-packages --extra-index-url https://download.pytorch.org/whl/cu118 torch==2.6.0+cu118 --no-warn-script-location
) else (
    echo No compatible CUDA version detected, installing CPU-only PyTorch...
    python\Scripts\pip.exe install --target=site-packages torch --no-warn-script-location
)

rem Verify installation
echo Verifying installation...
python\python.exe -c "import sys; print('Python paths:', sys.path); try: import torch; print(f'PyTorch: {torch.__version__}'); except ImportError: print('PyTorch not found!'); try: import whisper; print(f'Whisper: {whisper.__version__}'); except ImportError: print('Whisper not found!')"

echo Dependencies installed successfully
pause
