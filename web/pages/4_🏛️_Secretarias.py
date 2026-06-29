"""Cadastro de secretarias (código, nome, sigla)."""
from __future__ import annotations

import streamlit as st

from components.theme import header, setup_sidebar
from domain import Secretaria
from services import get_repository

st.set_page_config(page_title="Secretarias · Transporte SJC", page_icon="🏛️", layout="wide")
header("Secretarias", "Órgãos atendidos pela frota")
setup_sidebar()

repo = get_repository()

with st.expander("➕ Nova secretaria", expanded=False):
    with st.form("nova_secretaria", clear_on_submit=True):
        c1, c2, c3 = st.columns([1, 3, 1])
        codigo = c1.number_input("Código", min_value=1, step=1, value=20)
        nome = c2.text_input("Nome")
        sigla = c3.text_input("Sigla")
        if st.form_submit_button("Cadastrar", type="primary"):
            if repo.get_secretaria(int(codigo)):
                st.error(f"Já existe secretaria com código {int(codigo)}.")
            elif not nome:
                st.error("Informe o nome.")
            else:
                repo.upsert_secretaria(Secretaria(int(codigo), nome, sigla))
                st.success("Secretaria cadastrada.")
                st.rerun()

st.divider()

secretarias = repo.list_secretarias()
st.subheader(f"Cadastradas ({len(secretarias)})")
for s in secretarias:
    with st.expander(f"{s.codigo} · {s.nome} ({s.sigla})"):
        with st.form(f"edit_sec_{s.codigo}"):
            c1, c2 = st.columns([3, 1])
            nome = c1.text_input("Nome", s.nome)
            sigla = c2.text_input("Sigla", s.sigla)
            b1, b2 = st.columns(2)
            if b1.form_submit_button("Salvar", type="primary"):
                repo.upsert_secretaria(Secretaria(s.codigo, nome, sigla))
                st.success("Atualizada.")
                st.rerun()
            if b2.form_submit_button("Excluir"):
                repo.delete_secretaria(s.codigo)
                st.warning("Excluída.")
                st.rerun()
