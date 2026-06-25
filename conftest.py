"""
conftest.py
===========
Configures test runs, registers markers, and ensures headless matplotlib rendering.
"""

import os
import pytest

# Force matplotlib to use the non-interactive Agg backend during test sessions
os.environ["MPLBACKEND"] = "Agg"
