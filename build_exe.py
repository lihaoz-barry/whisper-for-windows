import os
import sys
import shutil
import subprocess
from pathlib import Path

REQUIRED_PYTHON_VERSION = "3.12.7"
PYTHON_DOWNLOAD_URL = f"https://www.python.org/ftp/python/{REQUIRED_PYTHON_VERSION}/python-{REQUIRED_PYTHON_VERSION}-amd64.exe"

def check_python_version():
    """
    Checks if the correct Python version is installed and being used.
    """
    current_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    
    if current_version != REQUIRED_PYTHON_VERSION:
        print(f"ERROR: This installer requires Python {REQUIRED_PYTHON_VERSION}")
        print(f"Current Python version: {current_version}")
        print(f"\nPlease download and install Python {REQUIRED_PYTHON_VERSION} from:")
        print(f"{PYTHON_DOWNLOAD_URL}")
        print("\nMake sure to check 'Add Python to PATH' during installation.")
        
        # Ask if the user wants to open the download page
        response = input("\nWould you like to open the download page now? (y/n): ")
        if response.lower().startswith('y'):
            # Open the download URL in the default browser
            import webbrowser
            webbrowser.open(PYTHON_DOWNLOAD_URL)
            
        sys.exit(1)
    else:
        print(f"Using Python {current_version} ✓")

def prepare_for_inno_setup():
    """
    Prepares the files needed for Inno Setup to create an installer.
    Instead of compiling an executable, this organizes the source files
    and creates necessary scripts for the final installation.
    """
    print("Preparing files for Inno Setup installer...")
    
    # Create a staging directory for the installer
    staging_dir = Path("dist/staging")
    if staging_dir.exists():
        shutil.rmtree(staging_dir)
    staging_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy the source code
    src_dest = staging_dir / "src"
    shutil.copytree("src", src_dest)
    
    # Copy resources directory if it exists
    resources_dir = Path("resources")
    if resources_dir.exists():
        shutil.copytree(resources_dir, staging_dir / "resources")
    
    # Copy LICENSE file
    shutil.copy("LICENSE", staging_dir / "LICENSE")
    
    # Create a base requirements.txt in the staging directory without openai-whisper and torch
    with open(staging_dir / "requirements_base.txt", "w") as f:
        f.write("--only-binary=:all: PyQt6 PyQt6-Qt6 PyQt6-sip\n")  # Force binary installs to avoid compilation
        f.write("PyQt6\n")  # No version specified, will install the latest
        f.write("PyQt6-Qt6\n")
        f.write("PyQt6-sip\n")
        f.write("numpy>=1.24.0\n")
        f.write("librosa>=0.10.0\n")
        f.write("soundfile>=0.12.1\n")
    
    # Create a separate file for openai-whisper requirements
    with open(staging_dir / "requirements_whisper.txt", "w") as f:
        f.write("openai-whisper==20231117\n")  # Use the latest version available
    
    # Create a version of requirements.txt with CPU-only PyTorch
    with open(staging_dir / "requirements_cpu.txt", "w") as f:
        f.write("--only-binary=:all: torch\n")  # Force binary installs to avoid compilation
        f.write("torch\n")  # No version specified, will install the latest CPU version
    
    # Create versions of requirements for different CUDA versions
    cuda_versions = {
        "11.8": "cu118",
        "12.4": "cu124",
        "12.6": "cu126"
    }
    
    for cuda_ver, cuda_tag in cuda_versions.items():
        with open(staging_dir / f"requirements_cuda{cuda_ver.replace('.', '')}.txt", "w") as f:
            f.write("--only-binary=:all: torch\n")  # Force binary installs to avoid compilation
            f.write(f"--extra-index-url https://download.pytorch.org/whl/{cuda_tag}\n")
            f.write(f"torch==2.6.0+{cuda_tag}\n")  # Specify exact PyTorch version with CUDA tag
    
    # Create a prerequisites check batch file
    with open(staging_dir / "check_prerequisites.bat", "w", encoding="utf-8") as f:
        f.write('@echo off\n')
        f.write('echo Checking prerequisites for sWhisper Transcriber installation...\n')
        f.write('echo.\n')
        
        # Check for specific Python version
        f.write(f'echo Checking for Python {REQUIRED_PYTHON_VERSION}...\n')
        f.write('python --version > python_version.txt 2>&1\n')
        f.write('findstr /C:"Python '+REQUIRED_PYTHON_VERSION+'" python_version.txt > nul\n')
        f.write('if %ERRORLEVEL% NEQ 0 (\n')
        f.write(f'    echo Python {REQUIRED_PYTHON_VERSION} is required but not detected.\n')
        f.write('    echo The version installed or in PATH might be different.\n')
        f.write('    echo.\n')
        f.write(f'    echo Please download and install Python {REQUIRED_PYTHON_VERSION} from:\n')
        f.write(f'    echo {PYTHON_DOWNLOAD_URL}\n')
        f.write('    echo.\n')
        f.write('    echo Make sure to check "Add Python to PATH" during installation.\n')
        f.write('    choice /C YN /M "Would you like to open the download page now?"\n')
        f.write('    if errorlevel 2 goto :python_check_done\n')
        f.write(f'    start "" "{PYTHON_DOWNLOAD_URL}"\n')
        f.write('    echo Please run the installer, then restart this application.\n')
        f.write('    pause\n')
        f.write('    exit /b 1\n')
        f.write(')\n')
        f.write(':python_check_done\n')
        f.write('del python_version.txt\n')
        f.write('echo.\n')
        
        # Check for Visual C++ redistributable
        f.write('echo Checking for Microsoft Visual C++ Redistributable...\n')
        f.write('reg query "HKLM\\SOFTWARE\\Microsoft\\VisualStudio\\14.0" >nul 2>&1\n')
        f.write('if %ERRORLEVEL% NEQ 0 (\n')
        f.write('    echo Microsoft Visual C++ Redistributable is not installed.\n')
        f.write('    echo This is required for some Python packages to work correctly.\n')
        f.write('    echo.\n')
        f.write('    echo Please download and install the Microsoft Visual C++ Redistributable:\n')
        f.write('    echo https://aka.ms/vs/17/release/vc_redist.x64.exe\n')
        f.write('    echo.\n')
        f.write('    choice /C YN /M "Would you like to open the download page now?"\n')
        f.write('    if errorlevel 2 goto :continue\n')
        f.write('    start "" "https://aka.ms/vs/17/release/vc_redist.x64.exe"\n')
        f.write('    echo Please run the installer, then return to this window and press any key to continue.\n')
        f.write('    pause\n')
        f.write(')\n')
        f.write(':continue\n')
        f.write('echo.\n')
        f.write('echo All prerequisites checked.\n')
        f.write('echo You can now run "Run Whisper Transcriber.bat" to start the application.\n')
        f.write('echo.\n')
        f.write('pause\n')
    
    # Create a batch file to run the application
    with open(staging_dir / "Run Whisper Transcriber.bat", "w", encoding="utf-8") as f:
        f.write('@echo off\n')
        f.write('echo Starting Whisper Transcriber...\n')
        f.write('cd "%~dp0"\n')  # Change to the directory of the batch file
        
        # Check for specific Python version
        f.write(f'echo Checking for Python {REQUIRED_PYTHON_VERSION}...\n')
        f.write('python --version > python_version.txt 2>&1\n')
        f.write('findstr /C:"Python '+REQUIRED_PYTHON_VERSION+'" python_version.txt > nul\n')
        f.write('if %ERRORLEVEL% NEQ 0 (\n')
        f.write(f'    echo Python {REQUIRED_PYTHON_VERSION} is required but not detected.\n')
        f.write('    echo The version installed or in PATH might be different.\n')
        f.write('    echo.\n')
        f.write(f'    echo Please download and install Python {REQUIRED_PYTHON_VERSION} from:\n')
        f.write(f'    echo {PYTHON_DOWNLOAD_URL}\n')
        f.write('    echo.\n')
        f.write('    echo Make sure to check "Add Python to PATH" during installation.\n')
        f.write('    choice /C YN /M "Would you like to open the download page now?"\n')
        f.write('    if errorlevel 2 goto :python_check_exit\n')
        f.write(f'    start "" "{PYTHON_DOWNLOAD_URL}"\n')
        f.write('    echo Please run the installer, then restart this application.\n')
        f.write('    pause\n')
        f.write('    exit /b 1\n')
        f.write(':python_check_exit\n')
        f.write('    exit /b 1\n')
        f.write(')\n')
        f.write('del python_version.txt\n')
        
        # Check if a virtual env already exists, if not create one
        f.write('if not exist venv (\n')
        f.write('    echo Setting up virtual environment for first use...\n')
        f.write(f'    python -m venv venv\n')
        
        # Upgrade pip to latest version
        f.write('    echo Upgrading pip to latest version...\n')
        f.write('    venv\\Scripts\\python -m pip install --upgrade pip\n')
        
        # Install base requirements first
        f.write('    echo Installing base dependencies...\n')
        f.write('    venv\\Scripts\\pip install -r requirements_base.txt\n')
        
        # Install openai-whisper with multiple fallback methods
        f.write('    echo Installing openai-whisper...\n')
        f.write('    venv\\Scripts\\pip install -r requirements_whisper.txt\n')
        f.write('    if %ERRORLEVEL% NEQ 0 (\n')
        f.write('        echo Attempting alternative installation method for openai-whisper...\n')
        f.write('        venv\\Scripts\\pip install --only-binary=:all: openai-whisper\n')
        f.write('    )\n')
        
        # CUDA detection and appropriate PyTorch installation
        f.write('    echo Checking for CUDA installation...\n')
        f.write('    venv\\Scripts\\python -c "import subprocess; import re; import sys; result = subprocess.run([\'nvcc\', \'--version\'], capture_output=True, text=True, shell=True); cuda_ver = re.search(r\'release (\\d+\\.\\d+)\', result.stdout); print(cuda_ver.group(1) if cuda_ver else \'NONE\'); sys.exit(0 if cuda_ver else 1)" > cuda_version.txt 2>nul\n')
        f.write('    set /p CUDA_VERSION=<cuda_version.txt\n')
        # f.write('    del cuda_version.txt\n')
                
        # Display the detected CUDA version explicitly
        f.write('    echo Detected CUDA Version: %CUDA_VERSION%\n')

        # Install PyTorch based on detected CUDA version
        f.write('    if "%CUDA_VERSION%"=="11.8" (\n')
        f.write('        echo CUDA 11.8 detected, installing compatible PyTorch...\n')
        f.write('        venv\\Scripts\\pip install -r requirements_cuda118.txt\n')
        f.write('    ) else if "%CUDA_VERSION%"=="12.1" (\n')
        f.write('        echo CUDA 12.4 detected, installing compatible PyTorch...\n')
        f.write('        venv\\Scripts\\pip install -r requirements_cuda124.txt\n')
        f.write('    ) else if "%CUDA_VERSION%"=="12.2" (\n')
        f.write('        echo CUDA 12.6 detected, installing compatible PyTorch...\n')
        f.write('        venv\\Scripts\\pip install -r requirements_cuda126.txt\n')
        f.write('    ) else (\n')
        f.write('        echo No compatible CUDA version detected, installing CPU-only PyTorch...\n')
        f.write('        venv\\Scripts\\pip install -r requirements_cpu.txt\n')
        f.write('    )\n')
        
        f.write(')\n')
        
        # Verify the installation was successful and show installed versions
        f.write('echo Verifying installation...\n')
        f.write('venv\\Scripts\\python -c "import PyQt6; import whisper; print(\'\\nInstallation successful!\'); print(\'\\nInstalled package versions:\'); print(f\'PyQt6: {PyQt6.__version__}\'); print(f\'Whisper: {whisper.__version__}\')" || echo ERROR: Dependencies check failed\n')
        
        # Run the application
        f.write('echo Starting Whisper Transcriber application...\n')
        f.write('venv\\Scripts\\python src\\run.py\n')
        f.write('if %ERRORLEVEL% NEQ 0 pause\n')  # Pause if there's an error
    
    print("Files prepared for Inno Setup!")
    print(f"Files are in: {staging_dir.absolute()}")
    print("Now you can run Inno Setup to build the installer using the installer.iss script.")

if __name__ == "__main__":
    # Check if the correct Python version is being used
    check_python_version()
    prepare_for_inno_setup()