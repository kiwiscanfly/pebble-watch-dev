# Project & resource configuration  **[framework-agnostic]**

How a Moddable Pebble project declares itself, its resources, and its modules.
Reflects **our** `watchface/package.json` and `manifest.json`. Sources:
`hellopoco-pdc`, `hellowatchface`, `piu/watchfaces/*`, our project.

## Contents
- `package.json` → `pebble` block
- Declaring media (resources) + positional IDs
- `manifest.json` module registration
- Per-platform & color-vs-mono assets
- Build/deploy commands

## `package.json` → `pebble`

```jsonc
"pebble": {
  "displayName": "watchface",
  "uuid": "9217a040-…",          // unique per app
  "projectType": "moddable",      // Moddable XS (our setup), not classic C
  "sdkVersion": "3",
  "enableMultiJS": true,          // multiple ES modules (required for our arch)
  "targetPlatforms": ["emery", "gabbro"],   // build targets
  "watchapp": { "watchface": true },        // false = it's an app, not a face
  "messageKeys": ["dummy"],       // AppMessage keys (see comms.md)
  "resources": { "media": [ /* … */ ] }
}
```

- `watchface: true` makes it a face (shows on the watchface carousel); `false`
  makes it a launchable app.
- The maintainer's watch is a **Pebble Time 2 → `emery`**; prefer it for emulator
  and on-device. `gabbro` is the round Pebble Round 2.

## Declaring media + positional resource IDs

```jsonc
"resources": {
  "media": [
    { "type": "raw",    "name": "ICON", "file": "pdc/icon.pdc" },   // PDC vector → "raw"
    { "type": "raw",    "name": "BOLT", "file": "pdc/bolt.pdc" },
    { "type": "bitmap", "name": "IMAGE_MENU_ICON", "file": "img/icon.png", "menuIcon": true }
  ]
}
```

- **PDC** vector files are `"type": "raw"`. **PNG** rasters are `"type": "bitmap"`.
- A `menuIcon: true` bitmap is the icon shown in the launcher/carousel.
- **Resource IDs are positional** — 1-based, in declaration order. The JS loads
  them by *number*: `new Poco.PebbleDrawCommandImage(1)`. **Never hardcode the
  number** — keep `resources.js` (`RESOURCES.ICON = 1`) in sync with this array's
  order, and load via the named constant. Reordering this list silently
  renumbers everything.

Our `npm run assets` converts `resources/svg/*.svg` → `resources/pdc/*.pdc` with
`svg2pdc` before building (the `pdc/` dir is git-ignored, generated). So: commit
the SVG, declare the PDC path here.

## `manifest.json` module registration

Every JS module must be registered or it won't resolve (from `CLAUDE.md`):

```jsonc
{
  "include": ["$(MODDABLE)/examples/manifest_mod.json",
              "$(MODDABLE)/examples/manifest_typings.json"],
  "modules": {
    "*": ["./main", "./theme", "./layout", "./resources", "./dateTime"],  // flat modules
    "widgets/icon": "./widgets/icon",     // namespaced modules, imported as "widgets/icon"
    "widgets/time": "./widgets/time"
  }
}
```

- Flat helper modules go in the `"*"` array.
- Widgets are namespaced (`"widgets/x": "./widgets/x"`) and imported by that name.
- Include `manifest_typings.json` to get Pebble TypeScript typings (and for `.ts`
  sources, `tsc` runs automatically — see `hellotypescript`).
- **Minimize module count** — each module has memory overhead on the watch.

## Per-platform & color-vs-mono assets

Two concepts from the Piu watchfaces, both framework-agnostic:

- **Per-platform asset folders.** Place assets in `src/embeddedjs/<platform>/`
  (e.g. `emery/dial.png`, `flint/dial.png`) and the build picks the right one for
  the target — handy when displays differ in size. `helsinki` even ships a
  per-platform *module* (`emery/layout.js` vs `flint/layout.js`).
- **Color vs mono art sets.** `redmond` ships two art sets and selects at runtime
  with `screen.color` (see [`input-and-watch-apis.md`](./input-and-watch-apis.md)).

## Build / deploy (our `package.json` scripts + `CLAUDE.md`)

```sh
npm run assets    # svg → pdc (svg2pdc)
npm run build     # assets + pebble build (all targetPlatforms)
npm run lint      # eslint (flat config); deploy/dev run this first as a gate
npm run dev       # lint + build + install to watch via cloudpebble, stream logs
npm run deploy    # lint + build + install to watch via cloudpebble

# Raw pebble-tool (run from the project dir):
pebble install --emulator emery        # emulator
pebble install --cloudpebble [--logs]  # physical Pebble Time 2 (via phone app)
pebble publish                          # Rebble Web Services appstore
```

> Installs/builds that are long-running or interactive are the **user's** to run
> (per global instructions) — suggest the command, don't execute it.
