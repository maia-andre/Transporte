"""Identidade visual SJC e helpers de UI para o painel.

Paleta: azul institucional (primária), dourado (destaque), verde (positivo).
Cores de status iguais às do app, para a sensação de produto único.
"""
from __future__ import annotations

from datetime import datetime

import streamlit as st

from domain import Role, StatusViagem
from services import Repository, get_repository

# --------------------------------------------------------------------------- #
# Paleta
# --------------------------------------------------------------------------- #
AZUL = "#0B3C7A"
AZUL_CLARO = "#1565C0"
DOURADO = "#C8A24B"
VERDE = "#2E7D32"
VERMELHO = "#C62828"
TEXTO = "#1A2733"
SUPERFICIE = "#F2F5F9"

STATUS_COR: dict[StatusViagem, str] = {
    StatusViagem.PENDENTE: DOURADO,
    StatusViagem.ACEITA: AZUL,
    StatusViagem.EM_ANDAMENTO: AZUL_CLARO,
    StatusViagem.CONCLUIDA: VERDE,
    StatusViagem.REJEITADA: VERMELHO,
    StatusViagem.CANCELADA: VERMELHO,
}

STATUS_ROTULO: dict[StatusViagem, str] = {
    StatusViagem.PENDENTE: "Pendente",
    StatusViagem.ACEITA: "Aceita",
    StatusViagem.EM_ANDAMENTO: "Em andamento",
    StatusViagem.CONCLUIDA: "Concluída",
    StatusViagem.REJEITADA: "Rejeitada",
    StatusViagem.CANCELADA: "Cancelada",
}


def inject_css() -> None:
    st.markdown(
        f"""
        <style>
          .sjc-header {{
            background: linear-gradient(90deg, {AZUL} 0%, {AZUL_CLARO} 100%);
            border-bottom: 4px solid {DOURADO};
            padding: 16px 22px; border-radius: 10px; margin-bottom: 18px;
            color: #fff;
          }}
          .sjc-header h1 {{ margin: 0; font-size: 1.45rem; color: #fff; }}
          .sjc-header p  {{ margin: 2px 0 0; opacity: .9; font-size: .9rem; }}
          .chip {{
            display: inline-block; padding: 2px 10px; border-radius: 999px;
            color: #fff; font-size: .78rem; font-weight: 600; white-space: nowrap;
          }}
          .card {{
            border: 1px solid #e3e8ef; border-left: 5px solid {AZUL};
            border-radius: 10px; padding: 12px 14px; margin-bottom: 10px;
            background: #fff;
          }}
          div.stButton > button[kind="primary"] {{ background: {AZUL}; border-color: {AZUL}; }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def header(titulo: str, subtitulo: str = "") -> None:
    inject_css()
    st.markdown(
        f'<div class="sjc-header"><h1>🚐 {titulo}</h1>'
        f'<p>{subtitulo}</p></div>',
        unsafe_allow_html=True,
    )


def status_chip(status: StatusViagem) -> str:
    cor = STATUS_COR[status]
    rotulo = STATUS_ROTULO[status]
    return f'<span class="chip" style="background:{cor}">{rotulo}</span>'


def fmt_dt(dt: datetime | None) -> str:
    return dt.strftime("%d/%m/%Y %H:%M") if dt else "—"


def fmt_periodo(ini: datetime, fim: datetime) -> str:
    if ini.date() == fim.date():
        return f'{ini.strftime("%d/%m %H:%M")} → {fim.strftime("%H:%M")}'
    return f"{fmt_dt(ini)} → {fmt_dt(fim)}"


def secretaria_label(repo: Repository, codigo: int | None) -> str:
    if codigo is None:
        return "—"
    s = repo.get_secretaria(codigo)
    return f"{s.sigla} ({s.codigo})" if s else f"#{codigo}"


# --------------------------------------------------------------------------- #
# Identidade do operador (mock) — usada como ``decididoPor``
# --------------------------------------------------------------------------- #
def setup_sidebar() -> None:
    """Barra lateral comum: identidade do operador e ações de demonstração."""
    repo = get_repository()
    controladores = [u for u in repo.list_usuarios() if u.role == Role.CONTROLADOR]
    with st.sidebar:
        st.caption("👤 Operador (controlador)")
        if controladores:
            nomes = {u.nome: u.uid for u in controladores}
            escolha = st.selectbox("Sessão", list(nomes.keys()), key="_operador_nome")
            st.session_state["_operador_uid"] = nomes[escolha]
        st.divider()
        st.caption("🧪 Demonstração (dados mockados)")
        if st.button("Restaurar dados de exemplo", use_container_width=True):
            from services import reset_mock_store

            reset_mock_store()
            st.rerun()
        try:
            src = st.secrets.get("data_source", "mock")
        except Exception:
            src = "mock"
        st.caption(f"Fonte de dados: **{src}**")


def operador_uid() -> str:
    return st.session_state.get("_operador_uid", "u_ctrl")
