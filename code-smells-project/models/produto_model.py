"""Acesso a dados de produtos."""
from models.database import get_connection

_COLUNAS = "id, nome, descricao, preco, estoque, categoria, ativo, criado_em"


def _para_dict(row):
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
    rows = get_connection().execute(f"SELECT {_COLUNAS} FROM produtos").fetchall()
    return [_para_dict(row) for row in rows]


def buscar_por_id(produto_id):
    row = get_connection().execute(
        f"SELECT {_COLUNAS} FROM produtos WHERE id = ?", (produto_id,)
    ).fetchone()
    return _para_dict(row) if row else None


def criar(nome, descricao, preco, estoque, categoria):
    cursor = get_connection().execute(
        "INSERT INTO produtos (nome, descricao, preco, estoque, categoria) VALUES (?, ?, ?, ?, ?)",
        (nome, descricao, preco, estoque, categoria),
    )
    return cursor.lastrowid


def atualizar(produto_id, nome, descricao, preco, estoque, categoria):
    get_connection().execute(
        "UPDATE produtos SET nome = ?, descricao = ?, preco = ?, estoque = ?, categoria = ? WHERE id = ?",
        (nome, descricao, preco, estoque, categoria, produto_id),
    )


def deletar(produto_id):
    get_connection().execute("DELETE FROM produtos WHERE id = ?", (produto_id,))


def buscar(termo, categoria=None, preco_min=None, preco_max=None):
    condicoes = []
    parametros = []
    if termo:
        condicoes.append("(nome LIKE ? OR descricao LIKE ?)")
        padrao = f"%{termo}%"
        parametros.extend([padrao, padrao])
    if categoria:
        condicoes.append("categoria = ?")
        parametros.append(categoria)
    if preco_min:
        condicoes.append("preco >= ?")
        parametros.append(preco_min)
    if preco_max:
        condicoes.append("preco <= ?")
        parametros.append(preco_max)

    sql = f"SELECT {_COLUNAS} FROM produtos WHERE 1=1"
    for condicao in condicoes:
        sql += " AND " + condicao
    rows = get_connection().execute(sql, parametros).fetchall()
    return [_para_dict(row) for row in rows]
