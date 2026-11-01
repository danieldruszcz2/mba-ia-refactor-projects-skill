'use strict';

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

// Adaptador fino com API de Promises sobre o driver sqlite3 (que só oferece callbacks).
class Database {
    constructor(connection) {
        this.connection = connection;
        this.transactionQueue = Promise.resolve();
    }

    static open(path) {
        return new Promise((resolve, reject) => {
            const connection = new sqlite3.Database(path, (err) => {
                if (err) reject(err);
                else resolve(new Database(connection));
            });
        });
    }

    run(sql, params = []) {
        return new Promise((resolve, reject) => {
            this.connection.run(sql, params, function onRun(err) {
                if (err) reject(err);
                else resolve({ lastID: this.lastID, changes: this.changes });
            });
        });
    }

    get(sql, params = []) {
        return new Promise((resolve, reject) => {
            this.connection.get(sql, params, (err, row) => (err ? reject(err) : resolve(row)));
        });
    }

    all(sql, params = []) {
        return new Promise((resolve, reject) => {
            this.connection.all(sql, params, (err, rows) => (err ? reject(err) : resolve(rows)));
        });
    }

    exec(sql) {
        return new Promise((resolve, reject) => {
            this.connection.exec(sql, (err) => (err ? reject(err) : resolve()));
        });
    }

    // Executa `work` entre BEGIN/COMMIT, com ROLLBACK em qualquer erro.
    // As transações são serializadas porque o SQLite usa uma única conexão.
    withTransaction(work) {
        const result = this.transactionQueue.then(async () => {
            await this.exec('BEGIN');
            try {
                const value = await work();
                await this.exec('COMMIT');
                return value;
            } catch (err) {
                await this.exec('ROLLBACK').catch(() => {});
                throw err;
            }
        });
        this.transactionQueue = result.catch(() => {});
        return result;
    }

    close() {
        return new Promise((resolve, reject) => {
            this.connection.close((err) => (err ? reject(err) : resolve()));
        });
    }
}

async function initSchema(db) {
    for (const statement of SCHEMA) {
        await db.run(statement);
    }
}

// Seed idempotente: só popula um banco vazio (mesmo estado inicial do código original).
async function seed(db) {
    const { total } = await db.get('SELECT COUNT(*) AS total FROM users');
    if (total > 0) return;

    const seedPasswordHash = await hashPassword('123');
    await db.withTransaction(async () => {
        await db.run('INSERT INTO users (name, email, pass) VALUES (?, ?, ?)',
            ['Leonan', 'leonan@fullcycle.com.br', seedPasswordHash]);
        await db.run('INSERT INTO courses (title, price, active) VALUES (?, ?, ?), (?, ?, ?)',
            ['Clean Architecture', 997.0, 1, 'Docker', 497.0, 1]);
        await db.run('INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)', [1, 1]);
        await db.run('INSERT INTO payments (enrollment_id, amount, status) VALUES (?, ?, ?)',
            [1, 997.0, PAYMENT_STATUS.PAID]);
    });
}

async function createDatabase(path) {
    const db = await Database.open(path);
    await initSchema(db);
    await seed(db);
    return db;
}

module.exports = { Database, createDatabase };
