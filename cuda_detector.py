import subprocess
import re
import os
import shutil
import sys

def detect_cuda_version():
    """
    Detect CUDA version using nvidia-smi.
    Returns:
        - The CUDA version string (e.g. "12.6") if detected
        - "NOT_FOUND" if nvidia-smi works but CUDA version can't be extracted
        - "COMMAND_FAILED" if the nvidia-smi command fails
    """
    cuda_version = None
    
    try:
        # Check if nvidia-smi is available using shutil.which
        nvidia_smi_path = shutil.which("nvidia-smi")
        if nvidia_smi_path:
            # First try a simple call with no arguments to verify it works
            try:
                result = subprocess.run([nvidia_smi_path], capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    # Extract CUDA version from the direct output
                    version_match = re.search(r"CUDA Version:\s+(\d+\.\d+)", result.stdout)
                    if version_match:
                        cuda_version = version_match.group(1)
                    else:
                        return "NOT_FOUND"
                else:
                    return "COMMAND_FAILED"
            except Exception:
                return "COMMAND_FAILED"
        else:
            # Try looking for it manually in common locations
            possible_paths = [
                os.path.join(os.environ.get("ProgramFiles", "C:\\Program Files"), "NVIDIA Corporation\\NVSMI\\nvidia-smi.exe"),
                os.path.join(os.environ.get("ProgramW6432", "C:\\Program Files"), "NVIDIA Corporation\\NVSMI\\nvidia-smi.exe")
            ]
            
            for possible_path in possible_paths:
                if os.path.exists(possible_path):
                    try:
                        result = subprocess.run([possible_path], capture_output=True, text=True, timeout=5)
                        if result.returncode == 0:
                            # Extract CUDA version from output
                            version_match = re.search(r"CUDA Version:\s+(\d+\.\d+)", result.stdout)
                            if version_match:
                                cuda_version = version_match.group(1)
                                break
                            else:
                                return "NOT_FOUND"
                        else:
                            continue  # Try next path
                    except Exception:
                        continue  # Try next path
            
            # If we've checked all paths and still have no version
            if cuda_version is None:
                return "COMMAND_FAILED"
    except Exception:
        return "COMMAND_FAILED"
        
    return cuda_version or "NOT_FOUND"

if __name__ == "__main__":
    # When run directly, print the CUDA version to stdout
    version = detect_cuda_version()
    print(version)