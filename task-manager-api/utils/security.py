"""Hash de senha (scrypt via Werkzeug) com suporte de migração a hashes MD5 legados."""
import hashlib
import hmac
import re

from werkzeug.security import check_password_hash, generate_password_hash

_LEGACY_MD5_HASH = re.compile(r'^[0-9a-f]{32}$')


def hash_password(raw_password):
    return generate_password_hash(raw_password)


def is_legacy_hash(stored_hash):
    return bool(stored_hash) and bool(_LEGACY_MD5_HASH.match(stored_hash))


def verify_password(raw_password, stored_hash):
    if not stored_hash or not isinstance(raw_password, str):
        return False
    if is_legacy_hash(stored_hash):
        # Somente para migração: o hash é regravado com scrypt no próximo login bem-sucedido.
        legacy_digest = hashlib.md5(raw_password.encode()).hexdigest()
        return hmac.compare_digest(stored_hash, legacy_digest)
    return check_password_hash(stored_hash, raw_password)
