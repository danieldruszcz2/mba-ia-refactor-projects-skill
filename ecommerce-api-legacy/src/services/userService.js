'use strict';

function createUserService({ transaction, userRepository, enrollmentRepository, paymentRepository }) {
    return {
        // Remove o usuário com seus pagamentos e matrículas, sem deixar órfãos.
        deleteUser(userId) {
            return transaction(async () => {
                await paymentRepository.deleteByUserId(userId);
                await enrollmentRepository.deleteByUserId(userId);
                await userRepository.deleteById(userId);
            });
        },
    };
}

module.exports = { createUserService };
