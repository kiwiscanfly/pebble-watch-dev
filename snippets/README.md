# snippets/

Curated, annotated code patterns for building **Pebble watchfaces and widgets**
on the modern (2025 Core Devices) PebbleOS, distilled from the
[Moddable-OpenSource/pebble-examples](https://github.com/Moddable-OpenSource/pebble-examples)
repo and adapted to **our** widget architecture (see the root `CLAUDE.md`).

## Why this folder exists

These are raw material for authoring **Claude Code skills** that help us develop
watchfaces. Each file is a focused reference doc with copy-pasteable code, written
so a future skill can point Claude at exactly the file it needs (progressive
disclosure). See [`skill-design.md`](./skill-design.md) for the proposed skills and
how they map onto these files.

## Important: Poco vs Piu

The Moddable examples use **two different rendering frameworks**. Know which one a
snippet targets before copying it:

- **Poco** (`commodetto/Poco`) — the lightweight immediate-mode graphics API.
  **This is what our `watchface/` project uses** (`new Poco(screen)`,
  `render.drawDCI`, `render.drawText`, a single `drawScreen()` paint path). Prefer
  Poco snippets.
- **Piu** — a higher-level retained-mode UI framework (`Application`, `Skin`,
  `Texture`, `Behavior`, `Content.template`). The `piu/watchfaces/*` examples use
  it. **Its API does not work in our Poco project.** We mine those examples only
  for *concepts* (hand-angle math, per-platform assets, color-vs-mono asset sets)
  and re-express them in Poco below.

Snippets are tagged **[Poco]**, **[Piu→Poco]** (concept ported), or
**[framework-agnostic]** (sensors, comms, storage, project config — these are the
same regardless of renderer).

## Index

| File | What's in it |
| :--- | :--- |
| [`skill-design.md`](./skill-design.md) | Claude Code skill authoring best practices + concrete skills proposed for this repo |
| [`poco-rendering.md`](./poco-rendering.md) | The Poco draw API we render with: colors, text, shapes, images, clip — plus the gotchas from `CLAUDE.md` |
| [`fonts.md`](./fonts.md) | Built-in font families and their **valid bitmap sizes** (wrong size = blank watch) |
| [`watchface-structure.md`](./watchface-structure.md) | The render loop, time events (`minutechange`/`secondchange`), `event.date`, `unobstructed` |
| [`widget-pattern.md`](./widget-pattern.md) | Our widget contract + a copy-paste template for adding a new widget |
| [`analog-hands.md`](./analog-hands.md) | Clock-hand angle math + rotating a PDC hand with Poco |
| [`animation.md`](./animation.md) | Three ways to animate, cheapest first: no-timer minute-frame, `setInterval` loop, PDC rotate/scale/sequence |
| [`settings.md`](./settings.md) | Phone-side config (Clay) → `Message` → `localStorage` → redraw |
| [`sensors.md`](./sensors.md) | ECMA-419 sensor pattern: battery, accelerometer, light, location (+ emulator drive commands) |
| [`input-and-watch-apis.md`](./input-and-watch-apis.md) | Buttons, vibration, wakeup, backlight, and `watch`/`screen`/`device` introspection |
| [`comms.md`](./comms.md) | Watch↔phone AppMessage, `fetch()`, and the PebbleKit-JS (`pkjs`) side |
| [`persistence.md`](./persistence.md) | `localStorage` and ECMA-419 key-value storage |
| [`project-config.md`](./project-config.md) | `package.json` media/platforms, `manifest.json` module registration, resource IDs |
| [`js-runtime-notes.md`](./js-runtime-notes.md) | XS engine limits: omitted JS features, Hardened JS, memory, strict mode |

## Provenance

Every snippet notes its source example (e.g. `hellopoco-pebblegraphics`). The
example repo's own `readme.md` is the authority for the font table and the list of
omitted JavaScript features. Verified against the repo state of **May 2026**.

## How these tie back to our project

Our watchface lives in `watchface/src/embeddedjs/` and follows a strict widget
architecture documented in the root `CLAUDE.md`. When a snippet here conflicts with
a `CLAUDE.md` convention, **`CLAUDE.md` wins** — the snippets are adapted to fit it,
and each file calls out the relevant convention (single render path, load resources
in `init()`, named resource IDs, register modules in `manifest.json`, etc.).
