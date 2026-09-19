const express = require("express");
const { settings } = require("./config");
const { createRepository } = require("./models/repository");
const { checkoutController } = require("./controllers/checkout");
const { administrationController } = require("./controllers/administration");
const { simulatePayment } = require("./services/payment");
const { createRoutes } = require("./views/routes");
const { errorHandler, DomainError } = require("./errors");

async function createApp(overrides = {}) {
  const config = { ...settings(), ...overrides };
  const repository = await createRepository(config);
  const app = express();
  app.disable("x-powered-by");
  app.use(express.json({ limit: "32kb", strict: false }));
  app.use(
    createRoutes(
      checkoutController(repository, overrides.payment || simulatePayment),
      administrationController(repository, config.adminToken),
    ),
  );
  app.use((req, res, next) =>
    next(new DomainError("Rota não encontrada", 404)),
  );
  app.use(errorHandler);
  return { app, repository, config };
}
if (require.main === module) {
  createApp()
    .then(({ app, repository, config }) => {
      const server = app.listen(config.port, "127.0.0.1", () =>
        console.log(`LMS ready on 127.0.0.1:${server.address().port}`),
      );
      const shutdown = () =>
        server.close(() => repository.close().then(() => process.exit(0)));
      process.on("SIGTERM", shutdown);
      process.on("SIGINT", shutdown);
      server.on("error", (error) => {
        console.error(error.message);
        repository.close().finally(() => {
          process.exitCode = 1;
        });
      });
    })
    .catch((error) => {
      console.error(error.message);
      process.exitCode = 1;
    });
}
module.exports = { createApp };
