import {APPLICATION_LAYOUT, PROJECT_LAYOUT, applicationArtifactPath, validateOutputLayout, type OutputLayout} from "./output-layout.js";
import {renderRustComposition} from "./rust-composition.js";
import { validateRealizationProfile, type RealizationProfile } from "./exact-uint64.js";
import {publishAtomicDirectory} from './atomic-publication.js';
import fs from "node:fs";
import path from "node:path";

import { createCompiledProjectCertificate, type CompiledProjectCertificateV1 } from "../compilation/certificate.js";
import { createMetaTypeFormalizationProjection, formalizationProjectionSha256 } from "../formalization/projection.js";
import { canonicalJson, sha256 } from "../input/source-manifest.js";
import { assertCompiledProjectSnapshot, loadCompiledProjectGraph, selectCompiledProjectNode, type CompiledProjectGraph } from "../input/project-model.js";
import type { SupportedLanguage } from "../meta-types/types.js";
import type { PlannedArtifact } from "./contracts.js";
import { planInstantiation } from "./plan-instantiation.js";
import { planSelectedReconciledProject as planReconciledProject, planCompiledSelectedReconciledProject as planCompiledReconciledProject, type SelectedReconciledCompilation as ReconciledCompilationSelection } from "./selected-reconciled-project.js";
import { verifyReconciledProject } from "./reconciled-output.js";
import { createReconciledBuild, selectReconciledBuild, publishReconciledBuild, type ReconciledBuildPlan, type ReconciledBuildPublication } from "./reconciled-build.js";

export type SelectedProjectBuildPlan = ProjectBuildPlanV1 | ReconciledBuildPlan;
export type ProjectBuildPublicationV1 = Readonly<{ target_root: string; receipt_path: string; receipt: ProjectBuildReceiptV1 }>;
export type ReconciledBuildVerification = ReturnType<typeof verifyReconciledProject>;

const RECEIPT_PATH = ".domainspec/project-build.json";

export interface ProjectBuildReceiptV1 {
  readonly output_layout?: typeof APPLICATION_LAYOUT.id;
  readonly realization_profile?: RealizationProfile;
  readonly schema_version: "domainspec.project-build-receipt/v1";
  readonly project_id: string;
  readonly language: SupportedLanguage;
  readonly source_manifest_sha256: string;
  readonly compiled_certificate: CompiledProjectCertificateV1;
  readonly formalization_projection_sha256: string;
  readonly node_selectors: readonly string[];
  readonly artifacts: readonly Omit<PlannedArtifact, "content">[];
  readonly authority_effect: "none";
  readonly receipt_sha256: string;
}

export interface ProjectBuildPlanV1 {
  readonly receipt: ProjectBuildReceiptV1;
  readonly artifacts: readonly PlannedArtifact[];
}

export class ProjectBuildError extends Error {
  readonly exitCode = 22;
  constructor(readonly code: string, readonly pointer: string, message: string) { super(message); this.name = "ProjectBuildError"; }
}

function fail(code: string, pointer: string, message: string): never { throw new ProjectBuildError(code, pointer, message); }

function assertTarget(targetRoot: unknown): { readonly target: string; readonly parent: string } {
  if (typeof targetRoot !== "string" || !path.isAbsolute(targetRoot) || path.resolve(targetRoot) !== targetRoot) fail("MTCLI_PROJECT_BUILD_ROOT", "/target-root", "target root must be a normalized absolute path");
  if (fs.existsSync(targetRoot)) fail("MTCLI_PROJECT_BUILD_EXISTS", "/target-root", "target root already exists");
  const parent = path.dirname(targetRoot);
  let stat: fs.Stats;
  try { stat = fs.lstatSync(parent); } catch { fail("MTCLI_PROJECT_BUILD_PARENT", "/target-root", "target parent does not exist"); }
  if (!stat.isDirectory() || stat.isSymbolicLink() || fs.realpathSync(parent) !== parent) fail("MTCLI_PROJECT_BUILD_PARENT", "/target-root", "target parent must be a real directory");
  return Object.freeze({ target: targetRoot, parent });
}

export function planProjectBuild(sourceRoot: string, language: SupportedLanguage, realizationProfile: RealizationProfile | undefined, outputLayout: OutputLayout | undefined, compilationSelection: ReconciledCompilationSelection): ReconciledBuildPlan;
export function planProjectBuild(sourceRoot: string, language: SupportedLanguage, realizationProfile?: RealizationProfile, outputLayout?: OutputLayout, compilationSelection?: undefined): ProjectBuildPlanV1;
export function planProjectBuild(sourceRoot: string, language: SupportedLanguage, realizationProfile: RealizationProfile | undefined, outputLayout: OutputLayout | undefined, compilationSelection: ReconciledCompilationSelection | undefined): SelectedProjectBuildPlan;
export function planProjectBuild(sourceRoot: string, language: SupportedLanguage, realizationProfile?: RealizationProfile, outputLayout?: OutputLayout, compilationSelection?: unknown): SelectedProjectBuildPlan {
  if (compilationSelection !== undefined) {
    const selection = selectReconciledBuild(language, realizationProfile, outputLayout, compilationSelection);
    return createReconciledBuild(planReconciledProject(sourceRoot, selection),outputLayout);
  }
  if (outputLayout === PROJECT_LAYOUT.id) fail("DS_PROJECT_LAYOUT_SELECTION", "/compilation-selection", "project layout requires a reconciled compilation selection");
  const graph = loadCompiledProjectGraph(sourceRoot);
  const plan = planCompiledProjectBuild(graph, language, realizationProfile, outputLayout);
  const finalGraph = loadCompiledProjectGraph(sourceRoot);
  if (finalGraph.source_manifest.manifest_sha256 !== graph.source_manifest.manifest_sha256) fail('MTCLI_PROJECT_SOURCE_DRIFT', '/sources', 'project changed during build planning');
  return plan;
}

/** Generation from one validated snapshot; no project source files are reloaded. */
export function planCompiledProjectBuild(graph: CompiledProjectGraph, language: SupportedLanguage, realizationProfile: RealizationProfile | undefined, outputLayout: OutputLayout | undefined, compilationSelection: ReconciledCompilationSelection): ReconciledBuildPlan;
export function planCompiledProjectBuild(graph: CompiledProjectGraph, language: SupportedLanguage, realizationProfile?: RealizationProfile, outputLayout?: OutputLayout, compilationSelection?: undefined): ProjectBuildPlanV1;
export function planCompiledProjectBuild(graph: CompiledProjectGraph, language: SupportedLanguage, realizationProfile: RealizationProfile | undefined, outputLayout: OutputLayout | undefined, compilationSelection: ReconciledCompilationSelection | undefined): SelectedProjectBuildPlan;
export function planCompiledProjectBuild(graph: CompiledProjectGraph, language: SupportedLanguage, realizationProfile?: RealizationProfile, outputLayout?: OutputLayout, compilationSelection?: unknown): SelectedProjectBuildPlan {
  if (compilationSelection !== undefined) {
    const selection = selectReconciledBuild(language, realizationProfile, outputLayout, compilationSelection);
    return createReconciledBuild(planCompiledReconciledProject(graph, selection),outputLayout);
  }
  if (outputLayout === PROJECT_LAYOUT.id) fail("DS_PROJECT_LAYOUT_SELECTION", "/compilation-selection", "project layout requires a reconciled compilation selection");
  assertCompiledProjectSnapshot(graph);
  validateRealizationProfile(realizationProfile, language);
  validateOutputLayout(outputLayout);
  if(graph.compositions?.some(c=>c.source.model.endpoint.target==="rust-http" ? language!=="rust" || realizationProfile!==undefined : language!=="typescript" || realizationProfile!=="domainspec.typescript-exact-uint64/v1")) fail("DS_PROJECT_COMPOSITION", "/language", "composition requires its declared target: TypeScript exact UInt64 or native Rust");
  const compiledCertificate = createCompiledProjectCertificate(graph);
  const formalizationProjection = createMetaTypeFormalizationProjection(graph);
  const artifacts: PlannedArtifact[] = [];
  const paths = new Set<string>();
  for (const node of graph.nodes) {
    const plan = planInstantiation(selectCompiledProjectNode(graph, node.selector), language, null, realizationProfile);
    for (const artifact of plan.artifacts) {
      if (artifact.relative_path === "Cargo.toml") continue;
      const relative_path=outputLayout === APPLICATION_LAYOUT.id?applicationArtifactPath(artifact.relative_path):artifact.relative_path;
      if (paths.has(relative_path)) fail("MTCLI_PROJECT_BUILD_COLLISION", `/nodes/${node.selector}`, `artifact collision:${artifact.relative_path}`);
      paths.add(relative_path);
      artifacts.push({...artifact,relative_path});
    }
  }
  for(const composition of graph.compositions??[])for(const [name,content]of Object.entries(outputLayout && composition.source.model.endpoint.target==='rust-http' ? {...composition.artifacts,...renderRustComposition(composition.source.contract,composition.source.core_bindings,composition.source.model,composition.id)} : composition.artifacts)) {
    const original=`compositions/${composition.id}/${name}`;
    const relative_path=outputLayout === APPLICATION_LAYOUT.id?applicationArtifactPath(original):original;
    if(paths.has(relative_path))fail('MTCLI_PROJECT_BUILD_COLLISION','/compositions',relative_path);
    paths.add(relative_path);artifacts.push({relative_path,content,size_bytes:Buffer.byteLength(content),sha256:sha256(content)});
  }
  artifacts.sort((left, right) => left.relative_path.localeCompare(right.relative_path));
  const inventory = Object.freeze(artifacts.map(({ relative_path, size_bytes, sha256: digest }) => Object.freeze({ relative_path, size_bytes, sha256: digest })));
  const body = {
    ...(outputLayout ? {output_layout: outputLayout} : {}),
    ...(realizationProfile ? { realization_profile: realizationProfile } : {}),
    schema_version: "domainspec.project-build-receipt/v1" as const,
    project_id: graph.project_id,
    language,
    source_manifest_sha256: graph.source_manifest.manifest_sha256,
    compiled_certificate: compiledCertificate,
    formalization_projection_sha256: formalizationProjectionSha256(formalizationProjection),
    node_selectors: Object.freeze(graph.nodes.map(({ selector }) => selector)),
    artifacts: inventory,
    authority_effect: "none" as const,
  };
  return Object.freeze({ artifacts: Object.freeze(artifacts), receipt: Object.freeze({ ...body, receipt_sha256: sha256(canonicalJson(body)) }) });
}

export function publishProjectBuild(plan: ReconciledBuildPlan, targetRoot: unknown): ReconciledBuildPublication;
export function publishProjectBuild(plan: ProjectBuildPlanV1, targetRoot: unknown): ProjectBuildPublicationV1;
export function publishProjectBuild(plan: SelectedProjectBuildPlan, targetRoot: unknown): ProjectBuildPublicationV1 | ReconciledBuildPublication;
export function publishProjectBuild(plan: SelectedProjectBuildPlan, targetRoot: unknown): ProjectBuildPublicationV1 | ReconciledBuildPublication {
  if ('schema_version' in plan || 'project' in plan || 'definition_sha256' in plan || 'plan_sha256' in plan || plan.receipt.schema_version !== 'domainspec.project-build-receipt/v1') return publishReconciledBuild(plan, targetRoot);
  const { target } = assertTarget(targetRoot);
  try {
    publishAtomicDirectory(target,[...plan.artifacts,{relative_path:plan.receipt.output_layout ? APPLICATION_LAYOUT.receipt : RECEIPT_PATH,content:`${canonicalJson(plan.receipt)}\n`}],'.domainspec-project-');
  } catch (error) {
    if ((error as NodeJS.ErrnoException).code==='DS_ATOMIC_EXISTS')fail("MTCLI_PROJECT_BUILD_EXISTS", "/target-root", "target root appeared during publication");
    if ((error as NodeJS.ErrnoException).code==='DS_ATOMIC_PATH')fail("MTCLI_PROJECT_BUILD_PATH", "/artifacts", "artifact path is not normalized and contained");
    if ((error as NodeJS.ErrnoException).code==='DS_NATIVE_PERMISSION')fail("MTCLI_PROJECT_BUILD_UNAVAILABLE", "/target-root", (error as Error).message);
    if (error instanceof ProjectBuildError) throw error;
    fail("MTCLI_PROJECT_BUILD_ATOMIC", "/target-root", error instanceof Error ? error.message : "atomic publication failed");
  }
  return Object.freeze({ target_root: target, receipt_path: plan.receipt.output_layout ? APPLICATION_LAYOUT.receipt : RECEIPT_PATH, receipt: plan.receipt });
}

export interface ProjectBuildVerificationV1 {
  readonly schema_version: "domainspec.project-build-verification/v1";
  readonly result: "pass" | "fail";
  readonly checks: readonly Readonly<{ id: string; result: "pass" | "fail" }>[];
  readonly expected_receipt_sha256: string;
  readonly observed_receipt_sha256: string | null;
  readonly authority_effect: "none";
}

export function verifyProjectBuild(sourceRoot: string, language: SupportedLanguage, targetRoot: string, realizationProfile: RealizationProfile | undefined, outputLayout: OutputLayout | undefined, compilationSelection: ReconciledCompilationSelection): ReconciledBuildVerification;
export function verifyProjectBuild(sourceRoot: string, language: SupportedLanguage, targetRoot: string, realizationProfile?: RealizationProfile, outputLayout?: OutputLayout, compilationSelection?: undefined): ProjectBuildVerificationV1;
export function verifyProjectBuild(sourceRoot: string, language: SupportedLanguage, targetRoot: string, realizationProfile: RealizationProfile | undefined, outputLayout: OutputLayout | undefined, compilationSelection: ReconciledCompilationSelection | undefined): ProjectBuildVerificationV1 | ReconciledBuildVerification;
export function verifyProjectBuild(sourceRoot: string, language: SupportedLanguage, targetRoot: string, realizationProfile?: RealizationProfile, outputLayout?: OutputLayout, compilationSelection?: unknown): ProjectBuildVerificationV1 | ReconciledBuildVerification {
  if (compilationSelection !== undefined) {
    const selection = selectReconciledBuild(language, realizationProfile, outputLayout, compilationSelection);
    const expected = planProjectBuild(sourceRoot, language, realizationProfile, outputLayout, selection);
    return verifyReconciledProject(expected.project, targetRoot,null,outputLayout);
  }
  const expected = planProjectBuild(sourceRoot, language, realizationProfile, outputLayout);
  const receiptPath=outputLayout?APPLICATION_LAYOUT.receipt:RECEIPT_PATH;
  const checks: Array<{ id: string; result: "pass" | "fail" }> = [];
  let observedReceipt: ProjectBuildReceiptV1 | null = null;
  try { observedReceipt = JSON.parse(fs.readFileSync(path.join(targetRoot, receiptPath), "utf8")) as ProjectBuildReceiptV1; } catch { /* recorded below */ }
  checks.push({ id: "receipt-current", result: observedReceipt !== null && canonicalJson(observedReceipt) === canonicalJson(expected.receipt) ? "pass" : "fail" });
  for (const artifact of expected.artifacts) {
    let current = false;
    try { const bytes = fs.readFileSync(path.join(targetRoot, artifact.relative_path)); current = bytes.length === artifact.size_bytes && sha256(bytes) === artifact.sha256; } catch { /* recorded below */ }
    checks.push({ id: `artifact:${artifact.relative_path}`, result: current ? "pass" : "fail" });
  }
  const expectedPaths = new Set([receiptPath, ...expected.artifacts.map(({ relative_path }) => relative_path)]);
  const observedPaths: string[] = [];
  if (fs.existsSync(targetRoot)) {
    const walk = (directory: string): void => { for (const entry of fs.readdirSync(directory, { withFileTypes: true })) { const absolute = path.join(directory, entry.name); if (entry.isDirectory()) walk(absolute); else observedPaths.push(path.relative(targetRoot, absolute).split(path.sep).join("/")); } };
    walk(targetRoot);
  }
  checks.push({ id: "artifact-set-exact", result: observedPaths.length === expectedPaths.size && observedPaths.every((candidate) => expectedPaths.has(candidate)) ? "pass" : "fail" });
  return Object.freeze({
    schema_version: "domainspec.project-build-verification/v1",
    result: checks.every(({ result }) => result === "pass") ? "pass" : "fail",
    checks: Object.freeze(checks.map((check) => Object.freeze(check))),
    expected_receipt_sha256: expected.receipt.receipt_sha256,
    observed_receipt_sha256: observedReceipt?.receipt_sha256 ?? null,
    authority_effect: "none",
  });
}
