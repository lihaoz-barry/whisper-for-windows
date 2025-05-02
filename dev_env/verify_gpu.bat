@echo off
setlocal enabledelayedexpansion
cd "%~dp0"
echo Whisper Transcriber - Development GPU Verification
echo ==============================================
set PYTHONPATH=%~dp0site-packages

echo Checking for CUDA-capable GPU...
python\python.exe ..\cuda_detector.py
echo.

echo Checking Python path and environment...
python\python.exe -c "import sys; print('Python executable:', sys.executable); print('Python version:', sys.version); print('Python paths:'); [print(f'  {p}') for p in sys.path]"
echo.

echo Checking PyTorch GPU support...
python\python.exe -c "import sys; print('Checking for PyTorch...'); try: import torch; print(f'PyTorch version: {torch.__version__}'); print(f'CUDA available: {torch.cuda.is_available()}'); print(f'CUDA version: {torch.version.cuda if torch.cuda.is_available() else \"N/A\"}'); print(f'GPU device count: {torch.cuda.device_count()}'); [print(f\"Device {i}: {torch.cuda.get_device_name(i)}\") for i in range(torch.cuda.device_count())] except ImportError as e: print(f'Error loading PyTorch: {e}')"
echo.

echo Checking whisper installation...
python\python.exe -c "import sys; print('Checking for Whisper...'); try: import whisper; print(f'Whisper version: {whisper.__version__}'); print('Available models:'); [print(f'  {m}') for m in whisper.available_models()] except ImportError as e: print(f'Error loading Whisper: {e}')"
echo.

pause
