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
