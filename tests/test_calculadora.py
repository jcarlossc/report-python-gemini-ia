from report_python_gemini_ia.calculadora import somar


def test_somar():
    resultado = somar(10, 5)

    assert resultado == 15