"""Demo on how dashed lines might be implemented"""

import math

import vpype as vp
import vsketch


class DashedLinesSketch(vsketch.Vsketch):
    # Sketch parameters:
    quantization = vsketch.Param(0.1, unit="mm")
    dash_steps = vsketch.Param(10)

    def draw(self) -> None:
        self.size("a5", landscape=False)

        # Create some drawings in a sub-sketch
        vsk = vsketch.Vsketch()
        vsk.scale("cm")
        vsk.rect(1, 1, 3, 4)
        vsk.circle(6, 6, 2)
        vsk.bezier(2.5, 3, 5, 2, 1, 7, 6, 6)

        # Iterate over the sub-sketch lines
        for line in vsk.document.layers[1]:
            line = vp.interpolate(line, self.quantization)
            for i in range(math.floor(len(line) / self.dash_steps)):
                if i % 2 == 1:
                    continue
                self.polygon(line[i * self.dash_steps : (i + 1) * self.dash_steps])

    def finalize(self) -> None:
        self.vpype("linemerge linesimplify reloop linesort")


if __name__ == "__main__":
    vsk = DashedLinesSketch()
    vsk.draw()
    vsk.finalize()
    vsk.display()
