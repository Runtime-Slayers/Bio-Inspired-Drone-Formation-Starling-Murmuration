"""
drone_swarm.model
=================
Core kinematics, Boids forces, and cognitive load balancing for multi-drone swarms.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
import numpy as np


@dataclass
class SwarmConfig:
    """Configuration for the swarm simulation.

    Parameters
    ----------
    n_drones : int
        Number of drones in the swarm.
    arena_size : tuple of float
        Dimensions of the 2D search arena (x, y) in meters.
    dt : float
        Simulation timestep in seconds.
    r_sense : float
        Sensing/communication range of each drone in meters.
    v_max : float
        Maximum drone velocity in m/s.
    k_sep : float
        Separation force gain.
    k_align : float
        Alignment force gain.
    k_coh : float
        Cohesion force gain.
    k_cog : float
        Cognitive load balancing force gain.
    k_task : float
        Attraction force toward unexplored areas.
    noise_std : float
        Standard deviation of random wandering noise.
    detect_range : float
        Camera target detection range in meters.
    detect_prob : float
        Detection probability if target is in range.
    """
    n_drones: int = 50
    arena_size: tuple[float, float] = (1000.0, 1000.0)
    dt: float = 0.5
    r_sense: float = 15.0
    v_max: float = 15.0
    k_sep: float = 2.0
    k_align: float = 1.0
    k_coh: float = 0.5
    k_cog: float = 0.3
    k_task: float = 0.2
    noise_std: float = 0.1
    detect_range: float = 20.0
    detect_prob: float = 0.85


class DroneSwarm:
    """Bio-inspired drone swarm simulator implementing the 4-rule Boids model.

    Includes cognitive load balancing task offloading to model distributed
    processing on the wing.
    """

    def __init__(
        self,
        config: SwarmConfig | None = None,
        with_cognitive_rule: bool = True,
    ) -> None:
        self.config = config if config is not None else SwarmConfig()
        self.with_cognitive = with_cognitive_rule
        cfg = self.config

        # Initialize positions randomly in the arena
        self.pos = np.random.uniform([0.0, 0.0], cfg.arena_size, size=(cfg.n_drones, 2))
        # Initialize velocities with small random vectors
        self.vel = np.random.uniform(-1.0, 1.0, size=(cfg.n_drones, 2)) * 2.0

        # Cognitive loads of drones
        self.load = np.random.uniform(0.3, 0.7, cfg.n_drones)

        # Status tracking
        self.alive = np.ones(cfg.n_drones, dtype=bool)
        self.tasks_completed = np.zeros(cfg.n_drones, dtype=float)

        # 100x100 coverage grid representing 10m grid cells
        self.coverage_grid = np.zeros((100, 100), dtype=float)
        self.time = 0.0

    def get_neighbors(self, i: int) -> np.ndarray:
        """Find indices of active neighbor drones within sensing range of drone i.

        Parameters
        ----------
        i : int
            Target drone index.

        Returns
        -------
        np.ndarray
            Array of active neighbor indices.
        """
        if not self.alive[i]:
            return np.array([], dtype=int)
        
        # Mask out self and inactive drones
        alive_mask = self.alive.copy()
        alive_mask[i] = False
        alive_indices = np.where(alive_mask)[0]

        if len(alive_indices) == 0:
            return np.array([], dtype=int)

        dists = np.linalg.norm(self.pos[alive_indices] - self.pos[i], axis=1)
        neighbors = alive_indices[dists < self.config.r_sense]
        return neighbors

    def compute_forces(self, i: int) -> np.ndarray:
        """Compute all forces (Separation, Alignment, Cohesion, Cognitive, Task, Noise) on drone i.

        Parameters
        ----------
        i : int
            Target drone index.

        Returns
        -------
        np.ndarray
            Resulting force vector.
        """
        cfg = self.config
        neighbors = self.get_neighbors(i)

        f_sep = np.zeros(2)
        f_align = np.zeros(2)
        f_coh = np.zeros(2)
        f_cog = np.zeros(2)

        if len(neighbors) == 0:
            # Wander randomly if isolated
            return np.random.randn(2) * 0.5

        for j in neighbors:
            diff = self.pos[j] - self.pos[i]
            dist = np.linalg.norm(diff) + 1e-6
            direction = diff / dist

            # Rule 1: Separation (inverse-square distance avoidance)
            f_sep -= cfg.k_sep * direction / (dist**2 + 1.0)

            # Rule 2: Alignment (velocity matching)
            f_align += cfg.k_align * (self.vel[j] - self.vel[i]) / len(neighbors)

            # Rule 3: Cohesion (group attraction)
            f_coh += cfg.k_coh * direction / len(neighbors)

            # Rule 4: Cognitive load balancing (NEW — push/pull based on CPU load differences)
            if self.with_cognitive:
                load_diff = self.load[j] - self.load[i]
                f_cog += cfg.k_cog * load_diff * direction / len(neighbors)

        # Mission task force: explore average gradients
        gx = int(np.clip(self.pos[i, 0] / (cfg.arena_size[0] / 100), 0, 99))
        gy = int(np.clip(self.pos[i, 1] / (cfg.arena_size[1] / 100), 0, 99))

        f_task = np.zeros(2)
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = np.clip(gx + dx, 0, 99), np.clip(gy + dy, 0, 99)
            if self.coverage_grid[nx, ny] < self.coverage_grid[gx, gy]:
                f_task += cfg.k_task * np.array([dx, dy])

        noise = np.random.randn(2) * cfg.noise_std
        return f_sep + f_align + f_coh + f_cog + f_task + noise

    def step(self) -> None:
        """Advance the swarm simulation one timestep."""
        cfg = self.config
        forces = np.zeros((cfg.n_drones, 2))

        for i in range(cfg.n_drones):
            if self.alive[i]:
                forces[i] = self.compute_forces(i)

        # Update velocities
        self.vel += forces * cfg.dt

        # Impose velocity limit
        speeds = np.linalg.norm(self.vel, axis=1, keepdims=True)
        self.vel = np.where(speeds > cfg.v_max, self.vel / (speeds + 1e-12) * cfg.v_max, self.vel)

        # Update positions
        self.pos += self.vel * cfg.dt

        # Reflect at boundaries
        for d in range(2):
            below = self.pos[:, d] < 0.0
            above = self.pos[:, d] > cfg.arena_size[d]

            self.pos[below, d] = -self.pos[below, d]
            self.pos[above, d] = 2.0 * cfg.arena_size[d] - self.pos[above, d]
            self.vel[below, d] *= -1.0
            self.vel[above, d] *= -1.0

        # Update spatial coverage grid (mark cells within detection range of active drones)
        grid_res_x = cfg.arena_size[0] / 100
        grid_res_y = cfg.arena_size[1] / 100
        for i in range(cfg.n_drones):
            if self.alive[i]:
                gx = int(np.clip(self.pos[i, 0] / grid_res_x, 0, 99))
                gy = int(np.clip(self.pos[i, 1] / grid_res_y, 0, 99))
                # Camera footprint exploration
                rad_cells_x = int(math.ceil(cfg.detect_range / grid_res_x))
                rad_cells_y = int(math.ceil(cfg.detect_range / grid_res_y))
                for dx in range(-rad_cells_x, rad_cells_x + 1):
                    for dy in range(-rad_cells_y, rad_cells_y + 1):
                        cx, cy = gx + dx, gy + dy
                        if 0 <= cx < 100 and 0 <= cy < 100:
                            self.coverage_grid[cx, cy] += 1.0

        # Update cognitive loads dynamically (mimics new mission computational demand)
        mission_tasks = np.random.uniform(0.1, 0.5, cfg.n_drones)
        self.load = 0.50 + mission_tasks * self.alive  # base load + variable load

        # Run cognitive offloading protocol
        if self.with_cognitive:
            for i in range(cfg.n_drones):
                if self.alive[i] and self.load[i] > 0.80:
                    neighbors = self.get_neighbors(i)
                    for j in neighbors:
                        if self.load[j] < 0.50:
                            offload = min(0.15, self.load[i] - 0.5)
                            self.load[i] -= offload
                            self.load[j] += offload
                            self.tasks_completed[j] += 1.0
                            break

        self.time += cfg.dt

    def kill_drones(self, fraction: float) -> None:
        """Simulate random hardware failures within the swarm.

        Parameters
        ----------
        fraction : float
            Fraction of the swarm to mark as dead.
        """
        n_kill = int(self.config.n_drones * fraction)
        active_indices = np.where(self.alive)[0]
        if len(active_indices) > 0:
            kill_indices = np.random.choice(
                active_indices,
                size=min(n_kill, len(active_indices)),
                replace=False,
            )
            self.alive[kill_indices] = False
            self.load[kill_indices] = 0.0

    def get_coverage_fraction(self) -> float:
        """Return the fraction of the arena explored so far.

        Returns
        -------
        float
            Explored fraction ∈ [0, 1].
        """
        return float(np.sum(self.coverage_grid > 0.0) / self.coverage_grid.size)

    def detect_targets(self, targets: np.ndarray) -> np.ndarray:
        """Evaluate which targets are detected by the swarm.

        Parameters
        ----------
        targets : np.ndarray
            Shape (M, 2) array of target positions.

        Returns
        -------
        np.ndarray
            Boolean mask of found targets.
        """
        targets = np.asarray(targets, dtype=float)
        found = np.zeros(len(targets), dtype=bool)
        cfg = self.config
        for i in range(cfg.n_drones):
            if self.alive[i]:
                dists = np.linalg.norm(targets - self.pos[i], axis=1)
                in_range = dists < cfg.detect_range
                rand_mask = np.random.random(len(targets)) < cfg.detect_prob
                found |= (in_range & rand_mask)
        return found

    def __repr__(self) -> str:
        active = np.sum(self.alive)
        cov = self.get_coverage_fraction() * 100.0
        return (
            f"DroneSwarm(drones={active}/{self.config.n_drones}, "
            f"coverage={cov:.1f}%, time={self.time:.1f}s)"
        )
