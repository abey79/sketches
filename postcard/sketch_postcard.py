"""Postcard mailing helper sketch

How to use:

1) Create the following files next to the sketch script:
-`addresses.txt`: all the addresses, separated by two new lines
- `header.txt`: header text
- `message.txt`: postcard message, may contain $FirstName$, which will be replaced as you
  expect

2) Run: `vsk run postcard`
"""

from pathlib import Path
from typing import List, Tuple

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


class PostcardSketch(vsketch.SketchClass):
    addr_id = vsketch.Param(0, 0, len(ADDRESSES) - 1)

    @staticmethod
    def draw_text(
        vsk: vsketch.Vsketch,
        lines: List[str],
        pos: Tuple[float, float],
        line_offset: float,
        text_size: float,
    ) -> None:
        for i, line in enumerate(lines):
            vsk.vpype(
                f"text -l 1 -s {text_size} -p {pos[0]}cm {pos[1] + i * line_offset}cm '{line}'"
            )

    def draw(self, vsk: vsketch.Vsketch) -> None:
        vsk.size("a6", landscape=True, center=False)
        vsk.scale("cm")

        vsk.line(8, 0.5, 8, 10)
        vsk.rect(12.5, 0.5, 1.8, 2.2)

        self.draw_text(
            vsk,
            HEADER.split("\n"),
            (0.5, 0.8),
            0.4,
            5.5,
        )

        address = ADDRESSES[self.addr_id].split("\n")
        name = address[0].split(" ")[0]

        self.draw_text(
            vsk, MESSAGE.replace("$FirstName$", name).split("\n"), (0.5, 2.5), 0.5, 7
        )

        self.draw_text(vsk, address, (8.5, 6.5), 0.5, 9)

    def finalize(self, vsk: vsketch.Vsketch) -> None:
        pass


if __name__ == "__main__":
    PostcardSketch.display()
