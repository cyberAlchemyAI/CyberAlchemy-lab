// Run after building the CLI. Arguments: documentation root, new report path.
import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { spawnSync } from "node:child_process";
import { fileURLToPath, pathToFileURL } from "node:url";
import { loadProjectNode } from "../dist/input/project-model.js";
import { planInstantiation } from "../dist/generation/plan-instantiation.js";
import { observeTarget } from "../dist/conformance/observe-target.js";
import { runInMemoryProject } from "../dist/runtime/in-memory.js";
import { sha256 } from "../dist/input/source-manifest.js";

const cli = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const [documentationRoot, reportPath] = process.argv.slice(2);
assert.ok(documentationRoot && path.isAbsolute(documentationRoot));
assert.ok(reportPath && path.isAbsolute(reportPath));
assert.equal(fs.existsSync(reportPath), false, "refuse to replace an existing verification record");
const example = path.join(cli, "examples/capacity-classification");
const node = loadProjectNode(example, "capacity-decision:classify-capacity");
const samples = [4, 5, 6].map((requested) => ({ snapshot: { request_id: `R-${requested}`, requested_units: requested, available_units: 5 } }));
const expected = ["Accept", "Reject", "Reject"].map((variant) => ({ variant, payload: null }));
const runtime = samples.map((inputs, index) => {
  const request = { schema_version: "domainspec.runtime-invocation/v1", invocation_id: `calculation-verification-${index}`, provider: "in-memory-v1", steps: [{ step_id: "classification", selector: "capacity-decision:classify-capacity", input: { inputs } }] };
  const before = structuredClone(request);
  const receipt = runInMemoryProject(example, request);
  assert.deepEqual(receipt.outcomes[0].output, expected[index]);
  assert.deepEqual(request, before);
  return { requested: inputs.snapshot.requested_units, available: 5, output: receipt.outcomes[0].output, receipt_sha256: receipt.receipt_sha256, snapshot_unchanged: true };
});
const artifacts = {};
for (const language of ["typescript", "python", "rust"]) {
  const target = path.join(example, "generated", language);
  const plan = planInstantiation(node, language);
  for (const artifact of plan.artifacts) assert.equal(fs.readFileSync(path.join(target, artifact.relative_path), "utf8"), artifact.content);
  assert.equal(observeTarget(target).result, "pass");
  artifacts[language] = { source: path.join(target, plan.artifacts[0].relative_path), sha256: plan.artifacts[0].sha256, exact_observation: "pass" };
}
const ts = await import(pathToFileURL(artifacts.typescript.source).href);
const typescript = samples.map((inputs) => {
  const before = structuredClone(inputs);
  const value = ts.classifyCapacity(Object.freeze({ snapshot: Object.freeze({ ...inputs.snapshot }) }));
  assert.deepEqual(inputs, before);
  return value;
});
assert.deepEqual(typescript, expected);
const py = spawnSync(process.env.PYTHON ?? "python3", ["-B", "-c", `import copy,importlib.util,json\ns=importlib.util.spec_from_file_location('c',${JSON.stringify(artifacts.python.source)});m=importlib.util.module_from_spec(s);s.loader.exec_module(m)\noutputs=[]\nfor inputs in json.loads(${JSON.stringify(JSON.stringify(samples))}):\n before=copy.deepcopy(inputs);outputs.append(m.classify_capacity(inputs));assert inputs==before\nprint(json.dumps(outputs))`], { encoding: "utf8" });
assert.equal(py.status, 0, py.error?.message ?? py.stderr);
const python = JSON.parse(py.stdout); assert.deepEqual(python, expected);
const scratch = fs.mkdtempSync(path.join(os.tmpdir(), "calculation-documentation-"));
let rust;
try {
  const harness = path.join(scratch, "main.rs"); const binary = path.join(scratch, "verify");
  fs.writeFileSync(harness, `mod c { include!(${JSON.stringify(artifacts.rust.source)}); }\nfn main(){for requested in [4,5,6]{let snapshot=c::CapacitySnapshot{request_id:format!("R-{requested}"),requested_units:requested,available_units:5};let before=snapshot.clone();println!("{:?}",c::classify_capacity(&snapshot));assert_eq!(snapshot,before);}}`);
  const compiled = spawnSync(process.env.RUSTC ?? "rustc", ["--edition", "2024", harness, "-o", binary], { encoding: "utf8" });
  assert.equal(compiled.status, 0, compiled.error?.message ?? compiled.stderr);
  const executed = spawnSync(binary, [], { encoding: "utf8" });
  assert.equal(executed.status, 0, executed.error?.message ?? executed.stderr);
  rust = executed.stdout.trim().split("\n"); assert.deepEqual(rust, expected.map(({ variant }) => variant));
} finally { fs.rmSync(scratch, { recursive: true, force: true }); }

const paths = ["craft-documentation-proposal/craft-model.md", "craft-documentation-proposal/craft-model.html", "governance-lab-series/governance-lab-reference.html"];
const documents = Object.fromEntries(paths.map((relative) => [relative, fs.readFileSync(path.join(documentationRoot, relative), "utf8")]));
const markdown = documents[paths[0]];
for (const [index, inputs] of samples.entries()) assert.match(markdown, new RegExp(`\\| ${inputs.snapshot.requested_units} \\| 5 \\| ${index === 0 ? "True" : "False"} \\| ${expected[index].variant} \\|`));
const plain = (html) => html.replace(/<script\b[^>]*>[\s\S]*?<\/script>/gi, " ").replace(/<style\b[^>]*>[\s\S]*?<\/style>/gi, " ").replace(/<[^>]+>/g, " ").replace(/\s+/g, " ");
const craft = plain(documents[paths[1]]); const lab = plain(documents[paths[2]]);
for (const [index, inputs] of samples.entries()) assert.match(craft, new RegExp(`\\b${inputs.snapshot.requested_units} 5 ${index === 0 ? "True" : "False"} ${expected[index].variant}\\b`));
assert.match(markdown, /requested units are strictly less than the available units/);
assert.match(craft, /Calculation/); assert.match(craft, /Neither branch reserves capacity/);
assert.match(craft, /Existing.*v1.*Calculations retain their UInt64 arithmetic contract/);
assert.match(lab, /Requests for 5 or 6 slots return Reject because the condition is strictly less/);
assert.match(lab, /All three classifications leave the snapshot’s available capacity at 5/);
assert.match(lab, /separate reservation Operation would check current capacity and reduce it to 1/);
const report = {
  schema_version: "craft.calculation-behavior-and-documentation-check/v1", date: "2026-10-11", authority_effect: "none", result: "pass",
  selector: node.typed_closure.root_selector, source_manifest_sha256: node.source_manifest.manifest_sha256,
  closure_sha256: node.typed_closure.closure_sha256, runtime,
  native: { typescript, python, rust, snapshot_unchanged: true }, artifacts,
  documentation: paths.map((relative) => ({ document: relative, sha256: sha256(documents[relative]), behavior_agreement: "pass" })),
  limits: ["Selected capacity classifier and three boundary cases only; numeric regression coverage is recorded separately.", "Reservation, concurrent state changes and deployment are not implemented by this classifier."]
};
fs.mkdirSync(path.dirname(reportPath), { recursive: true });
fs.writeFileSync(reportPath, `${JSON.stringify(report, null, 2)}\n`, { flag: "wx" });
console.log(JSON.stringify({ result: report.result, runtime_cases: 3, generated_language_cases: 9, documentation_files: paths.length, report: reportPath }));
