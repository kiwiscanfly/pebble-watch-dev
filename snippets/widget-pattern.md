# The widget pattern + new-widget template  **[Poco / our architecture]**

This is **our** convention, not from the Moddable examples — it's the architecture
documented in the root `CLAUDE.md`. A feature = one widget file + one `widgets`
array entry + one `manifest.json` line (+ a resource if it has art).

## The contract

Each widget is a module exporting `draw(ctx, state)`:

- `ctx = { render, theme, layout, images }`
  - `render` — the Poco instance ([`poco-rendering.md`](./poco-rendering.md))
  - `theme` — `{ colors, fonts }` from `theme.js`
  - `layout` — per-element anchors `{ x, y, ... }` from `layout.js`
  - `images` — resources loaded in `main.js` `init()`
- `state` — `{ now, battery, ... }`; widgets **read** it, never own it.

Widgets **only draw**. They don't read sensors, don't call `new Date()`, don't
trigger their own redraw. Pure data→string/number logic goes in a separate module
(like `dateTime.js`) so it stays unit-testable.

## Template: a text widget

```js
// widgets/example.js
import { formatExample } from "dateTime"; // or a dedicated pure module

// One self-contained, background-free draw. drawScreen() already painted the bg.
export function draw(ctx, state) {
    const { render, theme, layout } = ctx;
    const font = theme.fonts.date;
    const text = formatExample(state.now);
    const x = layout.example.x - render.getTextWidth(text, font) / 2; // center on anchor
    render.drawText(text, font, theme.colors.foreground, x, layout.example.y);
}
```

## Template: a widget with its own art + derived color

Mirrors `widgets/battery.js` — pure helper for the data decision, draw for pixels:

```js
// widgets/example.js
const THRESHOLD = 20;

// Pure: testable, no Poco. Export so it can be unit-tested separately.
export function pickColor(value, colors) {
    return value <= THRESHOLD ? colors.low : colors.good;
}

export function draw(ctx, state) {
    const { render, theme, layout, images } = ctx;
    const geom = layout.example;            // { x, y, width, height }
    render.frameRoundRect(geom.x, geom.y, geom.width, geom.height, theme.colors.foreground, 1);
    render.clip(geom.x + 1, geom.y + 1, geom.width - 2, geom.height - 2);
    render.fillRectangle(pickColor(state.example, theme.colors), geom.x + 1, geom.y + 1, 10, geom.height - 2);
    render.drawDCI(images.exampleIcon, geom.x, geom.y);
    render.clip();                          // pop
}
```

## Wiring a new widget in — the four edits

1. **Create** `widgets/example.js` exporting `draw(ctx, state)`.
2. **Register the module** in `manifest.json` (widgets are namespaced):
   ```json
   "widgets/example": "./widgets/example"
   ```
3. **Add to the render list** in `main.js`:
   ```js
   import * as exampleWidget from "widgets/example";
   const widgets = [iconWidget, timeWidget, dateWidget, batteryWidget, exampleWidget];
   ```
4. **If it has art or needs state/layout/theme**, also:
   - add the asset to `package.json` `resources.media` **and** a named ID in
     `resources.js` (keep their order in sync — IDs are positional), load it in
     `main.js` `init()` into `images`;
   - add a layout anchor in `layout.js`;
   - add any new colors/fonts in `theme.js`;
   - if it needs a new data source, extend `state` and update it from the
     relevant event handler in `main.js` (see
     [`watchface-structure.md`](./watchface-structure.md)).

## Checklist (paste into a PR / response)

```
New widget:
- [ ] widgets/<name>.js exports draw(ctx, state); no bg fill; no new Date()
- [ ] pure data logic split into a testable module (no Poco import)
- [ ] registered in manifest.json ("widgets/<name>": "./widgets/<name>")
- [ ] added to the widgets[] array in main.js
- [ ] resources: package.json media + resources.js ID in matching order (if art)
- [ ] resource loaded in init() (not at module top level)
- [ ] layout anchor + theme colors/fonts added (if needed)
- [ ] font sizes verified against fonts.md
- [ ] npm run lint passes; verified in `pebble install --emulator emery`
```
