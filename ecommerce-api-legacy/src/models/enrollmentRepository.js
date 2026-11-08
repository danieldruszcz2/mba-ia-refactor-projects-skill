function createEnrollmentRepository(db) {
    return {
        async create({ userId, courseId }, conn = db) {
            const { lastID } = await conn.run('INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)', [userId, courseId]);
            return lastID;
        },
        deleteByUserId(userId, conn = db) {
            return conn.run('DELETE FROM enrollments WHERE user_id = ?', [userId]);
        },
    };
}

module.exports = { createEnrollmentRepository };
