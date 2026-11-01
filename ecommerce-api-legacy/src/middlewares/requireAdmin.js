'use strict';

const crypto = require('crypto');
const { ForbiddenError } = require('../utils/errors');

function tokensMatch(received, expected) {
    const a = Buffer.from(received);
    const b = Buffer.from(expected);
    return a.length === b.length && crypto.timingSafeEqual(a, b);
}

// Rotas administrativas: desabilitadas por padrão (ENABLE_ADMIN_ROUTES=false → 403);
// quando habilitadas, exigem "Authorization: Bearer <ADMIN_TOKEN>".
function createRequireAdmin({ enabled, adminToken }) {
    return (req, res, next) => {
        if (!enabled || !adminToken) return next(new ForbiddenError());

        const header = req.get('authorization') || '';
        const [scheme, token] = header.split(' ');
        if (scheme !== 'Bearer' || !token || !tokensMatch(token, adminToken)) {
            return next(new ForbiddenError());
        }
        return next();
    };
}

module.exports = { createRequireAdmin };
