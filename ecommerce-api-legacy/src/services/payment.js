// Educational simulator only: no real card gateway, logging or persistence.
function simulatePayment(card) {
  return card.startsWith("4") ? "PAID" : "DENIED";
}
module.exports = { simulatePayment };
