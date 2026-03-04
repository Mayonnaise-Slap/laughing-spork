import numpy as np


def linear_blend_kernel(dist: np.ndarray, scale: np.ndarray) -> np.ndarray:
    """
    Linear radial falloff.
    dist: (H, W, N)
    scale: (N,)
    """
    return np.maximum(0.0, 1.0 - dist / (scale + 1e-8))


def quadratic_blend_kernel(dist: np.ndarray, scale: np.ndarray) -> np.ndarray:
    """
    Quadratic radial falloff.
    """
    x = np.maximum(0.0, 1.0 - dist / (scale + 1e-8))
    return x ** 2


def gaussian_blend_kernel(dist: np.ndarray, scale: np.ndarray) -> np.ndarray:
    """
    Gaussian radial kernel.
    """
    return np.exp(-(dist ** 2) / (2 * (scale + 1e-8) ** 2))
