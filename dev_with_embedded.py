#!/usr/bin/env python3
import os
import sys
import shutil
import subprocess
from pathlib import Path
import platform

def setup_dev_environment():
    """
    Set up a development environment using embedded Python
    """
    # Determine the architecture of the current system
    if platform.machine().endswith('64'):
        if platform.machine().startswith('ARM'):
            arch = "arm64"
        else:
            arch = "amd64"
    else:
        arch = "win32"
    
    print(f"Detected system architecture: {arch}")
    
    # Check if embedded Python distributions are extracted
    python_embedded_dir = Path("python_embedded")
    if not python_embedded_dir.exists() or not (python_embedded_dir / arch).exists():
        print("Embedded Python distribution not found or not extracted for your architecture.")
        print("Please run setup_embedded_python.py first.")
        sys.exit(1)
    
    # Create a development environment dir
    dev_dir = Path("dev_env")
    if dev_dir.exists():
        choice = input(f"{dev_dir} already exists. Do you want to recreate it? (y/n): ")
        if choice.lower() == 'y':
            print(f"Removing existing {dev_dir}...")
            shutil.rmtree(dev_dir)
        else:
            print("Using existing development environment.")
            return
    
    # Create dev_env directory
    dev_dir.mkdir(exist_ok=True)
    
    # Copy the embedded Python
    print(f"Copying embedded Python ({arch}) to {dev_dir}...")
    shutil.copytree(python_embedded_dir / arch, dev_dir / "python")
    
    # Create a site-packages directory
    site_packages_dir = dev_dir / "site-packages"
    site_packages_dir.mkdir(exist_ok=True)
    
    # Create a batch file to install pip in the embedded Python
    install_pip_bat = dev_dir / "install_pip.bat"
    with open(install_pip_bat, 'w') as f:
        f.write('@echo off\n')
        f.write('cd "%~dp0\\python"\n')  # Use correct path with quotes
        f.write('echo Running get-pip.py from the current directory...\n')
        f.write('python.exe get-pip.py\n')  # Use python.exe explicitly
        f.write('if %ERRORLEVEL% NEQ 0 (\n')
        f.write('    echo Failed to install pip\n')
        f.write('    pause\n')
        f.write('    exit /b 1\n')
        f.write(')\n')
        f.write('cd ..\n')
        f.write('echo Pip installed successfully\n')
    
    # Run the batch file
    print("Installing pip in embedded Python...")
    subprocess.run([str(install_pip_bat)], shell=True)
    
    # Create a batch file to install dependencies
    install_deps_bat = dev_dir / "install_deps.bat"
    with open(install_deps_bat, 'w') as f:
        f.write('@echo off\n')
        f.write('setlocal enabledelayedexpansion\n')
        f.write('cd "%~dp0"\n')  # Ensure we're in the right directory
        f.write('echo Installing dependencies for development...\n')
        
        # Check if pip is installed, if not install it
        f.write('if not exist "python\\Scripts\\pip.exe" (\n')
        f.write('    echo Pip not found, installing it first...\n')
        f.write('    call install_pip.bat\n')
        f.write(')\n')
        
        # Check CUDA capability
        f.write('echo Checking for CUDA-capable GPU...\n')
        f.write('python\\python.exe ..\\cuda_detector.py > cuda_version.txt\n')
        f.write('set /p CUDA_VERSION=<cuda_version.txt\n')
        f.write('del cuda_version.txt\n')
        
        # Install base dependencies from requirements.txt
        f.write('echo Installing base dependencies...\n')
        f.write('python\\Scripts\\pip.exe install --target=site-packages -r ..\\requirements.txt\n')
        
        # PyTorch installation based on CUDA version
        f.write('if "!CUDA_VERSION!"=="12.6" (\n')
        f.write('    echo CUDA 12.6 detected, installing compatible PyTorch...\n')
        f.write('    python\\Scripts\\pip.exe install --target=site-packages --extra-index-url https://download.pytorch.org/whl/cu126 torch==2.6.0+cu126\n')
        f.write(') else if "!CUDA_VERSION!"=="12.4" (\n')
        f.write('    echo CUDA 12.4 detected, installing compatible PyTorch...\n')
        f.write('    python\\Scripts\\pip.exe install --target=site-packages --extra-index-url https://download.pytorch.org/whl/cu124 torch==2.6.0+cu124\n')
        f.write(') else if "!CUDA_VERSION!"=="11.8" (\n')
        f.write('    echo CUDA 11.8 detected, installing compatible PyTorch...\n')
        f.write('    python\\Scripts\\pip.exe install --target=site-packages --extra-index-url https://download.pytorch.org/whl/cu118 torch==2.6.0+cu118\n')
        f.write(') else (\n')
        f.write('    echo No compatible CUDA version detected, installing CPU-only PyTorch...\n')
        f.write('    python\\Scripts\\pip.exe install --target=site-packages torch\n')
        f.write(')\n')
        
        f.write('echo Dependencies installed successfully\n')
        f.write('pause\n')
    
    # Create a batch file to run the application with embedded Python
    run_app_bat = dev_dir / "run_app.bat"
    with open(run_app_bat, 'w') as f:
        f.write('@echo off\n')
        f.write('setlocal enabledelayedexpansion\n')
        f.write('cd "%~dp0"\n')
        f.write('echo Running Whisper Transcriber with embedded Python...\n')
        f.write('set PYTHONPATH=%~dp0site-packages\n')
        f.write('python\\python.exe ..\\src\\run.py\n')
        f.write('if %ERRORLEVEL% NEQ 0 pause\n')
    
    # Create a batch file to verify GPU capabilities
    verify_gpu_bat = dev_dir / "verify_gpu.bat"
    with open(verify_gpu_bat, 'w') as f:
        f.write('@echo off\n')
        f.write('setlocal enabledelayedexpansion\n')
        f.write('cd "%~dp0"\n')
        f.write('echo Whisper Transcriber - Development GPU Verification\n')
        f.write('echo ==============================================\n')
        f.write('set PYTHONPATH=%~dp0site-packages\n')
        
        f.write('echo Checking for CUDA-capable GPU...\n')
        f.write('python\\python.exe ..\\cuda_detector.py\n')
        f.write('echo.\n')
        
        f.write('echo Checking PyTorch GPU support...\n')
        f.write('python\\python.exe -c "import torch; print(f\'PyTorch version: {torch.__version__}\'); print(f\'CUDA available: {torch.cuda.is_available()}\'); print(f\'CUDA version: {torch.version.cuda if torch.cuda.is_available() else \"N/A\"}\'); print(f\'GPU device count: {torch.cuda.device_count()}\'); [print(f\"Device {i}: {torch.cuda.get_device_name(i)}\") for i in range(torch.cuda.device_count())]"\n')
        f.write('echo.\n')
        
        f.write('echo Checking whisper installation...\n')
        f.write('python\\python.exe -c "import whisper; print(f\'Whisper version: {whisper.__version__}\'); print(\'Available models: \', whisper.available_models())"\n')
        f.write('echo.\n')
        
        f.write('pause\n')
    
    print("\nDevelopment environment set up successfully!")
    print("\nTo use the development environment:")
    print(f"1. First run: {dev_dir / 'install_deps.bat'} to install dependencies")
    print(f"2. Run the app: {dev_dir / 'run_app.bat'}")
    print(f"3. Verify GPU: {dev_dir / 'verify_gpu.bat'}")
    print("\nThis setup uses the embedded Python for development, providing")
    print("the same environment that end users will experience.")

if __name__ == "__main__":
    setup_dev_environment()