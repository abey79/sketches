"""Extract all the glyphs from Cairo into PNG files.

Cairo Font from Susan Kare, remastered by Haley Fiege
https://www.haleyfiege.fun/fonts
"""

import pathlib

import PIL.Image
import PIL.ImageDraw
import PIL.ImageFont
import PIL.ImageOps

GLYPHS = list(range(int("0x21", 0), int("0x7E", 0) + 1)) + [int("0xC4", 0), int("0xC5", 0)]


def export_glyphs(font_path: pathlib.Path, directory: pathlib.Path, size=625, down=20):
    font = PIL.ImageFont.truetype(font_path, size)

    for idx, i in enumerate(GLYPHS):
        image = PIL.Image.new("L", (size * 2, size * 2))
        draw = PIL.ImageDraw.Draw(image)
        draw.text((size // 2, size // 2), chr(i), font=font, fill=255)

        image = image.resize(
            (round(size * 2 / down), round(size * 2 / down)),
            resample=PIL.Image.Resampling.NEAREST,
        )

        # crop image to remove whitespace
        bbox = image.getbbox()
        image = image.crop(bbox)

        PIL.ImageOps.invert(image).save(directory / f"{idx}.png")


def main():
    directory = pathlib.Path("glyphs")
    directory.mkdir(exist_ok=True)

    # this size/down-sampling combination was hand-tuned to get the same results as the
    # original bitmap font
    export_glyphs("Cairo", directory, 625, 20)


if __name__ == "__main__":
    main()
