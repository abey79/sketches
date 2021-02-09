import numpy as np
import vpype as vp
import vsketch


def make_bundle(vsk, start, base_dir, k, freq, freq2):
    for t in np.linspace(0, freq2, 200):
        x = [vp.convert_length(start[0])]
        y = [vp.convert_length(start[1])]
        for _ in range(1000):
            dx = k * (vsk.noise(x[-1] * freq, y[-1] * freq, 0 + t) - 0.5) + base_dir[0]
            dy = k * (vsk.noise(x[-1] * freq, y[-1] * freq, 1000 + t) - 0.5) + base_dir[1]

            x.append(x[-1] + dx)
            y.append(y[-1] + dy)
        vsk.polygon(x, y)


class PerlinAgentsSketch(vsketch.Vsketch):
    k = vsketch.Param(3.0)
    freq = vsketch.Param(0.03)
    freq2 = vsketch.Param(0.5)

    def draw(self) -> None:
        self.size("a4", landscape=True)

        self.scale(2)

        make_bundle(self, (0, 0), (0.45, 0.45), self.k(), self.freq(), self.freq2())
        self.stroke(2)
        make_bundle(self, (300, 0), (-0.45, 0.45), self.k(), self.freq(), self.freq2())
        self.stroke(3)
        make_bundle(self, (500, 300), (-0.60, -0.3), self.k(), self.freq(), self.freq2())

    def finalize(self) -> None:
        self.vpype("linemerge linesort")


if __name__ == "__main__":
    vsk = PerlinAgentsSketch()
    vsk.draw()
    vsk.finalize()
    vsk.display()
