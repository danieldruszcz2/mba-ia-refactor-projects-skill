"""Validação de entrada: funções puras que lançam ValidationError (400)."""
from utils.constants import (
    CATEGORIA_PADRAO,
    CATEGORIAS_VALIDAS,
    NOME_PRODUTO_MAX,
    NOME_PRODUTO_MIN,
    STATUS_PEDIDO_VALIDOS,
)
from utils.errors import ValidationError


def _is_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _to_int(value):
    """Aceita int ou string de dígitos; devolve None se inválido."""
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.strip().isdigit():
        return int(value.strip())
    return None


def objeto_json(dados):
    if not dados or not isinstance(dados, dict):
        raise ValidationError("Dados inválidos")
    return dados


def validar_produto(dados, completo=True):
    """Valida o body de criação (completo=True) ou de atualização de produto.

    A atualização mantém as regras originais do contrato (sem checar tamanho do nome nem categoria).
    """
    dados = objeto_json(dados)
    for campo, mensagem in (("nome", "Nome é obrigatório"),
                            ("preco", "Preço é obrigatório"),
                            ("estoque", "Estoque é obrigatório")):
        if campo not in dados:
            raise ValidationError(mensagem)

    nome = dados["nome"]
    descricao = dados.get("descricao", "")
    preco = dados["preco"]
    estoque = dados["estoque"]
    categoria = dados.get("categoria", CATEGORIA_PADRAO)

    if not isinstance(nome, str):
        raise ValidationError("Nome deve ser texto")
    if not isinstance(descricao, str):
        raise ValidationError("Descrição deve ser texto")
    if not isinstance(categoria, str):
        raise ValidationError("Categoria deve ser texto")
    if not _is_number(preco):
        raise ValidationError("Preço deve ser numérico")
    if not _is_number(estoque):
        raise ValidationError("Estoque deve ser numérico")

    if preco < 0:
        raise ValidationError("Preço não pode ser negativo")
    if estoque < 0:
        raise ValidationError("Estoque não pode ser negativo")

    if completo:
        if len(nome) < NOME_PRODUTO_MIN:
            raise ValidationError("Nome muito curto")
        if len(nome) > NOME_PRODUTO_MAX:
            raise ValidationError("Nome muito longo")
        if categoria not in CATEGORIAS_VALIDAS:
            raise ValidationError("Categoria inválida. Válidas: " + str(CATEGORIAS_VALIDAS))

    return {"nome": nome, "descricao": descricao, "preco": preco, "estoque": estoque, "categoria": categoria}


def numero_opcional(valor, nome_parametro):
    if valor is None or valor == "":
        return None
    try:
        return float(valor)
    except (TypeError, ValueError):
        raise ValidationError(nome_parametro + " deve ser numérico")


def validar_usuario(dados):
    dados = objeto_json(dados)
    nome = dados.get("nome", "")
    email = dados.get("email", "")
    senha = dados.get("senha", "")
    if not nome or not email or not senha:
        raise ValidationError("Nome, email e senha são obrigatórios")
    if not all(isinstance(valor, str) for valor in (nome, email, senha)):
        raise ValidationError("Nome, email e senha devem ser texto")
    return {"nome": nome, "email": email, "senha": senha}


def validar_login(dados):
    dados = dados if isinstance(dados, dict) else {}
    email = dados.get("email", "")
    senha = dados.get("senha", "")
    if not email or not senha:
        raise ValidationError("Email e senha são obrigatórios")
    if not isinstance(email, str) or not isinstance(senha, str):
        raise ValidationError("Email e senha devem ser texto")
    return email, senha


def validar_pedido(dados):
    dados = objeto_json(dados)
    usuario_id = dados.get("usuario_id")
    itens = dados.get("itens", [])

    if not usuario_id:
        raise ValidationError("Usuario ID é obrigatório")
    usuario_id_int = _to_int(usuario_id)
    if usuario_id_int is None:
        raise ValidationError("Usuario ID inválido")
    if not itens:
        raise ValidationError("Pedido deve ter pelo menos 1 item")
    if not isinstance(itens, list):
        raise ValidationError("Itens devem ser uma lista")

    itens_validos = []
    for item in itens:
        if not isinstance(item, dict):
            raise ValidationError("Item de pedido inválido")
        produto_id = _to_int(item.get("produto_id"))
        if produto_id is None:
            raise ValidationError("produto_id é obrigatório em cada item")
        quantidade = item.get("quantidade")
        if isinstance(quantidade, bool) or not isinstance(quantidade, int) or quantidade <= 0:
            raise ValidationError("Quantidade deve ser um inteiro positivo")
        itens_validos.append({"produto_id": produto_id, "quantidade": quantidade})

    return usuario_id_int, itens_validos


def validar_status_pedido(dados):
    dados = dados if isinstance(dados, dict) else {}
    novo_status = dados.get("status", "")
    if novo_status not in STATUS_PEDIDO_VALIDOS:
        raise ValidationError("Status inválido")
    return novo_status
