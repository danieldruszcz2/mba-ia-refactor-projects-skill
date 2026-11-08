const { ValidationError } = require('../utils/errors');
const { toPositiveInteger } = require('../utils/validators');

function createUserController({ userService }) {
    return {
        async deleteUser(req, res) {
            const userId = toPositiveInteger(req.params.id);
            if (userId === null) throw new ValidationError('Bad Request');
            await userService.deleteUser(userId);
            res.send('Usuário deletado');
        },
    };
}

module.exports = { createUserController };
