'use strict';

// Uma única consulta (sem N+1): cada curso com suas matrículas, o aluno e o primeiro pagamento.
const FINANCIAL_ROWS_SQL = `
    SELECT c.id      AS course_id,
           c.title   AS course_title,
           e.id      AS enrollment_id,
           u.id      AS user_id,
           u.name    AS user_name,
           p.id      AS payment_id,
           p.amount  AS payment_amount,
           p.status  AS payment_status
      FROM courses c
      LEFT JOIN enrollments e ON e.course_id = c.id
      LEFT JOIN users u       ON u.id = e.user_id
      LEFT JOIN payments p    ON p.id = (SELECT MIN(p2.id) FROM payments p2 WHERE p2.enrollment_id = e.id)
     ORDER BY c.id, e.id`;

function createReportRepository(db) {
    return {
        findCourseEnrollmentPayments() {
            return db.all(FINANCIAL_ROWS_SQL);
        },
    };
}

module.exports = { createReportRepository };
