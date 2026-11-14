import logging

import pandas as pd


def get_clean_numeric_columns(
    df: pd.DataFrame,
    columns_dict: dict[str, dict[str, object]],
) -> pd.DataFrame:
    logger = logging.getLogger(__name__)

    try:
        if not isinstance(df, pd.DataFrame):
            raise TypeError("df deve ser um DataFrame do pandas.")

        if not isinstance(columns_dict, dict):
            raise TypeError("columns_dict deve ser um dicionário.")

        df_result = df.copy()

        numeric_types = {"int64", "float64"}

        numeric_columns = {
            column: config
            for column, config in columns_dict.items()
            if isinstance(config, dict) and config.get("type") in numeric_types
        }

        if not numeric_columns:
            logger.info(
                "Limpeza numérica não executada: nenhuma coluna numérica configurada."
            )
            return df_result

        for column, config in numeric_columns.items():
            if column not in df_result.columns:
                raise KeyError(f"Coluna numérica ausente: {column}")

            column_type = config["type"]
            nullable = config.get("nullable", True)

            if not isinstance(nullable, bool):
                raise TypeError(f"nullable deve ser booleano na coluna: {column}")

            logger.info("Iniciando limpeza numérica da coluna: %s", column)

            original = df_result[column].replace(r"^\s*$", pd.NA, regex=True)

            numeric = pd.to_numeric(original, errors="coerce")

            invalid = original.notna() & numeric.isna()

            invalid_count = int(invalid.sum())

            if invalid_count:
                logger.warning(
                    "Coluna %s: %d valor(es) inválido(s) convertido(s) para nulo.",
                    column,
                    invalid_count,
                )

            if not nullable and numeric.isna().any():
                raise ValueError(
                    f"Coluna '{column}' não permite valores nulos. "
                    f"Quantidade encontrada: {int(numeric.isna().sum())}."
                )

            if column_type == "int64":
                fractional = numeric.notna() & (numeric % 1 != 0)

                if fractional.any():
                    raise ValueError(
                        f"Coluna '{column}' possui valores não inteiros: "
                        f"{numeric[fractional].tolist()}."
                    )

                dtype = "Int64" if nullable else "int64"

            else:
                dtype = "Float64" if nullable else "float64"

            df_result[column] = numeric.astype(dtype)

            logger.info(
                "Limpeza numérica executada: coluna=%s, tipo=%s, "
                "valores inválidos=%d, valores nulos=%d.",
                column,
                column_type,
                invalid_count,
                int(df_result[column].isna().sum()),
            )

        logger.info("Limpeza numérica concluída com sucesso.")

        return df_result

    except Exception:
        logger.exception("Erro durante a limpeza das colunas numéricas.")
        raise
