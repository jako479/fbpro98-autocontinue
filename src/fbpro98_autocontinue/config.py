"""Config dataclass, INI loader, and change detection for auto-continue."""

from __future__ import annotations

import configparser
from dataclasses import dataclass
from importlib import resources
from pathlib import Path

CONFIG_CANDIDATES = [
    Path.cwd() / "auto-continue.dev.ini",
    Path.cwd() / "auto-continue.ini",
    Path.cwd() / "config" / "auto-continue.dev.ini",
    Path.cwd() / "config" / "auto-continue.ini",
]


class ConfigError(Exception):
    """The config file is missing, or present but invalid."""


@dataclass(frozen=True)
class Config:
    mouse_move_duration: float
    delay_before_continue: float


def load_config(path: Path | None = None) -> Config:
    """Read and validate the INI config into a Config.

    The config file is required. Raises ConfigError when no file is found,
    when an explicit `path` does not exist, when the file is not valid INI,
    or when the [Settings] section or either required numeric setting is
    missing or malformed.
    """
    resolved = _resolve_config_path(path)
    cp = configparser.ConfigParser()
    try:
        cp.read(resolved, encoding="utf-8")
    except configparser.Error as error:
        raise ConfigError(f"Config file '{resolved}' is not valid INI: {error}") from error
    if not cp.has_section("Settings"):
        raise ConfigError(f"Config file '{resolved}' is missing the required [Settings] section.")
    return Config(
        mouse_move_duration=_required_float(cp, resolved, "MouseMoveDuration"),
        delay_before_continue=_required_float(cp, resolved, "DelayBeforeContinue"),
    )


def config_signature(path: Path | None = None) -> tuple[str, int, int] | None:
    """Cheap fingerprint of the effective config file: (path, mtime_ns, size).

    Resolves the explicit `path`, or else the first existing candidate.
    Returns None when no config file exists. The value changes iff that file
    changes, letting the watch loop skip re-reading an unchanged INI.
    """
    resolved = path if path is not None else _first_existing_candidate()
    if resolved is None or not resolved.is_file():
        return None
    try:
        stat = resolved.stat()
    except OSError:
        return None
    return (str(resolved), stat.st_mtime_ns, stat.st_size)


def get_runtime_path(filename: str) -> Path:
    """Return the on-disk path to a packaged resource (e.g. continue_button.png)."""
    resource = resources.files("fbpro98_autocontinue") / "images" / filename
    return Path(str(resource))


def _resolve_config_path(path: Path | None) -> Path:
    """Resolve the config file to read, or raise ConfigError if there is none."""
    if path is not None:
        if not path.is_file():
            raise ConfigError(f"Config file not found: '{path}'.")
        return path
    found = _first_existing_candidate()
    if found is None:
        candidates = "\n  ".join(str(c) for c in CONFIG_CANDIDATES)
        raise ConfigError("No config file found. Pass --config, or create one of:\n  " + candidates)
    return found


def _first_existing_candidate() -> Path | None:
    return next((c for c in CONFIG_CANDIDATES if c.is_file()), None)


def _required_float(cp: configparser.ConfigParser, path: Path, key: str) -> float:
    raw = cp.get("Settings", key, fallback=None)
    if raw is None:
        raise ConfigError(f"Config file '{path}' is missing required setting '{key}' in [Settings].")
    try:
        return float(raw)
    except ValueError:
        raise ConfigError(f"Config file '{path}' has an invalid '{key}' value: {raw!r} (expected a number).") from None
