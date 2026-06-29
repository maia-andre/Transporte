"""Usuários e papéis.

No Firebase, novos usuários se auto-cadastram pelo app (e-mail @sjc.sp.gov.br) e
entram como SOLICITANTE; aqui o controlador os promove a MOTORISTA/CONTROLADOR.
A promoção grava ``usuarios/{uid}.role`` e o custom claim (ver firebase_repository).
"""
from __future__ import annotations

import streamlit as st

from components.theme import header, secretaria_label, setup_sidebar
from domain import Role
from services import get_repository

st.set_page_config(page_title="Usuários · Transporte SJC", page_icon="👥", layout="wide")
header("Usuários e papéis", "Auto-cadastro restrito a @sjc.sp.gov.br · promoção pelo controlador")
setup_sidebar()

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
