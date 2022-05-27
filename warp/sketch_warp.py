import dataclasses
import random

import vsketch


@dataclasses.dataclass
class Ray:
    x: int
    y: int
    start_time: float  # unit: loop
    speed: float  # unit: width / loop
    length: float  # unit: width


class WarpSketch(vsketch.SketchClass):
    m = vsketch.Param(50)
    n = vsketch.Param(50)
    frame_count = vsketch.Param(200)
    frame = vsketch.Param(1, step=10)

    def draw(self, vsk: vsketch.Vsketch) -> None:
        vsk.size("5x5cm", landscape=False, center=False)

        random.seed(vsk.random(1.0))
        rays = tuple(
            Ray(
                random.randint(1, self.m + 1),
                random.randint(0, self.n),
                vsk.random(-0.2, 1.2),
                3.0,
                0.5,
            )
            for _ in range(100)
        )

        time = self.frame / self.frame_count
        for ray in rays:
            for time_offset in (-1, 0, 1):
                start_pos = ((time + time_offset) - ray.start_time) * ray.speed * vsk.width
                vsk.stroke(ray.x)
                vsk.line(
                    start_pos,
                    ray.y / self.n * vsk.height,
                    start_pos - ray.length * vsk.width,
                    ray.y / self.n * vsk.height,
                )

        vsk.vpype("crop 0 0 {vp_page_size[0]} {vp_page_size[1]}")
        vsk.vpype(f"pspread {5/self.m}cm perspective --hfov 100 --pan 90 --move 0 0 -1cm")
        vsk.vpype("lmove all 1")
        # vsk.vpype("pixelize -m snake -pw 0.35mm")

    def finalize(self, vsk: vsketch.Vsketch) -> None:
        vsk.vpype("linesort")


if __name__ == "__main__":
    WarpSketch.display()
