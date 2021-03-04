import math

import vsketch


class DotsSketch(vsketch.Vsketch):
    # Sketch parameters:
    orient = vsketch.Param("portrait", choices=["portrait", "landscape"])
    pitch = vsketch.Param(0.5, 0.0, unit="cm", step=0.125, decimals=3)
    num_x = vsketch.Param(16, 1)
    num_y = vsketch.Param(24, 1)
    hi_density = vsketch.Param(1.1, step=0.05, decimals=2)
    lo_density = vsketch.Param(0.25, step=0.05, decimals=2)
    pen_width = vsketch.Param(0.3, unit="mm", step=0.05)
    mapping = vsketch.Param(
        "y_grad",
        choices=[
            "grad",
            "double_grad",
            "double_grad_inside",
            "crossover",
            "circular",
            "circular_crossover",
            "diagonal",
            "diagonal_crossover",
            "stripes",
            "circle_grad",
        ],
    )

    def draw(self) -> None:
        self.size("a6", landscape=self.orient == "landscape")
        self.penWidth(self.pen_width)

        for j in range(self.num_y):
            for i in range(self.num_x):
                if self.mapping == "grad":
                    amt = j / self.num_y
                    color_prob = 1.0
                elif self.mapping == "double_grad":
                    amt = abs(j - self.num_y / 2) / self.num_y * 2
                    color_prob = 1.0
                elif self.mapping == "double_grad_inside":
                    amt = 1.0 - abs(j - self.num_y / 2) / self.num_y * 2
                    color_prob = 1.0
                elif self.mapping == "crossover":
                    amt = 1.0 - abs(j - self.num_y / 2) / self.num_y * 2
                    color_prob = (j / self.num_y - 0.5) * 1.2 + 0.5
                elif self.mapping == "circular":
                    amt = 1 - math.hypot(i - self.num_x / 2, j - self.num_y / 2) / max(
                        self.num_x, self.num_y
                    )
                    color_prob = 1.0
                elif self.mapping == "circular_crossover":
                    amt = 1 - math.hypot(i - self.num_x / 2, j - self.num_y / 2) / max(
                        self.num_x, self.num_y
                    )
                    color_prob = (j / self.num_y - 0.5) * 1.2 + 0.5
                elif self.mapping == "diagonal":
                    amt = 1.0 - abs(1.0 - i / self.num_x - j / self.num_y)
                    color_prob = 1.0
                elif self.mapping == "diagonal_crossover":
                    amt = 1.0 - abs(1.0 - i / self.num_x - j / self.num_y)
                    color_prob = self.lerp(-0.2, 1.2, (i / self.num_x + j / self.num_y) / 2)
                elif self.mapping == "stripes":
                    color_prob = math.floor(i / self.num_x * 9) % 2
                    amt = j / self.num_y
                    if color_prob == 1:
                        amt = 1 - amt
                elif self.mapping == "circle_grad":
                    if math.hypot(i - self.num_x / 2, j - self.num_y / 2) > 0.4 * min(
                        self.num_x, self.num_y
                    ):
                        color_prob = 1.0
                        amt = j / self.num_y
                    else:
                        color_prob = 0.0
                        amt = self.lerp(-0.5, 1.5, 1 - j / self.num_y)
                else:
                    raise NotImplementedError

                prob = self.lerp(self.hi_density, self.lo_density, amt)
                if self.random(1.0) < color_prob:
                    self.stroke(1)
                else:
                    self.stroke(2)
                if self.random(1.0) < prob:
                    self.point(i * self.pitch, j * self.pitch)

    def finalize(self) -> None:
        self.vpype("reloop linesort")


if __name__ == "__main__":
    vsk = DotsSketch()
    vsk.draw()
    vsk.finalize()
    vsk.display()
