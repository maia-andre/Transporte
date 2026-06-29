"""Camada de domínio: entidades, enums e regras de negócio.

Independente de Streamlit e de Firebase — é o contrato compartilhado com o app.
"""
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
    "ConflitoEscala",
    "TransicaoInvalida",
    "checar_conflito",
    "transicoes_validas",
    "validar_transicao",
]
