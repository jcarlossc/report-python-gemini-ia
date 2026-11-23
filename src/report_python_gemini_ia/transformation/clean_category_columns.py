import logging

import pandas as pd


def get_clean_category_columns(
    df: pd.DataFrame,
    columns_dict: dict[str, dict[str, object]],
) -> pd.DataFrame:
    """
    Realiza a limpeza das colunas configuradas como string.

    As operações incluem conversão para StringDtype, remoção de
    espaços excedentes, normalização de espaços consecutivos e
    substituição de strings vazias por valores ausentes.

    A configuração nullable determina se a coluna pode conter
    valores ausentes após a limpeza.

    Args:
        df: DataFrame do pandas que será processado.
        columns_dict: Configurações das colunas carregadas do
            schema YAML.

    Returns:
        pd.DataFrame: Cópia do DataFrame com as colunas textuais
        tratadas.

    Raises:
        TypeError: Se os argumentos ou configurações forem inválidos.
        KeyError: Se uma coluna configurada não existir no DataFrame.
        ValueError: Se uma coluna não permitir valores ausentes
            e apresentar valores nulos após a limpeza.
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

            if config.get("type") != "string":
                continue

            if column not in df_result.columns:
                raise KeyError(f"Coluna configurada não encontrada: {column}")

            nullable = config.get("nullable", True)

            if not isinstance(nullable, bool):
                raise TypeError(f"nullable da coluna '{column}' deve ser bool.")

            # Converte os valores para StringDtype.
            original = df_result[column].astype("string")

            # Executa a normalização textual.
            cleaned = original.str.strip().str.replace(r"\s+", " ", regex=True)

            # Substitui strings vazias por valores ausentes.
            cleaned = cleaned.mask(cleaned.eq(""), pd.NA)

            # Valida a presença de valores ausentes.
            if not nullable and cleaned.isna().any():
                raise ValueError(f"A coluna '{column}' não permite valores nulos.")

            # Identifica alterações sem comparar tipos incompatíveis.
            changed_mask = original.ne(cleaned).fillna(False) | original.isna().ne(
                cleaned.isna()
            )

            changed_count = int(changed_mask.sum())

            # Atualiza a coluna processada.
            df_result[column] = cleaned

            logger.info(
                "Coluna '%s': %d valores tratados.",
                column,
                changed_count,
            )

        logger.info("Limpeza de colunas string concluída com sucesso.")

        return df_result

    except Exception:
        logger.exception("Erro durante a limpeza das colunas string.")
        raise
