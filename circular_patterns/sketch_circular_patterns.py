import math
import random
from typing import Dict, List, Type

import attr
import axi
import numpy as np
import vpype as vp
import vsketch


def norm_angle(a):
    while a > 360:
        a -= 360
    while a < 0:
        a += 360
    return a


@attr.s(auto_attribs=True)
class Elem:
    """
    Elem coordinate system rect:

        (0, 0) -> (w, dr)

    where w = (radius + dr/2) * (start_angle - stop_angle)
    """

    center_x: float = 0.0
    center_y: float = 0.0
    radius: float = 1.0
    dr: float = 0.1
    start_angle: float = 0.0
    stop_angle: float = 360.0
    unit_length: float = 1.0
    quantization: float = 0.1

    def __post_init__(self):
        # normalize angles such that start in is [0, 360] and stop in [0, 720] and greater
        # than start

        self.start_angle = norm_angle(self.start_angle)
        self.stop_angle = norm_angle(self.stop_angle)
        if self.stop_angle <= self.start_angle:
            self.stop_angle += 360

    def render(self) -> vp.LineCollection:
        raise NotImplementedError

    def angle_diff(self):
        """Compute angular difference"""
        return self.stop_angle - self.start_angle

    def width(self):
        return (self.radius + self.dr / 2) * math.pi / 180 * self.angle_diff()

    def elem_to_global_coord(self, x, y):
        r = self.radius + y
        alpha = self.start_angle + x / self.width() * (self.stop_angle - self.start_angle)
        alpha *= math.pi / 180.0

        return self.center_x + r * np.cos(-alpha), self.center_y + r * np.sin(-alpha)

    def elem_to_global_path(self, p: np.ndarray) -> np.ndarray:
        x, y = self.elem_to_global_coord(p.real, p.imag)
        return x + 1j * y

    def elem_to_global_lc(self, lc: vp.LineCollection) -> vp.LineCollection:
        return vp.LineCollection([self.elem_to_global_path(p) for p in lc])


@attr.s
class SpreadElem(Elem):
    """Base class for all element that spread items across the arc"""

    def render(self) -> vp.LineCollection:
        w = self.width()
        n = math.ceil(w / self.unit_length)
        lc = vp.LineCollection()
        for i in range(n):
            x, y = self.elem_to_global_coord((i / n) * w, self.dr / 2)
            item_lc = self.render_item(i, n)
            angle = self.start_angle + (i / n) * (self.stop_angle - self.start_angle) + 90.0
            item_lc.rotate(-angle * math.pi / 180.0)
            item_lc.translate(x, y)
            lc.extend(item_lc)
        return lc

    # noinspection PyMethodMayBeStatic,PyUnusedLocal
    def render_item(self, i: int, n: int) -> vp.LineCollection:
        """Render a single item, centered around (0, 0)"""
        return vp.LineCollection()


DOT_RADIUS = 0.01
DOT = vp.circle(0, 0, DOT_RADIUS, DOT_RADIUS)


@attr.s
class DotElem(SpreadElem):
    def render_item(self, i, n):
        return vp.LineCollection([DOT])


@attr.s
class CircleElem(SpreadElem):
    def render_item(self, i, n):
        return vp.LineCollection(
            [vp.circle(0, 0, self.unit_length / 4, self.unit_length / 10)]
        )


@attr.s
class PlusElem(SpreadElem):
    def render_item(self, i, n):
        u = self.unit_length
        return vp.LineCollection([vp.line(-u / 3, 0, u / 3, 0), vp.line(0, -u / 3, 0, u / 3)])


@attr.s
class BarElem(SpreadElem):
    def render_item(self, i, n):
        return vp.LineCollection([vp.line(0, -self.dr / 2, 0, self.dr / 2)])


@attr.s
class DotBarElem(SpreadElem):
    def render_item(self, i, n):
        if i % 2 == 0:
            return vp.LineCollection([vp.line(0, -self.dr / 2, 0, self.dr / 2)])
        else:
            return vp.LineCollection([DOT])


@attr.s
class SpringElem(Elem):
    def render(self):
        w = self.width()
        n = math.ceil(w / self.unit_length)

        x = np.hstack([[0, 0], np.arange(0.5, n - 0.5, 0.5), n - 1]) * w / n
        y = self.dr * np.ones(x.shape)
        y[1::2] = 0

        return vp.LineCollection([self.elem_to_global_path(x + 1j * y)])


@attr.s
class BoxElem(Elem):
    def render(self):
        w = self.width()
        n = max(math.ceil(self.dr / self.quantization), 2)
        m = max(math.ceil(w / self.quantization), 2)
        # noinspection PyTypeChecker
        p = np.hstack(
            [
                np.linspace(0, self.dr * 1j, n),
                np.linspace(self.dr * 1j, self.dr * 1j + w, m),
                np.linspace(self.dr * 1j + w, w, n),
                np.linspace(w, 0, m, dtype=complex),
            ]
        )
        return vp.LineCollection([self.elem_to_global_path(p)])


@attr.s(auto_attribs=True)
class TextElem(SpreadElem):
    text: str = "A"
    font: List = axi.hershey_fonts.FUTURAM

    def __post_init__(self):
        super().__post_init__()
        lines = axi.text(self.text, self.font)
        self.item_lc = vp.LineCollection()
        for line in lines:
            self.item_lc.append([x + 1j * y for x, y in line])
        x1, y1, x2, y2 = self.item_lc.bounds()
        self.item_lc.translate(-(x1 + x2) / 2, -(y1 + y2) / 2)
        s = self.unit_length / (y2 - y1)
        self.item_lc.scale(s, -s)

    def render_item(self, i, n):
        return vp.LineCollection(self.item_lc)


@attr.s
class SineElem(Elem):
    def render(self):
        n = self.width() / self.unit_length
        t = np.linspace(0, n * 2 * math.pi, int(n * 50))
        return vp.LineCollection(
            [
                self.elem_to_global_path(
                    t / t[-1] * self.width() + 1j * (self.dr / 2 + np.sin(t) * self.dr / 2)
                )
            ]
        )


@attr.s
class CarbonElem(Elem):
    def render(self):
        w = self.width()
        n = math.ceil(w / self.unit_length)

        lc = vp.LineCollection()
        lc.extend(
            [
                1j * self.dr / 2
                + np.linspace((i + 0.1) * w / n, (i + 0.9) * w / n, int(w / self.quantization))
                for i in range(n)
            ]
        )
        lc.extend([np.array([0.1, 0.4]) * 1j * self.dr + i * w / n for i in range(1, n)])
        lc.extend([np.array([0.6, 0.9]) * 1j * self.dr + i * w / n for i in range(1, n)])
        lc.extend(
            [
                vp.circle(i * w / n, self.dr / 2, DOT_RADIUS, DOT_RADIUS / 15)
                for i in range(1, n)
            ]
        )

        return self.elem_to_global_lc(lc)


@attr.s
class LineElem(Elem):
    def render(self):
        w = self.width()
        lc = vp.LineCollection(
            [np.linspace(0, w, math.ceil(w / self.quantization)) + 1j * self.dr / 2]
        )

        return self.elem_to_global_lc(lc)


@attr.s(auto_attribs=True)
class MultiLineElem(Elem):
    line_count: int = 5

    def render(self):
        w = self.width()
        lc = vp.LineCollection(
            [
                np.linspace(h * 1j, w + h * 1j, math.ceil(w / self.quantization))
                for h in np.linspace(0, self.dr, self.line_count)
            ]
        )
        return self.elem_to_global_lc(lc)


ALPHABET: Dict[str, Type[Elem]] = {
    "d": DotElem,
    "D": DotBarElem,
    "c": CircleElem,
    "b": BarElem,
    "p": PlusElem,
    "s": SpringElem,
    "r": BoxElem,
    "S": SineElem,
    "C": CarbonElem,
    "l": LineElem,
    "L": MultiLineElem,
}


def make_drawing(dwg: str) -> vp.LineCollection:
    lines = dwg.splitlines()
    if lines[0] == "":
        del lines[0]

    # base parameters
    base_radius = 1
    base_dr = 0.8
    base_margin = 0.2
    base_unit_length = 0.3

    lc = vp.LineCollection()
    radius = base_radius
    for i, ring in enumerate(lines):

        def count_modifier(s, plus, minus):
            cnt = s.count(plus) - s.count(minus)
            return s.replace(plus, "").replace(minus, ""), cnt

        # extract radii/len modifiers
        ring, dr_modifier = count_modifier(ring, "O", "o")
        ring, r_modifier = count_modifier(ring, "^", "v")
        ring, unit_length_modifier = count_modifier(ring, "+", "-")

        dr = base_dr * (1.2 ** dr_modifier)
        r = radius * (1.05 ** r_modifier)
        unit_length = base_unit_length * 0.7 ** unit_length_modifier

        radius += dr + base_margin

        # compute bounds
        if len(ring) == 0:
            continue
        elif len(ring) == 1:
            arc_bounds = np.array([0, 360])
        else:
            arc_bounds = np.linspace(0, 360, len(ring) + 1) + np.random.uniform(0, 360)

        pos = 0
        while pos < len(ring):
            # fast track to first valid letter
            while pos < len(ring) and ring[pos] not in ALPHABET:
                pos += 1
            if pos == len(ring):
                break

            # find end of streak
            end_pos = pos
            while end_pos < len(ring) and ring[end_pos] == ring[pos]:
                end_pos += 1

            elem_class = ALPHABET[ring[pos]]
            # noinspection PyArgumentList
            elem = elem_class(
                center_x=0,
                center_y=0,
                radius=r,
                dr=dr,
                start_angle=arc_bounds[pos],
                stop_angle=arc_bounds[end_pos],
                unit_length=unit_length,
            )
            lc.extend(elem.render())

            pos = end_pos

    return lc


class SimpleSketch(vsketch.Vsketch):

    # matrix
    page_size = vsketch.Param("a4", choices=vp.PAGE_SIZES.keys())
    nx = vsketch.Param(1, 1)
    ny = vsketch.Param(1, 1)
    nlayer = vsketch.Param(1, 1)
    dx = vsketch.Param(5.0, step=1.0)
    dy = vsketch.Param(5.0, step=1.0)

    letter_count = vsketch.Param(100)
    scale_factor = vsketch.Param(1.0, step=0.1)

    # modifiers
    prob_plus = vsketch.Param(0.1, 0, 1, decimals=2, step=0.05)
    prob_minus = vsketch.Param(0.1, 0, 1, decimals=2, step=0.05)
    prob_bigger = vsketch.Param(0.1, 0, 1, decimals=2, step=0.05)
    prob_smaller = vsketch.Param(0.1, 0, 1, decimals=2, step=0.05)
    prob_raise = vsketch.Param(0.1, 0, 1, decimals=2, step=0.05)
    prob_lower = vsketch.Param(0.1, 0, 1, decimals=2, step=0.05)
    prob_segsep = vsketch.Param(0.1, 0, 1, decimals=2, step=0.05)
    prob_ringsep = vsketch.Param(0.1, 0, 1, decimals=2, step=0.05)

    # primitives
    prob_dot = vsketch.Param(0.1, 0, 1, decimals=2, step=0.05)
    prob_dotbar = vsketch.Param(0.1, 0, 1, decimals=2, step=0.05)
    prob_circle = vsketch.Param(0.1, 0, 1, decimals=2, step=0.05)
    prob_bar = vsketch.Param(0.1, 0, 1, decimals=2, step=0.05)
    prob_cross = vsketch.Param(0.1, 0, 1, decimals=2, step=0.05)
    prob_spring = vsketch.Param(0.1, 0, 1, decimals=2, step=0.05)
    prob_box = vsketch.Param(0.1, 0, 1, decimals=2, step=0.05)
    prob_sine = vsketch.Param(0.1, 0, 1, decimals=2, step=0.05)
    prob_carbon = vsketch.Param(0.1, 0, 1, decimals=2, step=0.05)
    prob_line = vsketch.Param(0.1, 0, 1, decimals=2, step=0.05)
    prob_multiline = vsketch.Param(0.1, 0, 1, decimals=2, step=0.05)

    def draw(self) -> None:
        self.size(self.page_size(), landscape=False)
        self.scale("cm")
        self.scale(self.scale_factor())

        prob = {
            # modifiers
            "+": self.prob_plus(),
            "-": self.prob_minus(),
            "O": self.prob_bigger(),
            "o": self.prob_smaller(),
            "^": self.prob_raise(),
            "v": self.prob_lower(),
            " ": self.prob_segsep(),
            "\n": self.prob_ringsep(),
            # primitives
            "d": self.prob_dot(),
            "D": self.prob_dotbar(),
            "c": self.prob_circle(),
            "b": self.prob_bar(),
            "p": self.prob_cross(),
            "s": self.prob_spring(),
            "r": self.prob_box(),
            "S": self.prob_sine(),
            "C": self.prob_carbon(),
            "l": self.prob_line(),
            "L": self.prob_multiline(),
        }

        for j in range(self.ny()):
            for i in range(self.nx()):

                # noinspection SpellCheckingInspection
                drawing = "".join(
                    random.choices(
                        list(prob.keys()), list(prob.values()), k=self.letter_count()
                    )
                )

                lc = make_drawing(drawing)
                self.stroke((i + j * self.nx()) % self.nlayer() + 1)
                with self.pushMatrix():
                    self.translate(i * self.dx(), j * self.dy())
                    for line in lc:
                        self.polygon(line)

    def finalize(self) -> None:
        self.vpype("linesort linesimplify")
