import os
import sys
import shutil
import subprocess
from pathlib import Path
import importlib.util
import site

def build_executable(reduce_size=True, use_spec=True):
    print("Starting build process for Whisper Transcriber...")
    
    # Check if PyInstaller is installed
    try:
        import PyInstaller
    except ImportError:
        print("PyInstaller not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "PyInstaller"])
    
    # Find the whisper package and its assets directory
    try:
        import whisper
        whisper_dir = os.path.dirname(whisper.__file__)
        whisper_assets = os.path.join(whisper_dir, "assets")
        print(f"Found whisper assets directory at: {whisper_assets}")
    except ImportError:
        print("Error: Whisper package not found. Please install it first.")
        return
    
    # Create resource directories if they don't exist
    resources_dir = Path("resources")
    if not resources_dir.exists():
        resources_dir.mkdir()
    
    # Build the executable
    print("Building executable with PyInstaller...")
    
    if use_spec:
        # Use the existing spec file which has been optimized
        print("Using existing spec file...")
        cmd = ["pyinstaller", "--clean", "Whisper Transcriber.spec"]
        
    else:
        # Base command with common options
        cmd = [
            "pyinstaller",
            "--name", "Whisper Transcriber",
            "--windowed",  # No console window
            "--clean",     # Clean cache before building
        ]
        
        # Add whisper assets data
        cmd.extend([
            "--add-data", f"{whisper_assets};whisper/assets",
        ])
        
        if reduce_size:
            print("Building with size optimizations...")
            # Use directory mode instead of onefile to reduce size
            # Add exclusions for large packages that can be trimmed
            cmd.extend([
                # Use directory mode instead of onefile
                "--noconfirm",
                # Exclude unnecessary CUDA components
                "--exclude-module", "torch.distributed",
                # Exclude test modules
                "--exclude-module", "pytest",
                "--exclude-module", "unittest",
                # Exclude unnecessary deep learning components
                "--exclude-module", "torchvision",
                "--exclude-module", "torchaudio.datasets",
                # Add data
                "--add-data", "resources;resources",
            ])
        else:
            print("Building standard onefile executable...")
            cmd.extend([
                "--onefile",   # Single executable file
                "--add-data", "resources;resources",
            ])
            
        # Main script to execute
        cmd.append("src/run.py")
    
    print(f"Running command: {' '.join(cmd)}")
    subprocess.check_call(cmd)
    
    print("\nBuild completed!")
    if not use_spec or reduce_size:
        print("Executable components can be found in the 'dist/Whisper Transcriber' folder")
    else:
        print("Executable can be found in the 'dist' folder")

if __name__ == "__main__":
    # Parse command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "--standard":
            build_executable(reduce_size=False, use_spec=False)
        elif sys.argv[1] == "--spec":
            build_executable(use_spec=True)
        else:
            print(f"Unknown option: {sys.argv[1]}")
            print("Available options:")
            print("  --standard: Build full-size single executable")
            print("  --spec: Use optimized spec file (recommended)")
    else:
        # Default to using spec file (recommended)
        build_executable(use_spec=True)