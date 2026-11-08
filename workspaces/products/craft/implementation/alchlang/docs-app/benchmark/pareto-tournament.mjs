import { readFile, writeFile } from "node:fs/promises";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { paretoLayers, roundRobin } from "./pareto-core.mjs";

const benchmarkRoot = dirname(fileURLToPath(import.meta.url));
const runRoot = process.argv[2] ? resolve(process.argv[2]) : null;
if (!runRoot) throw new Error("Usage: node benchmark/pareto-tournament.mjs <frontend-run-directory> [human-observations.json]");

const config = JSON.parse(await readFile(join(benchmarkRoot, "config.json"), "utf8"));
const findings = JSON.parse(await readFile(join(runRoot, "findings.json"), "utf8"));
const bundle = JSON.parse(await readFile(join(runRoot, "measurements", "bundle.json"), "utf8"));
const humanPath = process.argv[3]
  ? resolve(process.argv[3])
  : join(benchmarkRoot, "human-observations.example.json");
const human = JSON.parse(await readFile(humanPath, "utf8"));

const globalBlockers = findings.findings.filter((finding) => finding.class === "hard_gate" && !finding.variant);
const candidates = [];
for (const variant of config.variants) {
  const variantBlockers = findings.findings.filter((finding) => finding.class === "hard_gate" && finding.variant === variant.id);
  const mobile = JSON.parse(await readFile(join(runRoot, "measurements", `${variant.id}-tutorial-workspace-mobile.json`), "utf8"));
  const desktop = JSON.parse(await readFile(join(runRoot, "measurements", `${variant.id}-tutorial-workspace-desktop.json`), "utf8"));
  const browserValues = {
    tutorial_mobile_viewport_pages: mobile.viewport_pages,
    tutorial_desktop_viewport_pages: desktop.viewport_pages,
  };
  const humanValues = human.variants?.[variant.id] || {};
  const missingHuman = config.pareto.human_objectives
    .map((objective) => objective.id)
    .filter((id) => !Number.isFinite(humanValues[id]));
  candidates.push({
    id: variant.id,
    treatment: variant.treatment,
    eligible: globalBlockers.length === 0 && variantBlockers.length === 0,
    blockers: [...globalBlockers, ...variantBlockers].map((finding) => finding.id),
    browser_values: browserValues,
    human_values: humanValues,
    missing_human_objectives: missingHuman,
  });
}

const eligible = candidates.filter((candidate) => candidate.eligible);
const browserCandidates = eligible.map((candidate) => ({ id: candidate.id, values: candidate.browser_values }));
const browserLayers = paretoLayers(browserCandidates, config.pareto.browser_objectives);
const productObjectives = [...config.pareto.browser_objectives, ...config.pareto.human_objectives];
const productCandidates = eligible
  .filter((candidate) => candidate.missing_human_objectives.length === 0)
  .map((candidate) => ({ id: candidate.id, values: { ...candidate.browser_values, ...candidate.human_values } }));
const productLayers = productCandidates.length ? paretoLayers(productCandidates, productObjectives) : [];
const collectionPairings = roundRobin(eligible.map((candidate) => candidate.id));
const ineligible = candidates.filter((candidate) => !candidate.eligible).map((candidate) => candidate.id);
const notEvaluable = candidates.filter((candidate) => candidate.eligible && candidate.missing_human_objectives.length).map((candidate) => candidate.id);
const status = ineligible.length ? "block" : notEvaluable.length ? "awaiting_human_observations" : "evaluated";

const result = {
  schema_version: "alchlang-pareto-tournament-result/v1",
  status,
  candidate_sha256: bundle.candidate_sha256,
  candidates,
  browser_proxy_frontier: browserLayers[0] || [],
  browser_proxy_layers: browserLayers,
  product_frontier: productLayers[0] || [],
  product_layers: productLayers,
  ineligible,
  not_evaluable: notEvaluable,
  collection_pairings: collectionPairings,
  human_observations: humanPath,
  claim_ceiling: "Browser proxy frontier plus tournament mechanics only. Product selection requires declared human task, comprehension, coverage, and preference observations."
};

await writeFile(join(runRoot, "pareto-tournament.json"), `${JSON.stringify(result, null, 2)}\n`);
await writeFile(join(runRoot, "pareto-summary.md"), `# AlchLang Pareto tournament\n\n- Status: **${status.toUpperCase()}**\n- Candidate: \`${bundle.candidate_sha256}\`\n- Eligible variants: ${eligible.map((candidate) => candidate.id).join(", ") || "none"}\n- Browser-proxy frontier: ${result.browser_proxy_frontier.join(", ") || "none"}\n- Product frontier: ${result.product_frontier.join(", ") || "not evaluable"}\n- Human evidence pending: ${notEvaluable.join(", ") || "none"}\n- Collection pairings: ${collectionPairings.length}\n\n## Claim boundary\n\n${result.claim_ceiling}\n`);
console.log(JSON.stringify({ status, output: join(runRoot, "pareto-tournament.json"), browser_proxy_frontier: result.browser_proxy_frontier, product_frontier: result.product_frontier, pairings: collectionPairings.length }, null, 2));
if (status === "block") process.exitCode = 1;
