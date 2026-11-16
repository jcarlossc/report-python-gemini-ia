import logging

import pandas as pd


def get_clean_category_columns(
    df: pd.DataFrame,
    columns_dict: dict[str, dict[str, object]],
) -> pd.DataFrame:
    logger = logging.getLogger(__name__)

    try:
        if not isinstance(df, pd.DataFrame):
            raise TypeError("df deve ser um DataFrame do pandas.")

        if not isinstance(columns_dict, dict):
            raise TypeError("columns_dict deve ser um dicionário.")

        category_columns = {
            column: config
            for column, config in columns_dict.items()
            if config.get("type") == "string"
        }

        result = df.copy()

        if not category_columns:
            logger.info("Nenhuma coluna string encontrada no schema.")
            return result

        for column, config in category_columns.items():
            if column not in result.columns:
                raise KeyError(f"Coluna configurada não encontrada: {column}")

            nullable = config.get("nullable", True)

            if not isinstance(nullable, bool):
                raise TypeError(f"nullable da coluna '{column}' deve ser bool.")

            original = result[column].copy()

            cleaned = result[column].astype("string")

            cleaned = cleaned.str.strip()

            cleaned = cleaned.str.replace(r"\s+", " ", regex=True)

            cleaned = cleaned.replace("", pd.NA)

            if not nullable and cleaned.isna().any():
                raise ValueError(f"A coluna '{column}' não permite valores nulos.")

            changed = (original.fillna("\0") != cleaned.fillna("\0")).sum()

            result[column] = cleaned

            logger.info(
                "Coluna '%s': %s valores tratados.",
                column,
                changed,
            )

        logger.info("Limpeza de colunas string concluída com sucesso.")

        return result

    except Exception:
        logger.exception("Erro durante a limpeza das colunas string.")

        raise
