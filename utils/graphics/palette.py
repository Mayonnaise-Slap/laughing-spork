import colorsys
import hashlib
import random

import matplotlib.pyplot as plt

from utils.graphics.color import Color


def generate_palette(digest: bytes, scheme="analogous", n=5):
    h = int.from_bytes(digest[0:2], "big") / 65535

    s = digest[2] / 255
    l = digest[3] / 255

    # Constrain to usable design ranges
    s = 0.45 + s * 0.4
    l = 0.35 + l * 0.3

    palette = []

    if scheme == "analogous":
        step = 0.05
        offsets = [i * step for i in range(-(n // 2), n // 2 + 1)]
    elif scheme == "complementary":
        offsets = [0, 0.5]  # 180°
    elif scheme == "triadic":
        offsets = [0, 1 / 3, 2 / 3]
    else:
        offsets = [0]

    for offset in offsets:
        new_h = (h + offset) % 1.0
        rgb = colorsys.hls_to_rgb(new_h, l, s)
        palette.append(Color(*rgb))

    return palette[:n]


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

    palette = generate_palette(seed, scheme="analogous", n=5)
    print(palette)
    _show_palette(palette)
