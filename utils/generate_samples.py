import hashlib
import random

import numpy as np

from utils.graphics.blends import (
    init_white_band_blend_kernel,
    log_blend_kernel,
)
from utils.graphics.gradients import GradientGraph, example_decoder
from utils.graphics.helpers import show_gradient, save_gradient
from utils.graphics.palette import init_palette
from utils.graphics.post_process import (
    init_noiser,
    init_ordered_dithering,
    init_quantize,
)

if __name__ == "__main__":
    seed = random.randint(0, 0xFFFFFFFF)
    seed = hashlib.sha256(str(seed).encode()).digest()

    palette = init_palette(seed)

    # kernel = init_white_band_blend_kernel(negative_log_blend_kernel, white_strength=1)
    kernel = init_white_band_blend_kernel(log_blend_kernel, white_strength=1)

    post_process = [
        init_ordered_dithering(0.05),
        init_noiser(
            mode="film",
            strength=0.02,
            monochrome=True,
        ),
        init_quantize(32),
    ]
    graph = GradientGraph(
        palette_function=palette,
        decoder=example_decoder,
        blend_kernel=kernel,
        post_process=post_process,
    )

    for i in range(5):  # generate samples
        latent = np.random.randn(16).astype(np.float32)
        img = graph.get_gradient(latent)

        # save_gradient(img, f"../samples/sample_{i}.png")
        show_gradient(img)
