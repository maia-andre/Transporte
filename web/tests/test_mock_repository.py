"""Testes de integração do MockRepository + regras (fluxo do controlador)."""
from datetime import datetime

import pytest

from domain import (
    Motorista,
    Role,
    StatusMotorista,
    StatusViagem,
    Viagem,
)
from domain.rules import ConflitoEscala, TransicaoInvalida, checar_conflito
from services.mock_data import build_seed
from services.mock_repository import MockRepository


@pytest.fixture
def repo():
    return MockRepository(build_seed())


def test_seed_tem_dados(repo):
    assert len(repo.list_secretarias()) == 3
    assert repo.get_secretaria(5).sigla == "GP"
    assert len(repo.list_motoristas()) >= 1
    assert len(repo.list_viagens()) >= 1


def test_crud_motorista(repo):
    novo = Motorista("", "Teste", "MAT-9", "Motorista", 10,
                     cnhCategoria="B", status=StatusMotorista.ATIVO)
    mid = repo.add_motorista(novo)
    assert repo.get_motorista(mid).nome == "Teste"

    m = repo.get_motorista(mid)
    m.nome = "Teste Editado"
    repo.update_motorista(m)
    assert repo.get_motorista(mid).nome == "Teste Editado"

    repo.delete_motorista(mid)
    assert repo.get_motorista(mid) is None


def test_aceitar_define_escala_e_status(repo):
    pend = next(v for v in repo.list_viagens() if v.status == StatusViagem.PENDENTE)
    repo.aceitar_viagem(pend.id, motorista_id="m1", veiculo_id="v1",
                        decidido_por="u_ctrl", quando=datetime.now())
    v = repo.get_viagem(pend.id)
    assert v.status == StatusViagem.ACEITA
    assert v.motoristaId == "m1" and v.veiculoId == "v1"
    assert v.decididoPor == "u_ctrl"


def test_rejeitar_grava_motivo(repo):
    pend = next(v for v in repo.list_viagens() if v.status == StatusViagem.PENDENTE)
    repo.rejeitar_viagem(pend.id, motivo="Sem frota", decidido_por="u_ctrl",
                         quando=datetime.now())
    v = repo.get_viagem(pend.id)
    assert v.status == StatusViagem.REJEITADA
    assert v.motivoRejeicao == "Sem frota"


def test_aceitar_viagem_concluida_falha(repo):
    concluida = next(v for v in repo.list_viagens() if v.status == StatusViagem.CONCLUIDA)
    with pytest.raises(TransicaoInvalida):
        repo.aceitar_viagem(concluida.id, motorista_id="m1", veiculo_id="v1",
                            decidido_por="u_ctrl", quando=datetime.now())


def test_set_role(repo):
    sol = next(u for u in repo.list_usuarios() if u.role == Role.SOLICITANTE)
    repo.set_role(sol.uid, Role.MOTORISTA)
    atualizado = next(u for u in repo.list_usuarios() if u.uid == sol.uid)
    assert atualizado.role == Role.MOTORISTA


def test_fluxo_ponta_a_ponta_com_conflito(repo):
    """Cria duas viagens sobrepostas; aceita a 1ª e a 2ª deve conflitar p/ mesmo motorista."""
    saida = datetime(2026, 7, 1, 9, 0)
    retorno = datetime(2026, 7, 1, 12, 0)
    t1 = repo.add_viagem(Viagem("", "u_sol1", "Carlos", 5, "A", "B",
                                saida, retorno, 1, "r1", status=StatusViagem.PENDENTE))
    t2 = repo.add_viagem(Viagem("", "u_sol2", "Bia", 15, "C", "D",
                                datetime(2026, 7, 1, 10, 0), datetime(2026, 7, 1, 11, 0),
                                1, "r2", status=StatusViagem.PENDENTE))

    repo.aceitar_viagem(t1, motorista_id="m1", veiculo_id="v1",
                        decidido_por="u_ctrl", quando=datetime.now())

    v2 = repo.get_viagem(t2)
    with pytest.raises(ConflitoEscala):
        checar_conflito(repo.list_viagens(), motorista_id="m1", veiculo_id="v2",
                        inicio=v2.dataHoraSaida, fim=v2.dataHoraRetorno, ignorar_id=t2)

    # outro motorista/veículo livre -> sem conflito, aceita normalmente
    checar_conflito(repo.list_viagens(), motorista_id="m2", veiculo_id="v3",
                    inicio=v2.dataHoraSaida, fim=v2.dataHoraRetorno, ignorar_id=t2)
    repo.aceitar_viagem(t2, motorista_id="m2", veiculo_id="v3",
                        decidido_por="u_ctrl", quando=datetime.now())
    assert repo.get_viagem(t2).status == StatusViagem.ACEITA
