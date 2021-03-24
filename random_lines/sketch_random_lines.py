import numpy as np
import vsketch


class RandomLinesSketch(vsketch.SketchClass):
    # Sketch parameters:
    num_lines = vsketch.Param(1000, step=100)

    def draw(self, vsk: vsketch.Vsketch) -> None:
        vsk.size("a4", landscape=False, center=False)
        vsk.scale(2)

        y_coords = np.linspace(0.0, 250.0, self.num_lines)
        x_coords = np.linspace(0.0, 250.0, 500)
        perlin = vsk.noise(x_coords * 0.1, y_coords * 0.2)

        x_factor = 0.5 * (1.0 - np.cos(x_coords / 250.0 * 2 * np.pi))
        y_factor = 0.5 * (1.0 - np.cos(y_coords / 250.0 * 2 * np.pi))

        for j, y in enumerate(y_coords):
            vsk.polygon(x_coords, y + perlin[:, j] * 12 * y_factor[j] * x_factor)

        vsk.vpype("layout -h center -v top a4 translate 0 3.8cm")

    def finalize(self, vsk: vsketch.Vsketch) -> None:
        vsk.vpype("linesimplify -t 0.001mm linemerge -t 0.5mm")


if __name__ == "__main__":
    RandomLinesSketch.display()
