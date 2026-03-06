from typing import Optional, Callable

import numpy as np
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
                0.299 * gradient[..., 0]
                + 0.587 * gradient[..., 1]
                + 0.114 * gradient[..., 2]
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
            out += x_pad[i : i + x.shape[0], j : j + x.shape[1]]

    return out / (k * k)


def init_ordered_dithering(strength: float = 0.02) -> Callable[[ndarray], ndarray]:
    def dithering(gradient: np.ndarray) -> np.ndarray:
        if gradient.ndim != 3 or gradient.shape[-1] != 3:
            raise ValueError("gradient must have shape (H, W, 3)")

        H, W, _ = gradient.shape

        # 4x4 Bayer matrix
        bayer = np.array(
            [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]],
            dtype=np.float32,
        )

        bayer = (bayer + 0.5) / 16.0  # normalize to [0,1]

        tiled = np.tile(bayer, (H // 4 + 1, W // 4 + 1))[:H, :W]

        tiled = tiled[..., None]  # match channel dimension

        dithered = gradient + (tiled - 0.5) * strength

        return np.clip(dithered, 0.0, 1.0)

    return dithering


def init_quantize(levels: int = 8) -> Callable[[ndarray], ndarray]:
    def quantize(gradient: np.ndarray) -> np.ndarray:
        if levels < 2:
            raise ValueError("levels must be >= 2")

        q = np.round(gradient * (levels - 1)) / (levels - 1)

        return np.clip(q, 0.0, 1.0)

    return quantize
