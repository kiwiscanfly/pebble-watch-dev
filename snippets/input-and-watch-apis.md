# Input & watch APIs  **[framework-agnostic]**

Buttons, vibration, wakeup, and introspecting the watch/screen/device. Sources:
`hellobutton`, `hellovibes`, `hellowakeup`, `helloinfo`, `helloconnected`.

> Watchfaces get **limited** button access (the system owns most button UX). These
> are most relevant for watch-*apps*; documented here because tap/accelerometer and
> wakeup are useful for faces too.

## Buttons (`hellobutton`)

```js
import Button from "pebble/button";

new Button({
    types: ["select", "up", "down", "back"],
    onPush(down, type) {
        // down === true on press, false on release; type is the button name
    }
});
```

## Vibration (`hellovibes`)

```js
import Vibes from "pebble/vibes";

Vibes.shortPulse();
Vibes.longPulse();
Vibes.doublePulse();
Vibes.pattern([100, 100, 150, 50, 50, 150, 1000]); // ms on/off durations
Vibes.cancel();
```

Good for an on-the-hour buzz or a connection-lost alert (gate it so you don't
buzz every redraw).

## Wakeup — scheduled relaunch (`hellowakeup`)

Schedule the app to launch at a future time even if it isn't running. IDs are
persisted (here via `localStorage`) so you can query/cancel later.

```js
import WakeUp from "pebble/wakeup";

// Inspect why we launched:
console.log(`reason ${watch.launch.reason}, args ${watch.launch.arguments}`);
if (watch.wake) {                 // launched BY a wakeup
    console.log(`wake id ${watch.wake.id}, cookie ${watch.wake.cookie}`);
    WakeUp.cancel(watch.wake.id);
}

// Schedule one ~3s out: schedule(timeMs, cookie, notifyIfMissed) → id
const id = WakeUp.schedule(Date.now() + 3000, 12345678, false);

WakeUp.query(id);   // → record or undefined
WakeUp.cancel(id);

// Fired while already running:
watch.addEventListener("wakeup", (wake) => { /* wake.id, wake.cookie */ });
```

## Watch / screen / device introspection (`helloinfo`)

Use these to adapt layout per device (round vs rectangular, color vs mono, 12/24h):

```js
screen.width, screen.height
screen.round            // true on round watches (gabbro)
screen.color            // true on color displays

device.sensor.Touch     // truthy if touch is available

watch.model             // device model string
watch.firmwareVersion   // { major, minor, patch }
watch.hour12            // true if the user prefers 12-hour display ← respect this!
watch.launch.reason     // why the app launched
watch.launch.arguments
```

> `watch.hour12` should drive 12/24-hour formatting instead of hardcoding — our
> `dateTime.js` currently hardcodes 12-hour; a real improvement is to branch on it.

## Connection state (`helloconnected`)

```js
function logConnected() {
    watch.connected.app;        // phone app connected?
    watch.connected.pebblekit;  // PebbleKit-JS connected?
}
watch.addEventListener("connected", logConnected);
logConnected();
```

Useful for a "phone disconnected" indicator, or to gate `fetch()`/AppMessage
([`comms.md`](./comms.md)) on connectivity.
