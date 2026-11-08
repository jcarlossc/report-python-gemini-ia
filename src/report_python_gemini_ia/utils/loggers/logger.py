import logging
from pathlib import Path
from typing import Any


def setup_logger(
    logging_config: dict[str, Any],
    show_console: bool = False,
) -> None:
    """
    Configura o registro em um arquivo e, opcionalmente, no console.

    Parâmetros
    ----------
    logging_config : dict[str, Any]
        Dicionário contendo as configurações de registro e logs.
        As chaves obrigatórias são logging.level, logging.format,
        logging.encoding e logs.file.
    show_console : bool, default=False
        Se True, exibe as mensagens de log no console.
        Se False, grava os logs apenas no arquivo.

    Retorna
    -------
    None
        Configura o logger raiz sem retornar um valor.

    Exceções
    ------
    ValueError
        Se a configuração não tiver as chaves obrigatórias ou tiver tipos inválidos.
    OSError
        Se o diretório ou arquivo de log não puder ser criado ou aberto.

    Observações
    -----
    A função usa logging.basicConfig com force=True.
    Os manipuladores existentes no logger raiz são substituídos.
    """

    logger = logging.getLogger(__name__)

    try:
        # Garante que a pasta exista.
        Path(logging_config["logs"]["file"]).parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        # Obtém o nível de registro definido na configuração.
        # Se o nível não existir, utiliza INFO como padrão.
        level = getattr(
            logging,
            logging_config["logging"]["level"],
            logging.INFO,
        )

        # Sempre grava os logs em um arquivo.
        handlers: list[logging.Handler] = [
            logging.FileHandler(
                logging_config["logs"]["file"],
                encoding=logging_config["logging"]["encoding"],
            ),
        ]

        # Adiciona a saída no console apenas quando solicitado explicitamente.
        if show_console:
            handlers.append(logging.StreamHandler())

        # Configura o logger raiz com os manipuladores selecionados.
        logging.basicConfig(
            level=level,
            format=logging_config["logging"]["format"],
            handlers=handlers,
            force=True,
        )

        logger.info("Logger configurado com sucesso.")

    except (KeyError, TypeError) as error:
        # Forneça uma mensagem de erro consistente para configurações inválidas.
        raise ValueError(f"CONFIG_ERROR: invalid configuration -> {error}") from error

    except OSError as error:
        # Preserve o erro original do sistema de arquivos como a causa da exceção.
        raise OSError(
            f"FILE_ERROR: error in the log file.'{logging_config}' -> {error}"
        ) from error
