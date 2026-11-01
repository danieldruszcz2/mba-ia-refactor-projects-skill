"""Emissão e verificação de tokens de autenticação assinados (itsdangerous)."""
from itsdangerous import BadSignature, URLSafeTimedSerializer

_TOKEN_SALT = 'auth-token'


class TokenService:
    def __init__(self, secret_key, max_age_seconds):
        self._serializer = URLSafeTimedSerializer(secret_key, salt=_TOKEN_SALT)
        self._max_age_seconds = max_age_seconds

    def issue(self, user_id):
        return self._serializer.dumps({'user_id': user_id})

    def verify(self, token):
        """Retorna o user_id do token, ou None se inválido/expirado."""
        if not token:
            return None
        try:
            payload = self._serializer.loads(token, max_age=self._max_age_seconds)
        except BadSignature:  # inclui SignatureExpired
            return None
        return payload.get('user_id') if isinstance(payload, dict) else None
