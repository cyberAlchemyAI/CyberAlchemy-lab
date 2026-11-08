import fs from "node:fs";
import path from "node:path";

import { canonicalJson, sha256 } from "../input/source-manifest.js";
import type { SupportedLanguage } from "../meta-types/types.js";
import { renderImplementation } from "../generation/generators.js";
import { discoverReceiptPath, readInstantiationReceipt, type InstantiationReceiptV1 } from "./receipt.js";
import { renderSystemIntegrationContract, verifySystemIntegrationContract } from "../system-integration/compiler.js";
import { renderTypedRustCrateManifest } from "../typed-operation/rust.js";

export class ConformanceError extends Error {
  readonly exitCode = 1;

  constructor(readonly code: string, readonly pointer: string, message: string) {
    super(message);
    this.name = "ConformanceError";
  }
}

function fail(code: string, pointer: string, message: string): never {
  throw new ConformanceError(code, pointer, message);
}

function normalizeTargetRoot(targetRoot: unknown): string {
  if (typeof targetRoot !== "string" || !path.isAbsolute(targetRoot) || path.resolve(targetRoot) !== targetRoot) fail("MTCLI_OBSERVE_EXPLICIT_ROOT", "/target-root", "target root must be an explicit normalized absolute path");
  let stats: fs.Stats;
  try {
    stats = fs.lstatSync(targetRoot);
  } catch {
    fail("MTCLI_OBSERVE_MISSING", "/target-root", "target root is missing");
  }
  if (stats.isSymbolicLink() || !stats.isDirectory() || fs.realpathSync(targetRoot) !== targetRoot) fail("MTCLI_OBSERVE_SYMLINK", "/target-root", "target root cannot be or traverse a symbolic link");
  return targetRoot;
}

function walkFiles(root: string, relative = ""): string[] {
  const directory = path.join(root, relative);
  const result: string[] = [];
  for (const entry of fs.readdirSync(directory, { withFileTypes: true }).sort((left, right) => left.name.localeCompare(right.name))) {
    const child = relative ? `${relative}/${entry.name}` : entry.name;
    const absolute = path.join(root, child);
    const stats = fs.lstatSync(absolute);
    if (stats.isSymbolicLink()) fail("MTCLI_OBSERVE_SYMLINK", `/${child}`, "symbolic links are forbidden in an instantiated target");
    if (stats.isDirectory()) result.push(...walkFiles(root, child));
    else if (stats.isFile()) result.push(child);
    else fail("MTCLI_OBSERVE_FILE_TYPE", `/${child}`, "unsupported target entry type");
  }
  return result;
}

function marker(content: string, name: string, pointer: string): string {
  const matches = [...content.matchAll(new RegExp(`^(?:\\/\\/|#) ${name}: (.+)$`, "gm"))];
  if (matches.length !== 1 || matches[0]?.[1] === undefined) fail("MTCLI_OBSERVE_PROVENANCE", pointer, `expected exactly one ${name} marker`);
  return matches[0][1];
}

function jsonMarker(content: string, name: string, pointer: string): unknown {
  try {
    return JSON.parse(marker(content, name, pointer));
  } catch (error) {
    if (error instanceof ConformanceError) throw error;
    fail("MTCLI_OBSERVE_PROVENANCE", pointer, `${name} marker is not valid JSON`);
  }
}

function operationOrder(content: string, language: SupportedLanguage, pointer: string): void {
  const signatures = {
    typescript: { guard: "if (!guard())", mutation: "const nextState", outbox: "const outbox", success: "return { ok: true as const, reads: readSet, state: nextState, outbox }" },
    python: { guard: "if not guard:", mutation: "next_state =", outbox: "outbox =", success: 'return {"ok": True, "reads": read_set, "state": next_state, "outbox": outbox}' },
    rust: { guard: "if !guard", mutation: "let mut next_state", outbox: "let outbox", success: "Ok(" },
  } as const;
  const expected = signatures[language];
  const guard = content.indexOf(expected.guard);
  const mutation = content.indexOf(expected.mutation);
  if (guard < 0 || mutation < 0 || guard >= mutation) fail("MTCLI_OPERATION_GUARD_ORDER", pointer, "guard must execute before state mutation");
  const outbox = content.indexOf(expected.outbox, mutation);
  const success = content.indexOf(expected.success, outbox);
  if (outbox < 0 || success < 0 || mutation >= outbox || outbox >= success) fail("MTCLI_OPERATION_ATOMICITY", pointer, "state and outbox must be formed before one success outcome");
}

function operationEffectConstruction(content: string, receipt: InstantiationReceiptV1, pointer: string): void {
  const body = receipt.semantic_contract.body;
  const effects = Array.isArray(body.effects) ? body.effects : [];
  const expected = {
    typescript: `const outbox = ${receipt.input.node_id.split(/[^A-Za-z0-9]+/).filter(Boolean).map((word) => `${word[0]?.toUpperCase() ?? ""}${word.slice(1)}`).join("")}Contract.effects.map((type) => Object.freeze({ type, operation: ${JSON.stringify(receipt.input.node_id)} }));`,
    python: `outbox = [{"type": effect, "operation": ${JSON.stringify(receipt.input.node_id)}} for effect in ${JSON.stringify(effects)}]`,
    rust: `let outbox: Vec<String> = [${effects.map((value) => JSON.stringify(value)).join(", ")}].iter().map(|value| (*value).to_owned()).collect();`,
  } as const;
  if (!content.includes(expected[receipt.language])) fail("MTCLI_OPERATION_UNDECLARED_EFFECT", pointer, "Operation effect construction is not exactly derived from the declared effect set");
}

function operationStateConstruction(content: string, receipt: InstantiationReceiptV1, pointer: string): void {
  const body = receipt.semantic_contract.body;
  const reads = Array.isArray(body.reads) ? body.reads : [];
  const writes = Array.isArray(body.writes) ? body.writes : [];
  const name = receipt.input.node_id.split(/[^A-Za-z0-9]+/).filter(Boolean).map((word) => `${word[0]?.toUpperCase() ?? ""}${word.slice(1)}`).join("");
  const expectedReads = {
    typescript: `const readSet = Object.freeze(Object.fromEntries(${name}Contract.reads.map((key) => [key, state[key]])));`,
    python: `read_set = {key: state.get(key) for key in ${JSON.stringify(reads)}}`,
    rust: `let reads = [${reads.map((value) => JSON.stringify(value)).join(", ")}].iter().filter_map(|key| state.get(*key).map(|value| ((*key).to_owned(), value.clone()))).collect();`,
  } as const;
  const expectedWrites = {
    typescript: `const nextState = Object.freeze(${name}Contract.writes.reduce<Record<string, unknown>>((next, key) => ({ ...next, [key]: changes[key] }), { ...state }));`,
    python: `for key in ${JSON.stringify(writes)}:\n        next_state[key] = changes.get(key)`,
    rust: `for key in [${writes.map((value) => JSON.stringify(value)).join(", ")}] { if let Some(value) = changes.get(key) { next_state.insert(key.to_owned(), value.clone()); } }`,
  } as const;
  if (!content.includes(expectedReads[receipt.language])) fail("MTCLI_OPERATION_UNDECLARED_READ", pointer, "Operation reads are not exactly derived from the declared read set");
  if (!content.includes(expectedWrites[receipt.language])) fail("MTCLI_OPERATION_UNDECLARED_WRITE", pointer, "Operation writes are not exactly derived from the declared write set");
}

function operationInstrumentationBoundary(content: string, receipt: InstantiationReceiptV1, pointer: string): void {
  if (marker(content, "domainspec-operation-core-instrumentation-free", pointer) !== "true") {
    fail("MTCLI_OPERATION_INSTRUMENTATION_BOUNDARY", pointer, "Operation core must remain instrumentation-free");
  }
  if (marker(content, "domainspec-operation-instrumentation-owner", pointer) !== '"outer-wrapper"') {
    fail("MTCLI_OPERATION_INSTRUMENTATION_BOUNDARY", pointer, "Operation instrumentation must be owned by the outer wrapper");
  }
  const fragments = {
    typescript: [`export function ${lowerCamel(receipt.input.node_id)}Observed(`, `const outcome = ${lowerCamel(receipt.input.node_id)}(state, changes, guard);`],
    python: [`def ${snake(receipt.input.node_id)}_observed(`, `outcome = ${snake(receipt.input.node_id)}(state, changes, guard)`],
    rust: [`pub fn ${snake(receipt.input.node_id)}_observed(`, `let outcome = ${snake(receipt.input.node_id)}(state, changes, guard);`],
  } as const;
  if (fragments[receipt.language].some((fragment) => !content.includes(fragment))) {
    fail("MTCLI_OPERATION_INSTRUMENTATION_BOUNDARY", pointer, "outer instrumentation wrapper does not delegate to the pure Operation core");
  }
}

function operationCreationTargets(content: string, receipt: InstantiationReceiptV1, pointer: string): void {
  const targets = Array.isArray(receipt.semantic_contract.body.creation_targets)
    ? receipt.semantic_contract.body.creation_targets
    : [];
  const constant = snake(receipt.input.node_id).toUpperCase();
  const rustConstant = pascal(receipt.input.node_id).toUpperCase();
  const expected = {
    typescript: `export const ${pascal(receipt.input.node_id)}Contract = Object.freeze({"creation_targets":${JSON.stringify(targets)}`,
    python: `${constant}_CREATION_TARGETS = tuple(${JSON.stringify(targets)})`,
    rust: `pub const ${rustConstant}_CREATION_TARGETS: &[&str] = &[${targets.map((target) => JSON.stringify(target)).join(", ")}];`,
  } as const;
  if (!content.includes(expected[receipt.language])) {
    fail("MTCLI_OPERATION_CREATION_TARGETS", pointer, "Operation creation_targets projection is absent or drifted");
  }
}

function words(value: string): string[] {
  return value.split(/[^A-Za-z0-9]+/).filter(Boolean);
}

function pascal(value: string): string {
  return words(value).map((word) => `${word[0]?.toUpperCase() ?? ""}${word.slice(1)}`).join("");
}

function lowerCamel(value: string): string {
  const name = pascal(value);
  return `${name[0]?.toLowerCase() ?? "d"}${name.slice(1)}`;
}

function snake(value: string): string {
  return words(value).map((word) => word.toLowerCase()).join("_");
}

function workflowCompensation(content: string, receipt: InstantiationReceiptV1, pointer: string): void {
  if (marker(content, "domainspec-workflow-recovery-results", pointer) !== '["not-required","recovery-required"]') {
    fail("MTCLI_WORKFLOW_COMPENSATION_STATE", pointer, "Workflow recovery evaluation result set drifted");
  }
  if (marker(content, "domainspec-recovery-intent-statuses", pointer) !== '["required","satisfied","unresolved"]') {
    fail("MTCLI_WORKFLOW_COMPENSATION_STATE", pointer, "Recovery Intent semantic status set drifted");
  }
  if (marker(content, "domainspec-workflow-compensation-execution", pointer) !== "false") {
    fail("MTCLI_WORKFLOW_COMPENSATION_EXECUTION", pointer, "Workflow compensation execution must remain disabled for the selected realization");
  }
  if (marker(content, "domainspec-compensation-contract", pointer) !== '"forward-recovery-operation/v2"') {
    fail("MTCLI_WORKFLOW_COMPENSATION_CONTRACT", pointer, "Workflow must expose the selected forward-recovery Operation contract");
  }
  if (marker(content, "domainspec-compensation-order", pointer) !== '"explicit-dependency-graph-with-reverse-completion-default"') {
    fail("MTCLI_WORKFLOW_COMPENSATION_ORDER", pointer, "Workflow compensation ordering contract drifted");
  }
  if (marker(content, "domainspec-compensation-executor-owner", pointer) !== '"external-runtime"') {
    fail("MTCLI_WORKFLOW_COMPENSATION_EXECUTOR", pointer, "compensation executor must remain outside Workflow evaluation");
  }
  if (marker(content, "domainspec-compensation-operation-role", pointer) !== '"Operation"') {
    fail("MTCLI_WORKFLOW_COMPENSATION_RELATIONSHIP", pointer, "compensation targets must remain Operations");
  }
  const name = pascal(receipt.input.node_id);
  const fn = receipt.language === "typescript" ? lowerCamel(receipt.input.node_id) : snake(receipt.input.node_id);
  const fragments = {
    typescript: [`export async function ${fn}(run:`, "void compensate;", `plan${name}Recovery`, `execute${name}Recovery`, "const registry = new Map", "compensationExecution: false", "directEffectsExecuted"],
    python: [`def ${fn}(run, compensate, workflow_execution_id: str, failure_occurrence_id: str, digest)`, "_ = compensate", `def plan_${fn}_recovery`, `def execute_${fn}_recovery`, '"compensation_execution": False', '"direct_effects_executed"'],
    rust: [`pub fn ${fn}(mut run:`, "let _ = &mut compensate;", `pub fn plan_${fn}_recovery`, `pub fn execute_${fn}_recovery`, "compensation_execution: false", "direct_effects_executed"],
  } as const;
  if (fragments[receipt.language].some((fragment) => !content.includes(fragment))) {
    fail("MTCLI_WORKFLOW_COMPENSATION_CALLABLE", pointer, "Workflow does not bind its composition-root compensation callable as a forward-recovery intent");
  }
  const forbiddenInvocations = {
    typescript: "await compensate(recovery",
    python: "compensate(recovery",
    rust: "compensate(value).is_err()",
  } as const;
  if (content.includes(forbiddenInvocations[receipt.language])) {
    fail("MTCLI_WORKFLOW_COMPENSATION_EXECUTION", pointer, "Workflow invokes compensation despite the selected intent-only realization");
  }
}

function stateMachineSemantics(content: string, receipt: InstantiationReceiptV1, pointer: string): void {
  const body = receipt.semantic_contract.body;
  const transitions = Array.isArray(body.transitions) ? body.transitions : [];
  if (marker(content, "domainspec-state-machine-initial", pointer) !== JSON.stringify(body.initial)) {
    fail("MTCLI_STATE_MACHINE_INITIAL", pointer, "State Machine initial state drifted");
  }
  if (canonicalJson(jsonMarker(content, "domainspec-state-machine-transitions", pointer)) !== canonicalJson(transitions)) {
    fail("MTCLI_STATE_MACHINE_TRANSITION_TABLE", pointer, "State Machine transition table drifted");
  }
  if (marker(content, "domainspec-state-machine-event-intents-only", pointer) !== "true") {
    fail("MTCLI_STATE_MACHINE_EFFECT_BOUNDARY", pointer, "State Machine effects must remain declared Event intents only");
  }
  if (marker(content, "domainspec-state-machine-guard-contract", pointer) !== '"rule-reference-callback/v1"') {
    fail("MTCLI_STATE_MACHINE_GUARD_CONTRACT", pointer, "State Machine guards must be evaluated through the declared Rule-reference callback");
  }
  if (marker(content, "domainspec-state-machine-guard-required", pointer) !== "true") {
    fail("MTCLI_STATE_MACHINE_GUARD_CONTRACT", pointer, "State Machine guard evaluation cannot have an allow-by-default bypass");
  }
  if (marker(content, "domainspec-state-machine-source-enforcement", pointer) !== "true") {
    fail("MTCLI_STATE_MACHINE_SOURCE_ENFORCEMENT", pointer, "State Machine source-state enforcement is absent");
  }
  if (marker(content, "domainspec-state-machine-causal-rejections", pointer) !== '["invalid-current-state","undeclared-transition","source-mismatch","guard-rejected"]') {
    fail("MTCLI_STATE_MACHINE_REJECTION_CONTRACT", pointer, "State Machine causal rejection set drifted");
  }
  const fragments = {
    typescript: ["transition.source_state !== current", "evaluateGuard: (guardRef: string) => boolean):", "effectEventRef: transition.effect_event_ref"],
    python: ['transition["source_state"] != current', "transition_id: str, evaluate_guard) ->", '"effect_event_ref": transition["effect_event_ref"]'],
    rust: ["transition.source_state != current", "!evaluate_guard(guard_ref)", "effect_event_ref: transition.effect_event_ref.map(str::to_owned)"],
  } as const;
  const [sourceFragment, guardFragment, effectFragment] = fragments[receipt.language];
  if (!content.includes(sourceFragment)) fail("MTCLI_STATE_MACHINE_SOURCE_ENFORCEMENT", pointer, "generated realization does not enforce the declared source state");
  if (!content.includes(guardFragment) || !content.includes(receipt.language === "rust" ? "!evaluate_guard(guard_ref)" : receipt.language === "python" ? 'not evaluate_guard(transition["guard_ref"])' : "!evaluateGuard(transition.guard_ref)")) fail("MTCLI_STATE_MACHINE_GUARD_CONTRACT", pointer, "generated realization does not require and evaluate the declared guard reference");
  if (!content.includes(effectFragment)) fail("MTCLI_STATE_MACHINE_EFFECT_BOUNDARY", pointer, "generated realization does not return the declared Event intent exactly");
}

function l1Semantics(content: string, receipt: InstantiationReceiptV1, pointer: string): void {
  const body = receipt.semantic_contract.body;
  if (canonicalJson(jsonMarker(content, "domainspec-l1-contract", pointer)) !== canonicalJson({ kind: receipt.input.kind, body })) {
    fail("MTCLI_L1_CONTRACT", pointer, "typed L1 contract marker drifted");
  }
  const language = receipt.language;
  if (receipt.input.kind === "Entity") {
    if (marker(content, "domainspec-entity-identity", pointer) !== JSON.stringify(body.identity_field)) fail("MTCLI_ENTITY_IDENTITY", pointer, "Entity identity marker drifted");
    const fragments = { typescript: "sameIdentity(other:", python: "def same_identity(self, other:", rust: "pub fn same_identity(&self, other: &Self)" } as const;
    if (!content.includes(fragments[language])) fail("MTCLI_ENTITY_IDENTITY", pointer, "Entity identity comparison is absent");
  }
  if (receipt.input.kind === "Value Object") {
    if (marker(content, "domainspec-value-object-structural-equality", pointer) !== "true") fail("MTCLI_VALUE_EQUALITY", pointer, "Value Object structural equality marker drifted");
    const fragments = { typescript: "equals(other:", python: "def equals(self, other:", rust: "pub fn equals(&self, other: &Self)" } as const;
    if (!content.includes(fragments[language])) fail("MTCLI_VALUE_EQUALITY", pointer, "Value Object structural equality is absent");
  }
  if (receipt.input.kind === "Enum") {
    if (canonicalJson(jsonMarker(content, "domainspec-enum-closed-values", pointer)) !== canonicalJson(body.values)) fail("MTCLI_ENUM_CLOSED_VALUES", pointer, "Enum finite value set drifted");
  }
  if (receipt.input.kind === "Event") {
    if (canonicalJson(jsonMarker(content, "domainspec-event-compatibility", pointer)) !== canonicalJson({ event_type: body.event_type, version: body.version })) fail("MTCLI_EVENT_COMPATIBILITY", pointer, "Event type/version compatibility drifted");
    if (marker(content, "domainspec-event-occurred-at-policy", pointer) !== JSON.stringify(body.occurred_at_policy)) fail("MTCLI_EVENT_OCCURRENCE", pointer, "Event occurred-at policy drifted");
    const fragments = { typescript: "Compatible(candidate:", python: "_compatible(candidate_type:", rust: "_compatible(candidate_type: &str" } as const;
    if (!content.includes(fragments[language])) fail("MTCLI_EVENT_COMPATIBILITY", pointer, "Event compatibility predicate is absent");
  }
  if (receipt.input.kind === "Interface") {
    if (marker(content, "domainspec-interface-boundary", pointer) !== JSON.stringify(body.boundary_kind)) fail("MTCLI_INTERFACE_BOUNDARY", pointer, "Interface boundary kind drifted");
    if (canonicalJson(jsonMarker(content, "domainspec-interface-compatibility", pointer)) !== canonicalJson({ version: body.version, direction: body.compatibility })) fail("MTCLI_INTERFACE_COMPATIBILITY", pointer, "Interface compatibility direction drifted");
    const fragments = { typescript: "AcceptsVersion(candidateVersion:", python: "_accepts_version(candidate_version:", rust: "_accepts_version(candidate_version: &str" } as const;
    if (!content.includes(fragments[language])) fail("MTCLI_INTERFACE_COMPATIBILITY", pointer, "Interface compatibility predicate is absent");
  }
}

function observeSemantics(content: string, receipt: InstantiationReceiptV1, pointer: string): void {
  const expectedMeta = {
    baseline_id: receipt.baseline.id,
    baseline_digest: receipt.baseline.digest,
    meta_type_id: receipt.input.meta_type_id,
    meta_type_label: receipt.input.kind,
    language: receipt.language,
    source_sha256: receipt.selected_realization.source.sha256,
    provider_sha256: receipt.selected_realization.provider.sha256,
    binding_sha256: receipt.selected_realization.binding.sha256,
  };
  if (canonicalJson(jsonMarker(content, "domainspec-meta", pointer)) !== canonicalJson(expectedMeta)) fail("MTCLI_OBSERVE_REALIZATION", pointer, "generated realization provenance does not match the receipt");
  if (canonicalJson(jsonMarker(content, "domainspec-body", pointer)) !== canonicalJson(receipt.semantic_contract.body)) fail("MTCLI_OBSERVE_BODY", pointer, "generated body contract does not match the receipt");
  if (canonicalJson(jsonMarker(content, "domainspec-relationships", pointer)) !== canonicalJson(receipt.semantic_contract.relationships)) fail("MTCLI_OBSERVE_RELATIONSHIPS", pointer, "generated relationships do not match the receipt");
  if (receipt.input.kind === "Operation") {
    const body = receipt.semantic_contract.body;
    const expectedSets = { reads: body.reads ?? [], writes: body.writes ?? [], effects: body.effects ?? [] };
    if (canonicalJson(jsonMarker(content, "domainspec-operation-sets", pointer)) !== canonicalJson(expectedSets)) fail("MTCLI_OPERATION_DECLARED_SETS", pointer, "Operation read/write/effect sets drifted");
    if (marker(content, "domainspec-operation-guard", pointer) !== JSON.stringify(body.guard)) fail("MTCLI_OPERATION_GUARD_ORDER", pointer, "Operation guard identity drifted");
    if (marker(content, "domainspec-guard-before-mutation", pointer) !== "true") fail("MTCLI_OPERATION_GUARD_ORDER", pointer, "guard-before-mutation obligation is absent");
    if (marker(content, "domainspec-atomic-state-outbox", pointer) !== "true") fail("MTCLI_OPERATION_ATOMICITY", pointer, "atomic state-and-outbox obligation is absent");
    if (marker(content, "domainspec-failure-continuation", pointer) !== JSON.stringify(body.failure_continuation)) fail("MTCLI_OPERATION_CONTINUATION", pointer, "failure continuation drifted");
    if (receipt.semantic_contract.typed_closure !== undefined) {
      if (marker(content, "domainspec-typed-closure-sha256", pointer) !== JSON.stringify(receipt.semantic_contract.typed_closure.closure_sha256)) fail("MTCLI_TYPED_CLOSURE_DRIFT", pointer, "typed closure identity drifted");
      if (content.includes("guard: bool")) fail("MTCLI_TYPED_EXTERNAL_GUARD", pointer, "typed Operation must derive its guard from the bound Rule closure");
    } else {
      operationOrder(content, receipt.language, pointer);
      operationStateConstruction(content, receipt, pointer);
      operationEffectConstruction(content, receipt, pointer);
      operationInstrumentationBoundary(content, receipt, pointer);
    }
    operationCreationTargets(content, receipt, pointer);
  }
  if (receipt.input.kind === "Workflow") workflowCompensation(content, receipt, pointer);
  if (receipt.input.kind === "State Machine") stateMachineSemantics(content, receipt, pointer);
  if (receipt.semantic_contract.body.typed_contract === undefined && ["Entity", "Value Object", "Enum", "Event", "Interface"].includes(receipt.input.kind)) l1Semantics(content, receipt, pointer);
}

function expectedImplementation(receipt: InstantiationReceiptV1): string {
  const rendered = renderImplementation({
    project_id: receipt.input.project_id,
    feature_id: receipt.input.feature_id,
    node_id: receipt.input.node_id,
    kind: receipt.input.kind,
    meta_type_id: receipt.input.meta_type_id,
    body: receipt.semantic_contract.body,
    relationships: receipt.semantic_contract.relationships,
    realization: receipt.selected_realization,
    typed_closure: receipt.semantic_contract.typed_closure ?? null,
  });
  if (rendered.generator_id !== receipt.generator_id) fail("MTCLI_OBSERVE_GENERATOR", "/generator_id", "receipt generator is not the closed selected-row generator");
  return rendered.content;
}

export interface TargetObservationV1 {
  readonly schema_version: "domainspec.target-observation/v1";
  readonly result: "pass";
  readonly target_root: string;
  readonly receipt_path: string;
  readonly receipt_sha256: string;
  readonly observed_artifacts: readonly { readonly relative_path: string; readonly size_bytes: number; readonly sha256: string }[];
  readonly checks: readonly string[];
  readonly authority_effect: "none";
}

export interface TargetObservationFailureV1 {
  readonly schema_version: "domainspec.target-observation/v1";
  readonly result: "fail";
  readonly target_root: string;
  readonly code: string;
  readonly pointer: string;
  readonly message: string;
  readonly authority_effect: "none";
}

export type TargetObservationReceiptV1 = TargetObservationV1 | TargetObservationFailureV1;

export function observeTarget(targetRoot: unknown): TargetObservationV1 {
  const root = normalizeTargetRoot(targetRoot);
  const receiptPath = discoverReceiptPath(root);
  const receipt = readInstantiationReceipt(root, receiptPath);
  const expectedFiles = [...receipt.artifacts.map((artifact) => artifact.relative_path), receiptPath].sort();
  const actualFiles = walkFiles(root).sort();
  if (canonicalJson(actualFiles) !== canonicalJson(expectedFiles)) fail("MTCLI_OBSERVE_UNDECLARED_OUTPUT", "/target-root", "target file inventory does not exactly match the receipt");
  const integrationPath = receipt.system_integration?.generated_relative_path ?? null;
  const observed = receipt.artifacts.map((artifact) => {
    const absolute = path.join(root, artifact.relative_path);
    const stats = fs.lstatSync(absolute);
    if (stats.isSymbolicLink() || !stats.isFile()) fail("MTCLI_OBSERVE_FILE_TYPE", `/${artifact.relative_path}`, "artifact is not a regular file");
    const bytes = fs.readFileSync(absolute);
    const content = bytes.toString("utf8");
    if (artifact.relative_path === integrationPath && receipt.system_integration !== null) {
      verifySystemIntegrationContract(content, receipt.system_integration.manifest);
      if (content !== renderSystemIntegrationContract(receipt.system_integration.manifest)) fail("MTCLI_OBSERVE_EXACT_INTEGRATION_PROFILE", `/${artifact.relative_path}`, "artifact is not the exact deterministic output for the selected system-integration profile");
    } else if (artifact.relative_path === "Cargo.toml" && receipt.semantic_contract.typed_closure !== undefined && receipt.language === "rust") {
      const libraryPath = `src/domainspec/rust/${receipt.input.feature_id}/${receipt.input.node_id}.rs`;
      if (content !== renderTypedRustCrateManifest(receipt.input.project_id, receipt.input.feature_id, receipt.input.node_id, libraryPath)) fail("MTCLI_OBSERVE_TYPED_CRATE", `/${artifact.relative_path}`, "Cargo manifest is not the exact deterministic typed Rust crate manifest");
    } else {
      observeSemantics(content, receipt, `/${artifact.relative_path}`);
      if (content !== expectedImplementation(receipt)) fail("MTCLI_OBSERVE_EXACT_REALIZATION", `/${artifact.relative_path}`, "artifact is not the exact deterministic implementation for the selected frozen row");
    }
    if (bytes.length !== artifact.size_bytes || sha256(bytes) !== artifact.sha256) fail("MTCLI_OBSERVE_ARTIFACT_DIGEST", `/${artifact.relative_path}`, "artifact bytes do not match the receipt");
    return Object.freeze({ relative_path: artifact.relative_path, size_bytes: bytes.length, sha256: sha256(bytes) });
  });
  return Object.freeze({
    schema_version: "domainspec.target-observation/v1",
    result: "pass",
    target_root: root,
    receipt_path: receiptPath,
    receipt_sha256: receipt.receipt_sha256,
    observed_artifacts: Object.freeze(observed),
    checks: Object.freeze(["exact-file-inventory", "frozen-realization-provenance", "closed-body-contract", "relationship-contract", "relationship-generated-projections", "operation-obligations-when-applicable", "operation-boundary-placement-when-applicable", "typed-rust-crate-when-selected", "workflow-obligations-when-applicable", "state-machine-obligations-when-applicable", "l1-typed-role-obligations-when-applicable", "system-integration-profile-when-selected", "artifact-digests"]),
    authority_effect: "none",
  });
}

export function observeTargetReceipt(targetRoot: unknown): TargetObservationReceiptV1 {
  try {
    return observeTarget(targetRoot);
  } catch (error) {
    const candidate = error as Partial<Error> & { code?: unknown; pointer?: unknown };
    return Object.freeze({
      schema_version: "domainspec.target-observation/v1",
      result: "fail",
      target_root: typeof targetRoot === "string" ? targetRoot : String(targetRoot),
      code: typeof candidate.code === "string" ? candidate.code : "MTCLI_OBSERVE_UNEXPECTED",
      pointer: typeof candidate.pointer === "string" ? candidate.pointer : "$",
      message: error instanceof Error ? error.message : "unexpected target observation failure",
      authority_effect: "none",
    });
  }
}
