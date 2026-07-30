"""Usuários e papéis.

Auto-cadastro é livre pela tela de login e sempre vira SOLICITANTE; aqui o
controlador promove a MOTORISTA/CONTROLADOR. No Firebase (futuro), a promoção
também grava o custom claim (ver firebase_repository).
"""
from __future__ import annotations

import streamlit as st

from components.auth import exigir_papel
from components.theme import header, secretaria_label, setup_sidebar
from domain import Role
from services import get_repository

header("Usuários e papéis", "Auto-cadastro livre (vira requisitante) · promoção pelo controlador")
setup_sidebar()
exigir_papel(Role.CONTROLADOR)

repo = get_repository()
usuarios = repo.list_usuarios()

ICONE_ROLE = {Role.SOLICITANTE: "🙋", Role.MOTORISTA: "🧑‍✈️", Role.CONTROLADOR: "🛡️"}

st.subheader(f"Usuários ({len(usuarios)})")
for u in usuarios:
    with st.container(border=True):
        c1, c2, c3 = st.columns([3, 2, 2])
        c1.markdown(f"{ICONE_ROLE[u.role]} **{u.nome}**  \n<small>{u.email}</small>",
                    unsafe_allow_html=True)
        c2.markdown(f"Secretaria: **{secretaria_label(repo, u.secretariaId)}**")
        novo = c3.selectbox(
            "Papel", list(Role), index=list(Role).index(u.role),
            format_func=lambda r: r.value.title(), key=f"role_{u.uid}",
        )
        if novo != u.role:
            if c3.button("Aplicar", key=f"apply_{u.uid}", type="primary"):
                repo.set_role(u.uid, novo)
                st.success(f"{u.nome} agora é {novo.value.title()}.")
                st.rerun()
