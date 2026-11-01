'use strict';

const LEVELS = Object.freeze({ debug: 10, info: 20, warn: 30, error: 40 });

function createLogger(level = 'info') {
    const threshold = LEVELS[level] ?? LEVELS.info;
    const write = (name, method) => (message, ...details) => {
        if (LEVELS[name] < threshold) return;
        // eslint-disable-next-line no-console
        console[method](`${new Date().toISOString()} [${name.toUpperCase()}] ${message}`, ...details);
    };
    return Object.freeze({
        debug: write('debug', 'log'),
        info: write('info', 'log'),
        warn: write('warn', 'warn'),
        error: write('error', 'error'),
    });
}

module.exports = { createLogger };
