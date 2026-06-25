"""
hrv_analysis.dfa
================
Detrended Fluctuation Analysis (DFA) for estimating scaling exponents of non-stationary time series.
"""

from __future__ import annotations

import numpy as np


def dfa_alpha(signal: np.ndarray, scales: np.ndarray) -> float:
    """Compute the DFA scaling exponent alpha.

    Parameters
    ----------
    signal : array-like
        The input 1D time series (e.g. RR intervals in ms).
    scales : array-like
        List or array of segment scales to evaluate.

    Returns
    -------
    float
        The scaling exponent alpha (Hurst exponent).
    """
    signal = np.asarray(signal, dtype=float)
    scales = np.asarray(scales, dtype=int)
    N = len(signal)
    
    # 1. Integrate the signal
    y = np.cumsum(signal - np.mean(signal))
    
    F_sq = []
    for s in scales:
        n_seg = int(N / s)
        if n_seg < 2:
            F_sq.append(np.nan)
            continue
        
        f_sq_seg = []
        for k in range(n_seg):
            # Segment boundaries
            seg = y[k * s : (k + 1) * s]
            t = np.arange(s)
            
            # Linear fit and detrend
            p = np.polyfit(t, seg, 1)
            res = seg - np.polyval(p, t)
            f_sq_seg.append(np.mean(res**2))
            
        F_sq.append(np.sqrt(np.mean(f_sq_seg)))
        
    F_sq = np.array(F_sq)
    valid = ~np.isnan(F_sq) & (F_sq > 0.0)
    
    if np.sum(valid) < 3:
        return 0.5  # Return baseline white noise scaling
        
    # Fit log(F(s)) vs log(s)
    slope, _ = np.polyfit(np.log(scales[valid]), np.log(F_sq[valid]), 1)
    return float(slope)
