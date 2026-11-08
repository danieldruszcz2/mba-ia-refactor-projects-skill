function createPaymentRepository(db) {
    return {
        async create({ enrollmentId, amount, status }, conn = db) {
            const { lastID } = await conn.run('INSERT INTO payments (enrollment_id, amount, status) VALUES (?, ?, ?)', [enrollmentId, amount, status]);
            return lastID;
        },
        deleteByUserId(userId, conn = db) {
            return conn.run(
                'DELETE FROM payments WHERE enrollment_id IN (SELECT id FROM enrollments WHERE user_id = ?)',
                [userId],
            );
        },
    };
}

module.exports = { createPaymentRepository };
