from pathlib import Path
import logging
from typing import Any

import pandas as pd
from prefect import flow, task

from report_python_gemini_ia.utils.yaml.load_yaml import load_all_configs
from report_python_gemini_ia.utils.loggers.logger import setup_logger

from report_python_gemini_ia.ingestion.load_csv import get_load_csv

from report_python_gemini_ia.transformation.standardize_columns import (
    get_standardize_columns,
)
from report_python_gemini_ia.transformation.clean_numeric_columns import (
    get_clean_numeric_columns,
)
from report_python_gemini_ia.transformation.clean_category_columns import (
    get_clean_category_columns,
)
from report_python_gemini_ia.transformation.clean_datetime_columns import (
    get_clean_datetime_columns,
)

from report_python_gemini_ia.analytics.create_sales_summary import (
    get_create_sales_summary,
)
from report_python_gemini_ia.visualization.create_sales_charts import (
    get_create_sales_charts,
)
from report_python_gemini_ia.report.create_sales_report import (
    get_create_sales_report,
)


# -----------------------------------------------------
# Tarefas do pipeline.
# -----------------------------------------------------


@task(name="carregar-configuracoes")
def load_configs_task(
    config_path: Path,
) -> dict[str, Any]:
    """Carrega as configurações YAML do projeto."""
    return load_all_configs(config_path)


@task(
    name="carregar-dados-csv",
    retries=3,
    retry_delay_seconds=5,
)
def load_csv_task(data_raw: Path) -> pd.DataFrame:
    """Carrega os dados originais do arquivo CSV."""
    return get_load_csv(data_raw)


@task(name="padronizar-colunas")
def standardize_columns_task(
    df: pd.DataFrame,
    columns_dict: dict[str, Any],
) -> pd.DataFrame:
    """Padroniza os nomes das colunas."""
    return get_standardize_columns(df, columns_dict)


@task(name="limpar-colunas-numericas")
def clean_numeric_columns_task(
    df: pd.DataFrame,
    columns_dict: dict[str, Any],
) -> pd.DataFrame:
    """Limpa e converte as colunas numéricas."""
    return get_clean_numeric_columns(df, columns_dict)


@task(name="limpar-colunas-categoricas")
def clean_category_columns_task(
    df: pd.DataFrame,
    columns_dict: dict[str, Any],
) -> pd.DataFrame:
    """Limpa as colunas categóricas."""
    return get_clean_category_columns(df, columns_dict)


@task(name="limpar-colunas-datetime")
def clean_datetime_columns_task(
    df: pd.DataFrame,
    columns_dict: dict[str, Any],
) -> pd.DataFrame:
    """Limpa e converte as colunas de data."""
    return get_clean_datetime_columns(df, columns_dict)


@task(name="salvar-dados-processados")
def save_processed_data_task(
    df: pd.DataFrame,
    processed_path: Path,
) -> Path:
    """Salva o DataFrame processado em CSV."""
    processed_path.parent.mkdir(parents=True, exist_ok=True)

    df.to_csv(
        processed_path,
        index=False,
        encoding="utf-8-sig",
        sep=",",
    )

    return processed_path


@task(name="gerar-resumo-analitico")
def create_sales_summary_task(
    df: pd.DataFrame,
    columns_dict: dict[str, Any],
) -> Any:
    """Gera KPIs e métricas comerciais."""
    return get_create_sales_summary(df, columns_dict)


@task(name="gerar-graficos", retries=3, retry_delay_seconds=[5, 10, 20, 40, 60])
def create_sales_charts_task(
    analytics: Any,
    output_dir: Path,
) -> Any:
    """Gera os gráficos da análise comercial."""
    return get_create_sales_charts(analytics, output_dir)


@task(
    name="gerar-relatorio-pdf",
    retries=5,
    retry_delay_seconds=10,
)
def create_sales_report_task(
    analytics: Any,
    charts: Any,
    report_path: Path,
) -> None:
    """Gera o relatório comercial em PDF."""
    get_create_sales_report(
        analytics=analytics,
        charts=charts,
        output_path=report_path,
        company_name="DataQuantum",
    )


# -----------------------------------------------------
# Fluxo principal do Prefect.
# -----------------------------------------------------


@flow(
    name="pipeline-report-python-gemini-ia",
    description="Pipeline ETL, análise de vendas, gráficos e relatório PDF.",
    log_prints=True,
)
def pipeline_report() -> None:
    """
    Executa o pipeline completo de análise de vendas.

    Etapas:
        1. Carregamento das configurações.
        2. Ingestão dos dados.
        3. Padronização e limpeza.
        4. Salvamento dos dados processados.
        5. Geração de KPIs e métricas.
        6. Criação dos gráficos.
        7. Geração do relatório PDF.
    """

    # -----------------------------------------------------
    # Configura raiz do sistema.
    # -----------------------------------------------------

    base_dir = Path(__file__).resolve().parents[2]

    # -----------------------------------------------------
    # Carrega configurações YAML.
    # -----------------------------------------------------

    config_path = base_dir / "config"
    configs = load_configs_task(config_path)

    # -----------------------------------------------------
    # Configura sistema de logs.
    # -----------------------------------------------------

    setup_logger(configs["logging"], True)

    logger = logging.getLogger(__name__)

    logger.info("INÍCIO DO PIPELINE REPORT PYTHON GEMINI IA")

    # -----------------------------------------------------
    # Carrega dados originais.
    # -----------------------------------------------------

    data_raw = base_dir / configs["paths"]["paths_config"]["data_raw"]

    df = load_csv_task(data_raw)

    # -----------------------------------------------------
    # Padroniza e limpa os dados.
    # -----------------------------------------------------

    columns_dict = configs["columns_list"]["columns"]

    df = standardize_columns_task(df, columns_dict)

    df = clean_numeric_columns_task(df, columns_dict)

    df = clean_category_columns_task(df, columns_dict)

    df = clean_datetime_columns_task(df, columns_dict)

    # -----------------------------------------------------
    # Salva os dados processados.
    # -----------------------------------------------------

    processed_path = base_dir / "data" / "data_processed" / "global_sales_processed.csv"

    saved_path = save_processed_data_task(
        df,
        processed_path,
    )

    logger.info(
        "Dados processados salvos com sucesso: %s",
        saved_path,
    )

    # -----------------------------------------------------
    # Gera resumo de KPIs e métricas.
    # -----------------------------------------------------

    analytics = create_sales_summary_task(
        df,
        columns_dict,
    )

    # -----------------------------------------------------
    # Gera gráficos em formato PNG.
    # -----------------------------------------------------

    output_dir = base_dir / "reports" / "charts"

    charts = create_sales_charts_task(
        analytics,
        output_dir,
    )

    # -----------------------------------------------------
    # Gera relatório em PDF.
    # -----------------------------------------------------

    report_path = base_dir / "reports" / "DataQuantum_Relatorio_Vendas.pdf"

    create_sales_report_task(
        analytics,
        charts,
        report_path,
    )

    logger.info("PIPELINE FINALIZADO COM SUCESSO.")


if __name__ == "__main__":
    pipeline_report()
