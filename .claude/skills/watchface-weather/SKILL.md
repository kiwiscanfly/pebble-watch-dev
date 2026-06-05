---
name: watchface-weather
description: Adds a weather or other web-data complication to the watchface — phone connectivity via the PebbleKit JS proxy, on-watch fetch()/Location, and a widget that draws the result. Use when the user wants to show weather, temperature, conditions, sunrise, or any internet/web data on the watchface.
allowed-tools: Read, Edit, Write, Glob, Grep, Bash(cd watchface && npm run validate*), Bash(cd watchface && npm run lint*)
---

# Add a weather / web-data complication

Confirmed against the modern Alloy docs (developer.repebble.com
`guides/alloy/networking`, `guides/alloy/sensors-and-input`). On the watch you can
use the web-standard **`fetch()`**; it tunnels through PebbleKit JS on the phone via
the Moddable proxy. The free [Open-Meteo](https://open-meteo.com/) API needs no key.

Reference depth: [`snippets/comms.md`](../../../snippets/comms.md),
[`snippets/sensors.md`](../../../snippets/sensors.md) (Location).

## Prerequisites (one-time project setup)

1. **Add the proxy dependency** to `watchface/package.json` `dependencies` (NOT
   devDependencies — the build only bundles `dependencies`):
   ```json
   "dependencies": { "@moddable/pebbleproxy": "*" }
   ```
2. **Add the phone-side glue** at `watchface/src/pkjs/index.js`:
   ```js
   const moddableProxy = require("@moddable/pebbleproxy");
   Pebble.addEventListener("ready", moddableProxy.readyReceived);
   Pebble.addEventListener("appmessage", function (e) {
       if (moddableProxy.appMessageReceived(e)) return;
       // non-proxy app messages (e.g. Clay settings) handled here
   });
   ```
   The build picks up `src/pkjs/**` (see `wscript`); confirm `enableMultiJS: true`.
3. **For location**, add `"capabilities": ["location"]` to the `pebble` block.

## Implement

4. **Get a fix + fetch** (watch side). Do this in `init()` or on a refresh timer —
   never at module top level:
   ```js
   import Location from "embedded:sensor/Location";

   async function refreshWeather() {
       const here = await new Promise((resolve) => {
           const loc = new Location({ onSample() { resolve(this.sample()); this.close(); } });
       });
       const url = new URL("https://api.open-meteo.com/v1/forecast");
       url.search = new URLSearchParams({
           latitude: here.latitude, longitude: here.longitude,
           current: "temperature_2m,weather_code"
       }).toString();
       const data = await (await fetch(url)).json();
       state.weather = { temp: data.current.temperature_2m | 0, code: data.current.weather_code };
       localStorage.setItem("weather", JSON.stringify(state.weather)); // cache
       if (state.now) drawScreen();
   }
   ```
5. **Add a widget** that reads `state.weather` and draws it
   ([`adding-watchface-widget`](../adding-watchface-widget/SKILL.md) skill +
   `snippets/widget-pattern.md`). Map `weather_code` → an icon/label in a **pure**
   helper so it stays testable.
6. **Seed from cache** in `init()` so a dropped phone connection doesn't blank the
   complication: `state.weather = JSON.parse(localStorage.getItem("weather") || "null")`.

## Refresh cadence (battery)

Refresh **occasionally**, not every `minutechange` — e.g. every 30 min, on the
`connected` event, or on first launch. Gate on `watch.connected.pebblekit`
([`snippets/input-and-watch-apis.md`](../../../snippets/input-and-watch-apis.md))
so you don't fetch while disconnected.

## Architecture fit

Weather is **plumbing in `main.js`** like a sensor: fetch in `init()`/timer, write
into `state.weather`, redraw once `state.now` is set. The widget only draws. Keep
`weather_code → display` logic in a pure module.

## Alternatives & notes

- **Low-level AppMessage** (explicit keys instead of `fetch`) — use the
  `pebble/message` `Message` class; see `snippets/comms.md`. The proxy handles the
  "watch can only send after the phone sends first" handshake automatically; raw
  AppMessage does not.
- **User-configurable units/city** → pair with the `watchface-settings` skill.

## Verify

`cd watchface && npm run validate && npm run lint`, then the `verify-watchface`
skill (screenshot + check the complication renders, with and without a fix).
