"""Minhas requisições — acompanhar e cancelar (papel do requisitante)."""
from __future__ import annotations

from datetime import datetime

import streamlit as st

from components.auth import exigir_papel
from components.theme import fmt_periodo, header, secretaria_label, setup_sidebar, status_chip
from domain import Role
from domain.rules import CANCELAVEIS_PELO_SOLICITANTE
from services import get_repository

header("Minhas Requisições", "Acompanhe o status das suas viagens")
setup_sidebar()
usuario = exigir_papel(Role.SOLICITANTE)

repo = get_repository()
minhas = [v for v in repo.list_viagens() if v.solicitanteId == usuario.uid]
minhas.sort(key=lambda v: v.dataHoraSaida, reverse=True)

st.subheader(f"Minhas requisições ({len(minhas)})")
if not minhas:
    st.info("Você ainda não fez nenhuma requisição.")

for v in minhas:
    with st.container(border=True):
        st.markdown(
            f"{status_chip(v.status)} &nbsp; **{v.origem} → {v.destino}**  \n"
            f"🕒 {fmt_periodo(v.dataHoraSaida, v.dataHoraRetorno)} · "
            f"🏛️ {secretaria_label(repo, v.secretariaId)} · 👥 {v.numPassageiros}",
            unsafe_allow_html=True,
        )
        if v.finalidade:
            st.caption(f"Finalidade: {v.finalidade}")
        if v.motivoRejeicao:
            st.caption(f"Motivo da rejeição: {v.motivoRejeicao}")
        if v.status in CANCELAVEIS_PELO_SOLICITANTE:
            if st.button("Cancelar", key=f"cancelar_{v.id}"):
                repo.cancelar_viagem(v.id, quando=datetime.now())
                st.warning("Requisição cancelada.")
                st.rerun()
