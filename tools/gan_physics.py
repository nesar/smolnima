"""GAN physics tools for particle event generation."""

import numpy as np
import matplotlib.pyplot as plt
from smolagents import tool
from scipy.integrate import quad
from scipy import interpolate
from typing import List, Tuple, Optional
import io
import base64


# Default truth parameters for quark distributions
DEFAULT_TRUTH_PARAMS = [-0.4, 2.4, 0.5, -0.06, 0.4, 0.48]


def get_u(x: np.ndarray, a: float, b: float, p: float) -> np.ndarray:
    """Calculate u-quark distribution."""
    return p * x ** a * (1 - x) ** b


def get_d(x: np.ndarray, a: float, b: float, q: float) -> np.ndarray:
    """Calculate d-quark distribution."""
    return q * x ** a * (1 - x) ** b


def get_sigma1(x: np.ndarray, p: List[float]) -> np.ndarray:
    """Calculate first cross-section (4u + d)."""
    u = get_u(x, p[0], p[1], p[2])
    d = get_d(x, p[3], p[4], p[5])
    return 4 * u + d


def get_sigma2(x: np.ndarray, p: List[float]) -> np.ndarray:
    """Calculate second cross-section (4d + u)."""
    u = get_u(x, p[0], p[1], p[2])
    d = get_d(x, p[3], p[4], p[5])
    return 4 * d + u


@tool
def generate_physics_events(
    num_events: int = 10000,
    truth_params: Optional[List[float]] = None,
    seed: Optional[int] = None
) -> str:
    """
    Generate particle physics events based on quark distribution models.

    Args:
        num_events: Number of events to generate
        truth_params: Optional list of 6 parameters [u_a, u_b, u_p, d_a, d_b, d_q]
        seed: Random seed for reproducibility

    Returns:
        String describing the generated events with statistics
    """
    if truth_params is None:
        truth_params = DEFAULT_TRUTH_PARAMS

    if seed is not None:
        np.random.seed(seed)

    # Generate events for both cross-sections
    xmin, xmax = 0.1, 1

    def gen_events_from_sigma(sigma_func, n):
        """Generate events from cross-section function."""
        norm = quad(sigma_func, xmin, xmax)[0]
        pdf = lambda x: sigma_func(x) / norm
        get_cdf = lambda x: quad(pdf, x, xmax)[0]

        x = np.linspace(xmin, xmax, 100)
        invcdf = interpolate.interp1d(
            [get_cdf(_) for _ in x], x,
            bounds_error=False, fill_value=0
        )

        u = np.random.uniform(0, 1, n)
        return invcdf(u)

    sigma1_events = gen_events_from_sigma(lambda x: get_sigma1(x, truth_params), num_events)
    sigma2_events = gen_events_from_sigma(lambda x: get_sigma2(x, truth_params), num_events)

    # Calculate statistics
    stats = {
        "sigma1_mean": float(np.mean(sigma1_events)),
        "sigma1_std": float(np.std(sigma1_events)),
        "sigma2_mean": float(np.mean(sigma2_events)),
        "sigma2_std": float(np.std(sigma2_events)),
        "num_events": num_events,
    }

    result = f"""Generated {num_events} physics events:

Sigma1 (4u + d) distribution:
  Mean: {stats['sigma1_mean']:.3f}
  Std: {stats['sigma1_std']:.3f}

Sigma2 (4d + u) distribution:
  Mean: {stats['sigma2_mean']:.3f}
  Std: {stats['sigma2_std']:.3f}

Truth parameters used: {truth_params}
"""

    return result


@tool
def visualize_quark_distributions(
    truth_params: Optional[List[float]] = None,
    save_path: Optional[str] = None
) -> str:
    """
    Create visualization of u and d quark distributions and cross-sections.

    Args:
        truth_params: Optional list of 6 parameters [u_a, u_b, u_p, d_a, d_b, d_q]
        save_path: Optional path to save the figure

    Returns:
        Description of the generated visualization
    """
    if truth_params is None:
        truth_params = DEFAULT_TRUTH_PARAMS

    x_range = np.linspace(0.1, 1, 1000)

    # Calculate distributions
    u = get_u(x_range, truth_params[0], truth_params[1], truth_params[2])
    d = get_d(x_range, truth_params[3], truth_params[4], truth_params[5])
    sigma1 = 4 * u + d
    sigma2 = 4 * d + u

    # Create figure
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))

    # Plot quark distributions
    axes[0, 0].plot(x_range, u, 'b-', linewidth=2, label='u-quark')
    axes[0, 0].plot(x_range, d, 'r-', linewidth=2, label='d-quark')
    axes[0, 0].set_title('Quark Distributions')
    axes[0, 0].set_xlabel('Momentum Fraction (x)')
    axes[0, 0].set_ylabel('PDF')
    axes[0, 0].legend()
    axes[0, 0].grid(alpha=0.3)

    # Plot ratio u/d
    with np.errstate(divide='ignore', invalid='ignore'):
        ratio = np.where(d > 0, u/d, np.nan)
    axes[0, 1].plot(x_range, ratio, 'g-', linewidth=2)
    axes[0, 1].set_title('u/d Ratio')
    axes[0, 1].set_xlabel('Momentum Fraction (x)')
    axes[0, 1].set_ylabel('Ratio')
    axes[0, 1].grid(alpha=0.3)

    # Plot cross-sections
    axes[1, 0].plot(x_range, sigma1, 'b-', linewidth=2, label='σ1 = 4u + d')
    axes[1, 0].plot(x_range, sigma2, 'r-', linewidth=2, label='σ2 = 4d + u')
    axes[1, 0].set_title('Cross Sections')
    axes[1, 0].set_xlabel('Momentum Fraction (x)')
    axes[1, 0].set_ylabel('Cross Section')
    axes[1, 0].legend()
    axes[1, 0].grid(alpha=0.3)

    # Plot ratio sigma1/sigma2
    with np.errstate(divide='ignore', invalid='ignore'):
        ratio_sigma = np.where(sigma2 > 0, sigma1/sigma2, np.nan)
    axes[1, 1].plot(x_range, ratio_sigma, 'm-', linewidth=2)
    axes[1, 1].set_title('σ1/σ2 Ratio')
    axes[1, 1].set_xlabel('Momentum Fraction (x)')
    axes[1, 1].set_ylabel('Ratio')
    axes[1, 1].grid(alpha=0.3)

    plt.suptitle(f'Quark Distributions for Parameters: {truth_params}', fontsize=14)
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        result = f"Visualization saved to {save_path} and displayed in GUI"
    else:
        result = "Visualization created (4 subplots showing quark distributions, ratios, and cross-sections)"

    # Don't close the figure - let Streamlit capture it for display
    # plt.close(fig) is now handled by Streamlit after capturing

    return result
