# fbpro98-autocontinue — Architecture

CLI tool that watches the screen for the FbPro '98 'Continue' button and clicks it automatically, freeing the user from clicking through every play during unattended sim runs.

## Module layout

```
src/fbpro98_autocontinue/
├── __init__.py     # docstring
├── cli.py          # argparse + main()
├── main.py         # auto_continue() orchestration loop, screen helpers
├── config.py       # Config + ConfigError, load_config(), config_signature()
└── images/         # button reference images for pyautogui.locateCenterOnScreen
```

## What this package does

- Provides a CLI: `pnfl auto-continue [--config FILE]`
- Polls the screen for the 'Continue' button using PyAutoGUI's image matcher against `images/continue_button.png`
- When the button is found, moves the mouse to it (over `MouseMoveDuration` seconds) and clicks (after `DelayBeforeContinue` seconds)
- Re-reads the INI only when the config file changes on disk (mtime-gated), so settings can be tuned while the watcher is running
- Backs off cleanly when the screen grab fails (e.g. workstation locked) so the log doesn't flood

## What this package assumes

- Windows host — uses `ctypes.windll.user32` to query screen size with DPI-awareness enabled
- The 'Continue' button is visible on the primary display when it appears
- The bundled reference images in `images/` match the user's display scale and color scheme reasonably well (PyAutoGUI grayscale match at confidence 0.8)

## What this package enforces

CLI-level (raise SystemExit via argparse):

- `--config` if provided is a path

Config (`ConfigError` → CLI prints the message and exits 1):

- A config file is required — no discoverable file and no `--config` is an error
- An explicit `--config` path must exist
- The `[Settings]` section and both numeric settings are required and must parse as numbers
- A mid-run reload that fails validation is logged; the previous settings are kept

Runtime:

- `Ctrl-C` triggers `shutdown()` which prints a fade-out message and exits cleanly
- `pyautogui.ImageNotFoundException` per iteration → silently keep watching
- Any other exception during screen grab → sleep `_LOCKED_SCREEN_BACKOFF` seconds and resume

## What this package does NOT do

- Inspect or modify FbPro '98 game files — the tool only sees pixels
- Detect anything other than the 'Continue' button. The other reference images in `images/` (offense/defense/teams/return) are reserved for future button-aware modes but are not used today.
- Provide a Linux/macOS port — the screen-size helper is Windows-only

## Configuration

Settings live in `auto-continue.ini` (or `.dev.ini`); first found wins:

1. `auto-continue.dev.ini` / `auto-continue.ini` in the current working directory
2. `config/auto-continue.dev.ini` / `config/auto-continue.ini` under the current working directory

| Setting               | Default | Meaning                                                                                     |
| --------------------- | ------- | ------------------------------------------------------------------------------------------- |
| `MouseMoveDuration`   | `0.0`   | Seconds to move the mouse to the button (`0.0` = instant).                                  |
| `DelayBeforeContinue` | `1.0`   | Seconds to wait before clicking. `0.0` clicks instantly, `-1.0` disables clicking entirely. |

The config file and both settings are **required** — a missing file or setting raises `ConfigError`, not a silent fallback; `Default` above is the value the released `config/auto-continue.ini` ships. The INI is the only source for these settings (no CLI overrides). `config_signature()` fingerprints the file (path, mtime, size); the watch loop re-reads the INI only when that changes.

## Testing

`cli.py` and `config.py` have an automated `pytest` suite (argument parsing, `load_config` precedence, `config_signature` change detection). The `auto_continue` watch loop is **manually tested only** — image-recognition correctness depends on the live display state and PyAutoGUI's screen-grab capabilities.

Manual smoke test: launch `pnfl auto-continue`, run a season-sim in FbPro '98, confirm the watcher clicks through plays at the expected pace.
