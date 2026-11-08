function createUserService({ db, users, enrollments, payments }) {
    return {
        // Remove o usuário e, em cascata, seus pagamentos e matrículas (sem órfãos).
        deleteUser(userId) {
            return db.transaction(async (tx) => {
                await payments.deleteByUserId(userId, tx);
                await enrollments.deleteByUserId(userId, tx);
                await users.deleteById(userId, tx);
            });
        },
    };
}

module.exports = { createUserService };
