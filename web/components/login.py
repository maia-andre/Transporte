"""Tela de login + auto-cadastro do painel.

Autenticação local por enquanto (sem Firebase): auto-cadastro é livre e sempre
vira **SOLICITANTE**; o papel de **CONTROLADOR** só é concedido por um
controlador já existente (tela Usuários), igual ao desenho original do
Firebase (self-signup -> SOLICITANTE, promoção pelo painel).
"""
from __future__ import annotations

import streamlit as st

from domain import EmailJaCadastrado, Role
from services import get_repository

from .auth import definir_usuario_logado
from .theme import header


def render_login() -> None:
    header("Transporte SJC", "Entre com sua conta ou crie uma nova")
    repo = get_repository()

    aba_entrar, aba_cadastro = st.tabs(["Entrar", "Criar conta"])

    with aba_entrar:
        with st.form("form_login"):
            email = st.text_input("E-mail", key="login_email")
            senha = st.text_input("Senha", type="password", key="login_senha")
            ok = st.form_submit_button("Entrar", type="primary", key="login_submit")
            if ok:
                usuario = repo.autenticar(email, senha)
                if usuario is None:
                    st.error("E-mail ou senha inválidos.")
                else:
                    definir_usuario_logado(usuario)
                    st.rerun()

    with aba_cadastro:
        st.caption(
            "Cadastro livre — você entra como **requisitante**. O papel de "
            "controlador é concedido por um controlador já existente (tela Usuários)."
        )
        secretarias = repo.list_secretarias()
        with st.form("form_cadastro", clear_on_submit=True):
            nome = st.text_input("Nome completo", key="cadastro_nome")
            email_c = st.text_input("E-mail", key="cadastro_email")
            secretaria = st.selectbox(
                "Secretaria", secretarias, key="cadastro_secretaria",
                format_func=lambda s: f"{s.nome} ({s.codigo})",
            ) if secretarias else None
            senha_c = st.text_input("Senha", type="password", key="cadastro_senha")
            senha_c2 = st.text_input("Confirmar senha", type="password", key="cadastro_senha2")
            ok_c = st.form_submit_button("Criar conta", type="primary", key="cadastro_submit")
            if ok_c:
                if not nome.strip() or not email_c.strip():
                    st.error("Informe nome e e-mail.")
                elif secretaria is None:
                    st.error("Cadastre ao menos uma secretaria antes de criar contas.")
                elif len(senha_c) < 6:
                    st.error("A senha deve ter pelo menos 6 caracteres.")
                elif senha_c != senha_c2:
                    st.error("As senhas não conferem.")
                else:
                    try:
                        repo.criar_usuario(
                            nome=nome, email=email_c, senha=senha_c,
                            secretaria_id=secretaria.codigo, role=Role.SOLICITANTE,
                        )
                        st.success("Conta criada! Entre pela aba “Entrar”.")
                    except EmailJaCadastrado:
                        st.error("Já existe uma conta com esse e-mail.")
