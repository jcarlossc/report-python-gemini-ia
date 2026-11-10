import re
import unicodedata

import pandas as pd


def get_standardize_columns(
    df: pd.DataFrame,
    remove_accents: bool = True,
) -> pd.DataFrame:
    """
    Padroniza os nomes das colunas de um DataFrame e garante que sejam únicos.

    Os nomes são convertidos para letras minúsculas, espaços e hifens são substituídos
    por sublinhados, caracteres não suportados são removidos e sufixos numéricos
    são adicionados caso ocorram colisões após a normalização.

    A remoção de acentos está habilitada por padrão, mas pode ser desativada.

    O DataFrame original não é modificado.

    Argumentos:
        df: DataFrame cujos nomes de coluna devem ser padronizados.
        remove_accents: Indica se os acentos devem ser removidos dos nomes das colunas.
            O padrão é True.

    Retorna:
        Uma cópia do DataFrame com nomes de coluna únicos e padronizados.

    Exceções:
        TypeError: Se `df` não for um DataFrame do pandas.
        TypeError: Se `remove_accents` não for um valor booleano.
    """

    if not isinstance(df, pd.DataFrame):
        raise TypeError("df deve ser um DataFrame do pandas.")

    if not isinstance(remove_accents, bool):
        raise TypeError("remove_accents deve ser um booleano.")

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

        # Remova caracteres não suportados.
        name = re.sub(r"[^\w]", "", name)

        # Remove os sublinhados do início e do fim.
        name = name.strip("_")

        # Usa um valor padrão para nomes vazios.
        base_name = name or "column"
        unique_name = base_name
        counter = 1

        # Garanta que cada nome seja único.
        while unique_name in used_names:
            unique_name = f"{base_name}_{counter}"
            counter += 1

        # Adiciona o nome final à lista de nomes limpos.
        cleaned_names.append(unique_name)

        # Registra o nome no conjunto de nomes já utilizados.
        used_names.add(unique_name)

    # Substitui os nomes das colunas da cópia por nomes limpos e exclusivos.
    result.columns = cleaned_names

    return result
