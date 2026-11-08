import { mkdir, writeFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";

import {
  acceptSagaProofFreshnessClaim,
  assertBehavioralObligations,
  buildFreshnessClaim,
  buildReadSet,
  buildToyRunResult,
  enumerateRuns,
  stableStringify,
  validateGraph,
} from "./saga-spec.ts";
import {
  currentFactsAfterStaleWaiver,
  orderFulfillmentSaga,
  readSetFacts,
} from "./order-fulfillment.fixture.ts";

const here = dirname(resolve(process.argv[1] ?? "projects/domainspec-v2/research/dcb-saga-correctness/toy-harness/run-toy.ts"));
const resultJsonPath = resolve(here, "../toy-run-result.json");
const resultMarkdownPath = resolve(here, "../toy-run-result.md");

function renderMarkdown(result: ReturnType<typeof buildToyRunResult>): string {
  const assertions = result.behavior.assertions
    .map((assertion) => `| ${assertion.id} | ${assertion.status} | ${assertion.detail} |`)
    .join("\n");
  const trace = result.trace
    .map((event, index) => {
      const evidence = event.evidence?.length ? ` (${event.evidence.join(", ")})` : "";
      return `${index + 1}. ${event.kind}: ${event.operation} -> ${event.outcome}${evidence}`;
    })
    .join("\n");
  const readSet = result.freshness.claim.readSet
    .map((entry) => `| ${entry.id} | ${entry.mechanism} | ${entry.marker.slice(0, 16)}... |`)
    .join("\n");

  return `# Toy Run Result: ${result.scenario}

Status: ${result.behavioral_witness === "pass" && result.freshness_claim === "rejected" ? "pass" : "flag"}
Witness kind: ${result.witness_kind}
Recommendation: ${result.recommendation}

## Summary

| Check | Result |
| --- | --- |
| Graph witness | ${result.graph_witness} |
| Behavioral witness | ${result.behavioral_witness} |
| Freshness claim | ${result.freshness_claim} |
| Command | ${result.command} |
| Deterministic fact mechanism | ${result.deterministic_fact_mechanism} |
| Non-rerunnable fact | ${result.non_rerunnable_fact} |

## Graph Residue

${result.graph_residue.map((item) => `- ${item}`).join("\n")}

## Bounded Trace

${trace}

## Behavioral Assertions

| Assertion | Result | Detail |
| --- | --- | --- |
${assertions}

## Read Set

| Fact | Mechanism | Marker |
| --- | --- | --- |
${readSet}

## Freshness Verdict

${result.freshness.result.status.toUpperCase()}: ${result.freshness.result.reason}

Stale fact: ${result.stale_fact}
Current fact: ${result.current_fact}

## Notes

${result.notes.map((note) => `- ${note}`).join("\n")}
`;
}

async function main(): Promise<void> {
  const graph = validateGraph(orderFulfillmentSaga);
  const run = enumerateRuns(orderFulfillmentSaga);
  const behavior = assertBehavioralObligations(orderFulfillmentSaga, run);
  const readSet = buildReadSet(readSetFacts);
  const claim = buildFreshnessClaim("order-fulfillment-saga-proof-c1", readSet);
  const freshnessResult = acceptSagaProofFreshnessClaim(
    claim,
    currentFactsAfterStaleWaiver,
  );
  const result = buildToyRunResult({
    spec: orderFulfillmentSaga,
    graph,
    behavior,
    claim,
    freshnessResult,
  });

  await mkdir(dirname(resultJsonPath), { recursive: true });
  await writeFile(resultJsonPath, `${stableStringify(result)}\n`, "utf8");
  await writeFile(resultMarkdownPath, renderMarkdown(result), "utf8");

  if (
    result.behavioral_witness !== "pass" ||
    result.freshness_claim !== "rejected" ||
    result.command !== "AcceptSagaProofFreshnessClaim"
  ) {
    throw new Error("Toy run did not satisfy required witness criteria.");
  }

  console.log(`Wrote ${resultJsonPath}`);
  console.log(`Wrote ${resultMarkdownPath}`);
}

main().catch((error: unknown) => {
  console.error(error);
  process.exitCode = 1;
});
