const { connect } = require("./database");
const { DomainError } = require("../errors");

async function createRepository(config) {
  const db = connect(config.database);
  let queue = Promise.resolve();
  let queryCount = 0;
  // All operations on this connection pass through the same queue. Reads cannot
  // observe another request's uncommitted writes on the shared SQLite handle.
  const serialized = (work) => {
    const result = queue.then(work);
    queue = result.catch(() => {});
    return result;
  };
  const run = (sql, params) => {
    queryCount++;
    return db.run(sql, params);
  };
  const get = (sql, params) => {
    queryCount++;
    return db.get(sql, params);
  };
  const all = (sql, params) => {
    queryCount++;
    return db.all(sql, params);
  };
  const transaction = (work) =>
    serialized(async () => {
      await run("BEGIN IMMEDIATE");
      try {
        const result = await work();
        await run("COMMIT");
        return result;
      } catch (error) {
        await run("ROLLBACK");
        throw error;
      }
    });
  try {
    for (const sql of [
      "CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, email TEXT, pass TEXT)",
      "CREATE TABLE IF NOT EXISTS courses (id INTEGER PRIMARY KEY, title TEXT, price REAL, active INTEGER)",
      "CREATE TABLE IF NOT EXISTS enrollments (id INTEGER PRIMARY KEY, user_id INTEGER, course_id INTEGER)",
      "CREATE TABLE IF NOT EXISTS payments (id INTEGER PRIMARY KEY, enrollment_id INTEGER, amount REAL, status TEXT)",
      "CREATE TABLE IF NOT EXISTS audit_logs (id INTEGER PRIMARY KEY, action TEXT, created_at DATETIME)",
    ])
      await run(sql);
    if (config.seedDemo) {
      const populated = await get(
        "SELECT (SELECT COUNT(*) FROM users)+(SELECT COUNT(*) FROM courses)+(SELECT COUNT(*) FROM enrollments)+(SELECT COUNT(*) FROM payments) AS n",
      );
      if (populated.n !== 0)
        throw new DomainError("Demo seed requires an empty database", 409);
      await run(
        "INSERT INTO courses(title,price,active) VALUES ('Clean Architecture',997,1),('Docker',497,1)",
      );
    }
  } catch (error) {
    await db.close();
    throw error;
  }
  return {
    get queryCount() {
      return queryCount;
    },
    withTransaction(work) {
      return transaction(() =>
        work({
          getCourse: (courseId) =>
            get("SELECT * FROM courses WHERE id=? AND active=1", [courseId]),
          findUser: (email) =>
            get("SELECT * FROM users WHERE email=?", [email]),
          createUser: (name, email, passwordHash) =>
            run("INSERT INTO users(name,email,pass) VALUES (?,?,?)", [
              name,
              email,
              passwordHash,
            ]),
          enroll: (userId, courseId) =>
            run("INSERT INTO enrollments(user_id,course_id) VALUES (?,?)", [
              userId,
              courseId,
            ]),
          recordPayment: (enrollmentId, amount, status) =>
            run(
              "INSERT INTO payments(enrollment_id,amount,status) VALUES (?,?,?)",
              [enrollmentId, amount, status],
            ),
          audit: (action) =>
            run(
              "INSERT INTO audit_logs(action,created_at) VALUES (?,datetime('now'))",
              [action],
            ),
        }),
      );
    },
    financialReport() {
      return serialized(async () => {
        const rows = await all(
          "SELECT c.id,c.title,u.name,p.amount,p.status,e.id AS enrollment_id FROM courses c LEFT JOIN enrollments e ON e.course_id=c.id LEFT JOIN users u ON u.id=e.user_id LEFT JOIN payments p ON p.enrollment_id=e.id ORDER BY c.id,e.id",
        );
        const courses = new Map();
        for (const row of rows) {
          if (!courses.has(row.id))
            courses.set(row.id, {
              course: row.title,
              revenue: 0,
              students: [],
            });
          const course = courses.get(row.id);
          if (row.enrollment_id !== null) {
            if (row.status === "PAID") course.revenue += row.amount;
            course.students.push({
              student: row.name || "Unknown",
              paid: row.amount || 0,
            });
          }
        }
        return [...courses.values()].map((course) => ({
          ...course,
          revenue: Math.round(course.revenue * 100) / 100,
        }));
      });
    },
    deleteUser(userId) {
      return transaction(async () => {
        if (!(await get("SELECT id FROM users WHERE id=?", [userId])))
          throw new DomainError("Usuário não encontrado", 404);
        await run(
          "DELETE FROM payments WHERE enrollment_id IN (SELECT id FROM enrollments WHERE user_id=?)",
          [userId],
        );
        await run("DELETE FROM enrollments WHERE user_id=?", [userId]);
        await run("DELETE FROM users WHERE id=?", [userId]);
      });
    },
    findUser(email) {
      return serialized(() =>
        get("SELECT * FROM users WHERE email=?", [email]),
      );
    },
    counts() {
      return serialized(async () => {
        const result = {};
        for (const table of [
          "users",
          "courses",
          "enrollments",
          "payments",
          "audit_logs",
        ])
          result[table] = (await get(`SELECT COUNT(*) AS n FROM ${table}`)).n;
        return result;
      });
    },
    // In-process diagnostic hook, never registered as an HTTP endpoint.
    executeForTest(sql) {
      return serialized(() => run(sql));
    },
    close() {
      return serialized(() => db.close());
    },
  };
}
module.exports = { createRepository };
