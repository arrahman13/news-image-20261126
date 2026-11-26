#!/usr/bin/env python3
"""Entrypoint for the news-image-20261126 v2 entry.

Copies the committed entry.png to the output directory and nothing else.
Uses only the standard library. Verifies the copied file against the
committed SHA-256 before writing it out, so a tampered or stale image
can never be graded.
"""

import hashlib
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ENTRY_PNG = os.path.join(HERE, "entry.png")

# SHA-256 of the committed entry.png. Updated whenever entry.png changes.
EXPECTED_SHA256 = "b90083ac3c095780bdf9aa8bf598b7729475fc4e876903d5e6f66b9014e76f61"


def main() -> int:
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)

    with open(ENTRY_PNG, "rb") as f:
        data = f.read()

    digest = hashlib.sha256(data).hexdigest()
    if digest != EXPECTED_SHA256:
        print(
            "entry.png SHA-256 mismatch: got %s, expected %s"
            % (digest, EXPECTED_SHA256),
            file=sys.stderr,
        )
        return 1

    dest = os.path.join(out_dir, "entry.png")
    with open(dest, "wb") as f:
        f.write(data)

    # Double-check what landed on disk matches the committed image.
    with open(dest, "rb") as f:
        if hashlib.sha256(f.read()).hexdigest() != EXPECTED_SHA256:
            print("output verification failed", file=sys.stderr)
            return 1

    print("wrote %s (%d bytes, sha256 %s)" % (dest, len(data), digest))
    return 0


if __name__ == "__main__":
    sys.exit(main())
