import logging

import pandas as pd


def get_clean_category_columns(
    df: pd.DataFrame,
    columns_dict: dict[str, dict[str, object]],
) -> pd.DataFrame:
    logger = logging.getLogger(__name__)
    """
    Realiza a limpeza das colunas configuradas como string.

    A função identifica as colunas cujo tipo definido no schema
    YAML é string e executa as seguintes operações:

    - Converte os valores para o tipo string do pandas.
    - Remove espaços no início e no final dos valores.
    - Normaliza espaços consecutivos.
    - Converte strings vazias em valores ausentes (pd.NA).
    - Verifica a configuração nullable de cada coluna.

    Args:
        df: DataFrame do pandas que será processado.
        columns_dict: Dicionário com as configurações das colunas
            carregadas do schema YAML.

    Returns:
        pd.DataFrame: Uma cópia do DataFrame com as colunas
        textuais tratadas.

    Raises:
        TypeError: Se df não for um DataFrame ou columns_dict
            não for um dicionário.
        KeyError: Se uma coluna configurada não existir no DataFrame.
        ValueError: Se uma coluna não aceitar valores ausentes
            e possuir valores nulos após a limpeza.
    """

    try:
        # Verifica se o objeto recebido é um DataFrame do pandas.
        if not isinstance(df, pd.DataFrame):
            raise TypeError("df deve ser um DataFrame do pandas.")

        # Verifica se as configurações foram recebidas como dicionário.
        if not isinstance(columns_dict, dict):
            raise TypeError("columns_dict deve ser um dicionário.")

        # Identifica as colunas configuradas como string.
        category_columns = {
            column: config
            for column, config in columns_dict.items()
            if config.get("type") == "string"
        }

        # Cria uma cópia para preservar o DataFrame original.
        df_result = df.copy()

        # Verifica se existem colunas textuais configuradas.
        if not category_columns:
            logger.info("Nenhuma coluna string encontrada no schema.")
            return df_result

        # Percorre somente as colunas configuradas como string.
        for column, config in category_columns.items():
            # Verifica se a coluna existe no DataFrame.
            if column not in df_result.columns:
                raise KeyError(f"Coluna configurada não encontrada: {column}")

            # Obtém a configuração de valores nulos.
            nullable = config.get("nullable", True)

            # Verifica se nullable é um valor booleano.
            if not isinstance(nullable, bool):
                raise TypeError(f"nullable da coluna '{column}' deve ser bool.")

            # Guarda os valores originais para identificar alterações.
            original = df_result[column].copy()

            # Converte os valores para o tipo string do pandas.
            cleaned = df_result[column].astype("string")

            # Remove espaços no início e no final dos valores.
            cleaned = cleaned.str.strip()

            # Substitui sequências de espaços por apenas um espaço.
            cleaned = cleaned.str.replace(r"\s+", " ", regex=True)

            # Converte strings vazias em valores ausentes.
            cleaned = cleaned.replace("", pd.NA)

            # Verifica se a coluna permite valores ausentes.
            if not nullable and cleaned.isna().any():
                raise ValueError(f"A coluna '{column}' não permite valores nulos.")

            # Conta quantos valores foram modificados pela limpeza.
            changed = (original.fillna("\0") != cleaned.fillna("\0")).sum()

            # Atualiza a coluna no DataFrame resultante.
            df_result[column] = cleaned

            # Registra a quantidade de valores alterados.
            logger.info(
                "Coluna '%s': %s valores tratados.",
                column,
                changed,
            )

        logger.info("Limpeza de colunas string concluída com sucesso.")

        return df_result

    except Exception:
        # Registra a exceção com informações completas do erro.
        logger.exception("Erro durante a limpeza das colunas string.")

        # Propaga a exceção para que possa ser tratada externamente.
        raise
