# watchface

A Pebble Alloy project — embedded JavaScript on the watch, powered by Moddable
XS, alongside C.

## Building & running

The npm scripts are the primary workflow:

```sh
npm run lint        # ESLint: unused/undefined vars + style checks
npm run lint:fix    # auto-fix the fixable style issues
npm run build       # pebble build (all targetPlatforms)
npm run dev         # build + install to the watch, streaming logs
npm run deploy      # lint, then build + install to the watch
```

`npm run deploy` runs the linter first and stops if it fails, so broken code
doesn't reach the watch. Under the hood these wrap the `pebble` CLI:

```sh
pebble build                          # build for all targetPlatforms
pebble install --emulator emery       # install on the emery emulator
pebble install --cloudpebble --logs   # install to the connected watch + logs
```

## Target platforms

Alloy targets the modern Pebble hardware: **emery** (Pebble Time 2) and
**gabbro** (Pebble Round 2). Other platforms are currently not supported.

## Project layout

```
src/c/mdbl.c                   C glue around the Moddable runtime
src/embeddedjs/main.js         JavaScript that runs on the watch
src/embeddedjs/manifest.json   Moddable manifest
src/pkjs/index.js              PebbleKit JS (phone-side) code
package.json                   Project metadata (UUID, platforms, resources)
wscript                        Build rules — usually no need to edit
```

## Documentation

Full SDK docs and tutorials: <https://developer.repebble.com>
