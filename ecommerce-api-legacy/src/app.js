'use strict';

const { loadConfig } = require('./config');
const { createDatabase } = require('./models/database');
const { createApp } = require('./createApp');
const { createLogger } = require('./utils/logger');

async function start() {
    const config = loadConfig();
    const logger = createLogger(config.logLevel);

    if (!config.paymentGatewayKey) logger.warn('PAYMENT_GATEWAY_KEY não definida (gateway simulado).');
    if (config.enableAdminRoutes && !config.adminToken) {
        logger.warn('ENABLE_ADMIN_ROUTES=true sem ADMIN_TOKEN: rotas admin continuarão respondendo 403.');
    }

    const db = await createDatabase(config.dbPath);
    const app = createApp({ db, config, logger });

    app.listen(config.port, () => {
        logger.info(`LMS API rodando na porta ${config.port}`);
    });
}

start().catch((err) => {
    // eslint-disable-next-line no-console
    console.error('Falha ao iniciar a aplicação', err);
    process.exit(1);
});
