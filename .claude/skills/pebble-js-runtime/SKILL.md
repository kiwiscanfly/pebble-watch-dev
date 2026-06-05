---
name: pebble-js-runtime
description: The JavaScript runtime limits of the XS engine that runs watch-side code in watchface/src/embeddedjs/ — which language features are stripped (and throw at runtime), Hardened JS immutability, ES-modules-only, which Web Platform APIs exist, and memory constraints. Use when writing or debugging watch-side JS, choosing an API, or diagnosing a "dead strip" exception.
paths: watchface/src/embeddedjs/**
allowed-tools: Read, Glob, Grep
---

# Pebble JS runtime (XS engine)

Watch-side code (`watchface/src/embeddedjs/`) runs on Moddable's **XS** engine
under **Hardened JavaScript**, precompiled to bytecode at build time. It is **not**
a full browser/Node environment. (Phone-side `src/pkjs/` is a *different*, standard
JS runtime — `require`, full APIs — these limits don't apply there.)

## Stripped features — using these throws a "dead strip" exception

Do **not** write watch-side code that uses:

- `Proxy`, `Reflect`
- `Atomics` (no Web Workers)
- `WeakMap`, `WeakSet`
- `BigInt`
- `eval`, the `Function` constructor, generator functions (`function*`)

A "dead strip" exception at runtime almost always means one of these slipped in
(often via a dependency or a clever one-liner). Everything else in ES2025 works,
including **`RegExp`**, **`JSON`**, classes, `Map`/`Set`, destructuring, optional
chaining, spread, async/await.

## Hardened JavaScript

All primordials are **immutable** — you can't monkey-patch built-ins
(`Array.prototype.foo = ...` fails). Don't mutate globals or prototypes. `Date` and
`Math.random()` are exempted and behave normally.

## Modules & syntax

- **ES modules only** on the watch side — no CommonJS `require`. (pkjs uses
  `require`; that's the phone runtime.)
- **Strict mode** always.
- **Top-level `await`** is supported.

## Web Platform APIs that exist (subsets)

`fetch`, `WebSocket`, `URL`, `URLSearchParams`, `Headers`, `localStorage`,
`setTimeout`/`setInterval`/`setImmediate` (+ `clear*`), `console.log`.

These are embedded-friendly **subsets** — e.g. `fetch` excludes anything needing
Web Streams. Don't assume a browser API exists; check this list (or
`snippets/js-runtime-notes.md`) before reaching for one.

## Memory

- Each module carries overhead — **minimize module count** to avoid exhausting
  memory. Balance against the one-widget-per-feature architecture: keep modules
  small, but don't multiply them needlessly.
- Apps launch instantly because JS is precompiled to a **mod** (bytecode), wrapped
  in a tiny C app (`src/c/mdbl.c`); the mod is the last resource id.

## Reference

- `snippets/js-runtime-notes.md` — the same constraints with more detail.
- `pebble-poco-rendering` skill — the rendering API (the *what to draw with*; this
  skill is the *what the language allows*).
