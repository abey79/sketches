import io
import itertools
import math
import os
import string
import sys
from pathlib import Path

import freetype
import vpype as vp
import vsketch
from matplotlib import font_manager
from shapely.affinity import scale, translate
from shapely.geometry import JOIN_STYLE, MultiLineString, MultiPoint, Point, Polygon, box
from shapely.ops import unary_union

sys.path.append(str(Path(__file__).parent))


def move_to(a, ctx):
    ctx.append("M {},{}".format(a.x, a.y))


def line_to(a, ctx):
    ctx.append("L {},{}".format(a.x, a.y))


def conic_to(a, b, ctx):
    ctx.append("Q {},{} {},{}".format(a.x, a.y, b.x, b.y))


def cubic_to(a, b, c, ctx):
    ctx.append("C {},{} {},{} {},{}".format(a.x, a.y, b.x, b.y, c.x, c.y))


def load_glyph(font_name: str, glyph: str, index: int = 0) -> Polygon:
    face = freetype.Face(font_manager.findfont(font_name), index=index)
    face.set_char_size(128 * 64)
    face.load_char(glyph, freetype.FT_LOAD_DEFAULT | freetype.FT_LOAD_NO_BITMAP)
    ctx = []
    face.glyph.outline.decompose(
        ctx, move_to=move_to, line_to=line_to, conic_to=conic_to, cubic_to=cubic_to
    )
    bbox = face.glyph.outline.get_bbox()
    width = bbox.xMax - bbox.xMin
    height = bbox.yMax - bbox.yMin
    svg = f"""<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">
  <g transform="translate(0, {bbox.yMax - bbox.yMin}) scale(1, -1) translate({-bbox.xMin}, {-bbox.yMin})" transform-origin="0 0">
    <path
      style="fill:none;stroke:#000000;stroke-width:2;stroke-linecap:butt;stroke-linejoin:miter;stroke-miterlimit:4;stroke-opacity:1;stroke-dasharray:none;stroke-dashoffset:0"
      d="{' '.join(ctx)}"
    />
    <!-- rect x="{bbox.xMin}" y="{bbox.yMin}" width="{width}" height="{height}" /-->
  </g>
</svg>
"""

    svg_io = io.StringIO(svg)
    lc, w, h = vp.read_svg(svg_io, 1)

    mls = lc.as_mls()
    poly = Polygon(mls.geoms[0])
    for geom in mls.geoms[1:]:
        poly = poly.symmetric_difference(Polygon(geom))
    return poly


class MachineTypographySketch(vsketch.SketchClass):
    # Sketch parameters:
    font = vsketch.Param(
        "Times",
        choices=[
            "Times",
            "Helvetica Neue",
            "Zapfino",
            "American Typewriter",
            "Arial Black",
            "Avenir",
            "Avenir Next",
            "Bangla MN",
            "Baskerville",
            "Bodoni 72",
            "CMU Serif Upright Italic",
            "Copperplate",
            "Futura",
            "Heiti TC",
            "Ideal Sans",
            "Impact",
            "Kannada MN",
            "Labtop",
            "Lao MN",
        ],
    )
    face_index = vsketch.Param(0, 0)
    glyph = vsketch.Param("a", choices=string.ascii_lowercase + string.ascii_uppercase)
    pen_width = vsketch.Param(0.15, 0.05, 2.0, step=0.05, unit="mm")
    margin = vsketch.Param(1.0, 0, 3.0, step=0.2, unit="cm")
    glyph_margin = vsketch.Param(2.0, 0, 3.0, step=0.2, unit="cm")
    glyph_voffset = vsketch.Param(0.0, -2.0, 2.0, step=0.01, unit="cm")

    pitch = vsketch.Param(0.5, 0, 8.0, step=0.025, unit="cm")
    thickness = vsketch.Param(0.1, 0.05, 5.0, step=0.05, unit="cm")

    draw_glyph = vsketch.Param(False)
    fill_glyph = vsketch.Param(False)
    glyph_weight = vsketch.Param(1, 1, 20)
    glyph_chroma = vsketch.Param(False)
    glyph_shadow = vsketch.Param(False)
    glyph_chroma_offset = vsketch.Param(2.0, 0.0, 10.0, step=0.2, unit="mm")
    glyph_chroma_angle = vsketch.Param(30, -180, 180, step=15)
    glyph_space = vsketch.Param(0.0, 0.0, 3.0, step=0.1, unit="mm")
    glyph_space_inside = vsketch.Param(0.0, 0.0, 3.0, step=0.1, unit="mm")
    draw_h_stripes = vsketch.Param(False)
    h_stripes_pitch = vsketch.Param(0.5, 0, 8.0, step=0.025, unit="cm")
    h_stripes_inside = vsketch.Param(False)
    h_stripes_inside_chroma = vsketch.Param(False)
    draw_concentric = vsketch.Param(False)
    concentric_pitch = vsketch.Param(1.0, 0.5, 4.0, step=0.25, unit="mm", decimals=2)
    draw_dots = vsketch.Param(False)
    draw_cut_circles = vsketch.Param(False)
    cut_circles_inside = vsketch.Param(False)
    cut_circle_chroma = vsketch.Param(False)
    draw_dot_matrix = vsketch.Param(False)
    draw_dot_matrix_inside = vsketch.Param(False)
    dot_matrix_pitch = vsketch.Param(0.5, 0.0, 20.0, step=0.1, unit="mm")
    dot_matrix_density = vsketch.Param(0.5, 0.0, 1.0, step=0.05)

    def draw(self, vsk: vsketch.Vsketch) -> None:
        print(os.getcwd())
        vsk.size("a6", landscape=False, center=False)
        vsk.scale(1)
        vsk.penWidth(self.pen_width)

        glyph_poly = load_glyph(self.font, self.glyph, self.face_index)

        # normalize glyph size
        bounds = glyph_poly.bounds
        scale_factor = min(
            (vsk.width - 2 * self.glyph_margin) / (bounds[2] - bounds[0]),
            (vsk.height - 2 * self.glyph_margin) / (bounds[3] - bounds[1]),
        )
        glyph_poly = scale(glyph_poly, scale_factor, scale_factor)
        bounds = glyph_poly.bounds
        glyph_poly = translate(
            glyph_poly,
            vsk.width / 2 - bounds[0] - (bounds[2] - bounds[0]) / 2,
            vsk.height / 2 - bounds[1] - (bounds[3] - bounds[1]) / 2 + self.glyph_voffset,
        )

        if self.draw_glyph:
            vsk.strokeWeight(self.glyph_weight)
            if self.fill_glyph:
                vsk.fill(1)
            vsk.geometry(glyph_poly)

            if self.fill_glyph and self.glyph_chroma:
                angle = self.glyph_chroma_angle / 180.0 * math.pi
                glyph_poly_chroma1 = translate(
                    glyph_poly,
                    -self.glyph_chroma_offset * math.cos(angle),
                    -self.glyph_chroma_offset * math.sin(angle),
                ).difference(glyph_poly)
                glyph_poly_chroma2 = translate(
                    glyph_poly,
                    self.glyph_chroma_offset * math.cos(angle),
                    self.glyph_chroma_offset * math.sin(angle),
                ).difference(glyph_poly)

                vsk.strokeWeight(1)
                vsk.stroke(2)
                vsk.fill(2)
                vsk.geometry(glyph_poly_chroma1)
                vsk.stroke(3)
                vsk.fill(3)
                vsk.geometry(glyph_poly_chroma2)

                glyph_poly = unary_union([glyph_poly, glyph_poly_chroma1, glyph_poly_chroma2])

            vsk.strokeWeight(1)
            vsk.stroke(1)
            vsk.noFill()

        glyph_shadow = None
        if self.glyph_shadow:
            angle = self.glyph_chroma_angle / 180.0 * math.pi
            glyph_shadow = translate(
                glyph_poly,
                self.glyph_chroma_offset * math.cos(angle),
                self.glyph_chroma_offset * math.sin(angle),
            ).difference(glyph_poly)
            vsk.fill(3)
            vsk.stroke(3)
            vsk.geometry(glyph_shadow)
            vsk.noFill()
            vsk.stroke(1)
            glyph_poly = glyph_poly.union(glyph_shadow)

        if self.glyph_weight == 1:
            glyph_poly_ext = glyph_poly.buffer(
                self.glyph_space,
                join_style=JOIN_STYLE.mitre,
            )
            glyph_poly_int = glyph_poly.buffer(
                -self.glyph_space_inside,
                join_style=JOIN_STYLE.mitre,
            )
        else:
            buf_len = (self.glyph_weight - 1) / 2 * self.pen_width
            glyph_poly_ext = glyph_poly.buffer(
                buf_len * 2 + self.glyph_space,
                join_style=JOIN_STYLE.mitre,
            )
            glyph_poly_int = glyph_poly.buffer(
                -buf_len - self.glyph_space_inside,
                join_style=JOIN_STYLE.mitre,
            )

        if glyph_shadow is not None:
            glyph_poly_int = glyph_poly_int.difference(glyph_shadow)

        # horizontal stripes
        if self.draw_h_stripes:
            count = round((vsk.height - 2 * self.margin) / self.h_stripes_pitch)
            corrected_pitch = (vsk.height - 2 * self.margin) / count
            hstripes = MultiLineString(
                [
                    [
                        (self.margin, self.margin + i * corrected_pitch),
                        (vsk.width - self.margin, self.margin + i * corrected_pitch),
                    ]
                    for i in range(count + 1)
                ]
            )

            vsk.geometry(hstripes.difference(glyph_poly_ext))

            if self.h_stripes_inside:
                inside_stripes = translate(hstripes, 0, corrected_pitch / 2).intersection(
                    glyph_poly_int
                )
                vsk.geometry(inside_stripes)

                if self.h_stripes_inside_chroma:
                    chroma_offset = math.sqrt(2) * self.pen_width
                    vsk.stroke(2)
                    vsk.geometry(translate(inside_stripes, -chroma_offset, -chroma_offset))
                    vsk.stroke(3)
                    vsk.geometry(translate(inside_stripes, chroma_offset, chroma_offset))
                    vsk.stroke(1)

        # concentric
        if self.draw_concentric:
            circle_count = int(
                math.ceil(math.hypot(vsk.width, vsk.height) / 2 / self.concentric_pitch)
            )
            circles = unary_union(
                [
                    Point(vsk.width / 2, vsk.height / 2)
                    .buffer(
                        (i + 1) * self.concentric_pitch,
                        resolution=int(1 * (i + 1) * self.concentric_pitch),
                    )
                    .exterior
                    for i in range(circle_count)
                ]
            )
            vsk.geometry(
                circles.difference(glyph_poly_ext).intersection(
                    box(
                        self.margin,
                        self.margin,
                        vsk.width - self.margin,
                        vsk.height - self.margin,
                    )
                )
            )

        # dots
        vsk.fill(1)
        if self.draw_dots or self.draw_cut_circles:
            v_pitch = self.pitch * math.tan(math.pi / 3) / 2
            h_count = int((vsk.width - 2 * self.margin) // self.pitch)
            v_count = int((vsk.height - 2 * self.margin) // v_pitch)
            h_offset = (vsk.width - h_count * self.pitch) / 2
            v_offset = (vsk.height - v_count * v_pitch) / 2

            dot_array = []
            for j in range(v_count + 1):
                odd_line = j % 2 == 1
                for i in range(h_count + (0 if odd_line else 1)):
                    dot = Point(
                        h_offset + i * self.pitch + (self.pitch / 2 if odd_line else 0),
                        v_offset + j * v_pitch,
                    ).buffer(self.thickness / 2)

                    if self.draw_dots:
                        if not dot.buffer(self.thickness / 2).intersects(glyph_poly_ext):
                            dot_array.append(dot)
                    else:
                        dot_array.append(dot)

            dots = unary_union(dot_array)

            if self.draw_dots:
                vsk.geometry(dots)

            if self.draw_cut_circles:
                if self.cut_circles_inside:
                    op_func = lambda geom: geom.intersection(glyph_poly_int)
                else:
                    op_func = lambda geom: geom.difference(glyph_poly_ext)

                vsk.geometry(op_func(dots))

                if self.cut_circle_chroma:
                    angle = math.pi / 6
                    dist = self.pitch * 0.1
                    vsk.fill(2)
                    vsk.stroke(2)
                    vsk.geometry(
                        op_func(
                            translate(
                                dots, -dist * math.cos(angle), -dist * math.sin(angle)
                            ).difference(dots)
                        )
                    )
                    vsk.fill(3)
                    vsk.stroke(3)
                    vsk.geometry(
                        op_func(
                            translate(
                                dots, dist * math.cos(angle), dist * math.sin(angle)
                            ).difference(dots)
                        )
                    )
                    vsk.fill(1)
                    vsk.stroke(1)

        vsk.stroke(4)  # apply line sort, see finalize()
        if self.draw_dot_matrix:
            h_count = int((vsk.width - 2 * self.margin) // self.dot_matrix_pitch) + 1
            v_count = int((vsk.height - 2 * self.margin) // self.dot_matrix_pitch) + 1
            h_pitch = (vsk.width - 2 * self.margin) / (h_count - 1)
            v_pitch = (vsk.height - 2 * self.margin) / (v_count - 1)

            mp = MultiPoint(
                [
                    (self.margin + i * h_pitch, self.margin + j * v_pitch)
                    for i, j in itertools.product(range(h_count), range(v_count))
                    if vsk.random(1) < self.dot_matrix_density
                ]
            )

            if self.draw_dot_matrix_inside:
                mp = mp.intersection(glyph_poly_int)
            else:
                mp = mp.difference(glyph_poly_ext)

            vsk.geometry(mp)
            vsk.vpype("color -l4 black")

        vsk.vpype("color -l1 black color -l2 cyan color -l3 magenta")

    def finalize(self, vsk: vsketch.Vsketch) -> None:
        vsk.vpype("linemerge linesimplify -t 0.01mm reloop linesort -l 4 lmove 4 1")


if __name__ == "__main__":
    MachineTypographySketch.display()
