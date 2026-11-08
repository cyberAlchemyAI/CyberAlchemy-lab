#!/usr/bin/env node

import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const TOOL_PATH = fileURLToPath(import.meta.url);
const DEFAULT_REPOSITORY_ROOT = path.resolve(path.dirname(TOOL_PATH), "../../../../..");
const FEATURE_ID = "governance-evaluation-kernel";
const PRODUCT_CAPABILITY_REF = "GOV-CAP-ASSESS-RULE-FITNESS";
const REQUIRED_NODES = Object.freeze({
  "governance-program": {
    kind: "Entity",
    metaTypeId: "DS-D1.1",
    businessConceptRef: "GovernanceProgram",
    realizationBindingRef: "LANG-REALIZATION-GOVERNANCE-PROGRAM-001",
    rustProtocolId: "rust.validated-extensible-entity-factory/v1",
    fields: [
      ["id", "ProgramId", true, true],
      ["version", "u32", true, false],
      ["effect_ceiling", "EffectCeiling", true, false],
      ["selector", "GovernanceRequest", true, false],
      ["clauses", "ProgramClause[]", true, false]
    ],
    extra: { identity_fields: ["id"], lifecycle_fields: ["version"] }
  },
  "governance-request": {
    kind: "Value Object",
    metaTypeId: "DS-D1.2",
    businessConceptRef: "GovernanceRequest",
    realizationBindingRef: "LANG-REALIZATION-GOVERNANCE-REQUEST-001",
    rustProtocolId: "rust.owned-value-object-factory/v1",
    fields: [
      ["principal", "String", true, false],
      ["subject", "String", true, false],
      ["action", "String", true, false],
      ["target", "String", true, false],
      ["consequence", "String", true, false],
      ["requested_effect", "String", true, false],
      ["integration_surface", "String", true, false],
      ["mode", "String", true, false],
      ["context", "String", true, false]
    ],
    extra: { equality: "complete-value" }
  },
  "governance-fact": {
    kind: "Value Object",
    metaTypeId: "DS-D1.2",
    businessConceptRef: "GovernanceFact",
    realizationBindingRef: "LANG-REALIZATION-GOVERNANCE-FACT-001",
    rustProtocolId: "rust.owned-value-object-factory/v1",
    fields: [
      ["scope", "GovernanceRequest", true, false],
      ["source", "String", true, false],
      ["verifier", "String", true, false],
      ["value", "FactValue", true, false]
    ],
    extra: { equality: "complete-value" }
  },
  "governance-fact-set": {
    kind: "Value Object",
    metaTypeId: "DS-D1.2",
    businessConceptRef: "GovernanceFactSet",
    realizationBindingRef: "LANG-REALIZATION-GOVERNANCE-FACT-SET-001",
    rustProtocolId: "rust.owned-value-object-factory/v1",
    fields: [["facts", "GovernanceFact[]", true, false]],
    extra: { equality: "normalized-complete-value" }
  },
  "governance-verdict": {
    kind: "Enum",
    metaTypeId: "DS-D1.3",
    businessConceptRef: "GovernanceVerdict",
    realizationBindingRef: "candidate:governance-verdict",
    rustProtocolId: "rust.nominal-enum-explicit-wire/v1",
    members: [
      ["Allow", "allow"],
      ["Deny", "deny"],
      ["Abstain", "abstain"],
      ["Error", "error"]
    ]
  },
  "evaluate-governance": {
    kind: "Calculation",
    metaTypeId: "DS-D1.6",
    businessConceptRef: "EvaluateGovernance",
    realizationBindingRef: "candidate:evaluate-governance",
    rustProtocolId: "rust.bound-calculation/v1",
    inputs: [
      ["program", "GovernanceProgram"],
      ["request", "GovernanceRequest"],
      ["fact_set", "GovernanceFactSet"]
    ],
    output: ["evaluation", "Evaluation"],
    extra: { deterministic: true, effects: [], formal_return_type: "value", pure: true }
  }
});

const TEMPLATE_OUTPUTS = Object.freeze({
  ".gitignore": "gitignore.tmpl",
  "Cargo.toml": "Cargo.toml.tmpl",
  "Cargo.lock": "Cargo.lock.tmpl",
  "src/lib.rs": "lib.rs.tmpl",
  "src/main.rs": "main.rs.tmpl",
  "README.md": "README.md.tmpl",
  "DOMAIN-MODEL.md": "DOMAIN-MODEL.md.tmpl"
});

export class GovernanceKernelContractError extends Error {
  constructor(code, pointer, message) {
    super(`${code} ${pointer}: ${message}`);
    this.name = "GovernanceKernelContractError";
    this.code = code;
    this.pointer = pointer;
  }
}

function fail(code, pointer, message) {
  throw new GovernanceKernelContractError(code, pointer, message);
}

function isObject(value) {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}

function exactKeys(value, expected, pointer) {
  if (!isObject(value)) fail("GKC_SCHEMA", pointer, "expected object");
  const actual = Object.keys(value).sort();
  const wanted = [...expected].sort();
  if (JSON.stringify(actual) !== JSON.stringify(wanted)) {
    fail("GKC_SCHEMA", pointer, `expected keys ${wanted.join(", ")}`);
  }
}

function same(actual, expected, pointer) {
  if (JSON.stringify(actual) !== JSON.stringify(expected)) {
    fail("GKC_CONTRACT", pointer, `expected ${JSON.stringify(expected)}`);
  }
}

function readRegularJson(filePath, pointer) {
  let stat;
  try {
    stat = fs.lstatSync(filePath);
  } catch {
    fail("GKC_MISSING", pointer, "file is missing");
  }
  if (stat.isSymbolicLink() || !stat.isFile()) fail("GKC_FILE", pointer, "expected a regular non-symlink file");
  try {
    return { value: JSON.parse(fs.readFileSync(filePath, "utf8")), bytes: fs.readFileSync(filePath) };
  } catch {
    fail("GKC_JSON", pointer, "invalid JSON");
  }
}

function sha256(bytes) {
  return crypto.createHash("sha256").update(bytes).digest("hex");
}

function prettyJson(value) {
  return `${JSON.stringify(value, null, 2)}\n`;
}

function validateField(field, expected, pointer) {
  exactKeys(field, ["name", "type", "required", "identity", "description"], pointer);
  same([field.name, field.type, field.required, field.identity], expected, pointer);
  if (typeof field.description !== "string" || field.description.length === 0) {
    fail("GKC_SCHEMA", `${pointer}/description`, "expected nonempty description");
  }
}

function validateNode(node, expected, nodeId, pointer) {
  exactKeys(node, ["schema_version", "node_id", "feature_id", "kind", "body"], pointer);
  same(node.schema_version, "domainspec.node/v1", `${pointer}/schema_version`);
  same(node.node_id, nodeId, `${pointer}/node_id`);
  same(node.feature_id, FEATURE_ID, `${pointer}/feature_id`);
  same(node.kind, expected.kind, `${pointer}/kind`);

  const commonKeys = ["business_concept_ref", "meta_type_id", "ontology_capability_ref", "realization_binding_ref", "rust_protocol_id"];
  let variantKeys;
  if (expected.fields) variantKeys = ["fields", ...Object.keys(expected.extra)];
  else if (expected.members) variantKeys = ["members"];
  else variantKeys = ["inputs", "output", ...Object.keys(expected.extra)];
  exactKeys(node.body, [...commonKeys, ...variantKeys], `${pointer}/body`);
  same(node.body.business_concept_ref, expected.businessConceptRef, `${pointer}/body/business_concept_ref`);
  same(node.body.meta_type_id, expected.metaTypeId, `${pointer}/body/meta_type_id`);
  same(node.body.ontology_capability_ref, PRODUCT_CAPABILITY_REF, `${pointer}/body/ontology_capability_ref`);
  same(node.body.realization_binding_ref, expected.realizationBindingRef, `${pointer}/body/realization_binding_ref`);
  same(node.body.rust_protocol_id, expected.rustProtocolId, `${pointer}/body/rust_protocol_id`);
  for (const [key, value] of Object.entries(expected.extra ?? {})) same(node.body[key], value, `${pointer}/body/${key}`);

  if (expected.fields) {
    if (!Array.isArray(node.body.fields) || node.body.fields.length !== expected.fields.length) {
      fail("GKC_SCHEMA", `${pointer}/body/fields`, `expected ${expected.fields.length} fields`);
    }
    node.body.fields.forEach((field, index) => validateField(field, expected.fields[index], `${pointer}/body/fields/${index}`));
  } else if (expected.members) {
    if (!Array.isArray(node.body.members)) fail("GKC_SCHEMA", `${pointer}/body/members`, "expected member array");
    const actual = node.body.members.map((member, index) => {
      exactKeys(member, ["name", "wire", "description"], `${pointer}/body/members/${index}`);
      if (typeof member.description !== "string" || member.description.length === 0) {
        fail("GKC_SCHEMA", `${pointer}/body/members/${index}/description`, "expected nonempty description");
      }
      return [member.name, member.wire];
    });
    same(actual, expected.members, `${pointer}/body/members`);
  } else {
    const actualInputs = node.body.inputs.map((input, index) => {
      exactKeys(input, ["name", "type"], `${pointer}/body/inputs/${index}`);
      return [input.name, input.type];
    });
    exactKeys(node.body.output, ["name", "type"], `${pointer}/body/output`);
    same(actualInputs, expected.inputs, `${pointer}/body/inputs`);
    same([node.body.output.name, node.body.output.type], expected.output, `${pointer}/body/output`);
  }
}

function validatePinnedBindings(repositoryRoot, baselineRef, nodes) {
  exactKeys(baselineRef, ["id", "manifest"], "/instantiation.json/baseline_ref");
  const manifestPath = path.join(repositoryRoot, baselineRef.manifest);
  const manifestBytes = fs.readFileSync(manifestPath);
  const manifest = JSON.parse(manifestBytes.toString("utf8"));
  same(manifest.baseline_id, baselineRef.id, "/instantiation.json/baseline_ref/id");
  const rustRows = new Map(
    manifest.realization_rows
      .filter((row) => row.language === "rust")
      .map((row) => [row.meta_type_id, row])
  );
  for (const expected of Object.values(REQUIRED_NODES)) {
    const row = rustRows.get(expected.metaTypeId);
    if (!row) fail("GKC_BASELINE", `/accepted/realization/${expected.metaTypeId}`, "missing Rust realization row");
    const bindingPath = path.join(repositoryRoot, row.binding.path);
    same(sha256(fs.readFileSync(bindingPath)), row.binding.sha256, `/accepted/realization/${expected.metaTypeId}/binding/sha256`);
    const binding = JSON.parse(fs.readFileSync(bindingPath, "utf8"));
    same(binding.protocol_id, expected.rustProtocolId, `/accepted/realization/${expected.metaTypeId}/protocol_id`);
  }

  const languagePath = path.join(repositoryRoot, "cyberAlchemy-v2/language/realization-bindings.json");
  const language = readRegularJson(languagePath, "/language/realization-bindings.json").value;
  const languageBindings = new Map(language.bindings.map((binding) => [binding.binding_id, binding]));
  for (const [nodeId, expected] of Object.entries(REQUIRED_NODES)) {
    if (expected.realizationBindingRef.startsWith("candidate:")) continue;
    const binding = languageBindings.get(expected.realizationBindingRef);
    if (!binding) fail("GKC_LANGUAGE", `/nodes/${nodeId}/realization_binding_ref`, "binding is missing");
    same(binding.concept_ref, expected.businessConceptRef, `/nodes/${nodeId}/business_concept_ref`);
    same(binding.selected_domainspec_type_ref, expected.metaTypeId, `/nodes/${nodeId}/meta_type_id`);
    same(binding.status, "selected", `/nodes/${nodeId}/realization_binding_status`);
  }

  const productNodesPath = path.join(repositoryRoot, "cyberAlchemy-v2/ontology/governance/product/nodes.json");
  const productNodes = readRegularJson(productNodesPath, "/governance/product/nodes.json").value;
  if (!productNodes.nodes.some((node) => node.id === PRODUCT_CAPABILITY_REF)) {
    fail("GKC_ONTOLOGY", "/ontology_capability_ref", `missing ${PRODUCT_CAPABILITY_REF}`);
  }
  for (const node of nodes) same(node.body.ontology_capability_ref, PRODUCT_CAPABILITY_REF, `/nodes/${node.node_id}/ontology_capability_ref`);
  return {
    baselineId: manifest.baseline_id,
    baselineDigest: manifest.baseline_digest,
    manifestPath: baselineRef.manifest,
    manifestSha256: sha256(manifestBytes)
  };
}

export function loadGovernanceKernelProject({ repositoryRoot = DEFAULT_REPOSITORY_ROOT, projectRoot }) {
  const root = path.resolve(projectRoot);
  const sources = [];
  const readSource = (relativePath) => {
    const absolute = path.resolve(root, relativePath);
    const relative = path.relative(root, absolute);
    if (relative.startsWith("..") || path.isAbsolute(relative)) fail("GKC_PATH", `/${relativePath}`, "path escapes project root");
    const read = readRegularJson(absolute, `/${relativePath}`);
    sources.push({ relativePath, bytes: read.bytes });
    return read.value;
  };

  const project = readSource("project.json");
  exactKeys(project, ["schema_version", "project_id", "features", "cross_feature_edges"], "/project.json");
  same(project.schema_version, "domainspec.project/v1", "/project.json/schema_version");
  same(project.project_id, "smallest-governance-program", "/project.json/project_id");
  same(project.features, [FEATURE_ID], "/project.json/features");
  same(project.cross_feature_edges, [], "/project.json/cross_feature_edges");

  const instantiation = readSource("instantiation.json");
  exactKeys(
    instantiation,
    ["schema_version", "profile_id", "baseline_ref", "product_capability_ref", "evaluation_hashing", "lifecycle_clock", "authority_effect", "enforcement_effect"],
    "/instantiation.json"
  );
  same(instantiation.schema_version, "domainspec.governance-kernel-instantiation/v1", "/instantiation.json/schema_version");
  same(instantiation.profile_id, "domainspec.rust-governance-evaluation-kernel/v1", "/instantiation.json/profile_id");
  same(instantiation.product_capability_ref, PRODUCT_CAPABILITY_REF, "/instantiation.json/product_capability_ref");
  same(instantiation.evaluation_hashing, "none", "/instantiation.json/evaluation_hashing");
  same(instantiation.lifecycle_clock, "explicit-program-version-only", "/instantiation.json/lifecycle_clock");
  same(instantiation.authority_effect, "none", "/instantiation.json/authority_effect");
  same(instantiation.enforcement_effect, "none", "/instantiation.json/enforcement_effect");

  const featurePath = `specs/${FEATURE_ID}/feature.json`;
  const feature = readSource(featurePath);
  exactKeys(feature, ["schema_version", "feature_id", "nodes", "edges"], `/${featurePath}`);
  same(feature.schema_version, "domainspec.feature/v1", `/${featurePath}/schema_version`);
  same(feature.feature_id, FEATURE_ID, `/${featurePath}/feature_id`);
  same(feature.nodes, Object.keys(REQUIRED_NODES), `/${featurePath}/nodes`);
  same(feature.edges, [], `/${featurePath}/edges`);

  const nodes = [];
  for (const [nodeId, expected] of Object.entries(REQUIRED_NODES)) {
    const nodePath = `specs/${FEATURE_ID}/nodes/${nodeId}.json`;
    const node = readSource(nodePath);
    validateNode(node, expected, nodeId, `/${nodePath}`);
    nodes.push(node);
  }

  const accepted = validatePinnedBindings(path.resolve(repositoryRoot), instantiation.baseline_ref, nodes);
  const sourceRows = sources
    .sort((left, right) => left.relativePath.localeCompare(right.relativePath))
    .map(({ relativePath, bytes }) => ({ relative_path: relativePath, size_bytes: bytes.length, sha256: sha256(bytes) }));
  const sourceAggregate = sha256(sourceRows.map((row) => `${row.relative_path}\t${row.size_bytes}\t${row.sha256}\n`).join(""));
  return { project, instantiation, feature, nodes, sourceRows, sourceAggregate, accepted };
}

function renderTemplates(repositoryRoot, model) {
  const templateRoot = path.join(repositoryRoot, "projects/domainspec-v2/impl/cli/templates/governance-kernel");
  const replacements = new Map([
    ["{{BASELINE_ID}}", model.accepted.baselineId],
    ["{{BASELINE_DIGEST}}", model.accepted.baselineDigest],
    ["{{SOURCE_AGGREGATE_SHA256}}", model.sourceAggregate]
  ]);
  const outputs = new Map();
  for (const [relativePath, templateName] of Object.entries(TEMPLATE_OUTPUTS)) {
    let bytes = fs.readFileSync(path.join(templateRoot, templateName), "utf8");
    for (const [needle, value] of replacements) bytes = bytes.replaceAll(needle, value);
    outputs.set(relativePath, Buffer.from(bytes));
  }
  return outputs;
}

function buildReceipt(model, outputs) {
  const artifacts = [...outputs]
    .map(([relativePath, bytes]) => ({ relative_path: relativePath, size_bytes: bytes.length, sha256: sha256(bytes) }))
    .sort((left, right) => left.relative_path.localeCompare(right.relative_path));
  return {
    schema_version: "domainspec.governance-kernel-instantiation-receipt/v1",
    project_id: model.project.project_id,
    feature_id: model.feature.feature_id,
    instantiation_profile: model.instantiation.profile_id,
    baseline: {
      id: model.accepted.baselineId,
      manifest: model.accepted.manifestPath,
      baseline_digest: model.accepted.baselineDigest,
      manifest_sha256: model.accepted.manifestSha256
    },
    meta_type_bindings: Object.entries(REQUIRED_NODES).map(([nodeId, expected]) => ({
      node_id: nodeId,
      meta_type_id: expected.metaTypeId,
      rust_protocol_id: expected.rustProtocolId,
      realization_binding_ref: expected.realizationBindingRef
    })),
    source: { aggregate_sha256: model.sourceAggregate, files: model.sourceRows },
    artifacts,
    evaluation_hashing: model.instantiation.evaluation_hashing,
    type_hash_protocol: "rust-hash-trait-for-equality-not-invoked-by-evaluator",
    lifecycle_clock: model.instantiation.lifecycle_clock,
    authority_effect: "none",
    enforcement_effect: "none",
    claim_ceiling: "candidate-static-instantiation-and-local-behavior-evidence"
  };
}

export function renderGovernanceKernel(options) {
  const repositoryRoot = path.resolve(options.repositoryRoot ?? DEFAULT_REPOSITORY_ROOT);
  const model = loadGovernanceKernelProject({ repositoryRoot, projectRoot: options.projectRoot });
  const outputs = renderTemplates(repositoryRoot, model);
  outputs.set("DOMAINSPEC-INSTANTIATION-RECEIPT.json", Buffer.from(prettyJson(buildReceipt(model, outputs))));
  return { model, outputs };
}

export function materializeGovernanceKernel(options) {
  const rendered = renderGovernanceKernel(options);
  const outputRoot = path.resolve(options.outputRoot);
  for (const [relativePath, bytes] of rendered.outputs) {
    const target = path.join(outputRoot, relativePath);
    fs.mkdirSync(path.dirname(target), { recursive: true });
    fs.writeFileSync(target, bytes);
  }
  return rendered;
}

export function checkGovernanceKernel(options) {
  const rendered = renderGovernanceKernel(options);
  const outputRoot = path.resolve(options.outputRoot);
  const differences = [];
  for (const [relativePath, expected] of rendered.outputs) {
    const target = path.join(outputRoot, relativePath);
    if (!fs.existsSync(target)) {
      differences.push({ relative_path: relativePath, status: "missing" });
      continue;
    }
    const actual = fs.readFileSync(target);
    if (!actual.equals(expected)) differences.push({ relative_path: relativePath, status: "drift" });
  }
  if (differences.length > 0) fail("GKC_TARGET_DRIFT", "/output", JSON.stringify(differences));
  return rendered;
}

function usage() {
  return "usage: governance-kernel.mjs <generate|check> <absolute-project-root> <absolute-output-root>";
}

if (process.argv[1] && path.resolve(process.argv[1]) === TOOL_PATH) {
  const [mode, projectRoot, outputRoot] = process.argv.slice(2);
  if (!["generate", "check"].includes(mode) || !path.isAbsolute(projectRoot ?? "") || !path.isAbsolute(outputRoot ?? "")) {
    console.error(usage());
    process.exitCode = 2;
  } else {
    try {
      const result = mode === "generate"
        ? materializeGovernanceKernel({ projectRoot, outputRoot })
        : checkGovernanceKernel({ projectRoot, outputRoot });
      console.log(JSON.stringify({
        status: "PASS",
        mode,
        project_id: result.model.project.project_id,
        source_aggregate_sha256: result.model.sourceAggregate,
        authority_effect: "none",
        enforcement_effect: "none"
      }));
    } catch (error) {
      console.error(error instanceof Error ? error.message : String(error));
      process.exitCode = 1;
    }
  }
}
