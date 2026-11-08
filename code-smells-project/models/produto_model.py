"""Acesso a dados de produtos."""
from models.database import get_db

_COLUNAS = "id, nome, descricao, preco, estoque, categoria, ativo, criado_em"


def to_dict(row):
    return {
        "id": row["id"],
        "nome": row["nome"],
        "descricao": row["descricao"],
        "preco": row["preco"],
        "estoque": row["estoque"],
        "categoria": row["categoria"],
        "ativo": row["ativo"],
        "criado_em": row["criado_em"],
    }


def listar():
    rows = get_db().execute("SELECT " + _COLUNAS + " FROM produtos").fetchall()
    return [to_dict(row) for row in rows]


def buscar_por_id(produto_id):
    row = get_db().execute("SELECT " + _COLUNAS + " FROM produtos WHERE id = ?", (produto_id,)).fetchone()
    return to_dict(row) if row else None


def buscar(termo=None, categoria=None, preco_min=None, preco_max=None):
    condicoes, parametros = [], []
    if termo:
        condicoes.append("(nome LIKE ? OR descricao LIKE ?)")
        padrao = "%" + termo + "%"
        parametros += [padrao, padrao]
    if categoria:
        condicoes.append("categoria = ?")
        parametros.append(categoria)
    if preco_min is not None:
        condicoes.append("preco >= ?")
        parametros.append(preco_min)
    if preco_max is not None:
        condicoes.append("preco <= ?")
        parametros.append(preco_max)

    sql = "SELECT " + _COLUNAS + " FROM produtos"
    if condicoes:
        sql += " WHERE " + " AND ".join(condicoes)
    rows = get_db().execute(sql, parametros).fetchall()
    return [to_dict(row) for row in rows]


def criar(nome, descricao, preco, estoque, categoria):
    conn = get_db()
    with conn:
        cursor = conn.execute(
            "INSERT INTO produtos (nome, descricao, preco, estoque, categoria) VALUES (?, ?, ?, ?, ?)",
            (nome, descricao, preco, estoque, categoria),
        )
    return cursor.lastrowid


def atualizar(produto_id, nome, descricao, preco, estoque, categoria):
    conn = get_db()
    with conn:
        conn.execute(
            "UPDATE produtos SET nome = ?, descricao = ?, preco = ?, estoque = ?, categoria = ? WHERE id = ?",
            (nome, descricao, preco, estoque, categoria, produto_id),
        )


def deletar(produto_id):
    conn = get_db()
    with conn:
        conn.execute("DELETE FROM produtos WHERE id = ?", (produto_id,))
