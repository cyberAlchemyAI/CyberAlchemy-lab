// Handwritten expectations. This target does not import the compiler, generator, or runtime interpreter.
export const independentRuntimeTarget = Object.freeze({
  target_id: "handwritten-settlement-reference-v1",
  expected_outputs: Object.freeze({
    query: Object.freeze([Object.freeze({ customer_id: "a", settlement_details: "A" })]),
    calculation: 6,
    mapping: Object.freeze({ customer_id: "a", settlement_details: "A", preferred_method: "standard" }),
    policy: "alpha:total-cost",
    rule: true,
    state: Object.freeze({ state: "settled", event: "beta:settlement-completed" }),
  }),
});
