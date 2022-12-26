import numpy as np
import vsketch


class SnowflakeSketch(vsketch.SketchClass):
    width = vsketch.Param(5.0, unit="cm")
    height = vsketch.Param(5.0, unit="cm")
    max_branch_count = vsketch.Param(10)

    def draw(self, vsk: vsketch.Vsketch) -> None:
        vsk.size(f"{self.width}x{self.height}", landscape=False)
        vsk.scale(self.width, self.height)
        vsk.scale(0.5)
        vsk.translate(0.5, 0.5)

        branch_count = np.random.randint(3, self.max_branch_count + 1)

        branch_locations = np.linspace(0.1, 0.8, branch_count) + np.random.uniform(
            -0.08, 0.08, branch_count
        )
        branch_sizes = np.linspace(0.15, 0.05, branch_count) + np.random.uniform(
            -0.05, 0.1, branch_count
        )

        for _ in range(6):
            vsk.line(0, 0, 0, 0.9)
            vsk.rotate(60, degrees=True)
            for location, size in zip(branch_locations, branch_sizes):
                vsk.line(0, location, size, location + size)
                vsk.line(0, location, -size, location + size)

                if np.random.random() < 0.3:
                    sub_length = size * 0.3
                    sub_pos = size * 0.6
                    with vsk.pushMatrix():
                        vsk.translate(sub_pos, location + sub_pos)
                        vsk.line(0, 0, 0, sub_length)
                        vsk.line(0, 0, sub_length, 0)
                    with vsk.pushMatrix():
                        vsk.translate(-sub_pos, location + sub_pos)
                        vsk.rotate(90, degrees=True)
                        vsk.line(0, 0, 0, sub_length)
                        vsk.line(0, 0, sub_length, 0)

    def finalize(self, vsk: vsketch.Vsketch) -> None:
        vsk.vpype("linemerge linesort")


if __name__ == "__main__":
    SnowflakeSketch.display()
