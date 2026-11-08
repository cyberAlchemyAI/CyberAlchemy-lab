/**
 * domainspec:
 *   concept:
 *     id: payment.MaxAmountRule
 *     type: Rule
 *     concern: biz
 *     spec_ref:
 *       path: docs/features/payments/SPEC.md
 *       line: 7
 *       section: Concept Registry
 *   edges:
 *     - edge: enforces
 *       to: payment.ProcessPayment
 */
export function maxAmountRule(amount: number, limit: number): boolean {
  return amount <= limit;
}

/**
 * domainspec:
 *   concept:
 *     id: payment.PaymentAPI
 *     type: Interface
 *     concern: sys
 *     spec_ref:
 *       path: docs/features/payments/SPEC.md
 *       line: 10
 *       section: Concept Registry
 *   edges:
 *     - edge: exposes
 *       to: payment.ProcessPayment
 */
export async function paymentApi(
  apiClient: { post: (path: string, body: unknown) => Promise<unknown> },
  payload: unknown,
) {
  return apiClient.post("/payments", payload);
}
