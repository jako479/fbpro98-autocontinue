# fbpro98-autocontinue — Test Status

**Test Status: More Tests Needed**

## Covered by automated tests

- INI config loading: valid file parsing, required-file enforcement, missing/invalid settings, and missing `[Settings]` section
- `config_signature` change detection: missing-file handling, stability when unchanged, and detection of file rewrites
- CLI argument parsing and the no-config-found error path returning exit code 1

## Needs tests

- The `auto_continue` watch-and-click loop (manually tested only — depends on the live display and PyAutoGUI screen grab)
- Mid-run config reload behavior and locked-screen back-off
