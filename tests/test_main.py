from unittest.mock import patch

from report_python_gemini_ia.main import main


def test_main_pipeline_report() -> None:
    """
    Verifica se a função main executa o pipeline principal.

    Assertions:
        - pipeline_report deve ser chamado exatamente uma vez.
    """
    with patch("report_python_gemini_ia.main.pipeline_report") as mock_pipeline:
        main()

        mock_pipeline.assert_called_once()
