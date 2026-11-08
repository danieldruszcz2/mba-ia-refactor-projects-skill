const crypto = require('crypto');
const { ForbiddenError } = require('../utils/errors');

// Rotas administrativas: desligadas por padrão (ENABLE_ADMIN_ROUTES) e, quando
// ligadas, exigem o header X-Admin-Token igual a ADMIN_TOKEN (comparação em tempo constante).
function createRequireAdmin({ enableAdminRoutes, adminToken }) {
    const expected = Buffer.from(adminToken || '');
    return (req, res, next) => {
        if (!enableAdminRoutes) return next(new ForbiddenError('Rotas administrativas desabilitadas'));
        const received = Buffer.from(req.get('x-admin-token') || '');
        const authorized = expected.length > 0
            && received.length === expected.length
            && crypto.timingSafeEqual(received, expected);
        return authorized ? next() : next(new ForbiddenError('Acesso negado'));
    };
}

module.exports = { createRequireAdmin };
