"""Dashboard — visão geral do controlador."""
from __future__ import annotations

from datetime import datetime

import streamlit as st

from components.auth import exigir_papel
from components.theme import header, secretaria_label, setup_sidebar, status_chip
from domain import Role, StatusViagem
from services import get_repository

header("Transporte SJC — Painel de Controle",
       "Escala de motoristas e veículos da prefeitura")
setup_sidebar()
exigir_papel(Role.CONTROLADOR)

repo = get_repository()
viagens = repo.list_viagens()
motoristas = repo.list_motoristas()
veiculos = repo.list_veiculos()

por_status = {s: 0 for s in StatusViagem}
for v in viagens:
    por_status[v.status] += 1

hoje = datetime.now().date()
viagens_hoje = [v for v in viagens if v.dataHoraSaida.date() == hoje]

# --------------------------------------------------------------------------- #
# KPIs
# --------------------------------------------------------------------------- #
c1, c2, c3, c4 = st.columns(4)
c1.metric("Pendentes", por_status[StatusViagem.PENDENTE])
c2.metric("Viagens hoje", len(viagens_hoje))
c3.metric("Motoristas ativos",
          sum(1 for m in motoristas if m.status.value == "ATIVO"))
c4.metric("Veículos disponíveis",
          sum(1 for v in veiculos if v.status.value == "DISPONIVEL"))

st.divider()

col_esq, col_dir = st.columns([2, 1])

with col_esq:
    st.subheader("📥 Requisições pendentes")
    pendentes = [v for v in viagens if v.status == StatusViagem.PENDENTE]
    if not pendentes:
        st.success("Nenhuma requisição pendente. 🎉")
    for v in pendentes:
        st.markdown(
            f'<div class="card">{status_chip(v.status)} '
            f'&nbsp;<b>{v.origem} → {v.destino}</b><br>'
            f'<small>{v.solicitanteNome} · {secretaria_label(repo, v.secretariaId)} · '
            f'{v.dataHoraSaida.strftime("%d/%m %H:%M")}</small></div>',
            unsafe_allow_html=True,
        )
    if pendentes:
        st.page_link("pages/1_📅_Calendário.py", label="Tratar no calendário →",
                     icon="📅")

with col_dir:
    st.subheader("📊 Por status")
    for s in StatusViagem:
        st.markdown(f"{status_chip(s)} &nbsp; **{por_status[s]}**",
                    unsafe_allow_html=True)

st.divider()
st.caption("Dados de demonstração (mock). Pronto para conectar ao Firebase — "
           "veja `services/firebase_repository.py`.")
