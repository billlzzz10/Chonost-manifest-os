#!/usr/bin/env python3
"""
Simple script to run the Chonost Unified Backend Server
"""

import sys
import os

# Add parent directory to Python path for imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

# Import after path modification
from backend.main import run_app

if __name__ == "__main__":
    run_app()
