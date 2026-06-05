---
name: watchface-settings
description: Adds a user-configurable setting to the watchface using the Clay config framework — a phone-side settings screen, receiving the value on the watch via AppMessage, persisting it in localStorage, and applying it to theme/layout/widgets. Use when the user wants adjustable options like colors, a 12/24-hour toggle, units, or a settings screen.
allowed-tools: Read, Edit, Write, Glob, Grep, Bash(cd watchface && npm run validate*), Bash(cd watchface && npm run lint*)
---

# Add a configurable setting (Clay)

Same Clay config the C watchface skill uses; confirmed for our Moddable-JS stack by
the Alloy docs (developer.repebble.com `tutorials/alloy-watchface-tutorial/part6`,
`guides/user-interfaces/app-configuration`). Reference depth:
[`snippets/settings.md`](../../../snippets/settings.md),
[`snippets/persistence.md`](../../../snippets/persistence.md).

## The one rule that bites: keys must match in three places

A setting's `messageKey` must be identical in **all** of:
1. `watchface/package.json` → `pebble.messageKeys`
2. the Clay config `messageKey` (phone)
3. the watch-side `Message({ keys: [...] })`

A mismatch silently drops the value. Add the key to all three at once.

## Implement

1. **Install Clay** (one-time): `pebble package install @rebble/clay`.
2. **Define the UI** — `watchface/src/pkjs/config.js`:
   ```js
   module.exports = [
       { type: "section", items: [
           { type: "color",  messageKey: "BackgroundColor", defaultValue: "0x000000" },
           { type: "toggle", messageKey: "Use24Hour",       defaultValue: false }
       ]},
       { type: "submit", defaultValue: "Save" }
   ];
   ```
3. **Wire Clay** — `watchface/src/pkjs/index.js`:
   ```js
   const Clay = require("@rebble/clay");
   const clay = new Clay(require("./config"));
   ```
   (If the proxy is also present for weather, keep both — Clay handles the config
   page; the proxy handles non-config app messages.)
4. **Receive + persist on the watch** — open in `init()`:
   ```js
   import Message from "pebble/message";
   new Message({
       keys: ["BackgroundColor", "Use24Hour"],
       onReadable() {
           const m = this.read();
           const bg = m.get("BackgroundColor");      // 0x00RRGGBB int
           if (bg !== undefined) settings.bg = { r: (bg>>16)&0xFF, g: (bg>>8)&0xFF, b: bg&0xFF };
           const h24 = m.get("Use24Hour");
           if (h24 !== undefined) settings.use24Hour = h24;
           localStorage.setItem("settings", JSON.stringify(settings));
           applySettings();   // rebuild theme colors etc.
           drawScreen();
       }
   });
   ```
5. **Load with a defaults-merge** in `init()` (so adding settings later doesn't
   break saved data):
   ```js
   const DEFAULTS = { bg: { r: 0, g: 0, b: 0 }, use24Hour: false };
   settings = { ...DEFAULTS, ...JSON.parse(localStorage.getItem("settings") || "{}") };
   ```
6. **Apply it.** Route settings into where they belong: a color → `theme.colors`
   (have `theme.js` read from `settings`); a toggle → either gate whether a widget
   draws, or branch a pure formatter (e.g. `use24Hour` in `dateTime.js`).

## Architecture fit

Settings are **plumbing in `main.js`**, like a sensor: `Message` opens in `init()`,
writes into a `settings` object, then `applySettings()` + `drawScreen()`. Widgets
and pure modules read `settings`/`theme`; they don't talk to `Message`. This is the
clean way to honor `watch.hour12` / a 12-24h toggle instead of hardcoding.

## Verify

`cd watchface && npm run validate && npm run lint`, then the `verify-watchface`
skill. To exercise the config page in the emulator: `pebble emu-app-config`
(opens the Clay page in a browser), change a value, confirm the watch redraws.

## Checklist

```
- [ ] key in package.json messageKeys + Clay config + watch Message keys (all three)
- [ ] @rebble/clay installed
- [ ] config.js + Clay wired in src/pkjs/index.js
- [ ] Message opened in init(); value persisted to localStorage
- [ ] defaults-merge on load
- [ ] setting actually applied (theme/widget/formatter), then drawScreen()
- [ ] npm run validate && npm run lint; verified via emu-app-config + verify-watchface
```
