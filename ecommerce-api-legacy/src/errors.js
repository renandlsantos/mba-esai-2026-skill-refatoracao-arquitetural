class DomainError extends Error {
  constructor(message, status = 400) {
    super(message);
    this.status = status;
  }
}
const asyncRoute = (handler) => (req, res, next) =>
  Promise.resolve(handler(req, res)).catch(next);
function errorHandler(error, req, res, next) {
  const status =
    error instanceof DomainError
      ? error.status
      : error.type === "entity.parse.failed"
        ? 400
        : error.type === "entity.too.large"
          ? 413
          : 500;
  res
    .status(status)
    .json({ error: status === 500 ? "Erro interno" : error.message });
}
module.exports = { DomainError, asyncRoute, errorHandler };
