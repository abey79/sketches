"""Postcard mailing helper sketch

How to use:

1) Create the following files next to the sketch script:
-`addresses.txt`: all the addresses, separated by two new lines
- `header.txt`: header text
- `message.txt`: postcard message, may contain $FirstName$, which will be replaced as you
  expect

2) Run: `vsk run postcard`

Note: the bitmap mode requires the Monocraft font (https://github.com/IdreesInc/Monocraft) and
vpype-pixelart (https://github.com/abey79/vpype-pixelart) to work.
"""

from __future__ import annotations

import pathlib
import tempfile
from pathlib import Path

import PIL.Image
import PIL.ImageDraw
import PIL.ImageFont
import vpype as vp
import vpype_cli
import vsketch

try:
    ADDRESSES = (Path(__file__).parent / "addresses.txt").read_text().split("\n\n")
except FileNotFoundError:
    ADDRESSES = ["John Doe\n123 Main St\nAnytown, USA"]

try:
    HEADER = (Path(__file__).parent / "header.txt").read_text()
except FileNotFoundError:
    HEADER = "Myself\nMy Place\nMy town, USA"

try:
    MESSAGE = (Path(__file__).parent / "message.txt").read_text()
except FileNotFoundError:
    MESSAGE = """
Dear $FirstName$,

Please enjoy this postcard!

Best,
Me
"""


def extract_name(line: str) -> tuple[str, str]:
    """Extract the name from the address first line.

    If the line contains square brackets in the form of '[name] surname', return a tuple with
    the content of the brackets and the entire line without the brackets. Otherwise, return a
    tuple with the first word of the line and the entire line.
    """
    if "[" in line and "]" in line:
        name = line[line.index("[") + 1: line.index("]")]
        return name, line.replace("[", "").replace("]", "")
    else:
        return line.split()[0], line


def text_dimension(txt: str) -> tuple[int, int]:
    lines = txt.splitlines()
    return max(len(line) for line in lines), len(lines)


def draw_bitmap_font(
        vsk: vsketch.Vsketch,
        txt: str,
        pos: tuple[float | str, float | str],
        upscale: int,
        pen_width: float,
) -> None:
    # generate image
    w, h = text_dimension(txt)
    font = PIL.ImageFont.truetype("Monocraft", 9)
    image = PIL.Image.new("1", (w * 6, h * 12), color=1)
    draw = PIL.ImageDraw.Draw(image)
    draw.text((0, 0), txt, font=font, fill=0)

    with tempfile.TemporaryDirectory() as tmp_dir:
        path = pathlib.Path(tmp_dir) / "icon.png"
        image.save(path)
        doc = vpype_cli.execute(
            f"pixelart -m snake -bg white -u {upscale} -pw {pen_width} {path}"
        )

    with vsk.resetMatrix():
        vsk.translate(*[vp.convert_length(p) for p in pos])
        for line in doc.layers[1]:
            vsk.polygon(line)


def draw_text(
        vsk: vsketch.Vsketch,
        txt: str,
        pos: tuple[float, float],
        line_offset: float,
        text_size: float,
) -> None:
    for i, line in enumerate(txt.splitlines()):
        vsk.text(line, pos[0], pos[1] + i * line_offset, size=text_size, mode="label")


class PostcardSketch(vsketch.SketchClass):
    addr_id = vsketch.Param(0, 0, len(ADDRESSES) - 1)
    pen_width = vsketch.Param(0.30, step=0.05, unit="mm")
    address_only = vsketch.Param(False)

    # address stuff
    address_bitmap_font = vsketch.Param(False)
    address_font_size = vsketch.Param(18)
    address_line_spacing = vsketch.Param(0.6, decimals=1)
    address_y_offset = vsketch.Param(6.5, decimals=1)

    # header stuff
    header_bitmap_font = vsketch.Param(False)
    header_font_size = vsketch.Param(12)
    header_line_spacing = vsketch.Param(0.4, decimals=1)
    header_y_offset = vsketch.Param(0.8, decimals=1)

    # message stuff
    message_bitmap_font = vsketch.Param(False)
    message_font_size = vsketch.Param(12)
    message_line_spacing = vsketch.Param(0.4, decimals=2)
    message_y_offset = vsketch.Param(2.8, decimals=1)

    def draw(self, vsk: vsketch.Vsketch) -> None:
        vsk.size("a6", landscape=True, center=False)
        vsk.scale("cm")

        address = ADDRESSES[self.addr_id]
        address_lines = address.splitlines()
        name, first_line = extract_name(address_lines[0])
        address = "\n".join([first_line] + address_lines[1:])

        if not self.address_only:
            vsk.line(8, 0.5, 8, 10)
            vsk.rect(12.5, 0.5, 1.8, 2.2)

            if self.header_bitmap_font:
                draw_bitmap_font(
                    vsk,
                    HEADER,
                    ("0.5cm", f"{self.header_y_offset}cm"),
                    upscale=1,
                    pen_width=self.pen_width,
                )
            else:
                draw_text(
                    vsk,
                    HEADER,
                    (0.5, 0.8),
                    self.header_line_spacing,
                    self.header_font_size,
                )

            if self.message_bitmap_font:
                draw_bitmap_font(
                    vsk,
                    MESSAGE.replace("$FirstName$", name),
                    ("0.5cm", f"{self.message_y_offset}cm"),
                    upscale=1,
                    pen_width=self.pen_width,
                )
            else:
                draw_text(
                    vsk,
                    MESSAGE.replace("$FirstName$", name),
                    (0.5, self.message_y_offset),
                    self.message_line_spacing,
                    self.message_font_size,
                )

        if self.address_bitmap_font:
            draw_bitmap_font(
                vsk,
                address,
                ("8.5cm", f"{self.address_y_offset}cm"),
                upscale=2,
                pen_width=self.pen_width,
            )
        else:
            draw_text(
                vsk,
                address,
                (8.5, self.address_y_offset),
                self.address_line_spacing,
                self.address_font_size,
            )

    def finalize(self, vsk: vsketch.Vsketch) -> None:
        vsk.vpype("linesort")


if __name__ == "__main__":
    PostcardSketch.display()
