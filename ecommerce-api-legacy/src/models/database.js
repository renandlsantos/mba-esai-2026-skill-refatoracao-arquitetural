const sqlite3 = require("sqlite3");
function connect(filename) {
  const db = new sqlite3.Database(filename);
  db.configure("busyTimeout", 5000);
  const api = {
    run(sql, params = []) {
      return new Promise((resolve, reject) =>
        db.run(sql, params, function (error) {
          error
            ? reject(error)
            : resolve({ id: this.lastID, changes: this.changes });
        }),
      );
    },
    get(sql, params = []) {
      return new Promise((resolve, reject) =>
        db.get(sql, params, (error, row) =>
          error ? reject(error) : resolve(row),
        ),
      );
    },
    all(sql, params = []) {
      return new Promise((resolve, reject) =>
        db.all(sql, params, (error, rows) =>
          error ? reject(error) : resolve(rows),
        ),
      );
    },
    close() {
      return new Promise((resolve, reject) =>
        db.close((error) => (error ? reject(error) : resolve())),
      );
    },
  };
  return api;
}
module.exports = { connect };
