# watchface

A Pebble Alloy project — embedded JavaScript on the watch, powered by Moddable
XS, alongside C.

## Building & running

The npm scripts are the primary workflow:

```sh
npm run lint        # ESLint: unused/undefined vars + style checks
npm run lint:fix    # auto-fix the fixable style issues
npm run assets      # convert resources/svg/*.svg -> resources/pdc/*.pdc
npm run build       # assets, then pebble build (all targetPlatforms)
npm run dev         # lint + build + install to the watch, streaming logs
npm run deploy      # lint + build + install to the watch
```

`npm run deploy` runs the linter first and stops if it fails, so broken code
doesn't reach the watch. `build` regenerates vector assets first (see below). Under the hood these wrap the `pebble` CLI:

```sh
pebble build                          # build for all targetPlatforms
pebble install --emulator emery       # install on the emery emulator
pebble install --cloudpebble --logs   # install to the connected watch + logs
```

## Target platforms

Alloy targets the modern Pebble hardware: **emery** (Pebble Time 2) and
**gabbro** (Pebble Round 2). Other platforms are currently not supported.

## Vector icons (SVG → PDC)

Vector graphics are authored as SVG in `resources/svg/` (the source of truth,
viewable on your Mac) and converted to Pebble Draw Command files in
`resources/pdc/` by the [`../svg2pdc`](../svg2pdc) tool. `npm run build` runs the
conversion automatically; `resources/pdc/` is generated and git-ignored.

To use one in `main.js`, declare it in `package.json` under `resources.media`
(`{ "type": "raw", "name": "...", "file": "pdc/<name>.pdc" }`), then load it by
its **numeric resource ID** and draw it:

```js
const icon = new Poco.PebbleDrawCommandImage(1);   // 1 = first media entry
// inside draw():
render.drawDCI(icon, x, y);
```

> Resource IDs are positional (1, 2, 3… in declaration order). If you add more
> media, keep the `PebbleDrawCommandImage(n)` numbers in sync. See the tool's
> README for SVG constraints (limited element set; path curves are approximated).

## Project layout

```
src/c/mdbl.c                   C glue around the Moddable runtime
src/embeddedjs/main.js         JavaScript that runs on the watch
src/embeddedjs/manifest.json   Moddable manifest
src/pkjs/index.js              PebbleKit JS (phone-side) code
resources/svg/*.svg            Vector art (source of truth, committed)
resources/pdc/*.pdc            Generated draw-command files (git-ignored)
package.json                   Project metadata (UUID, platforms, resources)
wscript                        Build rules — usually no need to edit
```

## Documentation

Full SDK docs and tutorials: <https://developer.repebble.com>
