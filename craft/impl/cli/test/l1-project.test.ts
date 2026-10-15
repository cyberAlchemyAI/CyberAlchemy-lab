import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { spawnSync } from "node:child_process";
import test from "node:test";

import { runCli } from "../src/cli/main.ts";
import { loadCompiledProjectGraph } from "../src/input/project-model.ts";
import { createCompleteL1Project } from "./helpers/l1-project.ts";

test("complete L1 corpus covers all 13 backend meta-types, 17 relationships, and applicable DS-D8 obligations", () => {
  const fixture = createCompleteL1Project();
  try {
    const graph = loadCompiledProjectGraph(fixture.root);
    assert.equal(new Set(graph.nodes.map(({ kind }) => kind)).size, 13);
    assert.equal(new Set(graph.relationships.map(({ relationship }) => relationship)).size, 17);
    assert.equal(graph.obligation_applicability.every(({ applicable }) => applicable), true);
    for (const obligation of graph.obligation_applicability) {
      assert.equal(graph.obligation_witnesses.some(({ obligation_id }) => obligation_id === obligation.obligation_id), true, obligation.obligation_id);
    }
  } finally { fs.rmSync(fixture.parent, { recursive: true, force: true }); }
});

test("compile certificate and whole-project builds are reproducible and source-sensitive", () => {
  const fixture = createCompleteL1Project();
  const outputParent = fs.mkdtempSync(path.join(os.tmpdir(), "domainspec-l1-output-"));
  const certificate = path.join(outputParent, "compiled.json");
  const target = path.join(outputParent, "generated-rust");
  try {
    const stdout: string[] = []; const stderr: string[] = [];
    assert.equal(runCli(["compile", fixture.root, "--target", certificate], { stdout: (value) => stdout.push(value), stderr: (value) => stderr.push(value) }), 0, stderr.at(-1));
    const compiled = JSON.parse(fs.readFileSync(certificate, "utf8"));
    assert.equal(compiled.node_count, 16);
    assert.equal(compiled.backend_type_ids.length, 13);
    assert.equal(compiled.backend_relationship_ids.length, 17);
    const certificateBytes = fs.readFileSync(certificate, "utf8");
    const compileErrors: string[] = [];
    assert.equal(runCli(["compile", fixture.root, "--target", certificate], { stdout: () => undefined, stderr: (value) => compileErrors.push(value) }), 22);
    assert.equal(JSON.parse(compileErrors.at(-1)!).code, "MTCLI_COMPILED_CERTIFICATE_EXISTS");
    assert.equal(fs.readFileSync(certificate, "utf8"), certificateBytes);
    for (const language of ["typescript", "python", "rust"] as const) {
      const languageTarget = path.join(outputParent, `generated-${language}`);
      assert.equal(runCli(["build", fixture.root, "--language", language, "--target-root", languageTarget], { stdout: (value) => stdout.push(value), stderr: (value) => stderr.push(value) }), 0, stderr.at(-1));
      assert.equal(runCli(["verify", fixture.root, "--language", language, "--target-root", languageTarget], { stdout: (value) => stdout.push(value), stderr: (value) => stderr.push(value) }), 0, stderr.at(-1));
    }
    const receipt = JSON.parse(fs.readFileSync(path.join(target, ".domainspec/project-build.json"), "utf8"));
    assert.equal(receipt.node_selectors.length, 16);
    assert.equal(receipt.artifacts.length, 16);
    const receiptPath = path.join(target, ".domainspec/project-build.json");
    const schemas = path.resolve(path.dirname(new URL(import.meta.url).pathname), "../contracts");
    const schemaCheck = spawnSync("python3", ["-c", "import json,sys\nfrom jsonschema import Draft202012Validator\nfrom referencing import Registry,Resource\nc=json.load(open(sys.argv[1]));r=json.load(open(sys.argv[2]));v=json.load(open(sys.argv[3]));Draft202012Validator(c).validate(v['compiled_certificate']);registry=Registry().with_resource(c['$id'],Resource.from_contents(c));Draft202012Validator(r,registry=registry).validate(v)", path.join(schemas, "compiled-project-certificate.schema.json"), path.join(schemas, "project-build-receipt.schema.json"), receiptPath], { encoding: "utf8" });
    assert.equal(schemaCheck.status, 0, schemaCheck.stderr);

    const generated = path.join(target, receipt.artifacts[0].relative_path);
    fs.appendFileSync(generated, "hostile drift");
    assert.equal(runCli(["verify", fixture.root, "--language", "rust", "--target-root", target], { stdout: (value) => stdout.push(value), stderr: (value) => stderr.push(value) }), 1);

    const source = path.join(fixture.root, "specs/alpha/nodes/total-cost.json");
    const node = JSON.parse(fs.readFileSync(source, "utf8"));
    node.body.typed_contract.division_rounding = "floor";
    fs.writeFileSync(source, `${JSON.stringify(node, null, 2)}\n`);
    const verification: string[] = [];
    assert.equal(runCli(["verify", fixture.root, "--language", "rust", "--target-root", target], { stdout: (value) => verification.push(value), stderr: (value) => verification.push(value) }), 1);
    assert.equal(JSON.parse(verification.at(-1)!).result, "fail");
  } finally { fs.rmSync(fixture.parent, { recursive: true, force: true }); fs.rmSync(outputParent, { recursive: true, force: true }); }
});

test("whole-project publication is fail-closed and leaves no partial target", () => {
  const fixture = createCompleteL1Project();
  const outputParent = fs.mkdtempSync(path.join(os.tmpdir(), "domainspec-l1-hostile-"));
  const target = path.join(outputParent, "generated");
  try {
    const edge = path.join(fixture.root, "specs/alpha/edges/settle-produces-settlement-requested.json");
    const value = JSON.parse(fs.readFileSync(edge, "utf8"));
    value.source_node_id = "customer";
    fs.writeFileSync(edge, `${JSON.stringify(value, null, 2)}\n`);
    const errors: string[] = [];
    assert.equal(runCli(["build", fixture.root, "--language", "rust", "--target-root", target], { stdout: () => undefined, stderr: (value) => errors.push(value) }), 22);
    assert.equal(JSON.parse(errors.at(-1)!).code, "MTCLI_RELATIONSHIP_ENDPOINT");
    assert.equal(fs.existsSync(target), false);
  } finally { fs.rmSync(fixture.parent, { recursive: true, force: true }); fs.rmSync(outputParent, { recursive: true, force: true }); }
});
