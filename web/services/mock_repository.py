"""Implementação em memória do ``Repository``.

Opera sobre um ``store`` (dict de coleções) que o painel mantém em
``st.session_state`` — assim as edições persistem durante a sessão de teste.
A geração de id usa uuid curto, imitando o id de documento do Firestore.
"""
from __future__ import annotations

import uuid
from datetime import datetime

from domain import (
    Motorista,
    Secretaria,
    StatusViagem,
    Usuario,
    Veiculo,
    Viagem,
)
from domain.rules import validar_transicao

from .repository import Repository


def _novo_id() -> str:
    return uuid.uuid4().hex[:8]


class MockRepository(Repository):
    def __init__(self, store: dict[str, dict]):
        self._s = store

    # ---- Secretarias ---------------------------------------------------- #
    def list_secretarias(self) -> list[Secretaria]:
        return sorted(self._s["secretarias"].values(), key=lambda x: x.codigo)

    def get_secretaria(self, codigo: int) -> Secretaria | None:
        return self._s["secretarias"].get(codigo)

    def upsert_secretaria(self, s: Secretaria) -> None:
        self._s["secretarias"][s.codigo] = s

    def delete_secretaria(self, codigo: int) -> None:
        self._s["secretarias"].pop(codigo, None)

    # ---- Motoristas ----------------------------------------------------- #
    def list_motoristas(self) -> list[Motorista]:
        return sorted(self._s["motoristas"].values(), key=lambda x: x.nome)

    def get_motorista(self, id: str) -> Motorista | None:
        return self._s["motoristas"].get(id)

    def add_motorista(self, m: Motorista) -> str:
        if not m.id:
            m.id = _novo_id()
        self._s["motoristas"][m.id] = m
        return m.id

    def update_motorista(self, m: Motorista) -> None:
        self._s["motoristas"][m.id] = m

    def delete_motorista(self, id: str) -> None:
        self._s["motoristas"].pop(id, None)

    # ---- Veículos ------------------------------------------------------- #
    def list_veiculos(self) -> list[Veiculo]:
        return sorted(self._s["veiculos"].values(), key=lambda x: x.prefixo)

    def get_veiculo(self, id: str) -> Veiculo | None:
        return self._s["veiculos"].get(id)

    def add_veiculo(self, v: Veiculo) -> str:
        if not v.id:
            v.id = _novo_id()
        self._s["veiculos"][v.id] = v
        return v.id

    def update_veiculo(self, v: Veiculo) -> None:
        self._s["veiculos"][v.id] = v

    def delete_veiculo(self, id: str) -> None:
        self._s["veiculos"].pop(id, None)

    # ---- Usuários ------------------------------------------------------- #
    def list_usuarios(self) -> list[Usuario]:
        return sorted(self._s["usuarios"].values(), key=lambda x: x.nome)

    def add_usuario(self, u: Usuario) -> str:
        if not u.uid:
            u.uid = _novo_id()
        self._s["usuarios"][u.uid] = u
        return u.uid

    def update_usuario(self, u: Usuario) -> None:
        self._s["usuarios"][u.uid] = u

    # ---- Viagens -------------------------------------------------------- #
    def list_viagens(self) -> list[Viagem]:
        return sorted(self._s["viagens"].values(), key=lambda x: x.dataHoraSaida)

    def get_viagem(self, id: str) -> Viagem | None:
        return self._s["viagens"].get(id)

    def add_viagem(self, v: Viagem) -> str:
        if not v.id:
            v.id = _novo_id()
        if v.criadoEm is None:
            v.criadoEm = datetime.now()
        v.atualizadoEm = datetime.now()
        self._s["viagens"][v.id] = v
        return v.id

    def update_viagem(self, v: Viagem) -> None:
        v.atualizadoEm = datetime.now()
        self._s["viagens"][v.id] = v

    def aceitar_viagem(self, viagem_id, *, motorista_id, veiculo_id, decidido_por, quando) -> None:
        v = self._s["viagens"][viagem_id]
        validar_transicao(v.status, StatusViagem.ACEITA)
        v.status = StatusViagem.ACEITA
        v.motoristaId = motorista_id
        v.veiculoId = veiculo_id
        v.decididoPor = decidido_por
        v.decididoEm = quando
        v.atualizadoEm = quando

    def rejeitar_viagem(self, viagem_id, *, motivo, decidido_por, quando) -> None:
        v = self._s["viagens"][viagem_id]
        validar_transicao(v.status, StatusViagem.REJEITADA)
        v.status = StatusViagem.REJEITADA
        v.motivoRejeicao = motivo
        v.decididoPor = decidido_por
        v.decididoEm = quando
        v.atualizadoEm = quando
