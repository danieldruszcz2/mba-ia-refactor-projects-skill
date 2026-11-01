'use strict';

const { parseCheckoutInput } = require('../utils/validators');

function createCheckoutController({ checkoutService }) {
    return {
        async checkout(req, res) {
            const input = parseCheckoutInput(req.body);
            const { enrollmentId } = await checkoutService.checkout(input);
            res.status(200).json({ msg: 'Sucesso', enrollment_id: enrollmentId });
        },
    };
}

module.exports = { createCheckoutController };
