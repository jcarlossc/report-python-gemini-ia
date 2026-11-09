import logging
from pathlib import Path

import pandas as pd


def get_load_csv(
    file_csv: Path,
    sep: str = ",",
    encoding: str = "utf-8",
) -> pd.DataFrame:
    logger = logging.getLogger(__name__)

    try:
        logger.info("Iniciando o carregamento do arquivo CSV: %s", file_csv)

        if not file_csv.exists():
            raise FileNotFoundError(f"Arquivo CSV não encontrado: {file_csv}")

        df = pd.read_csv(
            file_csv,
            sep=sep,
            encoding=encoding,
        )

        if df.empty:
            logger.warning("O arquivo CSV não contém linhas.: %s", file_csv)

        logger.info(
            "CSV carregado com sucesso. Linhas: %s | Colunas: %s",
            df.shape[0],
            df.shape[1],
        )

        return df

    except FileNotFoundError:
        logger.exception("Arquivo CSV não encontrado: %s", file_csv)
        raise

    except pd.errors.EmptyDataError:
        logger.exception("O arquivo CSV não contém dados nem cabeçalhos: %s", file_csv)
        raise

    except pd.errors.ParserError:
        logger.exception("Falha ao analisar o arquivo CSV: %s", file_csv)
        raise

    except UnicodeDecodeError:
        logger.exception("Falha ao decodificar arquivo CSV: %s", file_csv)
        raise

    except Exception:
        logger.exception("Erro inesperado ao carregar CSV: %s", file_csv)
        raise
