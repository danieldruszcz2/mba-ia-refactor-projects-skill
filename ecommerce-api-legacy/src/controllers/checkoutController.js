const { ValidationError } = require('../utils/errors');
const { isNonEmptyString, isEmail, isCardNumber, toPositiveInteger } = require('../utils/validators');

// Os nomes de campo do body (usr, eml, pwd, c_id, card) são contrato da API.
function parseCheckoutBody(body = {}) {
    const { usr: name, eml: email, pwd: password, c_id: rawCourseId, card: cardNumber } = body;
    const courseId = toPositiveInteger(rawCourseId);

    const valid = isNonEmptyString(name)
        && isEmail(email)
        && courseId !== null
        && isCardNumber(cardNumber)
        && (password === undefined || password === null || typeof password === 'string');
    if (!valid) throw new ValidationError('Bad Request');

    return { name: name.trim(), email: email.trim(), password: password || null, courseId, cardNumber };
}

function createCheckoutController({ checkoutService }) {
    return {
        async checkout(req, res) {
            const input = parseCheckoutBody(req.body);
            const { enrollmentId } = await checkoutService.checkout(input);
            res.status(200).json({ msg: 'Sucesso', enrollment_id: enrollmentId });
        },
    };
}

module.exports = { createCheckoutController };
