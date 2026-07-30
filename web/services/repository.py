"""Interface de acesso a dados (contrato Mock <-> Firebase).

As páginas do painel SÓ conhecem esta interface. Hoje a implementação é
``MockRepository`` (em memória); amanhã, ``FirebaseRepository`` (Firestore via
Admin SDK). Trocar uma pela outra é um único ponto em ``services/__init__.py``.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime

from domain import (
    Motorista,
    Role,
    Secretaria,
    Usuario,
    Veiculo,
    Viagem,
)


class Repository(ABC):
    # ---- Secretarias ---------------------------------------------------- #
    @abstractmethod
    def list_secretarias(self) -> list[Secretaria]: ...

    @abstractmethod
    def get_secretaria(self, codigo: int) -> Secretaria | None: ...

    @abstractmethod
    def upsert_secretaria(self, s: Secretaria) -> None: ...

    @abstractmethod
    def delete_secretaria(self, codigo: int) -> None: ...

    # ---- Motoristas ----------------------------------------------------- #
    @abstractmethod
    def list_motoristas(self) -> list[Motorista]: ...

    @abstractmethod
    def get_motorista(self, id: str) -> Motorista | None: ...

    @abstractmethod
    def add_motorista(self, m: Motorista) -> str: ...

    @abstractmethod
    def update_motorista(self, m: Motorista) -> None: ...

    @abstractmethod
    def delete_motorista(self, id: str) -> None: ...

    # ---- Veículos ------------------------------------------------------- #
    @abstractmethod
    def list_veiculos(self) -> list[Veiculo]: ...

    @abstractmethod
    def get_veiculo(self, id: str) -> Veiculo | None: ...

    @abstractmethod
    def add_veiculo(self, v: Veiculo) -> str: ...

    @abstractmethod
    def update_veiculo(self, v: Veiculo) -> None: ...

    @abstractmethod
    def delete_veiculo(self, id: str) -> None: ...

    # ---- Usuários ------------------------------------------------------- #
    @abstractmethod
    def list_usuarios(self) -> list[Usuario]: ...

    @abstractmethod
    def add_usuario(self, u: Usuario) -> str: ...

    @abstractmethod
    def update_usuario(self, u: Usuario) -> None: ...

    def set_role(self, uid: str, role: Role) -> None:
        """Promove/rebaixa um usuário. No Firebase isto também grava o custom claim."""
        u = next((x for x in self.list_usuarios() if x.uid == uid), None)
        if u is None:
            raise KeyError(uid)
        u.role = role
        self.update_usuario(u)

    # ---- Autenticação (local, enquanto não há Firebase Auth) ------------- #
    @abstractmethod
    def criar_usuario(
        self,
        *,
        nome: str,
        email: str,
        senha: str,
        secretaria_id: int | None,
        role: Role = Role.SOLICITANTE,
    ) -> str:
        """Auto-cadastro. Levanta ``EmailJaCadastrado`` se o e-mail já existir."""
        ...

    @abstractmethod
    def autenticar(self, email: str, senha: str) -> Usuario | None:
        """Retorna o ``Usuario`` se e-mail/senha conferirem, senão ``None``."""
        ...

    # ---- Viagens -------------------------------------------------------- #
    @abstractmethod
    def list_viagens(self) -> list[Viagem]: ...

    @abstractmethod
    def get_viagem(self, id: str) -> Viagem | None: ...

    @abstractmethod
    def add_viagem(self, v: Viagem) -> str: ...

    @abstractmethod
    def update_viagem(self, v: Viagem) -> None: ...

    # Operações de alto nível (a regra de conflito é checada na camada de domínio
    # pelas páginas antes de chamar ``aceitar_viagem``).
    @abstractmethod
    def aceitar_viagem(
        self,
        viagem_id: str,
        *,
        motorista_id: str,
        veiculo_id: str,
        decidido_por: str,
        quando: datetime,
    ) -> None: ...

    @abstractmethod
    def rejeitar_viagem(
        self,
        viagem_id: str,
        *,
        motivo: str,
        decidido_por: str,
        quando: datetime,
    ) -> None: ...

    @abstractmethod
    def cancelar_viagem(self, viagem_id: str, *, quando: datetime) -> None: ...
