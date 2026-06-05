---
name: pebble-poco-rendering
description: Poco rendering API reference and hard-won gotchas for the Pebble watchface in watchface/src/embeddedjs/. Use when reading or editing watchface drawing code — Poco calls (drawText, drawDCI, fillRectangle, frameRoundRect, drawRoundRect, drawLine, drawCircle, clip), choosing a built-in font, loading PDC or bitmap resources, or building a widget. Carries the rules that prevent silently blanking the watch.
paths: watchface/src/embeddedjs/**
allowed-tools: Read, Glob, Grep
---

# Pebble Poco rendering

Our watchface (`watchface/src/embeddedjs/`) renders with **Poco**
(`commodetto/Poco`): a single `drawScreen()` between `render.begin()` and
`render.end()` loops the `widgets` array. Apply these rules whenever you touch
rendering code.

## Critical rules — violating these silently blanks the watch

- **Never do throwing work at import.** Load resources, fonts, and sensors in
  `init()`, not at module top level. A throw there blanks the whole watch with no
  error to point at.
- **Built-in font sizes are fixed bitmaps.** `new render.Font(family, size)` must
  use a size that actually exists, or it fails to load and blanks the watch. Valid
  sizes are in `snippets/fonts.md` (e.g. `Bitham-Bold` exists only at 42). For an
  arbitrary size, ship a custom font resource instead of guessing.
- **Read time from the event:** `event.date`, never `new Date()`. Non-time redraws
  (battery sample, etc.) reuse the last known `state.now`.

## Draw-call argument orders (the #1 source of Poco bugs)

The TypeScript typings are misleading — they name rect args `x0, y0, x1, y1`. The
actual signatures are:

- `fillRectangle(color, x, y, w, h)` — **color first**
- `frameRoundRect(x, y, w, h, color, radius)` — a Pebble **GRect** (x, y, WIDTH,
  HEIGHT), **not** corner coordinates
- `drawRoundRect(x, y, w, h, color, radius [, cornerMask])`
- `drawLine(x0, y0, x1, y1, color, width)`
- `drawCircle(color, cx, cy, radius, startAngle, endAngle)`
- `drawText(text, font, color, x, y)` — `x, y` is the top-left; measure width with
  `render.getTextWidth(text, font)` to center
- `clip(x, y, w, h)` to push a clip, `clip()` (no args) to pop
- `drawDCI(dci, x, y)` — rotate via `dci.clone().rotate(angle, originX, originY)`
  (clone so the source image isn't mutated)

## Widget rules

- **Single render path.** Events mutate `state` and call `drawScreen()`. Don't add
  a second redraw path or per-widget draw logic.
- **Don't paint a background inside a widget.** `drawScreen()` repaints the whole
  background each frame, so leave "empty" regions (e.g. a battery's unfilled area)
  as background — don't over-paint them.
- **Name resources, don't hardcode IDs.** Use `RESOURCES.X` from `resources.js`;
  IDs are positional and must stay in sync with `package.json` `resources.media`
  declaration order.

## Full reference (load on demand when the rules above aren't enough)

These live in the repo's `snippets/` folder (repo root):

- `snippets/poco-rendering.md` — complete Poco API: colors, text (incl. custom
  fonts), shapes, clipping, PDC + GBitmap images, the frame loop.
- `snippets/fonts.md` — every built-in font family and its valid sizes.
- `snippets/watchface-structure.md` — the render loop and time events.
- `snippets/widget-pattern.md` — the widget contract and a new-widget template.
