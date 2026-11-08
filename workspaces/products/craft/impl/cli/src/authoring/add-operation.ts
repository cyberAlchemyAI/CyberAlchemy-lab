import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";

import { decodeBody, loadProjectNode, validateProjectRoot } from "../input/project-model.js";
import { sha256, type SourceManifestV1 } from "../input/source-manifest.js";
import { decodeTypedRuleContract, type RuleExpression, type TypedParameter } from "../typed-operation/contracts.js";
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
  readonly source_root: string;
  readonly selector: string;
  readonly node_path: string;
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
  readonly source_root: string;
  readonly selector: string;
  readonly node_path: string;
  readonly source_manifest: SourceManifestV1;
  readonly authority_effect: "none";
}

export type ThinBackendKind = "Query" | "Calculation" | "Mapping" | "Policy";

export interface AddThinBackendInput {
  readonly sourceRoot: string;
  readonly featureId: string;
  readonly nodeId: string;
  readonly description: string;
  readonly kind: ThinBackendKind;
  readonly typedContract: unknown;
}

export interface AddThinBackendResult {
  readonly schema_version: "domainspec.add-thin-backend-result/v1";
  readonly source_root: string;
  readonly selector: string;
  readonly node_path: string;
  readonly source_manifest: SourceManifestV1;
  readonly authority_effect: "none";
}

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

function acquireLock(root: string, operation: string): AuthoringLock {
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

interface AuthorNodeInput {
  readonly sourceRoot: string;
  readonly featureId: string;
  readonly nodeId: string;
  readonly kind: "Operation" | "Rule" | ThinBackendKind;
  readonly metaTypeId: "DS-D1.4" | "DS-D1.5" | "DS-D1.6" | "DS-D1.7" | "DS-D1.8" | "DS-D1.13";
  readonly transaction: string;
  readonly body: Record<string, unknown>;
  readonly edges?: readonly Readonly<{ relationship: "reads" | "maps" | "applies"; target: string }>[];
}

interface AuthorNodeResult {
  readonly source_root: string;
  readonly selector: string;
  readonly node_path: string;
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

  const lock = acquireLock(root, input.transaction);
  let stageRoot: string | null = null;
  const edgeSpecs = (input.edges ?? []).map(({ relationship, target }) => {
    const [targetFeature, targetNode, extra] = target.split(":");
    if (!targetFeature || !targetNode || extra !== undefined || targetFeature !== input.featureId) fail("MTCLI_AUTHORING_EDGE_SCOPE", "/contract-json", `${relationship} authoring requires a same-feature target`);
    requireId(targetNode, "/contract-json");
    const edgeId = `${input.nodeId}-${relationship}-${targetNode}`;
    return Object.freeze({ relationship, targetNode, edgeId, relativePath: `specs/${input.featureId}/edges/${edgeId}.json` });
  });
  if (new Set(edgeSpecs.map(({ edgeId }) => edgeId)).size !== edgeSpecs.length) fail("MTCLI_AUTHORING_SET", "/contract-json", "duplicate authored relationship");
  for (const edge of edgeSpecs) if (fs.existsSync(path.join(root, edge.relativePath))) fail("MTCLI_AUTHORING_EDGE_EXISTS", "/contract-json", `edge already exists:${edge.edgeId}`);
  const publishedPaths: string[] = [];
  const createdDirectories: string[] = [];
  try {
    const lockedManifest = validateProjectRoot(root);
    if (lockedManifest.manifest_sha256 !== initialManifest.manifest_sha256) {
      fail("MTCLI_AUTHORING_SOURCE_DRIFT", "/source-root", "source project changed before authoring lock acquisition");
    }
    if (fs.existsSync(nodeAbsolutePath)) fail("MTCLI_AUTHORING_NODE_EXISTS", "/name", `node already exists:${input.featureId}:${input.nodeId}`);

    const feature = readFeature(root, input.featureId);
    if (feature.value.nodes.includes(input.nodeId)) fail("MTCLI_AUTHORING_NODE_EXISTS", "/name", `feature already declares:${input.nodeId}`);

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
      edges: [...feature.value.edges, ...edgeSpecs.map(({ edgeId }) => edgeId)].sort(compareIds),
    });

    stageRoot = fs.mkdtempSync(path.join(path.dirname(root), `.${path.basename(root)}.${input.transaction}-`));
    copyDeclaredSources(root, stageRoot, lockedManifest);
    fs.mkdirSync(path.dirname(path.join(stageRoot, nodeRelativePath)), { recursive: true, mode: 0o755 });
    fs.writeFileSync(path.join(stageRoot, nodeRelativePath), nodeDocument, { encoding: "utf8", flag: "wx", mode: 0o644 });
    for (const edge of edgeSpecs) {
      const stagedEdge = path.join(stageRoot, edge.relativePath);
      fs.mkdirSync(path.dirname(stagedEdge), { recursive: true, mode: 0o755 });
      fs.writeFileSync(stagedEdge, canonicalDocument({ schema_version: "domainspec.edge/v1", edge_id: edge.edgeId, feature_id: input.featureId, relationship: edge.relationship, source_node_id: input.nodeId, target_node_id: edge.targetNode, scope: "feature" }), { encoding: "utf8", flag: "wx", mode: 0o644 });
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

    fs.writeFileSync(nodeAbsolutePath, nodeDocument, { encoding: "utf8", flag: "wx", mode: 0o644 });
    publishedPaths.push(nodeAbsolutePath);
    for (const edge of edgeSpecs) {
      const absolute = path.join(root, edge.relativePath);
      const directory = path.dirname(absolute);
      if (!fs.existsSync(directory)) {
        fs.mkdirSync(directory, { recursive: true, mode: 0o755 });
        createdDirectories.push(directory);
      }
      fs.writeFileSync(absolute, canonicalDocument({ schema_version: "domainspec.edge/v1", edge_id: edge.edgeId, feature_id: input.featureId, relationship: edge.relationship, source_node_id: input.nodeId, target_node_id: edge.targetNode, scope: "feature" }), { encoding: "utf8", flag: "wx", mode: 0o644 });
      publishedPaths.push(absolute);
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
    createdDirectories.length = 0;
    return Object.freeze({
      source_root: root,
      selector: `${input.featureId}:${input.nodeId}`,
      node_path: nodeRelativePath,
      source_manifest: prospectiveManifest,
      authority_effect: "none",
    });
  } catch (error) {
    for (const publishedPath of publishedPaths.reverse()) fs.rmSync(publishedPath, { force: true });
    for (const directory of createdDirectories.reverse()) {
      try { fs.rmdirSync(directory); } catch { /* preserve non-empty or concurrently owned directories */ }
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
    }),
  });
}

function thinBackendBody(input: AddThinBackendInput): Record<string, unknown> {
  requireId(input.featureId, "/feature");
  requireId(input.nodeId, "/name");
  requireText(input.description, "/description");
  const typed = decodeTypedBackendContract(input.kind, input.typedContract);
  let body: Record<string, unknown>;
  if (typed.schema_version === "domainspec.typed-query/v1") body = { description: input.description.trim(), reads: [typed.source], typed_contract: typed };
  else if (typed.schema_version === "domainspec.typed-calculation/v1" || typed.schema_version === "domainspec.typed-calculation/v2") body = { description: input.description.trim(), inputs: typed.inputs.map(({ name }) => name), typed_contract: typed };
  else if (typed.schema_version === "domainspec.typed-mapping/v1") body = { description: input.description.trim(), source: typed.source, target: typed.target, typed_contract: typed };
  else body = { description: input.description.trim(), strategies: [...new Set([...typed.cases.map(({ target }) => target), typed.default_target])], typed_contract: typed };
  decodeBody(input.kind, body);
  return body;
}

export function addThinBackend(input: AddThinBackendInput): AddThinBackendResult {
  const body = thinBackendBody(input);
  const identities: Record<ThinBackendKind, { readonly id: AuthorNodeInput["metaTypeId"]; readonly command: string }> = {
    Query: { id: "DS-D1.5", command: "query" },
    Calculation: { id: "DS-D1.6", command: "calculation" },
    Policy: { id: "DS-D1.8", command: "policy" },
    Mapping: { id: "DS-D1.13", command: "mapping" },
  };
  const identity = identities[input.kind];
  const typed = body.typed_contract as TypedBackendContract;
  const edges = typed.schema_version === "domainspec.typed-query/v1"
    ? [{ relationship: "reads" as const, target: typed.source }]
    : typed.schema_version === "domainspec.typed-mapping/v1"
      ? [{ relationship: "maps" as const, target: typed.target }]
      : typed.schema_version === "domainspec.typed-policy/v1"
        ? [...new Set([...typed.cases.map(({ target }) => target), typed.default_target])].map((target) => ({ relationship: "applies" as const, target }))
        : [];
  return Object.freeze({
    schema_version: "domainspec.add-thin-backend-result/v1",
    ...authorNode({ sourceRoot: input.sourceRoot, featureId: input.featureId, nodeId: input.nodeId, kind: input.kind, metaTypeId: identity.id, transaction: `add-${identity.command}`, body, edges }),
  });
}
