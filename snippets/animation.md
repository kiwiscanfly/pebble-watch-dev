# Animation  **[Poco] / [Piu→Poco concept]**

Three ways to add motion, cheapest first. Sourced from `hellopoco-pebblegraphics`,
`hellopoco-pdc-rotate`, `hellopoco-pdc-sequence`, the C watchface skill (the
no-timer pattern), and the modern Alloy/Poco docs
(developer.repebble.com/guides/alloy/poco-guide).

## Contents
- Battery-first rule
- Pattern 1: animation without a timer (minute-frame counter)
- Pattern 2: a timed frame loop (setInterval)
- Pattern 3: rotating/scaling a PDC, and PDC sequences

## Battery-first rule

Continuous sub-second redraws drain the battery. Default to **no animation**;
when you do animate, prefer the no-timer pattern, or run a `setInterval` loop only
in a **brief burst** (e.g. a couple of seconds after a tap or a minute change) and
`clearInterval` when done. Reserve continuous animation for when the user asks.

## Pattern 1: animation without a timer (minute-frame counter)

Borrowed from the C skill: get visual variety **once per minute** with zero extra
redraws by deriving positions from a counter bumped on each `minutechange`. No
timer, no battery cost beyond the redraw you already do.

```js
// in main.js state + the minutechange handler:
state.frame = (state.frame ?? 0);
watch.addEventListener("minutechange", (event) => {
    state.now = event.date;
    state.frame += 1;       // advances once a minute
    drawScreen();
});

// in a widget's draw(ctx, state) — deterministic "drift" per minute:
const x = (i * 37 + state.frame * 7)  % render.width;
const y = 40 + (i * 23 + state.frame * 11) % skyHeight;
```

Each minute the scene shifts; between minutes it's static. Great for ambient faces.

## Pattern 2: a timed frame loop (setInterval)

For true motion. `setInterval` is best-effort — frame rate drops if a frame can't
render in time; ~20fps (50ms) is a realistic target. Keep the single-render-path
discipline: the interval callback is just another thing that calls `drawScreen()`.

```js
let angle = 0;
const spin = setInterval(() => {
    angle += Math.PI / 30;
    state.angle = angle;
    drawScreen();
}, 50);

// stop the burst so it doesn't run forever:
setTimeout(() => clearInterval(spin), 2000);
```

(There is no `PropertyAnimation`/easing framework like C's — you drive frames
yourself. Implement easing in the callback if needed.)

## Pattern 3: rotating/scaling a PDC, and PDC sequences

Rotate or scale a vector image per frame. **Always `.clone()` first** — mutating
the source breaks later draws (from `hellopoco-pdc-rotate`):

```js
render.drawDCI(dci.clone().rotate(angle, dci.width >> 1, dci.height >> 1), x, y);
render.drawDCI(dci.clone().scale(1.5), x, y);
```

For pre-authored animated vector art, use a **PDC sequence** (animated SVG →
multi-frame PDC). Advance its playback frame each tick and redraw — see the
`hellopoco-pdc-sequence` example for the exact playback API
(`Poco.PebbleDrawCommandSequence` + a frame/time advance). Cross-ref
[`analog-hands.md`](./analog-hands.md) for hand-rotation angle math.
