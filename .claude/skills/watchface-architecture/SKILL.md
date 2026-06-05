---
name: watchface-architecture
description: Explains how the Pebble watchface's on-watch JS is structured in watchface/src/embeddedjs/ — the module roles, the event→state→drawScreen→widgets data flow, the ctx/state contracts, and the import-vs-init lifecycle. Use when understanding, navigating, refactoring, reviewing, or extending the watchface code, or when figuring out where a change belongs.
paths: watchface/src/embeddedjs/**
allowed-tools: Read, Glob, Grep
---

# Watchface architecture

The on-watch JS (`watchface/src/embeddedjs/`) is a **widget architecture** built on
**Poco** (`commodetto/Poco`). One render path repaints the whole screen; widgets are
small `draw(ctx, state)` functions. Keep new work within this shape.

## Module map

| Module | Role |
| :--- | :--- |
| `main.js` | Thin orchestrator: builds `render`/`theme`/`layout`, owns `state` and `ctx`, runs `init()`, wires events → `drawScreen()`. |
| `theme.js` | `createTheme(render) → { colors, fonts }` — the visual style (Poco colors + `render.Font` instances). |
| `layout.js` | `createLayout(render, theme) → { <element>: { x, y, ... } }` — per-element position anchors derived from screen size + font metrics. |
| `resources.js` | `RESOURCES = { ICON: 1, ... }` — named handles for the **positional** resource IDs declared in `package.json` `resources.media`. |
| `dateTime.js` | Pure formatters (`formatTime`/`formatDate`) — **no Poco**, unit-testable. |
| `widgets/<x>.js` | Each exports `draw(ctx, state)`; draws one element. May also export a pure helper (e.g. `batteryColor`). |
| `manifest.json` | Registers every module so it resolves: flat modules in the `"*"` array, widgets namespaced (`"widgets/time": "./widgets/time"`). |

## Data flow

```
import time:   render = new Poco(screen)
               theme  = createTheme(render)     // colors + fonts
               layout = createLayout(render, theme)
               state  = { now: undefined, battery: {...} }
               ctx    = { render, theme, layout, images }
               widgets = [iconWidget, timeWidget, dateWidget, batteryWidget]

init():        load PDC images into `images`; open sensors (Battery); take first sample

events ───▶ mutate `state` ───▶ drawScreen()
  minutechange → state.now = event.date
  battery onSample → state.battery = {...}   (redraws only once state.now is set)

drawScreen():  render.begin()
               fill background (whole screen)
               for each widget: widget.draw(ctx, state)
               render.end()
```

Every frame repaints the full screen and loops `widgets`. Events never draw
directly — they update `state` and call `drawScreen()`.

## Contracts

- **`ctx = { render, theme, layout, images }`** — the shared, frame-stable
  rendering context. Passed to every widget; widgets read from it, never rebuild it.
- **`state = { now, battery, ... }`** — the mutable data widgets render from.
  `main.js` owns it; events mutate it; widgets only read it.
- **A widget is** `export function draw(ctx, state)` — draws one element, fills no
  background, triggers no redraw, calls no `new Date()`. Pure data→display logic
  lives in a separate module so it stays testable.

## Lifecycle: import vs `init()`

- **At module load:** `render`, `theme` (incl. `render.Font` construction), `layout`,
  `state`, `ctx`, and the `widgets` array are built. These are construction-only.
- **In `init()`:** PDC **images** (`new Poco.PebbleDrawCommandImage(...)`) and
  **sensors** (`new Battery(...)`) are created, so a missing resource or sensor
  fails in one obvious place instead of silently at import.
- A throw at module top level **silently blanks the whole watch** — which is why
  resource/sensor setup is deferred to `init()` and why font sizes must be valid
  (a bad `render.Font` size in `theme.js` blanks the watch at load).

## Conventions (violating these has bitten us)

- **Single render path** — no per-feature draw logic or second redraw path.
- **Separate pure logic from drawing** — testable modules like `dateTime.js`.
- **Never do throwing work at import** — resources/sensors in `init()`.
- **Name resources; don't hardcode IDs** — `RESOURCES.X`, kept in sync with
  `package.json` media order (IDs are positional).
- **Register every module in `manifest.json`** or it won't resolve.

## Where changes go

- **Add a feature** → one widget. See the **`adding-watchface-widget`** skill +
  `snippets/widget-pattern.md`.
- **Draw correctly** (Poco API, arg orders, fonts) → the **`pebble-poco-rendering`**
  skill + `snippets/poco-rendering.md`, `snippets/fonts.md`.
- **Add art** → the **`svg-to-pdc-assets`** skill.
- **Build / run / install** → the **`pebble-build-deploy`** skill.
- Deeper reference: `snippets/watchface-structure.md` (render loop + events),
  `snippets/sensors.md`, `snippets/comms.md` (data-driven widgets).
