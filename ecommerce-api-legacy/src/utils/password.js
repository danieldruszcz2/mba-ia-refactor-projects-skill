'use strict';

const crypto = require('crypto');
const { promisify } = require('util');

const scrypt = promisify(crypto.scrypt);

const KEY_LENGTH = 64;
const SALT_BYTES = 16;
const RANDOM_PASSWORD_BYTES = 16;

// Formato armazenado: scrypt$<salt hex>$<hash hex>
async function hashPassword(password) {
    const salt = crypto.randomBytes(SALT_BYTES).toString('hex');
    const derived = await scrypt(password, salt, KEY_LENGTH);
    return `scrypt$${salt}$${derived.toString('hex')}`;
}

function generateRandomPassword() {
    return crypto.randomBytes(RANDOM_PASSWORD_BYTES).toString('hex');
}

module.exports = { hashPassword, generateRandomPassword };
