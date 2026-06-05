---
name: svg-to-pdc-assets
description: Adds or updates a vector art asset (icon, clock hand, glyph) in the Pebble watchface via the SVG to PDC pipeline. Use when the user wants to add an icon or vector image to the watchface, change existing art, or work with svg2pdc / .pdc / resources.media. Handles the order-sensitive resource-ID bookkeeping that silently breaks rendering if done wrong.
allowed-tools: Read, Edit, Glob, Grep, Bash(cd watchface && npm run assets*), Bash(uv run --project svg2pdc*)
---

# SVG → PDC assets

Watchface vector art lives as **committed SVG** in `watchface/resources/svg/` and is
converted to **PDC** (Pebble Draw Command) files in `watchface/resources/pdc/`
(generated, git-ignored) by `npm run assets`, which `npm run build` runs
automatically. The watch loads PDCs by **positional resource ID**, so the order of
declarations must stay in lockstep across three files.

## The pipeline — do these in order

1. **Add the SVG** to `watchface/resources/svg/<name>.svg`. Author for the
   converter's limits (next section).

2. **Convert** (from the `watchface/` dir): `npm run assets`
   — runs `uv run --project ../svg2pdc svg2pdc convert resources/svg resources/pdc`
   over the whole folder. Confirm `resources/pdc/<name>.pdc` appears.

3. **Declare the media** in `watchface/package.json` → `pebble.resources.media`,
   as a `raw` entry pointing at the PDC:
   ```json
   { "type": "raw", "name": "<NAME>", "file": "pdc/<name>.pdc" }
   ```

4. **Add the matching named ID** in `watchface/src/embeddedjs/resources.js`. **IDs
   are positional, 1-based, in `resources.media` order** — append in the same
   position you added the media entry:
   ```js
   export const RESOURCES = { ICON: 1, BOLT: 2, <NAME>: 3 };
   ```

5. **Load it in `init()`** (in `main.js`), never at module top level:
   ```js
   images.<name> = new Poco.PebbleDrawCommandImage(RESOURCES.<NAME>);
   ```
   Then draw it from a widget with `render.drawDCI(images.<name>, x, y)`.

> ⚠️ **The ordering is the trap.** Inserting a media entry anywhere but the end
> renumbers every later ID. If `resources.js` and `package.json` `media` ever drift
> out of order, the watch loads the wrong art (or blanks). After editing, re-check
> that the Nth `media` entry matches the constant whose value is N.

## svg2pdc authoring limits (from svg2pdc/README.md)

- Supported elements only: `g`, `layer`, `path`, `rect`, `polyline`, `polygon`,
  `line`, `circle`. Export "Plain SVG" / "SVG Tiny 1.1"; flatten transforms/groups.
- Use `#rrggbb` colors — they're reduced to Pebble's 2-bits-per-channel palette.
- **`path` curves are approximated** by the anchor at the start of each segment (a
  polyline through nodes), not by sampling the curve. **Prefer `circle`, `line`,
  `rect`, `polygon`/`polyline`** or straight-segment paths for crisp output.
  `circle` becomes a true PDC circle command.

## Verify

- Quick sanity: a valid PDC starts with ASCII magic `PDCI` (`xxd resources/pdc/<name>.pdc | head`).
- Preview the **source SVG** on the Mac (not the PDC): `uv run --project ../svg2pdc
  svg2pdc preview resources/svg/<name>.svg /tmp/<name>.png -b "#46342B"`.
- The real test is on-device / emulator: `pebble install --emulator emery`.

## Reference

- `svg2pdc/README.md` — full converter docs and fidelity caveats.
- `snippets/project-config.md` — media/manifest/resource-ID rules in context.
- `snippets/poco-rendering.md` — drawing PDCs (`drawDCI`, rotate/scale).
