# Watch ↔ phone communication  **[framework-agnostic]**

Two layers: low-level **AppMessage** (watch↔PebbleKit-JS), and **`fetch()`/
WebSocket** built on top of it via the Moddable proxy. The watch-side JS lives in
`src/embeddedjs/`; the phone-side ("PebbleKit JS" / **pkjs**) lives in
`src/pkjs/index.js`. Sources: `hellomessage`, `hellofetch`.

> **Protocol rule (from the example readme):** the watch can only *send* to the
> phone after it has *received* a message from the phone — this guarantees the pkjs
> code is running. The proxy used by `fetch`/WebSocket handles this for you; if you
> write raw pkjs, send a message when pkjs gets its `ready` event.

## Easiest path: `fetch()` (`hellofetch`)

Watch side — just standard `fetch` (a subset; no Web Streams):

```js
// src/embeddedjs/main.js
const url = new URL("https://api.openweathermap.org/data/2.5/weather");
url.search = new URLSearchParams({ appid, lat: 37.44, lon: -122.14 }).toString();

const response = await fetch(url);   // top-level await is supported
const json = await response.json();
console.log(`${json.name} ${(json.main.temp - 273.15) | 0}°C`);
export {}   // make it a module
```

Phone side — wire up the Moddable proxy (this is the whole file):

```js
// src/pkjs/index.js
const moddableProxy = require("@moddable/pebbleproxy");
Pebble.addEventListener("ready", moddableProxy.readyReceived);
Pebble.addEventListener("appmessage", function (e) {
    if (moddableProxy.appMessageReceived(e)) return;
    // non-proxy events handled here
});
```

> `fetch`/WebSocket require the `@moddable/proxy` package as a **dependency** in
> `package.json` (not devDependency), plus the pkjs glue above. Our project doesn't
> have it yet — add it before using `fetch`.

## Low-level: AppMessage (`hellomessage`)

When you want explicit key/value messaging and full control.

Watch side:

```js
// src/embeddedjs/main.js
import Message from "pebble/message";

const message = new Message({
    keys: ["RANDOM", "DATE", "COUNTER"],
    onReadable() {
        this.read().forEach((value, key) => console.log(`${key}: ${value}`));
    },
    onWritable() {
        if (this.once) return;
        this.once = true;
        const m = new Map();
        m.set("COUNTER", 1000);
        this.write(m);          // send to phone
    },
    onSuspend() {}
});
```

Phone side:

```js
// src/pkjs/index.js
Pebble.addEventListener("ready", function () { send(); });      // send first → unblocks watch
Pebble.addEventListener("appmessage", function (e) {
    const counter = e.payload.COUNTER;
    send();
});
function send() {
    Pebble.sendAppMessage({ RANDOM: (Math.random() * 1e6) | 0, DATE: Date(), COUNTER: ++counter });
}
```

Keys used in messages must be declared in `package.json` → `pebble.messageKeys`
(ours currently has only `"dummy"`).

## Build note (our `wscript`)

The build bundles pkjs from `src/pkjs/**` with `js_entry_file: src/pkjs/index.js`.
So phone-side code goes in `src/pkjs/`, watch-side in `src/embeddedjs/`.

## For a weather complication

`Location` ([`sensors.md`](./sensors.md)) → `fetch()` here → store result in
`state` → a widget draws it ([`widget-pattern.md`](./widget-pattern.md)). Refresh on
a timer or `connected`, not every `minutechange`, to save battery/data. The free
[Open-Meteo API](https://open-meteo.com/) needs no key. Cache the last result in
`localStorage` ([`persistence.md`](./persistence.md)) so a dropped connection
doesn't blank the complication.

Confirmed against the modern Alloy docs: developer.repebble.com
`guides/alloy/networking` (fetch/proxy) and `guides/alloy/sensors-and-input`
(Location). For a user-configurable city/units, see [`settings.md`](./settings.md).
