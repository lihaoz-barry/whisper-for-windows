import sys
import subprocess
import re
import os
import shutil
from PyQt6.QtWidgets import QApplication
from gui.main_window import MainWindow
import torch

def print_cuda_info():
    print("\n=== CUDA Information ===")
    print(f"PyTorch version: {torch.__version__}")
    print(f"CUDA available: {torch.cuda.is_available()}")
    
    cuda_version = None
    
    # Try to get CUDA info from PyTorch first
    if torch.cuda.is_available():
        try:
            # Get CUDA version directly from PyTorch (safer approach)
            if hasattr(torch.cuda, 'get_device_properties'):
                props = torch.cuda.get_device_properties(0)
                print(f"CUDA device count: {torch.cuda.device_count()}")
                print(f"Using GPU: {torch.cuda.get_device_name(0)}")
                print(f"Compute capability: {props.major}.{props.minor}")
                print(f"GPU Memory: {props.total_memory / (1024**3):.2f} GB")
                print(f"GPU Name: {props.name}")
        except Exception as e:
            print(f"Could not get detailed GPU information: {e}")
    else:
        print("No CUDA GPU detected through PyTorch")
    
    # Try to get CUDA version using nvidia-smi
    try:
        # Check if nvidia-smi is available using shutil.which
        nvidia_smi_path = shutil.which("nvidia-smi")
        if nvidia_smi_path:
            print(f"Found nvidia-smi at: {nvidia_smi_path}")
            
            # First try a simple call with no arguments to verify it works
            try:
                result = subprocess.run([nvidia_smi_path], capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    print("Basic nvidia-smi call succeeded")
                    
                    # Extract CUDA version from the direct output (which contains a header with the version)
                    version_match = re.search(r"CUDA Version: (\d+\.\d+)", result.stdout)
                    if version_match:
                        cuda_version = version_match.group(1)
                        print(f"Extracted CUDA version from nvidia-smi output: {cuda_version}")
                    else:
                        print("Could not extract CUDA version from nvidia-smi output")
                else:
                    print(f"Basic nvidia-smi call failed with error: {result.stderr}")
            except subprocess.TimeoutExpired:
                print("nvidia-smi command timed out")
            except Exception as e:
                print(f"Error running basic nvidia-smi: {e}")
        else:
            print("nvidia-smi not found in PATH")
            
            # Try looking for it manually in common locations
            possible_paths = [
                os.path.join(os.environ.get('ProgramFiles', 'C:\\Program Files'), 'NVIDIA Corporation\\NVSMI\\nvidia-smi.exe'),
                os.path.join(os.environ.get('ProgramW6432', 'C:\\Program Files'), 'NVIDIA Corporation\\NVSMI\\nvidia-smi.exe')
            ]
            
            for possible_path in possible_paths:
                if os.path.exists(possible_path):
                    print(f"Found nvidia-smi at: {possible_path}")
                    try:
                        result = subprocess.run([possible_path], capture_output=True, text=True, timeout=5)
                        if result.returncode == 0:
                            print("nvidia-smi call succeeded")
                            
                            # Extract CUDA version from output
                            version_match = re.search(r"CUDA Version: (\d+\.\d+)", result.stdout)
                            if version_match:
                                cuda_version = version_match.group(1)
                                print(f"Extracted CUDA version from nvidia-smi output: {cuda_version}")
                                break
                    except Exception as e:
                        print(f"Error running nvidia-smi from {possible_path}: {e}")
    except Exception as e:
        print(f"Error in nvidia-smi detection: {e}")
    
    print("========================\n")

def main():
    app = QApplication(sys.argv)
    print_cuda_info()
    window = MainWindow()
    window.show()
    sys.exit(app.exec())