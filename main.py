#!/usr/bin/env python3
"""news-image-20261117 entry (Python 3.13, standard library only).

The image is the entry.png beside this file: a newspaper front page summing
up the world's news of Tuesday 17 November 2026. The program copies it to
/output/entry.png. No network, no randomness: two runs write the same bytes.

Outside the grader's container, MAKEFUN_OUTPUT_DIR stands in for /output:
    mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
"""

import os
import shutil
from pathlib import Path

OUTPUT_NAME = "entry.png"


def main() -> None:
    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    out_dir.mkdir(parents=True, exist_ok=True)
    src = Path(__file__).resolve().parent / OUTPUT_NAME
    if not src.is_file():
        raise FileNotFoundError(f"missing image beside main.py: {src}")
    dest = out_dir / OUTPUT_NAME
    shutil.copyfile(src, dest)
    # The gate caps the image at 1 MiB; fail loudly rather than submit a
    # file the gate would refuse.
    if dest.stat().st_size > 1_048_576:
        raise ValueError(f"entry image is {dest.stat().st_size} bytes, over 1 MiB")


if __name__ == "__main__":
    main()
