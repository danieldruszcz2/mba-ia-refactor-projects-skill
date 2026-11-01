'use strict';

const { PAYMENT_STATUS, APPROVED_CARD_PREFIX } = require('../config/constants');
const { maskCardNumber } = require('../utils/mask');

// Gateway de pagamento simulado: aprova pelo prefixo do cartão.
// O cartão só aparece mascarado nos logs e a chave do gateway nunca é logada.
function createPaymentGateway({ logger }) {
    return {
        charge({ cardNumber, amount }) {
            logger.info(`Processando pagamento de ${amount} no cartão ${maskCardNumber(cardNumber)}`);
            return cardNumber.startsWith(APPROVED_CARD_PREFIX) ? PAYMENT_STATUS.PAID : PAYMENT_STATUS.DENIED;
        },
    };
}

module.exports = { createPaymentGateway };
