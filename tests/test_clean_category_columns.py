import pandas as pd
import pytest

from report_python_gemini_ia.transformation.clean_category_columns import (
    get_clean_category_columns,
)


@pytest.fixture
def sample_df() -> pd.DataFrame:
    """Cria um DataFrame para os testes."""
    return pd.DataFrame(
        {
            "order_id": [" ORD-001 ", "ORD-002", "ORD-003"],
            "customer_name": [" Carlos  Silva ", " Maria ", "João"],
            "quantity": [10, 20, 30],
        }
    )


@pytest.fixture
def columns_dict() -> dict[str, dict[str, object]]:
    """Cria as configurações das colunas."""
    return {
        "order_id": {
            "type": "string",
            "nullable": False,
        },
        "customer_name": {
            "type": "string",
            "nullable": False,
        },
        "quantity": {
            "type": "int64",
            "nullable": False,
        },
    }


def test_clean_string_columns(
    sample_df: pd.DataFrame,
    columns_dict: dict[str, dict[str, object]],
) -> None:
    """Remove espaços desnecessários das colunas string."""
    result = get_clean_category_columns(sample_df, columns_dict)

    assert result["order_id"].tolist() == [
        "ORD-001",
        "ORD-002",
        "ORD-003",
    ]

    assert result["customer_name"].tolist() == [
        "Carlos Silva",
        "Maria",
        "João",
    ]


def test_ignore_numeric_columns(
    sample_df: pd.DataFrame,
    columns_dict: dict[str, dict[str, object]],
) -> None:
    """Mantém as colunas numéricas sem alterações."""
    result = get_clean_category_columns(sample_df, columns_dict)

    pd.testing.assert_series_equal(
        result["quantity"],
        sample_df["quantity"],
    )


def test_convert_empty_strings_to_na() -> None:
    """Converte strings vazias em valores ausentes."""
    df = pd.DataFrame(
        {
            "customer_name": ["Carlos", "   ", "Maria"],
        }
    )

    config: dict[str, dict[str, object]] = {
        "customer_name": {
            "type": "string",
            "nullable": True,
        },
    }

    result = get_clean_category_columns(df, config)

    assert pd.isna(result.loc[1, "customer_name"])


def test_preserve_original_dataframe(
    sample_df: pd.DataFrame,
    columns_dict: dict[str, dict[str, object]],
) -> None:
    """Preserva o DataFrame original."""
    original = sample_df.copy()

    get_clean_category_columns(sample_df, columns_dict)

    pd.testing.assert_frame_equal(sample_df, original)


def test_reject_non_dataframe(
    columns_dict: dict[str, dict[str, object]],
) -> None:
    """Rejeita objetos que não sejam DataFrames."""
    with pytest.raises(TypeError, match="DataFrame do pandas"):
        get_clean_category_columns("invalid", columns_dict)  # type: ignore[arg-type]


def test_reject_non_dictionary(
    sample_df: pd.DataFrame,
) -> None:
    """Rejeita configurações que não sejam dicionários."""
    with pytest.raises(TypeError, match="dicionário"):
        get_clean_category_columns(sample_df, [])  # type: ignore[arg-type]


def test_reject_missing_column(
    sample_df: pd.DataFrame,
) -> None:
    """Rejeita colunas configuradas que não existem."""
    config = {
        "customer_email": {
            "type": "string",
            "nullable": True,
        },
    }

    with pytest.raises(KeyError, match="customer_email"):
        get_clean_category_columns(sample_df, config)


def test_reject_null_when_not_nullable() -> None:
    """Rejeita valores ausentes em colunas obrigatórias."""
    df = pd.DataFrame(
        {
            "order_id": ["ORD-001", "   "],
        }
    )

    config = {
        "order_id": {
            "type": "string",
            "nullable": False,
        },
    }

    with pytest.raises(ValueError, match="não permite valores nulos"):
        get_clean_category_columns(df, config)


def test_accept_null_when_nullable() -> None:
    """Aceita valores ausentes em colunas opcionais."""
    df = pd.DataFrame(
        {
            "region": ["North", "   "],
        }
    )

    config = {
        "region": {
            "type": "string",
            "nullable": True,
        },
    }

    result = get_clean_category_columns(df, config)

    assert pd.isna(result.loc[1, "region"])


def test_no_string_columns(
    sample_df: pd.DataFrame,
) -> None:
    """Retorna uma cópia quando não existem colunas string."""
    config = {
        "quantity": {
            "type": "int64",
            "nullable": False,
        },
    }

    result = get_clean_category_columns(sample_df, config)

    pd.testing.assert_frame_equal(result, sample_df)
    assert result is not sample_df
