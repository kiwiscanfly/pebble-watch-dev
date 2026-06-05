# pebble-watch-dev

Development workspace for **Pebble** watchfaces and apps, targeting the modern
[Core Devices](https://repebble.com) Pebble watches (the 2025 revival running
open-source PebbleOS).

## Hardware target

These projects target the new-generation Pebble hardware. SDK build platforms:

| Watch | Platform | Display |
| --- | --- | --- |
| Pebble Time 2 | `emery` | 64-colour e-paper (primary dev target here) |
| Pebble Round 2 | `gabbro` | round display |

The classic platforms (`aplite`, `basalt`, `chalk`, `diorite`) are still
supported by the SDK for older watches, but the projects here focus on the
modern watches.

## Prerequisites

The Pebble SDK is installed globally via [`uv`](https://docs.astral.sh/uv/):

```sh
uv tool install pebble-tool --python 3.13   # one-time install
pebble sdk install latest                   # install the latest SDK
pebble --version                            # verify (e.g. v5.0.37, SDK v4.9.169)
```

Requires Python 3.10–3.13 and Node.js. On Windows, use WSL/Ubuntu.

Upgrade later with:

```sh
uv tool upgrade pebble-tool --python 3.13
pebble sdk install latest
```

## Building & running a project

From inside a project directory:

```sh
pebble build                     # build for all targetPlatforms
pebble install --emulator emery  # run in the Pebble Time 2 emulator
pebble install --cloudpebble     # install to a physical watch via the phone app
```

### Installing to a physical watch

`--cloudpebble` is the method that works here: it routes the build through the
Pebble mobile app's CloudPebble connection (the watch must be connected to the
app over Bluetooth). No IP address needed.

```sh
pebble install --cloudpebble --logs   # install and stream app logs
```

> The direct `pebble install --phone <ip>` (local Wi-Fi Developer Connection)
> path is documented but was unreliable here (connection refused). Prefer
> `--cloudpebble`.

## Build paths

Two ways to build for Pebble; pick per project:

- **C** — the classic native API. Maximum API coverage; most existing tutorials
  apply directly.
- **Alloy** — newer JavaScript framework built on Moddable XS (runs JS on the
  watch). Faster iteration, but not all C APIs are exposed yet.

## Documentation

- Official SDK docs & tutorials: <https://developer.repebble.com>
- Core Devices / hardware: <https://repebble.com>
- Open-source PebbleOS & SDK: <https://github.com/coredevices>

> Note: `developer.rebble.io` hosts older community docs. The C tutorials there
> are still largely valid, but treat `developer.repebble.com` as the source of
> truth for tooling.
