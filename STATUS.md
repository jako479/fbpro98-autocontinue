# fbpro98-autocontinue — Status

**Status: Complete**

Watches the screen for the Front Page Sports Football Pro '98 'Continue' button and clicks it automatically, freeing the user from clicking through every play during unattended sim runs.

## Implemented

- CLI command `pnfl auto-continue [--config FILE]` registered through the `pnfl` umbrella CLI
- Screen watch loop that locates the 'Continue' button via PyAutoGUI image matching, moves the mouse to it, and clicks
- INI config loading with candidate-path lookup, required `[Settings]` section, and validation of both numeric settings
- Live config reload — the watch loop re-reads the INI only when the file changes on disk (mtime/size fingerprint)
- `MouseMoveDuration` and `DelayBeforeContinue` tuning, including `-1.0` to disable clicking (detect-only mode)
- Resilient runtime behavior — clean Ctrl-C shutdown and back-off when the screen grab fails (e.g. locked workstation)

## Remaining

- Nothing outstanding for the current scope.
