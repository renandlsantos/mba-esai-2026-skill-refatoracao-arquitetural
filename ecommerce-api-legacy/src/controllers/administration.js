const { timingSafeEqual } = require("node:crypto");
const { DomainError } = require("../errors");
function authorize(header, expected) {
  const actual =
    typeof header === "string" && header.startsWith("Bearer ")
      ? header.slice(7)
      : "";
  const left = Buffer.from(actual),
    right = Buffer.from(expected);
  if (
    !expected ||
    left.length !== right.length ||
    !timingSafeEqual(left, right)
  )
    throw new DomainError("Acesso administrativo negado", 403);
}
function administrationController(repository, token) {
  return {
    async report(header) {
      authorize(header, token);
      return repository.financialReport();
    },
    async deleteUser(header, id) {
      authorize(header, token);
      if (
        !/^\d+$/.test(id) ||
        !Number.isSafeInteger(Number(id)) ||
        Number(id) < 1
      )
        throw new DomainError("ID inválido");
      await repository.deleteUser(Number(id));
      return "Usuário deletado";
    },
  };
}
module.exports = { administrationController };
