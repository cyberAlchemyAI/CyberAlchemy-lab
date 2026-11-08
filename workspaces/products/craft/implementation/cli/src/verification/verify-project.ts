import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { spawnSync } from "node:child_process";

import { checkLeanMetaTypeFormalization, createMetaTypeFormalizationProjection, materializeLeanMetaTypeFormalization } from "../formalization/projection.js";
import { validateGraphBoundCertificate } from "../formalization/refinement.js";
import { planProjectInstantiation, type ProjectInstantiationPlanV1 } from "../generation/project-instantiation.js";
import { publishProjectInstantiation, type ProjectPublicationResult } from "../generation/publish-project.js";
import { SUBPROCESS_TIMEOUT_MS } from "../input/limits.js";
import { loadCompiledProjectGraph, validateCompiledProjectGraphObligations } from "../input/project-model.js";
import { canonicalJson, sha256 } from "../input/source-manifest.js";
import { SUPPORTED_LANGUAGES } from "../meta-types/types.js";
import {verifyReconciledPythonSourceProject,verifyReconciledRustSourceProject,verifyReconciledSourceProject} from './reconciled-project.js';
import {validateReconciledVerificationTools,type ReconciledVerificationTools,type ReconciledVerificationExecution} from './reconciled-execution.js';
import type {ReconciledCompilationSelection} from '../generation/reconciled-project.js';
import {decodeSelectedReconciledCompilation,type SelectedReconciledCompilation} from '../generation/selected-reconciled-project.js';
import {validatePythonVerificationOptions,type PythonVerificationOptions,type PythonVerification} from './reconciled-python-native.js';
import {validateRustVerificationOptions,type RustVerificationOptions} from './reconciled-rust-native.js';

export interface ProjectVerificationReceiptV1 {
  readonly schema_version: "domainspec.project-verification-receipt/v1";
  readonly result: "pass";
  readonly project_id: string;
  readonly source_manifest_sha256: string;
  readonly project_plan_sha256: string;
  readonly publication_receipt_sha256: string;
  readonly graph_certificate: ProjectInstantiationPlanV1["graph_certificate"];
  readonly checks: readonly Readonly<{ readonly id: string; readonly result: "pass"; readonly evidence: Readonly<Record<string, unknown>> }>[];
  readonly skipped_check_count: 0;
  readonly inferred_evidence_count: 0;
  readonly authority_effect: "none";
}

export class ProjectVerificationError extends Error {
  readonly exitCode = 22;
  constructor(readonly code: string, message: string) { super(message); this.name = "ProjectVerificationError"; }
}

function fail(code: string, message: string): never { throw new ProjectVerificationError(code, message); }

function exactSourceReplay(sourceRoot: string, plan: ProjectInstantiationPlanV1, replayRoot: string): void {
  for (const source of plan.source_manifest.sources) {
    const input = path.join(sourceRoot, source.relative_path);
    const bytes = fs.readFileSync(input);
    if (bytes.byteLength !== source.size_bytes || sha256(bytes) !== source.sha256) fail("MTCLI_VERIFY_SOURCE_DRIFT", `source changed before isolated replay:${source.relative_path}`);
    const output = path.join(replayRoot, source.relative_path);
    fs.mkdirSync(path.dirname(output), { recursive: true });
    fs.copyFileSync(input, output, fs.constants.COPYFILE_EXCL);
  }
}

function verifyPublishedArtifacts(publication: ProjectPublicationResult, plan: ProjectInstantiationPlanV1): void {
  const receiptPath = path.join(publication.target_root, publication.receipt_path);
  const receiptBytes = fs.readFileSync(receiptPath, "utf8");
  if (receiptBytes !== `${canonicalJson(publication.receipt)}\n`) fail("MTCLI_VERIFY_RECEIPT", "publication receipt bytes do not match the in-process receipt");
  const { receipt_sha256: claimedReceiptSha256, ...receiptBody } = publication.receipt;
  if (sha256(canonicalJson(receiptBody)) !== claimedReceiptSha256) fail("MTCLI_VERIFY_RECEIPT", "publication receipt digest is stale");
  for (const artifact of plan.artifacts) {
    const bytes = fs.readFileSync(path.join(publication.target_root, artifact.relative_path));
    if (bytes.byteLength !== artifact.size_bytes || sha256(bytes) !== artifact.sha256) fail("MTCLI_VERIFY_ARTIFACT", `published artifact differs from its plan:${artifact.relative_path}`);
  }
}

interface ArtifactValidationEvidence {
  readonly typescript_count: number;
  readonly python_count: number;
  readonly rust_count: number;
  readonly cargo_manifest_count: number;
  readonly validators: Readonly<{ readonly typescript: string; readonly python: string; readonly rust: string; readonly cargo: string }>;
}

function executable(name: string, environmentName: string, localCandidates: readonly string[] = []): string {
  const configured = process.env[environmentName];
  if (configured) {
    if (!path.isAbsolute(configured) || !fs.existsSync(configured)) fail("MTCLI_VERIFY_TOOLCHAIN", `${environmentName} must name an existing absolute executable`);
    return configured;
  }
  return localCandidates.find((candidate) => fs.existsSync(candidate)) ?? name;
}

function runValidator(command: string, args: readonly string[], cwd: string, environment: NodeJS.ProcessEnv = process.env): string {
  const result = spawnSync(command, [...args], { cwd, encoding: "utf8", env: environment, timeout: SUBPROCESS_TIMEOUT_MS });
  if (result.error || result.status !== 0) {
    fail("MTCLI_VERIFY_ARTIFACT_COMPILE", `${command} rejected generated artifacts:${result.error?.message ?? (result.stderr || result.stdout || `exit ${result.status}`)}`);
  }
  return (result.stdout || result.stderr).trim();
}

function validateGeneratedArtifacts(plan: ProjectInstantiationPlanV1, validationRoot: string): ArtifactValidationEvidence {
  const artifactRoot = path.join(validationRoot, "generated-artifacts");
  fs.mkdirSync(artifactRoot);
  for (const artifact of plan.artifacts) {
    const target = path.join(artifactRoot, artifact.relative_path);
    fs.mkdirSync(path.dirname(target), { recursive: true });
    fs.writeFileSync(target, artifact.content, { encoding: "utf8", flag: "wx" });
  }
  const typescript = plan.artifacts.filter(({ relative_path }) => relative_path.endsWith(".ts")).map(({ relative_path }) => path.join(artifactRoot, relative_path));
  const python = plan.artifacts.filter(({ relative_path }) => relative_path.endsWith(".py")).map(({ relative_path }) => path.join(artifactRoot, relative_path));
  const rust = plan.artifacts.filter(({ relative_path }) => relative_path.endsWith(".rs")).map(({ relative_path }) => path.join(artifactRoot, relative_path));
  const cargoManifests = plan.artifacts.filter(({ relative_path }) => relative_path.endsWith("Cargo.toml")).map(({ relative_path }) => path.join(artifactRoot, relative_path));
  const tsc = executable("tsc", "DOMAINSPEC_TSC");
  const python3 = executable("python3", "DOMAINSPEC_PYTHON");
  const rustc = executable("rustc", "DOMAINSPEC_RUSTC");
  const cargo = executable("cargo", "DOMAINSPEC_CARGO");
  const typeScriptVersion = runValidator(tsc, ["--version"], artifactRoot);
  const pythonVersion = runValidator(python3, ["--version"], artifactRoot);
  const rustVersion = runValidator(rustc, ["--version"], artifactRoot);
  const cargoVersion = runValidator(cargo, ["--version"], artifactRoot);
  if (typescript.length > 0) runValidator(tsc, ["--noEmit", "--target", "ES2022", "--module", "NodeNext", "--moduleResolution", "NodeNext", "--skipLibCheck", ...typescript], artifactRoot);
  if (python.length > 0) runValidator(python3, ["-m", "py_compile", ...python], artifactRoot, { ...process.env, PYTHONPYCACHEPREFIX: path.join(validationRoot, "pycache") });
  for (const [index, file] of rust.entries()) runValidator(rustc, ["--edition", "2024", "--crate-type", "lib", file, "-o", path.join(validationRoot, `artifact-${index}.rlib`)], artifactRoot);
  for (const manifest of cargoManifests) runValidator(cargo, ["metadata", "--no-deps", "--format-version", "1", "--manifest-path", manifest], artifactRoot, { ...process.env, CARGO_TARGET_DIR: path.join(validationRoot, "cargo-target") });
  if (typescript.length + python.length + rust.length + cargoManifests.length !== plan.artifacts.length) fail("MTCLI_VERIFY_ARTIFACT_KIND", "generated artifact lacks an executable validator");
  return Object.freeze({
    typescript_count: typescript.length,
    python_count: python.length,
    rust_count: rust.length,
    cargo_manifest_count: cargoManifests.length,
    validators: Object.freeze({ typescript: typeScriptVersion, python: pythonVersion, rust: rustVersion, cargo: cargoVersion }),
  });
}

export function verifyProject(sourceRoot:string,targetRoot:string):ProjectVerificationReceiptV1;
export function verifyProject(sourceRoot:string,targetRoot:string,selection:ReconciledCompilationSelection,tools:ReconciledVerificationTools):ReconciledVerificationExecution;
export function verifyProject(sourceRoot:string,targetRoot:string,selection:SelectedReconciledCompilation,tools:ReconciledVerificationTools|PythonVerificationOptions|RustVerificationOptions):ReconciledVerificationExecution|PythonVerification|ReturnType<typeof verifyReconciledRustSourceProject>;
export function verifyProject(sourceRoot:string,targetRoot:string,selection?:SelectedReconciledCompilation,tools?:ReconciledVerificationTools|PythonVerificationOptions|RustVerificationOptions):ProjectVerificationReceiptV1|ReconciledVerificationExecution|PythonVerification|ReturnType<typeof verifyReconciledRustSourceProject> {
  if(selection!==undefined||tools!==undefined){
    if(selection===undefined)fail('DS_RECONCILED_VERIFICATION_ENTRYPOINTS','explicit compilation selection required');
    const selected=decodeSelectedReconciledCompilation(selection);
    if(tools===undefined)fail('DS_RECONCILED_VERIFICATION_ENTRYPOINTS','explicit verification tools required');
    if(selected.language==='python'){
      const options=validatePythonVerificationOptions(tools);
      if(options.target_root!==targetRoot)fail('DS_RECONCILED_VERIFICATION_ENTRYPOINTS','conflicting target roots');
      return verifyReconciledPythonSourceProject(sourceRoot,selected,options);
    }
    if(selected.language==='rust'){
      const options=validateRustVerificationOptions(tools);
      if(options.target_root!==undefined&&options.target_root!==targetRoot)fail('DS_RECONCILED_VERIFICATION_ENTRYPOINTS','conflicting target roots');
      return verifyReconciledRustSourceProject(sourceRoot,selected,validateRustVerificationOptions({...options,target_root:targetRoot}));
    }
    const options=validateReconciledVerificationTools(tools);
    if(options.target_root!==undefined&&options.target_root!==targetRoot)fail('DS_RECONCILED_VERIFICATION_ENTRYPOINTS','conflicting target roots');
    return verifyReconciledSourceProject(sourceRoot,selected,validateReconciledVerificationTools({...options,target_root:targetRoot}));
  }
  const graph = validateCompiledProjectGraphObligations(loadCompiledProjectGraph(sourceRoot));
  const applicable = graph.obligation_applicability.filter(({ classification }) => classification === "applicable");
  const inapplicable = graph.obligation_applicability.filter(({ classification }) => classification === "inapplicable");
  if (graph.obligation_applicability.length !== 28 || graph.obligation_outcomes.some(({ outcome }) => outcome !== "pass")) fail("MTCLI_VERIFY_OBLIGATIONS", "backend DS-D8 applicability or witness outcome denominator is incomplete");

  const plan = planProjectInstantiation(sourceRoot, SUPPORTED_LANGUAGES);
  if (plan.plan_count !== graph.nodes.length * SUPPORTED_LANGUAGES.length) fail("MTCLI_VERIFY_COVERAGE", "whole-project plan does not cover every node-language pair");
  const planPairs = new Set(plan.plans.map(({ input, language }) => `${input.feature_id}:${input.node_id}/${language}`));
  if (planPairs.size !== plan.plan_count) fail("MTCLI_VERIFY_COVERAGE", "whole-project plan contains duplicate or missing node-language pairs");
  const forbiddenRuntimePlaceholders = /(?:NotImplemented|todo!\s*\(|unimplemented!\s*\(|requires authored domainspec)/;
  if (plan.artifacts.some(({ content }) => forbiddenRuntimePlaceholders.test(content))) fail("MTCLI_VERIFY_SKIP", "generated artifact contains a runtime placeholder or semantic skip");

  const verificationRoot = fs.mkdtempSync(path.join(os.tmpdir(), "domainspec-verify-project-"));
  try {
    const isolatedSource = path.join(verificationRoot, "source");
    fs.mkdirSync(isolatedSource);
    exactSourceReplay(sourceRoot, plan, isolatedSource);
    const replay = planProjectInstantiation(isolatedSource, SUPPORTED_LANGUAGES);
    if (replay.project_plan_sha256 !== plan.project_plan_sha256 || canonicalJson(replay.artifacts) !== canonicalJson(plan.artifacts)) fail("MTCLI_VERIFY_REPLAY", "isolated exact-source replay differs from the original project plan");
    const artifactValidation = validateGeneratedArtifacts(plan, verificationRoot);

    const formalizationTarget = path.join(verificationRoot, "formalization", "CurrentVerifiedDomainSpecMetaTypes.lean");
    const formalization = materializeLeanMetaTypeFormalization(graph, formalizationTarget);
    const current = checkLeanMetaTypeFormalization(graph, formalizationTarget);
    if (!current.current) fail("MTCLI_VERIFY_FORMALIZATION", "materialized formalization is not current for the compiled graph");

    const projection = createMetaTypeFormalizationProjection(graph);
    validateGraphBoundCertificate(graph, { nodes: projection.render_payload.project_graph.nodes, edges: projection.render_payload.project_graph.edges }, plan.graph_certificate);
    if (plan.graph_certificate.source_identity.source_manifest_sha256 !== graph.source_manifest.manifest_sha256 || plan.graph_certificate.denominators.node_count !== graph.nodes.length || plan.graph_certificate.denominators.edge_count !== graph.relationships.length) fail("MTCLI_VERIFY_CERTIFICATE", "project certificate is not bound to the source graph denominators");

    const publication = publishProjectInstantiation(plan, targetRoot);
    verifyPublishedArtifacts(publication, plan);
    const checks = Object.freeze([
      Object.freeze({ id: "source", result: "pass" as const, evidence: Object.freeze({ source_count: graph.source_manifest.source_count, source_manifest_sha256: graph.source_manifest.manifest_sha256 }) }),
      Object.freeze({ id: "compiled-graph", result: "pass" as const, evidence: Object.freeze({ node_count: graph.nodes.length, edge_count: graph.relationships.length, graph_sha256: plan.graph_certificate.graph_sha256 }) }),
      Object.freeze({ id: "ds-d8-obligations", result: "pass" as const, evidence: Object.freeze({ denominator: graph.obligation_applicability.length, applicable_count: applicable.length, inapplicable_count: inapplicable.length, witness_count: graph.obligation_outcomes.length }) }),
      Object.freeze({ id: "artifacts", result: "pass" as const, evidence: Object.freeze({ plan_count: plan.plan_count, artifact_count: plan.artifacts.length, language_count: plan.languages.length, ...artifactValidation }) }),
      Object.freeze({ id: "receipts", result: "pass" as const, evidence: Object.freeze({ receipt_sha256: publication.receipt.receipt_sha256 }) }),
      Object.freeze({ id: "formalization-currentness", result: "pass" as const, evidence: Object.freeze({ proof_unit_sha256: formalization.proof_unit_sha256, graph_sha256: formalization.project_graph_sha256 }) }),
      Object.freeze({ id: "isolated-clean-replay", result: "pass" as const, evidence: Object.freeze({ project_plan_sha256: replay.project_plan_sha256 }) }),
      Object.freeze({ id: "no-skips-or-inference", result: "pass" as const, evidence: Object.freeze({ skipped_check_count: 0, inferred_evidence_count: 0 }) }),
    ]);
    return Object.freeze({
      schema_version: "domainspec.project-verification-receipt/v1",
      result: "pass",
      project_id: graph.project_id,
      source_manifest_sha256: graph.source_manifest.manifest_sha256,
      project_plan_sha256: plan.project_plan_sha256,
      publication_receipt_sha256: publication.receipt.receipt_sha256,
      graph_certificate: plan.graph_certificate,
      checks,
      skipped_check_count: 0,
      inferred_evidence_count: 0,
      authority_effect: "none",
    });
  } finally {
    fs.rmSync(verificationRoot, { recursive: true, force: true });
  }
}
