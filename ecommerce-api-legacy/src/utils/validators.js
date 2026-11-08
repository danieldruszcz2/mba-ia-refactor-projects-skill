const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const CARD_PATTERN = /^\d{12,19}$/;

const isNonEmptyString = (value) => typeof value === 'string' && value.trim().length > 0;

const isEmail = (value) => isNonEmptyString(value) && EMAIL_PATTERN.test(value.trim());

const isCardNumber = (value) => typeof value === 'string' && CARD_PATTERN.test(value);

// Aceita inteiro ou string numérica ("2"), como a API original aceitava.
function toPositiveInteger(value) {
    if (typeof value === 'number' && Number.isInteger(value) && value > 0) return value;
    if (typeof value === 'string' && /^\d+$/.test(value.trim())) {
        const parsed = Number.parseInt(value, 10);
        return parsed > 0 ? parsed : null;
    }
    return null;
}

module.exports = { isNonEmptyString, isEmail, isCardNumber, toPositiveInteger };
