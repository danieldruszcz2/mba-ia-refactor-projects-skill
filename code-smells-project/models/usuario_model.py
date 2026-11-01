"""Acesso a dados de usuários. A representação pública nunca inclui a senha."""
from models.database import get_connection
from utils.constants import TIPO_USUARIO_CLIENTE

_COLUNAS_PUBLICAS = "id, nome, email, tipo, criado_em"


def _para_dict(row):
    return {
        "id": row["id"],
        "nome": row["nome"],
        "email": row["email"],
        "tipo": row["tipo"],
        "criado_em": row["criado_em"],
    }


def listar():
    rows = get_connection().execute(f"SELECT {_COLUNAS_PUBLICAS} FROM usuarios").fetchall()
    return [_para_dict(row) for row in rows]


def buscar_por_id(usuario_id):
    row = get_connection().execute(
        f"SELECT {_COLUNAS_PUBLICAS} FROM usuarios WHERE id = ?", (usuario_id,)
    ).fetchone()
    return _para_dict(row) if row else None


def buscar_credenciais_por_email(email):
    """Uso interno (autenticação): devolve id, nome, email, tipo e o hash da senha."""
    return get_connection().execute(
        "SELECT id, nome, email, tipo, senha FROM usuarios WHERE email = ? ORDER BY id", (email,)
    ).fetchall()


def criar(nome, email, senha_hash, tipo=TIPO_USUARIO_CLIENTE):
    cursor = get_connection().execute(
        "INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)",
        (nome, email, senha_hash, tipo),
    )
    return cursor.lastrowid
