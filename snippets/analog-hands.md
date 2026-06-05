# Analog clock hands  **[Piu→Poco]**

The `piu/watchfaces/*` examples draw analog faces with Piu `Behavior`s. The Piu
API doesn't apply to us, but the **angle math** does. Below is the math from
`piu/watchfaces/zurich` re-expressed for our **Poco** render path with rotated PDC
hands (see `hellopoco-pdc-rotate`).

## The math

A hand's rotation is a fraction of a full turn (`2π`). Compute the fraction, then
the angle. **12 o'clock is angle 0; clockwise is positive.**

```js
const TAU = Math.PI * 2;

// Fractions of a full revolution (0..1):
function hourFraction(now)   { return ((now.getHours() % 12) + now.getMinutes() / 60) / 12; }
function minuteFraction(now) { return (now.getMinutes() + now.getSeconds() / 60) / 60; }
function secondFraction(now) { return now.getSeconds() / 60; }

// Angle in radians, 12 o'clock = 0, clockwise positive:
const hourAngle = hourFraction(now) * TAU;
```

> Including the lower unit (minutes in the hour hand, seconds in the minute hand)
> makes hands sweep smoothly instead of jumping. Drop it if you only redraw on
> `minutechange` and want discrete ticks.
>
> Zurich computes the angle as `((-fraction * 2) - 1) * Math.PI` — that's the same
> rotation expressed for Piu's hand artwork orientation. With Poco's `.rotate()`
> the clean form above is easier to reason about; adjust by the art's "up"
> orientation if your PDC hand doesn't point up at angle 0.

## Drawing a hand with Poco (rotated PDC)

Hands are PDC vector art (crisp + rotatable + tiny). Clone before rotating so the
source image isn't mutated; rotate about the hand's **pivot** (its base, not its
center), then position the pivot at the watch center.

```js
import Poco from "commodetto/Poco";
const render = new Poco(screen);

const hourHand   = new Poco.PebbleDrawCommandImage(RESOURCES.HOUR_HAND);
const minuteHand = new Poco.PebbleDrawCommandImage(RESOURCES.MINUTE_HAND);

const cx = render.width  >> 1;
const cy = render.height >> 1;

// Pivot within the hand art (where it should rotate about). For Zurich-style
// art this was {cx:7, cy:22} for hour/minute, {cx:12, cy:30} for seconds.
function drawHand(dci, pivotX, pivotY, angle) {
    // rotate(angle, originX, originY) rotates the image about that point;
    // then draw so the pivot lands on the watch center.
    render.drawDCI(dci.clone().rotate(angle, pivotX, pivotY), cx - pivotX, cy - pivotY);
}

function drawScreen(now) {
    render.begin();
    render.fillRectangle(background, 0, 0, render.width, render.height);
    render.drawDCI(dial, (render.width - dial.width) / 2, (render.height - dial.height) / 2);
    drawHand(hourHand,   7, 22, hourFraction(now)   * TAU);
    drawHand(minuteHand, 7, 22, minuteFraction(now) * TAU);
    render.end();
}
```

## Tick rate & power

- **Hour + minute only** → redraw on `minutechange`. Cheap.
- **Second hand** → redraw on `secondchange`. Higher power draw; Zurich only shows
  the second hand on color screens (`screen.color ? ... : null`).

## Concepts worth stealing from the Piu watchfaces

- **Color vs mono asset sets** (`redmond`): ship two art sets and pick by
  `screen.color`. See [`project-config.md`](./project-config.md) → platform assets.
- **Per-platform modules** (`helsinki`): a `emery/layout.js` vs `flint/layout.js`
  resolved per watch model — more efficient than one module branching at runtime.
- **`screen.round`** (from `helloinfo`): round watches (`gabbro`) want centered,
  radial layouts; rectangular (`emery`) can use corners.
