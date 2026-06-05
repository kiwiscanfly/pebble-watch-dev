---
name: adding-watchface-widget
description: Adds a new widget to the Pebble watchface following the project's widget architecture. Use when the user wants to add a complication, indicator, time/date element, or any new drawn element to the watchface in watchface/src/embeddedjs/ — or to refactor existing draw code into a widget.
allowed-tools: Read, Edit, Write, Glob, Grep, Bash(cd watchface && npm run lint*)
---

# Adding a watchface widget

A feature in this watchface is **one widget** wired into a single render path. Each
widget is a module exporting `draw(ctx, state)`, where
`ctx = { render, theme, layout, images }` and `state = { now, battery, ... }`.
Widgets **only draw** — no sensors, no `new Date()`, no own redraw path.

Before writing draw code, the `pebble-poco-rendering` skill and
`snippets/poco-rendering.md` carry the Poco API and the watch-blanking traps.

## The four edits to add a widget

1. **Create `watchface/src/embeddedjs/widgets/<name>.js`** exporting
   `draw(ctx, state)`. Don't fill the background (the render loop already does).
   Put any data→string/number decision in a separate pure module (no Poco import)
   so it stays unit-testable, like `dateTime.js` / `batteryColor()`.

2. **Register the module** in `watchface/src/embeddedjs/manifest.json` (widgets are
   namespaced):
   ```json
   "widgets/<name>": "./widgets/<name>"
   ```

3. **Add it to the render list** in `main.js`:
   ```js
   import * as <name>Widget from "widgets/<name>";
   const widgets = [iconWidget, timeWidget, dateWidget, batteryWidget, <name>Widget];
   ```

4. **If it has art or new data**, also:
   - **Art:** add the asset to `package.json` `resources.media` **and** a named ID
     in `resources.js`, keeping the two in the **same order** (IDs are positional).
     Load it in `main.js` `init()` into `images` — never at module top level.
   - **Layout:** add an anchor in `layout.js`.
   - **Theme:** add colors/fonts in `theme.js`. Verify any font size against
     `snippets/fonts.md` — a missing size blanks the watch.
   - **New data source** (sensor/fetch): open it in `init()`, write into `state`,
     and redraw only once `state.now` is set. See `snippets/sensors.md` /
     `snippets/comms.md`.

## Conventions (these exist because violating them has bitten us)

- **Single render path** — events mutate `state` and call `drawScreen()`, which
  loops `widgets`. No per-feature draw logic or second redraw path.
- **Separate pure logic from drawing** so it's testable.
- **Never do throwing work at import** — resources/sensors load in `init()`.
- **Name resources; don't hardcode IDs.**
- **Register every module in `manifest.json`** or it won't resolve.

## Verify (feedback loop — don't skip)

1. `cd watchface && npm run lint` — must pass (it gates deploy).
2. Build/run in the emulator and eyeball it: `pebble install --emulator emery`
   (this is the user's to run if it's long-running — suggest it). Drive state with
   helpers like `pebble emu-battery --percent N [--charging]`.
3. Add features incrementally and verify each in the emulator before layering on.

## Completion checklist

```
- [ ] widgets/<name>.js exports draw(ctx, state); no bg fill; no new Date()
- [ ] pure data logic split into a testable module (no Poco import)
- [ ] registered in manifest.json
- [ ] added to widgets[] in main.js
- [ ] resources: package.json media + resources.js ID in matching order (if art)
- [ ] resource loaded in init(), not module top level
- [ ] layout anchor + theme colors/fonts added (if needed); font sizes valid
- [ ] npm run lint passes; verified in the emery emulator
```

## Reference

- `snippets/widget-pattern.md` — widget contract + copy-paste templates.
- `snippets/poco-rendering.md`, `snippets/fonts.md` — drawing API + valid fonts.
- `snippets/watchface-structure.md` — render loop + time events.
- `snippets/sensors.md`, `snippets/comms.md` — data-driven widgets.
