// Mantém apenas os 4 últimos dígitos do cartão para uso em logs.
function maskCard(cardNumber) {
    const digits = String(cardNumber || '');
    if (digits.length <= 4) return '****';
    return '*'.repeat(digits.length - 4) + digits.slice(-4);
}

module.exports = { maskCard };
