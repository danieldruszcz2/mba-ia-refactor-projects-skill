"""Hash de senha e tokens de autenticação."""
import hashlib
import hmac
import re

from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from werkzeug.security import check_password_hash, generate_password_hash

_LEGACY_MD5 = re.compile(r'^[0-9a-f]{32}$')
_TOKEN_SALT = 'auth-token'


def hash_password(password):
    return generate_password_hash(password)


def verify_password(stored_hash, password):
    """Retorna (válida, precisa_rehash).

    Hashes MD5 legados (gravados pela versão antiga) ainda são aceitos, comparados
    em tempo constante, e sinalizados para rehash com o algoritmo atual.
    """
    if not stored_hash:
        return False, False
    if _LEGACY_MD5.match(stored_hash):
        legacy = hashlib.md5(password.encode()).hexdigest()
        ok = hmac.compare_digest(legacy, stored_hash)
        return ok, ok
    return check_password_hash(stored_hash, password), False


def generate_token(secret_key, user_id):
    return URLSafeTimedSerializer(secret_key, salt=_TOKEN_SALT).dumps({'uid': user_id})


def read_token(secret_key, token, max_age):
    """Retorna o id do usuário do token, ou None se inválido/expirado."""
    try:
        data = URLSafeTimedSerializer(secret_key, salt=_TOKEN_SALT).loads(token, max_age=max_age)
    except (BadSignature, SignatureExpired):
        return None
    return data.get('uid') if isinstance(data, dict) else None
