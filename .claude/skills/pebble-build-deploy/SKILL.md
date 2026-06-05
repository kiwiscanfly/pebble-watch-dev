---
name: pebble-build-deploy
description: Build, run, and install the Pebble watchface — in the emery emulator or on the physical Pebble Time 2 — and drive emulator state. Use when the user wants to build, run, deploy, install, publish, or test the watchface, or stream device logs.
disable-model-invocation: true
allowed-tools: Read, Bash(cd watchface && npm run lint*), Bash(cd watchface && npm run build*), Bash(cd watchface && npm run assets*)
---

# Build & deploy the watchface

Run npm scripts from the `watchface/` directory. The SDK is already installed
(`pebble` on PATH); **do not** reinstall it.

## What I can run vs what you run

I can run the **safe, non-interactive** steps — validate, lint, asset conversion,
build, and screenshots:

```sh
cd watchface && npm run validate   # structural checks (see validate-watchface skill)
cd watchface && npm run lint       # eslint
cd watchface && npm run assets     # svg → pdc
cd watchface && npm run build      # assets + pebble build (all targetPlatforms)
pebble screenshot --no-open --emulator emery /tmp/shot.png   # grab a frame
```

`npm run validate` and `npm run lint` both gate `npm run dev`/`deploy`, so a broken
project can't reach the watch.

**You run anything that launches a long-running process, talks to the watch, or
publishes** — I'll print the exact command rather than execute it:

```sh
pebble install --emulator emery            # run in the Pebble Time 2 emulator
pebble install --cloudpebble               # install to the physical watch
pebble install --cloudpebble --logs        # ...and stream app logs
pebble publish                             # publish to the appstore (Rebble Web Services)

# Or the bundled npm flows (lint + build + install via cloudpebble):
cd watchface && npm run dev                # ...with --logs
cd watchface && npm run deploy             # ...without logs
```

## Installing to the physical Pebble Time 2

Use `pebble install --cloudpebble` — it routes through the Pebble mobile app's
CloudPebble connection, so the watch must be connected to the app over Bluetooth.
Add `--logs` to stream app logs. The direct `--phone <ip>` Developer Connection
path was unreliable here (connection refused), so prefer `--cloudpebble`.

## Driving emulator state

While the `emery` emulator runs, push fake input/sensor values to test widgets:

```sh
pebble emu-battery --percent 20 --charging       # battery level / charging
pebble emu-button click select --emulator emery  # press a button (select/up/down/back)
pebble emu-button click back --duration 2000 --emulator emery  # long-press
pebble emu-tap --emulator emery                  # accelerometer tap
# example-repo form also takes a qemu target, e.g. --qemu localhost:12344
```

To confirm a change actually *looks* right, use the **`verify-watchface`** skill
(build → screenshot → Read the PNG → checklist → iterate).

## Preview GIF (animated faces / store rollover)

With the emulator running:

```sh
python3 watchface/scripts/create_preview_gif.py --platform emery --frames 8 --delay 400
```

Captures N frames into `preview_emery.gif`. Requires Pillow (`pip3 install Pillow`).

## Publishing to the appstore

Publishing goes through Rebble Web Services (shared by the Core and Rebble stores).
This is **yours to run** (interactive, opens a browser, has side effects):

```sh
pebble login                 # one-time; opens a browser for auth
pebble login --status        # check login state
pebble publish               # interactive: prompts for name/description/screenshots
pebble publish --non-interactive --description "..." --release-notes "..."
```

Useful flags: `--release-notes TEXT`, `--is-published` (make the release live now),
`--no-gif-all-platforms` (skip rollover GIF capture), `--category <daily|tools|
notifications|remotes|health|games>`, `--name NAME` (new apps only).

## Platforms

Targets are `emery` (Pebble Time 2 — the maintainer's watch, prefer it) and
`gabbro` (Pebble Round 2). See `snippets/project-config.md` for the full project /
resource configuration.
