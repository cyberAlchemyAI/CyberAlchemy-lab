import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { spawnSync } from "node:child_process";
import test from "node:test";
import { fileURLToPath } from "node:url";

import { runCli } from "../../src/cli/main.ts";
import { CERTIFY_LEAN_TOOLCHAIN, certifyProject } from "../../src/assurance/certify.ts";
import { createCheckedInterchange, validateCheckedInterchange } from "../../src/assurance/checked-interchange.ts";
import { FORMALIZATION_LEAN_MODULE_FILENAMES } from "../../src/formalization/kernel.ts";
import { canonicalJson, sha256 } from "../../src/input/source-manifest.ts";
import { loadCompiledProjectGraph } from "../../src/input/project-model.ts";
import { createCompleteL1Project } from "../helpers/l1-project.ts";

const testDir = path.dirname(fileURLToPath(import.meta.url));
const cliRoot = path.resolve(testDir, "../..");
const fixtureRoot = path.resolve(cliRoot, "fixtures/input-roots/canonical-project");

function reseal(value: Record<string, unknown>): void {
  const { interchange_sha256: ignored, ...body } = value;
  value.interchange_sha256 = sha256(canonicalJson(body));
}

function resealCompiledCertificate(value: Record<string, unknown>): void {
  const certificate = value.compiled_certificate as Record<string, unknown>;
  const { certificate_sha256: ignored, ...body } = certificate;
  certificate.certificate_sha256 = sha256(canonicalJson(body));
}

function resealCompiledGraph(value: Record<string, unknown>): void {
  const certificate = value.compiled_certificate as Record<string, unknown>;
  const { project_root: ignored, ...semanticGraph } = value.compiled_graph as Record<string, unknown>;
  certificate.graph_sha256 = sha256(canonicalJson(semanticGraph));
  resealCompiledCertificate(value);
}

function resealFormalGraph(value: Record<string, unknown>): void {
  const payload = value.formalization_payload as Record<string, unknown>;
  const graph = payload.project_graph as Record<string, unknown>;
  const { graph_sha256: ignored, ...body } = graph;
  const graphSha256 = sha256(canonicalJson(body));
  graph.graph_sha256 = graphSha256;
  (payload.graph_certificate as Record<string, unknown>).graph_sha256 = graphSha256;
  (payload.typescript_projection as Record<string, unknown>).graph_sha256 = graphSha256;
}

test("certify publishes checked interchange, pinned Lean proof, and assurance certificate", () => {
  const parent = fs.mkdtempSync(path.join(os.tmpdir(), "domainspec-certify-"));
  const target = path.join(parent, "certificate");
  const output: string[] = [];
  const errors: string[] = [];
  try {
    assert.equal(runCli(["certify", fixtureRoot, "--target", target], { stdout: (value) => output.push(value), stderr: (value) => errors.push(value) }), 0, errors.join(""));
    const result = JSON.parse(output.at(-1)!);
    assert.equal(result.result, "pass");
    assert.equal(result.certificate.result, "pass");
    assert.equal(result.certificate.denominators.obligation_count, 45);
    assert.deepEqual(result.certificate.checks.map(({ check_id }: { check_id: string }) => check_id), ["compiled-certificate", "checked-interchange", "lean-interchange-decoder", "lean-proof-unit"]);
    assert.equal(result.certificate.toolchain.lean_toolchain, "leanprover/lean4:v4.33.1");
    assert.equal(result.certificate.claim_ceiling, "exact-finite-projection-and-proof-no-universal-compiler-runtime-or-authority-claim");
    assert.equal(result.certificate.authority_effect, "none");
    for (const relative of ["checked-interchange.json", "assurance-certificate.json", "proof/Current.lean", "proof/DomainSpecCheckedInterchangeDecoder.lean", "proof/DomainSpecMetaTypeKernel.lean", "proof/DomainSpecMetaTypeCompilerRefinement.lean", "proof/DomainSpecMetaTypeTypeScriptProjectionRefinement.lean"]) {
      assert.equal(fs.existsSync(path.join(target, relative)), true, relative);
    }
    const schemaCheck = spawnSync("python3", ["-c", [
      "import json,sys",
      "from jsonschema import Draft202012Validator",
      "for schema_path,value_path in ((sys.argv[1],sys.argv[3]),(sys.argv[2],sys.argv[4])):",
      " Draft202012Validator(json.load(open(schema_path))).validate(json.load(open(value_path)))",
    ].join("\n"), path.join(cliRoot, "contracts/checked-interchange.schema.json"), path.join(cliRoot, "contracts/assurance-certificate.schema.json"), path.join(target, "checked-interchange.json"), path.join(target, "assurance-certificate.json")], { encoding: "utf8" });
    assert.equal(schemaCheck.status, 0, schemaCheck.stderr);
    const decoder = path.join(target, "proof/DomainSpecCheckedInterchangeDecoder.lean");
    const proofDirectory = path.dirname(decoder);
    const leanEnvironment = { ...process.env, ELAN_TOOLCHAIN: CERTIFY_LEAN_TOOLCHAIN, LEAN_PATH: "." };
    const compiledObjects = FORMALIZATION_LEAN_MODULE_FILENAMES.map((filename) => {
      const objectName = filename.replace(/\.lean$/, ".olean");
      const compiled = spawnSync("lean", ["-o", objectName, filename], { cwd: proofDirectory, encoding: "utf8", env: leanEnvironment });
      assert.equal(compiled.status, 0, `${compiled.stdout}${compiled.stderr}`);
      return path.join(proofDirectory, objectName);
    });
    const validInterchange = JSON.parse(fs.readFileSync(path.join(target, "checked-interchange.json"), "utf8")) as Record<string, unknown>;
    const leanMutants: readonly [string, (candidate: Record<string, unknown>) => void, string][] = [
      ["missing-project", (candidate) => { delete candidate.project_id; }, "root:unexpected-or-missing-member"],
      ["duplicate-node", (candidate) => { const nodes = ((candidate.formalization_payload as Record<string, unknown>).project_graph as { nodes: Array<Record<string, unknown>> }).nodes; nodes[1]!.selector = nodes[0]!.selector; }, "nodes:duplicate:"],
      ["missing-witness", (candidate) => { ((candidate.formalization_payload as Record<string, unknown>).applicable_witnesses as unknown[]).pop(); }, "denominators:witness-count"],
      ["forged-graph", (candidate) => { ((candidate.formalization_payload as Record<string, unknown>).graph_certificate as Record<string, unknown>).graph_sha256 = "0".repeat(64); }, "graph_certificate:digest-mismatch"],
      ["missing-predicate-field", (candidate) => { const certificateWitness = (candidate.compiled_certificate as { obligation_witnesses: Array<{ predicate: Record<string, unknown> }> }).obligation_witnesses[0]!; const graphWitness = (candidate.compiled_graph as { obligation_witnesses: Array<{ predicate: Record<string, unknown> }> }).obligation_witnesses[0]!; delete certificateWitness.predicate.multiplicity; delete graphWitness.predicate.multiplicity; resealCompiledGraph(candidate); }, "detailed-witness:predicate:unexpected-or-missing-member"],
      ["unique-node-substitution", (candidate) => { const nodes = ((candidate.formalization_payload as Record<string, unknown>).project_graph as { nodes: Array<Record<string, unknown>> }).nodes; nodes[0]!.selector = "alpha:forged-customer"; resealFormalGraph(candidate); }, "node:selector-mismatch"],
      ["resealed-formal-typed-field-substitution", (candidate) => { const nodes = ((candidate.formalization_payload as Record<string, unknown>).project_graph as { nodes: Array<{ typed_field_ids: string[] }> }).nodes; nodes[0]!.typed_field_ids[0] = "forged-field"; resealFormalGraph(candidate); }, "compiled-projection:typed-field-ids:"],
      ["resealed-formal-graph-surplus", (candidate) => { const graph = (candidate.formalization_payload as { project_graph: Record<string, unknown> }).project_graph; graph.surplus = "forged"; resealFormalGraph(candidate); }, "project-graph:unexpected-or-missing-member"],
      ["resealed-formal-transition-surplus", (candidate) => { const nodes = ((candidate.formalization_payload as Record<string, unknown>).project_graph as { nodes: Array<{ state_machine_transitions: Array<Record<string, unknown>> }> }).nodes; const stateMachine = nodes.find(({ state_machine_transitions }) => state_machine_transitions.length > 0)!; stateMachine.state_machine_transitions[0]!.surplus = "forged"; resealFormalGraph(candidate); }, "state-machine-transition:unexpected-or-missing-member"],
      ["resealed-compiled-graph-digest", (candidate) => { (candidate.compiled_certificate as Record<string, unknown>).graph_sha256 = "0".repeat(64); resealCompiledCertificate(candidate); }, "compiled-graph:digest-mismatch"],
      ["resealed-predicate-substitution", (candidate) => { const certificateWitness = (candidate.compiled_certificate as { obligation_witnesses: Array<{ predicate: Record<string, unknown> }> }).obligation_witnesses[0]!; const graphWitness = (candidate.compiled_graph as { obligation_witnesses: Array<{ predicate: Record<string, unknown> }> }).obligation_witnesses[0]!; certificateWitness.predicate.multiplicity = "forged"; graphWitness.predicate.multiplicity = "forged"; resealCompiledGraph(candidate); }, "unknown-multiplicity:forged"],
      ["resealed-endpoint-substitution", (candidate) => { const certificateWitness = (candidate.compiled_certificate as { obligation_witnesses: Array<{ witness: Record<string, unknown> }> }).obligation_witnesses[0]!; const graphWitness = (candidate.compiled_graph as { obligation_witnesses: Array<{ witness: Record<string, unknown> }> }).obligation_witnesses[0]!; certificateWitness.witness.source_selector = "forged:selector"; graphWitness.witness.source_selector = "forged:selector"; resealCompiledGraph(candidate); }, "detailed-witness:source-selector-mismatch"],
    ];
    for (const [name, mutate, expectedError] of leanMutants) {
      const candidate = structuredClone(validInterchange);
      mutate(candidate);
      reseal(candidate);
      const mutantPath = path.join(parent, `${name}.json`);
      fs.writeFileSync(mutantPath, `${JSON.stringify(candidate)}\n`);
      const decoded = spawnSync("lean", ["--run", path.basename(decoder), mutantPath], { cwd: proofDirectory, encoding: "utf8", env: leanEnvironment });
      assert.equal(decoded.status, 22, `${decoded.stdout}${decoded.stderr}`);
      assert.match(decoded.stderr, new RegExp(expectedError));
    }
    for (const objectPath of compiledObjects) fs.rmSync(objectPath, { force: true });
    assert.equal(runCli(["certify-check", fixtureRoot, "--target", target], { stdout: (value) => output.push(value), stderr: (value) => errors.push(value) }), 0, errors.at(-1));
    assert.equal(JSON.parse(output.at(-1)!).current, true);
    const interchangePath = path.join(target, "checked-interchange.json");
    const originalBytes = fs.readFileSync(interchangePath);
    fs.appendFileSync(interchangePath, " \n");
    assert.equal(runCli(["certify-check", fixtureRoot, "--target", target], { stdout: (value) => output.push(value), stderr: (value) => errors.push(value) }), 1);
    assert.equal(JSON.parse(output.at(-1)!).current, false);
    fs.writeFileSync(interchangePath, originalBytes);
    assert.equal(runCli(["certify", fixtureRoot, "--target", target], { stdout: () => undefined, stderr: (value) => errors.push(value) }), 22);
    assert.equal(JSON.parse(errors.at(-1)!).code, "MTCLI_CERTIFY_TARGET_EXISTS");
  } finally {
    fs.rmSync(parent, { recursive: true, force: true });
  }
});

test("certify covers the complete 13-type and 17-relationship backend corpus", () => {
  const fixture = createCompleteL1Project();
  const target = path.join(fixture.parent, "certified");
  try {
    const certificate = certifyProject(fixture.root, target);
    const interchange = JSON.parse(fs.readFileSync(path.join(target, "checked-interchange.json"), "utf8"));
    assert.equal(interchange.compiled_certificate.backend_type_ids.length, 13);
    assert.equal(interchange.compiled_certificate.backend_relationship_ids.length, 17);
    assert.equal(interchange.denominators.obligation_count, 45);
    assert.equal(certificate.denominators.node_count, 16);
    assert.equal(certificate.denominators.edge_count, 19);
    assert.equal(certificate.checks.every(({ result }) => result === "pass"), true);
  } finally {
    fs.rmSync(fixture.parent, { recursive: true, force: true });
  }
});

test("checked interchange rejects omission and substitution even when the outer digest is refreshed", () => {
  const graph = loadCompiledProjectGraph(fixtureRoot);
  const original = createCheckedInterchange(graph);
  const mutations: readonly ((candidate: Record<string, unknown>) => void)[] = [
    (candidate) => { delete candidate.project_id; },
    (candidate) => { ((candidate.source_identity as Record<string, unknown>).source_bytes_sha256) = "0".repeat(64); },
    (candidate) => { ((candidate.denominators as Record<string, unknown>).node_count as number) += 1; },
    (candidate) => { ((candidate.formalization_payload as Record<string, unknown>).meta_types as unknown[]).pop(); },
    (candidate) => { ((candidate.formalization_payload as Record<string, unknown>).project_graph as { nodes: unknown[] }).nodes.pop(); },
    (candidate) => { ((candidate.formalization_payload as Record<string, unknown>).project_graph as { edges: unknown[] }).edges.pop(); },
    (candidate) => { ((candidate.formalization_payload as Record<string, unknown>).obligation_catalog as unknown[]).pop(); },
    (candidate) => { ((candidate.formalization_payload as Record<string, unknown>).applicable_witnesses as unknown[]).pop(); },
    (candidate) => { (((candidate.formalization_payload as Record<string, unknown>).graph_certificate as { graph_sha256: string }).graph_sha256) = "0".repeat(64); },
  ];
  for (const mutate of mutations) {
    const candidate = structuredClone(original) as unknown as Record<string, unknown>;
    mutate(candidate);
    if (Object.hasOwn(candidate, "interchange_sha256")) reseal(candidate);
    assert.throws(() => validateCheckedInterchange(candidate, graph), (error: unknown) => String((error as { code?: unknown }).code).startsWith("MTCLI_INTERCHANGE_"));
  }
});

test("legitimate source changes produce a different checked interchange and certificate", () => {
  const parent = fs.mkdtempSync(path.join(os.tmpdir(), "domainspec-certify-source-"));
  const source = path.join(parent, "source");
  fs.cpSync(fixtureRoot, source, { recursive: true });
  try {
    const before = createCheckedInterchange(loadCompiledProjectGraph(source));
    const nodePath = path.join(source, "specs/alpha/nodes/customer.json");
    const node = JSON.parse(fs.readFileSync(nodePath, "utf8"));
    node.body.description = "A source-sensitive certified customer.";
    fs.writeFileSync(nodePath, `${JSON.stringify(node, null, 2)}\n`);
    const after = createCheckedInterchange(loadCompiledProjectGraph(source));
    assert.notEqual(after.source_identity.source_bytes_sha256, before.source_identity.source_bytes_sha256);
    assert.notEqual(after.compiled_certificate.certificate_sha256, before.compiled_certificate.certificate_sha256);
    assert.notEqual(after.interchange_sha256, before.interchange_sha256);
  } finally {
    fs.rmSync(parent, { recursive: true, force: true });
  }
});
