"""Acesso a dados de pedidos e itens de pedido."""
from models.database import get_connection, transaction
from utils.constants import STATUS_APROVADO, STATUS_CANCELADO, STATUS_PENDENTE
from utils.errors import ValidationError


def criar(usuario_id, itens):
    """Cria o pedido, seus itens e baixa o estoque numa única transação."""
    conn = get_connection()
    produto_ids = sorted({item["produto_id"] for item in itens})
    placeholders = ", ".join("?" for _ in produto_ids)

    with transaction(conn):
        produtos = {
            row["id"]: row
            for row in conn.execute(
                f"SELECT id, nome, preco, estoque FROM produtos WHERE id IN ({placeholders})",
                produto_ids,
            )
        }

        total = 0
        for item in itens:
            produto = produtos.get(item["produto_id"])
            if produto is None:
                raise ValidationError(
                    "Produto " + str(item["produto_id"]) + " não encontrado", {"sucesso": False}
                )
            if produto["estoque"] < item["quantidade"]:
                raise ValidationError("Estoque insuficiente para " + produto["nome"], {"sucesso": False})
            total = total + (produto["preco"] * item["quantidade"])

        pedido_id = conn.execute(
            "INSERT INTO pedidos (usuario_id, status, total) VALUES (?, ?, ?)",
            (usuario_id, STATUS_PENDENTE, total),
        ).lastrowid

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
    """Pedidos com seus itens em uma única consulta (LEFT JOIN), na ordem de inserção."""
    sql = """
        SELECT p.id, p.usuario_id, p.status, p.total, p.criado_em,
               i.id AS item_id, i.produto_id, i.quantidade, i.preco_unitario,
               pr.nome AS produto_nome
        FROM pedidos p
        LEFT JOIN itens_pedido i ON i.pedido_id = p.id
        LEFT JOIN produtos pr ON pr.id = i.produto_id
    """
    parametros = []
    if usuario_id is not None:
        sql += " WHERE p.usuario_id = ?"
        parametros.append(usuario_id)
    sql += " ORDER BY p.id, i.id"

    pedidos = {}
    for row in get_connection().execute(sql, parametros):
        pedido = pedidos.get(row["id"])
        if pedido is None:
            pedido = {
                "id": row["id"],
                "usuario_id": row["usuario_id"],
                "status": row["status"],
                "total": row["total"],
                "criado_em": row["criado_em"],
                "itens": [],
            }
            pedidos[row["id"]] = pedido
        if row["item_id"] is not None:
            pedido["itens"].append({
                "produto_id": row["produto_id"],
                "produto_nome": row["produto_nome"] if row["produto_nome"] is not None else "Desconhecido",
                "quantidade": row["quantidade"],
                "preco_unitario": row["preco_unitario"],
            })
    return list(pedidos.values())


def atualizar_status(pedido_id, novo_status):
    get_connection().execute("UPDATE pedidos SET status = ? WHERE id = ?", (novo_status, pedido_id))


def totais_de_vendas():
    """Agregados de vendas numa única consulta."""
    row = get_connection().execute(
        """
        SELECT COUNT(*) AS total_pedidos,
               COALESCE(SUM(total), 0) AS faturamento,
               COALESCE(SUM(CASE WHEN status = ? THEN 1 ELSE 0 END), 0) AS pendentes,
               COALESCE(SUM(CASE WHEN status = ? THEN 1 ELSE 0 END), 0) AS aprovados,
               COALESCE(SUM(CASE WHEN status = ? THEN 1 ELSE 0 END), 0) AS cancelados
        FROM pedidos
        """,
        (STATUS_PENDENTE, STATUS_APROVADO, STATUS_CANCELADO),
    ).fetchone()
    return dict(row)
