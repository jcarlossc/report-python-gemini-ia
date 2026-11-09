import pandas as pd
import pytest

from report_python_gemini_ia.ingestion.load_csv import get_load_csv


def test_get_load_csv_success(tmp_path):
    """Testa o carregamento correto de um arquivo CSV."""
    file_csv = tmp_path / "sales.csv"
    file_csv.write_text(
        "name,price\nNotebook,2500\nMouse,100\n",
        encoding="utf-8",
    )

    df = get_load_csv(file_csv)

    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2
    assert list(df.columns) == ["name", "price"]
    assert df.loc[0, "name"] == "Notebook"


def test_get_load_csv_file_not_found(tmp_path):
    """Testa o comportamento quando o arquivo não existe."""
    file_csv = tmp_path / "not_found.csv"

    with pytest.raises(FileNotFoundError):
        get_load_csv(file_csv)


def test_get_load_csv_empty_file(tmp_path):
    """Testa o comportamento de um arquivo CSV vazio."""
    file_csv = tmp_path / "empty.csv"
    file_csv.write_text("", encoding="utf-8")

    with pytest.raises(pd.errors.EmptyDataError):
        get_load_csv(file_csv)


def test_get_load_csv_without_rows(tmp_path):
    """Testa o carregamento de um CSV que possui cabeçalho, mas não possui linhas."""
    file_csv = tmp_path / "no_rows.csv"
    file_csv.write_text("name,price\n", encoding="utf-8")

    df = get_load_csv(file_csv)

    assert isinstance(df, pd.DataFrame)
    assert df.empty
    assert list(df.columns) == ["name", "price"]


def test_get_load_csv_custom_separator(tmp_path):
    """Testa o carregamento utilizando separador personalizado."""
    file_csv = tmp_path / "sales.csv"
    file_csv.write_text(
        "name;price\nNotebook;2500\nMouse;100\n",
        encoding="utf-8",
    )

    df = get_load_csv(file_csv, sep=";")

    assert len(df.columns) == 2
    assert df.loc[0, "name"] == "Notebook"
    assert df.loc[0, "price"] == 2500


def test_get_load_csv_invalid_encoding(tmp_path):
    """Testa o comportamento quando ocorre erro de decodificação."""
    file_csv = tmp_path / "invalid.csv"
    file_csv.write_bytes(b"name,price\n\xff\xfe")

    with pytest.raises(UnicodeDecodeError):
        get_load_csv(file_csv, encoding="utf-8")
