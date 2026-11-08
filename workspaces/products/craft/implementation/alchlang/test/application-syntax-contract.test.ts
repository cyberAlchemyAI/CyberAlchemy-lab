import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import path from "node:path";
import test from "node:test";
import { defaultDomainSpecPackageRoot } from "../src/domainspec-cli.js";
import { parseDomainSource } from "../src/parser.js";
import { parseFormalProposition, type FormalSignature } from "../src/formal-claim.js";
import { CompilationRejected } from "../src/model.js";

const contract = JSON.parse(readFileSync(path.resolve(defaultDomainSpecPackageRoot(), "../../development/authoring-to-runtime-v1/syntax-cases.json"), "utf8"));
const supported = new Set([...contract.positive, ...contract.negative].map((c: any) => c.id));
const claim = `formal-claim EligibleClaim:
  profile fol-core/1-candidate
  sort Order
  predicate Eligible(Order)
  proposition forall order: Order: Eligible(order)
  ceiling "Eligibility only."
rule EligibleOrder:
  claim EligibleClaim
`;
function dependencies(id: string): string {
  if (["policy-rule-reference", "inline-policy"].includes(id)) return claim + `entity Order:
  id UInt64
  identity id
operation SubmitOrder:
  input Order
  output Order
operation RejectOrder:
  input Order
  output Order
`;
  if (id === "state-trigger-guard") return claim + `entity Order:
  id UInt64
  identity id
event OrderPlaced:
  id UInt64
`;
  if (id === "invariant-claim") return claim;
  if (id === "operation-rule") return claim + `entity Order:
  id UInt64
  identity id
operation SubmitOrder:
  input Order
  output Order
`;
  if (id === "competing-invariant") return claim;
  return "";
}
function parseCase(c: any) {
  if (c.proposition) {
    const signature: FormalSignature = { sorts: c.signature.sorts.map((name: string) => ({ name })), functions: [], constants: [],
      predicates: c.signature.predicates.map((p: any) => ({ name: p.name, parameter_sorts: p.parameters })) };
    return parseFormalProposition(c.proposition, signature);
  }
  const profile = /^profile /m.test(c.source) ? "" : "profile application-v1\n";
  return parseDomainSource('domain contract "Contract"\nowner fixture-owner\n' + profile + dependencies(c.id) + c.source);
}

test("every versioned syntax obligation is assigned to the current application profile", () => {
  const ids = [...contract.positive, ...contract.negative].map(c => c.id);
  assert.equal(new Set(ids).size, ids.length);
  assert.deepEqual([...ids].sort(), [...supported].sort());
});
test("application-v1 consumes every positive and exact-diagnostic negative case", () => {
  for (const c of contract.positive.filter((c: any) => supported.has(c.id))) assert.doesNotThrow(() => parseCase(c), c.id);
  for (const c of contract.negative.filter((c: any) => supported.has(c.id))) {
    assert.throws(() => parseCase(c), (e: unknown) => e instanceof CompilationRejected && e.issues.some(i => i.code === c.expected), c.id);
  }
});
