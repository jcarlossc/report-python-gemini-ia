import logging

import pandas as pd


def get_clean_numeric_columns(
    df: pd.DataFrame,
    columns_dict: dict[str, dict[str, object]],
) -> pd.DataFrame:
    """
    Limpa e converte as colunas numéricas conforme o columns.yaml.

    Identifica as colunas configuradas como int64 ou float64,
    converte seus valores para os tipos numéricos correspondentes
    e verifica a existência de valores nulos conforme a configuração.

    O DataFrame original não é modificado.

    Args:
        df: DataFrame que terá suas colunas numéricas limpas.
        columns_dict: Dicionário de configurações das colunas
            definido no arquivo YAML.

    Returns:
        pd.DataFrame: DataFrame com as colunas numéricas convertidas.

    Raises:
        TypeError: Se os argumentos tiverem tipos inválidos.
        KeyError: Se uma coluna numérica configurada estiver ausente.
        ValueError: Se existirem valores inválidos em colunas
            que não permitem valores nulos ou inteiros não integrais.
    """

    logger = logging.getLogger(__name__)

    try:
        # Verifica se o DataFrame é válido.
        if not isinstance(df, pd.DataFrame):
            raise TypeError("df deve ser um DataFrame do pandas.")

        # Verifica se a configuração das colunas é um dicionário.
        if not isinstance(columns_dict, dict):
            raise TypeError("columns_dict deve ser um dicionário.")

        # Cria uma cópia para preservar o DataFrame original.
        df_result = df.copy()

        # Identifica as colunas configuradas como numéricas.
        numeric_types = {"int64", "float64"}

        numeric_columns = {
            column: config
            for column, config in columns_dict.items()
            if isinstance(config, dict) and config.get("type") in numeric_types
        }

        # Registra quando não existem colunas numéricas para limpar.
        if not numeric_columns:
            logger.info(
                "Limpeza numérica não executada: nenhuma coluna numérica configurada."
            )
            return df_result

        # Percorre as colunas numéricas identificadas.
        for column, config in numeric_columns.items():
            if column not in df_result.columns:
                raise KeyError(f"Coluna numérica ausente: {column}")

            # Verifica se a coluna existe no DataFrame.
            column_type = config["type"]
            nullable = config.get("nullable", True)

            # Valida a configuração de nulidade.
            if not isinstance(nullable, bool):
                raise TypeError(f"nullable deve ser booleano na coluna: {column}")

            # Registra o início da limpeza da coluna.
            logger.info("Iniciando limpeza numérica da coluna: %s", column)

            # Substitui strings vazias ou contendo apenas espaços por nulos.
            original = df_result[column].replace(r"^\s*$", pd.NA, regex=True)

            # Converte os valores para números.
            numeric = pd.to_numeric(original, errors="coerce")

            # Identifica valores inválidos que não eram originalmente nulos.
            invalid = original.notna() & numeric.isna()

            # Registra a quantidade de valores inválidos encontrados.
            invalid_count = int(invalid.sum())

            if invalid_count:
                logger.warning(
                    "Coluna %s: %d valor(es) inválido(s) convertido(s) para nulo.",
                    column,
                    invalid_count,
                )

            # Verifica se a coluna permite valores nulos.
            if not nullable and numeric.isna().any():
                raise ValueError(
                    f"Coluna '{column}' não permite valores nulos. "
                    f"Quantidade encontrada: {int(numeric.isna().sum())}."
                )

            # Verifica se os valores inteiros não possuem casas decimais.
            if column_type == "int64":
                fractional = numeric.notna() & (numeric % 1 != 0)

                if fractional.any():
                    raise ValueError(
                        f"Coluna '{column}' possui valores não inteiros: "
                        f"{numeric[fractional].tolist()}."
                    )

                # Utiliza Int64 quando nulos são permitidos.
                dtype = "Int64" if nullable else "int64"

            else:
                # Utiliza Float64 quando nulos são permitidos.
                dtype = "Float64" if nullable else "float64"

            # Converte a coluna para o tipo numérico definido no YAML.
            df_result[column] = numeric.astype(dtype)

            # Registra a conclusão da limpeza.
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
        # Registra a falha durante o processo de limpeza.
        logger.exception("Erro durante a limpeza das colunas numéricas.")
        raise
