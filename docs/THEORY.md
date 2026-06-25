# Mathematical Theory: Swarm Drones & MFDFA

This document details the theoretical and mathematical foundations for the two research packages contained in this repository:
1. **Bio-Inspired Swarm Drones (Kinematics & Cognitive Load)**
2. **Multifractal Detrended Fluctuation Analysis (MFDFA) of Heart Rate Variability**

---

## 1. Bio-Inspired Swarm Drones (Starling Murmuration)

The drone swarm simulation utilizes a modified Boids model (Reynolds 1987) augmented with a novel 4th rule: **Cognitive Load Balancing**.

### 1.1 Spatial Kinematics
For each drone $i$ in a swarm of $N$ agents, the position $\vec{p}_i(t) \in \mathbb{R}^2$ and velocity $\vec{v}_i(t) \in \mathbb{R}^2$ are governed by:

$$\vec{a}_i(t) = \vec{F}_{\text{sep},i} + \vec{F}_{\text{align},i} + \vec{F}_{\text{coh},i} + \vec{F}_{\text{cog},i} + \vec{F}_{\text{task},i} + \vec{\eta}_i$$

$$\vec{v}_i(t+dt) = \vec{v}_i(t) + \vec{a}_i(t) \cdot dt, \quad ||\vec{v}_i|| \le v_{\text{max}}$$

$$\vec{p}_i(t+dt) = \vec{p}_i(t) + \vec{v}_i(t) \cdot dt$$

### 1.2 Force Formulations
Let $N(i) = \{j : ||\vec{p}_j - \vec{p}_i|| < R_{\text{sense}}, \; j \neq i\}$ represent the neighborhood set of drone $i$.

1. **Separation**: Avoids collisions by applying an inverse-square distance force.
   $$\vec{F}_{\text{sep},i} = -k_{\text{sep}} \sum_{j \in N(i)} \frac{\vec{p}_j - \vec{p}_i}{||\vec{p}_j - \vec{p}_i||^2 + 1}$$

2. **Alignment**: Matches heading velocities with local neighbors.
   $$\vec{F}_{\text{align},i} = \frac{k_{\text{align}}}{|N(i)|} \sum_{j \in N(i)} (\vec{v}_j - \vec{v}_i)$$

3. **Cohesion**: Attracts agents to the center of mass of their neighbors.
   $$\vec{F}_{\text{coh},i} = \frac{k_{\text{coh}}}{|N(i)|} \sum_{j \in N(i)} \frac{\vec{p}_j - \vec{p}_i}{||\vec{p}_j - \vec{p}_i||}$$

4. **Cognitive Load Balancing**: Shifts spatial attraction dynamically to pull highly loaded drones (CPU load $C_i \approx 1$) toward idle neighbors ($C_j \approx 0$) to facilitate wireless task offloading.
   $$\vec{F}_{\text{cog},i} = \frac{k_{\text{cog}}}{|N(i)|} \sum_{j \in N(i)} (C_j - C_i) \cdot \frac{\vec{p}_j - \vec{p}_i}{||\vec{p}_j - \vec{p}_i||}$$

---

## 2. Detrended Fluctuation Analysis (DFA & MFDFA)

Multifractal DFA is used to quantify the scaling properties of physiological time series, specifically the heart rate variability (HRV) RR-interval signals.

### 2.1 The MFDFA Algorithm
Given a time series $x_k$ of length $N$:

1. **Profile Integration**:
   $$y(i) = \sum_{k=1}^i (x_k - \bar{x}), \quad i = 1, \dots, N$$

2. **Segmentation**: Divides the profile $y(i)$ into $N_s = \lfloor N/s \rfloor$ non-overlapping segments of length $s$.
3. **Detrending**: For each segment $\nu = 1, \dots, N_s$, compute the local polynomial fit $y_\nu(i)$ and the variance:
   $$F^2(s, \nu) = \frac{1}{s} \sum_{i=1}^s \left(y((\nu-1)s + i) - y_\nu(i)\right)^2$$

4. **Fluctuation Function**: Computes the generalized $q$-order average:
   $$F_q(s) = \left( \frac{1}{N_s} \sum_{\nu=1}^{N_s} \left[ F^2(s, \nu) \right]^{q/2} \right)^{1/q}, \quad q \neq 0$$
   $$F_0(s) = \exp \left( \frac{1}{2 N_s} \sum_{\nu=1}^{N_s} \ln\left[ F^2(s, \nu) \right] \right)$$

5. **Generalized Hurst Exponents $h(q)$**:
   $$F_q(s) \propto s^{h(q)}$$
   The generalized Hurst exponent is obtained by the linear slope of $\ln(F_q(s))$ vs $\ln(s)$.
   For monofractal series, $h(q)$ is constant. For multifractal signals (such as healthy HRV), $h(q)$ decreases with increasing $q$.

6. **Multifractal Spectrum Width $\Delta h$**:
   $$\Delta h = h(q_{\text{min}}) - h(q_{\text{max}})$$
   A larger width $\Delta h$ indicates high complexity and health, whereas reduced width (e.g. $\Delta h < 0.15$) is a strong marker of physiological stress or disease.
