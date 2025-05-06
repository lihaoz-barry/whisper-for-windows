#!/usr/bin/env python3
import os
import sys
import shutil
import subprocess
from pathlib import Path

# The Python version used in embedded distributions
EMBEDDED_PYTHON_VERSION = "3.12.7"
ARCHITECTURES = ["amd64", "arm64", "win32"]

def check_prerequisites():
    """
    Check if embedded Python distributions are extracted and ready.
    """
    python_embedded_dir = Path("python_embedded")
    
    if not python_embedded_dir.exists():
        print("ERROR: Embedded Python distributions not found!")
        print("Please run setup_embedded_python.py first to extract the embedded Python distributions.")
        sys.exit(1)
    
    # Check if at least amd64 architecture is available (required for building)
    if not (python_embedded_dir / "amd64").exists():
        print("ERROR: amd64 embedded Python distribution not found!")
        print("Please ensure you have extracted at least the amd64 Python distribution.")
        sys.exit(1)
        
    print(f"Using embedded Python {EMBEDDED_PYTHON_VERSION} distributions ✓")

def prepare_for_inno_setup(arch):
    """
    Prepares the files needed for Inno Setup to create an installer for the given architecture.
    """
    print(f"Preparing files for {arch} architecture Inno Setup installer...")
    
    # Create a staging directory for the installer
    staging_dir = Path(f"dist/staging_{arch}")
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
    
    # Copy the CUDA detector script to the staging directory
    shutil.copy("cuda_detector.py", staging_dir / "cuda_detector.py")
    
    # Copy FFmpeg executable if it exists
    ffmpeg_src = Path("ffmpeg_bin/ffmpeg.exe")
    if ffmpeg_src.exists():
        ffmpeg_dest_dir = staging_dir / "bin"
        ffmpeg_dest_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy(ffmpeg_src, ffmpeg_dest_dir / "ffmpeg.exe")
        print(f"Copied ffmpeg.exe to {ffmpeg_dest_dir}")
    else:
        print(f"WARNING: ffmpeg.exe not found at {ffmpeg_src}. Audio loading might fail for some formats.")

    # Copy the embedded Python distribution for this architecture
    python_embedded_src = Path("python_embedded") / arch
    python_embedded_dest = staging_dir / "python"
    
    if python_embedded_src.exists():
        shutil.copytree(python_embedded_src, python_embedded_dest)
    else:
        print(f"WARNING: Embedded Python for {arch} not found at {python_embedded_src}")
        print("The installer will be built without embedded Python.")
    
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
    
    # Create a batch file to initialize embedded Python
    with open(staging_dir / "setup_embedded_python.bat", "w", encoding="utf-8") as f:
        f.write('@echo off\n')
        f.write('echo Setting up embedded Python environment...\n')
        
        # Run get-pip.py to install pip
        f.write('cd "%~dp0\\python"\n')  # Change to python directory
        f.write('echo Installing pip...\n')
        f.write('python get-pip.py\n')
        f.write('if %ERRORLEVEL% NEQ 0 (\n')
        f.write('    echo Failed to install pip. Please check the error message above.\n')
        f.write('    pause\n')
        f.write('    exit /b 1\n')
        f.write(')\n')
        f.write('echo Pip installed successfully.\n')
        
        # Install setuptools and wheel
        f.write('echo Installing setuptools and wheel...\n')
        f.write('Scripts\\pip.exe install --upgrade setuptools wheel\n')
        f.write('if %ERRORLEVEL% NEQ 0 (\n')
        f.write('    echo Failed to install setuptools/wheel. Please check the error message above.\n')
        f.write('    pause\n')
        f.write('    exit /b 1\n')
        f.write(')\n')
        f.write('echo Setuptools and wheel installed successfully.\n')
        
        f.write('cd "%~dp0"\n')  # Go back to app directory
        f.write('echo Setup complete!\n')
        f.write('pause\n')
    
    # Create a batch file to run the application
    with open(staging_dir / "Run Whisper Transcriber.bat", "w", encoding="utf-8") as f:
        f.write('@echo off\n')
        f.write('setlocal enabledelayedexpansion\n')
        f.write('echo Starting Whisper Transcriber...\n')
        f.write('cd "%~dp0"\n')
        f.write('\n')
        f.write(':: Always add the bin directory to PATH (contains ffmpeg if bundled)\n')
        f.write('set PATH=%~dp0bin;%PATH%\n')
        f.write('\n')
        f.write('if not exist "python\\python.exe" (\n')
        f.write('    echo ERROR: Embedded Python not found!\n')
        f.write('    echo Please reinstall the application.\n')
        f.write('    pause\n')
        f.write('    exit /b 1\n')
        f.write(')\n')
        f.write('if not exist "python\\Scripts\\pip.exe" (\n')
        f.write('    echo Setting up embedded Python for first use...\n')
        f.write('    call setup_embedded_python.bat\n')
        f.write(')\n')
        f.write('if not exist site-packages (\n')
        f.write('    echo Installing required packages for first use...\n')
        f.write('    md site-packages\n')
        f.write(')\n')
        f.write('echo ================================================\n')
        f.write('echo CUDA Detection & PyTorch Installation\n')
        f.write('echo ================================================\n')
        f.write('echo Checking for CUDA-capable GPU...\n')
        f.write('python\\python.exe cuda_detector.py > cuda_version.txt\n')
        f.write('set /p CUDA_VERSION=<cuda_version.txt\n')
        f.write('echo Raw output from cuda_detector.py:\n')
        f.write('type cuda_version.txt\n')
        f.write('del cuda_version.txt\n')
        f.write('echo After set /p command, CUDA_VERSION=!CUDA_VERSION!\n')
        f.write('if "!CUDA_VERSION!"=="COMMAND_FAILED" (\n')
        f.write('    echo nvidia-smi command failed, using CPU-only PyTorch\n')
        f.write('    set CUDA_VERSION=NONE\n')
        f.write(') else if "!CUDA_VERSION!"=="NOT_FOUND" (\n')
        f.write('    echo CUDA version not found in nvidia-smi output, using CPU-only PyTorch\n')
        f.write('    set CUDA_VERSION=NONE\n')
        f.write(') else (\n')
        f.write('    echo CUDA version detected: !CUDA_VERSION!\n')
        f.write(')\n')
        f.write('echo Detected CUDA Version: !CUDA_VERSION!\n')
        f.write('echo ================================================\n')
        f.write('\n')
        f.write('set PYTHONPATH=%~dp0site-packages\n')
        f.write('echo Installing base dependencies...\n')
        f.write('python\\Scripts\\pip.exe install -r requirements_base.txt\n')
        f.write('echo Installing openai-whisper...\n')
        f.write('python\\Scripts\\pip.exe install  -r requirements_whisper.txt\n')
        f.write('if %ERRORLEVEL% NEQ 0 (\n')
        f.write('    echo Attempting alternative installation method for openai-whisper...\n')
        f.write('    python\\Scripts\\pip.exe install --only-binary=:all: openai-whisper\n')
        f.write(')\n')
        f.write('echo CUDA detected: !CUDA_VERSION! - Determining compatible PyTorch version...\n')
        f.write('REM Parse Major.Minor version\n')
        f.write('for /f "tokens=1,2 delims=." %%a in ("!CUDA_VERSION!") do (\n')
        f.write('    set CUDA_MAJOR=%%a\n')
        f.write('    set CUDA_MINOR=%%b\n')
        f.write(')\n')
        f.write('echo Parsed CUDA Version: Major=!CUDA_MAJOR!, Minor=!CUDA_MINOR!\n')
        f.write('\n')
        f.write('REM Decision Logic: Find the highest compatible PyTorch version <= detected CUDA version\n')
        f.write('REM If detected version is newer than latest supported, use latest supported (cu126)\n')
        f.write('if not defined CUDA_MAJOR (\n')
        f.write('    echo ERROR: Could not parse CUDA version !CUDA_VERSION!. Using CPU PyTorch.\n')
        f.write('    set TORCH_REQ_FILE=requirements_cpu.txt\n')
        f.write(') else if "!CUDA_MAJOR!" == "NONE" (\n')
        f.write('    echo ERROR: Could not parse CUDA version !CUDA_VERSION!. Using CPU PyTorch.\n')
        f.write('    set TORCH_REQ_FILE=requirements_cpu.txt\n')
        f.write(') else if !CUDA_MAJOR! GEQ 13 (\n')
        f.write('    echo CUDA version !CUDA_VERSION! >= 13.0. Using latest supported PyTorch cu126S.\n')
        f.write('    set TORCH_REQ_FILE=requirements_cuda126.txt\n')
        f.write(') else if !CUDA_MAJOR! EQU 12 (\n')
        f.write('    if !CUDA_MINOR! GEQ 6 (\n')
        f.write('        echo CUDA version !CUDA_VERSION! >= 12.6. Using PyTorch cu126.\n')
        f.write('        set TORCH_REQ_FILE=requirements_cuda126.txt\n')
        f.write('    ) else if !CUDA_MINOR! GEQ 4 (\n')
        f.write('        echo CUDA version !CUDA_VERSION! >= 12.4 and < 12.6. Using PyTorch cu124.\n')
        f.write('        set TORCH_REQ_FILE=requirements_cuda124.txt\n')
        f.write('    ) else (\n')
        f.write('        echo CUDA version !CUDA_VERSION! >= 12.0 and < 12.4. Using PyTorch cu118.\n')
        f.write('        set TORCH_REQ_FILE=requirements_cuda118.txt\n')
        f.write('    )\n')
        f.write(') else if !CUDA_MAJOR! EQU 11 (\n')
        f.write('     if !CUDA_MINOR! GEQ 8 (\n')
        f.write('         echo CUDA version !CUDA_VERSION! >= 11.8 and < 12.0. Using PyTorch cu118.\n')
        f.write('         set TORCH_REQ_FILE=requirements_cuda118.txt\n')
        f.write('     ) else (\n')
        f.write('         echo CUDA version !CUDA_VERSION! < 11.8. Using CPU PyTorch.\n')
        f.write('         set TORCH_REQ_FILE=requirements_cpu.txt\n')
        f.write('     )\n')
        f.write(') else (\n')
        f.write('    echo CUDA version !CUDA_VERSION! < 11.8. Using CPU PyTorch.\n')
        f.write('    set TORCH_REQ_FILE=requirements_cpu.txt\n')
        f.write(')\n')
        f.write('\n')
        f.write('echo Selected PyTorch requirements file: !TORCH_REQ_FILE!\n')
        f.write('echo Checking if PyTorch is already installed...\n')
        f.write('python\\Scripts\\pip.exe show torch > nul 2>&1\n')
        f.write('if %ERRORLEVEL% EQU 0 (\n')
        f.write('    echo PyTorch is already installed. Verifying version...\n')
        f.write('    python\\python.exe -c "import torch; print(torch.__version__)" > torch_version.txt 2>&1\n')
        f.write('    set /p INSTALLED_TORCH_VERSION=<torch_version.txt\n')
        f.write('    del torch_version.txt\n')
        f.write('    echo Installed PyTorch version: !INSTALLED_TORCH_VERSION!\n')
        f.write('    for /f "tokens=1,2 delims== " %%a in (\'findstr "torch==" !TORCH_REQ_FILE!\') do set EXPECTED_VERSION=%%b\n')
        f.write('    echo Expected PyTorch version: !EXPECTED_VERSION!\n')
        f.write('    if "!INSTALLED_TORCH_VERSION!" NEQ "!EXPECTED_VERSION!" (\n')
        f.write('        echo PyTorch version mismatch. Uninstalling existing version...\n')
        f.write('        python\\Scripts\\pip.exe uninstall -y torch torch-cpu torch-directml torch-tensorrt torchcsprng torchaudio torchvision torchdata torchtext triton > nul 2>&1\n')
        f.write('    ) else (\n')
        f.write('        echo PyTorch version is correct. Skipping reinstallation.\n')
        f.write('    )\n')
        f.write(') else (\n')
        f.write('    echo PyTorch is not installed. Proceeding with installation...\n')
        f.write(')\n')
        f.write('\n')
        f.write('echo Installing PyTorch from !TORCH_REQ_FILE!...\n')
        f.write('python\\Scripts\\pip.exe install -r !TORCH_REQ_FILE! --no-cache-dir\n')
        f.write('if %ERRORLEVEL% NEQ 0 (\n')
        f.write('    echo ERROR: Failed to install PyTorch from !TORCH_REQ_FILE!. Check logs above.\n')
        f.write('    pause\n')
        f.write('    exit /b 1\n')
        f.write(')\n')
        f.write('echo ================================================\n')
        f.write('set PYTHONPATH=%~dp0site-packages\n')
        f.write('echo Verifying installation...\n')
        f.write('python\\python.exe -c "import sys; print(\'Python paths:\', sys.path); import PyQt6.QtCore; import whisper; print(\'\\nInstallation successful!\'); print(\'\\nInstalled package versions:\'); print(f\'PyQt6: {PyQt6.QtCore.PYQT_VERSION_STR}\'); print(f\'Whisper: {whisper.__version__}\')" || echo ERROR: Dependencies check failed\n')
        f.write('echo Starting Whisper Transcriber application...\n')
        f.write('python\\python.exe src\\run.py\n')
        f.write('if %ERRORLEVEL% NEQ 0 pause\n')
    
    # Create a verify GPU and dependencies script
    with open(staging_dir / "verify_gpu.bat", "w", encoding="utf-8") as f:
        f.write('@echo off\n')
        f.write('setlocal enabledelayedexpansion\n')
        f.write('echo Whisper Transcriber - GPU and Dependencies Verification Tool\n')
        f.write('echo ============================================================\n')
        f.write('cd "%~dp0"\n')
        
        # Set PYTHONPATH for the verification
        f.write('set PYTHONPATH=%~dp0site-packages\n')
        
        f.write('echo Checking for CUDA-capable GPU...\n')
        f.write('python\\python.exe cuda_detector.py > cuda_version.txt\n')
        f.write('set /p CUDA_VERSION=<cuda_version.txt\n')
        f.write('del cuda_version.txt\n')
        
        f.write('echo.\n')
        f.write('echo CUDA Detection Result: !CUDA_VERSION!\n')
        f.write('echo.\n')
        
        f.write('echo Checking PyTorch GPU availability...\n')
        f.write('python\\python.exe -c "import torch; print(f\'PyTorch version: {torch.__version__}\'); print(f\'CUDA available: {torch.cuda.is_available()}\'); print(f\'CUDA version: {torch.version.cuda if torch.cuda.is_available() else \"N/A\"}\'); print(f\'GPU device count: {torch.cuda.device_count()}\'); [print(f\"Device {i}: {torch.cuda.get_device_name(i)}\") for i in range(torch.cuda.device_count())]"\n')
        f.write('echo.\n')
        
        f.write('echo Checking Whisper installation...\n')
        f.write('python\\python.exe -c "import whisper; print(f\'Whisper version: {whisper.__version__}\'); print(\'Available Whisper models:\'); [print(f\"  {m}\") for m in whisper.available_models()]"\n')
        f.write('echo.\n')
        
        f.write('echo If you see any errors above, please run the "Run Whisper Transcriber.bat" script\n')
        f.write('echo to ensure all dependencies are properly installed.\n')
        f.write('echo.\n')
        
        f.write('pause\n')
    
    print(f"Files prepared for {arch} architecture Inno Setup!")
    print(f"Files are in: {staging_dir.absolute()}")

def generate_iss_script(arch):
    """
    Generate a modified Inno Setup script for the given architecture.
    """
    output_filename = f"WhisperTranscriber_Setup_{arch}"
    arch_display = {
        "amd64": "x64",
        "win32": "x86",
        "arm64": "ARM64"
    }.get(arch, arch)
    
    iss_file = f"installer_{arch}.iss"
    print(f"Generating Inno Setup script for {arch} architecture: {iss_file}")
    
    with open(iss_file, "w") as f:
        f.write(f'''#define MyAppName "Whisper Transcriber"
#define MyAppVersion "1.0.1"
#define MyAppPublisher "Whisper for Windows Team"
#define MyAppURL "https://github.com/yourusername/whisper-for-windows"
#define MyAppExeName "Run Whisper Transcriber.bat"
#define MyAppArchitecture "{arch_display}"

[Setup]
AppId={{{{738D9A98-D71E-4748-AD2D-D7125D97835B}}}}
AppName={{#MyAppName}} ({arch_display})
AppVersion={{#MyAppVersion}}
AppPublisher={{#MyAppPublisher}}
AppPublisherURL={{#MyAppURL}}
AppSupportURL={{#MyAppURL}}
AppUpdatesURL={{#MyAppURL}}
DefaultDirName={{autopf}}\\{{#MyAppName}} ({arch_display})
DisableProgramGroupPage=no
LicenseFile=LICENSE
OutputDir=release
OutputBaseFilename={output_filename}
Compression=lzma
SolidCompression=yes
WizardStyle=modern
; Comment out the icon if you don't have one yet
; SetupIconFile=resources\\app_icon.ico
PrivilegesRequired=lowest
''')

        # Add architecture specific settings
        if arch == "amd64":
            f.write('''ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64
''')
        elif arch == "win32":
            f.write('''ArchitecturesAllowed=x86 x64
''')
        elif arch == "arm64":
            f.write('''ArchitecturesAllowed=arm64
ArchitecturesInstallIn64BitMode=arm64
''')

        # Continue with the rest of the script
        f.write('''
[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "startmenuicon"; Description: "Create Start Menu shortcut"; GroupDescription: "{cm:AdditionalIcons}"; Flags: checkedonce

[Files]
; Source files - from the staging directory
''')
        f.write(f'Source: "dist\\staging_{arch}\\*"; DestDir: "{{app}}"; Flags: ignoreversion recursesubdirs createallsubdirs\n')
        f.write('Source: "LICENSE"; DestDir: "{app}"; Flags: ignoreversion\n')

        # Add icons and run section
        f.write('''
[Icons]
Name: "{group}\\{#MyAppName}"; Filename: "{app}\\{#MyAppExeName}"
Name: "{group}\\Verify GPU Capabilities"; Filename: "{app}\\verify_gpu.bat"
Name: "{group}\\Uninstall {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\\{#MyAppName}"; Filename: "{app}\\{#MyAppExeName}"; Tasks: desktopicon

[Run]
; Option to run the application after installation
Filename: "{app}\\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
''')
    
    print(f"Inno Setup script generated: {iss_file}")
    return iss_file

def create_gitignore():
    """
    Create or update .gitignore file to ignore generated files
    """
    gitignore_content = """
# Generated directories
__pycache__/
*.py[cod]
*$py.class
python_embedded/
dist/
build/
release/
site-packages/

# Embedded Python runtime
python_embedded/
python/

# Log files
*.log

# Generated ISS files
installer_*.iss
"""
    
    gitignore_path = Path(".gitignore")
    
    # If .gitignore exists, append our content if not already present
    if gitignore_path.exists():
        with open(gitignore_path, 'r') as f:
            current_content = f.read()
            
        if "python_embedded/" not in current_content:
            with open(gitignore_path, 'a') as f:
                f.write(gitignore_content)
    else:
        # Create new .gitignore file
        with open(gitignore_path, 'w') as f:
            f.write(gitignore_content)
            
    print("Updated .gitignore file")

def main():
    """
    Main function to build installers for all architectures
    """
    # Check embedded Python is ready
    check_prerequisites()
    
    # Create/update .gitignore
    create_gitignore()
    
    # Process each architecture
    for arch in ARCHITECTURES:
        print(f"\n=== Processing {arch} architecture ===")
        prepare_for_inno_setup(arch)
        iss_file = generate_iss_script(arch)
        
        # Optionally compile the ISS files here if Inno Setup is installed
        # For now, just print instructions
        print(f"To build the {arch} installer, run:")
        print(f"iscc {iss_file}")
    
    print("\nAll architectures prepared! To build all installers:")
    for arch in ARCHITECTURES:
        print(f"iscc installer_{arch}.iss")

if __name__ == "__main__":
    main()