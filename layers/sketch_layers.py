import math

import numpy as np
import shapely
import vsketch
from shapely import Polygon


class LayersSketch(vsketch.SketchClass):
    def draw(self, vsk: vsketch.Vsketch) -> None:
        vsk.size("13x20.5cm", landscape=False)
        vsk.scale(".3cm")

        vsk.noiseDetail(7, 0.75)

        lines = []

        for i in range(3, 50):
            t = np.linspace(0, math.tau, 1000)
            nx = 0.12345 * (i + 1) + i * 0.005 * np.cos(t)
            ny = 123.2123 * (i + 1) + i * 0.005 * np.sin(t)
            r = i / 3 + 10 * (vsk.noise(nx, ny, grid_mode=False) - 0.5)
            x = r * np.cos(t)
            y = r * np.sin(t)

            poly = Polygon([(px, py) for px, py in zip(x, y)])

            lines = [shapely.intersection(ls, poly) for ls in lines]
            lines.append(poly.exterior)

        for ls in lines:
            vsk.geometry(ls)

    def finalize(self, vsk: vsketch.Vsketch) -> None:
        vsk.vpype("linemerge linesimplify reloop linesort")


if __name__ == "__main__":
    LayersSketch.display()
