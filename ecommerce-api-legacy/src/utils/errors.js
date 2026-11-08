class HttpError extends Error {
    constructor(status, message) {
        super(message);
        this.name = this.constructor.name;
        this.status = status;
    }
}

class ValidationError extends HttpError {
    constructor(message = 'Bad Request') { super(400, message); }
}

class PaymentDeniedError extends HttpError {
    constructor(message = 'Pagamento recusado') { super(400, message); }
}

class ForbiddenError extends HttpError {
    constructor(message = 'Acesso negado') { super(403, message); }
}

class NotFoundError extends HttpError {
    constructor(message = 'Não encontrado') { super(404, message); }
}

module.exports = { HttpError, ValidationError, PaymentDeniedError, ForbiddenError, NotFoundError };
