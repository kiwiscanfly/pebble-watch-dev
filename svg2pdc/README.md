# svg2pdc

A small Python 3 CLI (managed by [`uv`](https://docs.astral.sh/uv/)) that converts
**SVG** images into **PDC** (Pebble Draw Command) vector files — the format Pebble
watchfaces/apps can render with `Poco.PebbleDrawCommandImage` + `render.drawDCI`.

It's a modernized vendoring of Pebble's original `svg2pdc.py` (which was Python 2),
plus a `preview` command for eyeballing art on your Mac.

## Usage

Run via `uv` (no global install needed — deps live in this folder's `.venv`):

```sh
# From this directory:
uv run svg2pdc convert icon.svg icon.pdc
uv run svg2pdc convert resources/svg resources/pdc   # batch: every *.svg -> *.pdc
uv run svg2pdc preview icon.svg icon.png -W 200 -H 200 -b "#46342B"

# From elsewhere (e.g. the watchface project), point uv at this project:
uv run --project ../svg2pdc svg2pdc convert resources/svg resources/pdc
```

- `convert <in.svg|dir> <out.pdc|dir>` — single file, or batch-convert a directory.
- `preview <in.svg> <out.png> [-W w] [-H h] [-b color]` — renders the SVG to PNG via
  `rsvg-convert`. Use `-b` (background) so light-colored icons are visible.

## Supported SVG

Only `g`, `layer`, `path`, `rect`, `polyline`, `polygon`, `line`, `circle`.
Export "Plain SVG" / "SVG Tiny 1.1", flatten transforms and groups, and use
`#rrggbb` colors. Colors are reduced to Pebble's 2-bits-per-channel palette.

**Fidelity caveat:** `path` curves are approximated by the **anchor point at the
start of each segment** (a polyline through the path nodes), not by sampling the
curve. For crisp results prefer `circle`, `line`, `rect`, `polygon`/`polyline`, or
paths made of straight segments. `circle` becomes a true PDC circle command.

## Verifying output

The first bytes of a valid image are the ASCII magic `PDCI`, followed by a 4-byte
size, then version/width/height. `xxd icon.pdc | head` is a quick sanity check.
The real test is on-device — `preview` only renders the source SVG, not the PDC.
