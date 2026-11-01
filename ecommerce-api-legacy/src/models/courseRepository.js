'use strict';

function createCourseRepository(db) {
    return {
        findActiveById(courseId) {
            return db.get('SELECT id, title, price, active FROM courses WHERE id = ? AND active = 1', [courseId]);
        },
    };
}

module.exports = { createCourseRepository };
