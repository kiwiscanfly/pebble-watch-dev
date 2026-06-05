# CLAUDE.md

Guidance for working in this repo: development of **Pebble watchfaces and apps**
for the modern Core Devices Pebble watches (2025 PebbleOS revival).

## Context: this is the NEW Pebble, not the original

Pebble was revived in 2025 by Eric Migicovsky's company **Core Devices** after
Google open-sourced PebbleOS in January 2025. When researching or citing docs,
distinguish old from new:

- **Trust as canonical:** `developer.repebble.com` (SDK docs/tutorials),
  `repebble.com` (hardware/app), `github.com/coredevices` (open-source PebbleOS
  + SDK).
- **Older community docs, use with care:** `developer.rebble.io` — its C API
  tutorials are still largely valid but predate the relaunch.
- **Outdated/dead — do not follow:** the original `pebble.com` SDK installer,
  pre-2025 `pebble-tool` install instructions, and the old product names
  "Core 2 Duo" / "Core Time 2" (now **Pebble 2 Duo** / **Pebble Time 2**).
- App publishing goes through **Rebble Web Services**, the shared backend for
  both the Core and Rebble appstores (`pebble publish`).

## Hardware / platforms

The maintainer owns a **Pebble Time 2** → SDK platform **`emery`**. Prefer
`emery` for emulator runs and on-device installs. The other modern platform is
`gabbro` (Pebble Round 2). Classic platforms (`aplite`, `basalt`, `chalk`,
`diorite`) exist for older watches but aren't the focus here.

## Toolchain

The SDK is **already installed globally via `uv`** (`pebble` on PATH at
`~/.local/bin/pebble`). Do **not** reinstall or run SDK installs yourself —
those are long-running/interactive and are the user's to run. Current versions:
pebble-tool v5.0.37, active SDK v4.9.169.

Common commands (run from inside a project dir):

```sh
pebble build                     # build for all targetPlatforms
pebble install --emulator emery  # run in the Pebble Time 2 emulator
pebble install --cloudpebble     # install to the physical watch via the phone app
pebble install --cloudpebble --logs  # ...and stream app logs
pebble publish                   # publish to the appstore
```

**On-device install** uses `pebble install --cloudpebble` (via the phone app over
Bluetooth; add `--logs` to stream). The **`pebble-build-deploy`** skill has the full
command set, the `--phone` unreliability caveat, and emulator state-driving — and
encodes that on-device/long-running commands are yours to run, not mine.

## Linting

The `watchface/` project uses ESLint (flat config, `eslint.config.mjs`) for
correctness (`no-undef`, `no-unused-vars`) plus style. Run `npm run lint` (or
`npm run lint:fix`) from the project dir; `npm run deploy` lints before
installing, so it blocks broken code from reaching the watch. ESLint lives in
`devDependencies` only — the Pebble build ignores it (it reads just the
`dependencies` key), so it never ships in the `.pbw`. No unit tests yet.

## Vector assets (svg2pdc)

Watchface art lives as committed SVG in `watchface/resources/svg/` and is converted
to `watchface/resources/pdc/` (generated, git-ignored) by `npm run assets` (which
`npm run build` runs). PDCs are declared in `package.json` as `{ "type":"raw" }`
media and loaded by **positional resource ID** — keep `resources.js` in lockstep
with `package.json` media order, or rendering silently breaks.

The full pipeline (svg2pdc authoring limits, the order-sensitive ID bookkeeping,
verifying output) is in the **`svg-to-pdc-assets`** skill, `svg2pdc/README.md`, and
`snippets/project-config.md`.

## Build paths

- **C** — classic native Pebble API; maximum API coverage.
- **Alloy** — JavaScript framework on Moddable XS (runs JS on the watch). Faster
  iteration, but not every C API is exposed yet. The existing `watchface/`
  project is an Alloy/Moddable project (`projectType: "moddable"`,
  `src/embeddedjs/` for on-watch JS, `src/pkjs/` for phone-side PebbleKit JS,
  `src/c/` for C glue around the Moddable runtime).

## Watchface architecture (`src/embeddedjs/`)

The on-watch JS is a **widget architecture**: one render path repaints the screen
and loops small `draw(ctx, state)` widgets. The full module map, the
event→state→drawScreen→widgets data flow, and the ctx/state contracts are in the
**`watchface-architecture`** skill (auto-loads when editing
`watchface/src/embeddedjs/`) and `snippets/watchface-structure.md`.

Conventions (these exist because violating them has bitten us):
- **Single render path.** Events mutate `state` and call `drawScreen()`, which
  loops the `widgets` array. No per-feature draw logic or second redraw path.
- **Separate pure logic from drawing.** Data→string/number logic goes in pure
  modules (like `dateTime.js`) so it stays testable; widgets only draw.
- **Never do throwing work at import.** Load resources/sensors in `init()`, not at
  module top level — a throw there silently blanks the whole watch (cost us the
  font-size and battery regressions).
- **Name resources; don't hardcode IDs.** Use `RESOURCES.X`, not
  `PebbleDrawCommandImage(2)`. IDs are positional — keep `resources.js` in sync
  with `package.json` "resources.media" order.
- **Register every module in `manifest.json`.** Flat modules go in the `"*"`
  array; widgets are namespaced (`"widgets/time": "./widgets/time"`) and imported
  as `"widgets/time"`. A new module that isn't registered won't resolve.
- **Adding a feature = one widget**, verified incrementally in the emulator. The
  full add-a-widget procedure, template, and verify loop are in the
  **`adding-watchface-widget`** skill and `snippets/widget-pattern.md`.

### Poco gotchas

The complete Poco API and detailed examples now live in the
**`pebble-poco-rendering`** skill (auto-loads when editing
`watchface/src/embeddedjs/`) and `snippets/poco-rendering.md`. The watch-blanking
traps are kept here as an always-on safety net:

- **System fonts are fixed bitmap sizes** — an unavailable size fails to load and
  blanks the watch (valid sizes: `snippets/fonts.md`; e.g. Bitham-Bold only at 42).
- **Draw-call arg orders differ from the typings.** `frameRoundRect` /
  `drawRoundRect` take a Pebble `GRect` `(x, y, width, height, color, radius)` —
  not corner coords; `fillRectangle` is `(color, x, y, w, h)`; `clip` is
  `(x, y, w, h)`.
- **Don't paint an "empty" background inside a widget** — `drawScreen()` repaints
  the background each frame.
- **`event.date`, not `new Date()`** — non-time redraws reuse `state.now`.
