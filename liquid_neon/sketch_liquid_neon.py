import numpy as np
import vpype as vp
import vsketch
from vpype_cli import execute


class LiquidNeonSketch(vsketch.SketchClass):
    # Sketch parameters:
    liquify = vsketch.Param(True)
    ampl = vsketch.Param(5.0, unit="mm")
    freq = vsketch.Param(0.01)

    def draw(self, vsk: vsketch.Vsketch) -> None:
        vsk.size("a6", landscape=False)

        doc = execute(
            "msrandom -ms -q 0.01mm -n 5 10 module_sets/ms_neon_v1 linemerge -t 0.5mm "
            "layout -m 2cm a6 "
        )

        for line in doc.layers[1]:

            line = vp.interpolate(line, step=0.1)

            if not self.liquify:
                vsk.polygon(line)
                continue

            perlin_x = vsk.noise(self.freq * line.real, self.freq * line.imag, grid_mode=False)
            perlin_y = vsk.noise(
                self.freq * line.real,
                self.freq * line.imag,
                1000 * np.ones_like(line.real),
                grid_mode=False,
            )
            line += self.ampl * 2.0 * ((perlin_x - 0.5) + (perlin_y - 0.5) * 1j)

            vsk.polygon(line)
            vsk.vpype("linesimplify -t 0.005mm")

    def finalize(self, vsk: vsketch.Vsketch) -> None:
        vsk.vpype("linemerge reloop linesort")


if __name__ == "__main__":
    LiquidNeonSketch.display()
