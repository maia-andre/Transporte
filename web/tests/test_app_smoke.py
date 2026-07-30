"""Testes de integração da UI: roda o app real (headless) via AppTest.

Confirma que o entry point e cada página carregam sem exceção, que o login
gate funciona (autenticação + controle de acesso por papel) e que o
auto-cadastro cria contas SOLICITANTE.
"""
from __future__ import annotations

from datetime import datetime

import pytest
from streamlit.testing.v1 import AppTest

from components.auth import SESSION_KEY_USUARIO
from domain import Role, Usuario
from services.mock_data import SENHA_DEMO

CONTROLADOR = Usuario("u_test_ctrl", "Ana Teste", "ana.controle@sjc.sp.gov.br",
                      Role.CONTROLADOR, 10, criadoEm=datetime.now())
SOLICITANTE = Usuario("u_test_sol", "Carlos Teste", "carlos.teste@sjc.sp.gov.br",
                      Role.SOLICITANTE, 5, criadoEm=datetime.now())

# Dashboard fica de fora: usa ``st.page_link`` para outra página, que só resolve
# dentro do contexto real de navegação (``app.py`` + ``st.navigation``) — ver
# ``test_dashboard_mostra_metricas``, que sobe pelo roteador de verdade.
PAGINAS_CONTROLADOR_SEM_NAV = [
    "pages/1_📅_Calendário.py",
    "pages/2_🧑‍✈️_Motoristas.py",
    "pages/3_🚗_Veículos.py",
    "pages/4_🏛️_Secretarias.py",
    "pages/5_👥_Usuários.py",
]
PAGINAS_CONTROLADOR = ["pages/0_🏠_Dashboard.py", *PAGINAS_CONTROLADOR_SEM_NAV]
PAGINAS_SOLICITANTE = [
    "pages/6_📝_Nova_Requisição.py",
    "pages/7_🧾_Minhas_Requisições.py",
]


def _autenticado(caminho: str, usuario: Usuario) -> AppTest:
    at = AppTest.from_file(caminho, default_timeout=30)
    at.session_state[SESSION_KEY_USUARIO] = usuario
    return at.run()


@pytest.mark.parametrize("caminho", PAGINAS_CONTROLADOR_SEM_NAV)
def test_paginas_controlador_carregam_autenticadas(caminho):
    at = _autenticado(caminho, CONTROLADOR)
    assert not at.exception, f"{caminho} levantou exceção: {at.exception}"


@pytest.mark.parametrize("caminho", PAGINAS_SOLICITANTE)
def test_paginas_solicitante_carregam_autenticadas(caminho):
    at = _autenticado(caminho, SOLICITANTE)
    assert not at.exception, f"{caminho} levantou exceção: {at.exception}"


@pytest.mark.parametrize("caminho", PAGINAS_CONTROLADOR)
def test_paginas_administrativas_bloqueiam_solicitante(caminho):
    at = _autenticado(caminho, SOLICITANTE)
    assert not at.exception, f"{caminho} levantou exceção: {at.exception}"
    assert len(at.error) >= 1, f"{caminho} deveria bloquear um solicitante"


@pytest.mark.parametrize("caminho", PAGINAS_SOLICITANTE)
def test_paginas_solicitante_bloqueiam_controlador(caminho):
    at = _autenticado(caminho, CONTROLADOR)
    assert not at.exception, f"{caminho} levantou exceção: {at.exception}"
    assert len(at.error) >= 1, f"{caminho} deveria bloquear um controlador"


def test_paginas_bloqueiam_sem_login():
    for caminho in [*PAGINAS_CONTROLADOR, *PAGINAS_SOLICITANTE]:
        at = AppTest.from_file(caminho, default_timeout=30).run()
        assert not at.exception, f"{caminho} levantou exceção: {at.exception}"
        assert len(at.warning) >= 1, f"{caminho} deveria pedir login"


def test_app_sem_login_mostra_tela_de_entrada():
    at = AppTest.from_file("app.py", default_timeout=30).run()
    assert not at.exception
    assert len(at.tabs) == 2  # "Entrar" / "Criar conta"


def test_dashboard_mostra_metricas():
    # Sobe pelo roteador de verdade (``app.py``): CONTROLADOR cai no Dashboard
    # por ser a página ``default``, com o contexto de navegação que o
    # ``st.page_link`` do Dashboard precisa para resolver a página de destino.
    at = _autenticado("app.py", CONTROLADOR)
    assert not at.exception
    assert len(at.metric) == 4


def test_login_com_credenciais_corretas_autentica():
    at = AppTest.from_file("app.py", default_timeout=30).run()
    at.text_input(key="login_email").input("ana.controle@sjc.sp.gov.br")
    at.text_input(key="login_senha").input(SENHA_DEMO)
    at.button(key="login_submit").click().run()

    assert not at.exception
    assert SESSION_KEY_USUARIO in at.session_state
    usuario = at.session_state[SESSION_KEY_USUARIO]
    assert usuario.role == Role.CONTROLADOR


def test_login_com_senha_errada_nao_autentica():
    at = AppTest.from_file("app.py", default_timeout=30).run()
    at.text_input(key="login_email").input("ana.controle@sjc.sp.gov.br")
    at.text_input(key="login_senha").input("senha-errada")
    at.button(key="login_submit").click().run()

    assert not at.exception
    assert SESSION_KEY_USUARIO not in at.session_state
    assert len(at.error) >= 1


def test_cadastro_cria_conta_solicitante():
    at = AppTest.from_file("app.py", default_timeout=30).run()
    at.text_input(key="cadastro_nome").input("Novo Usuário")
    at.text_input(key="cadastro_email").input("novo.usuario@sjc.sp.gov.br")
    at.text_input(key="cadastro_senha").input("senha123")
    at.text_input(key="cadastro_senha2").input("senha123")
    at.button(key="cadastro_submit").click().run()

    assert not at.exception
    assert len(at.success) >= 1

    # a conta foi criada como SOLICITANTE e já consegue logar.
    at.text_input(key="login_email").input("novo.usuario@sjc.sp.gov.br")
    at.text_input(key="login_senha").input("senha123")
    at.button(key="login_submit").click().run()
    assert SESSION_KEY_USUARIO in at.session_state
    usuario = at.session_state[SESSION_KEY_USUARIO]
    assert usuario.role == Role.SOLICITANTE
