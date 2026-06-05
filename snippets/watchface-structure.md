# Watchface structure: the loop & time events  **[Poco]**

How a watchface stays current: register for time events, read the date **off the
event**, mutate `state`, repaint. Sourced from `hellowatchface` and the `watch`
event model; aligned to our `main.js`.

## Contents
- The minimal watchface
- Which time event to use
- `event.date`, never `new Date()` in the redraw
- `resize` / `unobstructed`
- Our orchestrator shape

## The minimal watchface (from `hellowatchface`)

```js
import Poco from "commodetto/Poco";

const render = new Poco(screen);
const font = new render.Font("Bitham-Black", 30);
const black = render.makeColor(0, 0, 0);
const white = render.makeColor(255, 255, 255);

function draw(event) {
    render.begin();
    render.fillRectangle(white, 0, 0, render.width, render.height);
    const msg = event.date.toTimeString().slice(0, 8);  // read time off the event
    const w = render.getTextWidth(msg, font);
    render.drawText(msg, font, black,
        (render.unobstructed.width - w) / 2,
        (render.unobstructed.height - font.height) / 2);
    render.end();
}

watch.addEventListener("secondchange", draw);
watch.addEventListener("resize", draw);
```

> The stock example uses `new Date` inside `draw`. **We don't** — see below.

## Which time event?

| Event          | Fires            | Use for |
| :------------- | :--------------- | :------ |
| `secondchange` | every second     | second hands, stopwatch faces (higher power draw) |
| `minutechange` | every minute     | digital time, date — **our default** |
| `daychange`    | at midnight      | date-only updates |
| `resize`       | canvas changes   | recompute layout / repaint when system UI shows/hides |
| `wakeup`       | scheduled wakeup | see [`input-and-watch-apis.md`](./input-and-watch-apis.md) |

Both fire **immediately on registration**, so the first frame paints as soon as you
subscribe — no separate initial draw needed.

## `event.date`, not `new Date()`

`CLAUDE.md` rule: read the time from the event (`event.date`). Event-driven
redraws that aren't time ticks (e.g. a battery sample) reuse the last known
`state.now`. This keeps every widget drawing from one consistent timestamp and
avoids a battery sample racing ahead of the first time paint.

```js
const state = { now: undefined, battery: { percent: 100, charging: false } };

watch.addEventListener("minutechange", (event) => {
    state.now = event.date;   // single source of truth for "now"
    drawScreen();
});
```

## Our orchestrator shape (`main.js`)

```js
const render = new Poco(screen);
const theme  = createTheme(render);
const layout = createLayout(render, theme);

const images = {};            // populated in init()
const state  = { now: undefined, battery: { percent: 100, charging: false } };
const ctx    = { render, theme, layout, images };
const widgets = [iconWidget, timeWidget, dateWidget, batteryWidget];

function drawScreen() {
    render.begin();
    render.fillRectangle(theme.colors.background, 0, 0, render.width, render.height);
    for (let i = 0; i < widgets.length; i++) widgets[i].draw(ctx, state);
    render.end();
}

function init() {
    // load resources / open sensors HERE (never at module top level)
    images.icon = new Poco.PebbleDrawCommandImage(RESOURCES.ICON);
    // ...open Battery sensor, take first sample...
}

init();
watch.addEventListener("minutechange", (event) => { state.now = event.date; drawScreen(); });
```

Key conventions (all from `CLAUDE.md`):
- **One `drawScreen()`** loops the `widgets` array — no per-widget redraw path.
- **`init()` does the throwing work** (resources, sensors), not module top level.
- Widgets are pure-ish `draw(ctx, state)` functions; data→string logic lives in
  separate testable modules (e.g. `dateTime.js`).

## Layout & avoiding cropping

Borrowed discipline from the C watchface skill: **compute positions from the live
canvas, and check every element stays in bounds.** `emery` is **200×228**
(center `100,114`); `gabbro` is round **260×260**. Don't hardcode these.

- Derive from `render.width`/`render.height` (and `render.unobstructed` for the
  usable area), not literals — that's what `layout.js` does. The same layout then
  works across platforms.
- For each element check the **far edge**: `y + height` < `render.height` and
  `x + width` < `render.width`, with a small margin (≈2–5px). Leave margin off the
  bottom/sides so nothing clips.
- Centering: `x = anchorX - render.getTextWidth(text, font) / 2` for text;
  `x = (render.width - element.width) / 2` for images.
- Round watches (`screen.round`, see [`input-and-watch-apis.md`](./input-and-watch-apis.md))
  want radial/centered layouts; corners get clipped by the bezel.

The `verify-watchface` skill checks cropping visually after a build — this is the
math that prevents the failures it would catch.
