from __future__ import annotations

import logging
import os
from dotenv import load_dotenv
from pathlib import Path
from typing import Any, cast
from xml.sax.saxutils import escape

from google import genai

from pydantic import BaseModel, Field

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    Image,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
)
from reportlab.platypus.tableofcontents import TableOfContents


logger = logging.getLogger(__name__)

NAVY = "#022287"
CYAN = "#3ADDF7"
DARK = "#010417"
GRAY = "#979DAC"


# ---------------------------------------------------------
# 1. MODELO DA RESPOSTA DO GEMINI
# ---------------------------------------------------------


class ChartAnalysis(BaseModel):
    """Estrutura validada da análise produzida pelo Gemini."""

    analysis_points: list[str] = Field(
        min_length=10,
        description="Pelo menos dez observações analíticas fundamentadas nos dados.",
    )

    conclusion: str = Field(
        description="Conclusão objetiva sobre os indicadores analisados.",
    )

    recommendations: list[str] = Field(
        description="Orientações práticas, quando sustentadas pelos dados.",
    )


# ---------------------------------------------------------
# 2. DOCUMENTO COM SUMÁRIO AUTOMÁTICO
# ---------------------------------------------------------


class SalesReportDocument(BaseDocTemplate):
    """Documento ReportLab com sumário e numeração de páginas."""

    def __init__(self, filename: str | Path) -> None:
        super().__init__(
            str(filename),
            pagesize=A4,
            rightMargin=1.8 * cm,
            leftMargin=1.8 * cm,
            topMargin=1.8 * cm,
            bottomMargin=1.8 * cm,
            title="DataQuantum | Relatório de Vendas",
            author="DataQuantum",
        )

        frame = Frame(
            self.leftMargin,
            self.bottomMargin,
            self.width,
            self.height,
            id="normal",
        )

        template = PageTemplate(
            id="report",
            frames=[frame],
            onPage=self._draw_footer,
        )

        self.addPageTemplates([template])

    @staticmethod
    def _draw_footer(canvas: Any, document: Any) -> None:
        """Desenha rodapé e número da página."""

        canvas.saveState()

        canvas.setStrokeColor(colors.HexColor(CYAN))
        canvas.line(1.8 * cm, 1.35 * cm, 19.2 * cm, 1.35 * cm)

        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.HexColor(GRAY))

        canvas.drawString(
            1.8 * cm,
            0.9 * cm,
            "DataQuantum | Inteligência em Dados",
        )

        canvas.drawRightString(
            19.2 * cm,
            0.9 * cm,
            f"Página {document.page}",
        )

        canvas.restoreState()

    def afterFlowable(self, flowable: Any) -> None:
        """Registra os títulos para o sumário automático."""

        if isinstance(flowable, Paragraph) and flowable.style.name == "SectionHeading":
            title = flowable.getPlainText()

            self.notify(
                "TOCEntry",
                (0, title, self.page),
            )


# ---------------------------------------------------------
# 3. ESTILOS DO RELATÓRIO
# ---------------------------------------------------------


def get_report_styles() -> dict[str, ParagraphStyle]:
    """Cria os estilos visuais do relatório."""

    styles = getSampleStyleSheet()

    styles.add(
        ParagraphStyle(
            name="CoverTitle",
            parent=styles["Title"],
            fontName="Helvetica-Bold",
            fontSize=27,
            leading=34,
            alignment=TA_CENTER,
            textColor=colors.HexColor(NAVY),
            spaceAfter=20,
        )
    )

    styles.add(
        ParagraphStyle(
            name="SectionHeading",
            parent=styles["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=17,
            leading=22,
            textColor=colors.HexColor(NAVY),
            spaceBefore=12,
            spaceAfter=14,
            keepWithNext=True,
        )
    )

    styles.add(
        ParagraphStyle(
            name="ReportBody",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=9,
            leading=14,
            alignment=TA_JUSTIFY,
            textColor=colors.HexColor(DARK),
            spaceAfter=8,
        )
    )

    styles.add(
        ParagraphStyle(
            name="AnalysisPoint",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=8.5,
            leading=12,
            alignment=TA_JUSTIFY,
            leftIndent=10,
            firstLineIndent=-10,
            spaceAfter=5,
        )
    )

    styles.add(
        ParagraphStyle(
            name="SubHeading",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=11,
            leading=15,
            textColor=colors.HexColor(NAVY),
            spaceBefore=10,
            spaceAfter=7,
        )
    )

    styles.add(
        ParagraphStyle(
            name="CoverSubtitle",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=13,
            leading=20,
            alignment=TA_CENTER,
            textColor=colors.HexColor(GRAY),
        )
    )

    return {
        "cover": cast(ParagraphStyle, styles["CoverTitle"]),
        "subtitle": cast(ParagraphStyle, styles["CoverSubtitle"]),
        "heading": cast(ParagraphStyle, styles["SectionHeading"]),
        "body": cast(ParagraphStyle, styles["ReportBody"]),
        "point": cast(ParagraphStyle, styles["AnalysisPoint"]),
        "subheading": cast(ParagraphStyle, styles["SubHeading"]),
    }


# ---------------------------------------------------------
# 4. ANÁLISE DOS DADOS COM GEMINI
# ---------------------------------------------------------


def generate_chart_analysis(
    client: genai.Client,
    model: str,
    title: str,
    data: dict[str, object],
) -> ChartAnalysis:
    """
    Gera análise textual exclusivamente com base no dicionário recebido.

    A imagem do gráfico não é enviada ao Gemini.
    """

    prompt = f"""
    Você é um analista sênior de dados e negócios.

    Analise os dados apresentados abaixo para um relatório
    profissional de análise de vendas.

    TÍTULO: {title}

    DADOS:
    {data}

    REGRAS OBRIGATÓRIAS:

    1. Utilize exclusivamente os dados fornecidos.
    2. Não invente valores, tendências ou informações.
    3. Não descreva imagens ou gráficos.
    4. Produza pelo menos 10 observações analíticas distintas.
    5. Cada observação deve apresentar uma análise clara e útil.
    6. Destaque resultados relevantes, concentrações e diferenças.
    7. Quando não houver dados suficientes, informe a limitação.
    8. Não confunda correlação com causalidade.
    9. Produza uma conclusão objetiva.
    10. Recomende ações somente quando os dados justificarem.
    11. Se não houver necessidade de orientação, retorne uma
        lista vazia de recomendações.
    12. Escreva em português brasileiro, com linguagem
        profissional e adequada a um relatório empresarial.

    A análise deve ser específica para os indicadores recebidos.
    Evite frases genéricas e repetições.
    """

    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": ChartAnalysis,
            "temperature": 0.2,
        },
    )

    if response.parsed is not None:
        result = ChartAnalysis.model_validate(response.parsed)
    else:
        if not response.text:
            raise ValueError("O Gemini retornou uma resposta vazia.")

        result = ChartAnalysis.model_validate_json(response.text)

    if len(result.analysis_points) < 10:
        raise ValueError(f"A análise de '{title}' contém menos de 10 observações.")

    return result


# ---------------------------------------------------------
# 5. INTRODUÇÃO DO RELATÓRIO
# ---------------------------------------------------------


def generate_report_introduction(
    client: genai.Client,
    model: str,
    analytics: dict[str, object],
) -> str:
    """Gera a introdução utilizando exclusivamente os dados analíticos."""

    prompt = f"""
    Escreva a introdução de um relatório profissional de vendas.

    Utilize exclusivamente o dicionário de dados abaixo:

    {analytics}

    A introdução deve apresentar:
    - Objetivo do relatório.
    - Contexto dos dados.
    - Período analisado, se disponível.
    - Indicadores considerados.
    - Metodologia geral da análise.
    - Organização das seções do relatório.

    Não invente informações.
    Escreva em português brasileiro.
    Utilize linguagem empresarial, clara e objetiva.
    Produza aproximadamente três parágrafos.
    """

    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config={"temperature": 0.2},
    )

    if not response.text:
        raise ValueError("O Gemini não gerou a introdução.")

    return response.text.strip()


# ---------------------------------------------------------
# 6. MAPEAMENTO DOS GRÁFICOS E DADOS
# ---------------------------------------------------------


def get_chart_data_mapping(
    analytics: dict[str, Any],
) -> dict[str, tuple[str, dict[str, Any]]]:
    """
    Relaciona cada gráfico à seção correspondente do analytics.
    """

    return {
        "01_kpis": (
            "Indicadores gerais de vendas",
            analytics["kpis"],
        ),
        "02_products_top_revenue": (
            "Produtos com maior faturamento",
            analytics["products"]["top_revenue"],
        ),
        "03_products_top_quantity": (
            "Produtos com maior quantidade vendida",
            analytics["products"]["top_quantity"],
        ),
        "04_products_lowest_revenue": (
            "Produtos com menor faturamento",
            analytics["products"]["lowest_revenue"],
        ),
        "05_categories_revenue": (
            "Faturamento por categoria",
            analytics["categories"]["revenue"],
        ),
        "06_categories_quantity": (
            "Quantidade vendida por categoria",
            analytics["categories"]["quantity"],
        ),
        "07_categories_profit": (
            "Lucro por categoria",
            analytics["categories"]["profit"],
        ),
        "08_customers_revenue": (
            "Faturamento por cliente",
            analytics["customers"]["revenue"],
        ),
        "09_customers_orders": (
            "Pedidos por cliente",
            analytics["customers"]["orders"],
        ),
        "10_customers_segments": (
            "Segmentação de clientes",
            analytics["customers"]["segments"],
        ),
        "11_geography_countries": (
            "Faturamento por país",
            analytics["geography"]["countries"],
        ),
        "12_geography_regions": (
            "Faturamento por região",
            analytics["geography"]["regions"],
        ),
        "13_time_year": (
            "Vendas por ano",
            analytics["time"]["year"],
        ),
        "14_time_month": (
            "Vendas por mês",
            analytics["time"]["month"],
        ),
        "15_time_weekday": (
            "Vendas por dia da semana",
            analytics["time"]["weekday"],
        ),
        "16_payments_methods": (
            "Métodos de pagamento",
            analytics["payments"]["methods"],
        ),
        "17_payments_orders": (
            "Pedidos por método de pagamento",
            analytics["payments"]["orders"],
        ),
    }


# ---------------------------------------------------------
# 7. FUNÇÃO PRINCIPAL DE GERAÇÃO DO PDF
# ---------------------------------------------------------


def get_create_sales_report(
    analytics: dict[str, Any],
    charts: dict[str, Path],
    output_path: Path,
    company_name: str = "DataQuantum",
    model: str = "gemini-3.5-flash",
) -> Path:
    """
    Gera relatório PDF com análises produzidas pelo Gemini.

    Args:
        analytics: Dicionário com os resultados analíticos.
        charts: Dicionário com os caminhos dos gráficos.
        output_path: Caminho de saída do PDF.
        company_name: Nome da empresa.
        model: Modelo Gemini utilizado.

    Returns:
        Path: Caminho do relatório PDF gerado.

    Raises:
        TypeError: Se os parâmetros tiverem tipos inválidos.
        ValueError: Se os dados estiverem vazios ou inválidos.
        FileNotFoundError: Se algum gráfico não existir.
        RuntimeError: Se ocorrer uma falha durante a geração.
    """

    try:
        # Validação dos parâmetros.
        if not isinstance(analytics, dict) or not analytics:
            raise ValueError("analytics deve ser um dicionário não vazio.")

        if not isinstance(charts, dict) or not charts:
            raise ValueError("charts deve ser um dicionário não vazio.")

        if not isinstance(output_path, Path):
            raise TypeError("output_path deve ser pathlib Path.")

        if not all(isinstance(path, Path) for path in charts.values()):
            raise TypeError("Todos os gráficos devem ser objetos Path.")

        # Valida as imagens antes de chamar a API.
        for chart_path in charts.values():
            if not chart_path.is_file():
                raise FileNotFoundError(f"Gráfico não encontrado: {chart_path}")

        # Carrega a variável do arquivo .env
        load_dotenv()

        # Inicializa o cliente Gemini.
        API_KEY = os.getenv("GEMINI_API_KEY")

        if not API_KEY:
            raise ValueError("A variável GEMINI_API_KEY não foi configurada.")

        client = genai.Client(api_key=API_KEY)

        # Configura o documento.
        output_path.parent.mkdir(parents=True, exist_ok=True)

        document = SalesReportDocument(output_path)
        styles = get_report_styles()

        elements = []

        # -------------------------------------------------
        # CAPA
        # -------------------------------------------------

        elements.extend(
            [
                Spacer(1, 4.5 * cm),
                Paragraph(
                    escape(company_name),
                    styles["subtitle"],
                ),
                Spacer(1, 1.2 * cm),
                Paragraph(
                    "RELATÓRIO ANALÍTICO DE VENDAS",
                    styles["cover"],
                ),
                Paragraph(
                    "Inteligência de Dados | Análise de Desempenho",
                    styles["subtitle"],
                ),
                Spacer(1, 2 * cm),
                Paragraph(
                    "Relatório elaborado com base nos indicadores "
                    "e resultados do processamento dos dados.",
                    styles["body"],
                ),
                Spacer(1, 2 * cm),
                Paragraph(
                    "Documento gerado automaticamente",
                    styles["subtitle"],
                ),
                PageBreak(),
            ]
        )

        # -------------------------------------------------
        # SUMÁRIO AUTOMÁTICO
        # -------------------------------------------------

        toc = TableOfContents()

        toc.levelStyles = [
            ParagraphStyle(
                name="TOCLevel1",
                fontName="Helvetica",
                fontSize=9,
                leading=15,
                leftIndent=12,
                firstLineIndent=-12,
                textColor=colors.HexColor(DARK),
            )
        ]

        elements.extend(
            [
                Paragraph("SUMÁRIO", styles["heading"]),
                Spacer(1, 0.5 * cm),
                toc,
                PageBreak(),
            ]
        )

        # -------------------------------------------------
        # INTRODUÇÃO
        # -------------------------------------------------

        introduction = generate_report_introduction(
            client=client,
            model=model,
            analytics=analytics,
        )

        elements.append(Paragraph("INTRODUÇÃO", styles["heading"]))

        for paragraph in introduction.split("\n\n"):
            if paragraph.strip():
                elements.append(
                    Paragraph(
                        escape(paragraph.strip()),
                        styles["body"],
                    )
                )

        elements.append(PageBreak())

        # -------------------------------------------------
        # ANÁLISES INDIVIDUAIS
        # -------------------------------------------------

        chart_mapping = get_chart_data_mapping(analytics)

        for chart_name, chart_path in charts.items():
            # Obtém o nome do gráfico sem a extensão.
            key = chart_path.stem

            if key not in chart_mapping:
                logger.warning(
                    "Gráfico sem mapeamento analítico: %s",
                    chart_name,
                )
                continue

            title, data = chart_mapping[key]

            # Envia somente os dados textuais ao Gemini.
            analysis = generate_chart_analysis(
                client=client,
                model=model,
                title=title,
                data=data,
            )

            elements.append(
                Paragraph(
                    escape(title),
                    styles["heading"],
                )
            )

            # Insere a imagem no PDF.
            chart_image = Image(
                str(chart_path),
                width=16.5 * cm,
                height=8.2 * cm,
                kind="proportional",
            )

            chart_image.hAlign = "CENTER"

            elements.extend(
                [
                    chart_image,
                    Spacer(1, 0.4 * cm),
                    Paragraph(
                        "ANÁLISE DOS RESULTADOS",
                        styles["subheading"],
                    ),
                ]
            )

            # Insere as dez ou mais observações.
            for index, point in enumerate(
                analysis.analysis_points,
                start=1,
            ):
                elements.append(
                    Paragraph(
                        f"<b>{index}.</b> {escape(point)}",
                        styles["point"],
                    )
                )

            # Conclusão.
            elements.append(
                Paragraph(
                    "CONCLUSÃO",
                    styles["subheading"],
                )
            )

            elements.append(
                Paragraph(
                    escape(analysis.conclusion),
                    styles["body"],
                )
            )

            # Orientações.
            if analysis.recommendations:
                elements.append(
                    Paragraph(
                        "ORIENTAÇÕES E RECOMENDAÇÕES",
                        styles["subheading"],
                    )
                )

                for recommendation in analysis.recommendations:
                    elements.append(
                        Paragraph(
                            f"• {escape(recommendation)}",
                            styles["point"],
                        )
                    )

            elements.append(PageBreak())

        # -------------------------------------------------
        # GERAÇÃO FINAL DO PDF
        # -------------------------------------------------

        document.multiBuild(elements)

        logger.info(
            "Relatório PDF gerado com sucesso: %s",
            output_path,
        )

        return output_path

    except (TypeError, ValueError, FileNotFoundError):
        logger.exception("Erro de validação na geração do relatório.")
        raise

    except Exception as exc:
        logger.exception("Falha ao gerar relatório PDF.")
        raise RuntimeError("Não foi possível gerar o relatório de vendas.") from exc
