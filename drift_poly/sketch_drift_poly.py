import math
import random

import numpy as np
import vsketch


class DriftPolySketch(vsketch.SketchClass):
    # Sketch parameters:
    scale_factor = vsketch.Param(1.0)
    rotation = vsketch.Param(0.0, -180.0, 180.0, step=15.0)
    segment_count = vsketch.Param(8)
    delta = vsketch.Param(1.0)
    line_count = vsketch.Param(100)

    def draw(self, vsk: vsketch.Vsketch) -> None:
        vsk.size("a6", landscape=False)
        vsk.scale(self.scale_factor)
        vsk.rotate(self.rotation, degrees=True)

        N = 20

        angles = np.array(random.sample(range(N), self.segment_count), dtype=float)
        angles *= 2 * math.pi / N

        x = np.cos(angles)
        y = np.sin(angles)

        speeds = np.random.uniform(-1, 1, (self.segment_count, 2))
        speeds *= self.delta / np.hypot(speeds[:, 0], speeds[:, 1]).reshape(-1, 1)

        for _ in range(self.line_count):
            vsk.polygon(x, y)
            x += speeds[:, 0]
            y += speeds[:, 1]

    def finalize(self, vsk: vsketch.Vsketch) -> None:
        vsk.vpype("linemerge linesimplify reloop linesort")


if __name__ == "__main__":
    DriftPolySketch.display()
