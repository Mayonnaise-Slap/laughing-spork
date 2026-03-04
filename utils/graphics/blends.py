from typing import Callable

import numpy as np


def linear_blend_kernel(dist: np.ndarray, scale: np.ndarray) -> np.ndarray:
    return np.maximum(0.0, 1.0 - dist / (scale + 1e-8))


def quadratic_blend_kernel(dist: np.ndarray, scale: np.ndarray) -> np.ndarray:
    x = np.maximum(0.0, 1.0 - dist / (scale + 1e-8))
    return x ** 2


def gaussian_blend_kernel(dist: np.ndarray, scale: np.ndarray) -> np.ndarray:
    return np.exp(-(dist ** 2) / (2 * (scale + 1e-8) ** 2))

def log_blend_kernel(dist: np.ndarray, scale: np.ndarray) -> np.ndarray:
    return np.log(gaussian_blend_kernel(dist, scale))


def init_white_band_blend_kernel(
    base_kernel: Callable[[np.ndarray, np.ndarray], np.ndarray],
    white_strength: float = 0.5,
) -> Callable[[np.ndarray, np.ndarray], np.ndarray]:
    def kernel(dist: np.ndarray, scale: np.ndarray) -> np.ndarray:
        base = base_kernel(dist, scale)

        top2 = np.partition(base, -2, axis=-1)[..., -2:]
        r1 = top2[..., 1]
        r2 = top2[..., 0]

        eps = 1e-8
        closeness = (r1 - r2) / (r1 + eps)

        whiten_factor = np.clip(closeness * white_strength, 0, 1)

        # Expand to node axis
        whiten_factor = whiten_factor[..., None]

        adjusted = base + whiten_factor

        return adjusted

    return kernel
