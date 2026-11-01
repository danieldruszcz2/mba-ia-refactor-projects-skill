"""Consultas de sistema: health check e operações administrativas."""
import sqlite3

from models.database import get_connection, transaction
from utils.errors import ValidationError


def contar_registros():
    conn = get_connection()
    conn.execute("SELECT 1")
    row = conn.execute(
        """
        SELECT (SELECT COUNT(*) FROM produtos) AS produtos,
               (SELECT COUNT(*) FROM usuarios) AS usuarios,
               (SELECT COUNT(*) FROM pedidos) AS pedidos
        """
    ).fetchone()
    return dict(row)


def resetar_banco():
    conn = get_connection()
    with transaction(conn):
        for tabela in ("itens_pedido", "pedidos", "produtos", "usuarios"):
            conn.execute(f"DELETE FROM {tabela}")


def executar_consulta_leitura(sql):
    """Executa uma única consulta em modo somente leitura (PRAGMA query_only)."""
    conn = get_connection()
    conn.execute("PRAGMA query_only = ON")
    try:
        rows = conn.execute(sql).fetchall()
    except sqlite3.Error:
        raise ValidationError("Query inválida ou não permitida") from None
    finally:
        conn.execute("PRAGMA query_only = OFF")
    return [dict(row) for row in rows]
