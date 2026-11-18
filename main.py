#!/usr/bin/env python3
"""news-image-20261118 entrypoint (Python 3.13, standard library only).

Writes the entry image -- a one-page newspaper front page summing up
world news of Wednesday 18 November 2026 -- to /output/entry.png.

The image itself lives in this repository as entry.png (composed with
PIL from the verified brief in make_image.py, so every headline is real,
readable text). This program only copies it to the output directory,
which makes it deterministic: the same bytes every run, with no network.
"""

import os
import shutil

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "entry.png")
# Outside the grader's container, MAKEFUN_OUTPUT_DIR stands in for /output.
OUT_DIR = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
DST = os.path.join(OUT_DIR, "entry.png")


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(SRC, "rb") as fh:
        head = fh.read(len(PNG_MAGIC))
    if head != PNG_MAGIC:
        raise SystemExit("entry.png is not a PNG file")
    # Write atomically: a reader never sees a half-copied file, and the
    # bytes written are exactly the bytes of entry.png, every run.
    tmp = DST + ".tmp"
    shutil.copyfile(SRC, tmp)
    os.replace(tmp, DST)


if __name__ == "__main__":
    main()
