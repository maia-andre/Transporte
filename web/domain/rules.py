"""Regras de negócio do domínio (independentes de UI e de backend).

- ``checar_conflito``: invariante central — um motorista/veículo não pode estar
  escalado em duas viagens que se sobreponham no tempo.
- máquina de estados da viagem: transições permitidas.
"""
from __future__ import annotations

from datetime import datetime
from typing import Iterable

from .models import StatusViagem, Viagem


class ConflitoEscala(Exception):
    """Levantada quando motorista/veículo já está escalado no período."""


class TransicaoInvalida(Exception):
    """Levantada em uma mudança de status não permitida."""


# Estados que efetivamente ocupam um motorista/veículo na agenda.
ESTADOS_OCUPANTES = {StatusViagem.ACEITA, StatusViagem.EM_ANDAMENTO}

# Estados a partir dos quais o próprio solicitante pode cancelar (antes da
# viagem estar em andamento — depois disso é decisão do controlador/motorista).
CANCELAVEIS_PELO_SOLICITANTE = {StatusViagem.PENDENTE, StatusViagem.ACEITA}

# Máquina de estados: de -> conjunto de destinos válidos.
_TRANSICOES: dict[StatusViagem, set[StatusViagem]] = {
    StatusViagem.PENDENTE: {
        StatusViagem.ACEITA,
        StatusViagem.REJEITADA,
        StatusViagem.CANCELADA,
    },
    StatusViagem.ACEITA: {StatusViagem.EM_ANDAMENTO, StatusViagem.CANCELADA},
    StatusViagem.EM_ANDAMENTO: {StatusViagem.CONCLUIDA, StatusViagem.CANCELADA},
    StatusViagem.CONCLUIDA: set(),
    StatusViagem.REJEITADA: set(),
    StatusViagem.CANCELADA: set(),
}


def transicoes_validas(atual: StatusViagem) -> set[StatusViagem]:
    return set(_TRANSICOES.get(atual, set()))


def validar_transicao(atual: StatusViagem, novo: StatusViagem) -> None:
    if novo not in _TRANSICOES.get(atual, set()):
        raise TransicaoInvalida(
            f"Transição inválida: {atual.value} -> {novo.value}"
        )


def _sobrepoe(ini_a: datetime, fim_a: datetime, ini_b: datetime, fim_b: datetime) -> bool:
    """Dois intervalos [a] e [b] se sobrepõem?"""
    return ini_a < fim_b and ini_b < fim_a


def conflitos(
    viagens: Iterable[Viagem],
    *,
    motorista_id: str | None,
    veiculo_id: str | None,
    inicio: datetime,
    fim: datetime,
    ignorar_id: str | None = None,
) -> list[Viagem]:
    """Retorna as viagens que conflitam com o período/recursos informados."""
    achados: list[Viagem] = []
    for v in viagens:
        if v.id == ignorar_id:
            continue
        if v.status not in ESTADOS_OCUPANTES:
            continue
        mesmo_motorista = motorista_id is not None and v.motoristaId == motorista_id
        mesmo_veiculo = veiculo_id is not None and v.veiculoId == veiculo_id
        if not (mesmo_motorista or mesmo_veiculo):
            continue
        if _sobrepoe(inicio, fim, v.dataHoraSaida, v.dataHoraRetorno):
            achados.append(v)
    return achados


def checar_conflito(
    viagens: Iterable[Viagem],
    *,
    motorista_id: str | None,
    veiculo_id: str | None,
    inicio: datetime,
    fim: datetime,
    ignorar_id: str | None = None,
) -> None:
    """Levanta ``ConflitoEscala`` se houver sobreposição. Use antes de aceitar."""
    achados = conflitos(
        viagens,
        motorista_id=motorista_id,
        veiculo_id=veiculo_id,
        inicio=inicio,
        fim=fim,
        ignorar_id=ignorar_id,
    )
    if achados:
        ids = ", ".join(v.id for v in achados)
        raise ConflitoEscala(
            f"Conflito de agenda com viagem(ns): {ids}"
        )
