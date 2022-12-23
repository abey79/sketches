"""This is part of the Automatic #plotloop Machine project.

Details: https://bylr.info/articles/2022/12/22/automatic-plotloop-machine/
"""

from __future__ import annotations

import json
import math
import pathlib
import warnings

import numpy as np
import vpype as vp
import vsketch
from shapely.errors import ShapelyDeprecationWarning as shapely_warning
from shapely.geometry import LinearRing, MultiLineString, Polygon, shape
from shapely.ops import unary_union

warnings.filterwarnings("ignore", category=shapely_warning)


# downloaded from: https://hub.arcgis.com/datasets/esri::world-countries-generalized/about
DATA_FILE = pathlib.Path(__file__).parent / "World_Countries_(Generalized).geojson"


def polygon_area(lats, lons, radius=6378137):
    """
    Computes area of spherical polygon, assuming spherical Earth.
    Returns result in ratio of the sphere's area if the radius is specified.
    Otherwise, in the units of provided radius.
    lats and lons are in degrees.

    From: https://stackoverflow.com/a/61177081/229511
    """
    # Line integral based on Green's Theorem, assumes spherical Earth

    # close polygon
    if lats[0] != lats[-1]:
        lats = np.append(lats, lats[0])
        lons = np.append(lons, lons[0])

    # colatitudes relative to (0,0)
    a = np.sin(lats / 2) ** 2 + np.cos(lats) * np.sin(lons / 2) ** 2
    colat = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))

    # azimuths relative to (0,0)
    az = np.arctan2(np.cos(lats) * np.sin(lons), np.sin(lats)) % (2 * np.pi)

    # Calculate diffs
    # daz = diff(az) % (2*pi)
    daz = np.diff(az)
    daz = (daz + np.pi) % (2 * np.pi) - np.pi

    deltas = np.diff(colat) / 2
    colat = colat[0:-1] + deltas

    # Perform integral
    integrands = (1 - np.cos(colat)) * daz

    # Integrate
    area = np.abs(np.sum(integrands)) / (4 * np.pi)

    area = min(area, 1 - area)
    if radius is not None:  # return in units of radius
        return area * 4 * np.pi * radius**2
    else:  # return in ratio of sphere total area
        return area


def project_polygon(p: Polygon) -> np.ndarray | None:
    coords = np.array(p.exterior.coords)
    vectors = np.zeros(shape=(len(coords), 3))

    lats = np.deg2rad(coords[:, 1])
    lons = np.deg2rad(coords[:, 0])

    if polygon_area(lats, lons) < 1000000000:
        return None

    # apply latitude
    vectors[:, 0] = np.cos(lats)
    vectors[:, 2] = np.sin(lats)

    # apply longitude
    sin_lons = np.sin(lons)
    cos_lons = np.cos(lons)
    vectors_final = np.empty_like(vectors)
    vectors_final[:, 0] = cos_lons * vectors[:, 0] - sin_lons * vectors[:, 1]
    vectors_final[:, 1] = sin_lons * vectors[:, 0] + cos_lons * vectors[:, 1]
    vectors_final[:, 2] = vectors[:, 2]

    return vectors_final


def build_world() -> list[np.ndarray]:
    with open(DATA_FILE) as fp:
        data = json.load(fp)

    # This is a bit of a hack to handle antartica. Because the polygon would be
    # self-intersecting, in lat/lon coordinates, the data file closed it with a line at ~88°S,
    # which generated an ugly artifact. So we manually close the polygon and handle it
    # separately to deal with the self-intersection.
    antartica = data["features"][24]["geometry"]["coordinates"].pop(0)
    mls = unary_union([LinearRing(antartica[0][7:12247])])

    world = unary_union(
        [Polygon(ls) for ls in mls.geoms if len(ls.coords) > 2]
        + [shape(country["geometry"]) for country in data["features"]]
    )

    lines = []
    for p in world.geoms:
        projected = project_polygon(p)
        if projected is not None:
            lines.append(projected)

    return lines


LINES = build_world()


def _interpolate_crop(
    start: np.ndarray, stop: np.ndarray, loc: float, axis: int
) -> np.ndarray:
    """Interpolate between two points at a given coordinates."""

    start_dim, stop_dim = start[axis], stop[axis]

    diff = stop_dim - start_dim
    if diff == 0:
        raise ValueError("cannot interpolate line parallel to axis")

    r = (loc - start_dim) / diff

    if r < 0.5:
        return start + (stop - start) * r
    else:
        return stop - (stop - start) * (1.0 - r)


def crop_half_plane(
    line: np.ndarray, loc: float, axis: int, keep_smaller: bool
) -> list[np.ndarray]:
    """Adapted from vpype.crop_half_plane to support NxM array (lines of N M-dimensional
    points)"""

    if axis not in range(line.shape[0]):
        raise ValueError(f"invalid crop axis {axis}")

    if keep_smaller:
        outside = line[:, axis] > loc
    else:
        outside = line[:, axis] < loc

    if np.all(outside):
        return []
    elif np.all(~outside):
        return [line]

    diff = np.diff(outside.astype(int))
    (start_idx,) = np.nonzero(diff == -1)
    (stop_idx,) = np.nonzero(diff == 1)

    # The following properties are expected after normalization:
    #   - len(start_idx) == len(stop_idx)
    #   - (start_idx, stop_idx) are streak of points that must be kept
    #   - start_idx == -1 means beginning of line in not to be cropped
    #   - stop_idx == inf means end of line is not to be cropped
    inf = len(line)
    if len(start_idx) == 0:
        start_idx = np.array([-1])
    if len(stop_idx) == 0:
        stop_idx = np.array([inf])
    if start_idx[0] > stop_idx[0]:
        start_idx = np.hstack([-1, start_idx])
    if stop_idx[-1] < start_idx[-1]:
        stop_idx = np.hstack([stop_idx, inf])

    line_arr = []
    for start, stop in zip(start_idx, stop_idx):
        if start == -1:
            sub_line = np.vstack(
                [
                    line[: stop + 1],
                    _interpolate_crop(line[stop], line[stop + 1], loc, axis).reshape(1, -1),
                ]
            )
        elif stop == inf:
            sub_line = np.vstack(
                [
                    _interpolate_crop(line[start], line[start + 1], loc, axis).reshape(1, -1),
                    line[start + 1 :],
                ]
            )
        else:
            sub_line = np.vstack(
                [
                    _interpolate_crop(line[start], line[start + 1], loc, axis).reshape(1, -1),
                    line[start + 1 : stop + 1],
                    _interpolate_crop(line[stop], line[stop + 1], loc, axis).reshape(1, -1),
                ]
            )

        # check cases where coordinate lie on threshold
        sub_start = 1 if np.all(sub_line[0] == sub_line[1]) else 0
        sub_stop = (
            (len(sub_line) - 1) if np.all(sub_line[-1] == sub_line[-2]) else len(sub_line)
        )
        if sub_stop >= sub_start + 2:
            line_arr.append(sub_line[sub_start:sub_stop])

    return line_arr


class WorldSketch(vsketch.SketchClass):
    # Sketch parameters:
    mode = vsketch.Param("frame", choices=["manual", "frame"])
    rot_x = vsketch.Param(0, step=5)
    rot_y = vsketch.Param(0, step=5)
    rot_z = vsketch.Param(0, step=5)
    frame = vsketch.Param(0)
    frame_count = vsketch.Param(200)
    circle = vsketch.Param(True)
    crop_depth = vsketch.Param(0.0, step=0.01, decimals=2)
    pixelize = vsketch.Param(False)
    pen_width = vsketch.Param(0.5, unit="mm", step=0.05)

    def draw(self, vsk: vsketch.Vsketch) -> None:
        vsk.size("5x5cm", landscape=False, center=False)

        vsk.scale("2cm")
        vsk.translate(1.25, 1.25)

        if self.mode == "manual":
            rot_x_angle, rot_y_angle, rot_z_angle = self.rot_x, self.rot_y, self.rot_z
        elif self.mode == "frame":
            # begin and end at home (Lausanne, Switzerland)
            start_z = -6.6
            start_y = 46.5

            rot_x_angle = 360 * self.frame / self.frame_count
            # rot_y_angle = 720 * self.frame / self.frame_count
            rot_y_angle = start_y + math.sin(self.frame / self.frame_count * 2 * math.pi) * 360
            rot_z_angle = start_z + 2 * 360 * self.frame / self.frame_count
        else:
            raise ValueError(f"unknown mode {self.mode}")

        rot_x = np.array(
            [
                (1, 0, 0),
                (0, math.cos(math.radians(rot_x_angle)), -math.sin(math.radians(rot_x_angle))),
                (0, math.sin(math.radians(rot_x_angle)), math.cos(math.radians(rot_x_angle))),
            ]
        )
        rot_y = np.array(
            [
                (math.cos(math.radians(rot_y_angle)), 0, math.sin(math.radians(rot_y_angle))),
                (0, 1, 0),
                (-math.sin(math.radians(rot_y_angle)), 0, math.cos(math.radians(rot_y_angle))),
            ]
        )
        rot_z = np.array(
            [
                (math.cos(math.radians(rot_z_angle)), -math.sin(math.radians(rot_z_angle)), 0),
                (math.sin(math.radians(rot_z_angle)), math.cos(math.radians(rot_z_angle)), 0),
                (0, 0, 1),
            ]
        )
        rot = rot_x @ rot_y @ rot_z

        for line in LINES:

            rotated_line = (rot @ line.T).T

            for cropped_line in crop_half_plane(
                rotated_line, self.crop_depth, axis=0, keep_smaller=False
            ):
                vsk.polygon(cropped_line[:, 1], -cropped_line[:, 2])

        if self.circle:
            vsk.circle(0, 0, radius=1)
            if self.pixelize:
                # thicken the circle for a better pixelated look
                vsk.circle(0, 0, radius=1 + self.pen_width / vp.convert_length("2cm") / 9)

        if self.pixelize:
            vsk.vpype(
                f"pixelize --mode snake --pen-width {self.pen_width} "
                f"linemerge --tolerance {self.pen_width + 0.1}"
            )
        else:
            vsk.vpype("linesimplify -t 0.07mm")

    def finalize(self, vsk: vsketch.Vsketch) -> None:
        if self.pixelize:
            vsk.vpype("linesort")
        else:
            vsk.vpype("reloop linesort")


if __name__ == "__main__":
    WorldSketch.display()
