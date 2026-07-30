"""Transporte SJC — Painel de Controle (Streamlit). Ponto de entrada / roteador.

Rode a partir da pasta ``web/``:

    streamlit run app.py

Use um virtualenv (veja README) para não colidir com o Python do Debian.

Autenticação (local, sem Firebase por ora): sem login, mostra a tela de
entrada/cadastro. Autenticado, monta o menu conforme o papel — CONTROLADOR
(cadastros + calendário) ou SOLICITANTE (nova requisição + acompanhamento).
"""
from __future__ import annotations

import streamlit as st

from components.auth import usuario_logado
from components.login import render_login
from domain import Role

st.set_page_config(page_title="Transporte SJC", page_icon="🚐", layout="wide")

usuario = usuario_logado()
if usuario is None:
    render_login()
    st.stop()

PAGINAS_CONTROLADOR = [
    st.Page("pages/0_🏠_Dashboard.py", title="Dashboard", icon="🏠", default=True),
    st.Page("pages/1_📅_Calendário.py", title="Calendário", icon="📅"),
    st.Page("pages/2_🧑‍✈️_Motoristas.py", title="Motoristas", icon="🧑‍✈️"),
    st.Page("pages/3_🚗_Veículos.py", title="Veículos", icon="🚗"),
    st.Page("pages/4_🏛️_Secretarias.py", title="Secretarias", icon="🏛️"),
    st.Page("pages/5_👥_Usuários.py", title="Usuários", icon="👥"),
]
PAGINAS_SOLICITANTE = [
    st.Page("pages/6_📝_Nova_Requisição.py", title="Nova Requisição", icon="📝", default=True),
    st.Page("pages/7_🧾_Minhas_Requisições.py", title="Minhas Requisições", icon="🧾"),
]

paginas = PAGINAS_CONTROLADOR if usuario.role == Role.CONTROLADOR else PAGINAS_SOLICITANTE
st.navigation(paginas).run()
