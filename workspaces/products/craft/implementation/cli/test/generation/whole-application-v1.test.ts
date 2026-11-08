import {typescriptCompiler,tsxLoader,tsxCli} from '../helpers/node-toolchain.ts';
import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

import { sha256 } from "../../src/input/source-manifest.ts";
import {
  mergeWholeApplicationArtifactsV1,
  planWholeApplicationV1,
  planComposedWholeApplication,
  composeComposedWholeApplicationPlan,
  validateWholeApplicationImportClosureV1,
  WholeApplicationPlanError,
} from "../../src/generation/whole-application-v1.ts";
import * as wholeApplicationFacade from "../../src/whole-application.ts";
import {planComposedReconciledProject,planReconciledProject} from "../../src/generation/reconciled-project.ts";
import {selectComposedReconciledProjectArtifacts,selectReconciledProjectArtifacts} from "../../src/generation/reconciled-project-layout.ts";
import {validateApplicationIntegrationBinding} from "../../src/system-integration/application-binding-v1.ts";
import {planEmbeddedIntegrationContributionV1} from "../../src/system-integration/embedded-generation-v1.ts";
import {loadCompiledProjectGraph} from "../../src/input/project-model.ts";

const here = path.dirname(fileURLToPath(import.meta.url));
const cliRoot = path.resolve(here, "../..");
const example = path.join(cliRoot, "examples/reconciled-commerce");
const source = JSON.parse(fs.readFileSync(path.join(example, "integrations/application.json"), "utf8"));
const selection = JSON.parse(fs.readFileSync(path.join(example, "selections/typescript.json"), "utf8"));
const selectionFor = (language: "typescript" | "python" | "rust"): any => JSON.parse(fs.readFileSync(path.join(example, `selections/${language}.json`), "utf8"));
const makeArtifact = (relative_path: string, content = ""): any => ({ relative_path, content, size_bytes: Buffer.byteLength(content), sha256: sha256(content) });

function materialize(plan: ReturnType<typeof planWholeApplicationV1>, root: string): void {
  for (const item of plan.artifacts) {
    const target = path.join(root, item.relative_path);
    fs.mkdirSync(path.dirname(target), { recursive: true });
    fs.writeFileSync(target, item.content);
  }
}

test("L0 whole-application package facade exposes the joined planning API", () => {
  assert.equal(wholeApplicationFacade.planWholeApplicationV1, planWholeApplicationV1);
  assert.equal(wholeApplicationFacade.planComposedWholeApplication, planComposedWholeApplication);
  assert.equal(wholeApplicationFacade.composeComposedWholeApplicationPlan, composeComposedWholeApplicationPlan);
  assert.equal(typeof wholeApplicationFacade.validateApplicationIntegrationBinding, "function");
  assert.equal(typeof wholeApplicationFacade.compileApplicationGraphV1, "function");
  assert.equal(typeof wholeApplicationFacade.integrationRelationshipSignature, "function");
  assert.equal(typeof wholeApplicationFacade.planEmbeddedIntegrationContributionV1, "function");
});

test("explicit composed whole application preserves native Mapping dispatch and profile custody", t => {
  const root=fs.mkdtempSync(path.join(os.tmpdir(),"domainspec-composed-whole-"));
  t.after(()=>fs.rmSync(root,{recursive:true,force:true}));
  const selected=structuredClone(selection);
  selected.schema_version="domainspec.reconciled-compilation/v2-candidate";
  selected.profile_id="domainspec.reconciled-typescript/v2-candidate";
  selected.value_compositions=selected.operations.map((operation:any)=>({composition:{schema_version:"domainspec.operation-value-composition/v1-candidate",operation_ref:operation.selector,bindings:[{kind:"mapping",name:"normalized",selector:"commerce:integration-inbound",arguments:[{parameter:"amount",value:{op:"path",root:"amount",properties:[]}}]}]},absence_failures:[]}));
  for(const operation of selected.operations){operation.writes[0].value.root="normalized";operation.result.value.root="normalized";}
  const sourceRoot=path.join(example,"source"),application=planComposedReconciledProject(sourceRoot,selected);
  const binding=validateApplicationIntegrationBinding(loadCompiledProjectGraph(sourceRoot),source);
  const contribution=planEmbeddedIntegrationContributionV1(source,"typescript");
  const plan=planComposedWholeApplication(sourceRoot,selected,source);
  assert.deepEqual(plan,composeComposedWholeApplicationPlan(application,contribution,binding));
  assert.deepEqual(plan,planComposedWholeApplication(sourceRoot,structuredClone(selected),structuredClone(source)));
  assert.throws(()=>planWholeApplicationV1(sourceRoot,selected,source));
  assert.throws(()=>planComposedWholeApplication(sourceRoot,selection,source));
  assert.throws(()=>selectReconciledProjectArtifacts(application as never),/explicit composed project API/);
  assert.throws(()=>selectComposedReconciledProjectArtifacts(planReconciledProject(sourceRoot,selection) as never),/explicit composed v2/);
  assert.throws(()=>composeComposedWholeApplicationPlan(structuredClone(application),contribution,binding),/registered reconciled/);
  assert.throws(()=>composeComposedWholeApplicationPlan(application,structuredClone(contribution),binding));
  assert.throws(()=>composeComposedWholeApplicationPlan(application,contribution,structuredClone(binding)));
  assert.notEqual(plan.selection_sha256,planWholeApplicationV1(sourceRoot,selection,source).selection_sha256);
  assert.equal(plan.runtime_guarantees_observed,false);
  materialize(plan,root);
  const compiled=spawnSync(process.execPath,[typescriptCompiler,"-p","tsconfig.json","--noEmit"],{cwd:root,encoding:"utf8"});
  assert.equal(compiled.status,0,compiled.stdout+compiled.stderr);
  const runner=`import assert from 'node:assert/strict';
import {APPLICATION_REQUEST_HANDLERS as handlers} from './src/integrations/application-request-handlers.ts';
async function main(){
const amount={billing_customer_id:'7',choice:{variant:'Some',payload:{quantity:'5',note:null}},customer:{id:'7',name:'Ada'},id:'9',labels:['priority'],lines:[{quantity:'2',note:'first'}],money:{quantity:'25',note:null},tags:['new','paid']};
const notice_input={occurrence:{'event-id':'evt-9'},occurredAt:'2026-09-16T12:00:00Z',payload:{'order-id':'9',delta:'1',ratio:1}};
let commits=0;const dependencies={store:{begin:async()=>({read:async()=>{throw Error('unexpected read')},commit:async batch=>{commits++;assert.equal(batch.writes[0].value.id,9n);return {status:'committed'}},rollback:async()=>{throw Error('unexpected rollback')}})}};
const outcome=await handlers['api-mapping:payment-webhook-request']({amount,notice_input},dependencies);
assert.equal(outcome.status,'committed');assert.equal(outcome.value.id,9n);assert.equal(commits,1);
}
main().catch(error=>{console.error(error);process.exitCode=1});`;
  const executed=spawnSync(process.execPath,[tsxCli,"--eval",runner],{cwd:root,encoding:"utf8"});
  assert.equal(executed.status,0,executed.stdout+executed.stderr);
});

test("L0 whole application plan has one total deterministic path-owner table", () => {
  const first = planWholeApplicationV1(path.join(example, "source"), selection, source);
  const second = planWholeApplicationV1(path.join(example, "source"), structuredClone(selection), structuredClone(source));
  assert.deepEqual(second, first);
  // Current corpus includes the twelve added computation/query/interface nodes.
  assert.equal(first.artifacts.length, 81);
  assert.equal(first.path_owners.length, first.artifacts.length);
  assert.equal(first.path_owners.filter(item => item.relative_path === "tsconfig.json" && item.owner === "whole-application-composer").length, 1);
  const tsconfig = JSON.parse(first.artifacts.find(item => item.relative_path === "tsconfig.json")!.content);
  assert.equal(tsconfig.compilerOptions.noUnusedLocals, true);
  assert.equal(tsconfig.compilerOptions.noUnusedParameters, true);
  const bindings = first.artifacts.find(item => item.relative_path === "src/integrations/domain-bindings.ts")!;
  const contracts = first.artifacts.find(item => item.relative_path === "src/features/integration/application/contracts.ts")!;
  assert.match(bindings.content, /import \* as Application0/);
  assert.match(bindings.content, /commerce:order/);
  const runtimeBindings = first.artifacts.find(item => item.relative_path === "src/integrations/runtime-bindings.ts")!;
  assert.match(runtimeBindings.content, /import \{mappingIntegrationOutbound as mapping_3\}/);
  assert.match(runtimeBindings.content, /"commerce:integration-outbound":mapping_3/);
  assert.match(runtimeBindings.content, /invokeMessageMappingOrderSubmittedOut/);
  assert.match(runtimeBindings.content, /"message-mapping:order-submitted-out":invokeMessageMappingOrderSubmittedOut/);
  assert.match(runtimeBindings.content, /RUNTIME_MAPPING_INVOCATIONS/);
  assert.match(runtimeBindings.content, /"kind":"event-identity-reference"/);
  assert.match(runtimeBindings.content, /"path":\["order-id"\]/);
  assert.match(runtimeBindings.content, /"result_type":\{"kind":"named","selector":"commerce:customer"\}/);
  const operationRequests = first.artifacts.find(item => item.relative_path === "src/integrations/operation-requests.ts")!;
  assert.match(operationRequests.content, /OperationInput as OperationRequest0/);
  assert.match(operationRequests.content, /export type CommercePerformRequest=OperationRequest0/);
  assert.match(operationRequests.content, /"commerce:perform#request"/);
  assert.match(first.artifacts.find(item=>item.relative_path.endsWith('/events/posted.provider.ts'))!.content,/EventRef<"commerce:order",bigint>/);
  assert.doesNotMatch(contracts.content, /Readonly<Record<string, unknown>>/);
  assert.match(contracts.content, /ApplicationInput/);
  const applicationGraph = first.artifacts.find(item => item.relative_path === ".domainspec/application-graph.json")!;
  assert.equal(JSON.parse(applicationGraph.content).graph_sha256, first.application_graph_sha256);
  assert.equal(first.runtime_guarantees_observed, false);
  assert.equal(first.claim_ceiling, "formation-and-static-compilation-only");
  assert.equal(first.authority_effect, "none");
});

test("L0 Operation Request composition rejects missing selected Operation inputs", () => {
  const incomplete = structuredClone(source);
  const mapping = incomplete.messaging.message_mappings.find((item: { mapping_id: string }) => item.mapping_id === "message-mapping:order-submitted-in");
  mapping.request_parameters = mapping.request_parameters.filter((item: { parameter: string }) => item.parameter !== "notice_input");
  assert.throws(
    () => planWholeApplicationV1(path.join(example, "source"), selection, incomplete),
    (error: unknown) => error instanceof WholeApplicationPlanError && error.code === "DS_WHOLE_APPLICATION_OPERATION_REQUEST",
  );
});

test("L0 ownership rejects exact and case-folded collisions without overwriting", () => {
  const a = makeArtifact("src/a.ts");
  const exact = [{ artifact: a, owner: "reconciled-application" as const }, { artifact: a, owner: "embedded-integration" as const }];
  assert.throws(() => mergeWholeApplicationArtifactsV1(exact), (error: unknown) => error instanceof WholeApplicationPlanError && error.code === "DS_WHOLE_APPLICATION_COLLISION");
  const folded = [{ artifact: a, owner: "reconciled-application" as const }, { artifact: makeArtifact("SRC/A.ts"), owner: "embedded-integration" as const }];
  assert.throws(() => mergeWholeApplicationArtifactsV1(folded), (error: unknown) => error instanceof WholeApplicationPlanError && error.code === "DS_WHOLE_APPLICATION_CASE_COLLISION");
});

test("L0 import closure rejects unresolved relative imports", () => {
  assert.throws(() => validateWholeApplicationImportClosureV1([makeArtifact("src/a.ts", 'import {b} from "./b.js";\n')]), (error: unknown) => error instanceof WholeApplicationPlanError && error.code === "DS_WHOLE_APPLICATION_IMPORT");
});

test("L0 planning is repeatable across processes", () => {
  const helper = path.join(cliRoot, "test/helpers/whole-application-plan.ts");
  const run = () => spawnSync(process.execPath, ["--import", tsxLoader, helper, example], { cwd: cliRoot, encoding: "utf8", env: { ...process.env, TMPDIR: "/tmp" } });
  const left = run();
  const right = run();
  assert.equal(left.status, 0, left.stderr);
  assert.equal(right.status, 0, right.stderr);
  assert.equal(left.stdout, right.stdout);
});

test("L0 generated TypeScript compiles in a disposed temporary root", () => {
  const temporary = fs.mkdtempSync(path.join(os.tmpdir(), "domainspec-whole-application-l0-"));
  try {
    const plan = planWholeApplicationV1(path.join(example, "source"), selection, source);
    materialize(plan, temporary);
    const compiler = typescriptCompiler;
    const result = spawnSync(process.execPath, [compiler, "-p", "tsconfig.json", "--noEmit"], { cwd: temporary, encoding: "utf8" });
    assert.equal(result.status, 0, `${result.error?.message ?? ""}\n${result.stdout}\n${result.stderr}`);
    const runner = 'import {RUNTIME_MAPPING_INVOCATIONS} from "./src/integrations/runtime-bindings.ts";const result=RUNTIME_MAPPING_INVOCATIONS["message-mapping:order-submitted-out"]({order:7n});if(result.id!==7n||result.name!=="integration")throw new Error("RUNTIME_MAPPING_INVOCATION");';
    const invoked = spawnSync(process.execPath, [tsxCli, "--eval", runner], { cwd: temporary, encoding: "utf8" });
    assert.equal(invoked.status, 0, `${invoked.error?.message ?? ""}\n${invoked.stdout}\n${invoked.stderr}`);
  } finally {
    fs.rmSync(temporary, { recursive: true, force: true });
  }
  assert.equal(fs.existsSync(temporary), false);
});

test("L1 Python and Rust plans preserve one cross-language semantic binding", () => {
  const plans = (["typescript", "python", "rust"] as const).map(language => planWholeApplicationV1(path.join(example, "source"), selectionFor(language), source));
  assert.deepEqual(plans.map(plan => plan.language), ["typescript", "python", "rust"]);
  assert.equal(new Set(plans.map(plan => plan.binding_sha256)).size, 1);
  assert.equal(new Set(plans.map(plan => plan.integration_semantic_manifest_sha256)).size, 1);
  assert.equal(new Set(plans.map(plan => plan.domain_source_manifest_sha256)).size, 1);
  assert.equal(new Set(plans.map(plan => plan.application_graph_sha256)).size, 1);
  assert.deepEqual(plans.map(plan => plan.artifacts.length), [81, 131, 81]);
  assert.equal(new Set(plans.map(plan => plan.artifacts.find(item => item.relative_path === ".domainspec/application-graph.json")?.sha256)).size, 1);
  const python = plans[1]!;
  assert.equal(python.artifacts.some(item => item.relative_path.startsWith("src/features/")), false);
  assert.equal(python.artifacts.filter(item => item.relative_path === "pyproject.toml").length, 1);
  assert.equal(python.artifacts.some(item => item.relative_path === "src/commerce_corpus/integrations/domain_bindings.py"), true);
  const pythonRuntimeBindings = python.artifacts.find(item => item.relative_path === "src/commerce_corpus/integrations/runtime_bindings.py");
  assert.ok(pythonRuntimeBindings);
  assert.match(pythonRuntimeBindings.content, /mapping_integration_outbound as _mapping_3/);
  assert.match(pythonRuntimeBindings.content, /RUNTIME_MAPPINGS = _MappingProxyType/);
  assert.match(pythonRuntimeBindings.content, /def invoke_message_mapping_order_submitted_out\(parameters\)/);
  assert.match(pythonRuntimeBindings.content, /RUNTIME_MAPPING_INVOCATIONS = _MappingProxyType/);
  assert.match(pythonRuntimeBindings.content, /event-identity-reference/);
  const pythonOperationRequests = python.artifacts.find(item => item.relative_path === "src/commerce_corpus/integrations/operation_requests.py");
  assert.ok(pythonOperationRequests);
  assert.match(pythonOperationRequests.content, /OperationInput as _OperationRequest0/);
  assert.match(pythonOperationRequests.content, /CommercePerformRequest = _OperationRequest0/);
  assert.match(python.artifacts.find(item=>item.relative_path.endsWith('/event_references/commerce/order.py'))!.content,/NewType\("commerce:order", int\)/);
  const pythonContracts = python.artifacts.find(item => item.relative_path.endsWith("/features/integration/application/contracts.py"));
  assert.ok(pythonContracts);
  assert.doesNotMatch(pythonContracts.content, /\n    def (?:publish|load|save|authorize)\(/);
  assert.match(pythonContracts.content, /\n    async def publish\(/);
  assert.match(pythonContracts.content, /\n    async def authorize\(/);
  const rust = plans[2]!;
  for (const root of ["Cargo.toml", "src/lib.rs", "src/features/mod.rs", "src/integrations/mod.rs"]) {
    assert.equal(rust.artifacts.filter(item => item.relative_path === root).length, 1, root);
    assert.equal(rust.path_owners.find(item => item.relative_path === root)?.owner, "whole-application-composer", root);
  }
  assert.equal(rust.artifacts.some(item => item.relative_path === "src/integrations/domain_bindings.rs"), true);
  const rustRuntimeBindings = rust.artifacts.find(item => item.relative_path === "src/integrations/runtime_bindings.rs");
  assert.ok(rustRuntimeBindings);
  assert.match(rustRuntimeBindings.content, /integration_outbound as mapping_3/);
  assert.match(rustRuntimeBindings.content, /integration_outbound as invoke_message_mapping_order_submitted_out/);
  assert.match(rustRuntimeBindings.content, /invocation_symbol: "invoke_message_mapping_order_submitted_out"/);
  assert.match(rustRuntimeBindings.content, /source_kind: "event-identity-reference"/);
  assert.match(rustRuntimeBindings.content, /source_path: &\["order-id"\]/);
  const rustOperationRequests = rust.artifacts.find(item => item.relative_path === "src/integrations/operation_requests.rs");
  assert.ok(rustOperationRequests);
  assert.match(rustOperationRequests.content, /PerformRequest as CommercePerformRequest/);
  assert.match(rust.artifacts.find(item => item.relative_path.endsWith("operations/perform.rs"))!.content, /pub struct PerformRequest/);
  assert.match(rust.artifacts.find(item => item.relative_path.endsWith("operations/perform.rs"))!.content, /pub async fn perform_request/);
  assert.match(rust.artifacts.find(item=>item.relative_path.includes('events/')&&item.content.includes('commerce:posted'))!.content,/pub struct EventRefF8CommerceN5Order\(u64\)/);
  assert.match(rust.artifacts.find(item => item.relative_path === "src/integrations/mod.rs")!.content, /pub mod runtime_bindings;/);
  assert.match(rust.artifacts.find(item => item.relative_path === "src/integrations/mod.rs")!.content, /pub mod operation_requests;/);
});

test("L1 generated Python compiles and imports from a disposed temporary root", () => {
  const temporary = fs.mkdtempSync(path.join(os.tmpdir(), "domainspec-whole-application-l1-python-"));
  try {
    materialize(planWholeApplicationV1(path.join(example, "source"), selectionFor("python"), source), temporary);
    const compiled = spawnSync("python3", ["-m", "compileall", "-q", "."], { cwd: temporary, encoding: "utf8" });
    assert.equal(compiled.status, 0, `${compiled.stdout}\n${compiled.stderr}`);
    const importer = "import importlib,pathlib; root=pathlib.Path('src'); files=sorted(root.rglob('*.py')); modules=[]; [modules.append('.'.join((p.relative_to(root).with_suffix('').parts[:-1] if p.name=='__init__.py' else p.relative_to(root).with_suffix('').parts))) for p in files]; [importlib.import_module(m) for m in modules if m]; runtime=importlib.import_module('commerce_corpus.integrations.runtime_bindings'); result=runtime.RUNTIME_MAPPING_INVOCATIONS['message-mapping:order-submitted-out']({'order':7}); assert result['id']==7 and result['name']=='integration'";
    const imported = spawnSync("python3", ["-c", importer], { cwd: temporary, encoding: "utf8", env: { ...process.env, PYTHONPATH: path.join(temporary, "src") } });
    assert.equal(imported.status, 0, `${imported.stdout}\n${imported.stderr}`);
  } finally {
    fs.rmSync(temporary, { recursive: true, force: true });
  }
  assert.equal(fs.existsSync(temporary), false);
});
