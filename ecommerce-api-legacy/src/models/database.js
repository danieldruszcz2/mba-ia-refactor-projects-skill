const sqlite3 = require('sqlite3');
const { hashPassword } = require('../utils/password');
const { PAYMENT_STATUS } = require('../config/constants');

const SCHEMA = [
    'CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, email TEXT, pass TEXT)',
    'CREATE TABLE IF NOT EXISTS courses (id INTEGER PRIMARY KEY, title TEXT, price REAL, active INTEGER)',
    'CREATE TABLE IF NOT EXISTS enrollments (id INTEGER PRIMARY KEY, user_id INTEGER, course_id INTEGER)',
    'CREATE TABLE IF NOT EXISTS payments (id INTEGER PRIMARY KEY, enrollment_id INTEGER, amount REAL, status TEXT)',
    'CREATE TABLE IF NOT EXISTS audit_logs (id INTEGER PRIMARY KEY, action TEXT, created_at DATETIME)',
];

// Envolve a conexão sqlite3 (API de callbacks) em uma interface baseada em Promises.
function wrapConnection(connection) {
    let queue = Promise.resolve();

    const db = {
        run(sql, params = []) {
            return new Promise((resolve, reject) => {
                connection.run(sql, params, function onRun(err) {
                    if (err) return reject(err);
                    resolve({ lastID: this.lastID, changes: this.changes });
                });
            });
        },
        get(sql, params = []) {
            return new Promise((resolve, reject) => {
                connection.get(sql, params, (err, row) => (err ? reject(err) : resolve(row)));
            });
        },
        all(sql, params = []) {
            return new Promise((resolve, reject) => {
                connection.all(sql, params, (err, rows) => (err ? reject(err) : resolve(rows)));
            });
        },
        close() {
            return new Promise((resolve, reject) => {
                connection.close((err) => (err ? reject(err) : resolve()));
            });
        },
        // Transações são serializadas: a conexão é única, então duas transações
        // simultâneas não podem se intercalar.
        transaction(work) {
            const result = queue.then(async () => {
                await db.run('BEGIN TRANSACTION');
                try {
                    const value = await work(db);
                    await db.run('COMMIT');
                    return value;
                } catch (err) {
                    await db.run('ROLLBACK').catch(() => {});
                    throw err;
                }
            });
            queue = result.catch(() => {});
            return result;
        },
    };
    return db;
}

function openDatabase(path) {
    return new Promise((resolve, reject) => {
        const connection = new sqlite3.Database(path, (err) => (err ? reject(err) : resolve(wrapConnection(connection))));
    });
}

async function initSchema(db) {
    for (const statement of SCHEMA) {
        await db.run(statement);
    }
}

// Popula os dados iniciais apenas em banco vazio (o banco padrão é em memória).
async function seed(db) {
    const { count } = await db.get('SELECT COUNT(*) AS count FROM users');
    if (count > 0) return;

    const seedPasswordHash = await hashPassword('123');
    await db.transaction(async (tx) => {
        await tx.run('INSERT INTO users (name, email, pass) VALUES (?, ?, ?)', ['Leonan', 'leonan@fullcycle.com.br', seedPasswordHash]);
        await tx.run('INSERT INTO courses (title, price, active) VALUES (?, ?, 1), (?, ?, 1)', ['Clean Architecture', 997.0, 'Docker', 497.0]);
        await tx.run('INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)', [1, 1]);
        await tx.run('INSERT INTO payments (enrollment_id, amount, status) VALUES (?, ?, ?)', [1, 997.0, PAYMENT_STATUS.PAID]);
    });
}

async function createDatabase(path) {
    const db = await openDatabase(path);
    await initSchema(db);
    await seed(db);
    return db;
}

module.exports = { createDatabase };
