"""Entidades e enums do domínio Transporte SJC.

Cada entidade tem ``to_dict``/``from_dict`` para mapear 1:1 com documentos do
Firestore — é o que torna a troca Mock -> Firebase trivial. Os valores dos enums
são o **contrato** compartilhado com o app Kotlin: não mude sem versionar.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


# --------------------------------------------------------------------------- #
# Enums (contrato compartilhado com o app)
# --------------------------------------------------------------------------- #
class Role(str, Enum):
    SOLICITANTE = "SOLICITANTE"
    MOTORISTA = "MOTORISTA"
    CONTROLADOR = "CONTROLADOR"


class StatusViagem(str, Enum):
    PENDENTE = "PENDENTE"
    ACEITA = "ACEITA"
    EM_ANDAMENTO = "EM_ANDAMENTO"
    CONCLUIDA = "CONCLUIDA"
    REJEITADA = "REJEITADA"
    CANCELADA = "CANCELADA"


class StatusMotorista(str, Enum):
    ATIVO = "ATIVO"
    INATIVO = "INATIVO"


class StatusVeiculo(str, Enum):
    DISPONIVEL = "DISPONIVEL"
    EM_USO = "EM_USO"
    MANUTENCAO = "MANUTENCAO"


class Combustivel(str, Enum):
    GASOLINA = "GASOLINA"
    ETANOL = "ETANOL"
    DIESEL = "DIESEL"
    FLEX = "FLEX"
    ELETRICO = "ELETRICO"
    GNV = "GNV"


def _enum_value(v: Any) -> Any:
    return v.value if isinstance(v, Enum) else v


# --------------------------------------------------------------------------- #
# Entidades
# --------------------------------------------------------------------------- #
@dataclass
class Secretaria:
    codigo: int  # também é o id do documento (secretarias/{codigo})
    nome: str
    sigla: str

    def to_dict(self) -> dict:
        return {"codigo": self.codigo, "nome": self.nome, "sigla": self.sigla}

    @staticmethod
    def from_dict(d: dict) -> "Secretaria":
        return Secretaria(codigo=int(d["codigo"]), nome=d["nome"], sigla=d["sigla"])


@dataclass
class Usuario:
    uid: str
    nome: str
    email: str
    role: Role = Role.SOLICITANTE
    secretariaId: int | None = None
    fcmTokens: list[str] = field(default_factory=list)
    criadoEm: datetime | None = None

    def to_dict(self) -> dict:
        return {
            "nome": self.nome,
            "email": self.email,
            "role": _enum_value(self.role),
            "secretariaId": self.secretariaId,
            "fcmTokens": list(self.fcmTokens),
            "criadoEm": self.criadoEm,
        }

    @staticmethod
    def from_dict(uid: str, d: dict) -> "Usuario":
        return Usuario(
            uid=uid,
            nome=d["nome"],
            email=d["email"],
            role=Role(d.get("role", "SOLICITANTE")),
            secretariaId=d.get("secretariaId"),
            fcmTokens=list(d.get("fcmTokens", [])),
            criadoEm=d.get("criadoEm"),
        )


@dataclass
class Motorista:
    id: str
    nome: str
    matricula: str
    cargo: str
    secretariaId: int
    telefone: str = ""
    cnhNumero: str = ""
    cnhCategoria: str = ""
    cnhValidade: str = ""  # ISO date (YYYY-MM-DD)
    usuarioId: str | None = None
    status: StatusMotorista = StatusMotorista.ATIVO

    def to_dict(self) -> dict:
        d = asdict(self)
        d.pop("id")
        d["status"] = _enum_value(self.status)
        return d

    @staticmethod
    def from_dict(id: str, d: dict) -> "Motorista":
        return Motorista(
            id=id,
            nome=d["nome"],
            matricula=d["matricula"],
            cargo=d["cargo"],
            secretariaId=int(d["secretariaId"]),
            telefone=d.get("telefone", ""),
            cnhNumero=d.get("cnhNumero", ""),
            cnhCategoria=d.get("cnhCategoria", ""),
            cnhValidade=d.get("cnhValidade", ""),
            usuarioId=d.get("usuarioId"),
            status=StatusMotorista(d.get("status", "ATIVO")),
        )


@dataclass
class Veiculo:
    id: str
    prefixo: str
    placa: str
    placaPatrimonial: str
    marcaModelo: str
    secretariaId: int
    ano: int = 0
    capacidade: int = 0
    combustivel: Combustivel = Combustivel.FLEX
    status: StatusVeiculo = StatusVeiculo.DISPONIVEL

    def to_dict(self) -> dict:
        d = asdict(self)
        d.pop("id")
        d["combustivel"] = _enum_value(self.combustivel)
        d["status"] = _enum_value(self.status)
        return d

    @staticmethod
    def from_dict(id: str, d: dict) -> "Veiculo":
        return Veiculo(
            id=id,
            prefixo=d["prefixo"],
            placa=d["placa"],
            placaPatrimonial=d.get("placaPatrimonial", ""),
            marcaModelo=d["marcaModelo"],
            secretariaId=int(d["secretariaId"]),
            ano=int(d.get("ano", 0)),
            capacidade=int(d.get("capacidade", 0)),
            combustivel=Combustivel(d.get("combustivel", "FLEX")),
            status=StatusVeiculo(d.get("status", "DISPONIVEL")),
        )


@dataclass
class Viagem:
    id: str
    solicitanteId: str
    solicitanteNome: str
    secretariaId: int
    origem: str
    destino: str
    dataHoraSaida: datetime
    dataHoraRetorno: datetime
    numPassageiros: int
    finalidade: str
    status: StatusViagem = StatusViagem.PENDENTE
    motoristaId: str | None = None
    veiculoId: str | None = None
    decididoPor: str | None = None
    decididoEm: datetime | None = None
    motivoRejeicao: str | None = None
    criadoEm: datetime | None = None
    atualizadoEm: datetime | None = None

    def to_dict(self) -> dict:
        d = asdict(self)
        d.pop("id")
        d["status"] = _enum_value(self.status)
        return d

    @staticmethod
    def from_dict(id: str, d: dict) -> "Viagem":
        return Viagem(
            id=id,
            solicitanteId=d["solicitanteId"],
            solicitanteNome=d["solicitanteNome"],
            secretariaId=int(d["secretariaId"]),
            origem=d["origem"],
            destino=d["destino"],
            dataHoraSaida=d["dataHoraSaida"],
            dataHoraRetorno=d["dataHoraRetorno"],
            numPassageiros=int(d["numPassageiros"]),
            finalidade=d["finalidade"],
            status=StatusViagem(d.get("status", "PENDENTE")),
            motoristaId=d.get("motoristaId"),
            veiculoId=d.get("veiculoId"),
            decididoPor=d.get("decididoPor"),
            decididoEm=d.get("decididoEm"),
            motivoRejeicao=d.get("motivoRejeicao"),
            criadoEm=d.get("criadoEm"),
            atualizadoEm=d.get("atualizadoEm"),
        )
