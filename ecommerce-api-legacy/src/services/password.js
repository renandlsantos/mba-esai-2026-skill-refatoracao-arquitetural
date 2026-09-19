const { scrypt: derive, randomBytes, timingSafeEqual } = require("node:crypto");
const { promisify } = require("node:util");
const scrypt = promisify(derive);
async function hashPassword(password) {
  const salt = randomBytes(16).toString("hex");
  const hash = await scrypt(password, salt, 64);
  return `scrypt:${salt}:${hash.toString("hex")}`;
}
async function checkPassword(stored, candidate) {
  if (
    typeof stored !== "string" ||
    !/^scrypt:[a-f0-9]{32}:[a-f0-9]{128}$/.test(stored)
  )
    return false;
  const [, salt, expected] = stored.split(":");
  const actual = await scrypt(candidate, salt, 64);
  return timingSafeEqual(actual, Buffer.from(expected, "hex"));
}
module.exports = { hashPassword, checkPassword };
