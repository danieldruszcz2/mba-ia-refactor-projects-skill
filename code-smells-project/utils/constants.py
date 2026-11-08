"""Constantes de domínio."""

API_VERSION = "1.0.0"

# Produtos
CATEGORIA_PADRAO = "geral"
CATEGORIAS_VALIDAS = ["informatica", "moveis", "vestuario", "geral", "eletronicos", "livros"]
NOME_PRODUTO_MIN = 2
NOME_PRODUTO_MAX = 200

# Usuários
TIPO_USUARIO_PADRAO = "cliente"

# Pedidos
STATUS_PENDENTE = "pendente"
STATUS_APROVADO = "aprovado"
STATUS_ENVIADO = "enviado"
STATUS_ENTREGUE = "entregue"
STATUS_CANCELADO = "cancelado"
STATUS_PEDIDO_VALIDOS = [STATUS_PENDENTE, STATUS_APROVADO, STATUS_ENVIADO, STATUS_ENTREGUE, STATUS_CANCELADO]

PRODUTO_DESCONHECIDO = "Desconhecido"

# Relatório de vendas: (faturamento mínimo exclusivo, percentual de desconto), da maior faixa para a menor
FAIXAS_DESCONTO = [
    (10000, 0.10),
    (5000, 0.05),
    (1000, 0.02),
]
