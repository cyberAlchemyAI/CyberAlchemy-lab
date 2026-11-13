import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";

import { runCli } from "../../src/cli/main.ts";
import { loadCompiledProjectGraph } from "../../src/input/project-model.ts";
import { deriveConstructionTestPlan } from "../../src/verification/test-derivation-plan.ts";
import { createCompleteL1Project } from "../helpers/l1-project.ts";

test("construction plan traces all active backend types and actual edges to checked source", () => {
  const fixture = createCompleteL1Project();
  try {
    const graph = loadCompiledProjectGraph(fixture.root);
    const plan = deriveConstructionTestPlan(graph);
    assert.equal(plan.catalog.active_backend_meta_types.length, 13);
    assert.equal(plan.catalog.backend_signatures.length, 17);
    assert.equal(plan.catalog.ui_candidate_signatures.length, 14);
    assert.equal(plan.counts.nodes, graph.nodes.length);
    assert.equal(plan.counts.relationships, graph.relationships.length);
    assert.equal(plan.cases.filter(({ family }) => family === "meta-type-formation").length, graph.nodes.length);
    assert.equal(plan.cases.filter(({ family }) => family === "relationship-consequence").length, graph.relationships.length);
    assert.deepEqual(new Set(plan.cases.filter(({ family }) => family === "meta-type-formation").map(({ definition_id }) => definition_id)), new Set(plan.catalog.active_backend_meta_types));
    assert.deepEqual(new Set(plan.cases.filter(({ family }) => family === "relationship-consequence").map(({ clause }) => clause)), new Set(plan.catalog.backend_signatures));
    for (const item of plan.cases) {
      const source = graph.source_manifest.sources.find(({ relative_path }) => relative_path === item.source_path);
      assert.equal(item.source_sha256, source?.sha256);
      assert.equal(item.disposition === "source-checked", item.family === "meta-type-formation");
    }
    assert.equal(plan.cases.some(({ disposition }) => disposition === "needs-oracle"), true);
  } finally { fs.rmSync(fixture.parent, { recursive: true, force: true }); }
});

test("one source change changes only that source's case identities", () => {
  const fixture = createCompleteL1Project();
  try {
    const before = deriveConstructionTestPlan(loadCompiledProjectGraph(fixture.root));
    const nodePath = path.join(fixture.root, "specs/alpha/nodes/customer.json");
    const node = JSON.parse(fs.readFileSync(nodePath, "utf8"));
    node.body.description += " Revised source wording.";
    fs.writeFileSync(nodePath, `${JSON.stringify(node, null, 2)}\n`);
    const after = deriveConstructionTestPlan(loadCompiledProjectGraph(fixture.root));
    const beforeOther = before.cases.filter(({ source_path }) => source_path !== "specs/alpha/nodes/customer.json").map(({ case_id }) => case_id);
    const afterOther = after.cases.filter(({ source_path }) => source_path !== "specs/alpha/nodes/customer.json").map(({ case_id }) => case_id);
    assert.deepEqual(afterOther, beforeOther);
    assert.notDeepEqual(after.cases.filter(({ source_path }) => source_path === "specs/alpha/nodes/customer.json").map(({ case_id }) => case_id), before.cases.filter(({ source_path }) => source_path === "specs/alpha/nodes/customer.json").map(({ case_id }) => case_id));
  } finally { fs.rmSync(fixture.parent, { recursive: true, force: true }); }
});

test("derive-tests CLI exposes the same read-only plan", () => {
  const fixture = createCompleteL1Project();
  try {
    const stdout: string[] = [], stderr: string[] = [];
    const expected = deriveConstructionTestPlan(loadCompiledProjectGraph(fixture.root));
    assert.equal(runCli(["derive-tests", fixture.root], { stdout: (value) => stdout.push(value), stderr: (value) => stderr.push(value) }), 0, stderr.at(-1));
    assert.deepEqual(JSON.parse(stdout.join("")), expected);
    const capabilities: string[] = [];
    assert.equal(runCli(["capabilities"], { stdout: (value) => capabilities.push(value), stderr: (value) => stderr.push(value) }), 0);
    const capabilityView = JSON.parse(capabilities.join(""));
    assert.equal(capabilityView.experimental_commands.includes("derive-tests"), true);
    assert.equal(capabilityView.test_derivation.executable_tests, false);
  } finally { fs.rmSync(fixture.parent, { recursive: true, force: true }); }
});
