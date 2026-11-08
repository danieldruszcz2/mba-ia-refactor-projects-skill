"""Acesso a dados de usuários. A representação pública nunca inclui a senha."""
from models.database import get_db
from utils.constants import TIPO_USUARIO_PADRAO
from utils.security import hash_password, verify_password

_COLUNAS_PUBLICAS = "id, nome, email, tipo, criado_em"


def to_public(row):
    return {
        "id": row["id"],
        "nome": row["nome"],
        "email": row["email"],
        "tipo": row["tipo"],
        "criado_em": row["criado_em"],
    }


def listar():
    rows = get_db().execute("SELECT " + _COLUNAS_PUBLICAS + " FROM usuarios").fetchall()
    return [to_public(row) for row in rows]


def buscar_por_id(usuario_id):
    row = get_db().execute(
        "SELECT " + _COLUNAS_PUBLICAS + " FROM usuarios WHERE id = ?", (usuario_id,)
    ).fetchone()
    return to_public(row) if row else None


def criar(nome, email, senha, tipo=TIPO_USUARIO_PADRAO):
    conn = get_db()
    with conn:
        cursor = conn.execute(
            "INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)",
            (nome, email, hash_password(senha), tipo),
        )
    return cursor.lastrowid


def autenticar(email, senha):
    """Retorna {id, nome, email, tipo} se as credenciais conferem; senão None.

    Senhas legadas em texto puro são aceitas uma vez e regravadas com hash.
    """
    conn = get_db()
    rows = conn.execute(
        "SELECT id, nome, email, tipo, senha FROM usuarios WHERE email = ? ORDER BY id", (email,)
    ).fetchall()
    for row in rows:
        confere, precisa_rehash = verify_password(senha, row["senha"])
        if not confere:
            continue
        if precisa_rehash:
            with conn:
                conn.execute("UPDATE usuarios SET senha = ? WHERE id = ?", (hash_password(senha), row["id"]))
        return {"id": row["id"], "nome": row["nome"], "email": row["email"], "tipo": row["tipo"]}
    return None
