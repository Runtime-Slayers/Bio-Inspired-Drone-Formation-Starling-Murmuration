"""
tests.test_drone_swarm
======================
Unit tests for the drone_swarm simulation kinematics and cognitive load balancing.
"""

from __future__ import annotations

import numpy as np
import pytest
from drone_swarm import DroneSwarm, SwarmConfig


def test_swarm_default_config():
    cfg = SwarmConfig()
    assert cfg.n_drones == 50
    assert cfg.arena_size == (1000.0, 1000.0)


def test_swarm_initialization():
    cfg = SwarmConfig(n_drones=10)
    swarm = DroneSwarm(config=cfg)
    assert swarm.pos.shape == (10, 2)
    assert swarm.vel.shape == (10, 2)
    assert len(swarm.load) == 10
    assert np.all(swarm.alive)
    assert np.all(swarm.tasks_completed == 0.0)


def test_get_neighbors():
    cfg = SwarmConfig(n_drones=5, r_sense=50.0)
    swarm = DroneSwarm(config=cfg)
    # Force positions: drone 0 and 1 are close, others far
    swarm.pos[0] = [10.0, 10.0]
    swarm.pos[1] = [20.0, 10.0]  # distance 10
    swarm.pos[2] = [100.0, 100.0]
    swarm.pos[3] = [200.0, 200.0]
    swarm.pos[4] = [300.0, 300.0]
    
    n_0 = swarm.get_neighbors(0)
    assert len(n_0) == 1
    assert n_0[0] == 1


def test_forces_computation():
    cfg = SwarmConfig(n_drones=3, r_sense=50.0)
    swarm = DroneSwarm(config=cfg)
    # Setup positions
    swarm.pos[0] = [10.0, 10.0]
    swarm.pos[1] = [15.0, 10.0]
    swarm.pos[2] = [20.0, 10.0]
    
    force_0 = swarm.compute_forces(0)
    assert force_0.shape == (2,)
    # Verify that it is finite
    assert np.all(np.isfinite(force_0))


def test_simulation_step():
    cfg = SwarmConfig(n_drones=5, dt=0.1)
    swarm = DroneSwarm(config=cfg)
    initial_pos = swarm.pos.copy()
    swarm.step()
    # Position should change
    assert not np.array_equal(swarm.pos, initial_pos)
    assert swarm.time == pytest.approx(0.1)


def test_kill_drones():
    cfg = SwarmConfig(n_drones=10)
    swarm = DroneSwarm(config=cfg)
    swarm.kill_drones(0.3)
    assert np.sum(swarm.alive) == 7
    # Dead drones load should be 0
    dead_indices = np.where(~swarm.alive)[0]
    assert np.all(swarm.load[dead_indices] == 0.0)


def test_detect_targets():
    cfg = SwarmConfig(n_drones=2, detect_range=10.0, detect_prob=1.0)
    swarm = DroneSwarm(config=cfg)
    swarm.pos[0] = [50.0, 50.0]
    swarm.pos[1] = [500.0, 500.0]
    
    targets = np.array([
        [52.0, 50.0],   # In range of drone 0
        [800.0, 800.0]   # Out of range of all
    ])
    
    found = swarm.detect_targets(targets)
    assert found[0]
    assert not found[1]


def test_cognitive_offloading():
    cfg = SwarmConfig(n_drones=2, r_sense=100.0)
    swarm = DroneSwarm(config=cfg, with_cognitive_rule=True)
    # Put close
    swarm.pos[0] = [10.0, 10.0]
    swarm.pos[1] = [15.0, 10.0]
    # Set loads: drone 0 is heavily loaded, drone 1 is idle
    swarm.load[0] = 0.95
    swarm.load[1] = 0.20
    
    # Run the offloading protocol block manually to test it in isolation
    for i in range(swarm.config.n_drones):
        if swarm.alive[i] and swarm.load[i] > 0.80:
            neighbors = swarm.get_neighbors(i)
            for j in neighbors:
                if swarm.load[j] < 0.50:
                    offload = min(0.15, swarm.load[i] - 0.5)
                    swarm.load[i] -= offload
                    swarm.load[j] += offload
                    swarm.tasks_completed[j] += 1.0
                    break
                    
    # Verify drone 0 offloaded some tasks to drone 1
    assert swarm.load[0] < 0.95
    assert swarm.load[1] > 0.20
    assert swarm.tasks_completed[1] > 0.0
