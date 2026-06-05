# JS runtime notes (XS engine on Pebble)  **[framework-agnostic]**

The watch runs **XS** (Moddable's JS engine) under **Hardened JavaScript**, with
some language features stripped to save flash. Code is precompiled to bytecode at
build time. Source: the example repo `readme.md` ("Things you should know" /
"Omitted JavaScript features"), verified May 2026.

## Omitted features — using them throws a "dead strip" exception

Do **not** write watch-side (`src/embeddedjs/`) code that uses:

- `Proxy`, `Reflect` — meta-programming / test frameworks
- `Atomics` — no Web Workers
- `WeakMap`, `WeakSet`
- `BigInt`
- `eval`, `Function` (the constructor), generator functions (`function*`)

These *could* be enabled but aren't today. Everything else in ES2025 is available,
including **`RegExp`**, **`JSON`**, classes, `Map`/`Set`, destructuring, optional
chaining, etc.

## Available and normal

- **Top-level `await`** is supported.
- `Date` and `Math.random()` behave normally (they're exempted from Hardened JS
  determinism).
- **Strict mode** always — no sloppy-mode behaviors.
- **ES modules only** — no CommonJS (`require`) on the watch side. (pkjs / phone
  side *does* use `require`, e.g. `@moddable/pebbleproxy` — different runtime.)

## Hardened JavaScript

All primordials are **immutable** — you cannot monk-patch built-ins
(`Array.prototype.foo = …` will fail). Write code that doesn't mutate globals.

## Web Platform APIs present

`fetch`, `WebSocket`, `URL`, `URLSearchParams`, `Headers`, `localStorage`,
`setTimeout`/`setInterval`/`setImmediate` (+ `clear*`), `console.log`.

## Memory

- Each module carries overhead — **minimize module count** to avoid exhausting
  memory. (Balance against our widget-per-feature arch: keep modules small but
  don't explode their number needlessly.)
- Apps launch instantly because JS is precompiled to a **mod** (bytecode), wrapped
  in a tiny C app (`src/c/mdbl.c`). The mod is the last resource id.

## Practical implications for our code

- Don't reach for `Proxy`/`WeakMap`/`BigInt` in widgets or helpers.
- `timers` (`setInterval`) are fine for, e.g., periodic data refresh — but prefer
  watch events (`minutechange`) for time, and gate timers to save power.
- Keep pure logic in modules and lean on `Map`/`Set`/`RegExp`/`JSON` freely.
