import { createMetaTypeFormalizationProjection } from "../formalization/projection.js";
import { loadCompiledProjectGraph, loadProjectNode } from "../input/project-model.js";
import { canonicalJson, sha256, type SourceManifestV1 } from "../input/source-manifest.js";
import type { SupportedLanguage } from "../meta-types/types.js";
import type { GraphBoundCertificate } from "../formalization/refinement.js";
import type { InstantiationPlanV1, PlannedArtifact } from "./contracts.js";
import { planInstantiation } from "./plan-instantiation.js";
import type { SelectedReconciledCompilation as ReconciledCompilationSelection } from "./selected-reconciled-project.js";
import { planReconciledProjectInstantiation, type ReconciledProjectInstantiationPlan } from "./reconciled-instantiation.js";

export interface ProjectInstantiationPlanV1 {
  readonly schema_version: "domainspec.project-instantiation-plan/v1";
  readonly project_id: string;
  readonly source_manifest: SourceManifestV1;
  readonly languages: readonly SupportedLanguage[];
  readonly node_count: number;
  readonly plan_count: number;
  readonly plans: readonly InstantiationPlanV1[];
  readonly artifacts: readonly PlannedArtifact[];
  readonly graph_certificate: GraphBoundCertificate;
  readonly project_plan_sha256: string;
  readonly authority_effect: "none";
}

export class ProjectInstantiationError extends Error {
  readonly exitCode = 22;
  constructor(readonly code: string, message: string) { super(message); this.name = "ProjectInstantiationError"; }
}

function fail(code: string, message: string): never { throw new ProjectInstantiationError(code, message); }

function projectArtifact(plan: InstantiationPlanV1, artifact: PlannedArtifact): PlannedArtifact {
  if (artifact.relative_path !== "Cargo.toml") return artifact;
  const relativePath = `.domainspec/rust-crates/${plan.input.feature_id}.${plan.input.node_id}/Cargo.toml`;
  const content = artifact.content.replace('path = "src/', 'path = "../../../src/');
  return Object.freeze({ relative_path: relativePath, content, size_bytes: Buffer.byteLength(content), sha256: sha256(content) });
}

export function planProjectInstantiation(sourceRoot: string, languages: readonly SupportedLanguage[], compilationSelection: ReconciledCompilationSelection): ReconciledProjectInstantiationPlan;
export function planProjectInstantiation(sourceRoot: string, languages: readonly SupportedLanguage[], compilationSelection?: undefined): ProjectInstantiationPlanV1;
export function planProjectInstantiation(sourceRoot: string, languages: readonly SupportedLanguage[], compilationSelection: ReconciledCompilationSelection | undefined): ProjectInstantiationPlanV1 | ReconciledProjectInstantiationPlan;
export function planProjectInstantiation(sourceRoot: string, languages: readonly SupportedLanguage[], compilationSelection?: unknown): ProjectInstantiationPlanV1 | ReconciledProjectInstantiationPlan {
  if (compilationSelection !== undefined) return planReconciledProjectInstantiation(sourceRoot, languages, compilationSelection);
  const uniqueLanguages = [...new Set(languages)].sort();
  if (uniqueLanguages.length === 0) fail("MTCLI_PROJECT_LANGUAGE", "project instantiation requires at least one language");
  const graph = loadCompiledProjectGraph(sourceRoot);
  if(graph.compositions?.length)fail("DS_PROJECT_COMPOSITION", "use build with the TypeScript exact UInt64 profile for compositions");
  const selectors = graph.nodes.map(({ selector }) => selector).sort();
  const plans = Object.freeze(selectors.flatMap((selector) => {
    const node = loadProjectNode(sourceRoot, selector);
    if (node.source_manifest.manifest_sha256 !== graph.source_manifest.manifest_sha256 || node.source_manifest.aggregate_sha256 !== graph.source_manifest.aggregate_sha256) {
      fail("MTCLI_PROJECT_SOURCE_DRIFT", `source project changed while planning:${selector}`);
    }
    return uniqueLanguages.map((language) => planInstantiation(node, language));
  }));
  const artifacts = Object.freeze(plans.flatMap((plan) => plan.artifacts.map((artifact) => projectArtifact(plan, artifact))).sort((left, right) => left.relative_path.localeCompare(right.relative_path)));
  const paths = new Set<string>();
  for (const artifact of artifacts) {
    if (paths.has(artifact.relative_path)) fail("MTCLI_PROJECT_ARTIFACT_COLLISION", `project artifact collision:${artifact.relative_path}`);
    paths.add(artifact.relative_path);
  }
  const finalGraph = loadCompiledProjectGraph(sourceRoot);
  if (finalGraph.source_manifest.manifest_sha256 !== graph.source_manifest.manifest_sha256 || finalGraph.source_manifest.aggregate_sha256 !== graph.source_manifest.aggregate_sha256) {
    fail("MTCLI_PROJECT_SOURCE_DRIFT", "source project changed during whole-project planning");
  }
  const certificate = createMetaTypeFormalizationProjection(graph).render_payload.graph_certificate;
  const body = Object.freeze({ schema_version: "domainspec.project-instantiation-plan/v1" as const, project_id: graph.project_id, source_manifest: graph.source_manifest, languages: Object.freeze(uniqueLanguages), node_count: selectors.length, plan_count: plans.length, plans, artifacts, graph_certificate: certificate, authority_effect: "none" as const });
  return Object.freeze({ ...body, project_plan_sha256: sha256(canonicalJson(body)) });
}
