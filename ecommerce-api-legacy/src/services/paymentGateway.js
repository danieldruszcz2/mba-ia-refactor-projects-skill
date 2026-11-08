const { PAYMENT_STATUS, APPROVED_CARD_PREFIX } = require('../config/constants');
const { maskCard } = require('../utils/mask');

// Gateway simulado. A chave fica encapsulada aqui e nunca é escrita em log.
function createPaymentGateway({ apiKey, logger }) {
    return {
        async charge({ cardNumber, amount }) {
            logger.info(`Processando pagamento no cartão ${maskCard(cardNumber)}`, {
                amount,
                gatewayConfigured: Boolean(apiKey),
            });
            return cardNumber.startsWith(APPROVED_CARD_PREFIX) ? PAYMENT_STATUS.PAID : PAYMENT_STATUS.DENIED;
        },
    };
}

module.exports = { createPaymentGateway };
