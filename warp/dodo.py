# doit script

import dataclasses
import pathlib

CUR_DIR = pathlib.Path(__file__).parent

PAPER_ROLL_DIST = 6
EV = 1

VPYPE = CUR_DIR.parent / "venv/bin/vpype"

AXICLI = f"ssh axidraw.local /home/pi/src/taxi/venv/bin/axicli -L 2 -d 37 -u 60 -N"
CAMPI_SERVER = "http://campi.local:8000"

FRAMES = range(1, 201)
SOURCE_TEMPLATE = "output/warp_frame_count_200_frame_{}.svg"


@dataclasses.dataclass()
class FileSpec:
    source: pathlib.Path
    plotted: pathlib.Path = dataclasses.field(init=False)
    postprocessed: pathlib.Path = dataclasses.field(init=False)

    def __post_init__(self):
        self.plotted = self.source.with_name(self.source.stem + "_plotted.jpg")
        self.postprocessed = self.plotted.with_name(self.plotted.stem + "_postprocessed.jpg")


FILE_SPECS = {i: FileSpec(pathlib.Path(SOURCE_TEMPLATE.format(i))) for i in FRAMES}


def task_toggle():
    return {"actions": [f"{AXICLI} -m toggle"]}


def task_disable_xy():
    return {"actions": [f"{AXICLI} -m manual -M disable_xy"]}


def task_generate():
    """Generates golden master SVGs from the list of input files."""
    return {
        "actions": ["vsk save -n warp -p frame_count 200 -p frame 1..200 -m ."],
        "file_dep": [CUR_DIR / "sketch_warp.py", __file__],
        "targets": list(spec.source for spec in FILE_SPECS.values()),
    }


def task_plot():
    """Plot the plotter-ready SVGs."""
    for frame, spec in FILE_SPECS.items():
        yield {
            "name": f"{frame:04d}",
            "actions": [
                f"cat {spec.source} | {AXICLI} -m plot",
                f"{AXICLI} -m manual -M walk_y --walk_dist -3",
                f"curl -s --output {spec.plotted} {CAMPI_SERVER}/img/?ev={EV}",
                f"{AXICLI} -m manual -M walk_y --walk_dist 3",
                f"curl -s --output /dev/null {CAMPI_SERVER}/motor/{PAPER_ROLL_DIST}",
            ],
            "file_dep": [spec.source],
            "targets": [spec.plotted],
        }


def task_plotsim():
    """Simulate plotting."""
    for frame, spec in FILE_SPECS.items():
        yield {
            "name": f"{frame:04d}",
            "actions": [
                f"convert {spec.source} -scale 200x200 {spec.postprocessed}",
            ],
            "file_dep": [spec.source, __file__],
        }


def task_postprocess():
    """Post-process the plotted images."""
    for frame, spec in FILE_SPECS.items():
        yield {
            "name": f"{frame:04d}",
            "actions": [
                (
                    f"convert '{spec.plotted}' -crop 1700x1700+878+584 -colorspace Gray "
                    f"-brightness-contrast 5x15 '{spec.postprocessed}'"
                )
            ],
            "file_dep": [spec.plotted, __file__],
            "targets": [spec.postprocessed],
        }
