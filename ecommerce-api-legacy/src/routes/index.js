const express = require('express');
const { asyncHandler } = require('../middlewares/asyncHandler');

function createRouter({ controllers, requireAdmin }) {
    const router = express.Router();

    router.post('/api/checkout', asyncHandler(controllers.checkout.checkout));
    router.get('/api/admin/financial-report', requireAdmin, asyncHandler(controllers.report.financialReport));
    router.delete('/api/users/:id', requireAdmin, asyncHandler(controllers.user.deleteUser));

    return router;
}

module.exports = { createRouter };
