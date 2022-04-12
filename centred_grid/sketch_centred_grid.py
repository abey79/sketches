import itertools

import vsketch

PX_TO_CM = 2.54 / 96.0


class CentredGridSketch(vsketch.SketchClass):
    width = vsketch.Param(21.0, step=0.1, unit="cm")
    height = vsketch.Param(29.7, step=0.1, unit="cm")
    landscape = vsketch.Param(False)
    N = vsketch.Param(5, 1)
    M = vsketch.Param(7, 1)

    def draw(self, vsk: vsketch.Vsketch) -> None:
        vsk.size(self.width, self.height, landscape=self.landscape, center=False)

        delta = (vsk.height - vsk.width) / (self.M - self.N)
        margin = (self.M * vsk.width - self.N * vsk.height) / 2 / (self.M - self.N)

        vsk.stroke(1)
        vsk.vpype(
            f"text -p 10 20 -s 25 'cell size = {delta*PX_TO_CM:0.2f}cm / "
            f"margin = {margin*PX_TO_CM:0.2f}cm' penwidth -l1 3"
        )

        if delta < 0:
            vsk.vpype("text -p 10 55 -s 25 'negative cell size, adjust M and N!!!'")
        else:
            vsk.stroke(2)
            vsk.translate(margin, margin)
            for i in range(self.N + 1):
                vsk.line(i * delta, 0, i * delta, self.M * delta)
            for j in range(self.M + 1):
                vsk.line(0, j * delta, self.N * delta, j * delta)
            vsk.vpype("color -l2 #ccc")
            vsk.stroke(3)
            vsk.penWidth(3, 3)
            for i, j in itertools.product(range(self.N + 1), range(self.M + 1)):
                vsk.point(i * delta, j * delta)
            vsk.vpype("color -l3 red")

    def finalize(self, vsk: vsketch.Vsketch) -> None:
        vsk.vpype("linemerge linesimplify reloop linesort")


if __name__ == "__main__":
    CentredGridSketch.display()
