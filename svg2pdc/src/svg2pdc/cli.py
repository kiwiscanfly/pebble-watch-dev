"""Command-line interface for svg2pdc.

Subcommands:
  convert  SVG file or directory -> PDC file(s) the watch can render
  preview  SVG -> PNG (via rsvg-convert) so you can eyeball it on your Mac
"""

import argparse
import glob
import os
import subprocess
import sys

from .svg2pdc import create_pdc_from_path

FRAME_DURATION_MS = 33
PLAY_COUNT = 1


def _convert_one(svg_path, pdc_path, verbose, precise):
    out_dir = os.path.dirname(os.path.abspath(pdc_path))
    os.makedirs(out_dir, exist_ok=True)
    errors = create_pdc_from_path(
        svg_path, False, pdc_path, verbose, FRAME_DURATION_MS, PLAY_COUNT, precise
    )
    return errors or []


def cmd_convert(args):
    source = args.input
    dest = args.output

    if os.path.isdir(source):
        svgs = sorted(glob.glob(os.path.join(source, "*.svg")))
        if not svgs:
            print(f"No .svg files found in {source}; nothing to do.")
            return 0
        os.makedirs(dest, exist_ok=True)
        errors = []
        for svg in svgs:
            stem = os.path.splitext(os.path.basename(svg))[0]
            pdc = os.path.join(dest, stem + ".pdc")
            errors += _convert_one(svg, pdc, args.verbose, args.precise)
            print(f"  {svg} -> {pdc}")
    else:
        if os.path.isdir(dest) or dest.endswith(os.sep):
            stem = os.path.splitext(os.path.basename(source))[0]
            dest = os.path.join(dest, stem + ".pdc")
        errors = _convert_one(source, dest, args.verbose, args.precise)
        print(f"{source} -> {dest}")

    if errors:
        print("Conversion reported issues in:", file=sys.stderr)
        for ef in errors:
            print(f"\t{ef}", file=sys.stderr)
        return 1
    return 0


def cmd_preview(args):
    cmd = ["rsvg-convert"]
    if args.width:
        cmd += ["-w", str(args.width)]
    if args.height:
        cmd += ["-h", str(args.height)]
    if args.background:
        cmd += ["-b", args.background]
    cmd += [args.input, "-o", args.output]
    try:
        subprocess.run(cmd, check=True)
    except FileNotFoundError:
        print(
            "rsvg-convert not found. Install it with: brew install librsvg",
            file=sys.stderr,
        )
        return 1
    except subprocess.CalledProcessError as exc:
        return exc.returncode
    print(f"{args.input} -> {args.output}")
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="svg2pdc",
        description="Convert SVGs to Pebble Draw Command (PDC) files and preview them.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    convert = sub.add_parser("convert", help="Convert an SVG file or a directory of SVGs to PDC")
    convert.add_argument("input", help="SVG file, or a directory of .svg files")
    convert.add_argument("output", help="Output .pdc file (single input) or directory (batch)")
    convert.add_argument("-p", "--precise", action="store_true", help="Use sub-pixel precision for paths")
    convert.add_argument("-v", "--verbose", action="store_true", help="Print the parsed draw commands")
    convert.set_defaults(func=cmd_convert)

    preview = sub.add_parser("preview", help="Render an SVG to PNG (via rsvg-convert) to view on your Mac")
    preview.add_argument("input", help="SVG file")
    preview.add_argument("output", help="Output PNG file")
    preview.add_argument("-W", "--width", type=int, help="Target width in pixels")
    preview.add_argument("-H", "--height", type=int, help="Target height in pixels")
    preview.add_argument(
        "-b", "--background",
        help="Background color (e.g. '#46342B' or 'black') so light icons are visible",
    )
    preview.set_defaults(func=cmd_preview)

    args = parser.parse_args(argv)
    return args.func(args)
