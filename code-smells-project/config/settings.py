"""Configuração da aplicação. Único módulo que lê variáveis de ambiente."""
import os
import secrets

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _env_bool(name, default=False):
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in ("1", "true", "yes", "on")


def _env_list(name, default):
    value = os.environ.get(name, default)
    return [item.strip() for item in value.split(",") if item.strip()]


class Config:
    # Sem SECRET_KEY no ambiente, gera uma chave aleatória por processo (apenas para desenvolvimento).
    SECRET_KEY = os.environ.get("SECRET_KEY") or secrets.token_hex(32)
    DEBUG = _env_bool("DEBUG", False)
    HOST = os.environ.get("HOST", "127.0.0.1")
    PORT = int(os.environ.get("PORT", "5000"))
    ENVIRONMENT = os.environ.get("APP_ENV", "producao")
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")

    DATABASE_PATH = os.environ.get("DATABASE_PATH", os.path.join(BASE_DIR, "loja.db"))

    CORS_ORIGINS = _env_list("CORS_ORIGINS", "*")

    ENABLE_ADMIN_ROUTES = _env_bool("ENABLE_ADMIN_ROUTES", False)
    ADMIN_TOKEN = os.environ.get("ADMIN_TOKEN", "")
