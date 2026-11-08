"""Consultas de sistema: health check, reset e consulta administrativa somente leitura."""
from models.database import get_db, get_read_only_db

_TABELAS_RESET = ["itens_pedido", "pedidos", "produtos", "usuarios"]


def contagens():
    row = get_db().execute(
        "SELECT (SELECT COUNT(*) FROM produtos) AS produtos, "
        "(SELECT COUNT(*) FROM usuarios) AS usuarios, "
        "(SELECT COUNT(*) FROM pedidos) AS pedidos"
    ).fetchone()
    return dict(row)


def resetar():
    conn = get_db()
    with conn:
        for tabela in _TABELAS_RESET:
            conn.execute("DELETE FROM " + tabela)  # nomes fixos da lista acima, sem entrada externa


def consultar_somente_leitura(sql):
    """Executa uma única instrução numa conexão aberta em modo read-only."""
    conn = get_read_only_db()
    try:
        rows = conn.execute(sql).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()
