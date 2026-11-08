import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";

/** Exercise the public AlchLang module supplied by the consumer's resolver. */
export async function runLegacyMembership({ alchModule }) {
  const source = `domain membership "Membership example"
owner membership-owner
logic sfol-v1
entity Sample:
  amount: integer required
`;
  const original = alchModule.parseDomainSource(source).carrier;
  const literal = (value_type, value) => ({ node: "literal", value_type, value });
  const make = (operator, operands) => {
    const carrier = structuredClone(original);
    carrier.rules.push({ rule_id: "MembershipRule", owner_route: carrier.owners[0].owner_route,
      condition: { operator, operands }, source_refs: ["example:membership"] });
    return carrier;
  };
  const observations = [];
  for (const [id, operator, operands, expected] of [
    ["string-contains-true", "contains", [literal("string", "abc"), literal("string", "b")], true],
    ["string-contains-false", "contains", [literal("string", "abc"), literal("string", "z")], false],
    ["list-contains-true", "contains", [literal("list", [1, 2]), literal("integer", 2)], true],
    ["list-contains-false", "contains", [literal("list", [1, 2]), literal("integer", 3)], false],
    ["list-in-true", "in", [literal("integer", 2), literal("list", [1, 2])], true],
    ["list-in-false", "in", [literal("integer", 3), literal("list", [1, 2])], false],
  ]) {
    const compiled = alchModule.compileCarrier(make(operator, operands));
    assert.equal(alchModule.evaluateRule(compiled.plan.model.rules[0], {}), expected);
    observations.push({ id, result: "pass" });
  }
  for (const [id, operator, operands] of [
    ["numeric-contains-rejects", "contains", [literal("integer", 7), literal("integer", 1)]],
    ["numeric-in-rejects", "in", [literal("integer", 1), literal("integer", 7)]],
    ["substring-coercion-rejects", "contains", [literal("string", "123"), literal("integer", 2)]],
    ["malformed-list-literal-rejects", "contains", [literal("list", 7), literal("integer", 1)]],
    ["malformed-string-literal-rejects", "contains", [literal("string", 123), literal("string", "2")]],
    ["malformed-substring-literal-rejects", "contains", [literal("string", "123"), literal("string", 2)]],
  ]) {
    assert.throws(() => alchModule.compileCarrier(make(operator, operands)), error =>
      error instanceof alchModule.CompilationRejected && error.issues.some(issue => issue.code === "TYPE_MISMATCH"));
    observations.push({ id, result: "pass" });
  }
  return { schema_version: "alchlang.membership-witness/v1-candidate", result: "pass",
    observations, cases: observations.length, authority_effect: "none", formal_proof: false };
}

/** Execute the actual compiled generated exports; no compiler source imports. */
export async function runDecisions({ generatedRoot, exampleRoot }) {
  const observations = [];
  const record = (id, fn) => { fn(); observations.push({ id, result: "pass" }); };
  const load = (role, name) => import(pathToFileURL(path.join(generatedRoot,
    "commerce-corpus/features/commerce/src", role === "queries" ? "application" : "domain", role, `${name}.js`)).href);
  const [{ ruleAllowed }, { rulePositive }, { calculateTotal }, { calculateProduct },
    { calculateQuotientReject }, { calculateQuotientFloor }, { calculateQuotientCeil },
    { queryFind }, { queryFindOptional }, { queryFindRankedAsc }, { queryFindRankedDesc },
    { policyChooseCalculation }] = await Promise.all([
      load("rules", "allowed"), load("rules", "positive"), load("calculations", "total"),
      load("calculations", "product"), load("calculations", "quotient-reject"),
      load("calculations", "quotient-floor"), load("calculations", "quotient-ceil"),
      load("queries", "find"), load("queries", "find-optional"),
      load("queries", "find-ranked-asc"), load("queries", "find-ranked-desc"),
      load("policies", "choose-calculation"),
    ]);
  const expectError = (fn, code) => assert.throws(fn, error => error instanceof Error && error.message === code);
  record("rule-true", () => assert.equal(ruleAllowed({ value: "99" }), true));
  record("rule-false", () => assert.equal(ruleAllowed({ value: "100" }), false));
  record("rule-positive-boundary", () => { assert.equal(rulePositive({ value: 0n }), false); assert.equal(rulePositive({ value: 1 }), true); });
  record("rule-wrong-type", () => expectError(() => ruleAllowed({ value: true }), "RULE_INPUT"));
  record("rule-missing-argument", () => expectError(() => ruleAllowed({}), "RULE_INPUT"));
  record("rule-extra-argument", () => expectError(() => ruleAllowed({ value: "1", unexpected: "2" }), "RULE_INPUT"));

  const input = (gross, adjustment) => ({ gross, adjustment });
  const max = (1n << 64n) - 1n;
  record("calculation-parameterized-subtraction", () => {
    assert.equal(calculateTotal(input("100", "7")), 93n);
    assert.equal(calculateTotal(input(12, 7n)), 5n);
  });
  record("calculation-above-number-safe-range", () => assert.equal(calculateTotal(input("9007199254740993", "1")), 9007199254740992n));
  record("calculation-full-width", () => assert.equal(calculateTotal(input(max, "0")), max));
  record("calculation-multiplication", () => assert.equal(calculateProduct(input("7", "6")), 42n));
  record("calculation-exact-division", () => assert.equal(calculateQuotientReject(input("42", "6")), 7n));
  record("calculation-floor-division", () => assert.equal(calculateQuotientFloor(input("7", "2")), 3n));
  record("calculation-ceil-division", () => assert.equal(calculateQuotientCeil(input("7", "2")), 4n));
  record("calculation-rounding-exact-remainder", () => {
    assert.equal(calculateQuotientFloor(input("8", "2")), 4n);
    assert.equal(calculateQuotientCeil(input("8", "2")), 4n);
  });
  record("calculation-large-division", () => {
    assert.equal(calculateQuotientFloor(input(max, "2")), 9223372036854775807n);
    assert.equal(calculateQuotientCeil(input(max, "2")), 9223372036854775808n);
  });
  record("calculation-division-zero-numerator-and-full-width", () => {
    for (const fn of [calculateQuotientReject, calculateQuotientFloor, calculateQuotientCeil]) {
      assert.equal(fn(input("0", "2")), 0n); assert.equal(fn(input(max, "1")), max);
    }
  });
  record("calculation-underflow", () => expectError(() => calculateTotal(input("0", "1")), "CALCULATION_UNDERFLOW"));
  record("calculation-overflow", () => expectError(() => calculateProduct(input(max, "2")), "CALCULATION_OVERFLOW"));
  record("calculation-inexact", () => expectError(() => calculateQuotientReject(input("7", "2")), "CALCULATION_INEXACT"));
  for (const [mode, fn] of [["reject", calculateQuotientReject], ["floor", calculateQuotientFloor], ["ceil", calculateQuotientCeil]]) {
    record(`calculation-zero-divisor-${mode}`, () => expectError(() => fn(input("7", "0")), "CALCULATION_DIVIDE_BY_ZERO"));
  }
  for (const [label, value] of [["unsafe-number", Number.MAX_SAFE_INTEGER + 1], ["negative", -1n], ["too-large", max + 1n], ["noncanonical", "01"], ["fraction", 1.5], ["bool", true]]) {
    record(`calculation-input-${label}`, () => expectError(() => calculateTotal(input(value, "0")), "CALCULATION_INPUT"));
  }
  record("calculation-input-not-mutated", () => {
    const parameters = Object.freeze(input("100", "7"));
    assert.equal(calculateTotal(parameters), 93n); assert.deepEqual(parameters, input("100", "7"));
  });
  // Addition comes from the already packaged independent billing feature.
  const billing = await import(pathToFileURL(path.join(generatedRoot,
    "commerce-corpus/features/billing/src/domain/calculations/total.js")).href);
  record("calculation-addition", () => assert.equal(billing.calculateTotal(input("7", "6")), 13n));
  record("calculation-addition-overflow", () => expectError(() => billing.calculateTotal(input(max, "1")), "CALCULATION_OVERFLOW"));

  const template = JSON.parse(fs.readFileSync(path.join(exampleRoot, "values.json"), "utf8")).order;
  const row = (id, customer) => ({ ...structuredClone(template), id: String(id), billing_customer_id: String(customer) });
  const rows = [row(3, 2), row(1, 2), row(4, 9), row(2, 1)];
  const snapshot = structuredClone(rows);
  const projection = (id, customer) => ({ id: BigInt(id), billing_customer_id: BigInt(customer) });
  record("query-list-zero", () => assert.deepEqual(queryFind([], {}), []));
  record("query-list-one", () => assert.deepEqual(queryFind([rows[0]], {}), [projection(3, 2)]));
  record("query-list-many", () => assert.deepEqual(queryFind(rows, {}), [projection(3, 2), projection(1, 2), projection(4, 9), projection(2, 1)]));
  record("query-optional-zero", () => assert.equal(queryFindOptional(rows, { min_id: "5" }), null));
  record("query-optional-one", () => assert.deepEqual(queryFindOptional(rows, { min_id: "4" }), projection(4, 9)));
  record("query-optional-many-rejects", () => expectError(() => queryFindOptional(rows, { min_id: "3" }), "QUERY_CARDINALITY"));
  record("query-filter-projection-limit-ascending", () => assert.deepEqual(queryFindRankedAsc(rows, { min_id: "1" }), [projection(2, 1), projection(3, 2)]));
  record("query-filter-projection-limit-descending", () => assert.deepEqual(queryFindRankedDesc(rows, { min_id: "1" }), [projection(4, 9), projection(3, 2)]));
  record("query-stable-ties-before-limit", () => assert.deepEqual(queryFindRankedAsc([row(3, 2), row(1, 2), row(4, 2)], { min_id: "1" }), [projection(3, 2), projection(1, 2)]));
  record("query-descending-stable-ties-before-limit", () => assert.deepEqual(queryFindRankedDesc([row(3, 2), row(1, 2), row(4, 2)], { min_id: "1" }), [projection(3, 2), projection(1, 2)]));
  record("query-ranked-zero-and-one", () => {
    assert.deepEqual(queryFindRankedAsc(rows, { min_id: "5" }), []);
    assert.deepEqual(queryFindRankedDesc(rows, { min_id: "4" }), [projection(4, 9)]);
  });
  record("query-exact-large-key-ordering", () => {
    const large = [row(1, "9007199254740993"), row(2, "9007199254740992")];
    assert.deepEqual(queryFindRankedAsc(large, { min_id: "1" }), [projection(2, "9007199254740992"), projection(1, "9007199254740993")]);
  });
  record("query-filter-excludes-rows", () => assert.deepEqual(queryFindRankedAsc(rows, { min_id: "3" }), [projection(3, 2), projection(4, 9)]));
  record("query-does-not-mutate-supplied-rows", () => assert.deepEqual(rows, snapshot));
  record("query-missing-input", () => expectError(() => queryFindOptional(rows, {}), "QUERY_INPUT"));
  record("query-wrong-parameter-type", () => expectError(() => queryFindOptional(rows, { min_id: true }), "QUERY_INPUT"));
  record("query-invalid-row", () => expectError(() => queryFind([{ ...rows[0], id: true }], {}), "QUERY_INPUT"));

  record("policy-first-case", () => assert.equal(policyChooseCalculation({ gate: "1", amount: "0" }), "commerce:total"));
  record("policy-later-case", () => assert.equal(policyChooseCalculation({ gate: "100", amount: "1" }), "commerce:product"));
  record("policy-overlap-first-wins", () => assert.equal(policyChooseCalculation({ gate: "1", amount: "1" }), "commerce:total"));
  record("policy-default", () => assert.equal(policyChooseCalculation({ gate: "100", amount: "0" }), "commerce:quotient-floor"));
  record("policy-missing-input", () => expectError(() => policyChooseCalculation({ gate: "1" }), "POLICY_INPUT"));
  record("policy-wrong-input", () => expectError(() => policyChooseCalculation({ gate: true, amount: "1" }), "POLICY_INPUT"));
  record("policy-selection-separate-from-invocation", () => {
    let invocations = 0;
    const targets = {
      "commerce:total": values => { invocations++; return calculateTotal(values); },
      "commerce:product": values => { invocations++; return calculateProduct(values); },
      "commerce:quotient-floor": values => { invocations++; return calculateQuotientFloor(values); },
    };
    const selected = policyChooseCalculation({ gate: "1", amount: "1" });
    assert.equal(invocations, 0); assert.equal(typeof selected, "string");
    assert.equal(targets[selected](input("100", "7")), 93n); assert.equal(invocations, 1);
    // Arithmetic errors happen only at the explicit invocation boundary.
    const overflowing = policyChooseCalculation({ gate: "100", amount: "1" });
    assert.equal(invocations, 1);
    expectError(() => targets[overflowing](input(max, "2")), "CALCULATION_OVERFLOW");
    assert.equal(invocations, 2);
    assert.equal(targets[overflowing](input("100", "7")), 700n);
    const fallback = policyChooseCalculation({ gate: "100", amount: "0" });
    assert.equal(invocations, 3);
    assert.equal(targets[fallback](input("100", "7")), 14n);
    assert.equal(invocations, 4);
  });
  return { schema_version: "domainspec.meta-type-decisions-witness/v1-candidate", result: "pass",
    profile: "domainspec.reconciled-typescript/v1-candidate", observations,
    cases: observations.length, authority_effect: "none", formal_proof: false };
}
