const { test, after } = require("node:test");
const fs = require("node:fs");
const covered = [];
after(() => {
  if (process.env.COVERAGE_OUTPUT)
    fs.writeFileSync(
      process.env.COVERAGE_OUTPUT,
      JSON.stringify(covered, null, 2),
    );
});
const assert = require("node:assert/strict");
const { createApp } = require("../src/app");

async function fixture(overrides = {}) {
  const built = await createApp({
    database: ":memory:",
    adminToken: "test-admin",
    seedDemo: true,
    ...overrides,
  });
  const server = built.app.listen(0, "127.0.0.1");
  await new Promise((r) => server.once("listening", r));
  const base = `http://127.0.0.1:${server.address().port}`;
  return {
    ...built,
    async call(method, path, body, admin = false) {
      const response = await fetch(base + path, {
        method,
        headers: {
          "content-type": "application/json",
          ...(admin ? { authorization: "Bearer test-admin" } : {}),
        },
        body: body === undefined ? undefined : JSON.stringify(body),
      });
      covered.push({ method, path, status: response.status });
      const raw = await response.text();
      let data;
      try {
        data = JSON.parse(raw);
      } catch {
        data = raw;
      }
      return { status: response.status, data };
    },
    async close() {
      await new Promise((r) => server.close(r));
      await built.repository.close();
    },
  };
}
const customer = (suffix = "") => ({
  usr: "Synthetic",
  eml: `user${suffix}@example.test`,
  pwd: "test-only",
  c_id: 1,
  card: "4111111111111111",
});
test("all routes, checkout denial, admin and dependent cleanup", async () => {
  const f = await fixture();
  try {
    const result = await f.call("POST", "/api/checkout", customer());
    assert.equal(result.status, 200);
    assert.ok(result.data.enrollment_id);
    assert.equal(
      (
        await f.call("POST", "/api/checkout", {
          ...customer("denied"),
          card: "5111111111111111",
        })
      ).status,
      400,
    );
    assert.equal(
      (await f.call("GET", "/api/admin/financial-report")).status,
      403,
    );
    const report = await f.call(
      "GET",
      "/api/admin/financial-report",
      undefined,
      true,
    );
    assert.equal(report.status, 200);
    assert.equal(report.data[0].revenue, 997);
    assert.equal((await f.call("DELETE", "/api/users/1")).status, 403);
    assert.equal(
      (await f.call("DELETE", "/api/users/1", undefined, true)).status,
      200,
    );
    const counts = await f.repository.counts();
    assert.equal(counts.enrollments, 0);
    assert.equal(counts.payments, 0);
    assert.equal(
      (await f.call("DELETE", "/api/users/999", undefined, true)).status,
      404,
    );
  } finally {
    await f.close();
  }
});
test("invalid input and secrets never enter logs", async () => {
  const f = await fixture();
  const logs = [];
  const original = console.log;
  console.log = (...x) => logs.push(x.join(" "));
  try {
    for (const value of [
      [],
      null,
      { ...customer(), card: 123 },
      { ...customer(), c_id: true },
      { ...customer(), pwd: "" },
      { ...customer(), eml: "invalid" },
    ])
      assert.equal((await f.call("POST", "/api/checkout", value)).status, 400);
    assert.equal(
      (await f.call("POST", "/api/checkout", customer())).status,
      200,
    );
    const text = JSON.stringify(logs);
    assert.ok(!text.includes(customer().card));
    assert.ok(!text.includes("test-only"));
    assert.equal((await f.call("GET", "/unknown")).status, 404);
    const user = await f.repository.findUser(customer().eml);
    assert.match(user.pass, /^scrypt:/);
    assert.notEqual(user.pass, customer().pwd);
    assert.equal(
      (await f.call("POST", "/api/checkout", { ...customer(), pwd: "wrong" }))
        .status,
      401,
    );
  } finally {
    console.log = original;
    await f.close();
  }
});
test("failed payment insert rolls back user, enrollment and payment", async () => {
  const f = await fixture();
  try {
    await f.repository.executeForTest(
      "CREATE TRIGGER fail_payment BEFORE INSERT ON payments BEGIN SELECT RAISE(ABORT, 'simulated'); END",
    );
    assert.equal(
      (await f.call("POST", "/api/checkout", customer())).status,
      500,
    );
    const counts = await f.repository.counts();
    assert.equal(counts.users, 0);
    assert.equal(counts.enrollments, 0);
    assert.equal(counts.payments, 0);
    assert.equal(counts.audit_logs, 0);
  } finally {
    await f.close();
  }
});
test("concurrent checkouts serialize transactions and report query count stays bounded", async () => {
  const f = await fixture();
  try {
    const results = await Promise.all(
      Array.from({ length: 8 }, (_, i) =>
        f.call("POST", "/api/checkout", customer(String(i))),
      ),
    );
    assert.ok(results.every((r) => r.status === 200));
    const before = f.repository.queryCount;
    const report = await f.call(
      "GET",
      "/api/admin/financial-report",
      undefined,
      true,
    );
    assert.equal(report.status, 200);
    assert.equal(report.data[0].revenue, 8 * 997);
    assert.equal(f.repository.queryCount - before, 1);
    const counts = await f.repository.counts();
    assert.equal(counts.enrollments, 8);
    assert.equal(counts.payments, 8);
  } finally {
    await f.close();
  }
});

test("password hashes use independent salts and reject wrong values", async () => {
  const { hashPassword, checkPassword } = require("../src/services/password");
  const first = await hashPassword("synthetic");
  const second = await hashPassword("synthetic");
  assert.notEqual(first, second);
  assert.equal(await checkPassword(first, "synthetic"), true);
  assert.equal(await checkPassword(first, "wrong"), false);
  assert.equal(await checkPassword("legacy", "synthetic"), false);
});
