#!/usr/bin/env python3
"""Entrypoint for the news-image-20261126 entry.

Copies the committed entry.png to the grader's output directory.
Standard library only. The SHA-256 of entry.png is verified against the
hash embedded below before copying, so the grader always sees exactly
the bytes that were committed. This program never renders anything:
the image was rendered once, locally, by build_image.py, and is
shipped as a file.
"""

import hashlib
import os
import shutil
import sys
from pathlib import Path

# SHA-256 of the committed entry.png. The copy refuses to run on a
# mismatch, so the grader always sees exactly the committed bytes.
ENTRY_SHA256 = "4904979f4f2c74a697d8215be55042b0a167f5b893b71003432d01b6a575d514"
ENTRY_NAME = "entry.png"


def main() -> int:
    here = Path(__file__).resolve().parent
    src = here / ENTRY_NAME
    data = src.read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    if digest != ENTRY_SHA256:
        print(
            "entry.png sha256 mismatch: got %s, expected %s" % (digest, ENTRY_SHA256),
            file=sys.stderr,
        )
        return 1
    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    out_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, out_dir / ENTRY_NAME)
    print("copied %s (%d bytes, sha256 %s) to %s" % (ENTRY_NAME, len(data), digest, out_dir))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
