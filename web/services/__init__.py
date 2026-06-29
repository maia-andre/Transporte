"""Ponto único de seleção do backend de dados.

``get_repository()`` decide entre Mock (padrão) e Firebase a partir de
``data_source`` nos secrets do Streamlit. No modo mock, o "banco" vive em
``st.session_state`` para persistir durante a sessão de teste.

Este é o ÚNICO lugar que muda quando o Firebase entrar.
"""
from __future__ import annotations

from .mock_data import build_seed
from .mock_repository import MockRepository
from .repository import Repository

__all__ = ["Repository", "MockRepository", "get_repository", "reset_mock_store"]

_STORE_KEY = "_transporte_store"


def _data_source() -> str:
    try:
        import streamlit as st

        return str(st.secrets.get("data_source", "mock")).lower()
    except Exception:
        return "mock"


def get_repository() -> Repository:
    source = _data_source()
    if source == "firebase":
        from .firebase_repository import FirebaseRepository

        return FirebaseRepository()

    # Mock: store por sessão.
    import streamlit as st

    if _STORE_KEY not in st.session_state:
        st.session_state[_STORE_KEY] = build_seed()
    return MockRepository(st.session_state[_STORE_KEY])


def reset_mock_store() -> None:
    """Recarrega os dados de demonstração (botão 'restaurar' do painel)."""
    import streamlit as st

    st.session_state[_STORE_KEY] = build_seed()
