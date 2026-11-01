'use strict';

const { PAYMENT_STATUS } = require('../config/constants');
const { NotFoundError, ValidationError } = require('../utils/errors');
const { hashPassword, generateRandomPassword } = require('../utils/password');

function createCheckoutService({
    transaction, userRepository, courseRepository, enrollmentRepository,
    paymentRepository, auditLogRepository, paymentGateway, logger,
}) {
    return {
        // Matricula o aluno num curso após aprovar o pagamento. Todas as escritas são atômicas.
        async checkout({ userName, email, password, courseId, cardNumber }) {
            const course = await courseRepository.findActiveById(courseId);
            if (!course) throw new NotFoundError('Curso não encontrado');

            const existingUser = await userRepository.findByEmail(email);

            const status = paymentGateway.charge({ cardNumber, amount: course.price });
            if (status === PAYMENT_STATUS.DENIED) throw new ValidationError('Pagamento recusado');

            // Hash lento calculado fora da transação para não segurar o banco.
            const passwordHash = existingUser
                ? null
                : await hashPassword(password || generateRandomPassword());

            const { userId, enrollmentId } = await transaction(async () => {
                const id = existingUser
                    ? existingUser.id
                    : await userRepository.create({ name: userName, email, passwordHash });
                const newEnrollmentId = await enrollmentRepository.create({ userId: id, courseId });
                await paymentRepository.create({ enrollmentId: newEnrollmentId, amount: course.price, status });
                await auditLogRepository.record(`Checkout curso ${courseId} por ${id}`);
                return { userId: id, enrollmentId: newEnrollmentId };
            });

            logger.info(`Checkout concluído: usuário ${userId}, curso "${course.title}"`);
            return { enrollmentId };
        },
    };
}

module.exports = { createCheckoutService };
