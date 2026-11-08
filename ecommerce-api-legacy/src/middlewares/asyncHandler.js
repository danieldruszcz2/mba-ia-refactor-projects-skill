// Express 4 não encaminha rejeições de handlers async: repassa o erro para next().
const asyncHandler = (handler) => (req, res, next) => {
    Promise.resolve(handler(req, res, next)).catch(next);
};

module.exports = { asyncHandler };
