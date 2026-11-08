"""Hash e verificação de senhas."""
import hmac

from werkzeug.security import check_password_hash, generate_password_hash

_HASH_PREFIXES = ("scrypt:", "pbkdf2:")


def hash_password(raw):
    return generate_password_hash(raw)


def is_hashed(stored):
    return isinstance(stored, str) and stored.startswith(_HASH_PREFIXES)


def verify_password(raw, stored):
    """Retorna (senha_confere, precisa_rehash).

    Senhas legadas gravadas em texto puro continuam aceitas e são sinalizadas para rehash.
    """
    if not stored:
        return False, False
    if is_hashed(stored):
        return check_password_hash(stored, raw), False
    return hmac.compare_digest(raw.encode("utf-8"), stored.encode("utf-8")), True
