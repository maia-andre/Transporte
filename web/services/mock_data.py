"""Dados de demonstração (seed) para o repositório em memória.

Serve para o painel ser testável sem Firebase. As datas das viagens são geradas
em torno de "agora" para popularem a agenda do calendário.
"""
from __future__ import annotations

from datetime import datetime, timedelta

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

Store = dict[str, dict]


def _hoje_as(hora: int, minuto: int = 0, dia_offset: int = 0) -> datetime:
    base = datetime.now().replace(second=0, microsecond=0)
    base = base.replace(hour=hora, minute=minuto)
    return base + timedelta(days=dia_offset)


def build_seed() -> Store:
    secretarias = {
        5: Secretaria(5, "Gabinete do Prefeito", "GP"),
        10: Secretaria(10, "Secretaria de Governança", "SG"),
        15: Secretaria(15, "Secretaria de Assuntos Jurídicos", "SAJ"),
    }

    usuarios = {
        "u_ctrl": Usuario("u_ctrl", "Ana Controladora", "ana.controle@sjc.sp.gov.br",
                          Role.CONTROLADOR, 10, criadoEm=datetime.now()),
        "u_sol1": Usuario("u_sol1", "Carlos Solicitante", "carlos.silva@sjc.sp.gov.br",
                          Role.SOLICITANTE, 5, criadoEm=datetime.now()),
        "u_sol2": Usuario("u_sol2", "Beatriz Souza", "beatriz.souza@sjc.sp.gov.br",
                          Role.SOLICITANTE, 15, criadoEm=datetime.now()),
        "u_mot1": Usuario("u_mot1", "João Motorista", "joao.motorista@sjc.sp.gov.br",
                          Role.MOTORISTA, 10, criadoEm=datetime.now()),
    }

    motoristas = {
        "m1": Motorista("m1", "João Pereira", "MAT-1001", "Motorista Oficial", 10,
                        telefone="(12) 99999-1001", cnhNumero="01234567890",
                        cnhCategoria="D", cnhValidade="2028-05-30",
                        usuarioId="u_mot1", status=StatusMotorista.ATIVO),
        "m2": Motorista("m2", "Marcos Lima", "MAT-1002", "Motorista", 5,
                        telefone="(12) 99999-1002", cnhNumero="11223344556",
                        cnhCategoria="B", cnhValidade="2026-11-15",
                        status=StatusMotorista.ATIVO),
        "m3": Motorista("m3", "Rita Gomes", "MAT-1003", "Motorista", 15,
                        telefone="(12) 99999-1003", cnhNumero="99887766554",
                        cnhCategoria="D", cnhValidade="2027-02-20",
                        status=StatusMotorista.INATIVO),
    }

    veiculos = {
        "v1": Veiculo("v1", "GP-01", "ABC1D23", "PAT-55001", "Chevrolet Onix", 10,
                      ano=2022, capacidade=5, combustivel=Combustivel.FLEX,
                      status=StatusVeiculo.DISPONIVEL),
        "v2": Veiculo("v2", "SG-07", "EFG4H56", "PAT-55002", "Fiat Toro", 10,
                      ano=2023, capacidade=5, combustivel=Combustivel.DIESEL,
                      status=StatusVeiculo.DISPONIVEL),
        "v3": Veiculo("v3", "SAJ-03", "IJK7L89", "PAT-55003", "Renault Master (van)", 15,
                      ano=2021, capacidade=15, combustivel=Combustivel.DIESEL,
                      status=StatusVeiculo.MANUTENCAO),
    }

    viagens = {
        "t1": Viagem(
            "t1", "u_sol1", "Carlos Solicitante", 5,
            "Paço Municipal", "Aeroporto de Guarulhos",
            _hoje_as(8, 0, 0), _hoje_as(13, 0, 0), 2,
            "Transporte de autoridade para evento estadual.",
            status=StatusViagem.PENDENTE, criadoEm=datetime.now(),
        ),
        "t2": Viagem(
            "t2", "u_sol2", "Beatriz Souza", 15,
            "Fórum", "Cartório Central",
            _hoje_as(14, 0, 0), _hoje_as(16, 0, 0), 1,
            "Protocolo de documentos urgentes.",
            status=StatusViagem.PENDENTE, criadoEm=datetime.now(),
        ),
        "t3": Viagem(
            "t3", "u_sol1", "Carlos Solicitante", 10,
            "Secretaria de Governança", "Câmara Municipal",
            _hoje_as(9, 0, 1), _hoje_as(11, 0, 1), 3,
            "Reunião de pauta legislativa.",
            status=StatusViagem.ACEITA, motoristaId="m1", veiculoId="v2",
            decididoPor="u_ctrl", decididoEm=datetime.now(), criadoEm=datetime.now(),
        ),
        "t4": Viagem(
            "t4", "u_sol2", "Beatriz Souza", 15,
            "Fórum", "Defensoria Pública",
            _hoje_as(10, 0, -1), _hoje_as(12, 0, -1), 1,
            "Audiência.",
            status=StatusViagem.CONCLUIDA, motoristaId="m2", veiculoId="v1",
            decididoPor="u_ctrl", decididoEm=datetime.now() - timedelta(days=1),
            criadoEm=datetime.now() - timedelta(days=1),
        ),
        "t5": Viagem(
            "t5", "u_sol1", "Carlos Solicitante", 5,
            "Paço Municipal", "Distrito Industrial",
            _hoje_as(15, 0, -1), _hoje_as(17, 0, -1), 4,
            "Vistoria de obra (sem justificativa de prioridade).",
            status=StatusViagem.REJEITADA, motivoRejeicao="Frota indisponível no período.",
            decididoPor="u_ctrl", decididoEm=datetime.now() - timedelta(days=1),
            criadoEm=datetime.now() - timedelta(days=1),
        ),
    }

    return {
        "secretarias": secretarias,
        "usuarios": usuarios,
        "motoristas": motoristas,
        "veiculos": veiculos,
        "viagens": viagens,
    }
