"""Implementação Firestore do ``Repository`` — **pronta para conexão**.

Ainda NÃO está em uso (o painel roda com ``MockRepository``). Para ativar:
  1. instale ``firebase-admin`` (já está em requirements.txt);
  2. preencha as credenciais do service account em ``.streamlit/secrets.toml``
     (veja ``secrets.toml.example``);
  3. defina ``data_source = "firebase"`` em ``secrets.toml``.

O mapeamento documento <-> entidade usa ``to_dict``/``from_dict`` dos modelos, que
já refletem os nomes de campo do Firestore. Revise os pontos marcados ``# TODO``
ao validar contra um projeto real (índices, regras, custom claims).
"""
from __future__ import annotations

from datetime import datetime

from domain import (
    Motorista,
    Role,
    Secretaria,
    StatusViagem,
    Usuario,
    Veiculo,
    Viagem,
)
from domain.rules import validar_transicao

from .repository import Repository


class FirebaseRepository(Repository):
    def __init__(self) -> None:
        import firebase_admin
        from firebase_admin import credentials, firestore
        import streamlit as st

        if not firebase_admin._apps:
            # Credenciais do service account vindas dos secrets do Streamlit.
            cred = credentials.Certificate(dict(st.secrets["firebase"]))
            firebase_admin.initialize_app(cred)
        self.db = firestore.client()

    # ---- Secretarias ---------------------------------------------------- #
    def list_secretarias(self) -> list[Secretaria]:
        return [Secretaria.from_dict(d.to_dict())
                for d in self.db.collection("secretarias").stream()]

    def get_secretaria(self, codigo: int) -> Secretaria | None:
        snap = self.db.collection("secretarias").document(str(codigo)).get()
        return Secretaria.from_dict(snap.to_dict()) if snap.exists else None

    def upsert_secretaria(self, s: Secretaria) -> None:
        self.db.collection("secretarias").document(str(s.codigo)).set(s.to_dict())

    def delete_secretaria(self, codigo: int) -> None:
        self.db.collection("secretarias").document(str(codigo)).delete()

    # ---- Motoristas ----------------------------------------------------- #
    def list_motoristas(self) -> list[Motorista]:
        return [Motorista.from_dict(d.id, d.to_dict())
                for d in self.db.collection("motoristas").stream()]

    def get_motorista(self, id: str) -> Motorista | None:
        snap = self.db.collection("motoristas").document(id).get()
        return Motorista.from_dict(snap.id, snap.to_dict()) if snap.exists else None

    def add_motorista(self, m: Motorista) -> str:
        ref = self.db.collection("motoristas").document()
        ref.set(m.to_dict())
        m.id = ref.id
        return ref.id

    def update_motorista(self, m: Motorista) -> None:
        self.db.collection("motoristas").document(m.id).set(m.to_dict())

    def delete_motorista(self, id: str) -> None:
        self.db.collection("motoristas").document(id).delete()

    # ---- Veículos ------------------------------------------------------- #
    def list_veiculos(self) -> list[Veiculo]:
        return [Veiculo.from_dict(d.id, d.to_dict())
                for d in self.db.collection("veiculos").stream()]

    def get_veiculo(self, id: str) -> Veiculo | None:
        snap = self.db.collection("veiculos").document(id).get()
        return Veiculo.from_dict(snap.id, snap.to_dict()) if snap.exists else None

    def add_veiculo(self, v: Veiculo) -> str:
        ref = self.db.collection("veiculos").document()
        ref.set(v.to_dict())
        v.id = ref.id
        return ref.id

    def update_veiculo(self, v: Veiculo) -> None:
        self.db.collection("veiculos").document(v.id).set(v.to_dict())

    def delete_veiculo(self, id: str) -> None:
        self.db.collection("veiculos").document(id).delete()

    # ---- Usuários ------------------------------------------------------- #
    def list_usuarios(self) -> list[Usuario]:
        return [Usuario.from_dict(d.id, d.to_dict())
                for d in self.db.collection("usuarios").stream()]

    def add_usuario(self, u: Usuario) -> str:
        self.db.collection("usuarios").document(u.uid).set(u.to_dict())
        return u.uid

    def update_usuario(self, u: Usuario) -> None:
        self.db.collection("usuarios").document(u.uid).set(u.to_dict())

    def set_role(self, uid: str, role: Role) -> None:
        # Atualiza o doc...
        self.db.collection("usuarios").document(uid).update({"role": role.value})
        # ...e o custom claim (fonte da verdade das regras de segurança).
        from firebase_admin import auth
        auth.set_custom_user_claims(uid, {"role": role.value})  # TODO: validar em produção

    # ---- Autenticação ----------------------------------------------------- #
    def criar_usuario(self, *, nome, email, senha, secretaria_id, role=Role.SOLICITANTE) -> str:
        # TODO: no Firebase real, o auto-cadastro é feito pelo app via Firebase Auth
        # (client SDK) + blocking function `beforeUserCreated`. O painel roda como
        # Admin e não deveria assumir esse fluxo — ver CLAUDE.md § Autenticação.
        raise NotImplementedError(
            "Auto-cadastro é responsabilidade do Firebase Auth (client SDK), não do painel."
        )

    def autenticar(self, email: str, senha: str) -> Usuario | None:
        # TODO: idem — login por senha é do Firebase Auth (client SDK); o Admin SDK
        # não verifica senha de usuário diretamente.
        raise NotImplementedError(
            "Login por senha é responsabilidade do Firebase Auth (client SDK), não do painel."
        )

    # ---- Viagens -------------------------------------------------------- #
    def list_viagens(self) -> list[Viagem]:
        return [Viagem.from_dict(d.id, d.to_dict())
                for d in self.db.collection("viagens").stream()]

    def get_viagem(self, id: str) -> Viagem | None:
        snap = self.db.collection("viagens").document(id).get()
        return Viagem.from_dict(snap.id, snap.to_dict()) if snap.exists else None

    def add_viagem(self, v: Viagem) -> str:
        ref = self.db.collection("viagens").document()
        if v.criadoEm is None:
            v.criadoEm = datetime.now()
        v.atualizadoEm = datetime.now()
        ref.set(v.to_dict())
        v.id = ref.id
        return ref.id

    def update_viagem(self, v: Viagem) -> None:
        v.atualizadoEm = datetime.now()
        self.db.collection("viagens").document(v.id).set(v.to_dict())

    def aceitar_viagem(self, viagem_id, *, motorista_id, veiculo_id, decidido_por, quando) -> None:
        v = self.get_viagem(viagem_id)
        validar_transicao(v.status, StatusViagem.ACEITA)
        self.db.collection("viagens").document(viagem_id).update({
            "status": StatusViagem.ACEITA.value,
            "motoristaId": motorista_id,
            "veiculoId": veiculo_id,
            "decididoPor": decidido_por,
            "decididoEm": quando,
            "atualizadoEm": quando,
        })

    def rejeitar_viagem(self, viagem_id, *, motivo, decidido_por, quando) -> None:
        v = self.get_viagem(viagem_id)
        validar_transicao(v.status, StatusViagem.REJEITADA)
        self.db.collection("viagens").document(viagem_id).update({
            "status": StatusViagem.REJEITADA.value,
            "motivoRejeicao": motivo,
            "decididoPor": decidido_por,
            "decididoEm": quando,
            "atualizadoEm": quando,
        })

    def cancelar_viagem(self, viagem_id, *, quando) -> None:
        v = self.get_viagem(viagem_id)
        validar_transicao(v.status, StatusViagem.CANCELADA)
        self.db.collection("viagens").document(viagem_id).update({
            "status": StatusViagem.CANCELADA.value,
            "atualizadoEm": quando,
        })
