"""Prints some information on a font. Stolen from somewhere on the internet.

Usage:

    python font_info.py FONTNAME
"""

from freetype import *
from matplotlib import font_manager

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: %s font_filename" % sys.argv[0])
        sys.exit()

    if len(sys.argv) >= 3:
        index = int(sys.argv[2])
    else:
        index = 0

    font_file = font_manager.findfont(sys.argv[1])
    print(f"Reading {font_file}")
    face = Face(font_file, index=index)

    print("Family name:         {}".format(face.family_name))
    print("Style name:          {}".format(face.style_name))
    print(
        "Charmaps:            {}".format([charmap.encoding_name for charmap in face.charmaps])
    )
    print("")
    print("Face number:         {}".format(face.num_faces))
    print("Face index:          {}".format(face.face_index))
    print("Glyph number:        {}".format(face.num_glyphs))
    print("Available sizes:     {}".format(face.available_sizes))
    print("")
    print("units per em:        {}".format(face.units_per_EM))
    print("ascender:            {}".format(face.ascender))
    print("descender:           {}".format(face.descender))
    print("height:              {}".format(face.height))
    print("")
    print("max_advance_width:   {}".format(face.max_advance_width))
    print("max_advance_height:  {}".format(face.max_advance_height))
    print("")
    print("underline_position:  {}".format(face.underline_position))
    print("underline_thickness: {}".format(face.underline_thickness))
    print("")
    print("Has horizontal:      {}".format(face.has_horizontal))
    print("Has vertical:        {}".format(face.has_vertical))
    print("Has kerning:         {}".format(face.has_kerning))
    print("Is fixed width:      {}".format(face.is_fixed_width))
    print("Is scalable:         {}".format(face.is_scalable))
    print("")
