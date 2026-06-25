# Swarm Drone Murmuration & HRV MFDFA Analysis

[![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![CI](https://github.com/Runtime-Slayers/Bio-Inspired-Drone-Formation-Starling-Murmuration/actions/workflows/ci.yml/badge.svg)](https://github.com/Runtime-Slayers/Bio-Inspired-Drone-Formation-Starling-Murmuration/actions)

This repository contains two bio-inspired packages:
1. **`drone_swarm`**: Bio-inspired drone swarm simulator implementing the Boids model with a novel **4th rule: Cognitive Load Balancing** (BT19).
2. **`hrv_analysis`**: Detrended Fluctuation Analysis (DFA) and Multifractal DFA (MFDFA) for physiological stress classification using heart rate variability (HRV) (P39).

---

## 1. Bio-Inspired Swarm Drones (`drone_swarm`)

Implements flocking dynamics (separation, alignment, cohesion) plus a cognitive load rule to distribute computational tasks on the fly among nearest neighbors.

### Kinematics Equations

$$\vec{a}_i(t) = \vec{F}_{\text{sep},i} + \vec{F}_{\text{align},i} + \vec{F}_{\text{coh},i} + \vec{F}_{\text{cog},i} + \vec{F}_{\text{task},i} + \vec{\eta}_i$$

* **Separation**: $\vec{F}_{\text{sep},i} = -k_{\text{sep}} \sum_{j \in N(i)} \frac{\vec{p}_j - \vec{p}_i}{||\vec{p}_j - \vec{p}_i||^2 + 1}$
* **Cognitive balancing (Rule 4)**: $\vec{F}_{\text{cog},i} = \frac{k_{\text{cog}}}{|N(i)|} \sum_{j \in N(i)} (C_j - C_i) \cdot \frac{\vec{p}_j - \vec{p}_i}{||\vec{p}_j - \vec{p}_i||}$

---

## 2. HRV MFDFA Stress Analyzer (`hrv_analysis`)

Quantifies complexity in heart rate fluctuations (RR intervals) to classify cognitive/academic stress.

### MFDFA Exponent
The generalized Hurst exponent $h(q)$ is computed from the log-log scaling slope:

$$F_q(s) \propto s^{h(q)}$$

Stress is indicated by a narrow multifractal spectrum width: $\Delta h = h(q_{\text{min}}) - h(q_{\text{max}}) < 0.15$.

---

## Installation

```bash
# Clone the repository
git clone https://github.com/Runtime-Slayers/Bio-Inspired-Drone-Formation-Starling-Murmuration.git
cd Bio-Inspired-Drone-Formation-Starling-Murmuration

# Install in editable mode
pip install -e .
```

---

## Quick Start

### 1. Swarm Simulation
```python
from drone_swarm import DroneSwarm, SwarmConfig

# Init swarm with custom config
cfg = SwarmConfig(n_drones=30, v_max=12.0)
swarm = DroneSwarm(config=cfg, with_cognitive_rule=True)

# Advance simulation step
swarm.step()
print(swarm)
```

### 2. HRV MFDFA Analysis
```python
import numpy as np
from hrv_analysis import dfa_alpha, mfdfa_analysis

# Generate random RR-intervals
rr_intervals = np.random.normal(800.0, 50.0, 1000)
scales = np.array([10, 20, 50, 100])

# Run DFA
alpha = dfa_alpha(rr_intervals, scales)
print(f"DFA Alpha: {alpha:.3f}")

# Run MFDFA
q_vals = np.array([-2, 0, 2])
h_q, delta_h = mfdfa_analysis(rr_intervals, q_vals, s=50)
print(f"Spectrum width delta_h: {delta_h:.3f}")
```

---

## Run Validation Experiments

To run the Starling Swarm simulation:
```bash
python experiments/bt19_swarm_drones.py
```

To run the MFDFA HRV Stress validation:
```bash
python experiments/p39_real_data.py
```

Outputs will be saved in `figures_p39/` as PNG plots and JSON result logs.

---

## Running Tests

To execute the test suite:
```bash
pytest tests/ -v
```

---

## Citations

```bibtex
@article{reynolds1987flocks,
  title={Flocks, herds and schools: A distributed behavioral model},
  author={Reynolds, Craig W},
  journal={ACM SIGGRAPH computer graphics},
  volume={21},
  number={4},
  pages={25--34},
  year={1987}
}

@article{kantelhardt2002multifractal,
  title={Multifractal detrended fluctuation analysis of nonstationary time series},
  author={Kantelhardt, Jan W and Zschiegner, Stephan A and Koscielny-Bunde, Eva and Havlin, Shlomo and Bunde, Armin and Stanley, H Eugene},
  journal={Physica A: Statistical Mechanics and its Applications},
  volume={316},
  number={1-4},
  pages={87--114},
  year={2002}
}
```

---

## License
[MIT](LICENSE) © Runtime-Slayers
