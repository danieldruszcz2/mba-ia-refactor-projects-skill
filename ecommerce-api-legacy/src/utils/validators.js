'use strict';

const { ValidationError } = require('./errors');

const isNonEmptyString = (value) => typeof value === 'string' && value.trim() !== '';

// Valida o body de POST /api/checkout. Os nomes de campo (usr, eml, pwd, c_id, card) são contrato da API.
function parseCheckoutInput(body) {
    if (!body || typeof body !== 'object') throw new ValidationError();

    const { usr, eml, pwd, c_id: courseId, card } = body;

    // Mesma regra de presença do código original (valores "falsy" são rejeitados).
    if (!usr || !eml || !courseId || !card) throw new ValidationError();

    if (!isNonEmptyString(usr) || !isNonEmptyString(eml) || !isNonEmptyString(card)) {
        throw new ValidationError();
    }
    if (pwd !== undefined && pwd !== null && typeof pwd !== 'string') throw new ValidationError();
    if (typeof courseId !== 'number' && typeof courseId !== 'string') throw new ValidationError();

    return {
        userName: usr,
        email: eml,
        password: pwd || null,
        courseId,
        cardNumber: card,
    };
}

module.exports = { parseCheckoutInput };
