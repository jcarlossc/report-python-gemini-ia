import logging
from pathlib import Path
from typing import Any


def setup_logger(
    logging_config: dict[str, Any],
    show_console: bool = False,
) -> None:
    logger = logging.getLogger(__name__)

    try:
        Path(logging_config["logs"]["file"]).parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        level = getattr(
            logging,
            logging_config["logging"]["level"],
            logging.INFO,
        )

        handlers: list[logging.Handler] = [
            logging.FileHandler(
                logging_config["logs"]["file"],
                encoding=logging_config["logging"]["encoding"],
            ),
        ]

        if show_console:
            handlers.append(logging.StreamHandler())

        logging.basicConfig(
            level=level,
            format=logging_config["logging"]["format"],
            handlers=handlers,
            force=True,
        )

        logger.info("Logger configurado com sucesso.")

    except (KeyError, TypeError) as error:
        raise ValueError(f"CONFIG_ERROR: invalid configuration -> {error}") from error

    except OSError as error:
        raise OSError(
            f"FILE_ERROR: error in the log file.'{logging_config}' -> {error}"
        ) from error
