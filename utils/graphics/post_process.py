import numpy as np
from typing import Optional, Callable

from numpy import ndarray


def init_noiser(
    mode: str = "gaussian",
    strength: float = 0.02,
    monochrome: bool = True,
    smooth: bool = False,
    seed: Optional[int] = None,
) -> Callable[[ndarray], ndarray]:
    def noiser(gradient: np.ndarray) -> np.ndarray:
        if gradient.ndim != 3 or gradient.shape[-1] != 3:
            raise ValueError("gradient must have shape (H, W, 3)")

        rng = np.random.default_rng(seed)

        H, W, C = gradient.shape

        if monochrome:
            noise = rng.normal(0.0, 1.0, size=(H, W, 1))
            noise = np.repeat(noise, 3, axis=2)
        else:
            noise = rng.normal(0.0, 1.0, size=(H, W, 3))

        if smooth:
            noise = _box_blur(noise)

        if mode == "gaussian":
            out = gradient + strength * noise

        elif mode == "multiplicative":
            out = gradient * (1.0 + strength * noise)

        elif mode == "film":
            lum = (
                0.299 * gradient[..., 0] +
                0.587 * gradient[..., 1] +
                0.114 * gradient[..., 2]
            )[..., None]

            grain = strength * noise
            out = gradient + grain * (0.5 + lum)

        else:
            raise ValueError("Unknown noise mode")

        return np.clip(out, 0.0, 1.0)
    return noiser

def _box_blur(x: np.ndarray, k: int = 3) -> np.ndarray:
    """
    k must be odd.
    """
    pad = k // 2
    x_pad = np.pad(x, ((pad, pad), (pad, pad), (0, 0)), mode="reflect")

    out = np.zeros_like(x)

    for i in range(k):
        for j in range(k):
            out += x_pad[i:i + x.shape[0], j:j + x.shape[1]]

    return out / (k * k)