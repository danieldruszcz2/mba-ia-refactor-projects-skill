"""Validadores puros de entrada. Lançam ValidationError (→ 400) com mensagem clara."""
from utils.constants import (
    CATEGORIA_PADRAO,
    CATEGORIAS_VALIDAS,
    NOME_PRODUTO_MAX,
    NOME_PRODUTO_MIN,
    STATUS_PEDIDO_VALIDOS,
)
from utils.errors import ValidationError


def _e_numero(valor):
    return isinstance(valor, (int, float)) and not isinstance(valor, bool)


def _e_inteiro(valor):
    return _e_numero(valor) and float(valor).is_integer()


def _para_inteiro(valor):
    """Converte int ou string numérica em int; devolve None se inválido."""
    if isinstance(valor, bool):
        return None
    if _e_inteiro(valor):
        return int(valor)
    if isinstance(valor, str) and valor.strip().lstrip("-").isdigit():
        return int(valor.strip())
    return None


def exigir_objeto(dados, mensagem="Dados inválidos"):
    if not dados or not isinstance(dados, dict):
        raise ValidationError(mensagem)
    return dados


def validar_produto(dados):
    """Validação única para criação e atualização de produto. Devolve os campos normalizados."""
    exigir_objeto(dados)
    if "nome" not in dados:
        raise ValidationError("Nome é obrigatório")
    if "preco" not in dados:
        raise ValidationError("Preço é obrigatório")
    if "estoque" not in dados:
        raise ValidationError("Estoque é obrigatório")

    nome = dados["nome"]
    descricao = dados.get("descricao", "")
    preco = dados["preco"]
    estoque = dados["estoque"]
    categoria = dados.get("categoria", CATEGORIA_PADRAO)

    if not isinstance(nome, str):
        raise ValidationError("Nome deve ser texto")
    if descricao is None:
        descricao = ""
    if not isinstance(descricao, str):
        raise ValidationError("Descrição deve ser texto")
    if not _e_numero(preco):
        raise ValidationError("Preço deve ser numérico")
    if not _e_inteiro(estoque):
        raise ValidationError("Estoque deve ser um número inteiro")

    if preco < 0:
        raise ValidationError("Preço não pode ser negativo")
    if estoque < 0:
        raise ValidationError("Estoque não pode ser negativo")
    if len(nome) < NOME_PRODUTO_MIN:
        raise ValidationError("Nome muito curto")
    if len(nome) > NOME_PRODUTO_MAX:
        raise ValidationError("Nome muito longo")
    if categoria not in CATEGORIAS_VALIDAS:
        raise ValidationError("Categoria inválida. Válidas: " + str(CATEGORIAS_VALIDAS))

    return {
        "nome": nome,
        "descricao": descricao,
        "preco": preco,
        "estoque": int(estoque),
        "categoria": categoria,
    }


def validar_filtro_preco(valor, nome_parametro):
    if valor is None or valor == "":
        return None
    try:
        return float(valor)
    except ValueError:
        raise ValidationError(nome_parametro + " deve ser numérico") from None


def validar_usuario(dados):
    exigir_objeto(dados)
    nome = dados.get("nome", "")
    email = dados.get("email", "")
    senha = dados.get("senha", "")
    if not nome or not email or not senha:
        raise ValidationError("Nome, email e senha são obrigatórios")
    if not all(isinstance(campo, str) for campo in (nome, email, senha)):
        raise ValidationError("Nome, email e senha devem ser texto")
    return {"nome": nome, "email": email, "senha": senha}


def validar_login(dados):
    dados = dados if isinstance(dados, dict) else {}
    email = dados.get("email", "")
    senha = dados.get("senha", "")
    if not email or not senha or not isinstance(email, str) or not isinstance(senha, str):
        raise ValidationError("Email e senha são obrigatórios")
    return email, senha


def validar_pedido(dados):
    exigir_objeto(dados)
    usuario_id = dados.get("usuario_id")
    itens = dados.get("itens", [])

    if not usuario_id:
        raise ValidationError("Usuario ID é obrigatório")
    usuario_id_int = _para_inteiro(usuario_id)
    if usuario_id_int is None:
        raise ValidationError("Usuario ID inválido")
    if not itens:
        raise ValidationError("Pedido deve ter pelo menos 1 item")
    if not isinstance(itens, list):
        raise ValidationError("Itens devem ser uma lista")

    itens_normalizados = []
    for item in itens:
        produto_id = _para_inteiro(item.get("produto_id")) if isinstance(item, dict) else None
        quantidade = _para_inteiro(item.get("quantidade")) if isinstance(item, dict) else None
        if produto_id is None or quantidade is None or quantidade <= 0:
            raise ValidationError(
                "Item inválido: produto_id e quantidade (inteiro positivo) são obrigatórios"
            )
        itens_normalizados.append({"produto_id": produto_id, "quantidade": quantidade})

    return usuario_id_int, itens_normalizados


def validar_status_pedido(dados):
    dados = dados if isinstance(dados, dict) else {}
    novo_status = dados.get("status", "")
    if novo_status not in STATUS_PEDIDO_VALIDOS:
        raise ValidationError("Status inválido")
    return novo_status
