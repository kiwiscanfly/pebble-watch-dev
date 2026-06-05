#!/usr/bin/env python3
"""
Capture an animated GIF preview of the watchface from a running emulator.

Grabs N screenshots a fixed delay apart and stitches them into a looping GIF —
useful for an animated face, an App Store rollover, or documenting a change.

Usage:
    python3 scripts/create_preview_gif.py [--platform emery] [--frames 8] [--delay 400]

Options:
    --platform NAME   Emulator platform (default: emery; e.g. gabbro)
    --frames N        Number of frames to capture (default: 8)
    --delay MS        Wall-clock delay between captures, ms (default: 400)
    --out PATH        Output GIF path (default: preview_<platform>.gif)

Requires: Pillow (`pip3 install Pillow`) and a running emulator
(`pebble install --emulator <platform>`).
"""

import argparse
import subprocess
import sys
import tempfile
import time
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    sys.exit("Pillow is required: pip3 install Pillow")


def emulator_running(platform):
    """A quick screenshot to /dev/null succeeds only if the emulator is up."""
    probe = subprocess.run(
        ["pebble", "screenshot", "--no-open", "--emulator", platform, "/dev/null"],
        capture_output=True, text=True)
    return probe.returncode == 0


def capture_frames(platform, count, delay_ms, tmp):
    frames = []
    for i in range(count):
        path = tmp / f"frame_{i:03d}.png"
        result = subprocess.run(
            ["pebble", "screenshot", "--no-open", "--emulator", platform, str(path)],
            capture_output=True, text=True)
        if result.returncode == 0 and path.exists():
            frames.append(Image.open(path).copy())
            print(f"  captured frame {i + 1}/{count}", end="\r")
        else:
            print(f"\n  warning: frame {i} failed: {result.stderr.strip()}")
        time.sleep(delay_ms / 1000.0)
    print()
    return frames


def main():
    ap = argparse.ArgumentParser(description="Capture an animated GIF of the watchface")
    ap.add_argument("--platform", default="emery")
    ap.add_argument("--frames", type=int, default=8)
    ap.add_argument("--delay", type=int, default=400)
    ap.add_argument("--out")
    args = ap.parse_args()

    if not emulator_running(args.platform):
        sys.exit(f"Emulator '{args.platform}' is not running. "
                 f"Start it with: pebble install --emulator {args.platform}")

    out = Path(args.out or f"preview_{args.platform}.gif")
    print(f"Capturing {args.frames} frames from {args.platform} "
          f"({args.delay}ms apart)...")

    with tempfile.TemporaryDirectory() as td:
        frames = capture_frames(args.platform, args.frames, args.delay, Path(td))

    if not frames:
        sys.exit("No frames captured — is the watchface installed and rendering?")

    # GIF frame duration mirrors the capture cadence so playback matches reality.
    frames[0].save(out, save_all=True, append_images=frames[1:],
                   duration=args.delay, loop=0)
    print(f"Wrote {out} ({len(frames)} frames)")


if __name__ == "__main__":
    main()
