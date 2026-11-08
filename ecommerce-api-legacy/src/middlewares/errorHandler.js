const { HttpError } = require('../utils/errors');

// Formato único de erro: texto puro, como a API original respondia.
// Nunca devolve mensagem/stack de erros internos ao cliente.
function createErrorHandler({ logger }) {
    // eslint-disable-next-line no-unused-vars
    return (err, req, res, next) => {
        if (err instanceof HttpError) {
            return res.status(err.status).send(err.message);
        }
        if (err && err.type === 'entity.parse.failed') {
            return res.status(400).send('Bad Request');
        }
        logger.error(`Erro não tratado em ${req.method} ${req.path}`, { error: err && err.message });
        return res.status(500).send('Erro interno');
    };
}

module.exports = { createErrorHandler };
