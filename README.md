# fbpro98-autocontinue

Watches the screen for the Front Page Sports Football Pro '98 'Continue' button and clicks it automatically. Useful for unattended sim runs — set the watcher running and the game will progress through plays without manual input.

## Setup

```bash
py -3.13 -m venv .venv
.venv\Scripts\activate
py -m pip install -e ".[dev]"
```

## Usage

Distributed via the [`pnfl`](../pnfl) umbrella CLI:

```bash
pnfl auto-continue
pnfl auto-continue --config my-config.ini
```

Press `CTRL-C` to stop. Move the mouse to a screen corner to invoke PyAutoGUI's fail-safe.

Settings live only in the INI config file — `--config` just selects which file. The INI is re-read whenever the file changes on disk, so edits apply while the watcher is running.

Config lookup order (first match wins; `.dev.ini` variants take precedence at each level):

1. `auto-continue.dev.ini` / `auto-continue.ini` in the current working directory
2. `config/auto-continue.dev.ini` / `config/auto-continue.ini` under the current working directory

The config file is required: if none is found and `--config` is not given, the command exits with an error. Both settings must be present and numeric — a missing setting is an error, not a silent fallback.

### Settings

| Key                   | Default | Meaning                                                                  |
| --------------------- | ------- | ------------------------------------------------------------------------ |
| `MouseMoveDuration`   | `0.0`   | Seconds to move the mouse to the button. `0.0` is instant.               |
| `DelayBeforeContinue` | `1.0`   | Seconds to wait before clicking. `0.0` is instant; `-1.0` disables click.|

`-1.0` for `DelayBeforeContinue` is useful when you want the watcher to find the button but let the game progress on its own (e.g. when the game is configured to auto-continue already and you only want detection logging).

## Building a Release

This project is distributed as part of the [`pnfl`](../pnfl) umbrella CLI. See `pnfl/scripts/build_release.py` for release packaging.

## Testing

The CLI and config loading have an automated `pytest` suite. The image-recognition watch loop is tested manually only — its behavior depends on the live display.
