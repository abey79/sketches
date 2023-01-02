import hashlib
import pathlib
import tempfile

import numpy as np
import PIL.Image
import vpype_cli
import vsketch

ICON_DICT = {
    path.stem: path for path in (pathlib.Path(__file__).parent / "icons").glob("*.png")
}


def convert_to_base_96(i: int) -> list[int]:
    """Convert an integer to a list of base 96 digits."""
    digits = []
    while i:
        digits.append(i % 96)
        i //= 96
    return digits


def check_sum(img: PIL.Image.Image) -> list[int]:
    arr = np.array(img.convert("1").getdata()).reshape(img.size)
    b = np.packbits(arr > 0).tobytes()
    hb = hashlib.sha256(b).digest()
    byte_count = 7
    val = sum(int(hb[i]) * 256**i for i in range(byte_count))

    return convert_to_base_96(val)


def make_checksum_img(img: PIL.Image.Image, spacing: int = 10) -> PIL.Image.Image:
    digits = check_sum(img)
    imgs = [PIL.Image.open(f"glyphs/{digit}.png") for digit in digits]
    widths = [img.width for img in imgs]
    heights = [img.height for img in imgs]
    max_height = max(heights)

    # make a horizontal mosaic with imgs, based on individual image size
    mosaic = PIL.Image.new("1", (sum(widths) + spacing * (len(imgs) - 1), max_height))
    mosaic.paste(1, (0, 0, mosaic.width, mosaic.height))
    cur_offset = 0
    for img, width, height in zip(imgs, widths, heights):
        mosaic.paste(img, (cur_offset, (max_height - height) // 2))
        cur_offset += width + spacing
    return mosaic


def draw_image(
    vsk: vsketch.Vsketch, img: PIL.Image.Image, upscale: int, pen_width: float
) -> None:
    with tempfile.TemporaryDirectory() as tmp_dir:
        path = pathlib.Path(tmp_dir) / "icon.png"
        img.save(path)
        doc = vpype_cli.execute(
            f"pixelart -m snake -bg white -u {upscale} -pw {pen_width} {path}"
        )
    with vsk.pushMatrix():
        vsk.translate(
            -(img.width * upscale * pen_width) / 2, -(img.height * upscale * pen_width) / 2
        )
        for line in doc.layers[1]:
            vsk.polygon(line)


class KareSketch(vsketch.SketchClass):
    icon = vsketch.Param("mac", choices=list(ICON_DICT.keys()))
    icon_offset = vsketch.Param(1.7, step=0.1)
    upscale = vsketch.Param(3, 1)
    pen_width = vsketch.Param(0.3, step=0.05, unit="mm")
    checksum_offset = vsketch.Param(3.0, step=0.1)
    lateral_offset = vsketch.Param(0.355, step=0.05, decimals=3)

    def draw(self, vsk: vsketch.Vsketch) -> None:
        vsk.size("a6", landscape=True, center=False)
        vsk.translate(vsk.width / 2, 0)
        vsk.penWidth(f"{self.pen_width}mm")

        # draw the frame
        with vsk.pushMatrix():
            img = PIL.Image.open("macpaint_frame.png")
            vsk.translate(0, vsk.height / 2)
            draw_image(vsk, img, 1, self.pen_width)

        # draw the icon
        with vsk.pushMatrix():
            img = PIL.Image.open(ICON_DICT[self.icon])
            img = img.convert("1")
            bbox = PIL.ImageOps.invert(img).getbbox()
            img = img.crop(bbox)
            vsk.translate(self.lateral_offset * 100, self.icon_offset * 100)
            draw_image(vsk, img, self.upscale, self.pen_width)

        # draw checksum
        with vsk.pushMatrix():
            vsk.translate(self.lateral_offset * 100, self.checksum_offset * 100)
            checksum_img = make_checksum_img(img)
            draw_image(vsk, checksum_img, 1, self.pen_width)

        vsk.vpype(f"color black penwidth {self.pen_width}")

    def finalize(self, vsk: vsketch.Vsketch) -> None:
        vsk.vpype("linesort")


if __name__ == "__main__":
    KareSketch.display()
