from typing import Tuple

import numpy as np
from PIL import Image

from utils.graphics.color import Color


def softmax(x: np.ndarray, axis: int = -1) -> np.ndarray:
    x = x - np.max(x, axis=axis, keepdims=True)
    e = np.exp(x)
    return e / np.sum(e, axis=axis, keepdims=True)


def create_meshgrid(size_x: int, size_y: int) -> Tuple[np.ndarray, np.ndarray]:
    xs = np.linspace(0, 1, size_x, dtype=np.float32)
    ys = np.linspace(0, 1, size_y, dtype=np.float32)
    return np.meshgrid(xs, ys, indexing="ij")


def _draw_gradient(grad: np.ndarray[Color]):
    if not isinstance(grad, np.ndarray):
        raise TypeError("grad must be a numpy array")

    if grad.ndim != 3 or grad.shape[-1] != 3:
        raise ValueError("grad must have shape (H, W, 3)")

    grad = np.clip(grad, 0.0, 1.0)

    grad_uint8 = (grad * 255).astype(np.uint8)

    return Image.fromarray(grad_uint8, mode="RGB")


def show_gradient(grad: np.ndarray):
    image = _draw_gradient(grad)
    image.show()


def save_gradient(grad: np.ndarray, path: str):
    image = _draw_gradient(grad)
    image.save(path)
