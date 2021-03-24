import pathlib
import re

import vsketch

fish_list = [file.stem for file in (pathlib.Path(__file__).parent / "images").glob("*.png")]


class FishSketch(vsketch.SketchClass):
    # Sketch parameters:
    fish_image = vsketch.Param(fish_list[0], choices=fish_list)
    image_scale = vsketch.Param(0.15, step=0.05)
    pitch = vsketch.Param(1.1, step=0.1)
    pen_width = vsketch.Param(0.18, step=0.02)
    black_level = vsketch.Param(0.05, 0.0, 1.0, step=0.025, decimals=3)
    white_level = vsketch.Param(0.95, 0.0, 1.0, step=0.025, decimals=3)
    delete_white = vsketch.Param(True)
    outline_alpha = vsketch.Param(2, 0)
    invert_image = vsketch.Param(False)

    def draw(self, vsk: vsketch.Vsketch) -> None:
        vsk.size("a4", landscape=False)
        vsk.scale("cm")

        flags = ""
        if self.invert_image:
            flags += "i"
        if self.delete_white:
            flags += "d"
        flags += "a" * self.outline_alpha
        if flags != "":
            flags = "-" + flags

        cmd = re.sub(
            r"\s+",
            " ",
            f"""
                variablewidth -s {self.image_scale} -p {self.pitch}mm 
                -pw {self.pen_width}mm -bl {self.black_level} -wl {self.white_level} 
                {flags} images/"{self.fish_image}.png"
            """,
        )
        print(cmd)

        vsk.vpype(cmd)

    def finalize(self, vsk: vsketch.Vsketch) -> None:
        vsk.vpype("linemerge linesimplify reloop linesort")


if __name__ == "__main__":
    FishSketch.display()
