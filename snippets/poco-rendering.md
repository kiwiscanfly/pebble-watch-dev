# Poco rendering API  **[Poco]**

The immediate-mode graphics API our watchface renders with. Everything happens
between `render.begin()` and `render.end()`. Sourced from `hellowatchface`,
`hellopoco-pebbletext`, `hellopoco-text`, `hellopoco-pebblegraphics`,
`hellopoco-pdc*`, `hellopoco-gbitmap`.

## Contents
- Setup & the frame
- Colors
- Text
- Shapes (line, rect, round-rect, circle)
- Clipping
- Images: PDC (vector) and GBitmap (raster)
- Gotchas (from `CLAUDE.md` — these have bitten us)

## Setup & the frame

```js
import Poco from "commodetto/Poco";

const render = new Poco(screen);   // `screen` is a global

// Each frame: begin → paint → end. begin() with no args uses the full display;
// begin(x, y, w, h) restricts the dirty area.
render.begin();
render.fillRectangle(background, 0, 0, render.width, render.height);
// ...draw...
render.end();
```

`render.width` / `render.height` are the display size. `render.unobstructed`
gives the area not covered by system UI (`{ x, y, width, height }`) — center
content against `render.unobstructed.width/height`, not the raw display, so it
stays centered when a system overlay shrinks the canvas.

## Colors

```js
const black = render.makeColor(0, 0, 0);       // r, g, b (0–255)
const accent = render.makeColor(124, 111, 159); // #7C6F9F
```

Make colors **once** (e.g. in `theme.js`), not per frame. On 2-bit displays
(`gabbro`) colors are quantized; design for both color and mono targets.

## Text

```js
const font = new render.Font("Bitham-Bold", 42);   // built-in font — size MUST exist (see fonts.md)
const w = render.getTextWidth(text, font);          // measure for centering
render.drawText(text, font, color, x, y);           // x,y = top-left of the text

// Center horizontally on an anchor:
render.drawText(text, font, color, anchorX - w / 2, y);
```

Custom (Moddable) fonts for arbitrary sizes are loaded differently (from
`hellopoco-text`):

```js
import parseBMF from "commodetto/parseBMF";
import parseRLE from "commodetto/parseRLE";

function getFont(name, size) {
    const font = parseBMF(new Resource(`${name}-${size}.fnt`));
    font.bitmap = parseRLE(new Resource(`${name}-${size}-alpha.bm4`));
    return font;
}
```

`drawText` is UTF-8 aware (multibyte glyphs work given a font that has them).

## Shapes

From `hellopoco-pebblegraphics`. Note the **argument orders differ** between calls
— this is the #1 source of Poco bugs.

```js
// Line: (x0, y0, x1, y1, color, width)
render.drawLine(0, 0, render.width, render.height, gray, 4);

// Filled rect: (color, x, y, w, h)   ← color FIRST
render.fillRectangle(color, x, y, w, h);

// Round-rect OUTLINE: (x, y, w, h, color, radius [, cornerMask])
// cornerMask is a 4-bit field selecting which corners are rounded (default all).
render.drawRoundRect(x, y, w, h, color, radius);
render.drawRoundRect(x, y, w, h, color, radius, 0b0011);

// Round-rect FRAME (1px border): (x, y, w, h, color, radius)
// ← a Pebble GRect: x, y, WIDTH, HEIGHT — NOT corner coords, despite the typings.
render.frameRoundRect(x, y, w, h, color, radius);

// Arc / circle: (color, cx, cy, radius, startAngle, endAngle)
render.drawCircle(color, render.width >> 1, render.height >> 1, 15, start, end);
```

> ⚠️ The TypeScript typings name the rect args `x0, y0, x1, y1`. **They are
> actually `x, y, width, height`.** Passing corner coordinates draws garbage.

## Clipping

```js
render.clip(x, y, w, h);  // push a rectangular clip
// ...draws are masked to that rect...
render.clip();            // pop (no args)
```

Used in our battery widget to mask the fill to the battery interior.

## Images: PDC (vector)

PDC = Pebble Draw Command, our vector format (built from SVG by `svg2pdc`).
From `hellopoco-pdc`, `hellopoco-pdc-rotate`.

```js
// Construct from a resource ID (positional — see resources.js / package.json).
const dci = new Poco.PebbleDrawCommandImage(RESOURCES.ICON);
console.log(`${dci.width} x ${dci.height}`);

// Draw at top-left (x, y). Center it:
render.drawDCI(dci, (render.width - dci.width) / 2, (render.height - dci.height) / 2);

// Rotate (radians) about a pivot, without mutating the original: clone first.
render.drawDCI(dci.clone().rotate(angle, dci.width >> 1, dci.height >> 1), x, y);
```

`.scale(...)` and PDC *sequences* (animated multi-frame PDC) also exist — see the
`hellopoco-pdc-scale` and `hellopoco-pdc-sequence` examples if needed.

## Images: GBitmap (raster PNG)

From `hellopoco-gbitmap`. Use for photographic / background art; prefer PDC for
icons and hands (crisp, rotatable, tiny).

```js
const bitmap = new Poco.PebbleBitmap(RESOURCES.BG);  // resource ID
render.drawBitmap(bitmap, (render.width - bitmap.width) / 2, (render.height - bitmap.height) / 2);
```

## Gotchas (from `CLAUDE.md`)

- **Single render path.** Don't add a second redraw path. Events mutate `state`
  and call `drawScreen()`, which repaints the whole frame.
- **Don't paint an "empty" background inside a widget.** `drawScreen()` already
  fills the background each frame; an unfilled region (e.g. a battery's empty
  portion) should just be left as background, not over-painted black.
- **Never do throwing work at import.** Build images/fonts/sensors in `init()`.
  A throw at module top level silently blanks the entire watch.
- **System font sizes are fixed bitmaps.** An unavailable size fails to load and
  blanks the watch — check [`fonts.md`](./fonts.md).
- Integer-truncate pixel math with `| 0` or `>> 1` to avoid sub-pixel coords.
