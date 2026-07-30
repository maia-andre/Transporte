"""Camada de domínio: entidades, enums e regras de negócio.

Independente de Streamlit e de Firebase — é o contrato compartilhado com o app.
"""
from .auth import EmailJaCadastrado, hash_senha, verificar_senha
from .models import (
    Combustivel,
    Motorista,
    Role,
    Secretaria,
    StatusMotorista,
    StatusVeiculo,
    StatusViagem,
    Usuario,
    Veiculo,
    Viagem,
)
from .rules import (
    CANCELAVEIS_PELO_SOLICITANTE,
    ConflitoEscala,
    TransicaoInvalida,
    checar_conflito,
    transicoes_validas,
    validar_transicao,
)

__all__ = [
    "Combustivel",
    "Motorista",
    "Role",
    "Secretaria",
    "StatusMotorista",
    "StatusVeiculo",
    "StatusViagem",
    "Usuario",
    "Veiculo",
    "Viagem",
    "CANCELAVEIS_PELO_SOLICITANTE",
    "ConflitoEscala",
    "TransicaoInvalida",
    "checar_conflito",
    "transicoes_validas",
    "validar_transicao",
    "EmailJaCadastrado",
    "hash_senha",
    "verificar_senha",
]
