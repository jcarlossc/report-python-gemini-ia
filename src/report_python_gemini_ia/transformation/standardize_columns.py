import logging
import re
import unicodedata

import pandas as pd


def get_standardize_columns(
    df: pd.DataFrame,
    columns_dict: dict,
    remove_accents: bool = True,
) -> pd.DataFrame:
    """
    Padroniza os nomes das colunas e verifica as colunas obrigatórias.

    Os nomes são convertidos para letras minúsculas, espaços e hifens
    são substituídos por sublinhados, caracteres não suportados são
    removidos e sufixos numéricos garantem nomes únicos.

    O DataFrame original não é modificado.

    Args:
        df: DataFrame cujos nomes serão padronizados.
        columns_dict: dicionário de colunas obrigatórias.
        remove_accents: Indica se os acentos devem ser removidos.

    Returns:
        pd.DataFrame: DataFrame com nomes padronizados e únicos.

    Raises:
        TypeError: Se os argumentos tiverem tipos inválidos.
        KeyError: Se existirem colunas obrigatórias ausentes.
    """

    logger = logging.getLogger(__name__)

    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a pandas DataFrame.")

    if not isinstance(remove_accents, bool):
        raise TypeError("remove_accents must be a boolean.")

    result = df.copy()
    cleaned_names: list[str] = []
    used_names: set[str] = set()

    for column in result.columns:
        name = str(column).strip().lower()

        # Remove os acentos quando solicitado.
        if remove_accents:
            name = unicodedata.normalize("NFKD", name)
            name = "".join(
                character for character in name if not unicodedata.combining(character)
            )

        # Normaliza espaços em branco e hifens.
        name = re.sub(r"[\s-]+", "_", name)

        # Remove caracteres não suportados.
        name = re.sub(r"[^\w]", "", name)

        # Remova os sublinhados do início e do fim.
        name = name.strip("_")

        # Usa um valor padrão para nomes vazios.
        base_name = name or "column"
        unique_name = base_name
        counter = 1

        # Garante que cada nome seja único.
        while unique_name in used_names:
            unique_name = f"{base_name}_{counter}"
            counter += 1

        # Adiciona o nome final à lista de nomes limpos.
        cleaned_names.append(unique_name)

        # Registra o nome no conjunto de nomes já utilizados.
        used_names.add(unique_name)

    # Substitui os nomes das colunas da cópia por nomes limpos e exclusivos.
    result.columns = cleaned_names

    # Identifica as colunas obrigatórias que não existem no DataFrame padronizado.
    missing = [col for col in columns_dict if col not in result.columns]

    # Verifica se existem colunas obrigatórias ausentes.
    if missing:
        logger.warning(f"Colunas ausentes: {missing}")

        raise KeyError(f"Colunas obrigatórias ausentes: {missing}")

    logger.info("Colunas padronizadas com sucesso.")

    return result
