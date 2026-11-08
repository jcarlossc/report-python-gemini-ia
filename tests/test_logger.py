import logging
from pathlib import Path
from typing import Any

import pytest

from report_python_gemini_ia.utils.loggers.logger import setup_logger


@pytest.fixture
def logging_config(tmp_path: Path) -> dict[str, Any]:
    return {
        "logging": {
            "level": "INFO",
            "format": "%(levelname)s - %(message)s",
            "encoding": "utf-8",
        },
        "logs": {
            "file": str(tmp_path / "logs" / "app.log"),
        },
    }


@pytest.fixture(autouse=True)
def clean_root_logger() -> Any:
    yield

    root_logger = logging.getLogger()

    for handler in root_logger.handlers[:]:
        handler.close()
        root_logger.removeHandler(handler)


def test_setup_logger_writes_to_file(
    logging_config: dict[str, Any],
    capsys: pytest.CaptureFixture[str],
) -> None:
    setup_logger(logging_config)

    logging.getLogger("test_application").info("Test message")

    for handler in logging.getLogger().handlers:
        handler.flush()

    log_file = Path(logging_config["logs"]["file"])

    assert log_file.exists()
    assert "Test message" in log_file.read_text(encoding="utf-8")
    assert capsys.readouterr().out == ""


def test_setup_logger_displays_console_output(
    logging_config: dict[str, Any],
    capsys: pytest.CaptureFixture[str],
) -> None:
    setup_logger(logging_config, show_console=True)

    logging.getLogger("test_application").warning("Console message")

    captured = capsys.readouterr()

    assert "Console message" in captured.err


def test_setup_logger_creates_parent_directory(
    logging_config: dict[str, Any],
) -> None:
    setup_logger(logging_config)

    log_file = Path(logging_config["logs"]["file"])

    assert log_file.parent.is_dir()


@pytest.mark.parametrize(
    "invalid_config",
    [
        {},
        {"logging": {}, "logs": {}},
        None,
    ],
)
def test_setup_logger_rejects_invalid_configuration(
    invalid_config: Any,
) -> None:
    with pytest.raises(ValueError, match="CONFIG_ERROR"):
        setup_logger(invalid_config)


def test_setup_logger_wraps_filesystem_errors(
    logging_config: dict[str, Any],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail_mkdir(*args: Any, **kwargs: Any) -> None:
        raise PermissionError("Permission denied")

    monkeypatch.setattr(Path, "mkdir", fail_mkdir)

    with pytest.raises(OSError, match="FILE_ERROR"):
        setup_logger(logging_config)
