import assert from "node:assert/strict";
import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import os from "node:os";
import { spawnSync } from "node:child_process";
import test from "node:test";

import { defaultDomainSpecPackageRoot } from "../src/domainspec-cli.js";
import { validateCandidate as validateHistorical } from "../scripts/p03-exact-candidate.js";
import { validateCandidate as validateV4 } from "../scripts/p03-exact-candidate-v4.js";
import { buildCandidate, compareArtifactReplay, createQualification, validateCandidate, validateQualification, validatePredecessorSemantics, inspectArchive } from "../scripts/p03-exact-candidate-v5.js";

const repo = path.resolve(defaultDomainSpecPackageRoot(), "../../../../..");
const implementation = path.join(repo, "language/capabilities/alchlang/plans/general-compiler-v1/implementation");
const evidence = path.join(repo, "craft/projects/domainspec-v2/development/authoring-to-runtime-v1/evidence/p03-exact-candidate");
const candidatePath = path.join(evidence, "successor-v5-candidate/candidate.json");
const qualificationPath = path.join(evidence, "successor-v5-candidate/qualification.json");
const previousCandidatePath = path.join(evidence, "successor-v4-candidate/candidate.json");
const previousQualificationPath = path.join(evidence, "successor-v4-candidate/qualification.json");
const historicalCandidatePath = path.join(evidence, "candidate.json");
const historicalQualificationPath = path.join(evidence, "qualification.json");
const schemaPath = path.join(repo, "craft/projects/domainspec-v2/development/authoring-to-runtime-v1/p03-candidate.v2.schema.json");
const sha256 = (file: string) => crypto.createHash("sha256").update(fs.readFileSync(file)).digest("hex");
const read = (file: string) => JSON.parse(fs.readFileSync(file, "utf8"));

function snapshot(): Array<[string, number, string]> {
  return [historicalCandidatePath, historicalQualificationPath, previousCandidatePath, previousQualificationPath, candidatePath, qualificationPath]
    .concat([path.join(evidence,"successor-v2-candidate/candidate.json"),path.join(evidence,"successor-v2-candidate/qualification.json")])
    .concat([path.join(evidence,"successor-v3-candidate/candidate.json"),path.join(evidence,"successor-v3-candidate/qualification.json")])
    .map(file => [path.relative(evidence, file), fs.statSync(file).mtimeMs, sha256(file)]);
}

let measured: any;
function replay(candidate: any) { return measured ??= buildCandidate(candidate.date); }

test("P03 successor is freshly regenerated, current, schema-valid and fully denominator-bound", () => {
  const candidate = read(candidatePath);
  compareArtifactReplay(candidate,replay(candidate));
  const result = validateCandidate(candidate, true);
  assert.equal(result.result, "pass", JSON.stringify(result, null, 2));
  assert.equal(candidate.schema_version, "alchlang.p03-exact-candidate/v2-candidate");
  const schema = spawnSync("python3", ["-c", "import json,jsonschema,sys;jsonschema.Draft202012Validator(json.load(open(sys.argv[1]))).validate(json.load(open(sys.argv[2])))", schemaPath, candidatePath], { encoding: "utf8" });
  assert.equal(schema.status, 0, schema.stderr || String(schema.error));
  assert.equal(candidate.source_groups.length, 8);
  assert.equal(candidate.source_groups[7].id,"selected-consumer-envelope");
  assert.equal(candidate.source_groups[7].files.length,1907);
  assert.equal(candidate.package_archives.length, 4);
  assert.deepEqual(candidate.generated_projects.map((item: any) => item.language), ["typescript", "python", "rust"]);
  assert.ok(candidate.source_groups.every((item: any) => item.files.length > 0));
  const tools = candidate.source_groups.find((g: any) => g.id === "candidate-tools");
  assert.equal(tools.files.filter((r: any) => r.path.endsWith("/scripts/p03-exact-candidate-v5.ts")).length, 1);
  assert.equal(candidate.receipts.length, 13);
  for (const predecessor of [previousCandidatePath, previousQualificationPath]) {
    assert.deepEqual(candidate.receipts.filter((r: any) => r.path === path.relative(repo, predecessor)),
      [{path: path.relative(repo, predecessor), size_bytes: fs.statSync(predecessor).size, sha256: sha256(predecessor)}]);
  }
  assert.ok(candidate.package_archives.every((item: any) => item.archive_sha256 === item.p02_archive_sha256));
  assert.ok(candidate.package_archives.every((item: any)=>item.files.every((f: any)=>f.path.startsWith("package/") && !path.isAbsolute(f.path))));
  assert.ok(candidate.generated_projects.every((item: any) => item.build_manifest_sha256 === item.p02_build_manifest_sha256));
});

test("P03 currentness command is non-mutating", () => {
  const before = snapshot();
  const result = spawnSync(process.execPath, ["scripts/run-toolchain.mjs", "tsx", "scripts/p03-exact-candidate-v5.ts", "--check"], { cwd: implementation, encoding: "utf8" });
  assert.equal(result.status, 0, result.stdout + result.stderr);
  assert.equal(JSON.parse(result.stdout).result, "pass");
  assert.deepEqual(snapshot(), before);
});

test("P03 rejects stale files, archive drift, generated drift, tool drift and claim growth", () => {
  const original = read(candidatePath);
  const mutations = [
    (value: any) => { value.source_groups[0].files[0].sha256 = "0".repeat(64); },
    (value: any) => { value.package_archives[0].files.pop(); },
    (value: any) => { value.package_archives[1].archive_sha256 = "0".repeat(64); },
    (value: any) => { value.generated_projects[0].build_manifest_sha256 = "0".repeat(64); },
    (value: any) => { value.tools[0].version = "v0.0.0"; },
    (value: any) => { value.receipts[0].sha256 = "0".repeat(64); },
    (value: any) => { value.materialization.historical_evidence_refreshed = true; },
    (value: any) => { value.claim_ceiling.publication = true; },
  ];
  for (const mutate of mutations) {
    const changed = structuredClone(original);
    mutate(changed);
    assert.equal(validateCandidate(changed, true).result, "fail");
  }
});

test("P03 qualification binds candidate, schema, validator, test and predecessor", () => {
  const qualification = read(qualificationPath);
  assert.equal(qualification.schema_version, "alchlang.p03-exact-candidate-qualification/v5-candidate");
  assert.equal(qualification.task, "P03");
  assert.equal(qualification.result, "blocked");
  assert.equal(qualification.construction_result,"scoped-pass");
  assert.equal(qualification.inherited_boundaries.P01.result,"blocked");
  assert.equal(qualification.inherited_boundaries.P02.result,"blocked");
  assert.equal(qualification.authority_effect, "none");
  assert.equal(qualification.candidate.path, path.relative(repo, candidatePath));
  assert.equal(qualification.supersedes_historical_candidate.path, path.relative(repo, historicalCandidatePath));
  assert.equal(qualification.supersedes_historical_qualification.path, path.relative(repo, historicalQualificationPath));
  assert.equal(qualification.supersedes_previous_candidate.path, path.relative(repo, previousCandidatePath));
  assert.equal(qualification.supersedes_previous_qualification.path, path.relative(repo, previousQualificationPath));
  for (const binding of [qualification.candidate, qualification.supersedes_historical_candidate,
    qualification.supersedes_historical_qualification, qualification.supersedes_previous_candidate,
    qualification.supersedes_previous_qualification, ...Object.values(qualification.bindings), ...Object.values(qualification.inherited_boundaries)] as Array<{ path: string; size_bytes: number; sha256: string }>) {
    const file = path.join(repo, binding.path);
    assert.equal(sha256(file), binding.sha256, binding.path);
    assert.equal(fs.statSync(file).size, binding.size_bytes, binding.path);
  }
  assert.deepEqual(Object.keys(qualification.bindings), ["schema", "materializer_and_validator", "historical_materializer", "adversarial_test", "safety_test", "p01_predecessor", "p02_predecessor", "previous_materializer"]);
  assert.match(qualification.bindings.materializer_and_validator.path, /p03-exact-candidate-v5\.ts$/u);
  assert.match(qualification.bindings.previous_materializer.path, /p03-exact-candidate-v4\.ts$/u);
  assert.equal(qualification.bindings.schema.path, path.relative(repo, schemaPath));
  assert.match(qualification.bindings.p01_predecessor.path, /qualification\.v5-candidate\.json$/u);
  assert.match(qualification.bindings.p02_predecessor.path, /successor-v6-candidate\/qualification\.json$/u);
  const candidate = read(candidatePath);
  assert.equal(qualification.candidate_id, candidate.candidate_id);
  assert.equal(qualification.candidate_manifest_sha256, candidate.manifest_sha256);
  assert.deepEqual(qualification,createQualification(candidate));
  assert.equal(validateQualification(qualification,candidate).result,"pass");
  assert.ok(Object.values(qualification.hard_stops).every(item => item === false));
  assert.match(qualification.claim_ceiling, /construction evidence only/u);
});

test("previous P03 v4 and v3 remain preserved but cannot claim current source", () => {
  const previous = read(previousCandidatePath);
  for (const result of [validateV4(previous, true), validateHistorical(read(path.join(evidence,"successor-v3-candidate/candidate.json")), true)]) {
    assert.equal(result.result, "fail");
    assert.equal(result.checks.find(item => item.id === "source-current")?.result, "fail");
  }
});

const canonical = (value: any): string => Array.isArray(value) ? "["+value.map(canonical).join(",")+"]"
  : value!==null && typeof value==="object" ? "{"+Object.keys(value).sort().map(k => JSON.stringify(k)+":"+canonical(value[k])).join(",")+"}" : JSON.stringify(value) ?? "null";
const hash = (text: string) => crypto.createHash("sha256").update(text).digest("hex");
function reseal(value: any) {
  delete value.candidate_id; delete value.manifest_sha256;
  value.candidate_id="alchlang-domainspec-p03-"+hash(canonical(value)).slice(0,16);
  value.manifest_sha256=hash(canonical(value));
}
function reInventory(group: any) { group.inventory_sha256=hash(canonical(group.files)); }

test("P03 rejects resealed closure, archive, environment, receipt, tool, HEAD and effect substitutions", () => {
  const original=read(candidatePath);
  const mutations: Array<(v: any)=>void> = [
    v=>{v.source_groups.pop();},
    v=>{v.source_groups.push(structuredClone(v.source_groups[0]));},
    v=>{v.source_groups[0].id="substituted";},
    v=>{v.package_archives[0].files[0].sha256="0".repeat(64);reInventory(v.package_archives[0]);},
    v=>{v.package_archives[0].archive_size_bytes++;},
    v=>{v.package_archives[0].files[0].path="/"+v.package_archives[0].files[0].path;reInventory(v.package_archives[0]);},
    v=>{v.generated_projects[0].build_manifest_sha256="0".repeat(64);},
    v=>{v.generated_projects[0].archive_set_sha256="0".repeat(64);},
    v=>{v.receipts.pop();},
    v=>{v.receipts.find((r: any)=>r.path.endsWith("successor-v6-candidate/typescript.json")).sha256="0".repeat(64);},
    v=>{v.environment.platform="substituted-platform";},
    v=>{v.tools[0].executable_sha256="0".repeat(64);},
    v=>{v.source_posture.git_head="0".repeat(40);},
    v=>{v.materialization.task_owned_root_disposed=false;},
    v=>{v.materialization.historical_evidence_refreshed=true;},
    v=>{v.claim_ceiling.production=true;},
  ];
  for(const mutate of mutations) {
    const changed=structuredClone(original);mutate(changed);reseal(changed);
    const result=validateCandidate(changed,true);
    assert.equal(result.checks.find(c=>c.id==="candidate-id")?.result,"pass");
    assert.equal(result.checks.find(c=>c.id==="manifest-self-digest")?.result,"pass");
    assert.equal(result.result,"fail");
  }
});

test("P03 full measured replay rejects a resealed arbitrary generated member; cheap currentness is not replay", () => {
  const original=read(candidatePath),changed=structuredClone(original);
  const member=changed.generated_projects[0].files.find((r: any)=>r.path==="generated/package.json");
  assert.ok(member);
  member.sha256="0".repeat(64);reInventory(changed.generated_projects[0]);reseal(changed);
  const cheap=validateCandidate(changed,true);
  assert.equal(cheap.result,"pass", "uninspected generated-member forgery separates cheap currentness from full replay");
  assert.equal(cheap.artifact_replay_performed,false);
  assert.throws(()=>compareArtifactReplay(changed,replay(original)),/P03_FULL_ARTIFACT_REPLAY_MISMATCH/);
  compareArtifactReplay(original,replay(original));
});

test("P03 qualification rejects false lifecycle pass, missing or extra binding and stale predecessor", () => {
  const candidate=read(candidatePath),original=read(qualificationPath);
  for(const mutate of [
    (v: any)=>{v.result="pass";},
    (v: any)=>{v.construction_result="pass";},
    (v: any)=>{delete v.bindings.p02_predecessor;},
    (v: any)=>{v.bindings.extra=v.bindings.schema;},
    (v: any)=>{v.inherited_boundaries.P02.result="pass";},
    (v: any)=>{v.inherited_boundaries.P01.sha256="0".repeat(64);},
    (v: any)=>{v.validation.task_owned_root_disposed=false;},
    (v: any)=>{v.hard_stops.product_approval_inferred=true;},
    (v: any)=>{v.bindings.previous_materializer.sha256="0".repeat(64);},
    (v: any)=>{delete v.bindings.previous_materializer;},
  ]) {
    const changed=structuredClone(original);mutate(changed);
    assert.equal(validateQualification(changed,candidate).result,"fail");
  }
});

test("P03 archive inspection rejects links, duplicate members, traversal and backslashes without extraction", () => {
  const work=fs.mkdtempSync(path.join(os.tmpdir(),"alchlang-p03-tar-controls-"));
  try {
    const script=[
      "import io,os,sys,tarfile",
      "root=sys.argv[1]",
      "for kind in ['valid','symlink','duplicate','traversal','backslash']:",
      " with tarfile.open(os.path.join(root,kind+'.tgz'),'w:gz') as t:",
      "  name='package/file.txt' if kind not in ('traversal','backslash') else ('package/../escape' if kind=='traversal' else 'package/dir'+chr(92)+'file')",
      "  m=tarfile.TarInfo(name);data=b'valid';m.size=len(data)",
      "  if kind=='symlink': m.type=tarfile.SYMTYPE;m.linkname='/tmp/escape';m.size=0;t.addfile(m)",
      "  else:",
      "   t.addfile(m,io.BytesIO(data))",
      "   if kind=='duplicate': t.addfile(m,io.BytesIO(data))",
    ].join("\n");
    const generated=spawnSync("python3",["-I","-c",script,work],{encoding:"utf8"});
    assert.equal(generated.status,0,generated.stderr);
    assert.deepEqual(inspectArchive(path.join(work,"valid.tgz")),[{path:"file.txt",size_bytes:5,sha256:hash("valid")}]);
    for(const kind of ["symlink","duplicate","traversal","backslash"])assert.throws(()=>inspectArchive(path.join(work,kind+".tgz")),/P03_ARCHIVE_/);
    assert.deepEqual(fs.readdirSync(work).sort(),["backslash.tgz","duplicate.tgz","symlink.tgz","traversal.tgz","valid.tgz"]);
  } finally { fs.rmSync(work,{recursive:true,force:true}); }
  assert.equal(fs.existsSync(work),false);
});

test("P03 v5 rejects historical writes and malformed arguments before repository effects", () => {
  const before=snapshot();
  for(const args of [["--write"],["--write-successor"],["--check","--measure"],["--unknown"]]) {
    const result=spawnSync(process.execPath,["scripts/run-toolchain.mjs","tsx","scripts/p03-exact-candidate-v5.ts",...args],{cwd:implementation,encoding:"utf8"});
    assert.notEqual(result.status,0);
    assert.match(result.stderr,args[0].startsWith("--write")?/P03_HISTORICAL_WRITE_DISABLED/:/usage: p03-exact-candidate-v5/);
    assert.deepEqual(snapshot(),before);
  }
});

test("P03 rejects weakened predecessor semantics and a severed P01 to P02 archive chain", () => {
  const qualification=read(qualificationPath);
  const p01=read(path.join(repo,qualification.bindings.p01_predecessor.path));
  const p02=read(path.join(repo,qualification.bindings.p02_predecessor.path));
  validatePredecessorSemantics(p01,p02);
  for(const mutate of [
    (a: any,b: any)=>{a.result="pass";},
    (a: any,b: any)=>{b.result="pass";},
    (a: any,b: any)=>{a.hard_stops={};},
    (a: any,b: any)=>{b.hard_stops={};},
    (a: any,b: any)=>{b.hard_stops.extra=false;},
    (a: any,b: any)=>{b.validation.clean_consumer_reports.passed=2;},
    (a: any,b: any)=>{b.archive_observations[1].archive_sha256="0".repeat(64);},
    (a: any,b: any)=>{delete b.reports.python;},
  ]) {
    const a=structuredClone(p01),b=structuredClone(p02);mutate(a,b);
    assert.throws(()=>validatePredecessorSemantics(a,b));
  }
});

test("P03 v5 rejects forged or omitted additions before narrow v4 projection", () => {
  const original = read(candidatePath);
  const tool = (v: any) => v.source_groups.find((g: any) => g.id === "candidate-tools");
  const own = (v: any) => tool(v).files.find((r: any) => r.path.endsWith("/scripts/p03-exact-candidate-v5.ts"));
  const predecessor = (v: any) => v.receipts.find((r: any) => r.path === path.relative(repo, previousCandidatePath));
  for (const mutate of [
    (v: any) => {own(v).sha256 = "0".repeat(64); reInventory(tool(v));},
    (v: any) => {own(v).size_bytes++; reInventory(tool(v));},
    (v: any) => {tool(v).files = tool(v).files.filter((r: any) => r !== own(v)); reInventory(tool(v));},
    (v: any) => {tool(v).files.push(structuredClone(own(v))); reInventory(tool(v));},
    (v: any) => {tool(v).files.reverse(); reInventory(tool(v));},
    (v: any) => {tool(v).inventory_sha256 = "0".repeat(64);},
    (v: any) => {predecessor(v).sha256 = "0".repeat(64);},
    (v: any) => {predecessor(v).size_bytes++;},
    (v: any) => {v.receipts.find((r: any) => r.path === path.relative(repo, previousQualificationPath)).sha256 = "0".repeat(64);},
    (v: any) => {v.receipts = v.receipts.filter((r: any) => r !== predecessor(v));},
    (v: any) => {v.receipts.push(structuredClone(predecessor(v)));},
    (v: any) => {v.receipts.reverse();},
    (v: any) => {tool(v).files.push({...own(v), path:"unknown/extra.ts"}); reInventory(tool(v));},
    (v: any) => {v.receipts.push({...predecessor(v), path:"unknown/extra.json"});},
  ]) {
    const changed = structuredClone(original); mutate(changed); reseal(changed);
    const result = validateCandidate(changed, true);
    assert.equal(result.checks.find(c => c.id === "candidate-id")?.result, "pass");
    assert.equal(result.checks.find(c => c.id === "manifest-self-digest")?.result, "pass");
    assert.equal(result.result, "fail", "a discarded addition must not escape validation");
  }
  for (const value of [null, {}, {source_groups:[],receipts:[]}]) {
    assert.equal(validateCandidate(value as any, true).result, "fail");
  }
});
