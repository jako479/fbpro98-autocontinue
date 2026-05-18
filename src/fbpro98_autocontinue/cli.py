"""argparse + dispatch for `pnfl auto-continue`."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from fbpro98_autocontinue.config import ConfigError
from fbpro98_autocontinue.main import auto_continue, shutdown


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pnfl auto-continue",
        description="Auto-click the FbPro '98 'Continue' button between plays.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Press CTRL-C to stop. Move the mouse to a screen corner to invoke\n"
            "PyAutoGUI's fail-safe.\n"
            "\n"
            "Settings live in the INI config file and are re-read whenever the\n"
            "file changes, so edits apply while the watcher is running:\n"
            "  MouseMoveDuration     seconds to move the mouse to the button (0.0 = instant)\n"
            "  DelayBeforeContinue   seconds to wait before clicking (-1 disables click)\n"
        ),
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=None,
        help="Use this INI file instead of the default config lookup",
    )
    return parser


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    return build_parser().parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        auto_continue(config_path=args.config)
    except ConfigError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        shutdown()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
