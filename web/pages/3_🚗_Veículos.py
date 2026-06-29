"""Cadastro de veículos (prefixo, placa, placa patrimonial, modelo, secretaria...)."""
from __future__ import annotations

from datetime import date

import streamlit as st

from components.theme import header, secretaria_label, setup_sidebar
from domain import Combustivel, StatusVeiculo, Veiculo
from services import get_repository

st.set_page_config(page_title="Veículos · Transporte SJC", page_icon="🚗", layout="wide")
header("Veículos", "Cadastro da frota")
setup_sidebar()

repo = get_repository()
secretarias = repo.list_secretarias()
COMBUSTIVEIS = list(Combustivel)
ANO_ATUAL = date.today().year


def _sec_index(codigo: int) -> int:
    return next((i for i, s in enumerate(secretarias) if s.codigo == codigo), 0)


# --------------------------------------------------------------------------- #
# Novo veículo
# --------------------------------------------------------------------------- #
with st.expander("➕ Novo veículo", expanded=False):
    with st.form("novo_veiculo", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        prefixo = c1.text_input("Prefixo")
        placa = c2.text_input("Placa")
        placa_pat = c3.text_input("Placa patrimonial")
        marca = c1.text_input("Marca/Modelo")
        sec = c2.selectbox("Secretaria", secretarias,
                           format_func=lambda s: f"{s.nome} ({s.codigo})")
        ano = c3.number_input("Ano", min_value=1990, max_value=ANO_ATUAL + 1, value=ANO_ATUAL)
        c4, c5, c6 = st.columns(3)
        cap = c4.number_input("Capacidade (passageiros)", min_value=1, value=5)
        comb = c5.selectbox("Combustível", COMBUSTIVEIS, format_func=lambda c: c.value.title())
        status = c6.selectbox("Status", list(StatusVeiculo),
                              format_func=lambda s: s.value.replace("_", " ").title())
        if st.form_submit_button("Cadastrar", type="primary"):
            if not prefixo or not placa:
                st.error("Prefixo e placa são obrigatórios.")
            else:
                repo.add_veiculo(Veiculo(
                    id="", prefixo=prefixo, placa=placa, placaPatrimonial=placa_pat,
                    marcaModelo=marca, secretariaId=sec.codigo, ano=int(ano),
                    capacidade=int(cap), combustivel=comb, status=status,
                ))
                st.success(f"Veículo {prefixo} cadastrado.")
                st.rerun()

st.divider()

# --------------------------------------------------------------------------- #
# Lista + edição
# --------------------------------------------------------------------------- #
veiculos = repo.list_veiculos()
st.subheader(f"Cadastrados ({len(veiculos)})")
ICONE_STATUS = {
    StatusVeiculo.DISPONIVEL: "🟢",
    StatusVeiculo.EM_USO: "🔵",
    StatusVeiculo.MANUTENCAO: "🟠",
}
for v in veiculos:
    titulo = (f"{ICONE_STATUS[v.status]} {v.prefixo} · {v.placa} · {v.marcaModelo} "
              f"· {secretaria_label(repo, v.secretariaId)}")
    with st.expander(titulo):
        with st.form(f"edit_{v.id}"):
            c1, c2, c3 = st.columns(3)
            prefixo = c1.text_input("Prefixo", v.prefixo)
            placa = c2.text_input("Placa", v.placa)
            placa_pat = c3.text_input("Placa patrimonial", v.placaPatrimonial)
            marca = c1.text_input("Marca/Modelo", v.marcaModelo)
            sec = c2.selectbox("Secretaria", secretarias, index=_sec_index(v.secretariaId),
                               format_func=lambda s: f"{s.nome} ({s.codigo})")
            ano = c3.number_input("Ano", min_value=1990, max_value=ANO_ATUAL + 1,
                                  value=v.ano or ANO_ATUAL)
            c4, c5, c6 = st.columns(3)
            cap = c4.number_input("Capacidade", min_value=1, value=v.capacidade or 1)
            comb = c5.selectbox("Combustível", COMBUSTIVEIS,
                                index=COMBUSTIVEIS.index(v.combustivel),
                                format_func=lambda c: c.value.title())
            status = c6.selectbox("Status", list(StatusVeiculo),
                                  index=list(StatusVeiculo).index(v.status),
                                  format_func=lambda s: s.value.replace("_", " ").title())
            b1, b2 = st.columns(2)
            if b1.form_submit_button("Salvar", type="primary"):
                repo.update_veiculo(Veiculo(
                    id=v.id, prefixo=prefixo, placa=placa, placaPatrimonial=placa_pat,
                    marcaModelo=marca, secretariaId=sec.codigo, ano=int(ano),
                    capacidade=int(cap), combustivel=comb, status=status,
                ))
                st.success("Atualizado.")
                st.rerun()
            if b2.form_submit_button("Excluir"):
                repo.delete_veiculo(v.id)
                st.warning("Excluído.")
                st.rerun()
