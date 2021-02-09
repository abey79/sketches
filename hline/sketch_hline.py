import itertools

import numpy as np
import vpype as vp
import vsketch
from shapely.geometry import MultiLineString, Point, Polygon
from shapely.ops import unary_union


class HLineSketch(vsketch.Vsketch):
    page_size = vsketch.Param("a4", choices=vp.PAGE_FORMATS.keys())
    margin = vsketch.Param(15, 0, unit="mm")
    base_pitch = vsketch.Param(3.0, unit="mm")
    min_radius = vsketch.Param(10.0, unit="mm")
    max_radius = vsketch.Param(50, unit="mm")

    def draw(self) -> None:
        self.size(self.page_size())

        width = round((self.width - 2 * self.margin()) / self.base_pitch()) * self.base_pitch()
        height = (
            round((self.height - 2 * self.margin()) / self.base_pitch()) * self.base_pitch()
        )

        mls0 = MultiLineString(
            [
                [(0, y), (width, y)]
                for y in np.arange(0, height + self.base_pitch(), self.base_pitch())
            ]
        )
        mls1 = MultiLineString(
            [
                [(0, y), (width, y)]
                for y in np.arange(self.base_pitch() / 2, height, self.base_pitch())
            ]
        )
        mls2 = MultiLineString(
            [
                [(0, y), (width, y)]
                for y in np.arange(self.base_pitch() / 4, height, self.base_pitch() / 2)
            ]
        )

        # build a separation
        yy = np.linspace(0, height, 100)
        xx = np.array([self.noise(y * 0.002) for y in yy]) * width / 1.8 + 3 * width / 5 - 200
        p1 = Polygon(list(zip(xx, yy)) + [(width, height), (width, 0)])

        self.geometry(mls0)

        circles = [
            Point(self.random(0, width), self.random(0, height)).buffer(
                self.random(self.min_radius(), self.max_radius())
            )
            for _ in range(5)
        ]

        all_geom = circles + [p1]
        itrsct = unary_union(
            [a.intersection(b) for a, b in itertools.combinations(all_geom, 2)]
        )
        self.geometry(mls1.intersection(unary_union(all_geom)))
        self.geometry(mls2.intersection(itrsct))

    def finalize(self) -> None:
        self.vpype("linemerge linesimplify reloop linesort")


if __name__ == "__main__":
    vsk = HLineSketch()
    vsk.draw()
    vsk.finalize()
    vsk.display()
