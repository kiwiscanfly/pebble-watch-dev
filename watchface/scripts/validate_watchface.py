#!/usr/bin/env python3
"""
Watchface project validator.

Checks the invariants that this project's architecture depends on but that ESLint
cannot see — the failure modes documented in CLAUDE.md ("these have bitten us"):

  1. Resource IDs in resources.js stay in lockstep with package.json media
     (same count, contiguous 1..N, matching names) — a drift renders the wrong
     art or blanks the watch.
  2. Built-in font sizes used in the code actually exist — an unavailable size
     fails to load and blanks the whole watch.
  3. Every widget file is registered in manifest.json, imported in main.js, and
     present in the widgets[] render array — an unregistered module won't resolve.
  4. Resource images load inside init(), not at module top level — a throw at
     import silently blanks the watch.

Usage:
    python3 scripts/validate_watchface.py            # validates ./ (the watchface dir)
    python3 scripts/validate_watchface.py <dir>

Exit codes: 0 = passed (warnings allowed), 1 = errors found.
"""

import json
import re
import sys
from pathlib import Path

# Built-in font families → the bitmap sizes that actually exist (see snippets/fonts.md).
# A `new render.Font("Family-Style", size)` with a size not listed here blanks the watch.
FONT_SIZES = {
    "Bitham-Black": {30},
    "Bitham-Bold": {42},
    "Bitham-Light": {18, 34, 42},
    "Bitham-Medium": {34, 42},
    "DroidSerif-Bold": {28},
    "Gothic-Bold": {14, 18, 24, 28, 36},
    "Gothic-Regular": {9, 14, 18, 24, 28, 36},
    "Leco-Bold": {20, 26, 32, 36, 38},
    "Leco-Light": {28},
    "Leco-Regular": {42},
    "Roboto-Bold": {49},
    "Roboto-Condensed": {21},
}

USE_COLOR = sys.stdout.isatty()


def paint(code, text):
    return f"\033[{code}m{text}\033[0m" if USE_COLOR else text


def ok(msg):      print(f"  {paint('92', 'OK')}   {msg}")
def err(msg):     print(f"  {paint('91', 'FAIL')} {msg}")
def warn(msg):    print(f"  {paint('93', 'WARN')} {msg}")
def info(msg):    print(f"  {paint('94', 'INFO')} {msg}")
def heading(msg): print(f"\n{paint('1', msg)}")


def brace_depth_at(source, index):
    """Net `{` minus `}` before `index`, ignoring nothing fancy (good enough for
    spotting module-top-level (depth 0) vs inside-a-function (depth > 0) code)."""
    chunk = source[:index]
    return chunk.count("{") - chunk.count("}")


def validate_resource_sync(project, errors):
    heading("Resource IDs (resources.js ↔ package.json media)")
    pkg_path = project / "package.json"
    res_path = project / "src/embeddedjs/resources.js"

    try:
        media = json.loads(pkg_path.read_text())["pebble"]["resources"]["media"]
    except (OSError, KeyError, json.JSONDecodeError) as e:
        errors.append(f"could not read package.json media: {e}")
        err(f"could not read package.json media: {e}")
        return
    media_names = [m.get("name", "?") for m in media]

    if not res_path.exists():
        errors.append("resources.js not found")
        err("resources.js not found")
        return
    # Parse `NAME: 3` pairs out of the RESOURCES object.
    pairs = re.findall(r"(\w+)\s*:\s*(\d+)", res_path.read_text())
    res = {name: int(num) for name, num in pairs}

    if len(res) != len(media):
        errors.append(
            f"resource count mismatch: resources.js has {len(res)}, "
            f"package.json media has {len(media)}")
        err(f"count mismatch: resources.js={len(res)} vs media={len(media)}")
    else:
        ok(f"{len(res)} resources declared in both files")

    ids = sorted(res.values())
    if ids and ids != list(range(1, len(ids) + 1)):
        errors.append(f"resource IDs not contiguous 1..N: {ids}")
        err(f"IDs must be contiguous 1..N, got {ids}")
    elif ids:
        ok("IDs are contiguous 1..N")

    # Each ID should index the media entry at that position (1-based).
    for name, num in res.items():
        if 1 <= num <= len(media_names):
            expected = media_names[num - 1]
            if expected.upper() != name.upper():
                warn(f'RESOURCES.{name} = {num} but media[{num - 1}] is "{expected}" '
                     f"(order may have drifted)")
        else:
            errors.append(f"RESOURCES.{name} = {num} has no media entry")
            err(f"RESOURCES.{name} = {num} has no matching media entry")


def validate_font_sizes(project, errors):
    heading("Built-in font sizes")
    found = False
    for js in (project / "src/embeddedjs").rglob("*.js"):
        text = js.read_text()
        for family, size in re.findall(r'new\s+\w+\.Font\(\s*"([^"]+)"\s*,\s*(\d+)\s*\)', text):
            found = True
            size = int(size)
            valid = FONT_SIZES.get(family)
            if valid is None:
                info(f'{js.name}: "{family}" not a known built-in — verify it ships '
                     f"at size {size}, or it's a custom font resource")
            elif size not in valid:
                errors.append(f'{js.name}: {family} @ {size} does not exist '
                              f"(valid: {sorted(valid)}) — will blank the watch")
                err(f'{js.name}: {family} @ {size} invalid (valid: {sorted(valid)})')
            else:
                ok(f"{js.name}: {family} @ {size}")
    if not found:
        info("no built-in render.Font(...) calls found")


def validate_widgets(project, errors):
    heading("Widget registration (files ↔ manifest ↔ main.js)")
    emb = project / "src/embeddedjs"
    widget_files = sorted(p.stem for p in (emb / "widgets").glob("*.js")) if (emb / "widgets").is_dir() else []
    if not widget_files:
        info("no widgets/ files found")
        return

    try:
        modules = json.loads((emb / "manifest.json").read_text())["modules"]
    except (OSError, KeyError, json.JSONDecodeError) as e:
        errors.append(f"could not read manifest.json modules: {e}")
        err(f"could not read manifest.json modules: {e}")
        modules = {}

    main = (emb / "main.js").read_text() if (emb / "main.js").exists() else ""
    imported = dict(re.findall(r'import\s+\*\s+as\s+(\w+)\s+from\s+"(widgets/\w+)"', main))
    array_match = re.search(r"widgets\s*=\s*\[([^\]]*)\]", main)
    array_body = array_match.group(1) if array_match else ""

    for name in widget_files:
        key = f"widgets/{name}"
        problems = []
        if key not in modules:
            problems.append(f'not registered in manifest.json ("{key}")')
        alias = next((a for a, m in imported.items() if m == key), None)
        if alias is None:
            problems.append("not imported in main.js")
        elif alias not in array_body:
            problems.append("imported but missing from the widgets[] array")
        if problems:
            for p in problems:
                errors.append(f"widget '{name}': {p}")
                err(f"widget '{name}': {p}")
        else:
            ok(f"widget '{name}': registered, imported, in render array")


def validate_init_loads(project, errors):
    heading("Resource loads deferred to init()")
    main_path = project / "src/embeddedjs/main.js"
    if not main_path.exists():
        return
    src = main_path.read_text()
    hits = list(re.finditer(r"new\s+Poco\.(PebbleDrawCommandImage|PebbleBitmap)\s*\(", src))
    if not hits:
        info("no PDC/bitmap constructions found")
        return
    bad = [m for m in hits if brace_depth_at(src, m.start()) == 0]
    if bad:
        for m in bad:
            line = src.count("\n", 0, m.start()) + 1
            errors.append(f"main.js:{line}: resource constructed at module top level "
                          f"(move into init())")
            err(f"main.js:{line}: resource loaded at module top level — move into init()")
    else:
        ok(f"all {len(hits)} resource construction(s) are inside a function (not at import)")


def main():
    project = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    print(f"\n{paint('1', 'Validating watchface project')}: {project}")
    if not (project / "package.json").exists():
        err("no package.json here — run from the watchface/ dir or pass its path")
        sys.exit(1)

    errors = []
    validate_resource_sync(project, errors)
    validate_font_sizes(project, errors)
    validate_widgets(project, errors)
    validate_init_loads(project, errors)

    heading("Summary")
    if errors:
        print(f"  {paint('91', f'{len(errors)} error(s)')} — fix before building:")
        for e in errors:
            print(f"    • {e}")
        sys.exit(1)
    print(f"  {paint('92', 'All structural checks passed.')}")
    sys.exit(0)


if __name__ == "__main__":
    main()
