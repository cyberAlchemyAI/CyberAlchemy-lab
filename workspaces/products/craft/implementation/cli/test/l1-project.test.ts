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
    assert.equal(graph.obligation_applicability.length, 28);
    assert.equal(graph.obligation_applicability.every(({ classification }) => classification === "applicable"), true);
    for (const obligation of graph.obligation_applicability.filter(({ classification }) => classification === "applicable")) {
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
    assert.equal(compiled.node_count, 17);
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
    assert.equal(receipt.node_selectors.length, 17);
    assert.equal(receipt.artifacts.length, 17);
    const receiptPath = path.join(target, ".domainspec/project-build.json");
    const schemas = path.resolve(path.dirname(new URL(import.meta.url).pathname), "../contracts");
    const schemaScript = [
      "import json,sys",
      "from jsonschema import Draft202012Validator",
      "from referencing import Registry,Resource",
      "certificate_schema=json.load(open(sys.argv[1]))",
      "receipt_schema=json.load(open(sys.argv[2]))",
      "value=json.load(open(sys.argv[3]))",
      "registry=Registry().with_resources([(certificate_schema['$id'],Resource.from_contents(certificate_schema)),(receipt_schema['$id'],Resource.from_contents(receipt_schema))])",
      "Draft202012Validator.check_schema(certificate_schema)",
      "Draft202012Validator.check_schema(receipt_schema)",
      "Draft202012Validator(certificate_schema,registry=registry).validate(value['compiled_certificate'])",
      "Draft202012Validator(receipt_schema,registry=registry).validate(value)",
    ].join("\n");
    const schemaCheck = spawnSync("python3", ["-c", schemaScript, path.join(schemas, "compiled-project-certificate.schema.json"), path.join(schemas, "project-build-receipt.schema.json"), receiptPath], { encoding: "utf8" });
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
