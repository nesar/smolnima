"""Particle physics tools as smolagents tools."""

import numpy as np
import matplotlib.pyplot as plt
from smolagents import tool
from typing import Dict, Union


# Physical constants
PARTICLES = {
    "electron": {"mass_MeV": 0.51099895, "charge": -1, "lifetime_s": float('inf'), "spin": 0.5},
    "proton": {"mass_MeV": 938.272088, "charge": 1, "lifetime_s": float('inf'), "spin": 0.5},
    "neutron": {"mass_MeV": 939.565413, "charge": 0, "lifetime_s": 879.4, "spin": 0.5},
    "muon": {"mass_MeV": 105.6583755, "charge": -1, "lifetime_s": 2.1969811e-6, "spin": 0.5},
    "pion0": {"mass_MeV": 134.9768, "charge": 0, "lifetime_s": 8.52e-17, "spin": 0},
    "pion+": {"mass_MeV": 139.57039, "charge": 1, "lifetime_s": 2.6033e-8, "spin": 0},
}


@tool
def calculate_relativistic_energy(mass_MeV: float, momentum_MeV: float) -> float:
    """
    Calculate relativistic energy using E = sqrt((mc²)² + (pc)²).

    Args:
        mass_MeV: Particle rest mass in MeV/c²
        momentum_MeV: Particle momentum in MeV/c

    Returns:
        Energy in MeV
    """
    return float(np.sqrt(mass_MeV**2 + momentum_MeV**2))


@tool
def calculate_lorentz_factor(velocity_fraction: float) -> float:
    """
    Calculate Lorentz factor γ = 1/sqrt(1 - v²/c²).

    Args:
        velocity_fraction: Velocity as fraction of speed of light (v/c), must be < 1

    Returns:
        Lorentz factor (gamma)
    """
    if velocity_fraction >= 1.0:
        raise ValueError("Velocity must be less than speed of light")

    return float(1.0 / np.sqrt(1.0 - velocity_fraction**2))


@tool
def get_particle_properties(particle_name: str) -> Dict[str, Union[float, int]]:
    """
    Get particle properties from the particle database.

    Args:
        particle_name: Name of particle (e.g., 'electron', 'proton', 'muon')

    Returns:
        Dictionary with mass, charge, lifetime, and spin
    """
    if particle_name not in PARTICLES:
        available = ", ".join(PARTICLES.keys())
        raise ValueError(f"Particle '{particle_name}' not found. Available: {available}")

    return PARTICLES[particle_name].copy()


@tool
def calculate_decay_probability(lifetime_s: float, time_s: float) -> float:
    """
    Calculate decay probability P(t) = 1 - exp(-t/τ) for a particle.

    Args:
        lifetime_s: Mean lifetime in seconds
        time_s: Time elapsed in seconds

    Returns:
        Probability of decay (0 to 1)
    """
    if lifetime_s <= 0:
        return 1.0
    if np.isinf(lifetime_s):
        return 0.0

    return float(1.0 - np.exp(-time_s / lifetime_s))


@tool
def calculate_binding_energy(
    isotope_mass_u: float,
    num_protons: int,
    num_neutrons: int
) -> float:
    """
    Calculate nuclear binding energy from isotope mass.

    Args:
        isotope_mass_u: Measured isotope mass in atomic mass units
        num_protons: Number of protons (Z)
        num_neutrons: Number of neutrons (N)

    Returns:
        Binding energy in MeV
    """
    # Mass of constituent nucleons in u
    proton_mass_u = 938.272088 / 931.494095
    neutron_mass_u = 939.565413 / 931.494095

    nucleon_mass = num_protons * proton_mass_u + num_neutrons * neutron_mass_u

    # Mass defect in u
    mass_defect = nucleon_mass - isotope_mass_u

    # Convert to MeV (1 u = 931.494095 MeV/c²)
    return float(mass_defect * 931.494095)
