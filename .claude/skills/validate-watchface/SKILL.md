---
name: validate-watchface
description: Statically validate the watchface project before building — checks the architecture invariants ESLint can't see (resources.js ↔ package.json media ID sync, valid built-in font sizes, every widget registered in manifest.json and the render array, resources loaded in init() not at import). Use before a build, after editing resources/manifest/theme/widgets, or to diagnose a blank watch or unresolved-module error.
allowed-tools: Read, Glob, Grep, Bash(cd watchface && npm run validate*), Bash(cd watchface && python3 scripts/validate_watchface.py*)
---

# Validate the watchface

Run the bundled validator from the `watchface/` dir:

```sh
cd watchface && npm run validate
# or: python3 scripts/validate_watchface.py
```

It exits non-zero on errors and is wired into `npm run dev` / `npm run deploy`, so a
broken project can't reach the watch.

## What it checks (the "bitten us" failure modes)

1. **Resource ID sync** — `resources.js` and `package.json` `resources.media` have
   the same count, IDs are contiguous `1..N`, and each `RESOURCES.X = n` lines up
   with the nth media entry. Drift here renders the wrong art or blanks the watch.
2. **Font sizes** — every `new render.Font("Family-Style", size)` uses a size that
   actually exists (table embedded in the script, mirrors `snippets/fonts.md`). A
   bad size blanks the whole watch.
3. **Widget wiring** — every `widgets/<name>.js` is registered in `manifest.json`,
   imported in `main.js`, and present in the `widgets[]` render array. A missing
   link means the module won't resolve or the widget never draws.
4. **Deferred resource loads** — `new Poco.PebbleDrawCommandImage/PebbleBitmap` is
   constructed inside a function (`init()`), never at module top level (a throw at
   import silently blanks the watch).

## When it flags something

The error text says exactly what's wrong and where. Cross-reference:
- font size → `snippets/fonts.md`
- resource IDs → `svg-to-pdc-assets` skill, `snippets/project-config.md`
- widget wiring → `adding-watchface-widget` skill
- init()/blank watch → `pebble-poco-rendering`, `pebble-js-runtime` skills

The validator catches *structural* errors. For *visual* correctness (cropping,
layout, color), use the `verify-watchface` skill after it passes.

Script: `watchface/scripts/validate_watchface.py` (Python 3, stdlib only).
