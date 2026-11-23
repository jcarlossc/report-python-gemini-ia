import logging

import pandas as pd


def get_clean_numeric_columns(
    df: pd.DataFrame,
    columns_dict: dict[str, dict[str, object]],
) -> pd.DataFrame:
    """
    Limpa e converte as colunas numéricas conforme o schema YAML.

    Identifica as colunas configuradas como int64 ou float64,
    converte seus valores para os tipos numéricos correspondentes
    e verifica a existência de valores nulos conforme a configuração.

    Colunas que permitem valores ausentes utilizam os tipos
    anuláveis Int64 e Float64 do pandas.

    O DataFrame original não é modificado.

    Args:
        df: DataFrame que terá suas colunas numéricas limpas.
        columns_dict: Configurações das colunas definidas no schema YAML.

    Returns:
        pd.DataFrame: Cópia do DataFrame com as colunas numéricas tratadas.

    Raises:
        TypeError: Se os argumentos ou configurações forem inválidos.
        KeyError: Se uma coluna numérica configurada estiver ausente.
        ValueError: Se existirem valores nulos em colunas que não permitem
            valores ausentes ou valores fracionários em colunas inteiras.
    """
    logger = logging.getLogger(__name__)

    if not isinstance(df, pd.DataFrame):
        raise TypeError("df deve ser um DataFrame do pandas.")

    if not isinstance(columns_dict, dict):
        raise TypeError("columns_dict deve ser um dicionário.")

    try:
        df_result = df.copy()

        for column, config in columns_dict.items():
            if not isinstance(config, dict):
                raise TypeError(
                    f"Configuração da coluna '{column}' deve ser um dicionário."
                )

            column_type = config.get("type")

            if column_type not in ("int64", "float64"):
                continue

            if column not in df_result.columns:
                raise KeyError(f"Coluna numérica ausente: {column}")

            nullable = config.get("nullable", True)

            if not isinstance(nullable, bool):
                raise TypeError(f"nullable deve ser booleano na coluna: {column}")

            logger.info(
                "Iniciando limpeza numérica da coluna: %s",
                column,
            )

            # Identifica strings vazias e espaços em branco.
            original = df_result[column]

            blank_mask = original.astype("string").str.strip().eq("")

            # Substitui strings vazias por valores ausentes.
            normalized = original.mask(blank_mask, pd.NA)

            # Converte os valores para números.
            numeric = pd.to_numeric(
                normalized,
                errors="coerce",
            )

            # Identifica valores inválidos que não eram nulos.
            invalid_mask = normalized.notna() & numeric.isna()

            invalid_count = int(invalid_mask.sum())

            if invalid_count:
                logger.warning(
                    "Coluna %s: %d valor(es) inválido(s) convertido(s) para nulo.",
                    column,
                    invalid_count,
                )

            # Verifica se a coluna permite valores ausentes.
            null_count = int(numeric.isna().sum())

            if not nullable and null_count:
                raise ValueError(
                    f"Coluna '{column}' não permite valores nulos. "
                    f"Quantidade encontrada: {null_count}."
                )

            # Converte colunas inteiras.
            if column_type == "int64":
                # Identifica valores com casas decimais.
                fractional_mask = numeric.notna() & numeric.mod(1).ne(0)

                if fractional_mask.any():
                    raise ValueError(
                        f"Coluna '{column}' possui valores não inteiros: "
                        f"{numeric[fractional_mask].tolist()}."
                    )

                if nullable:
                    df_result[column] = numeric.astype("Int64")
                else:
                    df_result[column] = numeric.astype("int64")

            # Converte colunas decimais.
            else:
                if nullable:
                    df_result[column] = numeric.astype("Float64")
                else:
                    df_result[column] = numeric.astype("float64")

            # Atualiza a coluna processada.
            df_result[column] = df_result[column]

            logger.info(
                "Limpeza numérica executada: coluna=%s, tipo=%s, "
                "valores inválidos=%d, valores nulos=%d.",
                column,
                column_type,
                invalid_count,
                null_count,
            )

        logger.info("Limpeza numérica concluída com sucesso.")

        return df_result

    except Exception:
        logger.exception("Erro durante a limpeza das colunas numéricas.")
        raise
