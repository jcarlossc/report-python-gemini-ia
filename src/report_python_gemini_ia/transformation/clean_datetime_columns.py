import logging

import pandas as pd


def get_clean_datetime_columns(
    df: pd.DataFrame,
    columns_dict: dict[str, dict[str, object]],
) -> pd.DataFrame:
    """
    Converte as colunas configuradas como datetime.

    A função identifica as colunas cujo tipo definido no schema
    YAML é datetime e executa as seguintes operações:

    - Converte os valores para datetime64[ns].
    - Utiliza o formato de data definido no YAML, quando informado.
    - Converte valores inválidos em NaT quando nullable=True.
    - Verifica a configuração nullable de cada coluna.
    - Preserva o DataFrame original.

    Args:
        df: DataFrame do pandas que será processado.
        columns_dict: Dicionário com as configurações das colunas
            carregadas do schema YAML.

    Returns:
        pd.DataFrame: Uma cópia do DataFrame com as colunas
        datetime tratadas.

    Raises:
        TypeError: Se df ou columns_dict possuírem tipos inválidos.
        KeyError: Se uma coluna configurada não existir no DataFrame.
        ValueError: Se uma coluna obrigatória possuir valores
            inválidos ou ausentes.
    """

    logger = logging.getLogger(__name__)

    try:
        # Verifica se o objeto recebido é um DataFrame do pandas.
        if not isinstance(df, pd.DataFrame):
            raise TypeError("df deve ser um DataFrame do pandas.")

        # Verifica se as configurações foram recebidas como dicionário.
        if not isinstance(columns_dict, dict):
            raise TypeError("columns_dict deve ser um dicionário.")

        # Identifica as colunas configuradas como datetime.
        datetime_columns = {
            column: config
            for column, config in columns_dict.items()
            if isinstance(config, dict) and config.get("type") == "datetime"
        }

        # Cria uma cópia para preservar o DataFrame original.
        df_result = df.copy()

        # Verifica se existem colunas datetime configuradas.
        if not datetime_columns:
            logger.info("Nenhuma coluna datetime encontrada no schema.")
            return df_result

        # Percorre somente as colunas configuradas como datetime.
        for column, config in datetime_columns.items():
            # Verifica se a coluna existe no DataFrame.
            if column not in df_result.columns:
                raise KeyError(f"Coluna configurada não encontrada: {column}")

            # Obtém o formato de data definido no YAML.
            date_format = config.get("format")

            # Verifica se o formato informado é uma string.
            if date_format is not None and not isinstance(date_format, str):
                raise TypeError(f"format da coluna '{column}' deve ser string.")

            # Obtém a configuração de valores nulos.
            nullable = config.get("nullable", True)

            # Verifica se nullable é um valor booleano.
            if not isinstance(nullable, bool):
                raise TypeError(f"nullable da coluna '{column}' deve ser booleano.")

            # Guarda os valores originais para identificar alterações.
            original = df_result[column].copy()

            # Converte os valores para datetime.
            cleaned = pd.to_datetime(
                df_result[column],
                format=date_format,
                errors="coerce",
            ).astype("datetime64[ns]")

            # Identifica valores inválidos que não eram originalmente nulos.
            invalid = cleaned.isna() & original.notna()

            # Registra a quantidade de valores inválidos.
            invalid_count = int(invalid.sum())

            if invalid_count:
                logger.warning(
                    "Coluna '%s': %s valor(es) inválido(s) convertido(s) para NaT.",
                    column,
                    invalid_count,
                )

            # Verifica se a coluna permite valores ausentes.
            if not nullable and cleaned.isna().any():
                raise ValueError(f"A coluna '{column}' não permite valores nulos.")

            # Atualiza a coluna no DataFrame resultante.
            df_result[column] = cleaned

            # Registra a conclusão da conversão.
            logger.info(
                "Coluna '%s' convertida para datetime.",
                column,
            )

        logger.info("Conversão das colunas datetime concluída com sucesso.")

        return df_result

    except Exception:
        # Registra a exceção com informações completas do erro.
        logger.exception("Erro durante a conversão das colunas datetime.")

        # Propaga a exceção para tratamento externo.
        raise
