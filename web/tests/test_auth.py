"""Testes de autenticação: hash de senha e login/cadastro no MockRepository."""
from datetime import datetime

import pytest

from domain import EmailJaCadastrado, Role, StatusViagem, Viagem, hash_senha, verificar_senha
from domain.rules import CANCELAVEIS_PELO_SOLICITANTE
from services.mock_data import build_seed
from services.mock_repository import MockRepository


# --------------------------------- hash de senha ---------------------------- #
def test_hash_senha_gera_valores_diferentes_por_causa_do_sal():
    assert hash_senha("segredo123") != hash_senha("segredo123")


def test_verificar_senha_correta():
    h = hash_senha("segredo123")
    assert verificar_senha("segredo123", h)


def test_verificar_senha_incorreta():
    h = hash_senha("segredo123")
    assert not verificar_senha("outra-senha", h)


def test_verificar_senha_hash_invalido_nao_levanta():
    assert not verificar_senha("qualquer", "hash-mal-formado")


# --------------------------------- repositório ------------------------------ #
@pytest.fixture
def repo():
    return MockRepository(build_seed())


def test_criar_usuario_vira_solicitante_por_padrao(repo):
    uid = repo.criar_usuario(nome="Novo", email="Novo.Usuario@sjc.sp.gov.br",
                             senha="senha123", secretaria_id=5)
    criado = next(u for u in repo.list_usuarios() if u.uid == uid)
    assert criado.role == Role.SOLICITANTE
    assert criado.email == "novo.usuario@sjc.sp.gov.br"  # normalizado


def test_criar_usuario_email_duplicado_falha(repo):
    with pytest.raises(EmailJaCadastrado):
        repo.criar_usuario(nome="Dup", email="ana.controle@sjc.sp.gov.br",
                           senha="senha123", secretaria_id=5)


def test_autenticar_credenciais_corretas(repo):
    repo.criar_usuario(nome="Novo", email="novo@sjc.sp.gov.br",
                       senha="senha123", secretaria_id=5)
    usuario = repo.autenticar("novo@sjc.sp.gov.br", "senha123")
    assert usuario is not None
    assert usuario.email == "novo@sjc.sp.gov.br"


def test_autenticar_senha_errada_retorna_none(repo):
    repo.criar_usuario(nome="Novo", email="novo@sjc.sp.gov.br",
                       senha="senha123", secretaria_id=5)
    assert repo.autenticar("novo@sjc.sp.gov.br", "senha-errada") is None


def test_autenticar_email_inexistente_retorna_none(repo):
    assert repo.autenticar("ninguem@sjc.sp.gov.br", "qualquer") is None


def test_cancelar_viagem_pendente(repo):
    pend = next(v for v in repo.list_viagens() if v.status == StatusViagem.PENDENTE)
    repo.cancelar_viagem(pend.id, quando=datetime.now())
    assert repo.get_viagem(pend.id).status == StatusViagem.CANCELADA


def test_cancelar_viagem_concluida_falha(repo):
    from domain.rules import TransicaoInvalida

    concluida = next(v for v in repo.list_viagens() if v.status == StatusViagem.CONCLUIDA)
    with pytest.raises(TransicaoInvalida):
        repo.cancelar_viagem(concluida.id, quando=datetime.now())


def test_cancelaveis_pelo_solicitante_sao_pendente_e_aceita():
    assert CANCELAVEIS_PELO_SOLICITANTE == {StatusViagem.PENDENTE, StatusViagem.ACEITA}
