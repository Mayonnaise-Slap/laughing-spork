from typing import Callable, List, Tuple

from utils.graphics.blends import *
from utils.graphics.color import Color
from utils.graphics.helpers import create_meshgrid, softmax

DEFAULT_SIZE_X = 500
DEFAULT_SIZE_Y = 500


class GradientGraph:
    def __init__(
            self,
            palette_function: Callable[[int], List[Color]],
            decoder: Callable[[np.ndarray], Tuple[np.ndarray, np.ndarray, np.ndarray]],
            blend_kernel: Callable[[np.ndarray, np.ndarray], np.ndarray],
            post_process: List[Callable[[np.ndarray], np.ndarray]] = None,
            size_x: int = DEFAULT_SIZE_X,
            size_y: int = DEFAULT_SIZE_Y,
    ):
        self.size_x = size_x
        self.size_y = size_y

        self.palette_function = palette_function
        self.post_process = post_process

        self.decoder = decoder
        self.blend_kernel = blend_kernel

        self.grid_x, self.grid_y = create_meshgrid(size_x, size_y)

    def _compute_distances(self, positions: np.ndarray) -> np.ndarray:
        px = positions[:, 0]
        py = positions[:, 1]

        dx = self.grid_x[..., None] - px
        dy = self.grid_y[..., None] - py

        return np.sqrt(dx ** 2 + dy ** 2)

    def get_gradient(self, latent: np.ndarray) -> np.ndarray:
        positions, scales, logits = self.decoder(latent)

        palette = self.palette_function(positions.shape[0])
        palette = np.asarray(palette, dtype=np.float32)

        if positions.shape[0] != len(palette):
            raise ValueError("Number of nodes must match palette length.")

        dist = self._compute_distances(positions)

        responses = self.blend_kernel(dist, scales)

        weights = softmax(responses + logits, axis=-1)

        _gradient = np.einsum("hwn,nc->hwc", weights, palette)
        for post_process in self.post_process:
            _gradient = post_process(_gradient)

        return np.clip(_gradient, 0.0, 1.0)


def example_decoder(z: np.ndarray):
    N = 5

    # Example projection (replace with real NN output)
    positions = np.random.rand(N, 2).astype(np.float32)
    scales = np.random.uniform(0.1, 0.5, size=N).astype(np.float32)
    logits = np.random.randn(N).astype(np.float32)

    return positions, scales, logits
