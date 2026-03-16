"""
Root conftest.py to ensure proper module imports.

This file ensures that the backend module can be imported during tests.
"""

import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
