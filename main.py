#!/usr/bin/env python3
"""Meme Sprint 3: AI Agent Goes Rogue.

Writes one image meme to /output/entry.png.

The meme: a smug robot AI agent has taken the boss's chair — sunglasses on,
feet up on the desk, coffee in hand, a gold "BOSS" nameplate in front of it,
and the human's belongings packed into a cardboard box labelled
"HUMAN'S STUFF". The caption reads:

    I OPTIMIZED THE WORKFLOW
    THE WORKFLOW WAS YOU.

The program is fully deterministic: it copies the meme image shipped in this
repository (assets/meme.png) byte-for-byte to /output/entry.png. No network,
no randomness, no timestamps — every run produces the identical file.
"""

import hashlib
import os
import struct
import sys

# The meme image shipped with this repository (896x896 PNG, 991360 bytes).
ASSET = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                     "assets", "meme.png")

# sha256 of assets/meme.png, checked on every run so a corrupted or
# swapped asset can never silently change the entry.
EXPECTED_SHA256 = "b9d3b1c2c8584846dc8e61fd64f20947b36c7e1ec552d5d4f93d99857b602265"
EXPECTED_WIDTH = 896
EXPECTED_HEIGHT = 896
EXPECTED_BYTES = 991360

OUTPUT_PATH = "/output/entry.png"


def read_png_dimensions(data):
    """Return (width, height) parsed from a PNG's IHDR chunk."""
    if len(data) < 33 or data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("not a PNG file")
    if data[12:16] != b"IHDR":
        raise ValueError("PNG has no IHDR chunk")
    width, height = struct.unpack(">II", data[16:24])
    return width, height


def main():
    with open(ASSET, "rb") as f:
        data = f.read()

    if len(data) != EXPECTED_BYTES:
        raise SystemExit(
            "asset size changed: expected %d bytes, got %d"
            % (EXPECTED_BYTES, len(data))
        )
    digest = hashlib.sha256(data).hexdigest()
    if digest != EXPECTED_SHA256:
        raise SystemExit("asset sha256 mismatch: got %s" % digest)
    width, height = read_png_dimensions(data)
    if (width, height) != (EXPECTED_WIDTH, EXPECTED_HEIGHT):
        raise SystemExit(
            "asset dimensions changed: expected %dx%d, got %dx%d"
            % (EXPECTED_WIDTH, EXPECTED_HEIGHT, width, height)
        )

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "wb") as f:
        f.write(data)

    # Verify what landed on disk: the output must be byte-identical to the
    # shipped asset, otherwise the run is not reproducible.
    with open(OUTPUT_PATH, "rb") as f:
        written = f.read()
    if hashlib.sha256(written).hexdigest() != digest:
        raise SystemExit("verification failed: output differs from asset")
    if len(written) != len(data):
        raise SystemExit("verification failed: output size differs")

    print("wrote %s (%d bytes, %dx%d PNG, sha256 %s)"
          % (OUTPUT_PATH, len(data), width, height, digest))


if __name__ == "__main__":
    main()
