import logging

import pandas as pd


def get_clean_datetime_columns(
    df: pd.DataFrame,
    columns_dict: dict[str, dict[str, object]],
) -> pd.DataFrame:
    logger = logging.getLogger(__name__)

    try:
        if not isinstance(df, pd.DataFrame):
            raise TypeError("df deve ser um DataFrame do pandas.")

        if not isinstance(columns_dict, dict):
            raise TypeError("columns_dict deve ser um dicionário.")

        datetime_columns = {
            column: config
            for column, config in columns_dict.items()
            if isinstance(config, dict) and config.get("type") == "datetime"
        }

        df_result = df.copy()

        if not datetime_columns:
            logger.info("Nenhuma coluna datetime encontrada no schema.")
            return df_result

        for column, config in datetime_columns.items():
            if column not in df_result.columns:
                raise KeyError(f"Coluna configurada não encontrada: {column}")

            date_format = config.get("format")

            if date_format is not None and not isinstance(date_format, str):
                raise TypeError(f"format da coluna '{column}' deve ser string.")

            nullable = config.get("nullable", True)

            if not isinstance(nullable, bool):
                raise TypeError(f"nullable da coluna '{column}' deve ser booleano.")

            original = df_result[column].copy()

            cleaned = pd.to_datetime(
                df_result[column],
                format=date_format,
                errors="coerce",
            )

            invalid = cleaned.isna() & original.notna()

            invalid_count = int(invalid.sum())

            if invalid_count:
                logger.warning(
                    "Coluna '%s': %s valor(es) inválido(s) convertido(s) para NaT.",
                    column,
                    invalid_count,
                )

            if not nullable and cleaned.isna().any():
                raise ValueError(f"A coluna '{column}' não permite valores nulos.")

            df_result[column] = cleaned

            logger.info(
                "Coluna '%s' convertida para datetime.",
                column,
            )

        logger.info("Conversão das colunas datetime concluída com sucesso.")

        return df_result

    except Exception:
        logger.exception("Erro durante a conversão das colunas datetime.")

        raise
