"""
hrv_analysis.mfdfa
==================
Multifractal Detrended Fluctuation Analysis (MFDFA) for estimating the generalized Hurst exponents.
"""

from __future__ import annotations

import numpy as np


def mfdfa_analysis(
    signal: np.ndarray,
    q_vals: np.ndarray | list[float],
    s: int = 50,
) -> tuple[np.ndarray, float]:
    """Compute generalized Hurst exponents h(q) and spectrum width delta_h.

    Parameters
    ----------
    signal : array-like
        The input 1D physiological time series.
    q_vals : array-like
        Array of multifractal order parameters q.
    s : int
        Segment scale to analyze (default 50).

    Returns
    -------
    h_q : np.ndarray
        Array of generalized Hurst exponents for each q.
    delta_h : float
        Multifractal spectrum width (max(h_q) - min(h_q)).
    """
    signal = np.asarray(signal, dtype=float)
    q_vals = np.asarray(q_vals, dtype=float)
    N = len(signal)
    
    # 1. Integrate the signal
    y = np.cumsum(signal - np.mean(signal))
    
    n_seg = int(N / s)
    h_q = []
    
    for q in q_vals:
        f_q_list = []
        for k in range(n_seg):
            seg = y[k * s : (k + 1) * s]
            t = np.arange(s)
            
            # Linear detrending
            p = np.polyfit(t, seg, 1)
            res = seg - np.polyval(p, t)
            var = np.mean(res**2)
            
            if q == 0.0:
                f_q_list.append(np.log(var + 1e-12) / 2.0)
            else:
                f_q_list.append((var + 1e-12) ** (q / 2.0))
                
        f_q_mean = np.mean(f_q_list)
        
        if q == 0.0:
            h_val = 0.5 + f_q_mean / np.log(s)
        else:
            h_val = (f_q_mean ** (1.0 / q)) / s if f_q_mean > 0.0 else 0.5
            
        h_q.append(h_val)
        
    h_q = np.array(h_q)
    delta_h = float(np.max(h_q) - np.min(h_q))
    return h_q, delta_h
