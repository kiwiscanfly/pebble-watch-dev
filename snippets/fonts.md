# Built-in fonts & valid sizes  **[Poco/Piu]**

Pebble ships a fixed set of bitmap fonts. **A `new render.Font(family, size)` with
a size that doesn't exist fails to load and blanks the watch** (see `CLAUDE.md`).
Pick a size from this table, or ship a custom font resource for arbitrary sizes.

Source: the example repo `readme.md` ("Pebble built-in fonts"), verified May 2026.

## Family → style → available sizes

| Family            | Style     | Sizes                  |
| :---------------- | :-------- | :--------------------- |
| Bitham            | Black     | 30                     |
| Bitham            | Bold      | 42                     |
| Bitham            | Light     | 18, 34, 42             |
| Bitham            | Medium    | 34, 42                 |
| Droid Serif       | Bold      | 28                     |
| Gothic            | Bold      | 14, 18, 24, 28, 36     |
| Gothic            | Regular   | 9, 14, 18, 24, 28, 36  |
| Leco              | Bold      | 20, 26, 32, 36, 38     |
| Leco              | Light     | 28                     |
| Leco              | Regular   | 42                     |
| Roboto            | Bold      | 49                     |
| Roboto Condensed  | Regular   | 21                     |

> **Leco** (a clean LCD-style numeric face, great for clocks) ships **only a subset
> of glyphs** — fine for digits/colon, may be missing letters/punctuation.

## Naming in code

The string is `"Family-Style"`; pass the size as the second arg:

```js
new render.Font("Bitham-Bold", 42)        // ✓ exists
new render.Font("Gothic-Regular", 24)     // ✓ exists
new render.Font("Leco-Regular", 42)       // ✓ digits — verify glyph coverage
new render.Font("Bitham-Black", 30)       // ✓
new render.Font("Bitham-Bold", 40)        // ✗ 40 doesn't exist → blank watch
```

In Piu the same fonts are referenced as a CSS-ish style string, e.g.
`font: "bold 18px Gothic"` (see `piu/watchfaces/helsinki` `layout.js`) — not
applicable to our Poco project, listed only to disambiguate when reading examples.

## What we use today

`watchface/src/embeddedjs/theme.js`:
- `time`: `Bitham-Bold` @ **42**
- `date`: `Gothic-Bold` @ **24**

## Need a size that isn't listed?

Use a **custom font resource** (declared in `package.json` media) or a Moddable
BMF font (`parseBMF`/`parseRLE`, see [`poco-rendering.md`](./poco-rendering.md) →
Text). Don't guess a built-in size.
