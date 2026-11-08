import { executableFixture } from "./application-executable-fixture.js";
import { lowerApplicationDomain } from "../../src/application-domain-lowering.js";
import { lowerApplicationRuleProjections } from "../../src/application-rule-projection.js";
import { digest, json } from "../../src/domainspec-profile.js";

export function realizationFixture() {
  const base = executableFixture();
  const source = base.source + `realization SubmitOrderExecution:
  operation SubmitOrder
  input request
  read current <- Order key request.id
  guard EligibleOrder(order <- current)
  write Order replace <- request
  result <- request
  atomicity state-and-outbox
  continuation awaited-settlement
`;
  const bindings = { ...base.bindings, source_sha256: digest(source), formal: { ...base.bindings.formal, source_sha256: digest(source) } };
  const formation = lowerApplicationDomain(source, bindings, base.sources);
  const interpretation = { ...base.interpretation, formation_sha256: digest(json(formation)) };
  const projection = lowerApplicationRuleProjections(source, bindings, base.sources, interpretation);
  const { operations, ...selection } = base.execution.selection;
  return { source, bindings, sources: base.sources, interpretation, projection,
    expectedOperations: operations,
    execution: { schema_version: "alchlang.application-execution/v2-candidate", projection_sha256: digest(json(projection)), selection } };
}
