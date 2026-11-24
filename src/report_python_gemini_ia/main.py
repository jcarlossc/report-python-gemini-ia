from report_python_gemini_ia.pipeline_report import pipeline_report


def main() -> None:
    """
    Inicializa e executa o pipeline de processamento de relatórios.

    Responsabilidade:
        - Iniciar a execução do pipeline principal.
        - Delegar o processamento ao módulo pipeline_report.

    Returns:
        None
    """
    # Executa o pipeline principal da aplicação.
    pipeline_report()


if __name__ == "__main__":
    # Garante que a aplicação seja iniciada diretamente por este módulo.
    main()
