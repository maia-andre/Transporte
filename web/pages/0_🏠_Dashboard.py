"""Dashboard — visão geral do controlador."""
from __future__ import annotations

from datetime import datetime, timedelta

import streamlit as st

from components.auth import exigir_papel
from components.theme import (
    AZUL,
    AZUL_CLARO,
    DOURADO,
    VERDE,
    header,
    nome_dia_semana,
    secretaria_label,
    setup_sidebar,
    status_chip,
)
from domain import Role, StatusMotorista, StatusVeiculo, StatusViagem
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
c1, c2 = st.columns(2)
c1.metric("Pendentes", por_status[StatusViagem.PENDENTE])
c2.metric("Viagens hoje", len(viagens_hoje))

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

    st.markdown("<br>", unsafe_allow_html=True)

    qtd_ativos = sum(1 for m in motoristas if m.status == StatusMotorista.ATIVO)
    qtd_inativos = sum(1 for m in motoristas if m.status == StatusMotorista.INATIVO)
    st.markdown(
        f'<div class="card"><b>🧑‍✈️ Motoristas</b><br>'
        f'<span style="color:{VERDE}">●</span> Ativos: <b>{qtd_ativos}</b> &nbsp;&nbsp; '
        f'<span style="color:#9aa5b1">●</span> Inativos: <b>{qtd_inativos}</b></div>',
        unsafe_allow_html=True,
    )

    qtd_disp = sum(1 for v in veiculos if v.status == StatusVeiculo.DISPONIVEL)
    qtd_uso = sum(1 for v in veiculos if v.status == StatusVeiculo.EM_USO)
    qtd_manut = sum(1 for v in veiculos if v.status == StatusVeiculo.MANUTENCAO)
    st.markdown(
        f'<div class="card"><b>🚗 Veículos</b><br>'
        f'<span style="color:{VERDE}">●</span> Disponíveis: <b>{qtd_disp}</b><br>'
        f'<span style="color:{AZUL_CLARO}">●</span> Em uso: <b>{qtd_uso}</b><br>'
        f'<span style="color:{DOURADO}">●</span> Manutenção: <b>{qtd_manut}</b></div>',
        unsafe_allow_html=True,
    )

st.divider()

# --------------------------------------------------------------------------- #
# Semana (domingo a sábado) — um card por dia, navegável
# --------------------------------------------------------------------------- #
st.subheader("🗓️ Semana")

if "dash_semana_offset" not in st.session_state:
    st.session_state.dash_semana_offset = 0

domingo_atual = hoje - timedelta(days=(hoje.weekday() + 1) % 7)
semana_inicio = domingo_atual + timedelta(weeks=st.session_state.dash_semana_offset)
semana_fim = semana_inicio + timedelta(days=6)

nav_ant, nav_label, nav_prox = st.columns([1, 5, 1])
if nav_ant.button("◀", use_container_width=True, key="semana_ant"):
    st.session_state.dash_semana_offset -= 1
    st.rerun()
rotulo_semana = f'{semana_inicio.strftime("%d/%m")} – {semana_fim.strftime("%d/%m/%Y")}'
if st.session_state.dash_semana_offset != 0:
    rotulo_semana += " · fora da semana atual"
nav_label.markdown(
    f'<div style="text-align:center; padding-top:8px;"><b>{rotulo_semana}</b></div>',
    unsafe_allow_html=True,
)
if nav_prox.button("▶", use_container_width=True, key="semana_prox"):
    st.session_state.dash_semana_offset += 1
    st.rerun()

viagens_por_dia: dict = {}
for v in viagens:
    d = v.dataHoraSaida.date()
    viagens_por_dia[d] = viagens_por_dia.get(d, 0) + 1

dias_cols = st.columns(7)
for i, col in enumerate(dias_cols):
    dia = semana_inicio + timedelta(days=i)
    qtd = viagens_por_dia.get(dia, 0)
    borda = f"border-color:{AZUL}; border-width:2px;" if dia == hoje else ""
    cor_qtd = AZUL_CLARO if qtd else "#9aa5b1"
    with col:
        st.markdown(
            f'<div class="card" style="text-align:center; {borda}">'
            f'<small>{nome_dia_semana(dia, abreviado=True)}</small><br>'
            f'<b>{dia.strftime("%d/%m")}</b><br>'
            f'<span style="color:{cor_qtd}">{qtd} viagem(ns)</span></div>',
            unsafe_allow_html=True,
        )
        if st.button("Ver", use_container_width=True, key=f"dia_{dia.isoformat()}"):
            st.switch_page("pages/1_📅_Calendário.py")

st.divider()
st.caption("Dados de demonstração (mock). Pronto para conectar ao Firebase — "
           "veja `services/firebase_repository.py`.")
