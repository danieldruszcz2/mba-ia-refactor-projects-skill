'use strict';

function createUserRepository(db) {
    return {
        findByEmail(email) {
            return db.get('SELECT id, name, email FROM users WHERE email = ?', [email]);
        },

        async create({ name, email, passwordHash }) {
            const { lastID } = await db.run(
                'INSERT INTO users (name, email, pass) VALUES (?, ?, ?)', [name, email, passwordHash]);
            return lastID;
        },

        deleteById(userId) {
            return db.run('DELETE FROM users WHERE id = ?', [userId]);
        },
    };
}

module.exports = { createUserRepository };
