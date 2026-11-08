const crypto = require('crypto');
const { promisify } = require('util');

const scrypt = promisify(crypto.scrypt);
const KEY_LENGTH = 64;
const SALT_BYTES = 16;
const PREFIX = 'scrypt';

async function hashPassword(plain) {
    const salt = crypto.randomBytes(SALT_BYTES).toString('hex');
    const derived = await scrypt(String(plain), salt, KEY_LENGTH);
    return `${PREFIX}$${salt}$${derived.toString('hex')}`;
}

// Formato gravado: scrypt$<salt hex>$<hash hex>. A verificação deve usar
// crypto.timingSafeEqual quando um fluxo de login for criado.

// Usada quando o cliente não informa senha: nunca um valor fixo conhecido.
function generateRandomPassword() {
    return crypto.randomBytes(24).toString('base64url');
}

module.exports = { hashPassword, generateRandomPassword };
