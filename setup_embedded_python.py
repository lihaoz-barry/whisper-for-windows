#!/usr/bin/env python3
import os
import zipfile
import shutil
import subprocess
import urllib.request
from pathlib import Path

# Define the architectures we support
ARCHITECTURES = {
    "amd64": "64-bit (AMD64)",
    "arm64": "ARM64",
    "win32": "32-bit (x86)"
}

# URL for get-pip.py
GET_PIP_URL = "https://bootstrap.pypa.io/get-pip.py"

def download_get_pip():
    """Download get-pip.py from the official source"""
    get_pip_path = Path("get-pip.py")
    
    if not get_pip_path.exists():
        print(f"Downloading get-pip.py from {GET_PIP_URL}...")
        urllib.request.urlretrieve(GET_PIP_URL, get_pip_path)
        print("Download complete!")
    else:
        print("Using existing get-pip.py")
    
    return get_pip_path

def extract_embedded_python():
    """Extract the embedded Python distributions to appropriately named folders"""
    
    base_dir = Path("python_embed")
    extract_dir = Path("python_embedded")
    
    print("Setting up embedded Python environments...")
    
    # Download get-pip.py for later use
    get_pip_path = download_get_pip()
    
    # Create the extraction directory if it doesn't exist
    if not extract_dir.exists():
        extract_dir.mkdir(parents=True)
    
    # Process each architecture
    for arch, arch_name in ARCHITECTURES.items():
        zip_file = base_dir / f"python-3.12.7-embed-{arch}.zip"
        target_dir = extract_dir / arch
        
        if zip_file.exists():
            print(f"Processing {arch_name} Python distribution...")
            
            # Remove existing directory if it exists
            if target_dir.exists():
                shutil.rmtree(target_dir)
            
            # Create the target directory
            target_dir.mkdir(parents=True)
            
            # Extract the zip file
            with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                zip_ref.extractall(target_dir)
            
            # Enable pip by uncommenting the import site line in python*._pth file
            pth_files = list(target_dir.glob("python*._pth"))
            if pth_files:
                pth_file = pth_files[0]
                
                # Read the file content
                with open(pth_file, 'r') as f:
                    content = f.read()
                
                # Uncomment the import site line
                content = content.replace("#import site", "import site")
                
                # Write the modified content back
                with open(pth_file, 'w') as f:
                    f.write(content)
                
                print(f"Enabled site packages in {pth_file}")
            
            # Copy get-pip.py to the target directory
            shutil.copy(get_pip_path, target_dir / "get-pip.py")
            print(f"Copied get-pip.py to {target_dir}")
            
            print(f"{arch_name} Python environment setup complete!")
        else:
            print(f"Warning: {zip_file} not found. Skipping {arch_name} setup.")
    
    print("\nEmbedded Python setup complete!")
    print("You can now use the embedded Python distributions in your project.")

if __name__ == "__main__":
    extract_embedded_python()