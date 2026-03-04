import hashlib
import random

import numpy as np

from utils.graphics.blends import gaussian_blend_kernel
from utils.graphics.gradients import GradientGraph, example_decoder
from utils.graphics.helpers import show_gradient
from utils.graphics.palette import generate_palette, SCHEME_ANALOGOUS

if __name__ == '__main__':
    seed = random.randint(0, 0xFFFFFFFF)
    seed = hashlib.sha256(str(seed).encode()).digest()

    palette = generate_palette(seed, SCHEME_ANALOGOUS, 6)
    graph = GradientGraph(
        palette=palette,
        decoder=example_decoder,
        blend_kernel=gaussian_blend_kernel,
    )

    latent = np.random.randn(16).astype(np.float32)
    img = graph.get_gradient(latent)

    show_gradient(img)