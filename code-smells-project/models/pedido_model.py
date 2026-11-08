"""Acesso a dados de pedidos e itens."""
from models.database import get_db
from utils.constants import (
    PRODUTO_DESCONHECIDO,
    STATUS_APROVADO,
    STATUS_CANCELADO,
    STATUS_PENDENTE,
)
from utils.errors import ValidationError


def criar(usuario_id, itens):
    """Cria o pedido, os itens e baixa o estoque numa única transação.

    Lança ValidationError (e faz rollback) se um produto não existe ou falta estoque.
    """
    conn = get_db()
    with conn:
        produtos = {}
        total = 0
        for item in itens:
            produto_id = item["produto_id"]
            produto = conn.execute(
                "SELECT id, nome, preco, estoque FROM produtos WHERE id = ?", (produto_id,)
            ).fetchone()
            if produto is None:
                raise ValidationError("Produto " + str(produto_id) + " não encontrado", {"sucesso": False})
            if produto["estoque"] < item["quantidade"]:
                raise ValidationError("Estoque insuficiente para " + produto["nome"], {"sucesso": False})
            produtos[produto_id] = produto
            total = total + (produto["preco"] * item["quantidade"])

        cursor = conn.execute(
            "INSERT INTO pedidos (usuario_id, status, total) VALUES (?, ?, ?)",
            (usuario_id, STATUS_PENDENTE, total),
        )
        pedido_id = cursor.lastrowid

        for item in itens:
            produto = produtos[item["produto_id"]]
            conn.execute(
                "INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, preco_unitario) VALUES (?, ?, ?, ?)",
                (pedido_id, item["produto_id"], item["quantidade"], produto["preco"]),
            )
            baixa = conn.execute(
                "UPDATE produtos SET estoque = estoque - ? WHERE id = ? AND estoque >= ?",
                (item["quantidade"], item["produto_id"], item["quantidade"]),
            )
            if baixa.rowcount == 0:
                raise ValidationError("Estoque insuficiente para " + produto["nome"], {"sucesso": False})

    return {"pedido_id": pedido_id, "total": total}


def listar(usuario_id=None):
    """Lista pedidos (todos ou de um usuário) com itens, em 2 consultas."""
    conn = get_db()
    if usuario_id is None:
        pedidos_rows = conn.execute(
            "SELECT id, usuario_id, status, total, criado_em FROM pedidos ORDER BY id"
        ).fetchall()
    else:
        pedidos_rows = conn.execute(
            "SELECT id, usuario_id, status, total, criado_em FROM pedidos WHERE usuario_id = ? ORDER BY id",
            (usuario_id,),
        ).fetchall()

    pedidos = []
    por_id = {}
    for row in pedidos_rows:
        pedido = {
            "id": row["id"],
            "usuario_id": row["usuario_id"],
            "status": row["status"],
            "total": row["total"],
            "criado_em": row["criado_em"],
            "itens": [],
        }
        pedidos.append(pedido)
        por_id[row["id"]] = pedido

    if not por_id:
        return pedidos

    placeholders = ",".join("?" for _ in por_id)
    itens_rows = conn.execute(
        "SELECT ip.pedido_id, ip.produto_id, ip.quantidade, ip.preco_unitario, p.nome AS produto_nome "
        "FROM itens_pedido ip LEFT JOIN produtos p ON p.id = ip.produto_id "
        "WHERE ip.pedido_id IN (" + placeholders + ") ORDER BY ip.id",
        list(por_id.keys()),
    ).fetchall()
    for item in itens_rows:
        por_id[item["pedido_id"]]["itens"].append({
            "produto_id": item["produto_id"],
            "produto_nome": item["produto_nome"] if item["produto_nome"] is not None else PRODUTO_DESCONHECIDO,
            "quantidade": item["quantidade"],
            "preco_unitario": item["preco_unitario"],
        })
    return pedidos


def atualizar_status(pedido_id, novo_status):
    conn = get_db()
    with conn:
        conn.execute("UPDATE pedidos SET status = ? WHERE id = ?", (novo_status, pedido_id))


def totais_vendas():
    row = get_db().execute(
        "SELECT COUNT(*) AS total_pedidos, "
        "COALESCE(SUM(total), 0) AS faturamento, "
        "COALESCE(SUM(CASE WHEN status = ? THEN 1 ELSE 0 END), 0) AS pendentes, "
        "COALESCE(SUM(CASE WHEN status = ? THEN 1 ELSE 0 END), 0) AS aprovados, "
        "COALESCE(SUM(CASE WHEN status = ? THEN 1 ELSE 0 END), 0) AS cancelados "
        "FROM pedidos",
        (STATUS_PENDENTE, STATUS_APROVADO, STATUS_CANCELADO),
    ).fetchone()
    return dict(row)
