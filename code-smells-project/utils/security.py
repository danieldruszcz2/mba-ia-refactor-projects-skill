"""Hash e verificação de senhas (scrypt com salt, via Werkzeug)."""
import re

from werkzeug.security import check_password_hash, generate_password_hash

_FORMATO_HASH = re.compile(r"^(scrypt|pbkdf2)(:[^$]*)?\$[^$]+\$[0-9a-f]+$")


def hash_senha(senha):
    return generate_password_hash(senha)


def verificar_senha(senha, senha_hash):
    if not senha_hash or not e_hash_de_senha(senha_hash):
        return False
    return check_password_hash(senha_hash, senha)


def e_hash_de_senha(valor):
    return bool(valor) and bool(_FORMATO_HASH.match(valor))
