function createCourseRepository(db) {
    return {
        findActiveById(id, conn = db) {
            return conn.get('SELECT id, title, price FROM courses WHERE id = ? AND active = 1', [id]);
        },
    };
}

module.exports = { createCourseRepository };
