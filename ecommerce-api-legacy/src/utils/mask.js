'use strict';

function maskCardNumber(cardNumber) {
    const digits = String(cardNumber);
    return `**** **** **** ${digits.slice(-4)}`;
}

module.exports = { maskCardNumber };
