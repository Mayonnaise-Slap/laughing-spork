import numpy as np


class Color:
    def __init__(self, r: float, g: float, b: float):
        self.rgb = np.array([r, g, b], dtype=np.float32)

    def to_array(self) -> np.ndarray:
        return self.rgb


