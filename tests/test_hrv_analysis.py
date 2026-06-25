"""
tests.test_hrv_analysis
=======================
Unit tests for the hrv_analysis DFA and MFDFA algorithms.
"""

from __future__ import annotations

import numpy as np
import pytest
from hrv_analysis import dfa_alpha, mfdfa_analysis


def test_dfa_alpha_constant():
    # Constant signal should yield trivial scaling
    signal = np.ones(500)
    scales = np.array([10, 20, 50, 100])
    alpha = dfa_alpha(signal, scales)
    # Trivial detrending of flat line gives 0 error, but let's assert it computes without error
    assert isinstance(alpha, float)


def test_dfa_alpha_white_noise():
    # Pure white noise should yield alpha around 0.5
    np.random.seed(42)
    signal = np.random.normal(0.0, 1.0, 1000)
    scales = np.unique(np.geomspace(10, 200, 10, dtype=int))
    alpha = dfa_alpha(signal, scales)
    assert 0.4 < alpha < 0.65


def test_mfdfa_analysis():
    np.random.seed(42)
    signal = np.random.normal(0.0, 1.0, 500)
    q_vals = np.array([-2, 0, 2])
    h_q, delta_h = mfdfa_analysis(signal, q_vals, s=50)
    
    assert len(h_q) == 3
    assert isinstance(delta_h, float)
    assert delta_h >= 0.0
    # Generalized Hurst exponent should be bounded
    assert np.all(h_q > 0.0)
    assert np.all(h_q < 2.0)
