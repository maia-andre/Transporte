"""Autenticação local (hash de senha) — independente de backend.

Usada enquanto o painel não está ligado ao Firebase Auth. Formato do hash:
``sal_hex$hash_hex`` (PBKDF2-HMAC-SHA256, biblioteca padrão, sem dependência nova).
"""
from __future__ import annotations

import hashlib
import hmac
import os

_ITERACOES = 260_000


class EmailJaCadastrado(Exception):
    """Levantada ao tentar criar conta com e-mail já em uso."""


def hash_senha(senha: str) -> str:
    sal = os.urandom(16)
    h = hashlib.pbkdf2_hmac("sha256", senha.encode("utf-8"), sal, _ITERACOES)
    return f"{sal.hex()}${h.hex()}"


def verificar_senha(senha: str, hash_armazenado: str) -> bool:
    try:
        sal_hex, h_hex = hash_armazenado.split("$", 1)
    except ValueError:
        return False
    sal = bytes.fromhex(sal_hex)
    h_calculado = hashlib.pbkdf2_hmac("sha256", senha.encode("utf-8"), sal, _ITERACOES)
    return hmac.compare_digest(h_calculado, bytes.fromhex(h_hex))
