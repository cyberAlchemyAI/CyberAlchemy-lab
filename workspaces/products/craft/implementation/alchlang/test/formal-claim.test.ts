import assert from "node:assert/strict";
import test from "node:test";
import { parseFormalProposition, type FormalSignature } from "../src/formal-claim.js";
import { parseDomainSource } from "../src/parser.js";
import { compileCarrier } from "../src/index.js";

const signature = (): FormalSignature => ({ sorts: [{ name: "Order" }], functions: [], constants: [],
  predicates: [{ name: "HasLine", parameter_sorts: ["Order"] }, { name: "ValidTotal", parameter_sorts: ["Order"] }] });

test("typed universal proposition preserves conjunction and source-independent whitespace", () => {
  const proposition = "forall order: Order: HasLine(order) and ValidTotal(order)";
  const parsed = parseFormalProposition(proposition, signature());
  assert.deepEqual(parsed, parseFormalProposition(proposition.replaceAll(" ", "\n  "), signature()));
  assert.equal(parsed.kind, "forall");
  if (parsed.kind === "forall") { assert.equal(parsed.body.kind, "and"); assert.equal(parsed.sort, "Order"); }
});

test("functions constants and equality retain sort identity", () => {
  const s: FormalSignature = { sorts: [{ name: "Order" }, { name: "Amount" }],
    functions: [{ name: "Total", parameter_sorts: ["Order"], result_sort: "Amount" }],
    constants: [{ name: "Zero", sort: "Amount" }], predicates: [] };
  const parsed = parseFormalProposition("exists o: Order: Total(o) = Zero", s);
  assert.equal(parsed.kind, "exists");
  assert.throws(() => parseFormalProposition("exists o: Order: Total(o) = o", s), /FOL_SORT_MISMATCH/);
});

test("precedence and nested binders preserve meaning without implicit finite bounds", () => {
  const s = signature();
  const p = parseFormalProposition("forall o: Order: HasLine(o) implies exists p: Order: ValidTotal(p)", s);
  assert.equal(p.kind, "forall");
  if (p.kind === "forall" && p.body.kind === "implies") assert.equal(p.body.right.kind, "exists");
  else assert.fail("lost implication or quantifier");
  const q = parseFormalProposition("forall o: Order: not HasLine(o) or ValidTotal(o) and HasLine(o)", s);
  if (q.kind === "forall" && q.body.kind === "or") { assert.equal(q.body.left.kind, "not"); assert.equal(q.body.right.kind, "and"); }
  else assert.fail("wrong precedence");
});

test("semantic mutations reject with source-linked diagnostics", () => {
  const s = signature();
  for (const [source, code] of [
    ["forall o: Missing: HasLine(o) and ValidTotal(o)", "FOL_UNKNOWN_SORT"],
    ["forall o: Order: HasLine(x) and ValidTotal(o)", "FOL_UNBOUND_VARIABLE"],
    ["forall o: Order: HasLine(o, o) and ValidTotal(o)", "FOL_ARITY"],
    ["forall o: Order: Missing(o) and ValidTotal(o)", "FOL_UNKNOWN_SYMBOL"],
    ["forall o: Order: HasLine(o)", "FOL_UNUSED_SYMBOL"],
    ["forall o: Order: HasLine(o) and ValidTotal(o) rubbish", "FOL_SYNTAX"],
  ]) {
    assert.throws(() => parseFormalProposition(source!, s, "commerce.alch:9"), error => {
      assert.match(String(error), new RegExp(code!)); assert.match(String(error), /commerce.alch:9@/); return true;
    });
  }
  const duplicate = signature(); duplicate.sorts.push({ name: "Order" });
  assert.throws(() => parseFormalProposition("", duplicate), /FOL_DUPLICATE_SYMBOL/);
  const mismatch = signature(); mismatch.sorts.push({ name: "Customer" });
  assert.throws(() => parseFormalProposition("forall c: Customer: HasLine(c) and ValidTotal(c)", mismatch), /FOL_SORT_MISMATCH/);
});

const source = `domain commerce "Commerce"
profile application-v1
owner commerce
entity Order:
  orderId UInt64
  identity orderId
formal-claim EligibleClaim:
  profile fol-core/1-candidate
  sort Order
  predicate HasLine(Order)
  predicate ValidTotal(Order)
  proposition forall order: Order:
    HasLine(order) and ValidTotal(order)
  ceiling "Eligibility only."
rule EligibleOrder:
  claim EligibleClaim
`;

test("existing Alch parser produces typed claim declarations and Rule references", () => {
  const { carrier } = parseDomainSource(source);
  assert.equal(carrier.schema_version, "alchlang.application-source/v1-candidate");
  const claims = carrier.formal_claims as any[];
  assert.equal(claims[0].proposition.kind, "forall");
  assert.equal(claims[0].proposition.body.kind, "and");
  assert.equal((carrier.rules as any[])[0].claim_ref, "EligibleClaim");
  assert.equal((carrier.rules as any[])[0].condition, undefined);
  // Target syntax must never be silently evaluated through the legacy compiler.
  assert.throws(() => compileCarrier(carrier));
});

test("target declarations reject legacy fallback, duplicate propositions and missing claims", () => {
  assert.throws(() => parseDomainSource(source.replace("profile application-v1", "profile application-v1\nlogic sfol-v1")), /ALCH_PROFILE_CONFLICT/);
  assert.throws(() => parseDomainSource(source.replace("profile application-v1\n", "")), /ALCH_PROFILE_REQUIRED/);
  assert.throws(() => parseDomainSource(source.replace("claim EligibleClaim", "claim Missing")), /CLAIM_UNRESOLVED/);
  assert.throws(() => parseDomainSource(source.replace('  ceiling "Eligibility only."', '  proposition forall o: Order: HasLine(o) and ValidTotal(o)\n  ceiling "Eligibility only."')), /CLAIM_PROPOSITION_COUNT/);
  assert.throws(() => parseDomainSource(source + "  predicate total > 0\n"), /RULE_SECOND_CONDITION/);
});
