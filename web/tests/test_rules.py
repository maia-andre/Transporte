"""Testes unitários das regras de negócio: conflito de escala e máquina de estados."""
from datetime import datetime

import pytest

from domain import StatusViagem, Viagem
from domain.rules import (
    ConflitoEscala,
    TransicaoInvalida,
    checar_conflito,
    conflitos,
    transicoes_validas,
    validar_transicao,
)


def _viagem(id, ini, fim, *, status=StatusViagem.ACEITA, motorista=None, veiculo=None):
    return Viagem(id, "u1", "Sol", 5, "A", "B",
                  datetime(2026, 6, 28, ini, 0), datetime(2026, 6, 28, fim, 0),
                  1, "x", status=status, motoristaId=motorista, veiculoId=veiculo)


# --------------------------- conflito de escala ---------------------------- #
def test_conflito_mesmo_motorista_sobreposto():
    existentes = [_viagem("t1", 8, 12, motorista="m1", veiculo="v1")]
    with pytest.raises(ConflitoEscala):
        checar_conflito(existentes, motorista_id="m1", veiculo_id="v9",
                        inicio=datetime(2026, 6, 28, 10, 0),
                        fim=datetime(2026, 6, 28, 14, 0))


def test_conflito_mesmo_veiculo_sobreposto():
    existentes = [_viagem("t1", 8, 12, motorista="m1", veiculo="v1")]
    with pytest.raises(ConflitoEscala):
        checar_conflito(existentes, motorista_id="m9", veiculo_id="v1",
                        inicio=datetime(2026, 6, 28, 11, 0),
                        fim=datetime(2026, 6, 28, 13, 0))


def test_sem_conflito_horarios_disjuntos():
    existentes = [_viagem("t1", 8, 12, motorista="m1", veiculo="v1")]
    # encosta no fim (12:00) — não sobrepõe
    checar_conflito(existentes, motorista_id="m1", veiculo_id="v1",
                    inicio=datetime(2026, 6, 28, 12, 0),
                    fim=datetime(2026, 6, 28, 14, 0))


def test_pendente_nao_ocupa_agenda():
    existentes = [_viagem("t1", 8, 12, status=StatusViagem.PENDENTE,
                          motorista="m1", veiculo="v1")]
    # PENDENTE não bloqueia
    checar_conflito(existentes, motorista_id="m1", veiculo_id="v1",
                    inicio=datetime(2026, 6, 28, 9, 0),
                    fim=datetime(2026, 6, 28, 10, 0))


def test_ignorar_id_evita_auto_conflito():
    existentes = [_viagem("t1", 8, 12, motorista="m1", veiculo="v1")]
    achados = conflitos(existentes, motorista_id="m1", veiculo_id="v1",
                        inicio=datetime(2026, 6, 28, 8, 0),
                        fim=datetime(2026, 6, 28, 12, 0), ignorar_id="t1")
    assert achados == []


# --------------------------- máquina de estados ---------------------------- #
def test_transicoes_validas_pendente():
    assert transicoes_validas(StatusViagem.PENDENTE) == {
        StatusViagem.ACEITA, StatusViagem.REJEITADA, StatusViagem.CANCELADA,
    }


def test_transicao_valida_nao_levanta():
    validar_transicao(StatusViagem.ACEITA, StatusViagem.EM_ANDAMENTO)


def test_transicao_invalida_levanta():
    with pytest.raises(TransicaoInvalida):
        validar_transicao(StatusViagem.CONCLUIDA, StatusViagem.ACEITA)


def test_estado_final_sem_saida():
    assert transicoes_validas(StatusViagem.REJEITADA) == set()
