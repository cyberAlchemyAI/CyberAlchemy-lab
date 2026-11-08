import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";

import { decodeBody, loadCompiledProjectGraph, loadProjectNode, validateProjectRoot } from "../input/project-model.js";
import { sha256, type SourceManifestV1 } from "../input/source-manifest.js";
import {
  decodeTypedOperationContract,
  decodeTypedRuleContract,
  type RuleExpression,
  type TypedOperationContract,
  type TypedParameter,
} from "../typed-operation/contracts.js";
import type { CalculationSemantics, MappingField, PolicyDecision } from "../static-semantics/contracts.js";
import { decodeTypedBackendContract, type TypedBackendContract } from "../typed-backend/contracts.js";

const ID_PATTERN = /^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$/;

export interface AddOperationInput {
  readonly sourceRoot: string;
  readonly featureId: string;
  readonly nodeId: string;
  readonly description: string;
  readonly reads: readonly string[];
  readonly writes: readonly string[];
  readonly effects: readonly string[];
  readonly guard: string;
  readonly failureContinuation: string;
}

export interface AddOperationResult {
  readonly schema_version: "domainspec.add-operation-result/v1";
  readonly publication_protocol: "domainspec.atomic-authored-node/v1";
  readonly source_root: string;
  readonly selector: string;
  readonly node_path: string;
  readonly relationship_paths: readonly string[];
  readonly source_manifest: SourceManifestV1;
  readonly authority_effect: "none";
}

export interface AddRuleInput {
  readonly sourceRoot: string;
  readonly featureId: string;
  readonly nodeId: string;
  readonly description: string;
  readonly ontologyRule: string;
  readonly parameters: readonly TypedParameter[];
  readonly expression: RuleExpression;
}

export interface AddRuleResult {
  readonly schema_version: "domainspec.add-rule-result/v1";
  readonly publication_protocol: "domainspec.atomic-authored-node/v1";
  readonly source_root: string;
  readonly selector: string;
  readonly node_path: string;
  readonly relationship_paths: readonly string[];
  readonly source_manifest: SourceManifestV1;
  readonly authority_effect: "none";
}

export interface AddQueryInput {
  readonly sourceRoot: string;
  readonly featureId: string;
  readonly nodeId: string;
  readonly description: string;
  readonly reads: readonly string[];
  readonly typedContract: TypedOperationContract;
}

export interface AddQueryResult {
  readonly schema_version: "domainspec.add-query-result/v1";
  readonly publication_protocol: "domainspec.atomic-authored-node/v1";
  readonly source_root: string;
  readonly selector: string;
  readonly node_path: string;
  readonly relationship_paths: readonly string[];
  readonly source_manifest: SourceManifestV1;
  readonly authority_effect: "none";
}

interface AddStaticResultBase {
  readonly publication_protocol: "domainspec.atomic-authored-node/v1";
  readonly source_root: string;
  readonly selector: string;
  readonly node_path: string;
  readonly relationship_paths: readonly string[];
  readonly source_manifest: SourceManifestV1;
  readonly authority_effect: "none";
}

export interface AddCalculationInput { readonly sourceRoot: string; readonly featureId: string; readonly nodeId: string; readonly description: string; readonly inputs: readonly string[]; readonly semantics: CalculationSemantics; readonly calculates: readonly string[]; }
export interface AddCalculationResult extends AddStaticResultBase { readonly schema_version: "domainspec.add-calculation-result/v1"; }
export interface AddPolicyInput { readonly sourceRoot: string; readonly featureId: string; readonly nodeId: string; readonly description: string; readonly strategies: readonly string[]; readonly decisions: readonly PolicyDecision[]; readonly defaultStrategy: string; readonly applies: readonly string[]; }
export interface AddPolicyResult extends AddStaticResultBase { readonly schema_version: "domainspec.add-policy-result/v1"; }
export interface AddMappingInput { readonly sourceRoot: string; readonly featureId: string; readonly nodeId: string; readonly description: string; readonly sourceNodeId: string; readonly targetNodeId: string; readonly direction: "inbound" | "outbound" | "bidirectional"; readonly totality: "total" | "partial"; readonly fields: readonly MappingField[]; }
export interface AddMappingResult extends AddStaticResultBase { readonly schema_version: "domainspec.add-mapping-result/v1"; }

export type ThinBackendKind = "Query" | "Calculation" | "Mapping" | "Policy";
export interface AddThinBackendInput {
  readonly sourceRoot: string;
  readonly featureId: string;
  readonly nodeId: string;
  readonly description: string;
  readonly kind: ThinBackendKind;
  readonly typedContract: unknown;
  readonly calculates: readonly string[];
}
export interface AddThinBackendResult extends AddStaticResultBase { readonly schema_version: "domainspec.add-thin-backend-result/v1"; }

export class SourceAuthoringError extends Error {
  readonly exitCode = 22;

  constructor(readonly code: string, readonly pointer: string, message: string) {
    super(message);
    this.name = "SourceAuthoringError";
  }
}

function fail(code: string, pointer: string, message: string): never {
  throw new SourceAuthoringError(code, pointer, message);
}

function requireId(value: string, pointer: string): void {
  if (!ID_PATTERN.test(value)) fail("MTCLI_AUTHORING_ID", pointer, "expected a lowercase kebab-case identifier");
}

function requireText(value: string, pointer: string): void {
  if (value.trim().length === 0) fail("MTCLI_AUTHORING_TEXT", pointer, "expected nonempty text");
}

function requireSet(values: readonly string[], pointer: string): void {
  if (values.some((value) => value.trim().length === 0)) fail("MTCLI_AUTHORING_SET", pointer, "set entries must be nonempty");
  if (new Set(values).size !== values.length) fail("MTCLI_AUTHORING_SET", pointer, "set entries must be unique");
}

function canonicalDocument(value: unknown): string {
  return `${JSON.stringify(value, null, 2)}\n`;
}

function compareIds(left: string, right: string): number {
  return left < right ? -1 : left > right ? 1 : 0;
}

interface AuthoringLock {
  readonly path: string;
  readonly descriptor: number;
  readonly device: number;
  readonly inode: number;
}

function acquireLock(root: string, operation: "add-operation" | "add-query" | "add-rule" | "add-calculation" | "add-policy" | "add-mapping"): AuthoringLock {
  const lockPath = path.join(path.dirname(root), `.${path.basename(root)}.domainspec-authoring.lock`);
  let descriptor: number;
  try {
    descriptor = fs.openSync(lockPath, "wx", 0o600);
  } catch (error) {
    if ((error as NodeJS.ErrnoException).code === "EEXIST") {
      fail("MTCLI_AUTHORING_LOCKED", "/source-root", `another authoring transaction owns ${lockPath}`);
    }
    throw error;
  }
  try {
    fs.writeFileSync(descriptor, canonicalDocument({
      schema_version: "domainspec.authoring-lock/v1",
      operation,
      pid: process.pid,
    }));
    const stats = fs.fstatSync(descriptor);
    return { path: lockPath, descriptor, device: stats.dev, inode: stats.ino };
  } catch (error) {
    fs.closeSync(descriptor);
    fs.rmSync(lockPath, { force: true });
    throw error;
  }
}

function releaseLock(lock: AuthoringLock): void {
  try {
    const stats = fs.lstatSync(lock.path, { throwIfNoEntry: false });
    if (stats && stats.dev === lock.device && stats.ino === lock.inode) fs.rmSync(lock.path);
  } finally {
    fs.closeSync(lock.descriptor);
  }
}

function copyDeclaredSources(root: string, stageRoot: string, manifest: SourceManifestV1): void {
  for (const source of manifest.sources) {
    const sourcePath = path.join(root, source.relative_path);
    const targetPath = path.join(stageRoot, source.relative_path);
    fs.mkdirSync(path.dirname(targetPath), { recursive: true, mode: 0o755 });
    fs.copyFileSync(sourcePath, targetPath, fs.constants.COPYFILE_EXCL);
  }
}

function readFeature(root: string, featureId: string): {
  readonly relativePath: string;
  readonly absolutePath: string;
  readonly bytes: Buffer;
  readonly value: {
    readonly schema_version: "domainspec.feature/v1";
    readonly feature_id: string;
    readonly nodes: readonly string[];
    readonly edges: readonly string[];
  };
} {
  const relativePath = `specs/${featureId}/feature.json`;
  const absolutePath = path.join(root, relativePath);
  const bytes = fs.readFileSync(absolutePath);
  const value = JSON.parse(bytes.toString("utf8")) as {
    readonly schema_version: "domainspec.feature/v1";
    readonly feature_id: string;
    readonly nodes: readonly string[];
    readonly edges: readonly string[];
  };
  return { relativePath, absolutePath, bytes, value };
}

function validateOperationInput(input: AddOperationInput): void {
  requireId(input.featureId, "/feature");
  requireId(input.nodeId, "/name");
  requireText(input.description, "/description");
  requireText(input.guard, "/guard");
  requireText(input.failureContinuation, "/failure-continuation");
  requireSet(input.reads, "/reads");
  requireSet(input.writes, "/writes");
  requireSet(input.effects, "/effects");
  decodeBody("Operation", {
    description: input.description,
    reads: input.reads,
    writes: input.writes,
    effects: input.effects,
    guard: input.guard,
    failure_continuation: input.failureContinuation,
  });
}

function validateRuleInput(input: AddRuleInput): Record<string, unknown> {
  requireId(input.featureId, "/feature");
  requireId(input.nodeId, "/name");
  requireText(input.description, "/description");
  const typedContract = decodeTypedRuleContract({
    schema_version: "domainspec.typed-rule/v1",
    ontology_rule: input.ontologyRule,
    parameters: input.parameters,
    expression: input.expression,
  });
  return {
    description: input.description.trim(),
    predicate: "structured:domainspec.typed-rule/v1",
    typed_contract: typedContract,
  };
}

function validateQueryInput(input: AddQueryInput): Record<string, unknown> {
  requireId(input.featureId, "/feature");
  requireId(input.nodeId, "/name");
  requireText(input.description, "/description");
  requireSet(input.reads, "/reads");
  if (input.reads.length === 0) fail("MTCLI_QUERY_READS", "/reads", "Query must read at least one Entity");
  input.reads.forEach((read, index) => requireId(read, `/reads/${index}`));
  const typedContract = decodeTypedOperationContract(input.typedContract);
  if (typedContract.writes.length !== 0 || typedContract.effects.length !== 0) {
    fail("MTCLI_QUERY_READ_ONLY", "/typed-contract", "Query writes and effects must be empty");
  }
  const expectedReads = input.reads.map((read) => `${input.featureId}:${read}`).sort(compareIds);
  if (JSON.stringify([...typedContract.reads].sort(compareIds)) !== JSON.stringify(expectedReads)) {
    fail("MTCLI_QUERY_READS", "/typed-contract/reads", "typed Query reads must exactly match authored reads targets");
  }
  const graph = loadCompiledProjectGraph(input.sourceRoot);
  for (const read of input.reads) {
    const selector = `${input.featureId}:${read}`;
    const target = graph.nodes.find((node) => node.selector === selector);
    if (!target || target.kind !== "Entity") {
      fail("MTCLI_RELATIONSHIP_ENDPOINT", "/reads", `reads requires an Entity target:${target?.kind ?? "missing"}`);
    }
  }
  return {
    description: input.description.trim(),
    reads: [...input.reads].sort(compareIds),
    typed_contract: typedContract,
  };
}

interface AuthorRelationshipInput {
  readonly edgeId: string;
  readonly relationship: "reads" | "calculates" | "applies" | "maps";
  readonly targetNodeId: string;
}

interface AuthorNodeInput {
  readonly sourceRoot: string;
  readonly featureId: string;
  readonly nodeId: string;
  readonly kind: "Operation" | "Query" | "Calculation" | "Rule" | "Policy" | "Mapping";
  readonly metaTypeId: "DS-D1.4" | "DS-D1.5" | "DS-D1.6" | "DS-D1.7" | "DS-D1.8" | "DS-D1.13";
  readonly transaction: "add-operation" | "add-query" | "add-calculation" | "add-rule" | "add-policy" | "add-mapping";
  readonly body: Record<string, unknown>;
  readonly relationships: readonly AuthorRelationshipInput[];
}

interface AuthorNodeResult {
  readonly publication_protocol: "domainspec.atomic-authored-node/v1";
  readonly source_root: string;
  readonly selector: string;
  readonly node_path: string;
  readonly relationship_paths: readonly string[];
  readonly source_manifest: SourceManifestV1;
  readonly authority_effect: "none";
}

function authorNode(input: AuthorNodeInput): AuthorNodeResult {
  const initialManifest = validateProjectRoot(input.sourceRoot);
  const root = fs.realpathSync(input.sourceRoot);
  const featureExists = initialManifest.sources.some((source) => source.source_type === "feature" && source.source_id === input.featureId);
  if (!featureExists) fail("MTCLI_AUTHORING_FEATURE_MISSING", "/feature", `feature is absent:${input.featureId}`);

  const nodeRelativePath = `specs/${input.featureId}/nodes/${input.nodeId}.json`;
  const nodeAbsolutePath = path.join(root, nodeRelativePath);
  if (fs.existsSync(nodeAbsolutePath)) fail("MTCLI_AUTHORING_NODE_EXISTS", "/name", `node already exists:${input.featureId}:${input.nodeId}`);
  const relationshipDocuments = input.relationships.map((relationship) => {
    requireId(relationship.edgeId, "/relationships/edge-id");
    requireId(relationship.targetNodeId, "/relationships/target-node-id");
    const relativePath = `specs/${input.featureId}/edges/${relationship.edgeId}.json`;
    return Object.freeze({
      relativePath,
      absolutePath: path.join(root, relativePath),
      document: canonicalDocument({
        schema_version: "domainspec.edge/v1",
        edge_id: relationship.edgeId,
        feature_id: input.featureId,
        relationship: relationship.relationship,
        source_node_id: input.nodeId,
        target_node_id: relationship.targetNodeId,
        scope: "feature",
      }),
    });
  });
  for (const relationship of relationshipDocuments) {
    if (fs.existsSync(relationship.absolutePath)) fail("MTCLI_AUTHORING_EDGE_EXISTS", "/relationships", `edge already exists:${relationship.relativePath}`);
  }

  const lock = acquireLock(root, input.transaction);
  let stageRoot: string | null = null;
  const publishedPaths: { readonly path: string; readonly dev: number; readonly ino: number; readonly sha256: string }[] = [];
  const rememberPublishedPath = (publishedPath: string): void => {
    const identity = fs.lstatSync(publishedPath);
    publishedPaths.push(Object.freeze({ path: publishedPath, dev: identity.dev, ino: identity.ino, sha256: sha256(fs.readFileSync(publishedPath)) }));
  };
  try {
    const lockedManifest = validateProjectRoot(root);
    if (lockedManifest.manifest_sha256 !== initialManifest.manifest_sha256) {
      fail("MTCLI_AUTHORING_SOURCE_DRIFT", "/source-root", "source project changed before authoring lock acquisition");
    }
    if (fs.existsSync(nodeAbsolutePath)) fail("MTCLI_AUTHORING_NODE_EXISTS", "/name", `node already exists:${input.featureId}:${input.nodeId}`);

    const feature = readFeature(root, input.featureId);
    if (feature.value.nodes.includes(input.nodeId)) fail("MTCLI_AUTHORING_NODE_EXISTS", "/name", `feature already declares:${input.nodeId}`);
    for (const relationship of input.relationships) {
      if (feature.value.edges.includes(relationship.edgeId)) fail("MTCLI_AUTHORING_EDGE_EXISTS", "/relationships", `feature already declares:${relationship.edgeId}`);
    }

    const nodeDocument = canonicalDocument({
      schema_version: "domainspec.node/v1",
      node_id: input.nodeId,
      feature_id: input.featureId,
      kind: input.kind,
      body: input.body,
    });
    const featureDocument = canonicalDocument({
      schema_version: "domainspec.feature/v1",
      feature_id: input.featureId,
      nodes: [...feature.value.nodes, input.nodeId].sort(compareIds),
      edges: [...feature.value.edges, ...input.relationships.map(({ edgeId }) => edgeId)].sort(compareIds),
    });

    stageRoot = fs.mkdtempSync(path.join(path.dirname(root), `.${path.basename(root)}.${input.transaction}-`));
    copyDeclaredSources(root, stageRoot, lockedManifest);
    fs.mkdirSync(path.dirname(path.join(stageRoot, nodeRelativePath)), { recursive: true, mode: 0o755 });
    fs.writeFileSync(path.join(stageRoot, nodeRelativePath), nodeDocument, { encoding: "utf8", flag: "wx", mode: 0o644 });
    for (const relationship of relationshipDocuments) {
      const stagedPath = path.join(stageRoot, relationship.relativePath);
      fs.mkdirSync(path.dirname(stagedPath), { recursive: true, mode: 0o755 });
      fs.writeFileSync(stagedPath, relationship.document, { encoding: "utf8", flag: "wx", mode: 0o644 });
    }
    fs.writeFileSync(path.join(stageRoot, feature.relativePath), featureDocument, { encoding: "utf8", flag: "w", mode: 0o644 });

    const prospectiveManifest = validateProjectRoot(stageRoot);
    const stagedNode = loadProjectNode(stageRoot, `${input.featureId}:${input.nodeId}`);
    if (stagedNode.kind !== input.kind || stagedNode.meta_type_id !== input.metaTypeId) {
      fail("MTCLI_AUTHORING_META_TYPE", "/name", `authored node did not resolve to the canonical ${input.kind} meta-type`);
    }

    const liveManifest = validateProjectRoot(root);
    if (liveManifest.manifest_sha256 !== lockedManifest.manifest_sha256 || sha256(feature.bytes) !== sha256(fs.readFileSync(feature.absolutePath))) {
      fail("MTCLI_AUTHORING_SOURCE_DRIFT", "/source-root", "source project changed during authoring transaction");
    }
    if (fs.existsSync(nodeAbsolutePath)) fail("MTCLI_AUTHORING_NODE_EXISTS", "/name", `node appeared during authoring:${input.featureId}:${input.nodeId}`);
    for (const relationship of relationshipDocuments) {
      if (fs.existsSync(relationship.absolutePath)) fail("MTCLI_AUTHORING_EDGE_EXISTS", "/relationships", `edge appeared during authoring:${relationship.relativePath}`);
    }

    fs.writeFileSync(nodeAbsolutePath, nodeDocument, { encoding: "utf8", flag: "wx", mode: 0o644 });
    rememberPublishedPath(nodeAbsolutePath);
    for (const relationship of relationshipDocuments) {
      fs.writeFileSync(relationship.absolutePath, relationship.document, { encoding: "utf8", flag: "wx", mode: 0o644 });
      rememberPublishedPath(relationship.absolutePath);
    }

    const featureTemporaryPath = path.join(
      path.dirname(feature.absolutePath),
      `.${path.basename(feature.absolutePath)}.${crypto.randomUUID()}.tmp`,
    );
    try {
      fs.writeFileSync(featureTemporaryPath, featureDocument, { encoding: "utf8", flag: "wx", mode: 0o644 });
      fs.renameSync(featureTemporaryPath, feature.absolutePath);
    } catch (error) {
      fs.rmSync(featureTemporaryPath, { force: true });
      throw error;
    }

    publishedPaths.length = 0;
    return Object.freeze({
      publication_protocol: "domainspec.atomic-authored-node/v1" as const,
      source_root: root,
      selector: `${input.featureId}:${input.nodeId}`,
      node_path: nodeRelativePath,
      relationship_paths: Object.freeze(relationshipDocuments.map(({ relativePath }) => relativePath).sort(compareIds)),
      source_manifest: prospectiveManifest,
      authority_effect: "none",
    });
  } catch (error) {
    for (const published of publishedPaths.reverse()) {
      try {
        const current = fs.lstatSync(published.path);
        if (current.dev === published.dev && current.ino === published.ino && sha256(fs.readFileSync(published.path)) === published.sha256) fs.unlinkSync(published.path);
      } catch (cleanupError) {
        if ((cleanupError as NodeJS.ErrnoException).code !== "ENOENT") throw cleanupError;
      }
    }
    throw error;
  } finally {
    if (stageRoot !== null) fs.rmSync(stageRoot, { recursive: true, force: true });
    releaseLock(lock);
  }
}

export function addOperation(input: AddOperationInput): AddOperationResult {
  validateOperationInput(input);
  return Object.freeze({
    schema_version: "domainspec.add-operation-result/v1",
    ...authorNode({
      sourceRoot: input.sourceRoot,
      featureId: input.featureId,
      nodeId: input.nodeId,
      kind: "Operation",
      metaTypeId: "DS-D1.4",
      transaction: "add-operation",
      relationships: [],
      body: {
        description: input.description.trim(),
        reads: [...input.reads],
        writes: [...input.writes],
        effects: [...input.effects],
        guard: input.guard.trim(),
        failure_continuation: input.failureContinuation.trim(),
      },
    }),
  });
}

export function addRule(input: AddRuleInput): AddRuleResult {
  const body = validateRuleInput(input);
  return Object.freeze({
    schema_version: "domainspec.add-rule-result/v1",
    ...authorNode({
      sourceRoot: input.sourceRoot,
      featureId: input.featureId,
      nodeId: input.nodeId,
      kind: "Rule",
      metaTypeId: "DS-D1.7",
      transaction: "add-rule",
      body,
      relationships: [],
    }),
  });
}

export function addQuery(input: AddQueryInput): AddQueryResult {
  const body = validateQueryInput(input);
  const relationships = input.reads.map((targetNodeId) => Object.freeze({
    edgeId: `${input.nodeId}-reads-${targetNodeId}`,
    relationship: "reads" as const,
    targetNodeId,
  }));
  return Object.freeze({
    schema_version: "domainspec.add-query-result/v1",
    ...authorNode({
      sourceRoot: input.sourceRoot,
      featureId: input.featureId,
      nodeId: input.nodeId,
      kind: "Query",
      metaTypeId: "DS-D1.5",
      transaction: "add-query",
      body,
      relationships,
    }),
  });
}

function requireTargets(sourceRoot: string, featureId: string, nodeIds: readonly string[], kinds: readonly string[], pointer: string): void {
  requireSet(nodeIds, pointer);
  const graph = loadCompiledProjectGraph(sourceRoot);
  for (const [index, nodeId] of nodeIds.entries()) {
    requireId(nodeId, `${pointer}/${index}`);
    const target = graph.nodes.find(({ selector }) => selector === `${featureId}:${nodeId}`);
    if (!target || !kinds.includes(target.kind)) fail("MTCLI_RELATIONSHIP_ENDPOINT", pointer, `expected ${kinds.join("|")} target:${nodeId}`);
  }
}

export function addCalculation(input: AddCalculationInput): AddCalculationResult {
  requireId(input.featureId, "/feature"); requireId(input.nodeId, "/name"); requireText(input.description, "/description");
  if (input.calculates.length === 0) fail("MTCLI_CALCULATION_RELATIONSHIP", "/calculates", "Calculation requires an Operation target");
  requireTargets(input.sourceRoot, input.featureId, input.calculates, ["Operation"], "/calculates");
  const body = decodeBody("Calculation", { description: input.description.trim(), inputs: input.inputs, semantics: input.semantics });
  return Object.freeze({ schema_version: "domainspec.add-calculation-result/v1", ...authorNode({ sourceRoot: input.sourceRoot, featureId: input.featureId, nodeId: input.nodeId, kind: "Calculation", metaTypeId: "DS-D1.6", transaction: "add-calculation", body, relationships: input.calculates.map((targetNodeId) => Object.freeze({ edgeId: `${input.nodeId}-calculates-${targetNodeId}`, relationship: "calculates" as const, targetNodeId })) }) });
}

export function addPolicy(input: AddPolicyInput): AddPolicyResult {
  requireId(input.featureId, "/feature"); requireId(input.nodeId, "/name"); requireText(input.description, "/description");
  if (input.applies.length === 0) fail("MTCLI_POLICY_RELATIONSHIP", "/applies", "Policy requires an Operation or Calculation target");
  requireTargets(input.sourceRoot, input.featureId, input.applies, ["Operation", "Calculation"], "/applies");
  const graph = loadCompiledProjectGraph(input.sourceRoot);
  for (const decision of input.decisions) if (!graph.nodes.some(({ selector, kind }) => selector === decision.rule_ref && kind === "Rule")) fail("MTCLI_POLICY_RULE", "/decisions", `Policy Rule is missing:${decision.rule_ref}`);
  const body = decodeBody("Policy", { description: input.description.trim(), strategies: input.strategies, decisions: input.decisions, default_strategy: input.defaultStrategy });
  return Object.freeze({ schema_version: "domainspec.add-policy-result/v1", ...authorNode({ sourceRoot: input.sourceRoot, featureId: input.featureId, nodeId: input.nodeId, kind: "Policy", metaTypeId: "DS-D1.8", transaction: "add-policy", body, relationships: input.applies.map((targetNodeId) => Object.freeze({ edgeId: `${input.nodeId}-applies-${targetNodeId}`, relationship: "applies" as const, targetNodeId })) }) });
}

export function addMapping(input: AddMappingInput): AddMappingResult {
  requireId(input.featureId, "/feature"); requireId(input.nodeId, "/name"); requireText(input.description, "/description");
  requireTargets(input.sourceRoot, input.featureId, [input.sourceNodeId, input.targetNodeId], ["Entity", "Interface"], "/mapping-endpoints");
  const body = decodeBody("Mapping", { description: input.description.trim(), source: `${input.featureId}:${input.sourceNodeId}`, target: `${input.featureId}:${input.targetNodeId}`, direction: input.direction, totality: input.totality, fields: input.fields });
  return Object.freeze({ schema_version: "domainspec.add-mapping-result/v1", ...authorNode({ sourceRoot: input.sourceRoot, featureId: input.featureId, nodeId: input.nodeId, kind: "Mapping", metaTypeId: "DS-D1.13", transaction: "add-mapping", body, relationships: [Object.freeze({ edgeId: `${input.nodeId}-maps-${input.targetNodeId}`, relationship: "maps", targetNodeId: input.targetNodeId })] }) });
}

function sameFeatureTarget(featureId: string, selector: string, pointer: string): string {
  const [targetFeature, targetNode, extra] = selector.split(":");
  if (!targetFeature || !targetNode || extra !== undefined || targetFeature !== featureId) {
    fail("MTCLI_AUTHORING_EDGE_SCOPE", pointer, "typed backend authoring requires same-feature targets");
  }
  requireId(targetNode, pointer);
  return targetNode;
}

export function addThinBackend(input: AddThinBackendInput): AddThinBackendResult {
  requireId(input.featureId, "/feature");
  requireId(input.nodeId, "/name");
  requireText(input.description, "/description");
  const typed = decodeTypedBackendContract(input.kind, input.typedContract);
  let body: Record<string, unknown>;
  let relationships: readonly AuthorRelationshipInput[];
  if (typed.schema_version === "domainspec.typed-query/v1" || typed.schema_version === "domainspec.typed-query/v2") {
    const targetNodeId = sameFeatureTarget(input.featureId, typed.source, "/contract-json/source");
    body = { description: input.description.trim(), reads: [typed.source], typed_contract: typed };
    relationships = [{ edgeId: `${input.nodeId}-reads-${targetNodeId}`, relationship: "reads", targetNodeId }];
  } else if (typed.schema_version === "domainspec.typed-calculation/v1") {
    body = { description: input.description.trim(), inputs: typed.inputs.map(({ name }) => name), typed_contract: typed };
    if (input.calculates.length === 0) fail("MTCLI_CALCULATION_RELATIONSHIP", "/calculates", "typed Calculation requires at least one explicit Operation target");
    relationships = input.calculates.map((target) => {
      const targetNodeId = sameFeatureTarget(input.featureId, target.includes(":") ? target : `${input.featureId}:${target}`, "/calculates");
      return { edgeId: `${input.nodeId}-calculates-${targetNodeId}`, relationship: "calculates" as const, targetNodeId };
    });
  } else if (typed.schema_version === "domainspec.typed-mapping/v1") {
    const targetNodeId = sameFeatureTarget(input.featureId, typed.target, "/contract-json/target");
    sameFeatureTarget(input.featureId, typed.source, "/contract-json/source");
    body = { description: input.description.trim(), source: typed.source, target: typed.target, typed_contract: typed };
    relationships = [{ edgeId: `${input.nodeId}-maps-${targetNodeId}`, relationship: "maps", targetNodeId }];
  } else {
    const targets = [...new Set([...typed.cases.map(({ target }) => target), typed.default_target])];
    body = { description: input.description.trim(), strategies: targets, typed_contract: typed };
    relationships = targets.map((target) => {
      const targetNodeId = sameFeatureTarget(input.featureId, target, "/contract-json");
      return { edgeId: `${input.nodeId}-applies-${targetNodeId}`, relationship: "applies" as const, targetNodeId };
    });
  }
  decodeBody(input.kind, body);
  const identities: Record<ThinBackendKind, { readonly id: AuthorNodeInput["metaTypeId"]; readonly transaction: AuthorNodeInput["transaction"] }> = {
    Query: { id: "DS-D1.5", transaction: "add-query" },
    Calculation: { id: "DS-D1.6", transaction: "add-calculation" },
    Policy: { id: "DS-D1.8", transaction: "add-policy" },
    Mapping: { id: "DS-D1.13", transaction: "add-mapping" },
  };
  const identity = identities[input.kind];
  return Object.freeze({
    schema_version: "domainspec.add-thin-backend-result/v1",
    ...authorNode({ sourceRoot: input.sourceRoot, featureId: input.featureId, nodeId: input.nodeId, kind: input.kind, metaTypeId: identity.id, transaction: identity.transaction, body, relationships }),
  });
}
