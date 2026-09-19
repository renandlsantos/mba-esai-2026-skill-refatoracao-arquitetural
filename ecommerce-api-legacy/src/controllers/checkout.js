const { hashPassword, checkPassword } = require("../services/password");
const { DomainError } = require("../errors");
function validateCheckout(body) {
  if (!body || typeof body !== "object" || Array.isArray(body))
    throw new DomainError("Objeto JSON esperado");
  for (const key of ["usr", "eml", "pwd", "card"]) {
    if (
      typeof body[key] !== "string" ||
      !body[key].trim() ||
      body[key].length > 1024
    )
      throw new DomainError(`Campo inválido: ${key}`);
  }
  if (
    !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(body.eml) ||
    !Number.isSafeInteger(body.c_id) ||
    body.c_id < 1 ||
    !/^\d{13,19}$/.test(body.card)
  )
    throw new DomainError("Dados de checkout inválidos");
  return {
    name: body.usr.trim(),
    email: body.eml.trim().toLowerCase(),
    password: body.pwd,
    courseId: body.c_id,
    card: body.card,
  };
}
function checkoutController(repository, payment) {
  return async (body) => {
    const customer = validateCheckout(body);
    const enrollmentId = await repository.withTransaction(async (tx) => {
      const course = await tx.getCourse(customer.courseId);
      if (!course) throw new DomainError("Curso não encontrado", 404);
      let user = await tx.findUser(customer.email);
      if (user && !(await checkPassword(user.pass, customer.password)))
        throw new DomainError("Credenciais inválidas", 401);
      const status = await payment(customer.card);
      if (status !== "PAID") throw new DomainError("Pagamento recusado");
      if (!user)
        user = await tx.createUser(
          customer.name,
          customer.email,
          await hashPassword(customer.password),
        );
      const enrollment = await tx.enroll(user.id, course.id);
      await tx.recordPayment(enrollment.id, course.price, status);
      await tx.audit(`Checkout curso ${course.id} por ${user.id}`);
      return enrollment.id;
    });
    return { msg: "Sucesso", enrollment_id: enrollmentId };
  };
}
module.exports = { checkoutController };
