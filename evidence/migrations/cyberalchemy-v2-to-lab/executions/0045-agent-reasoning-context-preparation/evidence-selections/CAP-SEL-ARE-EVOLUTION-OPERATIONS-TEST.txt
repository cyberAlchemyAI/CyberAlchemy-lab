import assert from "node:assert/strict";
import {mkdtempSync, rmSync} from "node:fs";
import {tmpdir} from "node:os";
import {resolve} from "node:path";
import test, {afterEach} from "node:test";

import {
  applyUpgradeDecision,
  createEvolutionScheduler,
  createServingVersionStore,
  createUpgradeDecision,
  createVariantWorkspaceFactory,
} from "../index.mjs";

const temporary = [];
afterEach(() => {
  for (const path of temporary.splice(0)) rmSync(path, {recursive: true, force: true});
});

function temp(name) {
  const path = mkdtempSync(resolve(tmpdir(), `${name}-`));
  temporary.push(path);
  return path;
}

function fakeGit(statusText = "") {
  const calls = [];
  const runner = ({cwd, args}) => {
    calls.push({cwd, args});
    if (args[0] === "status") return {status: 0, stdout: statusText, stderr: ""};
    if (args[0] === "rev-parse") return {status: 0, stdout: `${"a".repeat(40)}\n`, stderr: ""};
    if (args[0] === "diff") return {status: 0, stdout: "fixture diff", stderr: ""};
    return {status: 0, stdout: "", stderr: ""};
  };
  return {calls, runner};
}

test("variant workspace is content-addressed, outside the repository, and single-writer", () => {
  const repository = temp("evolution-repo");
  const workspaces = temp("evolution-workspaces");
  const git = fakeGit(" M packages/context/index.mjs\n");
  const factory = createVariantWorkspaceFactory({repository_root: repository, workspace_root: workspaces, command_runner: git.runner});
  const prepared = factory.prepare({baseline_ref: "git:abc", target_ref: "target:precision", technique_refs: ["technique:one"], mutation_allowlist: ["packages/context"]});
  assert.equal(prepared.ok, true);
  assert.match(prepared.workspace_id, /^variant-[a-f0-9]{24}$/);
  assert.equal(factory.prepare({baseline_ref: "git:abc", target_ref: "target:other", mutation_allowlist: ["packages/context"]}).disposition, "busy");
  const finalized = factory.finalize();
  assert.equal(finalized.ok, true);
  assert.equal(finalized.source_tree_digest.length, 64);
  assert.deepEqual(finalized.changed_paths, ["packages/context/index.mjs"]);
  assert.equal(factory.release().disposition, "released");
});

test("variant workspace blocks changes outside the exact mutation allowlist", () => {
  const repository = temp("evolution-repo");
  const workspaces = temp("evolution-workspaces");
  const git = fakeGit(" M packages/context/index.mjs\n?? private/secret.txt\n");
  const factory = createVariantWorkspaceFactory({repository_root: repository, workspace_root: workspaces, command_runner: git.runner});
  factory.prepare({baseline_ref: "git:abc", target_ref: "target:precision", mutation_allowlist: ["packages/context"]});
  const assessment = factory.finalize();
  assert.equal(assessment.ok, false);
  assert.deepEqual(assessment.violations, ["private/secret.txt"]);
  factory.release();
});

test("variant workspace rejects repository ancestors as overly broad roots", () => {
  const broad = temp("evolution-broad");
  const repository = resolve(broad, "repository");
  assert.throws(() => createVariantWorkspaceFactory({repository_root: repository, workspace_root: broad, command_runner: fakeGit().runner}), /dedicated directory/);
});

test("recommend-only upgrade decision never changes the serving pointer", async () => {
  const root = temp("evolution-serving");
  const store = createServingVersionStore({path: resolve(root, "serving.json")});
  store.write({version_ref: "serving:v1"});
  let calls = 0;
  const decision = createUpgradeDecision({current_version_ref: "serving:v1", candidate_version_ref: "variant:v2", comparison_ref: "comparison:one", comparison_outcome: "KEEP", required_keep_streak_met: true, reproduction_passed: true, holdout_passed: true, mode: "recommend-only"});
  const result = await applyUpgradeDecision({decision, store, canary: async () => { calls += 1; return {ok: true}; }});
  assert.equal(result.disposition, "no-change");
  assert.equal(store.read().version_ref, "serving:v1");
  assert.equal(calls, 0);
});

test("controlled activation is atomic and rolls back after a failed canary", async () => {
  const root = temp("evolution-serving");
  const store = createServingVersionStore({path: resolve(root, "serving.json")});
  store.write({version_ref: "serving:v1"});
  const decision = createUpgradeDecision({current_version_ref: "serving:v1", candidate_version_ref: "variant:v2", comparison_ref: "comparison:one", comparison_outcome: "KEEP", required_keep_streak_met: true, reproduction_passed: true, holdout_passed: true, mode: "controlled-local", activation_enabled: true, canary_policy_ref: "canary:fixture"});
  const result = await applyUpgradeDecision({decision, store, canary: async () => ({ok: false})});
  assert.equal(result.disposition, "rolled-back");
  assert.equal(result.canary_calls, 1);
  assert.equal(store.read().version_ref, "serving:v1");
});

test("upgrade controller rejects a mutated decision before touching the store", async () => {
  const root = temp("evolution-serving");
  const store = createServingVersionStore({path: resolve(root, "serving.json")});
  store.write({version_ref: "serving:v1"});
  const decision = createUpgradeDecision({current_version_ref: "serving:v1", candidate_version_ref: "variant:v2", comparison_ref: "comparison:one", comparison_outcome: "KEEP", required_keep_streak_met: true, reproduction_passed: true, holdout_passed: true, mode: "controlled-local", activation_enabled: true});
  await assert.rejects(() => applyUpgradeDecision({decision: {...decision, candidate_version_ref: "variant:tampered"}, store, canary: async () => ({ok: true})}), /digest is invalid/);
  assert.equal(store.read().version_ref, "serving:v1");
});

test("scheduler serializes cycles and replays a completed trigger exactly once", async () => {
  let release;
  let calls = 0;
  const blocked = new Promise((resolvePromise) => { release = resolvePromise; });
  const scheduler = createEvolutionScheduler({run_cycle: async ({trigger_id}) => { calls += 1; await blocked; return {trigger_id, status: "done"}; }});
  const first = scheduler.runOnce({trigger_id: "benchmark:one"});
  assert.equal((await scheduler.runOnce({trigger_id: "benchmark:two"})).disposition, "busy");
  release();
  assert.equal((await first).disposition, "completed");
  const replay = await scheduler.runOnce({trigger_id: "benchmark:one"});
  assert.equal(replay.disposition, "replayed");
  assert.equal(calls, 1);
});
