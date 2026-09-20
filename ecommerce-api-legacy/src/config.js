function settings(env = process.env) {
  return {
    database: env.DATABASE_PATH || ":memory:",
    port: Number(env.PORT || 3000),
    adminToken: env.ADMIN_TOKEN || "",
    seedDemo: env.SEED_DEMO === "true",
  };
}
module.exports = { settings };
