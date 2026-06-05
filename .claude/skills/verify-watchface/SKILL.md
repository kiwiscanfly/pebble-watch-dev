---
name: verify-watchface
description: Build the watchface, capture a screenshot from the emery emulator, and visually verify the result against a cropping/layout/color/design checklist — iterating on the code until it looks right. Use after changing anything that affects how the watchface looks, or when the user asks to check, preview, verify, or screenshot how the watchface renders.
allowed-tools: Read, Edit, Glob, Grep, Bash(cd watchface && npm run build*), Bash(cd watchface && npm run lint*), Bash(pebble screenshot*)
---

# Verify the watchface visually

Building and installing isn't enough — **look at the rendered result and fix it
until it's right.** Poco renders to the same framebuffer the emulator screenshots,
so this works regardless of widget internals.

## The loop

1. **Build:** `cd watchface && npm run lint && npm run build`.
2. **Ensure the emery emulator is running with the latest build.** Per project
   convention, the emulator *install* is the user's to run (it boots a long-running
   QEMU). Ask them to run, or confirm they've run:
   ```sh
   pebble install --emulator emery
   ```
   (If they've authorized you to run installs for this loop, you may.)
3. **Screenshot** (quick, non-interactive — safe to run yourself):
   ```sh
   pebble screenshot --no-open --emulator emery /tmp/watchface_emery.png
   ```
4. **View it:** Read `/tmp/watchface_emery.png` with the Read tool and run the
   checklist below.
5. **Fix and repeat:** if any check fails, edit the code (`theme.js`/`layout.js`/
   the widget), rebuild, have the emulator reloaded, re-screenshot, re-verify.
   **Don't stop until every check passes.**

## Verification checklist

Emery is **200×228**, rectangular, 64-color; center is **(100, 114)**. Our
elements (per the widget set): app icon, time, date, battery indicator.

**A. Cropping — fail if anything is cut off**
- [ ] Every element fully visible; nothing clipped at an edge.
- [ ] No overflow past the bottom (y → 228) or sides (x → 0 / 200); margins intact.
- [ ] Text not truncated — the full time/date string fits.

**B. Positioning — fail if it doesn't match intent**
- [ ] Time where the layout anchor puts it; date below it; battery in its corner.
- [ ] Centered elements actually centered on x=100.
- [ ] Spacing looks deliberate, not crowded or lopsided.

**C. Color & contrast**
- [ ] Colors match `theme.js`; foreground readable on the background.
- [ ] On `gabbro` (if checked) colors survive 2-bit quantization.

**D. Design intent**
- [ ] Matches what the user asked for; key elements prominent; composition balanced.

## Fixing common issues

- **Cropping** → adjust anchors in `layout.js`; remember it derives positions from
  `render.width`/`render.height` (dynamic — never hardcode 200×228).
- **Wrong/blank text** → check the font loads at a valid size (`snippets/fonts.md`);
  a bad `render.Font` size blanks the watch (whole screen empty in the shot).
- **Whole screen blank** → almost always a throw at import or a bad font size; see
  the `pebble-poco-rendering` and `pebble-js-runtime` skills.
- **Element missing** → confirm the widget is in the `widgets[]` array and its
  resource was loaded in `init()`.

## Capturing a preview GIF (animated faces)

For motion or to show a rollover, capture several frames into a GIF:
```sh
python3 watchface/scripts/create_preview_gif.py watchface --frames 8 --delay 400
```
(Requires Pillow and a running emulator. See the `pebble-build-deploy` skill.)

## Related

- `validate-watchface` skill — catch structural errors *before* building.
- `pebble-build-deploy` skill — build/install/publish commands.
- `pebble-poco-rendering`, `pebble-js-runtime` skills — why a watch goes blank.
