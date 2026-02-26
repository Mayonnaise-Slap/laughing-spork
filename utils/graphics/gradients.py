import hashlib
import math
import random

from PIL import Image

from utils.graphics.blends import blend_colors, linear_blend_factor, inverse_linear_blend_factor, softmax_blend_factor, \
    log_sigmoid_blend_factor
from utils.graphics.palette import generate_palette


class GradientNode:
    def __init__(self, x: int, y: int, max_x: int, max_y: int):
        if x > max_x:
            raise ValueError("x is too big")
        if y > max_y:
            raise ValueError("y is too big")

        self.x = x
        self.y = y
        self.max_x = max_x
        self.max_y = max_y

    @property
    def absolute(self) -> (int, int):
        return self.x, self.y

    @property
    def relative(self) -> (float, float):
        return self.x / self.max_x, self.y / self.max_y

    def distance_relative(self, x: float, y: float) -> float:
        x_node = self.x / self.max_x
        y_node = self.y / self.max_y
        return math.sqrt((x - x_node) ** 2 + (y - y_node) ** 2)

class GradientGraph:
    min_gradient_nodes = 4
    max_gradient_nodes = 8
    gradient_x_dim = 512
    gradient_y_dim = 512
    nodes = list

    def __init__(self, seed, scheme="analogous", blend_factor=linear_blend_factor):
        self.seed = hashlib.sha256(str(seed).encode()).digest()
        self.blend = blend_factor


        self.n_nodes = random.randint(self.min_gradient_nodes, self.max_gradient_nodes)
        self.palette = generate_palette(self.seed, scheme, n=self.n_nodes)

        self.nodes = [
            GradientNode(
                random.randint(0, self.gradient_x_dim),
                random.randint(0, self.gradient_y_dim),
                self.gradient_x_dim, self.gradient_y_dim,
            ) for _ in range(self.n_nodes)
        ]


    def get_gradient(self):
        canvas = []
        for j in range(self.gradient_y_dim):
            canvas.append([])
            for i in range(self.gradient_x_dim):
                i_norm = i / self.gradient_x_dim
                j_norm = j / self.gradient_y_dim
                factors = self.blend(i_norm, j_norm, *self.nodes)
                color = blend_colors(factors, self.palette)

                canvas[j].append(color)
        return canvas


def _draw_gradient(grad):
    if not grad or not grad[0]:
        raise ValueError("Empty gradient")

    height = len(grad)
    width = len(grad[0])

    image = Image.new("RGB", (width, height))
    pixels = image.load()

    for y in range(height):
        for x in range(width):
            hex_color = grad[y][x].rgb()
            pixels[x, y] = hex_color

    image.show()


if __name__ == '__main__':
    # seed = random.randint(0, 0xFFFFFFFF)
    seed = 4259820596
    # gradient = GradientGraph(seed=seed, scheme="analogous", blend_factor=linear_blend_factor)
    # _draw_gradient(gradient.get_gradient())
    # gradient = GradientGraph(seed=seed, scheme="analogous", blend_factor=inverse_linear_blend_factor)
    # _draw_gradient(gradient.get_gradient())
    # gradient = GradientGraph(seed=seed, scheme="analogous", blend_factor=softmax_blend_factor)
    # _draw_gradient(gradient.get_gradient())
    gradient = GradientGraph(seed=seed, scheme="analogous", blend_factor=log_sigmoid_blend_factor)
    _draw_gradient(gradient.get_gradient())
