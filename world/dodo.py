"""This is part of the Automatic #plotloop Machine project.

Details: https://bylr.info/articles/2022/12/22/automatic-plotloop-machine/
"""

# requirements:
# - imagemagick
# - axicli
# - librsvg (rsvg-convert)

import pathlib

# parameters
PAPER_ROLL_DISTANCE = 6
EV_CORRECTION = 1
FRAME_COUNT = 280
PIXELIZE = False

PROJECT_NAME = "world"
BASENAME = f"{PROJECT_NAME}_frame_count_{FRAME_COUNT}_pixelize_{PIXELIZE}"

PROJECT_DIR = pathlib.Path(__file__).parent
VPYPE = PROJECT_DIR.parent / "venv/bin/vpype"
AXICLI = f"ssh axidraw.local /home/pi/src/taxi/venv/bin/axicli -L 2 -d 37 -u 60 -N"
CAMPI_SERVER = "http://campi.local:8000"


class FileSpec:
    def __init__(self, frame: int):
        self.frame = frame
        directory = PROJECT_DIR / "output"

        # vsketch doesn't add zero padding to frame number
        self.source = directory / (BASENAME + f"_frame_{self.frame}.svg")

        # for the other file we add the zero padding to keep the order with CLI tools
        base_frame = BASENAME + f"_frame_{self.frame:04d}"
        self.simulated = directory / (base_frame + "_simulated.jpg")
        self.plotted = directory / (base_frame + "_plotted.jpg")
        self.postprocessed = directory / (base_frame + "_postprocessed.jpg")


FILE_SPECS = {i: FileSpec(i) for i in range(1, FRAME_COUNT + 1)}


def task_generate():
    """Generates golden master SVGs from the list of input files."""
    return {
        "actions": [
            (
                f"vsk save -n {PROJECT_NAME} -p frame_count {FRAME_COUNT} "
                f"-p pixelize {PIXELIZE} -p frame 1..{FRAME_COUNT} -m ."
            )
        ],
        "file_dep": [PROJECT_DIR / f"sketch_{PROJECT_NAME}.py"],
        "targets": list(spec.source for spec in FILE_SPECS.values()),
        "clean": True,
    }


# -----------------------------------------------------------------------
# simulation tasks


def task_simframe():
    """Simulate a frame."""
    for frame, spec in FILE_SPECS.items():
        yield {
            "name": f"{frame:04d}",
            "actions": [
                # f"convert {spec.source} -scale 200x200 {spec.simulated}",
                f"rsvg-convert -b white -h 200 {spec.source} > {spec.simulated}",
            ],
            "file_dep": [spec.source],
            "targets": [spec.simulated],
            "clean": True,
        }


def task_simulate():
    """Make the simulated animation."""
    file_list = [spec.simulated for spec in FILE_SPECS.values()]
    paths = " ".join(str(file) for file in file_list)
    target = PROJECT_DIR / "output" / f"{BASENAME}.gif"
    return {
        "actions": [f"convert -delay 5 -loop 0 {paths} {target}"],
        "file_dep": file_list,
        "targets": [target],
        "clean": True,
    }


# -----------------------------------------------------------------------
# plotting tasks


def task_plot():
    """Plot the plotter-ready SVGs."""
    for frame, spec in FILE_SPECS.items():
        yield {
            "name": f"{frame:04d}",
            "actions": [
                f"cat {spec.source} | {AXICLI} -m plot",
                f"{AXICLI} -m manual -M walk_y --walk_dist -3",
                f"curl -s --output {spec.plotted} {CAMPI_SERVER}/img/?ev={EV_CORRECTION}",
                f"{AXICLI} -m manual -M walk_y --walk_dist 3",
                f"curl -s --output /dev/null {CAMPI_SERVER}/motor/{PAPER_ROLL_DISTANCE}",
            ],
            "file_dep": [spec.source],
            "targets": [spec.plotted],
            "clean": True,
        }


def task_postprocess():
    """Post-process the plotted images."""
    for frame, spec in FILE_SPECS.items():
        yield {
            "name": f"{frame:04d}",
            "actions": [
                (
                    f"convert '{spec.plotted}' -rotate 270 -crop 1900x1900+605+785 "
                    f"-colorspace Gray"
                    f" -brightness-contrast 5x15 '{spec.postprocessed}'"
                )
            ],
            "file_dep": [spec.plotted],
            "targets": [spec.postprocessed],
            "clean": True,
        }


def task_animation():
    """Make the animation."""
    file_list = [spec.postprocessed for spec in FILE_SPECS.values()]
    paths = " ".join(str(file) for file in file_list)
    target = PROJECT_DIR / "output" / f"{BASENAME}_final.gif"
    return {
        "actions": [f"convert -resize 28%% -delay 5 -loop 0 {paths} {target}"],
        "file_dep": file_list,
        "targets": [target],
        "clean": True,
    }


# -----------------------------------------------------------------------
# convenience tasks


def task_toggle():
    """Toggle pen up/down"""
    return {"actions": [f"{AXICLI} -m toggle"]}


def task_disable_xy():
    """Disable X/Y motors"""
    return {"actions": [f"{AXICLI} -m manual -M disable_xy"]}


def task_shutdown():
    """Shutdown everything"""
    return {
        "actions": [
            "ssh campi.local sudo poweroff",
            "ssh axidraw.local sudo poweroff",
        ],
        "task_dep": ["disable_xy"],
    }
