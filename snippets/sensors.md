# Sensors (ECMA-419 Sensor pattern)  **[framework-agnostic]**

All Pebble sensors follow the same ECMA-419 "Sensor Class Pattern": construct with
an `onSample` callback, optionally `configure(...)`, call `sample()` to read.
Identical under Poco or Piu. Sources: `hellobattery`, `helloaccelerometer`,
`hellolight`, `hellolocation`.

## Contents
- The pattern
- Battery
- Accelerometer (+ tap)
- Light / backlight
- Location (phone GPS)
- Driving sensors in the emulator
- Fitting a sensor into our architecture

## The pattern

```js
import Sensor from "embedded:sensor/<Name>";

const sensor = new Sensor({
    onSample() {
        const s = this.sample();   // read latest values
        // ...store into `state`, then redraw...
    }
});
sensor.configure({ /* rate / options */ });  // optional
const first = sensor.sample();                // synchronous one-shot read
```

## Battery (`hellobattery`)

```js
import Battery from "embedded:sensor/Battery";

const battery = new Battery({
    onSample() {
        const s = this.sample();
        // s.percent (0–100), s.charging (bool), s.plugged (bool)
    }
});
const s = battery.sample();
```

Our `main.js` opens this in `init()` and only redraws once `state.now` exists, so a
battery sample can't paint before the first time tick. See `widgets/battery.js`.

## Accelerometer (`helloaccelerometer`)

```js
import Accelerometer from "embedded:sensor/Accelerometer";

const accel = new Accelerometer({
    onSample()           { const { x, y, z } = this.sample(); },
    onTap(direction)     { /* single tap */ },
    onDoubleTap(direction) { /* double tap */ }
});
accel.configure({ hz: 10 });   // sample rate
```

Taps are handy for tap-to-reveal seconds / toggle a complication without buttons.

## Light / backlight (`hellolight`)

Not a sensor read — `watch.light(...)` controls the backlight:

```js
watch.light(true);   // force on
watch.light(false);  // force off
watch.light();       // no arg → on temporarily, as if from user interaction
```

## Location (`hellolocation`) — uses the phone's GPS

```js
import Location from "embedded:sensor/Location";

const location = new Location({
    onSample() {
        console.log(JSON.stringify(this.sample())); // { latitude, longitude, ... }
        this.close();   // close when you have what you need
    }
});
// configure() is optional; if used, call it immediately after construction.
location.configure({ enableHighAccuracy: false, timeout: 5000, maximumAge: 0 });
```

Needs the phone connection. For a weather complication, pair this with `fetch()`
([`comms.md`](./comms.md)).

## Driving sensors in the emulator

From `CLAUDE.md` / example comments — set fake values while the emulator runs:

```sh
pebble emu-battery --percent 20 --charging
# example-repo form (note the --qemu target):
#   pebble emu-battery --percent 20 --charging --qemu localhost:12344
#   rebble emu-accel tilt-left --qemu localhost:12344
```

## Fitting a sensor into our architecture

A sensor is **plumbing in `main.js`**, not a widget. The widget only draws:

1. Open the sensor in `main.js` `init()` (never at module top level — a throw
   there blanks the watch).
2. In `onSample`, write values into `state` and call `drawScreen()` **only if**
   `state.now` is set (don't outrun the first time paint).
3. Add a widget that reads those `state` fields and draws them
   ([`widget-pattern.md`](./widget-pattern.md)).
4. Keep any data→display decision (thresholds, formatting) in a pure exported
   helper so it's unit-testable, like `batteryColor(...)`.
