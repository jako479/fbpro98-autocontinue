from __future__ import annotations

from pathlib import Path

import pytest

from fbpro98_autocontinue import config
from fbpro98_autocontinue.cli import main, parse_args
from fbpro98_autocontinue.config import ConfigError


def _write_ini(path: Path, *, mouse_move: str | None = None, delay: str | None = None) -> Path:
    lines = ["[Settings]"]
    if mouse_move is not None:
        lines.append(f"MouseMoveDuration = {mouse_move}")
    if delay is not None:
        lines.append(f"DelayBeforeContinue = {delay}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


# ---------------------------------------------------------------------------
# config: load_config — the config file and both settings are required
# ---------------------------------------------------------------------------


def test_load_config_reads_valid_ini(tmp_path: Path) -> None:
    ini = _write_ini(tmp_path / "auto-continue.ini", mouse_move="0.5", delay="2.5")
    cfg = config.load_config(ini)
    assert cfg.mouse_move_duration == 0.5
    assert cfg.delay_before_continue == 2.5


def test_load_config_errors_when_no_config_found(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    # No --config and no discoverable config file -> error, not defaults.
    monkeypatch.setattr(config, "CONFIG_CANDIDATES", [tmp_path / "auto-continue.ini"])
    with pytest.raises(ConfigError):
        config.load_config()


def test_load_config_errors_when_explicit_path_missing(tmp_path: Path) -> None:
    with pytest.raises(ConfigError):
        config.load_config(tmp_path / "nonexistent.ini")


def test_load_config_succeeds_with_explicit_path_when_no_default(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # A valid --config file works even when no default config file exists.
    monkeypatch.setattr(config, "CONFIG_CANDIDATES", [tmp_path / "missing-default.ini"])
    ini = _write_ini(tmp_path / "explicit.ini", mouse_move="0.3", delay="1.5")
    cfg = config.load_config(ini)
    assert cfg.mouse_move_duration == 0.3
    assert cfg.delay_before_continue == 1.5


def test_load_config_errors_on_missing_setting(tmp_path: Path) -> None:
    # DelayBeforeContinue absent -> error, not a default.
    ini = _write_ini(tmp_path / "auto-continue.ini", mouse_move="0.5")
    with pytest.raises(ConfigError):
        config.load_config(ini)


def test_load_config_errors_on_invalid_value(tmp_path: Path) -> None:
    ini = _write_ini(tmp_path / "auto-continue.ini", mouse_move="fast", delay="2.5")
    with pytest.raises(ConfigError):
        config.load_config(ini)


def test_load_config_errors_on_missing_settings_section(tmp_path: Path) -> None:
    ini = tmp_path / "auto-continue.ini"
    ini.write_text("[Other]\nfoo = 1\n", encoding="utf-8")
    with pytest.raises(ConfigError):
        config.load_config(ini)


# ---------------------------------------------------------------------------
# config: config_signature (change detection for the watch loop)
# ---------------------------------------------------------------------------


def test_config_signature_none_when_file_missing(tmp_path: Path) -> None:
    assert config.config_signature(tmp_path / "nonexistent.ini") is None


def test_config_signature_returns_tuple_for_existing_file(tmp_path: Path) -> None:
    ini = _write_ini(tmp_path / "auto-continue.ini", mouse_move="0.5", delay="1.0")
    sig = config.config_signature(ini)
    assert sig is not None
    assert sig[0] == str(ini)


def test_config_signature_stable_when_file_unchanged(tmp_path: Path) -> None:
    ini = _write_ini(tmp_path / "auto-continue.ini", mouse_move="0.5", delay="1.0")
    assert config.config_signature(ini) == config.config_signature(ini)


def test_config_signature_changes_when_file_rewritten(tmp_path: Path) -> None:
    ini = tmp_path / "auto-continue.ini"
    _write_ini(ini, mouse_move="0.1", delay="1.0")
    before = config.config_signature(ini)
    # Rewrite with a genuinely different-length value so the size component
    # differs — the assertion then holds regardless of the filesystem's
    # mtime resolution between two quick writes.
    _write_ini(ini, mouse_move="0.123456", delay="1.0")
    after = config.config_signature(ini)
    assert before != after


def test_config_signature_resolves_first_existing_candidate(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    missing = tmp_path / "auto-continue.dev.ini"
    present = _write_ini(tmp_path / "auto-continue.ini", mouse_move="0.1", delay="1.0")
    monkeypatch.setattr(config, "CONFIG_CANDIDATES", [missing, present])
    sig = config.config_signature()  # path=None -> candidate resolution
    assert sig is not None
    assert sig[0] == str(present)


# ---------------------------------------------------------------------------
# cli
# ---------------------------------------------------------------------------


def test_parse_args_defaults() -> None:
    args = parse_args([])
    assert args.config is None


def test_parse_args_config_flag() -> None:
    args = parse_args(["--config", "custom.ini"])
    assert args.config == Path("custom.ini")


def test_main_errors_when_no_config_found(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(config, "CONFIG_CANDIDATES", [tmp_path / "auto-continue.ini"])
    exit_code = main([])
    assert exit_code == 1
    assert "error" in capsys.readouterr().err.lower()
