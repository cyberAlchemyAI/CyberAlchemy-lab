import fs from "node:fs";
import path from "node:path";

import type { InstantiationPlanV1, PlannedArtifact } from "../generation/contracts.js";
import { generatorIdFor } from "../generation/generators.js";
import { canonicalJson, sha256 } from "../input/source-manifest.js";
import {
  decodeBody,
  RELATIONSHIP_SIGNATURES,
  withGeneratedRelationshipProjections,
  type DecodedBody,
  type DecodedRelationship,
} from "../input/project-model.js";
import { FROZEN_META_TYPE_CATALOG, metaTypeIdForLabel, selectRealization } from "../meta-types/catalog.js";
import type { CatalogRealizationRow, SupportedLanguage } from "../meta-types/types.js";
import { RELATIONSHIP_AUTHORITY_SHA256, relationshipSignature } from "../relationships/authority.js";
import { generatedSystemIntegrationPath, validateSystemIntegrationManifest } from "../system-integration/compiler.js";
import type { SystemIntegrationReceiptBindingV1 } from "../system-integration/types.js";
import {
  compileTypedOperationClosure,
  compileTypedCalculationClosure,
  compileTypedRuleClosure,
  type TypedClosureSourceNode,
  type TypedNodeContract,
  type TypedOperationClosureV1,
  type TypedSemanticClosureV1,
} from "../typed-operation/closure.js";
import {
  decodeTypedOperationContract,
  decodeTypedRecordContract,
  decodeTypedRuleContract,
  decodeTypedSumContract,
} from "../typed-operation/contracts.js";
import { decodeTypedCalculationContract } from "../typed-backend/contracts.js";

export const RECEIPT_DIRECTORY = ".domainspec/instantiations" as const;

export interface InstantiationReceiptV1 {
  readonly schema_version: "domainspec.instantiation-receipt/v1";
  readonly baseline: {
    readonly id: `domainspec-meta-types-current-implemented@${number}`;
    readonly digest: string;
    readonly manifest_sha256: string;
  };
  readonly input: {
    readonly project_id: string;
    readonly feature_id: string;
    readonly node_id: string;
    readonly kind: string;
    readonly meta_type_id: string;
    readonly source_manifest_sha256: string;
  };
  readonly language: SupportedLanguage;
  readonly selected_realization: CatalogRealizationRow;
  readonly generator_id: string;
  readonly system_integration: SystemIntegrationReceiptBindingV1 | null;
  readonly semantic_contract: {
    readonly body: DecodedBody;
    readonly relationships: readonly DecodedRelationship[];
    readonly relationship_authority_sha256: typeof RELATIONSHIP_AUTHORITY_SHA256;
    readonly typed_closure?: TypedSemanticClosureV1;
  };
  readonly plan_sha256: string;
  readonly artifacts: readonly Omit<PlannedArtifact, "content">[];
  readonly authority_effect: "none";
  readonly receipt_sha256: string;
}

export class ReceiptError extends Error {
  readonly exitCode = 22;

  constructor(readonly code: string, readonly pointer: string, message: string) {
    super(message);
    this.name = "ReceiptError";
  }
}

function fail(code: string, pointer: string, message: string): never {
  throw new ReceiptError(code, pointer, message);
}

function isObject(value: unknown): value is Record<string, unknown> {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}

function exactKeys(value: unknown, expected: readonly string[], pointer: string): asserts value is Record<string, unknown> {
  if (!isObject(value)) fail("MTCLI_RECEIPT_SCHEMA", pointer, "expected object");
  if (canonicalJson(Object.keys(value).sort()) !== canonicalJson([...expected].sort())) {
    fail("MTCLI_RECEIPT_SCHEMA", pointer, "unexpected or missing member");
  }
}

function requireString(value: unknown, pointer: string): string {
  if (typeof value !== "string" || value.length === 0) fail("MTCLI_RECEIPT_SCHEMA", pointer, "expected nonempty string");
  return value;
}

function requireSha(value: unknown, pointer: string): string {
  if (typeof value !== "string" || !/^[0-9a-f]{64}$/.test(value)) fail("MTCLI_RECEIPT_SCHEMA", pointer, "expected SHA-256");
  return value;
}

export function receiptRelativePath(featureId: string, nodeId: string): string {
  if (!/^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$/.test(featureId) || !/^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$/.test(nodeId)) {
    fail("MTCLI_RECEIPT_IDENTITY", "/input", "invalid feature or node identity");
  }
  return `${RECEIPT_DIRECTORY}/${featureId}.${nodeId}.json`;
}

export function createInstantiationReceipt(plan: InstantiationPlanV1): InstantiationReceiptV1 {
  const semanticContract = plan.input.typed_closure == null
    ? {
        body: plan.input.body,
        relationships: plan.input.relationships,
        relationship_authority_sha256: RELATIONSHIP_AUTHORITY_SHA256,
      }
    : {
        body: plan.input.body,
        relationships: plan.input.relationships,
        relationship_authority_sha256: RELATIONSHIP_AUTHORITY_SHA256,
        typed_closure: plan.input.typed_closure,
      };
  const body = {
    schema_version: "domainspec.instantiation-receipt/v1" as const,
    baseline: plan.baseline,
    input: Object.freeze({
      project_id: plan.input.project_id,
      feature_id: plan.input.feature_id,
      node_id: plan.input.node_id,
      kind: plan.input.kind,
      meta_type_id: plan.input.meta_type_id,
      source_manifest_sha256: plan.input.source_manifest.manifest_sha256,
    }),
    language: plan.language,
    selected_realization: plan.selected_realization,
    generator_id: plan.generator_id,
    system_integration: plan.system_integration === null ? null : Object.freeze({
      profile_selector: plan.system_integration.profile_selector,
      binding_source: plan.system_integration.binding_source,
      manifest: plan.system_integration.manifest,
      generated_relative_path: plan.system_integration.generated_relative_path,
    }),
    semantic_contract: Object.freeze(semanticContract),
    plan_sha256: plan.plan_sha256,
    artifacts: Object.freeze(plan.artifacts.map(({ relative_path, size_bytes, sha256: digest }) => Object.freeze({ relative_path, size_bytes, sha256: digest }))),
    authority_effect: "none" as const,
  };
  return Object.freeze({ ...body, receipt_sha256: sha256(canonicalJson(body)) });
}

function decodeClosureContract(kind: string, value: unknown, pointer: string): TypedNodeContract {
  if (kind === "Entity" || kind === "Value Object") return decodeTypedRecordContract(value, pointer);
  if (kind === "Enum") return decodeTypedSumContract(value, pointer);
  if (kind === "Rule") return decodeTypedRuleContract(value, pointer);
  if (kind === "Calculation") {
    const contract = decodeTypedCalculationContract(value, pointer);
    if (contract.schema_version !== "domainspec.typed-calculation/v2") fail("MTCLI_RECEIPT_TYPED_CLOSURE", pointer, "Calculation closure requires v2");
    return contract;
  }
  if (kind === "Operation" || kind === "Query") return decodeTypedOperationContract(value, pointer);
  fail("MTCLI_RECEIPT_TYPED_CLOSURE", pointer, `unsupported typed closure node kind:${kind}`);
}

function validateTypedClosure(value: unknown, receiptInput: Record<string, unknown>, body: DecodedBody, relationships: readonly DecodedRelationship[]): TypedSemanticClosureV1 {
  const pointer = "/semantic_contract/typed_closure";
  const ruleRoot = isObject(value) && value.schema_version === "domainspec.typed-rule-closure/v1";
  const calculationRoot = isObject(value) && value.schema_version === "domainspec.typed-calculation-closure/v1";
  const rootKey = calculationRoot ? "calculation" : ruleRoot ? "rule" : "operation";
  exactKeys(value, ["schema_version", "root_selector", "nodes", "relationships", "properties", "variants", "rules", rootKey, "closure_sha256", "authority_effect"], pointer);
  if (!["domainspec.typed-operation-closure/v1", "domainspec.typed-rule-closure/v1", "domainspec.typed-calculation-closure/v1"].includes(String(value.schema_version)) || value.authority_effect !== "none") fail("MTCLI_RECEIPT_TYPED_CLOSURE", pointer, "invalid typed closure envelope");
  const expectedRoot = `${receiptInput.feature_id}:${receiptInput.node_id}`;
  if (value.root_selector !== expectedRoot) fail("MTCLI_RECEIPT_TYPED_CLOSURE", `${pointer}/root_selector`, "typed closure root does not match receipt input");
  if (!Array.isArray(value.nodes)) fail("MTCLI_RECEIPT_TYPED_CLOSURE", `${pointer}/nodes`, "typed closure nodes must be an array");
  const sourceNodes = value.nodes.map((candidate, index): TypedClosureSourceNode => {
    const nodePointer = `${pointer}/nodes/${index}`;
    exactKeys(candidate, ["selector", "kind", "typed_contract"], nodePointer);
    const nodeSelector = requireString(candidate.selector, `${nodePointer}/selector`);
    const [featureId, nodeId, extra] = nodeSelector.split(":");
    if (!featureId || !nodeId || extra !== undefined) fail("MTCLI_RECEIPT_TYPED_CLOSURE", `${nodePointer}/selector`, "invalid typed closure node selector");
    const kind = requireString(candidate.kind, `${nodePointer}/kind`);
    return Object.freeze({ feature_id: featureId, node_id: nodeId, kind, typed_contract: decodeClosureContract(kind, candidate.typed_contract, `${nodePointer}/typed_contract`) });
  });
  const rebuilt = calculationRoot ? compileTypedCalculationClosure(expectedRoot, sourceNodes, relationships) : ruleRoot ? compileTypedRuleClosure(expectedRoot, sourceNodes, relationships) : compileTypedOperationClosure(expectedRoot, sourceNodes, relationships);
  if (rebuilt === null || canonicalJson(rebuilt) !== canonicalJson(value)) fail("MTCLI_RECEIPT_TYPED_CLOSURE", pointer, "typed closure is not the deterministic closure of its bound nodes and relationships");
  if (!ruleRoot && !calculationRoot && canonicalJson(rebuilt.relationships) !== canonicalJson(relationships)) fail("MTCLI_RECEIPT_TYPED_CLOSURE", `${pointer}/relationships`, "typed closure relationships do not match the receipt relationship contract");
  const rootContract = rebuilt.schema_version === "domainspec.typed-calculation-closure/v1" ? rebuilt.calculation : rebuilt.schema_version === "domainspec.typed-rule-closure/v1" ? rebuilt.rule : rebuilt.operation;
  if (!isObject(body.typed_contract) || canonicalJson(rootContract) !== canonicalJson(body.typed_contract)) fail("MTCLI_RECEIPT_TYPED_CLOSURE", `${pointer}/${rootKey}`, "typed closure root contract does not match the selected body contract");
  return rebuilt;
}

export function validateInstantiationReceipt(value: unknown): InstantiationReceiptV1 {
  exactKeys(value, ["schema_version", "baseline", "input", "language", "selected_realization", "generator_id", "system_integration", "semantic_contract", "plan_sha256", "artifacts", "authority_effect", "receipt_sha256"], "$receipt");
  if (value.schema_version !== "domainspec.instantiation-receipt/v1") fail("MTCLI_RECEIPT_SCHEMA", "/schema_version", "unsupported receipt schema");
  exactKeys(value.baseline, ["id", "digest", "manifest_sha256"], "/baseline");
  if (value.baseline.id !== FROZEN_META_TYPE_CATALOG.baseline_id || value.baseline.digest !== FROZEN_META_TYPE_CATALOG.baseline_digest || value.baseline.manifest_sha256 !== FROZEN_META_TYPE_CATALOG.manifest_sha256) {
    fail("MTCLI_RECEIPT_BASELINE", "/baseline", "receipt is not bound to the frozen baseline");
  }
  exactKeys(value.input, ["project_id", "feature_id", "node_id", "kind", "meta_type_id", "source_manifest_sha256"], "/input");
  for (const key of ["project_id", "feature_id", "node_id", "kind", "meta_type_id"] as const) requireString(value.input[key], `/input/${key}`);
  requireSha(value.input.source_manifest_sha256, "/input/source_manifest_sha256");
  if (!(["typescript", "python", "rust"] as const).includes(value.language as SupportedLanguage)) fail("MTCLI_RECEIPT_LANGUAGE", "/language", "unsupported language");
  const selected = selectRealization(String(value.input.meta_type_id), value.language as SupportedLanguage);
  if (metaTypeIdForLabel(String(value.input.kind)) !== value.input.meta_type_id || selected.meta_type_label !== value.input.kind) fail("MTCLI_RECEIPT_META_TYPE", "/input", "kind and meta-type identity do not select the same frozen type");
  if (canonicalJson(value.selected_realization) !== canonicalJson(selected)) fail("MTCLI_RECEIPT_REALIZATION", "/selected_realization", "selected realization is not the frozen catalog row");
  const expectedGeneratorId = generatorIdFor(String(value.input.meta_type_id), value.language as SupportedLanguage);
  if (value.generator_id !== expectedGeneratorId) fail("MTCLI_RECEIPT_GENERATOR", "/generator_id", "generator identity does not match the selected row");
  let integrationPath: string | null = null;
  if (value.system_integration !== null) {
    exactKeys(value.system_integration, ["profile_selector", "binding_source", "manifest", "generated_relative_path"], "/system_integration");
    if (value.system_integration.profile_selector !== "provider-neutral-v1") fail("MTCLI_RECEIPT_INTEGRATION_PROFILE", "/system_integration/profile_selector", "unsupported system-integration profile");
    exactKeys(value.system_integration.binding_source, ["relative_path", "sha256"], "/system_integration/binding_source");
    const bindingSourcePath = requireString(value.system_integration.binding_source.relative_path, "/system_integration/binding_source/relative_path");
    requireSha(value.system_integration.binding_source.sha256, "/system_integration/binding_source/sha256");
    const manifest = validateSystemIntegrationManifest(value.system_integration.manifest, value.language as SupportedLanguage);
    if (manifest.subject_ref !== `${value.input.feature_id}:${value.input.node_id}`) fail("MTCLI_RECEIPT_INTEGRATION_SUBJECT", "/system_integration/manifest/subject_ref", "system-integration subject does not match selected node");
    if (bindingSourcePath !== `integrations/${manifest.binding_set_id}.json`) fail("MTCLI_RECEIPT_INTEGRATION_SOURCE", "/system_integration/binding_source/relative_path", "system-integration source path does not match binding-set identity");
    integrationPath = requireString(value.system_integration.generated_relative_path, "/system_integration/generated_relative_path");
    if (integrationPath !== generatedSystemIntegrationPath(manifest.binding_set_id, value.language as SupportedLanguage)) fail("MTCLI_RECEIPT_INTEGRATION_PATH", "/system_integration/generated_relative_path", "system-integration output path drifted");
  }
  if (!isObject(value.semantic_contract)) fail("MTCLI_RECEIPT_SCHEMA", "/semantic_contract", "invalid semantic contract");
  const hasTypedClosure = Object.hasOwn(value.semantic_contract, "typed_closure");
  exactKeys(value.semantic_contract, hasTypedClosure ? ["body", "relationships", "relationship_authority_sha256", "typed_closure"] : ["body", "relationships", "relationship_authority_sha256"], "/semantic_contract");
  if (!isObject(value.semantic_contract.body) || !Array.isArray(value.semantic_contract.relationships)) fail("MTCLI_RECEIPT_SCHEMA", "/semantic_contract", "invalid semantic contract");
  let priorEdge = "";
  const edgeIds = new Set<string>();
  for (const [index, relationship] of value.semantic_contract.relationships.entries()) {
    const pointer = `/semantic_contract/relationships/${index}`;
    exactKeys(relationship, ["edge_id", "relationship", "scope", "source", "target"], pointer);
    const edgeId = requireString(relationship.edge_id, `${pointer}/edge_id`);
    if (!/^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$/.test(edgeId) || edgeIds.has(edgeId) || (priorEdge && priorEdge.localeCompare(edgeId) > 0)) fail("MTCLI_RECEIPT_RELATIONSHIP", pointer, "relationship edges must be unique and sorted canonical identifiers");
    edgeIds.add(edgeId);
    priorEdge = edgeId;
    const relationshipId = requireString(relationship.relationship, `${pointer}/relationship`);
    if (relationship.scope !== "feature" && relationship.scope !== "project") fail("MTCLI_RECEIPT_RELATIONSHIP", `${pointer}/scope`, "invalid relationship scope");
    const sourceEndpoint = relationship.source;
    const targetEndpoint = relationship.target;
    exactKeys(sourceEndpoint, ["feature_id", "node_id", "kind"], `${pointer}/source`);
    exactKeys(targetEndpoint, ["feature_id", "node_id", "kind"], `${pointer}/target`);
    for (const [endpointName, endpoint] of [["source", sourceEndpoint], ["target", targetEndpoint]] as const) {
      for (const key of ["feature_id", "node_id", "kind"] as const) requireString(endpoint[key], `${pointer}/${endpointName}/${key}`);
    }
    const signature = relationshipSignature(relationshipId);
    if (!signature || !signature.source_types.includes(String(sourceEndpoint.kind)) || !signature.target_types.includes(String(targetEndpoint.kind))) fail("MTCLI_RECEIPT_RELATIONSHIP", pointer, "relationship does not match the frozen authority signature");
    const admittedScope = relationship.scope === "feature"
      ? signature.feature_scope.some((scope) => scope === "same-feature" || scope === "ui" || scope === "ui-backend")
      : signature.feature_scope.includes("cross-feature");
    if (!admittedScope) fail("MTCLI_RECEIPT_RELATIONSHIP", `${pointer}/scope`, "relationship placement does not match the frozen authority signature");
    const selectedKey = `${value.input.feature_id}:${value.input.node_id}`;
    if (`${sourceEndpoint.feature_id}:${sourceEndpoint.node_id}` !== selectedKey && `${targetEndpoint.feature_id}:${targetEndpoint.node_id}` !== selectedKey) fail("MTCLI_RECEIPT_RELATIONSHIP", pointer, "relationship is unrelated to the selected node");
  }
  const sourceBody = { ...value.semantic_contract.body };
  for (const signature of RELATIONSHIP_SIGNATURES) {
    const projection = signature.generated_source_projection;
    if (projection && signature.source_types.includes(String(value.input.kind))) delete sourceBody[projection.attribute];
  }
  const decodedBody = decodeBody(String(value.input.kind), sourceBody, "/semantic_contract/body");
  const compiledBody = withGeneratedRelationshipProjections(
    String(value.input.kind),
    String(value.input.feature_id),
    String(value.input.node_id),
    decodedBody,
    value.semantic_contract.relationships as unknown as readonly DecodedRelationship[],
  );
  if (canonicalJson(compiledBody) !== canonicalJson(value.semantic_contract.body)) {
    fail("MTCLI_RECEIPT_BODY", "/semantic_contract/body", "receipt body does not contain the exact derived relationship projections");
  }
  if (value.semantic_contract.relationship_authority_sha256 !== RELATIONSHIP_AUTHORITY_SHA256) fail("MTCLI_RECEIPT_RELATIONSHIP_AUTHORITY", "/semantic_contract/relationship_authority_sha256", "relationship authority drift");
  if (hasTypedClosure) validateTypedClosure(value.semantic_contract.typed_closure, value.input, decodedBody, value.semantic_contract.relationships as readonly DecodedRelationship[]);
  requireSha(value.plan_sha256, "/plan_sha256");
  if (!Array.isArray(value.artifacts) || value.artifacts.length === 0) fail("MTCLI_RECEIPT_SCHEMA", "/artifacts", "artifact inventory must be nonempty");
  const paths = new Set<string>();
  for (const [index, artifact] of value.artifacts.entries()) {
    exactKeys(artifact, ["relative_path", "size_bytes", "sha256"], `/artifacts/${index}`);
    const relativePath = requireString(artifact.relative_path, `/artifacts/${index}/relative_path`);
    if (path.isAbsolute(relativePath) || relativePath.includes("\\") || relativePath.split("/").some((segment) => segment === "" || segment === "." || segment === "..")) fail("MTCLI_RECEIPT_PATH", `/artifacts/${index}/relative_path`, "artifact path is not normalized and contained");
    if (paths.has(relativePath)) fail("MTCLI_RECEIPT_PATH", `/artifacts/${index}/relative_path`, "duplicate artifact path");
    paths.add(relativePath);
    if (!Number.isSafeInteger(artifact.size_bytes) || Number(artifact.size_bytes) < 1) fail("MTCLI_RECEIPT_SCHEMA", `/artifacts/${index}/size_bytes`, "invalid artifact size");
    requireSha(artifact.sha256, `/artifacts/${index}/sha256`);
  }
  const integrationArtifactCount = integrationPath === null ? 0 : value.artifacts.filter((artifact) => isObject(artifact) && artifact.relative_path === integrationPath).length;
  const typedRustArtifactCount = hasTypedClosure && value.language === "rust" ? 2 : 1;
  const expectedArtifactCount = typedRustArtifactCount + (integrationPath === null ? 0 : 1);
  const cargoManifestCount = value.artifacts.filter((artifact) => isObject(artifact) && artifact.relative_path === "Cargo.toml").length;
  if (hasTypedClosure && value.language === "rust" && cargoManifestCount !== 1) fail("MTCLI_RECEIPT_TYPED_CRATE", "/artifacts", "typed Rust receipt must contain one Cargo manifest");
  if ((!hasTypedClosure || value.language !== "rust") && cargoManifestCount !== 0) fail("MTCLI_RECEIPT_TYPED_CRATE", "/artifacts", "Cargo manifest is only supported for a typed Rust Operation");
  if (value.artifacts.length !== expectedArtifactCount || (integrationPath !== null && integrationArtifactCount !== 1)) fail("MTCLI_RECEIPT_INTEGRATION_ARTIFACT", "/artifacts", "receipt artifact count does not match its realization, typed crate, and integration selections");
  if (value.authority_effect !== "none") fail("MTCLI_RECEIPT_AUTHORITY", "/authority_effect", "authority growth is forbidden");
  requireSha(value.receipt_sha256, "/receipt_sha256");
  const { receipt_sha256: ignored, ...body } = value;
  if (sha256(canonicalJson(body)) !== value.receipt_sha256) fail("MTCLI_RECEIPT_DIGEST", "/receipt_sha256", "receipt digest is stale");
  return value as unknown as InstantiationReceiptV1;
}

export function readInstantiationReceipt(targetRoot: string, relativePath?: string): InstantiationReceiptV1 {
  const selectedPath = relativePath ?? discoverReceiptPath(targetRoot);
  let value: unknown;
  try {
    value = JSON.parse(fs.readFileSync(path.join(targetRoot, selectedPath), "utf8"));
  } catch (error) {
    fail("MTCLI_RECEIPT_READ", `/${selectedPath}`, error instanceof Error ? error.message : "cannot read receipt");
  }
  return validateInstantiationReceipt(value);
}

export function discoverReceiptPath(targetRoot: string): string {
  const directory = path.join(targetRoot, RECEIPT_DIRECTORY);
  let names: string[];
  try {
    names = fs.readdirSync(directory).filter((name) => name.endsWith(".json")).sort();
  } catch {
    fail("MTCLI_RECEIPT_MISSING", `/${RECEIPT_DIRECTORY}`, "instantiation receipt directory is missing");
  }
  if (names.length !== 1) fail("MTCLI_RECEIPT_COUNT", `/${RECEIPT_DIRECTORY}`, "target must contain exactly one instantiation receipt");
  return `${RECEIPT_DIRECTORY}/${names[0]}`;
}
