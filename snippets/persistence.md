# Persistence  **[framework-agnostic]**

Two ways to persist data on the watch. Each app gets its own storage. Sources:
`hellolocalstorage`, `hellokeyvalue`.

## `localStorage` (simplest — strings only)

Web-standard API, implemented on top of key-value storage. **Stores strings**, so
convert in/out.

```js
let counter = Number(localStorage.getItem("counter"));  // null → NaN if unset
if (Number.isNaN(counter)) counter = 1;
else counter += 1;

localStorage.setItem("counter", counter.toString());    // value must be a string
localStorage.removeItem("counter");
```

> The `hellolocalstorage` example checks `null === counter` after `Number(...)`,
> but `Number(null)` is `0` and `Number("")`/missing → `NaN`. Use
> `Number.isNaN(...)` (above) or check `getItem(...) === null` *before* converting.

Use for: user prefs (theme choice, 12/24h override), a persisted wakeup id (see
[`input-and-watch-apis.md`](./input-and-watch-apis.md)).

## ECMA-419 key-value store (`hellokeyvalue`)

Lower-level; can target named settings files and store strings or binary.

```js
const store = device.keyValue.open({ path: "examplesettings", format: "string" });

let counter = store.read("counter");        // undefined if unset
counter = (counter === undefined) ? 1 : Number(counter) + 1;

store.write("counter", counter);
store.delete("counter");
store.close();                               // close when done
```

`format: "string"` here; binary is supported, integer support was noted as future
work. A special mode can open settings files created by built-in apps.

## Which to use

- **`localStorage`** for almost everything — less ceremony, no `open`/`close`.
- **key-value store** when you need binary data or to interoperate with a specific
  Pebble settings file.

Don't write on every redraw — persist only when a value actually changes.
