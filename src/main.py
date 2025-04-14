import sys
from PyQt6.QtWidgets import QApplication
from gui.main_window import MainWindow
import torch

def print_cuda_info():
    print("\n=== CUDA Information ===")
    print(f"PyTorch version: {torch.__version__}")
    print(f"CUDA available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"CUDA device count: {torch.cuda.device_count()}")
        print(f"Using GPU: {torch.cuda.get_device_name(0)}")
        print(f"GPU Count: {torch.cuda.device_count()}")
        print(f"Current device: {torch.cuda.current_device()}")
    else:
        print("No CUDA GPU available - running in CPU mode")
    print("========================\n")

def main():
    app = QApplication(sys.argv)
    print_cuda_info()
    window = MainWindow()
    window.show()
    sys.exit(app.exec())