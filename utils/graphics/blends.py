from math import exp, log

from utils.graphics.color import Color


def blend_colors(factors, colors):
    if len(factors) != len(colors):
        raise ValueError("factors and colors must have the same length")

    result = Color(0, 0, 0)
    for factor, color in zip(factors, colors):
        result += color * factor

    return result


def linear_blend_factor(x_norm: float, y_norm: float, *nodes):
    if not (0 <= x_norm <= 1):
        raise ValueError("x_norm must be between 0 and 1")

    if not (0 <= y_norm <= 1):
        raise ValueError("y_norm must be between 0 and 1")

    distances = [node.distance_relative(x_norm, y_norm) for node in nodes]

    weights = [1 / (d + 1e-6) for d in distances]

    total = sum(weights)
    return [w / total for w in weights]


def inverse_linear_blend_factor(x_norm: float, y_norm: float, *nodes):
    if not (0 <= x_norm <= 1):
        raise ValueError("x_norm must be between 0 and 1")

    if not (0 <= y_norm <= 1):
        raise ValueError("y_norm must be between 0 and 1")

    distances = [node.distance_relative(x_norm, y_norm) for node in nodes]

    total = sum(distances)
    return [w / total for w in distances]


def softmax_blend_factor(x_norm: float, y_norm: float, *nodes):
    if not (0 <= x_norm <= 1):
        raise ValueError("x_norm must be between 0 and 1")
    if not (0 <= y_norm <= 1):
        raise ValueError("y_norm must be between 0 and 1")
    distances = [node.distance_relative(x_norm, y_norm) for node in nodes]

    return [1 / (1 + exp(-d)) for d in distances]


def log_sigmoid_blend_factor(x_norm: float, y_norm: float, *nodes):
    if not (0 <= x_norm <= 1):
        raise ValueError("x_norm must be between 0 and 1")
    if not (0 <= y_norm <= 1):
        raise ValueError("y_norm must be between 0 and 1")

    distances = [node.distance_relative(x_norm, y_norm) for node in nodes]

    return [log(1 + exp(-d)) for d in distances]
