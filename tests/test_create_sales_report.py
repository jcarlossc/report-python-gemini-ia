from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from pydantic import ValidationError

from report_python_gemini_ia.report.create_sales_report import (
    ChartAnalysis,
    SalesReportDocument,
    generate_chart_analysis,
    generate_report_introduction,
    get_chart_data_mapping,
    get_create_sales_report,
    get_report_styles,
)


@pytest.fixture
def analytics() -> dict:
    """Fornece dados analíticos para os testes."""
    return {
        "kpis": {
            "revenue": 3450.0,
            "profit": 690.0,
            "orders": 3,
        },
        "products": {
            "top_revenue": {"Notebook": 2000.0},
            "top_quantity": {"Mouse": 5},
            "lowest_revenue": {"Mouse": 100.0},
        },
        "categories": {
            "revenue": {"Eletrônicos": 2500.0},
            "quantity": {"Eletrônicos": 5},
            "profit": {"Eletrônicos": 500.0},
        },
        "customers": {
            "revenue": {"Carlos": 1500.0},
            "orders": {"Carlos": 2},
            "segments": {"Corporativo": 2},
        },
        "geography": {
            "countries": {"Brasil": 3450.0},
            "regions": {"Nordeste": 3450.0},
        },
        "time": {
            "year": {"2026": 3450.0},
            "month": {"Janeiro": 2150.0},
            "weekday": {"Segunda-feira": 2150.0},
        },
        "payments": {
            "methods": {"Pix": 2},
            "orders": {"Pix": 2},
        },
    }


@pytest.fixture
def chart_analysis() -> ChartAnalysis:
    """Fornece uma análise válida do Gemini."""
    return ChartAnalysis(
        analysis_points=[
            f"Observação analítica número {index}" for index in range(1, 11)
        ],
        conclusion="Resultado positivo nas vendas.",
        recommendations=["Avaliar o desempenho dos produtos."],
    )


@pytest.fixture
def mock_client(chart_analysis: ChartAnalysis) -> MagicMock:
    """Cria um cliente Gemini simulado."""
    client = MagicMock()

    response = MagicMock()
    response.parsed = chart_analysis
    response.text = None

    client.models.generate_content.return_value = response

    return client


def test_chart_analysis_valid(chart_analysis: ChartAnalysis) -> None:
    """Valida a criação de uma análise com dez observações."""
    assert len(chart_analysis.analysis_points) == 10
    assert chart_analysis.conclusion
    assert chart_analysis.recommendations


def test_chart_analysis_requires_ten_points() -> None:
    """Verifica a validação do número mínimo de observações."""
    with pytest.raises(ValidationError):
        ChartAnalysis(
            analysis_points=["Observação insuficiente"],
            conclusion="Conclusão",
            recommendations=[],
        )


def test_get_report_styles() -> None:
    """Verifica a criação dos estilos do relatório."""
    styles = get_report_styles()

    expected_styles = {
        "cover",
        "subtitle",
        "heading",
        "body",
        "point",
        "subheading",
    }

    assert set(styles) == expected_styles


def test_sales_report_document_creation(tmp_path: Path) -> None:
    """Verifica a inicialização do documento ReportLab."""
    output_path = tmp_path / "report.pdf"

    document = SalesReportDocument(output_path)

    assert document.pagesize
    assert document.title == "DataQuantum | Relatório de Vendas"


def test_get_chart_data_mapping(analytics: dict) -> None:
    """Verifica o mapeamento dos dezessete gráficos."""
    mapping = get_chart_data_mapping(analytics)

    assert len(mapping) == 17
    assert "01_kpis" in mapping
    assert "02_products_top_revenue" in mapping
    assert "17_payments_orders" in mapping


def test_get_chart_data_mapping_values(analytics: dict) -> None:
    """Verifica se o mapeamento aponta para os dados corretos."""
    mapping = get_chart_data_mapping(analytics)

    title, data = mapping["01_kpis"]

    assert title == "Indicadores gerais de vendas"
    assert data["revenue"] == 3450.0


def test_generate_chart_analysis(
    mock_client: MagicMock,
    chart_analysis: ChartAnalysis,
) -> None:
    """Verifica a geração de análise pelo Gemini."""
    result = generate_chart_analysis(
        client=mock_client,
        model="gemini-3.5-flash",
        title="Indicadores gerais",
        data={"revenue": 3450.0},
    )

    assert result == chart_analysis

    mock_client.models.generate_content.assert_called_once()


def test_generate_chart_analysis_empty_response() -> None:
    """Verifica o tratamento de resposta vazia do Gemini."""
    client = MagicMock()

    response = MagicMock()
    response.parsed = None
    response.text = None

    client.models.generate_content.return_value = response

    with pytest.raises(
        ValueError,
        match="resposta vazia",
    ):
        generate_chart_analysis(
            client=client,
            model="gemini-3.5-flash",
            title="Indicadores",
            data={"revenue": 100},
        )


def test_generate_chart_analysis_invalid_json() -> None:
    """Verifica o tratamento de JSON inválido."""
    client = MagicMock()

    response = MagicMock()
    response.parsed = None
    response.text = '{"analysis_points":'

    client.models.generate_content.return_value = response

    with pytest.raises(ValidationError):
        generate_chart_analysis(
            client=client,
            model="gemini-3.5-flash",
            title="Indicadores",
            data={"revenue": 100},
        )


def test_generate_report_introduction() -> None:
    """Verifica a geração da introdução do relatório."""
    client = MagicMock()

    response = MagicMock()
    response.text = "Introdução do relatório.\n\nContexto das vendas."

    client.models.generate_content.return_value = response

    result = generate_report_introduction(
        client=client,
        model="gemini-3.5-flash",
        analytics={"kpis": {"revenue": 3450}},
    )

    assert result == "Introdução do relatório.\n\nContexto das vendas."


def test_generate_report_introduction_empty() -> None:
    """Verifica o tratamento de introdução vazia."""
    client = MagicMock()

    response = MagicMock()
    response.text = None

    client.models.generate_content.return_value = response

    with pytest.raises(ValueError, match="introdução"):
        generate_report_introduction(
            client=client,
            model="gemini-3.5-flash",
            analytics={"kpis": {}},
        )


def test_create_sales_report_empty_analytics(tmp_path: Path) -> None:
    """Verifica a rejeição de analytics vazio."""
    with pytest.raises(ValueError, match="analytics"):
        get_create_sales_report(
            analytics={},
            charts={"chart": tmp_path / "chart.png"},
            output_path=tmp_path / "report.pdf",
        )


def test_create_sales_report_empty_charts(
    analytics: dict,
    tmp_path: Path,
) -> None:
    """Verifica a rejeição de gráficos vazios."""
    with pytest.raises(ValueError, match="charts"):
        get_create_sales_report(
            analytics=analytics,
            charts={},
            output_path=tmp_path / "report.pdf",
        )


def test_create_sales_report_invalid_output_path(
    analytics: dict,
    tmp_path: Path,
) -> None:
    """Verifica a validação do caminho de saída."""
    with pytest.raises(TypeError, match="pathlib Path"):
        get_create_sales_report(
            analytics=analytics,
            charts={"chart": tmp_path / "chart.png"},
            output_path="report.pdf",  # type: ignore[arg-type]
        )


def test_create_sales_report_missing_chart(
    analytics: dict,
    tmp_path: Path,
) -> None:
    """Verifica a rejeição de imagem inexistente."""
    with pytest.raises(FileNotFoundError, match="Gráfico não encontrado"):
        get_create_sales_report(
            analytics=analytics,
            charts={"chart": tmp_path / "missing.png"},
            output_path=tmp_path / "report.pdf",
        )


def test_create_sales_report_missing_api_key(
    analytics: dict,
    tmp_path: Path,
) -> None:
    """Verifica a ausência da chave da API Gemini."""
    chart = tmp_path / "chart.png"
    chart.touch()

    with (
        patch.dict("os.environ", {}, clear=True),
        patch("report_python_gemini_ia.report.create_sales_report.load_dotenv"),
    ):
        with pytest.raises(ValueError, match="GEMINI_API_KEY"):
            get_create_sales_report(
                analytics=analytics,
                charts={"chart": chart},
                output_path=tmp_path / "report.pdf",
            )
