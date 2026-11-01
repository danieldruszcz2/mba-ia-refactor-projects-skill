"""Configuração da aplicação — único módulo que lê variáveis de ambiente.

Os defaults são seguros e servem apenas para desenvolvimento local.
Veja `.env.example` para a lista de variáveis.
"""
import os
import secrets
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _env_bool(nome, padrao=False):
    valor = os.environ.get(nome)
    if valor is None:
        return padrao
    return valor.strip().lower() in ("1", "true", "yes", "on")


def _env_list(nome):
    valor = os.environ.get(nome, "")
    return [item.strip() for item in valor.split(",") if item.strip()]


def _resolver_caminho_banco(caminho):
    path = Path(caminho)
    return str(path if path.is_absolute() else PROJECT_ROOT / path)


def load_config():
    """Monta o dicionário de configuração a partir do ambiente."""
    return {
        # Sem SECRET_KEY definida, gera uma chave aleatória por processo (apenas dev).
        "SECRET_KEY": os.environ.get("SECRET_KEY") or secrets.token_hex(32),
        "DEBUG": _env_bool("DEBUG", False),
        "HOST": os.environ.get("HOST", "127.0.0.1"),
        "PORT": int(os.environ.get("PORT", "5000")),
        "DATABASE_PATH": _resolver_caminho_banco(os.environ.get("DATABASE_PATH", "loja.db")),
        "CORS_ORIGINS": _env_list("CORS_ORIGINS"),
        "ENABLE_ADMIN_ROUTES": _env_bool("ENABLE_ADMIN_ROUTES", False),
        "ADMIN_TOKEN": os.environ.get("ADMIN_TOKEN", ""),
        "LOG_LEVEL": os.environ.get("LOG_LEVEL", "INFO").upper(),
    }
