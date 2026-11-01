'use strict';

const { AppError } = require('../utils/errors');

// Error handler central: respostas em texto puro, como no contrato original.
// Erros inesperados são logados com stack no servidor e nunca expostos ao cliente.
function createErrorHandler({ logger }) {
    // eslint-disable-next-line no-unused-vars
    return (err, req, res, next) => {
        if (res.headersSent) return next(err);

        if (err instanceof AppError) {
            return res.status(err.status).send(err.message);
        }
        if (err.type === 'entity.parse.failed') {
            return res.status(400).send('Bad Request');
        }

        logger.error(`${req.method} ${req.originalUrl} falhou`, err);
        return res.status(500).send('Erro interno');
    };
}

module.exports = { createErrorHandler };
