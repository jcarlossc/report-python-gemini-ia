import re
import unicodedata

import pandas as pd


def get_standardize_columns(
    df: pd.DataFrame,
    remove_accents: bool = True,
) -> pd.DataFrame:
    if not isinstance(df, pd.DataFrame):
        raise TypeError("df deve ser um DataFrame do pandas..")

    if not isinstance(remove_accents, bool):
        raise TypeError("remove_accents deve ser um booleano.")

    result = df.copy()
    cleaned_names: list[str] = []
    used_names: set[str] = set()

    for column in result.columns:
        name = str(column).strip().lower()

        if remove_accents:
            name = unicodedata.normalize("NFKD", name)
            name = "".join(
                character for character in name if not unicodedata.combining(character)
            )

        name = re.sub(r"[\s-]+", "_", name)

        name = re.sub(r"[^\w]", "", name)

        name = name.strip("_")

        base_name = name or "column"
        unique_name = base_name
        counter = 1

        while unique_name in used_names:
            unique_name = f"{base_name}_{counter}"
            counter += 1

        cleaned_names.append(unique_name)

        used_names.add(unique_name)

    result.columns = cleaned_names

    return result
