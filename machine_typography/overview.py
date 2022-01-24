"""Generate/displays an overview of the Machine Typography project.

Usage:

    python overview.py
"""

import os
import re
import tempfile
from pathlib import Path
from typing import Optional

import multiprocess

TEMP_DIR_OBJECT = tempfile.TemporaryDirectory()
TEMP_DIR = Path(TEMP_DIR_OBJECT.name)
OUTPUT_DIR = Path(__file__).parent / "output"
CONFIG_DIR = Path(__file__).parent / "config"


def get_config(letter_id: int) -> Optional[str]:
    search_re = re.compile(str(r"^" + f"{letter_id:02}" + r"(_\d*)?.json"))

    for file in sorted(CONFIG_DIR.glob("*.json"), key=os.path.getmtime, reverse=True):
        if search_re.fullmatch(file.name) is not None:
            return str(file)

    return None


def run_export(letter_id: int, temp_dir: str):
    os.system(
        f"vsk save --name {str(letter_id)} --config {get_config(letter_id)} "
        f"--destination {temp_dir}"
    )


if __name__ == "__main__":
    with multiprocess.Pool(9) as p:
        p.map(lambda i: run_export(i, str(TEMP_DIR)), list(range(1, 18)))

    os.system(
        "vpype "
        f"read {TEMP_DIR / '8.svg'} "
        "translate -- -105mm 0 "
        f"read {TEMP_DIR / '9.svg'} "
        "translate -- -105mm 0 "
        f"read {TEMP_DIR / '10.svg'} "
        "translate -- -105mm 0 "
        f"read {TEMP_DIR / '11.svg'} "
        "translate -- -105mm 0 "
        f"read {TEMP_DIR / '12.svg'} "
        "translate -- -105mm 0 "
        f"read {TEMP_DIR / '13.svg'} "
        "translate -- -105mm 0 "
        f"read {TEMP_DIR / '14.svg'} "
        "translate -- -105mm 0 "
        f"read {TEMP_DIR / '15.svg'} "
        "translate -- -105mm 0 "
        f"read {TEMP_DIR / '16.svg'} "
        "translate -- -105mm 0 "
        f"read {TEMP_DIR / '17.svg'} "
        "translate 735mm 147mm "
        f"read {TEMP_DIR / '1.svg'} "
        "translate -- -105mm 0 "
        f"read {TEMP_DIR / '2.svg'} "
        "translate -- -105mm 0 "
        f"read {TEMP_DIR / '3.svg'} "
        "translate -- -105mm 0 "
        f"read {TEMP_DIR / '4.svg'} "
        "translate -- -105mm 0 "
        f"read {TEMP_DIR / '5.svg'} "
        "translate -- -105mm 0 "
        f"read {TEMP_DIR / '6.svg'} "
        "translate -- -105mm 0 "
        f"read {TEMP_DIR / '7.svg'} "
        "layout --landscape 1050x294mm "
        "color -l1 black color -l2 cyan color -l3 magenta "
        "show "
        f"write {OUTPUT_DIR}/combined_output.svg"
    )
