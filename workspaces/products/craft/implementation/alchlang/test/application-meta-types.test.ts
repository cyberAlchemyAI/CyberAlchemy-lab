import assert from "node:assert/strict";
import { mkdirSync, mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import test from "node:test";
import { lowerApplicationDomain } from "../src/application-domain-lowering.js";
import { digest } from "../src/domainspec-profile.js";
import { loadDomainSpecCompiler } from "../src/domainspec-cli.js";
import { parseDomainSource } from "../src/parser.js";
import type { ApplicationFormalSource } from "../src/formal-claim.js";
import { formalLoweringFixture } from "./fixtures/formal-lowering-fixture.js";

function fixture() {
  const formal = formalLoweringFixture();
  const source = formal.source + `enum Status:
  value Pending
  value Submitted
value-object Money:
  amount UInt64
entity Order:
  id UInt64
  identity id
  parent -> Order.id
  note optional<String>
  labels list<String>
  tags set<String>
  status sum<Status>
  amount UInt64
event OrderSubmitted:
  event-type order-submitted
  version 1
  occurrence-id eventId String
  occurred-at generated
  orderId -> Order.id
operation SubmitOrder:
  input Order
  output Order
  reads Order
  writes Order
  produces OrderSubmitted
  requires EligibleOrder
operation ConfirmOrder:
  input Order
  output Order
  reads Order
  writes Order
  requires EligibleOrder
query FindOrders:
  input minimum UInt64
  source order Order
  output list<Order>
  where EligibleOrder
  bind order <- order
calculation Fee:
  input amount UInt64
  result UInt64
  expression add(amount, 5)
  rounding reject
mapping OrderToMoney:
  input order Order
  target Money
  total true
  field amount <- order.amount
policy DispatchOrder:
  input order Order
  case EligibleOrder -> Fee
  default SubmitOrder
workflow SubmitFlow:
  scope intra-feature
  steps SubmitOrder, ConfirmOrder
interface OrderApi:
  kind external
  version 1.0.0
  compatibility exact
  contract SubmitRequest:
    id UInt64
  contract OrderResult:
    status sum<Status>
  exposes SubmitOrder:
    request SubmitRequest
    result OrderResult
states OrderLifecycle:
  initial pending
  pending -> submitted when EligibleOrder emits OrderSubmitted
`;
  const property = (owner: string, name: string) => ({ ontology: `${owner}#${name}`, meaning: `Synthetic ${name}.` });
  const input = { schema_version: "alchlang.application-bindings/v1", source_sha256: digest(source), owner: "fixture-owner",
    formal: { ...formal.input, source_sha256: digest(source) }, declarations: {
      EligibleOrder: { ontology: "FIXTURE-ELIGIBILITY", meaning: "Synthetic eligibility Rule." },
      Status: { ontology: "FIXTURE-STATUS", meaning: "Synthetic order state values.", variants: { Pending: "FIXTURE-STATUS#Pending", Submitted: "FIXTURE-STATUS#Submitted" } },
      Money: { ontology: "FIXTURE-MONEY", meaning: "Synthetic money value.", invariants: ["EligibleOrder"], properties: { amount: property("FIXTURE-MONEY", "amount") } },
      Order: { ontology: "FIXTURE-ORDER", meaning: "Synthetic order Entity.", properties: Object.fromEntries(["id", "parent", "note", "labels", "tags", "status", "amount"].map(name => [name, property("FIXTURE-ORDER", name)])) },
      OrderSubmitted: { ontology: "FIXTURE-ORDER-SUBMITTED", meaning: "Synthetic submission Event." },
      SubmitOrder: { ontology: "FIXTURE-SUBMIT-ORDER", meaning: "Submit an order.", failure_continuation: "return-submit-error" },
      ConfirmOrder: { ontology: "FIXTURE-CONFIRM-ORDER", meaning: "Confirm an order.", failure_continuation: "return-confirm-error" },
      FindOrders: { ontology: "FIXTURE-FIND-ORDERS", meaning: "Find synthetic orders." },
      Fee: { ontology: "FIXTURE-FEE", meaning: "Calculate a synthetic fee." },
      OrderToMoney: { ontology: "FIXTURE-ORDER-TO-MONEY", meaning: "Project an order amount." },
      DispatchOrder: { ontology: "FIXTURE-DISPATCH-ORDER", meaning: "Select a declared order strategy." },
      SubmitFlow: { ontology: "FIXTURE-SUBMIT-FLOW", meaning: "Order two submission Operations." },
      OrderApi: { ontology: "FIXTURE-ORDER-API", meaning: "Synthetic external boundary.", contracts: {
        SubmitRequest: { ontology: "FIXTURE-SUBMIT-REQUEST", properties: { id: property("FIXTURE-SUBMIT-REQUEST", "id") } },
        OrderResult: { ontology: "FIXTURE-ORDER-RESULT", properties: { status: property("FIXTURE-ORDER-RESULT", "status") } },
      } },
      OrderLifecycle: { ontology: "FIXTURE-ORDER-LIFECYCLE", meaning: "Synthetic order lifecycle." },
    } };
  return { source, input, sources: formal.sources };
}

test("application-v1 authors and lowers all thirteen backend meta-types and every selected field constructor", async t => {
  const f = fixture();
  const model = parseDomainSource(f.source).carrier as unknown as ApplicationFormalSource;
  const kinds = new Set([...model.declarations.map(item => item.kind), ...model.rules.map(() => "rule")]);
  assert.deepEqual([...kinds].sort(), ["calculation", "entity", "enum", "event", "interface", "mapping", "operation", "policy", "query", "rule", "state-machine", "value-object", "workflow"]);
  const order = model.declarations.find(item => item.kind === "entity" && item.id === "Order");
  assert.ok(order && order.kind === "entity");
  assert.deepEqual(order.fields.map(field => field.type.kind), ["scalar", "reference", "optional", "list", "set", "sum", "scalar"]);

  const formed = lowerApplicationDomain(f.source, f.input, f.sources);
  const nodes = Object.entries(formed.projectFiles).filter(([relative]) => relative.includes("/nodes/")).map(([, bytes]) => JSON.parse(bytes));
  assert.deepEqual([...new Set(nodes.map(node => node.kind))].sort(), ["Calculation", "Entity", "Enum", "Event", "Interface", "Mapping", "Operation", "Policy", "Query", "Rule", "State Machine", "Value Object", "Workflow"]);
  const orderNode = nodes.find(node => node.node_id === "order");
  assert.deepEqual(orderNode.body.typed_contract.properties.map((field: any) => field.type.kind), ["scalar", "reference", "optional", "list", "set", "sum", "scalar"]);
  assert.deepEqual(orderNode.body.typed_contract.properties[5].type.variants.map((variant: any) => variant.name), ["Pending", "Submitted"]);
  assert.equal(nodes.find(node => node.node_id === "fee").body.typed_contract.schema_version, "domainspec.typed-calculation/v2");
  assert.equal(nodes.find(node => node.node_id === "order-lifecycle").body.transitions[0].guard_ref, "commerce:eligible-order");

  const compiler = await loadDomainSpecCompiler(); const root = mkdtempSync(path.join(tmpdir(), "alch-c02-meta-types-"));
  t.after(() => rmSync(root, { recursive: true, force: true }));
  for (const [relative, bytes] of Object.entries(formed.projectFiles)) { const target = path.join(root, relative); mkdirSync(path.dirname(target), { recursive: true }); writeFileSync(target, bytes); }
  const compiled = compiler.compileProject(root);
  assert.equal(new Set(compiled.graph.nodes.map(node => node.kind)).size, 13);
});

test("C02 distinctions reject collapsed references, constructors and meta-type targets", () => {
  const f = fixture();
  for (const [before, after, code] of [
    ["status sum<Status>", "status sum<Order>", "APPLICATION_SUM"],
    ["parent -> Order.id", "parent -> Order.amount", "APPLICATION_IDENTITY_REFERENCE"],
    ["steps SubmitOrder, ConfirmOrder", "steps SubmitOrder, Fee", "APPLICATION_REFERENCE"],
    ["case EligibleOrder -> Fee", "case EligibleOrder -> Order", "APPLICATION_REFERENCE"],
    ["pending -> submitted when EligibleOrder emits OrderSubmitted", "pending -> submitted when EligibleOrder emits Order", "APPLICATION_REFERENCE"],
    ["expression add(amount, 5)", "expression add(missing, 5)", "APPLICATION_CALCULATION"],
  ]) assert.throws(() => parseDomainSource(f.source.replace(before!, after!)), new RegExp(code!));
});
