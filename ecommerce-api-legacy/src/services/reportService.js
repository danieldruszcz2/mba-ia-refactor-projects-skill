'use strict';

const { PAYMENT_STATUS, UNKNOWN_STUDENT_NAME } = require('../config/constants');

function createReportService({ reportRepository }) {
    return {
        // Receita e alunos por curso, na ordem dos cursos (id) e das matrículas (id).
        async financialReport() {
            const rows = await reportRepository.findCourseEnrollmentPayments();
            const reportByCourse = new Map();

            for (const row of rows) {
                if (!reportByCourse.has(row.course_id)) {
                    reportByCourse.set(row.course_id, { course: row.course_title, revenue: 0, students: [] });
                }
                if (row.enrollment_id === null) continue;

                const courseReport = reportByCourse.get(row.course_id);
                const hasPayment = row.payment_id !== null;

                if (hasPayment && row.payment_status === PAYMENT_STATUS.PAID) {
                    courseReport.revenue += row.payment_amount;
                }
                courseReport.students.push({
                    student: row.user_id !== null ? row.user_name : UNKNOWN_STUDENT_NAME,
                    paid: hasPayment ? row.payment_amount : 0,
                });
            }

            return [...reportByCourse.values()];
        },
    };
}

module.exports = { createReportService };
