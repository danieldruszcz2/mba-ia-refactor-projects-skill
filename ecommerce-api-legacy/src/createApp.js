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
const { createRequireAdmin } = require('./middlewares/requireAdmin');
const { createErrorHandler } = require('./middlewares/errorHandler');
const { createRouter } = require('./routes');

// Composition root: monta models → services → controllers → rotas.
function createApp({ db, config, logger }) {
    const users = createUserRepository(db);
    const courses = createCourseRepository(db);
    const enrollments = createEnrollmentRepository(db);
    const payments = createPaymentRepository(db);
    const auditLogs = createAuditLogRepository(db);
    const reports = createReportRepository(db);

    const paymentGateway = createPaymentGateway({ apiKey: config.paymentGatewayKey, logger });
    const checkoutService = createCheckoutService({ db, users, courses, enrollments, payments, auditLogs, paymentGateway });
    const reportService = createReportService({ reports });
    const userService = createUserService({ db, users, enrollments, payments });

    const controllers = {
        checkout: createCheckoutController({ checkoutService }),
        report: createReportController({ reportService }),
        user: createUserController({ userService }),
    };

    const app = express();
    app.use(express.json());
    app.use(createRouter({ controllers, requireAdmin: createRequireAdmin(config) }));
    app.use(createErrorHandler({ logger }));
    return app;
}

module.exports = { createApp };
