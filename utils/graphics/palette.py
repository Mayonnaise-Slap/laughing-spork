import hashlib
import random

import matplotlib.pyplot as plt
import numpy as np

from utils.graphics.color import Color

SCHEME_ANALOGOUS = "analogous"
SCHEME_COMPLEMENTARY = "complementary"
SCHEME_TRIADIC = "triadic"


def hls_to_rgb_np(h, l, s):
    h = np.asarray(h)
    l = np.asarray(l)
    s = np.asarray(s)

    def hue_to_rgb(p, q, t):
        t = t % 1.0
        return np.where(
            t < 1/6, p + (q - p) * 6 * t,
            np.where(
                t < 1/2, q,
                np.where(
                    t < 2/3, p + (q - p) * (2/3 - t) * 6,
                    p
                )
            )
        )

    q = np.where(l < 0.5, l * (1 + s), l + s - l * s)
    p = 2 * l - q

    r = hue_to_rgb(p, q, h + 1/3)
    g = hue_to_rgb(p, q, h)
    b = hue_to_rgb(p, q, h - 1/3)

    return np.stack([r, g, b], axis=-1)


def init_palette(digest: bytes, scheme=SCHEME_ANALOGOUS):
    digest = np.frombuffer(digest, dtype=np.uint8)

    base_h = int.from_bytes(digest[0:2].tobytes(), "big") / 65535.0

    s_seed = digest[2] / 255.0
    base_s = 0.65 + s_seed * 0.3

    l_seed = digest[3] / 255.0
    base_l = 0.35 + l_seed * 0.4

    jitter = (digest[4:12].astype(np.float32) / 255.0 - 0.5) * 0.08

    def generate_palette(n=5, as_color_objects=False):

        if scheme == SCHEME_ANALOGOUS:
            step = 0.08
            offsets = np.linspace(
                -(n // 2) * step,
                (n // 2) * step,
                n
            )

        elif scheme == SCHEME_COMPLEMENTARY:
            offsets = np.array([0.0, 0.5])

        elif scheme == SCHEME_TRIADIC:
            offsets = np.array([0.0, 1/3, 2/3])

        else:
            offsets = np.zeros(n)

        offsets = offsets[:n]

        hues = (base_h + offsets + jitter[:len(offsets)]) % 1.0

        contrast_curve = np.linspace(-0.15, 0.15, len(hues))
        ls = np.clip(base_l + contrast_curve, 0.25, 0.85)

        ss = np.clip(base_s + jitter[:len(hues)], 0.6, 1.0)

        rgb = hls_to_rgb_np(hues, ls, ss).astype(np.float32)

        while rgb.shape[0] != n:
            rgb = np.append(rgb, rgb, axis=0)[:n]

        if as_color_objects:
            return [Color(*c) for c in rgb]

        return rgb

    return generate_palette


def _show_palette(hex_colors):
    hex_colors = [str(i) for i in hex_colors]
    fig, ax = plt.subplots(figsize=(len(hex_colors) * 1.5, 2))

    for i, color in enumerate(hex_colors):
        ax.add_patch(plt.Rectangle((i, 0), 1, 1, color=color))

    ax.set_xlim(0, len(hex_colors))
    ax.set_ylim(0, 1)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_frame_on(False)
    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    seed = random.randint(0, 0xFFFF)
    seed = hashlib.sha256(str(seed).encode()).digest()

    palette = init_palette(seed, scheme="analogous")()
    print(palette)
    _show_palette(palette)
