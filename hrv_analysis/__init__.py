"""
hrv_analysis
============
Detrended Fluctuation Analysis (DFA) and Multifractal DFA (MFDFA) library
for heart rate variability (HRV) and physiological signals.
"""

from __future__ import annotations

from .dfa import dfa_alpha
from .mfdfa import mfdfa_analysis

__all__ = ["dfa_alpha", "mfdfa_analysis"]
__version__ = "0.1.0"
