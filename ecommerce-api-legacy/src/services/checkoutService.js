const { PAYMENT_STATUS } = require('../config/constants');
const { NotFoundError, PaymentDeniedError } = require('../utils/errors');
const { hashPassword, generateRandomPassword } = require('../utils/password');

function createCheckoutService({ db, users, courses, enrollments, payments, auditLogs, paymentGateway }) {
    return {
        async checkout({ name, email, password, courseId, cardNumber }) {
            const course = await courses.findActiveById(courseId);
            if (!course) throw new NotFoundError('Curso não encontrado');

            const existingUser = await users.findIdByEmail(email);

            const status = await paymentGateway.charge({ cardNumber, amount: course.price });
            if (status !== PAYMENT_STATUS.PAID) throw new PaymentDeniedError();

            const passwordHash = existingUser ? null : await hashPassword(password || generateRandomPassword());

            // Usuário, matrícula, pagamento e auditoria são gravados juntos ou nada é gravado.
            return db.transaction(async (tx) => {
                const userId = existingUser
                    ? existingUser.id
                    : await users.create({ name, email, passwordHash }, tx);
                const enrollmentId = await enrollments.create({ userId, courseId: course.id }, tx);
                await payments.create({ enrollmentId, amount: course.price, status }, tx);
                await auditLogs.record(`Checkout curso ${course.id} por ${userId}`, tx);
                return { enrollmentId };
            });
        },
    };
}

module.exports = { createCheckoutService };
