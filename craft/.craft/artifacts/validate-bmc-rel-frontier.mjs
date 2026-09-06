import { createHash } from "node:crypto";
import { existsSync, readFileSync, readdirSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const artifactDir = dirname(fileURLToPath(import.meta.url));
const scopeRoot = resolve(artifactDir, "../..");
const bindingPath = resolve(artifactDir, "BMC-REL-FRONTIER-BINDING.json");
const ledgerPath = resolve(scopeRoot, ".craft/ledger.yml");
const viewPath = resolve(scopeRoot, "CRAFT.md");
const binding = JSON.parse(readFileSync(bindingPath, "utf8"));
const ledger = readFileSync(ledgerPath, "utf8");
const view = readFileSync(viewPath, "utf8");
let checks = 0;

function assert(condition, message) {
  checks += 1;
  if (!condition) throw new Error(message);
}

function sha256(path) {
  return createHash("sha256").update(readFileSync(path)).digest("hex");
}

function readBoundJson(ref) {
  const path = resolve(scopeRoot, ref.path);
  assert(existsSync(path), `missing bound artifact: ${ref.path}`);
  assert(sha256(path) === ref.sha256, `bound artifact digest drift: ${ref.path}`);
  return JSON.parse(readFileSync(path, "utf8"));
}

function rowBlock(text, marker, nextMarker) {
  const start = text.indexOf(marker);
  assert(start >= 0, `missing row marker: ${marker}`);
  const end = text.indexOf(nextMarker, start + marker.length);
  return text.slice(start, end < 0 ? text.length : end);
}

function indexBlock(text, marker, nextMarker) {
  const start = text.indexOf(marker);
  assert(start >= 0, `missing index marker: ${marker}`);
  const end = text.indexOf(nextMarker, start + marker.length);
  assert(end > start, `missing index terminator: ${nextMarker}`);
  return text.slice(start, end);
}

function walkDirectories(root, visit) {
  for (const entry of readdirSync(root, { withFileTypes: true })) {
    if (!entry.isDirectory()) continue;
    const path = resolve(root, entry.name);
    visit(entry.name, path);
    walkDirectories(path, visit);
  }
}

function walkFiles(root, visit) {
  for (const entry of readdirSync(root, { withFileTypes: true })) {
    const path = resolve(root, entry.name);
    if (entry.isDirectory()) walkFiles(path, visit);
    else if (entry.isFile()) visit(entry.name, path);
  }
}

assert(binding.schema_version === "domainspec.craft-frontier-binding/v1", "binding schema drift");
assert(binding.context_id === "CTX-DSV2-BMC-REL", "binding context drift");
assert(binding.current_frontier.status === "block", "frontier must remain fail-closed");
assert(binding.authority_effect === "none", "binding authority must remain none");

const n05 = readBoundJson(binding.closed_decision.receipt);
assert(
  n05.selection?.selected_option_id === binding.closed_decision.native_selected_option_id,
  "N05 owner selection drift",
);
assert(n05.authorization_boundary?.implementation_authorized === false, "N05 authority ceiling drift");

const evidence = Object.fromEntries(
  binding.evidence_chain.map((ref) => [ref.artifact_id, { ref, value: readBoundJson(ref) }]),
);
assert(
  evidence["ART-DSV2-BMC-REL-N45-CLOSEOUT"].value.status === "selected-plan-entry-handoff-ready",
  "N45 closeout drift",
);
assert(
  evidence["ART-DSV2-BMC-REL-EVF-CANDIDATE-STAGING"].value.readiness?.independent_review_status === "pending",
  "staging receipt lifecycle drift",
);
assert(
  evidence["ART-DSV2-BMC-REL-CANDIDATE-REVIEW"].value.result === "pass",
  "candidate-local review drift",
);
assert(
  evidence["ART-DSV2-BMC-REL-PREACCEPTANCE-DEFECT"].value.status === "block",
  "governance-defect receipt drift",
);
assert(
  evidence["ART-DSV2-BMC-REL-GOV-REPAIR-SELECTION"].value.selected_option_id ===
    "BMC-REL-GOV-02-A-EXPLICIT-POSTIMAGE-CONTENT-KIND",
  "governance repair selection drift",
);
assert(
  evidence["ART-DSV2-BMC-REL-GOV-REPAIR-APPLY"].value.result === "pass" &&
    evidence["ART-DSV2-BMC-REL-GOV-REPAIR-APPLY"].value.authority_effect === "governance-repair-only",
  "governance repair apply drift",
);

const bmcRoot = resolve(scopeRoot, "development/relationship-constraint-decisions/BMC-REL-001");
let maxContinuation = 0;
walkDirectories(bmcRoot, (name) => {
  const match = /^N(\d+)-/.exec(name);
  if (match) maxContinuation = Math.max(maxContinuation, Number(match[1]));
});
assert(
  maxContinuation === binding.current_frontier.latest_design_continuation,
  `unbound BMC-REL continuation N${maxContinuation}`,
);

const preacceptanceRoot = resolve(
  scopeRoot,
  "development/relationship-constraint-decisions/BMC-REL-001/sidecars/BMC-REL-CONSTRAINT-COMPLETION/design/continuations/N37-EMITS-TARGET-MAX-CLOSURE-PROOF-SHAPE/research/closure-evidence-ownership-r1/define/closure-evidence-contract-r1/plan/closure-evidence-chain-contract-r1/preacceptance",
);
let maxCandidate = 0;
for (const entry of readdirSync(preacceptanceRoot, { withFileTypes: true })) {
  const match = entry.isDirectory() ? /^candidate-v(\d+)$/.exec(entry.name) : null;
  if (match) maxCandidate = Math.max(maxCandidate, Number(match[1]));
}
assert(
  maxCandidate === binding.current_frontier.latest_candidate_version,
  `unbound BMC-REL candidate-v${maxCandidate}`,
);

const laterReceiptNames = [];
walkFiles(preacceptanceRoot, (name, path) => {
  if (/(CLOSURE-GRAPH|AGGREGATE-RECEIPT|PREACCEPTANCE-CLOSURE)/i.test(name)) {
    laterReceiptNames.push(path.slice(scopeRoot.length + 1));
  }
});
const activeRepairRoot = resolve(
  preacceptanceRoot,
  "../governance-defects/preacceptance-non-json-postimage-r1",
);
walkFiles(activeRepairRoot, (name, path) => {
  if (/REPAIR-REVIEW/i.test(name)) laterReceiptNames.push(path.slice(scopeRoot.length + 1));
});
assert(
  laterReceiptNames.length === 0,
  `new post-repair frontier evidence requires Craft recomposition: ${laterReceiptNames.join(", ")}`,
);

const openDecisions = indexBlock(ledger, "  open_decisions:", "  blocking_decisions:");
const blockingDecisions = indexBlock(ledger, "  blocking_decisions:", "  active_blockers:");
const activeBlockers = indexBlock(ledger, "  active_blockers:", "  active_gaps:");
assert(!openDecisions.includes("DEC-DSV2-BMC-REL-N05"), "closed N05 remains in open index");
assert(!blockingDecisions.includes("DEC-DSV2-BMC-REL-N05"), "closed N05 remains in blocking index");
assert(!activeBlockers.includes("BLK-DSV2-BMC-REL-N05"), "resolved N05 blocker remains active");
assert(
  activeBlockers.includes("BLK-DSV2-BMC-REL-PREACCEPTANCE-CLOSURE"),
  "current preacceptance blocker missing from active index",
);

const n05Decision = rowBlock(
  ledger,
  "  - decision_id: DEC-DSV2-BMC-REL-N05",
  "\n  - decision_id: DEC-DSV2-ORODI-OWNER-BINDING-AUTHORITY",
);
assert(n05Decision.includes("status: closed"), "N05 Craft decision is not closed");
assert(n05Decision.includes("selected_option: uniform-future-rule"), "N05 Craft selection drift");
assert(n05Decision.includes("ART-DSV2-BMC-REL-N05-SELECTION"), "N05 receipt is not linked");

const n05Blocker = rowBlock(
  ledger,
  "  - blocker_id: BLK-DSV2-BMC-REL-N05",
  "\n  - blocker_id: BLK-DSV2-BMC-REL-PREACCEPTANCE-CLOSURE",
);
assert(n05Blocker.includes("status: resolved"), "N05 Craft blocker is not resolved");
const currentBlocker = rowBlock(
  ledger,
  "  - blocker_id: BLK-DSV2-BMC-REL-PREACCEPTANCE-CLOSURE",
  "\n  - blocker_id: BLK-DSV2-PROOF-GATE01-BINDING",
);
assert(currentBlocker.includes("status: active"), "current Craft blocker is not active");
assert(currentBlocker.includes("post-repair independent review"), "current blocker omits post-repair review");

for (const ref of [binding.closed_decision.receipt, ...binding.evidence_chain]) {
  assert(ledger.includes(ref.path), `ledger artifact index missing: ${ref.path}`);
}
assert(ledger.includes("stage: preacceptance"), "BMC-REL context is not at preacceptance");
assert(ledger.includes(".craft/artifacts/BMC-REL-FRONTIER-BINDING.json"), "frontier binding not indexed");

const staleClaims = [
  "N05 is the current blocker",
  "blocked at owner decision N05",
  "stops at N05 because no owner selection",
  "No owner selection has been recorded",
];
for (const claim of staleClaims) {
  assert(!ledger.includes(claim), `stale ledger claim recurred: ${claim}`);
  assert(!view.includes(claim), `stale CRAFT.md claim recurred: ${claim}`);
}
assert(view.includes("BLK-DSV2-BMC-REL-PREACCEPTANCE-CLOSURE"), "human view omits current blocker");
assert(view.includes("post-repair independent review"), "human view omits current frontier");
assert(view.includes("DEC-DSV2-BMC-REL-N05` — `closed"), "human view does not close N05");

process.stdout.write(
  `${JSON.stringify({ status: "pass", context_id: binding.context_id, checks, authority_effect: "none" }, null, 2)}\n`,
);
