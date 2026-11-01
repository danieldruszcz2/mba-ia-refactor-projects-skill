"""Erros de domínio convertidos em respostas HTTP pelo error handler central."""


class AppError(Exception):
    status_code = 500

    def __init__(self, mensagem, extra=None):
        super().__init__(mensagem)
        self.mensagem = mensagem
        self.extra = extra or {}


class ValidationError(AppError):
    status_code = 400


class UnauthorizedError(AppError):
    status_code = 401


class ForbiddenError(AppError):
    status_code = 403


class NotFoundError(AppError):
    status_code = 404
