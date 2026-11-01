'use strict';

// Único módulo que lê variáveis de ambiente. Defaults seguros apenas para desenvolvimento.

function parseBoolean(value, fallback) {
    if (value === undefined || value === '') return fallback;
    return ['1', 'true', 'yes', 'on'].includes(String(value).trim().toLowerCase());
}

function parsePort(value, fallback) {
    const port = Number.parseInt(value, 10);
    return Number.isInteger(port) && port > 0 && port < 65536 ? port : fallback;
}

function loadConfig(env = process.env) {
    return Object.freeze({
        port: parsePort(env.PORT, 3000),
        dbPath: env.DB_PATH || ':memory:',
        paymentGatewayKey: env.PAYMENT_GATEWAY_KEY || '',
        enableAdminRoutes: parseBoolean(env.ENABLE_ADMIN_ROUTES, false),
        adminToken: env.ADMIN_TOKEN || '',
        logLevel: env.LOG_LEVEL || 'info',
    });
}

module.exports = { loadConfig };
