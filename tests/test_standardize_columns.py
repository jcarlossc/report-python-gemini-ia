import pandas as pd
import pytest

from report_python_gemini_ia.transformation.standardize_columns import (
    get_standardize_columns,
)


def test_removes_accents_by_default() -> None:
    """Remove acentos por padrão.."""
    df = pd.DataFrame(columns=["Código", "Preço Médio", "Região"])

    result = get_standardize_columns(df)

    assert result.columns.tolist() == [
        "codigo",
        "preco_medio",
        "regiao",
    ]


def test_preserves_accents_when_disabled() -> None:
    """Preserva os acentos quando remove_accents for False."""
    df = pd.DataFrame(columns=["Código", "Preço Médio"])

    result = get_standardize_columns(df, remove_accents=False)

    assert result.columns.tolist() == [
        "código",
        "preço_médio",
    ]


def test_normalizes_spaces_hyphens_and_uppercase() -> None:
    """Normaliza letras maiúsculas, espaços e hifens."""
    df = pd.DataFrame(columns=[" Total Vendas ", "PREÇO-MÉDIO"])

    result = get_standardize_columns(df)

    assert result.columns.tolist() == [
        "total_vendas",
        "preco_medio",
    ]


def test_removes_special_characters() -> None:
    """Remove caracteres especiais não suportados."""
    df = pd.DataFrame(columns=["Preço ($)", "Produto@ID"])

    result = get_standardize_columns(df)

    assert result.columns.tolist() == [
        "preco",
        "produtoid",
    ]


def test_generates_unique_names() -> None:
    """Adiciona sufixos numéricos quando houver conflito entre nomes normalizados."""
    df = pd.DataFrame(columns=["Total Vendas", "total-vendas", "TOTAL VENDAS"])

    result = get_standardize_columns(df)

    assert result.columns.tolist() == [
        "total_vendas",
        "total_vendas_1",
        "total_vendas_2",
    ]


def test_handles_empty_column_names() -> None:
    """Usa um nome alternativo para nomes de coluna vazios ou inválidos."""
    df = pd.DataFrame(columns=["", "!!!", "   "])

    result = get_standardize_columns(df)

    assert result.columns.tolist() == [
        "column",
        "column_1",
        "column_2",
    ]


def test_handles_dataframe_without_columns() -> None:
    """Lida com um DataFrame sem colunas."""
    df = pd.DataFrame()

    result = get_standardize_columns(df)

    assert result.empty
    assert len(result.columns) == 0


def test_does_not_modify_original_dataframe() -> None:
    """Preserva os nomes das colunas do DataFrame original."""
    df = pd.DataFrame(columns=["Preço Médio", "Total Vendas"])
    original_columns = df.columns.copy()

    get_standardize_columns(df)

    pd.testing.assert_index_equal(df.columns, original_columns)


def test_rejects_non_dataframe() -> None:
    """Lança um TypeError quando df não é um DataFrame."""
    with pytest.raises(TypeError, match="df deve ser um DataFrame do pandas."):
        get_standardize_columns(["Preço"])  # type: ignore[arg-type]


def test_rejects_non_boolean_remove_accents() -> None:
    """Lança TypeError quando remove_accents não é um booleano."""
    df = pd.DataFrame(columns=["Preço"])

    with pytest.raises(TypeError, match="remove_accents"):
        get_standardize_columns(df, remove_accents=1)  # type: ignore[arg-type]


def test_preserves_underscores() -> None:
    """Preserva sublinhados válidos nos nomes das colunas."""
    df = pd.DataFrame(columns=["__Total_Vendas__"])

    result = get_standardize_columns(df)

    assert result.columns.tolist() == ["total_vendas"]
