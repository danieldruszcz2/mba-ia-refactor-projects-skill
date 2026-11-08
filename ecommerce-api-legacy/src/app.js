const { loadConfig } = require('./config');
const { createDatabase } = require('./models/database');
const { createApp } = require('./createApp');
const { createLogger } = require('./utils/logger');

async function main() {
    const config = loadConfig();
    const logger = createLogger(config.logLevel);
    const db = await createDatabase(config.databasePath);
    const app = createApp({ db, config, logger });

    app.listen(config.port, () => {
        logger.info(`LMS API rodando na porta ${config.port}`);
    });
}

main().catch((err) => {
    process.stderr.write(`Falha ao iniciar a aplicação: ${err.stack || err}\n`);
    process.exit(1);
});
