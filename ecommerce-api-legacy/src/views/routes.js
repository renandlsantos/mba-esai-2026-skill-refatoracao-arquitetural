const express = require("express");
const { asyncRoute } = require("../errors");
function createRoutes(checkout, admin) {
  const router = express.Router();
  router.post(
    "/api/checkout",
    asyncRoute(async (req, res) => res.json(await checkout(req.body))),
  );
  router.get(
    "/api/admin/financial-report",
    asyncRoute(async (req, res) =>
      res.json(await admin.report(req.headers.authorization)),
    ),
  );
  router.delete(
    "/api/users/:id",
    asyncRoute(async (req, res) =>
      res.send(
        await admin.deleteUser(req.headers.authorization, req.params.id),
      ),
    ),
  );
  return router;
}
module.exports = { createRoutes };
