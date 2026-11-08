const LEVELS = Object.freeze({ debug: 10, info: 20, warn: 30, error: 40 });

function createLogger(level = 'info') {
    const threshold = LEVELS[level] || LEVELS.info;
    const write = (name, stream) => (message, meta) => {
        if (LEVELS[name] < threshold) return;
        const line = `${new Date().toISOString()} ${name.toUpperCase()} ${message}`;
        stream.write(meta ? `${line} ${JSON.stringify(meta)}\n` : `${line}\n`);
    };
    return {
        debug: write('debug', process.stdout),
        info: write('info', process.stdout),
        warn: write('warn', process.stderr),
        error: write('error', process.stderr),
    };
}

module.exports = { createLogger };
