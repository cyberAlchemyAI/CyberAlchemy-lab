import assert from "node:assert/strict";
import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { spawnSync } from "node:child_process";
import test from "node:test";
import { defaultDomainSpecPackageRoot } from "../src/domainspec-cli.js";
import { FORMAL_IDENTITY_ALGORITHM_V3_BYTES } from "../src/formal-claim-lowering.js";
import { assertApplicationFormalClaimV2ProjectionCurrent, projectApplicationFormalClaimsToV2 } from "../src/formal-claim-v2-projection.js";
import { formalLoweringFixture, source } from "./fixtures/formal-lowering-fixture.js";

const repo = path.resolve(defaultDomainSpecPackageRoot(), "../../../../..");
const impl = "language/capabilities/alchlang/plans/general-compiler-v1/implementation";
const boundary = "craft/projects/domainspec-v2/development/authoring-to-runtime-v1";
const schemas = "craft/projects/domainspec-v2/formalization/schemas";
const evidence = `${boundary}/evidence/e02-formal-claim-projection`;
const qualificationPath = path.join(repo, evidence, "qualification.v3-candidate.json");
const sha = (bytes: string | Buffer) => crypto.createHash("sha256").update(bytes).digest("hex");
const fileSha = (file: string) => {
  const absolute = path.join(repo, file);
  assert.equal(fs.lstatSync(absolute).isFile(), true, `${file}: regular file required`);
  return sha(fs.readFileSync(absolute));
};
const bindingPaths = {
  projection_implementation: `${impl}/src/formal-claim-v2-projection.ts`,
  lowering_implementation: `${impl}/src/formal-claim-lowering.ts`,
  projection_test: `${impl}/test/formal-claim-v2-projection.test.ts`,
  lowering_test: `${impl}/test/formal-claim-lowering.test.ts`,
  qualification_test: `${impl}/test/formal-claim-e02-qualification.test.ts`,
  fixture: `${impl}/test/fixtures/formal-lowering-fixture.ts`,
  projection_schema: `${boundary}/formal-claim-v4-v2-projection.schema.json`,
  v2_target_schema: "craft/projects/domainspec-v2/development/spec-ontology-branch-decision/contracts/formal-claim-source-payload.v2.schema.json",
  v4_source_schema: `${schemas}/formal-claim-source-v4-candidate.schema.json`,
  preservation_schema: `${schemas}/preservation-binding.schema.json`,
  acceptance_decision_schema: `${schemas}/business-acceptance-decision.v1-candidate.schema.json`,
  business_meaning_v1_schema: `${schemas}/business-meaning.schema.json`,
  business_meaning_v2_schema: `${schemas}/business-meaning.v2-candidate.schema.json`,
  definition_binding_schema: `${schemas}/formal-claim-definition-binding.schema.json`,
  formal_profile_fixture_source: "craft/projects/domainspec-v2/formalization/profiles/formal-language-profiles.json",
  historical_acceptance_negative_fixture: "auth-foundation/formalization/decisions/AF-EXACT-SESSION-ROLE-PERMISSION-001/owner-semantic-decision.json",
  mapping_document: `${boundary}/FORMAL-CLAIM-V4-V2-PROJECTION.md`,
} as const;
const preservation = {
  semantic_loss_count: 0, representation_change_count: 5, meaning_repaired_or_invented: false,
  acceptance_and_interpretation_excluded_from_v3_claim_identity: true,
  acceptance_and_interpretation_changes_invalidate_projection_bytes: true,
};
const validation = {
  typecheck: "pass",
  focused_lowering_and_projection: { tests: 20, passed: 20, failed: 0, skipped: 0, cancelled: 0 },
  replay: { cases: 4, schema_validations: 16, status: "pass" },
  decision_and_interpretation_currentness: "pass",
  full_application_regression: "not-claimed; complete current-source regression and per-finding closure audit remain outstanding",
};
const limits = {
  formal_claim_admission: false, tde_evaluation: false, provider_execution: false,
  runtime_guarantees_observed: false, full_application_regression: false, product_approval: false,
  publication: false, deployment: false,
};
const claimCeiling = "Current E02 scoped compatibility evidence only; not a full application regression, FormalClaim admission, TDE evaluation, provider execution, runtime guarantee, product approval, publication, deployment, or authority.";
const openQuestions = [
  "E03/L3X still requires genuine selected execution evidence, not synthetic fixture success.",
  "Complete current-source regression, the per-finding closure audit and a final exact package successor remain outstanding.",
];

function keys(value: any, expected: string[], label: string): void {
  assert.ok(value && typeof value === "object" && !Array.isArray(value), label);
  assert.deepEqual(Object.keys(value).sort(), expected.sort(), label);
}

function exactRef(value: any, expected: string, label: string): void {
  keys(value, ["path", "sha256"], label);
  assert.equal(value.path, expected, `${label}: path`);
  assert.equal(value.sha256, fileSha(expected), `${label}: sha256`);
}

function rows(files: ReadonlyMap<string, Buffer> | Record<string, string>) {
  const entries = files instanceof Map ? [...files.entries()] : Object.entries(files);
  return entries.sort(([a], [b]) => a < b ? -1 : a > b ? 1 : 0).map(([file, bytes]) =>
    ({ path: file, sha256: sha(bytes), size_bytes: Buffer.byteLength(bytes) }));
}

function measureSourceInventory() {
  const root = `${impl}/src`;
  const paths: string[] = [];
  const visit = (relative: string) => {
    for (const entry of fs.readdirSync(path.join(repo, relative), { withFileTypes: true })) {
      const file = `${relative}/${entry.name}`;
      assert.equal(entry.isSymbolicLink(), false, `${file}: symlinks forbidden`);
      if (entry.isDirectory()) visit(file);
      else if (entry.name.endsWith(".ts")) {
        assert.equal(entry.isFile(), true, `${file}: regular source file required`);
        paths.push(file);
      }
    }
  };
  visit(root);
  const files = paths.sort().map(file => {
    const bytes = fs.readFileSync(path.join(repo, file));
    return { path: file, sha256: sha(bytes), size_bytes: bytes.length };
  });
  assert.ok(files.length > 0, "source inventory must not be empty");
  return { root, selection: "recursive regular *.ts; symlinks forbidden", file_count: files.length,
    manifest_sha256: sha(JSON.stringify(files)), files };
}

function measureReplay() {
  const schemasToCheck = [bindingPaths.v2_target_schema, bindingPaths.projection_schema,
    bindingPaths.preservation_schema, bindingPaths.v4_source_schema].map(file => path.join(repo, file));
  const observe = (id: string, fixture: ReturnType<typeof formalLoweringFixture>) => {
    const result = projectApplicationFormalClaimsToV2(source, fixture.input, fixture.sources);
    assertApplicationFormalClaimV2ProjectionCurrent(source, fixture.input, fixture.sources, result);
    assert.deepEqual(result, projectApplicationFormalClaimsToV2(source, structuredClone(fixture.input), fixture.sources), id);
    assert.equal(result.payloads.length, 1, id);
    const projection = result.projections[0] as any;
    assert.equal(projection.semantic_loss_count, 0, id);
    assert.equal(projection.representation_change_count, 5, id);
    assert.equal(projection.known_losses.length, 5, id);
    assert.equal(result.trace.meaning_repaired_or_invented, false, id);
    assert.equal(result.trace.provider_execution_observed, false, id);
    assert.equal(result.trace.authority_effect, "none", id);
    const values = [result.payloads[0], projection, result.preservation_bindings[0], result.attached_sources[0]];
    const check = spawnSync("python3", ["-c",
      "import json,sys,jsonschema; values=json.load(sys.stdin); assert len(values)==len(sys.argv[1:])==4; [(jsonschema.Draft202012Validator(json.load(open(s))).validate(v)) for v,s in zip(values,sys.argv[1:])]",
      ...schemasToCheck], { input: JSON.stringify(values), encoding: "utf8", timeout: 10000 });
    assert.equal(check.status, 0, `${id}: schema validation: ${check.stderr || String(check.error)}`);
    return { result, snapshot: { id, identity_algorithm_version: (result.payloads[0] as any).canonical_proposition.identity_algorithm.version,
      source_sha256: sha(source), input_sha256: sha(JSON.stringify(fixture.input)),
      fixture_source_files: rows(fixture.sources), formal_output_files: rows(result.formal.files),
      projection_output_files: rows(result.files), result_sha256: sha(JSON.stringify(result)) } };
  };
  const v1 = observe("v1-base", formalLoweringFixture());
  assert.equal(v1.snapshot.identity_algorithm_version, "1");

  const fixture = formalLoweringFixture();
  const originalRef = fixture.input.formal_claims.EligibleClaim.business_meaning_ref;
  const original = JSON.parse(fixture.sources.get(originalRef.path)!.toString());
  const meaning = { ...original, schema_version: "domainspec-v2.business-meaning/v2-candidate",
    supersedes: "Meaning:fixture@0", supersession_effect: "accepted-supersession",
    base_accepted_meaning_ref: originalRef, definition_source_ref: fixture.graph.definition_authority_ref,
    interpretation_model_ref: fixture.put("fixture/model.json", { model: "a" }),
    definition_policy: { canonical_location: "inline-in-this-business-meaning", normative_voice: "formal",
      explanatory_voices: ["plain_language", "domain_context"], conflict_rule: "formal-voice-prevails" },
    definitions: [fixture.definition] };
  fixture.input.formal_claims.EligibleClaim.business_acceptance_ref = fixture.acceptMeaning(meaning);
  fixture.input.formal_claims.EligibleClaim.business_meaning_ref = fixture.put("fixture/meaning-v2.json", meaning);
  fixture.input.formal_claims.EligibleClaim.identity_algorithm_ref = fixture.put("fixture/identity-v3.json", FORMAL_IDENTITY_ALGORITHM_V3_BYTES);
  const v3 = observe("v3-base", fixture);
  assert.equal(v3.snapshot.identity_algorithm_version, "3");
  fixture.input.formal_claims.EligibleClaim.business_acceptance_ref = fixture.acceptMeaning(meaning, "fixture/acceptance-reissued.json");
  fixture.input.formal_claims.EligibleClaim.business_meaning_ref = fixture.put("fixture/meaning-v2.json", meaning);
  assert.throws(() => assertApplicationFormalClaimV2ProjectionCurrent(source, fixture.input, fixture.sources, v3.result), /FORMAL_V2_PROJECTION_STALE/);
  const reissued = observe("v3-acceptance-reissued", fixture);
  meaning.interpretation_model_ref = fixture.put("fixture/model-b.json", { model: "b" });
  fixture.input.formal_claims.EligibleClaim.business_acceptance_ref = fixture.acceptMeaning(meaning);
  fixture.input.formal_claims.EligibleClaim.business_meaning_ref = fixture.put("fixture/meaning-v2.json", meaning);
  assert.throws(() => assertApplicationFormalClaimV2ProjectionCurrent(source, fixture.input, fixture.sources, reissued.result), /FORMAL_V2_PROJECTION_STALE/);
  const interpreted = observe("v3-interpretation-changed", fixture);
  for (const changed of [reissued, interpreted]) {
    assert.equal(changed.result.formal.claims[0]!.claim.identity_inputs_digest, v3.result.formal.claims[0]!.claim.identity_inputs_digest);
    assert.notEqual((changed.result.projections[0] as any).target_ref.sha256, (v3.result.projections[0] as any).target_ref.sha256);
  }
  return [v1.snapshot, v3.snapshot, reissued.snapshot, interpreted.snapshot];
}

function validate(value: any, measuredReplay: ReturnType<typeof measureReplay>, sourceInventory: ReturnType<typeof measureSourceInventory>): void {
  keys(value, ["schema_version", "date", "task", "result", "authority_effect", "supersedes_historical_qualification",
    "preserved_original_qualification", "inherited_boundary", "dag", "bindings", "source_inventory", "validation",
    "preservation", "replay", "limits", "claim_ceiling", "open_questions"], "qualification keys");
  assert.equal(value.schema_version, "alchlang.e02-formal-claim-projection-qualification/v3-candidate", "schema_version");
  assert.equal(value.date, "2026-10-07", "date");
  assert.equal(value.task, "E02", "task");
  assert.equal(value.result, "scoped-pass", "result");
  assert.equal(value.authority_effect, "none", "authority_effect");
  exactRef(value.supersedes_historical_qualification, `${evidence}/qualification.v2-candidate.json`, "predecessor");
  exactRef(value.preserved_original_qualification, `${evidence}/qualification.json`, "original qualification");
  exactRef(value.inherited_boundary, `${boundary}/E01-COMPLETION.md`, "inherited boundary");
  keys(value.dag, ["path", "sha256", "node"], "dag");
  assert.equal(value.dag.path, `${boundary}/EXECUTION-DAG.json`, "dag path");
  assert.equal(value.dag.sha256, fileSha(value.dag.path), "dag sha256");
  assert.equal(value.dag.node, "E02", "dag node");
  keys(value.bindings, Object.keys(bindingPaths), "binding keys");
  for (const [key, file] of Object.entries(bindingPaths)) exactRef(value.bindings[key], file, `binding ${key}`);
  assert.deepEqual(value.source_inventory, sourceInventory, "source inventory");
  assert.deepEqual(value.validation, validation, "validation");
  assert.deepEqual(value.preservation, preservation, "preservation");
  assert.deepEqual(value.replay, measuredReplay, "replay");
  assert.deepEqual(value.limits, limits, "limits");
  assert.equal(value.claim_ceiling, claimCeiling, "claim ceiling");
  assert.deepEqual(value.open_questions, openQuestions, "open questions");
}

test("E02 v3 binds current source closure and replays exact v1/v3 compatibility preservation", () => {
  validate(JSON.parse(fs.readFileSync(qualificationPath, "utf8")), measureReplay(), measureSourceInventory());
});

test("E02 v3 rejects targeted mutations after a passing measured baseline", () => {
  const original = JSON.parse(fs.readFileSync(qualificationPath, "utf8"));
  const measuredReplay = measureReplay(); const sourceInventory = measureSourceInventory();
  validate(original, measuredReplay, sourceInventory);
  const mutations: Array<[string, (value: any) => void, RegExp]> = [
    ["schema", v => { v.schema_version = "alchlang.e02-formal-claim-projection-qualification/v2-candidate"; }, /schema_version/],
    ["authority", v => { v.authority_effect = "admitted"; }, /authority_effect/],
    ["false task pass", v => { v.result = "pass"; }, /result/],
    ["extra top-level key", v => { v.ignored_claim = true; }, /qualification keys/],
    ["missing top-level key", v => { delete v.replay; }, /qualification keys/],
    ["predecessor substitution", v => { v.supersedes_historical_qualification = { path: `${evidence}/qualification.json`, sha256: fileSha(`${evidence}/qualification.json`) }; }, /predecessor: path/],
    ["predecessor stale bytes", v => { v.supersedes_historical_qualification.sha256 = "0".repeat(64); }, /predecessor: sha256/],
    ["wrong DAG node", v => { v.dag.node = "E03"; }, /dag node/],
    ["extra binding", v => { v.bindings.unknown = v.bindings.fixture; }, /binding keys/],
    ["missing binding", v => { delete v.bindings.fixture; }, /binding keys/],
    ["resealed binding substitution", v => { v.bindings.projection_implementation = v.bindings.lowering_implementation; }, /binding projection_implementation: path/],
    ["extra exact-ref key", v => { v.bindings.fixture.current = true; }, /binding fixture/],
    ["source stale hash", v => { v.source_inventory.files[0].sha256 = "0".repeat(64); }, /source inventory/],
    ["missing source row", v => { v.source_inventory.files.pop(); }, /source inventory/],
    ["extra source row", v => { v.source_inventory.files.push(v.source_inventory.files[0]); }, /source inventory/],
    ["resealed source manifest", v => { v.source_inventory.files[0].sha256 = "0".repeat(64); v.source_inventory.manifest_sha256 = sha(JSON.stringify(v.source_inventory.files)); }, /source inventory/],
    ["semantic loss", v => { v.preservation.semantic_loss_count = 1; }, /preservation/],
    ["omitted representation change", v => { v.preservation.representation_change_count = 4; }, /preservation/],
    ["invented meaning", v => { v.preservation.meaning_repaired_or_invented = true; }, /preservation/],
    ["wrong identity boundary", v => { v.preservation.acceptance_and_interpretation_excluded_from_v3_claim_identity = false; }, /preservation/],
    ["stale test census", v => { v.validation.focused_lowering_and_projection.tests = 18; }, /validation/],
    ["failed typecheck", v => { v.validation.typecheck = "fail"; }, /validation/],
    ["false regression pass", v => { v.validation.full_application_regression = "pass"; }, /validation/],
    ["unvalidated schemas", v => { v.validation.replay.schema_validations = 0; }, /validation/],
    ["changed replay result", v => { v.replay[0].result_sha256 = "0".repeat(64); }, /replay/],
    ["changed fixture input", v => { v.replay[0].fixture_source_files[0].sha256 = "0".repeat(64); }, /replay/],
    ["changed projection output", v => { v.replay[1].projection_output_files[0].sha256 = "0".repeat(64); }, /replay/],
    ["missing replay case", v => { v.replay.pop(); }, /replay/],
    ["extra replay case", v => { v.replay.push(v.replay[0]); }, /replay/],
    ["widened ceiling", v => { v.claim_ceiling = "Runtime guaranteed"; }, /claim ceiling/],
  ];
  for (const key of Object.keys(bindingPaths)) mutations.push([`stale ${key}`,
    v => { v.bindings[key].sha256 = "0".repeat(64); }, new RegExp(`binding ${key}: sha256`)]);
  for (const key of Object.keys(limits)) mutations.push([`false effect ${key}`,
    v => { v.limits[key] = true; }, /limits/]);
  for (const [name, mutate, expected] of mutations) {
    const changed = structuredClone(original); mutate(changed);
    assert.throws(() => validate(changed, measuredReplay, sourceInventory), expected, name);
  }
});
