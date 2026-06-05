# User settings & configuration (Clay)  **[framework-agnostic]**

How to give a watchface a phone-side settings screen and react to it on the watch.
Confirmed replicable in our Moddable-JS context by the modern Alloy docs (the C
skill uses the same Clay config). Sources: developer.repebble.com
(`tutorials/alloy-watchface-tutorial/part6`, `guides/alloy/storage`,
`guides/user-interfaces/app-configuration`).

## The pieces

```
Phone settings UI (Clay)  ──AppMessage──▶  Watch (Message class)  ──▶  localStorage + redraw
   src/pkjs/config.js                         src/embeddedjs/
   src/pkjs/index.js
```

Three moving parts, all using keys that must match across `package.json`
`messageKeys`, the Clay `messageKey` fields, and the watch-side `keys`.

## 1. Define the config UI (`src/pkjs/config.js`)

```js
module.exports = [
    { type: "section", items: [
        { type: "color",  messageKey: "BackgroundColor", defaultValue: "0x000000" },
        { type: "toggle", messageKey: "ShowDate",        defaultValue: true }
    ]},
    { type: "submit", defaultValue: "Save" }
];
```

## 2. Wire Clay on the phone (`src/pkjs/index.js`)

```js
const Clay = require("@rebble/clay");          // pebble package install @rebble/clay
const clayConfig = require("./config");
const clay = new Clay(clayConfig);
```

## 3. Receive + persist on the watch (`src/embeddedjs/`)

```js
import Message from "pebble/message";

const message = new Message({
    keys: ["BackgroundColor", "ShowDate"],
    onReadable() {
        const msg = this.read();
        const bg = msg.get("BackgroundColor");   // Clay color → 0x00RRGGBB int
        if (bg !== undefined) {
            settings.bg = { r: (bg >> 16) & 0xFF, g: (bg >> 8) & 0xFF, b: bg & 0xFF };
        }
        const showDate = msg.get("ShowDate");
        if (showDate !== undefined) settings.showDate = showDate;

        localStorage.setItem("settings", JSON.stringify(settings));
        drawScreen();
    }
});
```

Load with a defaults-merge so old saved data survives adding new settings
(see [`persistence.md`](./persistence.md)):

```js
const DEFAULTS = { bg: { r: 0, g: 0, b: 0 }, showDate: true };
function loadSettings() {
    const stored = localStorage.getItem("settings");
    if (stored) { try { return { ...DEFAULTS, ...JSON.parse(stored) }; } catch {} }
    return { ...DEFAULTS };
}
```

## Fitting our architecture

Settings are **plumbing in `main.js`**, like a sensor: open the `Message` in
`init()`, write parsed values into a `settings` object (or into `state`), then
`drawScreen()`. Widgets read `settings`/`theme` and draw — a color setting flows
into `theme.colors`; a toggle gates whether a widget draws. Keep `theme.js` /
`layout.js` reading from settings rather than hardcoding once this exists.

## Keys checklist

- [ ] each key appears in `package.json` `pebble.messageKeys`
- [ ] same key as the Clay `messageKey`
- [ ] same key in the watch-side `Message({ keys: [...] })`
- [ ] `@rebble/clay` installed (`pebble package install @rebble/clay`)

Docs: developer.repebble.com `tutorials/alloy-watchface-tutorial/part6`,
`guides/user-interfaces/app-configuration`.
