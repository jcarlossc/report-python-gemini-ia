import logging
from typing import cast

import pandas as pd
import pytest

from report_python_gemini_ia.transformation.clean_numeric_columns import (
    get_clean_numeric_columns,
)


@pytest.fixture
def dataframe() -> pd.DataFrame:
    """Cria um DataFrame de exemplo com valores numéricos e textuais."""
    return pd.DataFrame(
        {
            "quantity": ["10", "20", "30"],
            "unit_price": ["150.50", "200.75", "300.00"],
            "discount_percent": ["5.5", "10.0", "15.0"],
            "customer_name": ["Carlos", "Maria", "João"],
        }
    )


@pytest.fixture
def columns_dict() -> dict[str, dict[str, object]]:
    """Retorna a configuração das colunas."""
    return {
        "quantity": {
            "type": "int64",
            "nullable": False,
        },
        "unit_price": {
            "type": "float64",
        },
        "discount_percent": {
            "type": "float64",
        },
        "customer_name": {
            "type": "string",
        },
    }


def test_clean_numeric_columns(
    dataframe: pd.DataFrame,
    columns_dict: dict[str, dict[str, object]],
) -> None:
    """Converte as colunas numéricas conforme a configuração."""
    result = get_clean_numeric_columns(dataframe, columns_dict)

    assert str(result["quantity"].dtype) == "int64"
    assert str(result["unit_price"].dtype) == "Float64"
    assert str(result["discount_percent"].dtype) == "Float64"


def test_convert_integer_values() -> None:
    """Converte valores textuais para inteiros."""
    df = pd.DataFrame({"quantity": ["10", "20", "30"]})

    config = {"quantity": {"type": "int64", "nullable": False}}

    result = get_clean_numeric_columns(df, config)

    assert result["quantity"].tolist() == [10, 20, 30]


def test_convert_float_values() -> None:
    """Converte valores textuais para decimais."""
    df = pd.DataFrame({"unit_price": ["10.50", "20.75"]})

    config = {"unit_price": {"type": "float64"}}

    result = get_clean_numeric_columns(df, config)

    assert result["unit_price"].tolist() == [10.50, 20.75]


def test_convert_invalid_values_to_null(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Converte valores inválidos para nulo quando permitido."""
    df = pd.DataFrame({"unit_price": ["10.50", "invalid", "20.00"]})

    config = {"unit_price": {"type": "float64", "nullable": True}}

    with caplog.at_level(logging.WARNING):
        result = get_clean_numeric_columns(df, config)

    assert result["unit_price"].isna().sum() == 1
    assert "valor(es) inválido(s)" in caplog.text


def test_reject_null_values_when_not_nullable() -> None:
    """Rejeita valores nulos quando nullable é False."""
    df = pd.DataFrame({"quantity": ["10", "invalid", "30"]})

    config = {"quantity": {"type": "int64", "nullable": False}}

    with pytest.raises(ValueError, match="não permite valores nulos"):
        get_clean_numeric_columns(df, config)


def test_reject_missing_values_when_not_nullable() -> None:
    """Rejeita valores ausentes quando nullable é False."""
    df = pd.DataFrame({"quantity": [10, None, 30]})

    config = {"quantity": {"type": "int64", "nullable": False}}

    with pytest.raises(ValueError, match="não permite valores nulos"):
        get_clean_numeric_columns(df, config)


def test_reject_fractional_values_in_integer_columns() -> None:
    """Rejeita valores com casas decimais em colunas inteiras."""
    df = pd.DataFrame({"quantity": ["10", "20.5", "30"]})

    config = {"quantity": {"type": "int64", "nullable": False}}

    with pytest.raises(ValueError, match="valores não inteiros"):
        get_clean_numeric_columns(df, config)


def test_ignore_non_numeric_columns(
    dataframe: pd.DataFrame,
    columns_dict: dict[str, dict[str, object]],
) -> None:
    """Não executa limpeza numérica em colunas textuais."""
    result = get_clean_numeric_columns(dataframe, columns_dict)

    assert result["customer_name"].tolist() == ["Carlos", "Maria", "João"]


def test_preserve_original_dataframe(
    dataframe: pd.DataFrame,
    columns_dict: dict[str, dict[str, object]],
) -> None:
    """Preserva o DataFrame original durante a limpeza."""
    original = dataframe.copy()

    get_clean_numeric_columns(dataframe, columns_dict)

    pd.testing.assert_frame_equal(dataframe, original)


def test_accept_empty_numeric_columns() -> None:
    """Aceita configurações sem colunas numéricas."""
    df = pd.DataFrame({"customer_name": ["Carlos"]})

    config = {"customer_name": {"type": "string"}}

    result = get_clean_numeric_columns(df, config)

    assert list(result.columns) == ["customer_name"]


def test_reject_non_dataframe() -> None:
    """Rejeita argumentos que não sejam DataFrames."""
    with pytest.raises(TypeError, match="DataFrame do pandas"):
        get_clean_numeric_columns(
            cast(pd.DataFrame, []),
            {},
        )


def test_reject_non_dictionary_config() -> None:
    """Rejeita configurações que não sejam dicionários."""
    df = pd.DataFrame({"quantity": [10]})

    with pytest.raises(TypeError, match="dicionário"):
        get_clean_numeric_columns(
            df,
            cast(dict[str, dict[str, object]], []),
        )


def test_reject_missing_numeric_column() -> None:
    """Rejeita colunas numéricas ausentes no DataFrame."""
    df = pd.DataFrame({"unit_price": [10.50]})

    config = {"quantity": {"type": "int64"}}

    with pytest.raises(KeyError, match="quantity"):
        get_clean_numeric_columns(df, config)


def test_reject_invalid_nullable_configuration() -> None:
    """Rejeita configurações de nullable que não sejam booleanas."""
    df = pd.DataFrame({"quantity": [10]})

    config = {
        "quantity": {
            "type": "int64",
            "nullable": "False",
        }
    }

    with pytest.raises(TypeError, match="nullable deve ser booleano"):
        get_clean_numeric_columns(df, config)
