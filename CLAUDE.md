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

**Installing to the physical Pebble Time 2:** use `pebble install --cloudpebble`
(routes through the Pebble mobile app's CloudPebble connection; watch must be
connected to the app over Bluetooth). Add `--logs` to stream app logs. The
direct `--phone <ip>` Developer Connection path was unreliable here (connection
refused), so prefer `--cloudpebble`.

## Linting

The `watchface/` project uses ESLint (flat config, `eslint.config.mjs`) for
correctness (`no-undef`, `no-unused-vars`) plus style. Run `npm run lint` (or
`npm run lint:fix`) from the project dir; `npm run deploy` lints before
installing, so it blocks broken code from reaching the watch. ESLint lives in
`devDependencies` only — the Pebble build ignores it (it reads just the
`dependencies` key), so it never ships in the `.pbw`. No unit tests yet.

## Vector assets (svg2pdc)

The root **`svg2pdc/`** folder is a `uv`-managed Python 3 CLI (a modernized
vendoring of Pebble's old `svg2pdc.py`) that converts SVG → **PDC** (Pebble Draw
Command) vector files. Watchface art lives as SVG in `watchface/resources/svg/`
(committed) and is converted to `watchface/resources/pdc/` (generated,
git-ignored) by `npm run assets`, which `npm run build` runs automatically.

- PDCs are declared in `package.json` as `{ "type":"raw", ... }` media; the build
  bundles them. Resource IDs are **positional numbers** (1, 2, …) in declaration
  order — JS loads them via `new Poco.PebbleDrawCommandImage(n)` + `render.drawDCI`.
- The tool runs repo-locally (`uv run --project ../svg2pdc svg2pdc ...`); nothing
  is installed globally. SVG support is a limited element set and `path` curves
  are approximated — prefer circle/line/rect/polygon. See `svg2pdc/README.md`.

## Build paths

- **C** — classic native Pebble API; maximum API coverage.
- **Alloy** — JavaScript framework on Moddable XS (runs JS on the watch). Faster
  iteration, but not every C API is exposed yet. The existing `watchface/`
  project is an Alloy/Moddable project (`projectType: "moddable"`,
  `src/embeddedjs/` for on-watch JS, `src/pkjs/` for phone-side PebbleKit JS,
  `src/c/` for C glue around the Moddable runtime).

## Watchface architecture (`src/embeddedjs/`)

The on-watch JS is a **widget architecture**. Keep new work within it:

```
main.js        Thin orchestrator: owns state, builds ctx, wires events → drawScreen()
theme.js       createTheme(render) → { colors, fonts }      (visual style)
layout.js      createLayout(render, theme) → per-element { x, y } anchors (positions)
resources.js   RESOURCES = { ICON: 1, ... }                 (named resource IDs)
dateTime.js    Pure formatters (formatTime/formatDate) — no Poco, unit-testable
widgets/<x>.js Each exports draw(ctx, state); ctx = { render, theme, layout, images }
```

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
- **Adding a feature = one widget** (`widgets/x.js`) + one entry in the `widgets`
  array + a manifest line (+ a `resources.js`/media entry if it has an asset).
- **Add features incrementally and verify in the emulator** before layering on —
  `pebble install --emulator emery`, and drive state with helpers like
  `pebble emu-battery --percent N [--charging]`.

### Poco gotchas (learned the hard way)
- **`frameRoundRect` / `drawRoundRect` take `(x, y, width, height, color, radius)`**
  — a Pebble `GRect` — even though the TypeScript typings name the args
  `x0, y0, x1, y1`. Do **not** pass corner coordinates. `fillRectangle` is
  `(color, x, y, w, h)`; `clip` is `(x, y, w, h)`.
- **Don't paint an "empty" background inside a widget.** `drawScreen()` repaints
  the whole background each frame, so e.g. a battery's unfilled area should just
  be left as the background, not filled with black (that was a tutorial holdover
  for black-screen watches).
- **System fonts are fixed bitmap sizes.** `new render.Font("Bitham-Bold", 42)`
  must be a size that exists (Bitham-Bold only exists at 42); an unavailable size
  fails to load and blanks the watch. For arbitrary sizes use a custom font
  resource.
- **`event.date`, not `new Date()`.** Read the time from the `minutechange`
  event; event-driven redraws (e.g. battery) reuse the last known `state.now`.
