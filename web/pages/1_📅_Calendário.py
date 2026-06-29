"""Calendário de requisições — o loop central do controlador.

Requisições entram como PENDENTE; o controlador aceita (atribuindo motorista +
veículo, com checagem de conflito) ou rejeita (com justificativa). Inclui um
formulário para *simular* a requisição de um solicitante (papel do app).
"""
from __future__ import annotations

from datetime import date, datetime, time, timedelta
from itertools import groupby

import streamlit as st

from components.theme import (
    STATUS_COR,
    fmt_periodo,
    header,
    operador_uid,
    secretaria_label,
    setup_sidebar,
    status_chip,
)
from domain import StatusMotorista, StatusVeiculo, StatusViagem, Viagem
from domain.rules import ConflitoEscala, checar_conflito, conflitos
from services import get_repository

st.set_page_config(page_title="Calendário · Transporte SJC", page_icon="📅", layout="wide")
header("Calendário de Requisições", "Trate as viagens: aceite e escale, ou rejeite com justificativa")
setup_sidebar()

repo = get_repository()


# --------------------------------------------------------------------------- #
# Simular requisição (papel do solicitante / app)
# --------------------------------------------------------------------------- #
with st.expander("➕ Nova requisição (simular solicitante)"):
    usuarios = repo.list_usuarios()
    secretarias = repo.list_secretarias()
    with st.form("nova_requisicao", clear_on_submit=True):
        col1, col2 = st.columns(2)
        sol = col1.selectbox("Solicitante", usuarios,
                             format_func=lambda u: f"{u.nome} ({u.email})")
        sec = col2.selectbox("Secretaria", secretarias,
                             format_func=lambda s: f"{s.nome} ({s.codigo})")
        origem = col1.text_input("Origem")
        destino = col2.text_input("Destino")
        d_saida = col1.date_input("Data da saída", value=date.today())
        h_saida = col2.time_input("Hora da saída", value=time(8, 0))
        d_ret = col1.date_input("Data do retorno", value=date.today())
        h_ret = col2.time_input("Hora do retorno", value=time(12, 0))
        n_pax = col1.number_input("Nº de passageiros", min_value=1, value=1, step=1)
        finalidade = st.text_area("Finalidade / justificativa")
        ok = st.form_submit_button("Enviar requisição", type="primary")
        if ok:
            saida = datetime.combine(d_saida, h_saida)
            retorno = datetime.combine(d_ret, h_ret)
            if not origem or not destino:
                st.error("Informe origem e destino.")
            elif retorno <= saida:
                st.error("O retorno deve ser depois da saída.")
            else:
                repo.add_viagem(Viagem(
                    id="", solicitanteId=sol.uid, solicitanteNome=sol.nome,
                    secretariaId=sec.codigo, origem=origem, destino=destino,
                    dataHoraSaida=saida, dataHoraRetorno=retorno,
                    numPassageiros=int(n_pax), finalidade=finalidade,
                    status=StatusViagem.PENDENTE,
                ))
                st.success("Requisição enviada (PENDENTE).")
                st.rerun()

st.divider()

# --------------------------------------------------------------------------- #
# Filtros
# --------------------------------------------------------------------------- #
todas = repo.list_viagens()
fc1, fc2, fc3 = st.columns([1.4, 1.4, 1.2])
ini_padrao = date.today() - timedelta(days=2)
fim_padrao = date.today() + timedelta(days=7)
intervalo = fc1.date_input("Período", value=(ini_padrao, fim_padrao))
if isinstance(intervalo, tuple) and len(intervalo) == 2:
    d_ini, d_fim = intervalo
else:
    d_ini, d_fim = ini_padrao, fim_padrao

status_sel = fc2.multiselect(
    "Status", list(StatusViagem),
    default=list(StatusViagem),
    format_func=lambda s: s.value.replace("_", " ").title(),
)
secs = repo.list_secretarias()
sec_sel = fc3.multiselect("Secretaria", secs, default=secs,
                          format_func=lambda s: s.sigla)
sec_codigos = {s.codigo for s in sec_sel}

filtradas = [
    v for v in todas
    if d_ini <= v.dataHoraSaida.date() <= d_fim
    and v.status in status_sel
    and v.secretariaId in sec_codigos
]

# --------------------------------------------------------------------------- #
# Triagem dos pendentes
# --------------------------------------------------------------------------- #
pendentes = [v for v in filtradas if v.status == StatusViagem.PENDENTE]
st.subheader(f"📥 Para tratar ({len(pendentes)})")
if not pendentes:
    st.info("Sem requisições pendentes no filtro atual.")

motoristas_ativos = [m for m in repo.list_motoristas() if m.status == StatusMotorista.ATIVO]
veiculos_ok = [v for v in repo.list_veiculos() if v.status != StatusVeiculo.MANUTENCAO]

for v in pendentes:
    with st.container(border=True):
        st.markdown(
            f"{status_chip(v.status)} &nbsp; **{v.origem} → {v.destino}**  \n"
            f"🧑 {v.solicitanteNome} · 🏛️ {secretaria_label(repo, v.secretariaId)} · "
            f"🕒 {fmt_periodo(v.dataHoraSaida, v.dataHoraRetorno)} · 👥 {v.numPassageiros}",
            unsafe_allow_html=True,
        )
        if v.finalidade:
            st.caption(f"Finalidade: {v.finalidade}")

        aba_aceitar, aba_rejeitar = st.tabs(["✅ Aceitar e escalar", "⛔ Rejeitar"])

        with aba_aceitar:
            mot = st.selectbox(
                "Motorista", motoristas_ativos,
                format_func=lambda m: f"{m.nome} · {m.matricula} (CNH {m.cnhCategoria})",
                key=f"mot_{v.id}",
            ) if motoristas_ativos else None
            veic = st.selectbox(
                "Veículo", veiculos_ok,
                format_func=lambda x: f"{x.prefixo} · {x.placa} · {x.marcaModelo} "
                                      f"({x.capacidade} lug.)",
                key=f"veic_{v.id}",
            ) if veiculos_ok else None

            if mot and veic:
                # Pré-aviso de conflito (não bloqueia a renderização).
                conf = conflitos(
                    todas, motorista_id=mot.id, veiculo_id=veic.id,
                    inicio=v.dataHoraSaida, fim=v.dataHoraRetorno, ignorar_id=v.id,
                )
                if conf:
                    st.warning("⚠️ Possível conflito: " +
                               ", ".join(f"{c.origem}→{c.destino}" for c in conf))
                if st.button("Confirmar escala", type="primary", key=f"ace_{v.id}"):
                    try:
                        checar_conflito(
                            todas, motorista_id=mot.id, veiculo_id=veic.id,
                            inicio=v.dataHoraSaida, fim=v.dataHoraRetorno, ignorar_id=v.id,
                        )
                        repo.aceitar_viagem(
                            v.id, motorista_id=mot.id, veiculo_id=veic.id,
                            decidido_por=operador_uid(), quando=datetime.now(),
                        )
                        st.success("Viagem aceita e escalada.")
                        st.rerun()
                    except ConflitoEscala as e:
                        st.error(str(e))
            else:
                st.warning("Cadastre motoristas ativos e veículos disponíveis para escalar.")

        with aba_rejeitar:
            motivo = st.text_area("Justificativa (obrigatória)", key=f"mot_rej_{v.id}")
            if st.button("Confirmar rejeição", key=f"rej_{v.id}"):
                if not motivo.strip():
                    st.error("Informe a justificativa.")
                else:
                    repo.rejeitar_viagem(
                        v.id, motivo=motivo.strip(),
                        decidido_por=operador_uid(), quando=datetime.now(),
                    )
                    st.success("Viagem rejeitada.")
                    st.rerun()

st.divider()

# --------------------------------------------------------------------------- #
# Agenda (todas as viagens filtradas, agrupadas por dia)
# --------------------------------------------------------------------------- #
st.subheader("🗓️ Agenda")
agenda = sorted(filtradas, key=lambda v: v.dataHoraSaida)
if not agenda:
    st.info("Nada no período/seleção.")

mot_nome = {m.id: m.nome for m in repo.list_motoristas()}
veic_pref = {x.id: x.prefixo for x in repo.list_veiculos()}

for dia, grupo in groupby(agenda, key=lambda v: v.dataHoraSaida.date()):
    st.markdown(f"#### {dia.strftime('%A, %d/%m/%Y')}")
    for v in grupo:
        escala = ""
        if v.motoristaId or v.veiculoId:
            escala = (f" · 🧑 {mot_nome.get(v.motoristaId, '—')}"
                      f" · 🚗 {veic_pref.get(v.veiculoId, '—')}")
        extra = f" · _{v.motivoRejeicao}_" if v.motivoRejeicao else ""
        st.markdown(
            f'<div class="card" style="border-left-color:{STATUS_COR[v.status]}">'
            f"{status_chip(v.status)} &nbsp; <b>{v.origem} → {v.destino}</b><br>"
            f'<small>{fmt_periodo(v.dataHoraSaida, v.dataHoraRetorno)} · '
            f"{v.solicitanteNome} · {secretaria_label(repo, v.secretariaId)}"
            f"{escala}{extra}</small></div>",
            unsafe_allow_html=True,
        )
