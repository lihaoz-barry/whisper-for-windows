#!/usr/bin/env python3
import os
import sys

# Print diagnostic information
print(f"Python executable: {sys.executable}")
print(f"Python version: {sys.version}")
print(f"Current working directory: {os.getcwd()}")
print("\nPython paths:")
for path in sys.path:
    print(f"  {path}")

# Try to import the modules we need
modules_to_check = ['PyQt6', 'torch', 'numpy', 'whisper']
print("\nChecking for required modules:")
for module in modules_to_check:
    try:
        __import__(module)
        print(f"  {module}: OK")
    except ImportError as e:
        print(f"  {module}: ERROR - {e}")

# Try to import from our app modules
print("\nChecking application modules:")
try:
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
    from src.main import main
    print("  main module: OK")
except ImportError as e:
    print(f"  main module: ERROR - {e}")

print("\nEnvironment variables:")
for env_var in ['PYTHONPATH', 'PYTHONHOME']:
    print(f"  {env_var}: {os.environ.get(env_var, 'Not set')}")