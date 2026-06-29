"""Testes de integração da UI: roda o app real (headless) via AppTest.

Confirma que o entry point e todas as páginas carregam e renderizam sem exceção,
usando o repositório mock por padrão.
"""
import pytest
from streamlit.testing.v1 import AppTest

PAGINAS = [
    "app.py",
    "pages/1_📅_Calendário.py",
    "pages/2_🧑‍✈️_Motoristas.py",
    "pages/3_🚗_Veículos.py",
    "pages/4_🏛️_Secretarias.py",
    "pages/5_👥_Usuários.py",
]


@pytest.mark.parametrize("caminho", PAGINAS)
def test_pagina_carrega_sem_excecao(caminho):
    at = AppTest.from_file(caminho, default_timeout=30).run()
    assert not at.exception, f"{caminho} levantou exceção: {at.exception}"


def test_dashboard_mostra_metricas():
    at = AppTest.from_file("app.py", default_timeout=30).run()
    # Dashboard tem 4 KPIs (metric)
    assert len(at.metric) == 4
