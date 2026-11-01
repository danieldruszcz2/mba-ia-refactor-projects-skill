'use strict';

const express = require('express');

const { createUserRepository } = require('./models/userRepository');
const { createCourseRepository } = require('./models/courseRepository');
const { createEnrollmentRepository } = require('./models/enrollmentRepository');
const { createPaymentRepository } = require('./models/paymentRepository');
const { createAuditLogRepository } = require('./models/auditLogRepository');
const { createReportRepository } = require('./models/reportRepository');
const { createPaymentGateway } = require('./services/paymentGateway');
const { createCheckoutService } = require('./services/checkoutService');
const { createReportService } = require('./services/reportService');
const { createUserService } = require('./services/userService');
const { createCheckoutController } = require('./controllers/checkoutController');
const { createReportController } = require('./controllers/reportController');
const { createUserController } = require('./controllers/userController');
const { createRouter } = require('./routes');
const { createRequireAdmin } = require('./middlewares/requireAdmin');
const { createErrorHandler } = require('./middlewares/errorHandler');

// Composition root: monta models → services → controllers → rotas → middlewares.
function createApp({ db, config, logger }) {
    const transaction = (work) => db.withTransaction(work);

    const userRepository = createUserRepository(db);
    const courseRepository = createCourseRepository(db);
    const enrollmentRepository = createEnrollmentRepository(db);
    const paymentRepository = createPaymentRepository(db);
    const auditLogRepository = createAuditLogRepository(db);
    const reportRepository = createReportRepository(db);

    const paymentGateway = createPaymentGateway({ logger });
    const checkoutService = createCheckoutService({
        transaction, userRepository, courseRepository, enrollmentRepository,
        paymentRepository, auditLogRepository, paymentGateway, logger,
    });
    const reportService = createReportService({ reportRepository });
    const userService = createUserService({ transaction, userRepository, enrollmentRepository, paymentRepository });

    const app = express();
    app.use(express.json());
    app.use(createRouter({
        checkoutController: createCheckoutController({ checkoutService }),
        reportController: createReportController({ reportService }),
        userController: createUserController({ userService }),
        requireAdmin: createRequireAdmin({ enabled: config.enableAdminRoutes, adminToken: config.adminToken }),
    }));
    app.use(createErrorHandler({ logger }));

    return app;
}

module.exports = { createApp };
