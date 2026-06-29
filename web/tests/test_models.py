"""Testes unitários do mapeamento entidade <-> documento (to_dict/from_dict)."""
from datetime import datetime

from domain import (
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


def test_secretaria_round_trip():
    s = Secretaria(5, "Gabinete do Prefeito", "GP")
    assert Secretaria.from_dict(s.to_dict()) == s


def test_motorista_to_dict_sem_id_e_status_string():
    m = Motorista("m1", "João", "MAT-1", "Motorista", 10,
                  cnhCategoria="D", status=StatusMotorista.ATIVO)
    d = m.to_dict()
    assert "id" not in d
    assert d["status"] == "ATIVO"
    assert Motorista.from_dict("m1", d) == m


def test_veiculo_round_trip_enums_viram_string():
    v = Veiculo("v1", "GP-01", "ABC1D23", "PAT-1", "Onix", 10,
                ano=2022, capacidade=5, combustivel=Combustivel.FLEX,
                status=StatusVeiculo.DISPONIVEL)
    d = v.to_dict()
    assert d["combustivel"] == "FLEX"
    assert d["status"] == "DISPONIVEL"
    assert "id" not in d
    assert Veiculo.from_dict("v1", d) == v


def test_usuario_round_trip():
    u = Usuario("u1", "Ana", "ana@sjc.sp.gov.br", Role.CONTROLADOR, 10)
    d = u.to_dict()
    assert d["role"] == "CONTROLADOR"
    assert Usuario.from_dict("u1", d) == u


def test_viagem_round_trip():
    agora = datetime(2026, 6, 28, 8, 0)
    fim = datetime(2026, 6, 28, 12, 0)
    v = Viagem("t1", "u1", "Carlos", 5, "A", "B", agora, fim, 2, "reunião",
               status=StatusViagem.PENDENTE)
    d = v.to_dict()
    assert d["status"] == "PENDENTE"
    assert "id" not in d
    assert Viagem.from_dict("t1", d) == v
