import assert from "node:assert/strict";
import test from "node:test";
import { parseDomainSource } from "../src/parser.js";
import { parseApplicationType } from "../src/application-source.js";
import type { ApplicationFormalSource } from "../src/formal-claim.js";

const source = `domain commerce "Commerce"
profile application-v1
owner commerce
enum Currency:
  value USD "US dollar"
value-object Money:
  amount UInt64
  currency Currency
entity Order:
  id UInt64
  identity id
  total Money
  tags set<String>
  notes optional<list<String>>
event OrderSubmitted:
  orderId -> Order.id
  total Money
formal-claim EligibleClaim:
  profile fol-core/1-candidate
  sort Order
  predicate Eligible(Order)
  proposition forall o: Order: Eligible(o)
  ceiling "Submission eligibility only."
rule EligibleOrder:
  claim EligibleClaim
  enforces SubmitOrder
operation SubmitOrder:
  input Order
  output Order
  reads Order
  writes Order
  produces OrderSubmitted
  requires EligibleOrder
`;
const parse = (text = source) => parseDomainSource(text).carrier as unknown as ApplicationFormalSource;

test("application source preserves distinct data roles, nested fields and identity references", () => {
  const model = parse();
  assert.deepEqual(model.declarations.map(d => d.kind), ["enum", "value-object", "entity", "event", "operation"]);
  const entity = model.declarations.find(d => d.kind === "entity")!;
  assert.equal(entity.kind, "entity");
  if (entity.kind === "entity") {
    assert.equal(entity.identity, "id");
    assert.deepEqual(entity.fields[3]!.type, { kind: "optional", element: { kind: "list", element: { kind: "scalar", name: "String" } } });
  }
  const event = model.declarations.find(d => d.kind === "event")!;
  if (event.kind === "event") assert.deepEqual(event.fields[0]!.type, { kind: "reference", entity: "Order", field: "id" });
  const operation = model.declarations.find(d => d.kind === "operation")!;
  if (operation.kind === "operation") {
    assert.deepEqual(operation.requires, ["EligibleOrder"]);
    assert.deepEqual(operation.produces, ["OrderSubmitted"]);
  }
  assert.ok(model.declarations.every(d => !("rows" in d)));
});

test("unchecked declaration text cannot survive normalization", () => {
  for (const [before, after, code] of [
    ["amount UInt64", "amount Arbitrary", "APPLICATION_TYPE_REFERENCE"],
    ["identity id", "identity total", "APPLICATION_IDENTITY"],
    ["orderId -> Order.id", "orderId -> Order.total", "APPLICATION_IDENTITY_REFERENCE"],
    ["reads Order", "reads Money", "APPLICATION_REFERENCE"],
    ["produces OrderSubmitted", "produces Order", "APPLICATION_REFERENCE"],
    ["requires EligibleOrder", "requires EligibleClaim", "APPLICATION_REFERENCE"],
    ["output Order", "output Order\n  output Money", "APPLICATION_OPERATION"],
    ["writes Order", "run arbitraryCode()", "APPLICATION_OPERATION"],
    ["total Money", "total Money\n  total Money", "APPLICATION_FIELD"],
    ["value USD", "value USD\n  value USD", "APPLICATION_ENUM"],
  ]) assert.throws(() => parse(source.replace(before!, after!)), new RegExp(code!));
  assert.throws(() => parse(source + "query Unchecked:\n  anything at all\n"), /APPLICATION_QUERY/);
  assert.throws(() => parse(source + "domain other\n"), /APPLICATION_IDENTITY/);
  assert.throws(() => parse(source + "owner other\n"), /APPLICATION_IDENTITY/);
});

test("type syntax rejects trailing tokens, malformed nesting and unbounded nesting", () => {
  for (const text of ["list<String", "optional<>", "UInt64 garbage", "-> Order", "String; eval()", "set<String>>"]) {
    assert.throws(() => parseApplicationType(text, 12), /APPLICATION_TYPE.*line:12/);
  }
  assert.throws(() => parseApplicationType("list<".repeat(34) + "String" + ">".repeat(34), 12), /APPLICATION_TYPE_DEPTH/);
});
