"""Configuração da aplicação — único módulo que lê variáveis de ambiente.

Os defaults são seguros e servem apenas para desenvolvimento local.
Veja `.env.example` para a lista de variáveis.
"""
import os
import secrets

from dotenv import load_dotenv

load_dotenv()


def _env_bool(name, default=False):
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in ('1', 'true', 'yes', 'on')


def _env_list(name):
    value = os.environ.get(name, '')
    return [item.strip() for item in value.split(',') if item.strip()]


class Config:
    # Sem SECRET_KEY no ambiente, gera uma chave efêmera (tokens expiram a cada restart).
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(32)

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///tasks.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    DEBUG = _env_bool('DEBUG', False)
    HOST = os.environ.get('HOST', '127.0.0.1')
    PORT = int(os.environ.get('PORT', '5000'))

    # Origens permitidas; lista vazia = CORS desabilitado (nenhuma origem externa).
    CORS_ORIGINS = _env_list('CORS_ORIGINS')

    # Operações administrativas (DELETE /users/<id>, atribuir/alterar roles privilegiados)
    # respondem 403 a menos que esta flag seja ligada; ligada, exigem token de um admin.
    ENABLE_ADMIN_ROUTES = _env_bool('ENABLE_ADMIN_ROUTES', False)
    TOKEN_MAX_AGE_SECONDS = int(os.environ.get('TOKEN_MAX_AGE_SECONDS', '3600'))

    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO').upper()
