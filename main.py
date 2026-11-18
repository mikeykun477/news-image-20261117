"""Hand over the finished front page for Tuesday 17 November 2026.

This is the whole entry program. It does one small job and nothing else:
take the pre-built ``entry.png`` that lives next to this file and place an
exact copy of it in the output folder, so the judging harness can pick it
up. The picture itself is composed ahead of time (see ``compose.py``);
nothing here draws, downloads, or edits anything.

Where the copy lands comes from the ``MAKEFUN_OUTPUT_DIR`` environment
variable. When that variable is absent or blank, the copy goes to a
folder called ``output`` beside this file. The folder is created when it
does not already exist. A copy that would exceed one mebibyte is refused
with an error rather than delivered half-checked, so an oversized page
can never slip through silently.

Only the Python standard library is used, and running the program twice
writes the same bytes twice.
"""

import os
import shutil

from pathlib import Path

ONE_MEBIBYTE = 1024 * 1024
PICTURE_NAME = "entry.png"
OUTPUT_ENV_VAR = "MAKEFUN_OUTPUT_DIR"
DEFAULT_FOLDER_NAME = "output"


def _target_folder():
    """Work out where the finished picture should be delivered."""
    requested = os.environ.get(OUTPUT_ENV_VAR, "").strip()
    if requested:
        return Path(requested)
    here = Path(__file__).resolve().parent
    return here / DEFAULT_FOLDER_NAME


def _picture_beside_program():
    """Locate the pre-built front page sitting next to this file."""
    return Path(__file__).resolve().parent / PICTURE_NAME


def _refuse_oversized(picture):
    """Raise instead of delivering a picture bigger than one mebibyte."""
    size = picture.stat().st_size
    if size > ONE_MEBIBYTE:
        raise ValueError(
            f"{PICTURE_NAME} is {size} bytes, over the "
            f"{ONE_MEBIBYTE}-byte limit"
        )


def _deliver_copy():
    """Copy the front page into the output folder and report where."""
    picture = _picture_beside_program()
    _refuse_oversized(picture)
    folder = _target_folder()
    folder.mkdir(parents=True, exist_ok=True)
    destination = folder / PICTURE_NAME
    shutil.copyfile(picture, destination)
    _refuse_oversized(destination)
    print(f"Wrote {destination}")


if __name__ == "__main__":
    _deliver_copy()
