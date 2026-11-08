function createUserRepository(db) {
    return {
        findIdByEmail(email, conn = db) {
            return conn.get('SELECT id FROM users WHERE email = ?', [email]);
        },
        async create({ name, email, passwordHash }, conn = db) {
            const { lastID } = await conn.run('INSERT INTO users (name, email, pass) VALUES (?, ?, ?)', [name, email, passwordHash]);
            return lastID;
        },
        deleteById(id, conn = db) {
            return conn.run('DELETE FROM users WHERE id = ?', [id]);
        },
    };
}

module.exports = { createUserRepository };
