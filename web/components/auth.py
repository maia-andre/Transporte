"""Sessão do usuário logado e proteção de páginas por papel.

Autenticação local (sem Firebase, por ora): o usuário autenticado fica em
``st.session_state``, igual a qualquer outro estado da sessão do painel.
"""
from __future__ import annotations

import streamlit as st

from domain import Role, Usuario

SESSION_KEY_USUARIO = "_usuario_logado"


def usuario_logado() -> Usuario | None:
    return st.session_state.get(SESSION_KEY_USUARIO)


def definir_usuario_logado(usuario: Usuario) -> None:
    st.session_state[SESSION_KEY_USUARIO] = usuario


def logout() -> None:
    st.session_state.pop(SESSION_KEY_USUARIO, None)


def exigir_papel(*papeis: Role) -> Usuario:
    """Bloqueia a página (``st.stop()``) se não houver login ou o papel não bater.

    Defesa em profundidade: além do menu já filtrar por papel, cada página
    checa de novo — navegar direto para a URL de uma página não basta para
    contornar a restrição.
    """
    usuario = usuario_logado()
    if usuario is None:
        st.warning("Faça login para continuar.")
        st.stop()
    if usuario.role not in papeis:
        st.error("Você não tem permissão para acessar esta página.")
        st.stop()
    return usuario
