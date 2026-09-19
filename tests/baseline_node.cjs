const express = require("../ecommerce-api-legacy/node_modules/express");
const AppManager = require(process.argv[3]);
const fs = require("node:fs");
(async () => {
  const app = express();
  app.use(express.json());
  const manager = new AppManager();
  manager.initDb();
  manager.setupRoutes(app);
  await new Promise((resolve, reject) =>
    manager.db.get("SELECT count(*) AS n FROM courses", (err) =>
      err ? reject(err) : resolve(),
    ),
  );
  const server = app.listen(0, "127.0.0.1");
  await new Promise((r) => server.once("listening", r));
  const base = `http://127.0.0.1:${server.address().port}`;
  const checks = [];
  const originalLog = console.log;
  const logs = [];
  console.log = (...args) => logs.push(args.join(" "));
  try {
    for (const [method, path, body] of [
      [
        "POST",
        "/api/checkout",
        {
          usr: "Synthetic",
          eml: "synthetic@example.test",
          pwd: "test-only",
          c_id: 2,
          card: "4111111111111111",
        },
      ],
      [
        "POST",
        "/api/checkout",
        {
          usr: "Declined",
          eml: "declined@example.test",
          pwd: "test-only",
          c_id: 2,
          card: "5111111111111111",
        },
      ],
      ["GET", "/api/admin/financial-report"],
      ["DELETE", "/api/users/1"],
    ]) {
      const r = await fetch(base + path, {
        method,
        headers: { "content-type": "application/json" },
        body: body ? JSON.stringify(body) : undefined,
      });
      checks.push({ method, path, status: r.status });
      await r.text();
    }
    const routes = app._router.stack
      .filter((x) => x.route)
      .flatMap((x) =>
        Object.keys(x.route.methods).map((method) => ({
          method: method.toUpperCase(),
          rule: x.route.path,
        })),
      );
    fs.writeFileSync(
      process.argv[2],
      JSON.stringify(
        {
          project: "lms",
          routes,
          checks,
          observed_defects: {
            card_logged: logs.some((x) => x.includes("4111111111111111")),
            gateway_key_logged: logs.some((x) => x.includes("pk_live_")),
          },
          isolation:
            "in-memory database, synthetic data, loopback ephemeral port",
        },
        null,
        2,
      ) + "\n",
    );
  } finally {
    console.log = originalLog;
    await new Promise((r) => server.close(r));
    await new Promise((r) => manager.db.close(r));
  }
  console.log("lms baseline complete");
})().catch((e) => {
  console.error(e.message);
  process.exitCode = 1;
});
