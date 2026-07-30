"""Nova requisição de viagem — papel do requisitante (solicitante)."""
from __future__ import annotations

from datetime import date, datetime, time

import streamlit as st

from components.auth import exigir_papel
from components.theme import DATA_FORMATO, header, setup_sidebar
from domain import Role, StatusViagem, Viagem
from services import get_repository

header("Nova Requisição", "Solicite uma viagem para a frota")
setup_sidebar()
usuario = exigir_papel(Role.SOLICITANTE)

repo = get_repository()

with st.form("nova_requisicao_solicitante", clear_on_submit=True):
    col1, col2 = st.columns(2)
    origem = col1.text_input("Origem")
    destino = col2.text_input("Destino")
    d_saida = col1.date_input("Data da saída", value=date.today(), format=DATA_FORMATO)
    h_saida = col2.time_input("Hora da saída", value=time(8, 0))
    d_ret = col1.date_input("Data do retorno", value=date.today(), format=DATA_FORMATO)
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
                id="", solicitanteId=usuario.uid, solicitanteNome=usuario.nome,
                secretariaId=usuario.secretariaId, origem=origem, destino=destino,
                dataHoraSaida=saida, dataHoraRetorno=retorno,
                numPassageiros=int(n_pax), finalidade=finalidade,
                status=StatusViagem.PENDENTE,
            ))
            st.success("Requisição enviada! Acompanhe em “Minhas Requisições”.")
