import itertools

import vpype
import vsketch


class FillTestSketch(vsketch.SketchClass):
    # page layout
    page_size = vsketch.Param("a4", choices=vpype.PAGE_SIZES.keys())
    landscape = vsketch.Param(False)
    override_page_size = vsketch.Param(False)
    page_width = vsketch.Param(13, unit="cm")
    page_height = vsketch.Param(20.5, unit="cm")

    # hatch density
    smallest_width_mm = vsketch.Param(0.300, decimals=3, step=0.025)
    width_increment_mm = vsketch.Param(0.025, decimals=3, step=0.005)

    # grid layout
    column_count = vsketch.Param(2)
    row_count = vsketch.Param(6)
    horizontal_offset = vsketch.Param(5.5, step=0.1, unit="cm")
    vertical_offset = vsketch.Param(3.0, step=0.1, unit="cm")
    box_width = vsketch.Param(4.0, step=0.1, unit="cm")
    box_height = vsketch.Param(1.5, step=0.1, unit="cm")

    def draw(self, vsk: vsketch.Vsketch) -> None:
        if self.override_page_size:
            vsk.size(f"{self.page_width}x{self.page_height}")
        else:
            vsk.size(self.page_size, landscape=False)

        vsk.stroke(1)
        vsk.fill(1)

        for i, (y, x) in enumerate(
            itertools.product(range(self.row_count), range(self.column_count))
        ):
            pw = self.smallest_width_mm + i * self.width_increment_mm

            vsk.penWidth(f"{pw}mm", 1)
            vsk.rect(
                x * self.horizontal_offset,
                y * self.vertical_offset,
                self.box_width,
                self.box_height,
            )
            vsk.text(
                f"{pw:.3}mm",
                x * self.horizontal_offset + self.box_width / 2,
                y * self.vertical_offset + self.box_height + vpype.convert_length("0.5cm"),
                mode="label",
                align="center",
                size=12,
            )

    def finalize(self, vsk: vsketch.Vsketch) -> None:
        pass


if __name__ == "__main__":
    FillTestSketch.display()
