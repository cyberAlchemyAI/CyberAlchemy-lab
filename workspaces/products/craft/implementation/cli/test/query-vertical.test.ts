import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { spawnSync } from "node:child_process";
import test from "node:test";
import { pathToFileURL } from "node:url";

import { runCli } from "../src/cli/main.ts";
import { planInstantiation } from "../src/generation/plan-instantiation.ts";
import { loadCompiledProjectGraph, loadProjectNode, validateCompiledProjectGraphObligations } from "../src/input/project-model.ts";
import { checkoutRoot } from "./helpers/local-toolchain.ts";

const trustedInputSource = path.join(checkoutRoot, "auth-foundation/implementation/trusted-input-source");
const originalQueryPath = "specs/trusted-input-resolution/nodes/resolve-trusted-inputs.json";

function fixture(): { readonly parent: string; readonly root: string } {
  const parent = fs.mkdtempSync(path.join(os.tmpdir(), "domainspec-query-"));
  const root = path.join(parent, "source");
  fs.cpSync(trustedInputSource, root, { recursive: true });
  return { parent, root };
}

function snapshot(root: string): string {
  const rows: string[] = [];
  const visit = (relative: string): void => {
    for (const entry of fs.readdirSync(path.join(root, relative), { withFileTypes: true }).sort((left, right) => left.name.localeCompare(right.name))) {
      const child = relative ? `${relative}/${entry.name}` : entry.name;
      if (entry.isDirectory()) visit(child);
      else rows.push(`${child}\0${fs.readFileSync(path.join(root, child), "hex")}`);
    }
  };
  visit("");
  return rows.join("\n");
}

function queryContract(root: string): Record<string, unknown> {
  const original = JSON.parse(fs.readFileSync(path.join(root, originalQueryPath), "utf8"));
  return { ...original.body.typed_contract, ontology_operation: "AUTH-TI-QUERY-RESOLVE-TRUSTED-INPUTS-COPY" };
}

function addQueryArgs(root: string, contract: Record<string, unknown> = queryContract(root), reads = "authentication-evidence,route-authorization-binding"): string[] {
  return [
    "add", "query", root,
    "--feature", "trusted-input-resolution",
    "--name", "resolve-trusted-inputs-copy",
    "--description", "Return the same complete provider-supplied snapshot through an independently authored Query.",
    "--reads", reads,
    "--typed-contract-json", JSON.stringify(contract),
  ];
}

test("add query atomically authors typed source and exact reads edges", () => {
  const left = fixture();
  const right = fixture();
  try {
    const manifests: string[] = [];
    for (const root of [left.root, right.root]) {
      const out: string[] = [];
      const errors: string[] = [];
      assert.equal(runCli(addQueryArgs(root), { stdout: (value) => out.push(value), stderr: (value) => errors.push(value) }), 0, errors.at(-1));
      const receipt = JSON.parse(out.pop()!);
      assert.equal(receipt.schema_version, "domainspec.add-query-command-result/v1");
      assert.equal(receipt.selector, "trusted-input-resolution:resolve-trusted-inputs-copy");
      assert.equal(receipt.publication_protocol, "domainspec.atomic-authored-node/v1");
      assert.deepEqual(receipt.relationship_paths, [
        "specs/trusted-input-resolution/edges/resolve-trusted-inputs-copy-reads-authentication-evidence.json",
        "specs/trusted-input-resolution/edges/resolve-trusted-inputs-copy-reads-route-authorization-binding.json",
      ]);
      manifests.push(receipt.source_manifest_sha256);
      assert.deepEqual(errors, []);

      const graph = loadCompiledProjectGraph(root);
      const query = graph.nodes.find(({ selector }) => selector === receipt.selector)!;
      assert.equal(query.kind, "Query");
      assert.deepEqual(query.applicable_obligation_ids, [
        "reject_deprecated_queries_alias",
        "reject_non_entity_target",
        "reject_non_query_or_operation_source",
      ]);
      const witnesses = graph.obligation_witnesses.filter(({ witness }) => witness.source_selector === receipt.selector);
      assert.equal(witnesses.length, 6);
      assert.deepEqual(new Set(witnesses.map(({ family }) => family)), new Set(["deprecation", "endpoint"]));
      assert.throws(
        () => validateCompiledProjectGraphObligations({ ...graph, obligation_witnesses: graph.obligation_witnesses.filter(({ witness_id }) => witness_id !== witnesses[0]!.witness_id) }),
        (error: unknown) => (error as { code?: string }).code === "MTCLI_COMPILED_OBLIGATION",
      );
    }
    assert.equal(manifests[0], manifests[1]);
    assert.equal(snapshot(left.root), snapshot(right.root));
  } finally {
    fs.rmSync(left.parent, { recursive: true, force: true });
    fs.rmSync(right.parent, { recursive: true, force: true });
  }
});

test("hostile add query input leaves the source byte-identical", () => {
  const candidate = fixture();
  try {
    const before = snapshot(candidate.root);
    const stateful = { ...queryContract(candidate.root), writes: ["trusted-input-resolution:authentication-evidence"] };
    const errors: string[] = [];
    assert.equal(runCli(addQueryArgs(candidate.root, stateful), { stdout: () => undefined, stderr: (value) => errors.push(value) }), 22);
    assert.equal(JSON.parse(errors.pop()!).code, "MTCLI_QUERY_READ_ONLY");
    assert.equal(snapshot(candidate.root), before);

    const missingRead = { ...queryContract(candidate.root), reads: ["trusted-input-resolution:missing-entity"] };
    assert.equal(runCli(addQueryArgs(candidate.root, missingRead, "missing-entity"), { stdout: () => undefined, stderr: (value) => errors.push(value) }), 22);
    assert.equal(JSON.parse(errors.pop()!).code, "MTCLI_RELATIONSHIP_ENDPOINT");
    assert.equal(snapshot(candidate.root), before);
  } finally {
    fs.rmSync(candidate.parent, { recursive: true, force: true });
  }
});

test("Query authored semantics causally change closure and every binding", () => {
  const candidate = fixture();
  try {
    const before = loadProjectNode(candidate.root, "trusted-input-resolution:resolve-trusted-inputs");
    const beforePlans = (["typescript", "python", "rust"] as const).map((language) => planInstantiation(before, language));
    const rulePath = path.join(candidate.root, "specs/trusted-input-resolution/nodes/trusted-input-query-valid.json");
    const rule = JSON.parse(fs.readFileSync(rulePath, "utf8"));
    rule.body.typed_contract.expression.terms = rule.body.typed_contract.expression.terms.slice(0, 1);
    fs.writeFileSync(rulePath, `${JSON.stringify(rule, null, 2)}\n`);
    const after = loadProjectNode(candidate.root, "trusted-input-resolution:resolve-trusted-inputs");
    const afterPlans = (["typescript", "python", "rust"] as const).map((language) => planInstantiation(after, language));
    assert.notEqual(after.typed_closure!.closure_sha256, before.typed_closure!.closure_sha256);
    for (let index = 0; index < beforePlans.length; index += 1) {
      assert.notEqual(afterPlans[index]!.artifacts[0]!.sha256, beforePlans[index]!.artifacts[0]!.sha256);
      assert.match(afterPlans[index]!.artifacts[0]!.content, new RegExp(after.typed_closure!.closure_sha256));
    }
  } finally {
    fs.rmSync(candidate.parent, { recursive: true, force: true });
  }
});

test("TypeScript, Python, and Rust Query bindings execute one semantic corpus", async () => {
  const node = loadProjectNode(trustedInputSource, "trusted-input-resolution:resolve-trusted-inputs");
  const closureSha256 = node.typed_closure!.closure_sha256;
  const parent = fs.mkdtempSync(path.join(os.tmpdir(), "domainspec-query-native-"));
  const validQuery = { authentication_evidence_ref: "evidence-1", route_id: "route-1", decision_time: 1 };
  const invalidQuery = { ...validQuery, route_id: "" };
  const snapshotValue = { authentication_evidence: [], route_bindings: [] };
  try {
    const tsPath = path.join(parent, "resolve-trusted-inputs.ts");
    fs.writeFileSync(tsPath, planInstantiation(node, "typescript").artifacts[0]!.content);
    const ts = await import(`${pathToFileURL(tsPath).href}?query-native`);
    assert.equal(ts.DOMAINSPEC_QUERY_CLOSURE_SHA256, closureSha256);
    assert.deepEqual(ts.resolveTrustedInputs({ query: validQuery, snapshot: snapshotValue }), { variant: "Resolved", payload: snapshotValue });
    assert.deepEqual(ts.resolveTrustedInputs({ query: invalidQuery, snapshot: snapshotValue }), { variant: "Deny" });

    const pyPath = path.join(parent, "resolve_trusted_inputs.py");
    fs.writeFileSync(pyPath, planInstantiation(node, "python").artifacts[0]!.content);
    const pythonProgram = `import importlib.util,json\ns=importlib.util.spec_from_file_location('query',${JSON.stringify(pyPath)})\nm=importlib.util.module_from_spec(s)\ns.loader.exec_module(m)\nvalid=${JSON.stringify(validQuery)}\ninvalid=${JSON.stringify(invalidQuery)}\nsnapshot=${JSON.stringify(snapshotValue)}\nprint(m.DOMAINSPEC_QUERY_CLOSURE_SHA256)\nprint(json.dumps(m.resolve_trusted_inputs({'query':valid,'snapshot':snapshot}),sort_keys=True,separators=(',',':')))\nprint(json.dumps(m.resolve_trusted_inputs({'query':invalid,'snapshot':snapshot}),sort_keys=True,separators=(',',':')))`;
    const python = spawnSync("python3", ["-c", pythonProgram], { encoding: "utf8" });
    assert.equal(python.status, 0, python.stderr);
    assert.deepEqual(python.stdout.trim().split("\n"), [closureSha256, '{"payload":{"authentication_evidence":[],"route_bindings":[]},"variant":"Resolved"}', '{"variant":"Deny"}']);

    const rustPath = path.join(parent, "resolve_trusted_inputs.rs");
    fs.writeFileSync(rustPath, planInstantiation(node, "rust").artifacts[0]!.content);
    const harness = path.join(parent, "main.rs");
    fs.writeFileSync(harness, `mod generated { include!(${JSON.stringify(rustPath)}); }\nuse generated::*;\nfn label(value: TrustedInputResolution)->&'static str { match value { TrustedInputResolution::Resolved(_) => "Resolved", TrustedInputResolution::Deny => "Deny" } }\nfn main(){ let snapshot=TrustedInputSnapshot{authentication_evidence:vec![],route_bindings:vec![]}; let valid=TrustedInputQuery{authentication_evidence_ref:"evidence-1".to_owned(),route_id:"route-1".to_owned(),decision_time:1}; let invalid=TrustedInputQuery{route_id:"".to_owned(),..valid.clone()}; println!("{}",DOMAINSPEC_QUERY_CLOSURE_SHA256); println!("{}",label(resolve_trusted_inputs(&valid,&snapshot))); println!("{}",label(resolve_trusted_inputs(&invalid,&snapshot))); }\n`);
    const binary = path.join(parent, "query-bin");
    const compiled = spawnSync(process.env.DOMAINSPEC_RUSTC ?? "rustc", ["--edition", "2024", harness, "-o", binary], { encoding: "utf8" });
    assert.equal(compiled.status, 0, compiled.stderr ?? compiled.error?.message);
    const rust = spawnSync(binary, [], { encoding: "utf8" });
    assert.equal(rust.status, 0, rust.stderr);
    assert.deepEqual(rust.stdout.trim().split("\n"), [closureSha256, "Resolved", "Deny"]);
  } finally {
    fs.rmSync(parent, { recursive: true, force: true });
  }
});
