"""Cadastro de motoristas (nome, matrícula, cargo, secretaria + telefone e CNH)."""
from __future__ import annotations

from datetime import date

import streamlit as st

from components.theme import header, secretaria_label, setup_sidebar
from domain import Motorista, StatusMotorista
from services import get_repository

st.set_page_config(page_title="Motoristas · Transporte SJC", page_icon="🧑‍✈️", layout="wide")
header("Motoristas", "Cadastro da equipe de condutores")
setup_sidebar()

repo = get_repository()
secretarias = repo.list_secretarias()
CATEGORIAS = ["A", "B", "AB", "C", "D", "E"]


def _sec_index(codigo: int) -> int:
    return next((i for i, s in enumerate(secretarias) if s.codigo == codigo), 0)


# --------------------------------------------------------------------------- #
# Novo motorista
# --------------------------------------------------------------------------- #
with st.expander("➕ Novo motorista", expanded=False):
    with st.form("novo_motorista", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        nome = c1.text_input("Nome")
        matricula = c2.text_input("Matrícula")
        cargo = c3.text_input("Cargo", value="Motorista")
        sec = c1.selectbox("Secretaria", secretarias,
                           format_func=lambda s: f"{s.nome} ({s.codigo})")
        telefone = c2.text_input("Telefone")
        c4, c5, c6 = st.columns(3)
        cnh_num = c4.text_input("CNH — número")
        cnh_cat = c5.selectbox("CNH — categoria", CATEGORIAS, index=1)
        cnh_val = c6.date_input("CNH — validade", value=date.today())
        if st.form_submit_button("Cadastrar", type="primary"):
            if not nome or not matricula:
                st.error("Nome e matrícula são obrigatórios.")
            else:
                repo.add_motorista(Motorista(
                    id="", nome=nome, matricula=matricula, cargo=cargo,
                    secretariaId=sec.codigo, telefone=telefone,
                    cnhNumero=cnh_num, cnhCategoria=cnh_cat,
                    cnhValidade=cnh_val.isoformat(),
                    status=StatusMotorista.ATIVO,
                ))
                st.success(f"Motorista {nome} cadastrado.")
                st.rerun()

st.divider()

# --------------------------------------------------------------------------- #
# Lista + edição
# --------------------------------------------------------------------------- #
motoristas = repo.list_motoristas()
st.subheader(f"Cadastrados ({len(motoristas)})")
for m in motoristas:
    marca = "🟢" if m.status == StatusMotorista.ATIVO else "⚪"
    with st.expander(f"{marca} {m.nome} · {m.matricula} · {secretaria_label(repo, m.secretariaId)}"):
        with st.form(f"edit_{m.id}"):
            c1, c2, c3 = st.columns(3)
            nome = c1.text_input("Nome", m.nome)
            matricula = c2.text_input("Matrícula", m.matricula)
            cargo = c3.text_input("Cargo", m.cargo)
            sec = c1.selectbox("Secretaria", secretarias, index=_sec_index(m.secretariaId),
                               format_func=lambda s: f"{s.nome} ({s.codigo})")
            telefone = c2.text_input("Telefone", m.telefone)
            status = c3.selectbox("Status", list(StatusMotorista),
                                  index=list(StatusMotorista).index(m.status),
                                  format_func=lambda s: s.value.title())
            c4, c5, c6 = st.columns(3)
            cnh_num = c4.text_input("CNH — número", m.cnhNumero)
            cnh_cat = c5.selectbox("CNH — categoria", CATEGORIAS,
                                   index=CATEGORIAS.index(m.cnhCategoria)
                                   if m.cnhCategoria in CATEGORIAS else 1)
            cnh_val = c6.text_input("CNH — validade (AAAA-MM-DD)", m.cnhValidade)
            b1, b2 = st.columns(2)
            if b1.form_submit_button("Salvar", type="primary"):
                repo.update_motorista(Motorista(
                    id=m.id, nome=nome, matricula=matricula, cargo=cargo,
                    secretariaId=sec.codigo, telefone=telefone, cnhNumero=cnh_num,
                    cnhCategoria=cnh_cat, cnhValidade=cnh_val,
                    usuarioId=m.usuarioId, status=status,
                ))
                st.success("Atualizado.")
                st.rerun()
            if b2.form_submit_button("Excluir"):
                repo.delete_motorista(m.id)
                st.warning("Excluído.")
                st.rerun()
