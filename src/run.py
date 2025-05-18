#!/usr/bin/env python3
import os
import sys

# Add the site-packages directory and current directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# If running with embedded Python, ensure site-packages is in the path
if 'PYTHONPATH' in os.environ and os.environ['PYTHONPATH'] not in sys.path:
    sys.path.insert(0, os.environ['PYTHONPATH'])

# Now import the main function
from main import main

if __name__ == "__main__":
    main()