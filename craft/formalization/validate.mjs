#!/usr/bin/env node

import { createHash } from "node:crypto";
import {
  existsSync,
  mkdirSync,
  readFileSync,
  statSync,
  writeFileSync,
} from "node:fs";
import { dirname, isAbsolute, relative, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const packageRoot = dirname(fileURLToPath(import.meta.url));
const repositoryRoot = resolve(packageRoot, "../../..");
const manifestPath = resolve(packageRoot, "formalization-package.json");
const ontologyPath = resolve(packageRoot, "ontology/formalization.ontology.json");
const methodPath = resolve(packageRoot, "method/formalization-method.json");
const validatorPath = fileURLToPath(import.meta.url);

const checks = [];
const blockers = [];

function check(checkId, condition, detail) {
  const status = condition ? "pass" : "block";
  checks.push({ check_id: checkId, status, detail });
  if (!condition) blockers.push({ check_id: checkId, detail });
}

function parseJson(path, checkId) {
  try {
    const value = JSON.parse(readFileSync(path, "utf8"));
    check(checkId, true, `${relative(repositoryRoot, path)} parsed as JSON`);
    return value;
  } catch (error) {
    check(checkId, false, `${relative(repositoryRoot, path)}: ${error.message}`);
    return null;
  }
}

function sha256(path) {
  return createHash("sha256").update(readFileSync(path)).digest("hex");
}

function isInside(child, parent) {
  const fromParent = relative(parent, child);
  return fromParent === "" || (
    !fromParent.startsWith("..") && !isAbsolute(fromParent)
  );
}

function unique(values) {
  return new Set(values).size === values.length;
}

function sameSet(actual, expected) {
  return actual.length === expected.length &&
    expected.every((value) => actual.includes(value));
}

function nonEmptyString(value) {
  return typeof value === "string" && value.trim().length > 0;
}

function deepEqual(left, right) {
  return JSON.stringify(left) === JSON.stringify(right);
}

function materializeFixture(value, macros, resolving = new Set()) {
  if (typeof value === "string" && Object.hasOwn(macros, value)) {
    if (resolving.has(value)) throw new Error(`fixture macro cycle: ${value}`);
    return materializeFixture(
      macros[value],
      macros,
      new Set([...resolving, value]),
    );
  }
  if (Array.isArray(value)) {
    return value.map((item) => materializeFixture(item, macros, resolving));
  }
  if (value !== null && typeof value === "object") {
    return Object.fromEntries(Object.entries(value).map(([key, item]) => [
      key,
      materializeFixture(item, macros, resolving),
    ]));
  }
  return value;
}

function applyFixtureMutation(instance, mutation, macros) {
  if (mutation === null) return instance;
  let parent = instance;
  for (const token of mutation.path.slice(0, -1)) {
    if (parent === null || typeof parent !== "object" || !(token in parent)) {
      throw new Error(`fixture mutation path missing: ${mutation.path.join(".")}`);
    }
    parent = parent[token];
  }
  const finalToken = mutation.path.at(-1);
  if (mutation.operation === "delete") {
    if (Array.isArray(parent)) parent.splice(finalToken, 1);
    else delete parent[finalToken];
  } else if (mutation.operation === "set") {
    parent[finalToken] = materializeFixture(mutation.value, macros);
  } else {
    throw new Error(`unsupported fixture mutation: ${mutation.operation}`);
  }
  return instance;
}

function jsonType(value) {
  if (value === null) return "null";
  if (Array.isArray(value)) return "array";
  if (Number.isInteger(value)) return "integer";
  return typeof value;
}

function typeMatches(value, expectedType) {
  if (expectedType === "number") return typeof value === "number";
  if (expectedType === "object") {
    return value !== null && typeof value === "object" && !Array.isArray(value);
  }
  return jsonType(value) === expectedType;
}

function resolveLocalRef(ref, rootSchema) {
  if (!ref.startsWith("#/")) throw new Error(`unsupported schema reference: ${ref}`);
  return ref.slice(2).split("/").reduce((cursor, token) => {
    const decoded = token.replaceAll("~1", "/").replaceAll("~0", "~");
    if (cursor === undefined || !(decoded in cursor)) {
      throw new Error(`unresolved schema reference: ${ref}`);
    }
    return cursor[decoded];
  }, rootSchema);
}

function validateSchemaInstance(instance, schema, rootSchema, instancePath = "$") {
  const errors = [];

  if (schema.$ref) {
    return validateSchemaInstance(
      instance,
      resolveLocalRef(schema.$ref, rootSchema),
      rootSchema,
      instancePath,
    );
  }

  for (const branch of schema.allOf ?? []) {
    errors.push(...validateSchemaInstance(instance, branch, rootSchema, instancePath));
  }
  if (schema.anyOf) {
    const branchErrors = schema.anyOf.map((branch) =>
      validateSchemaInstance(instance, branch, rootSchema, instancePath)
    );
    if (!branchErrors.some((items) => items.length === 0)) {
      errors.push(`${instancePath}: does not satisfy anyOf`);
    }
  }
  if (schema.oneOf) {
    const matchingBranches = schema.oneOf.filter((branch) =>
      validateSchemaInstance(instance, branch, rootSchema, instancePath).length === 0
    ).length;
    if (matchingBranches !== 1) {
      errors.push(`${instancePath}: satisfies ${matchingBranches} oneOf branches instead of one`);
    }
  }
  if (schema.not && validateSchemaInstance(instance, schema.not, rootSchema, instancePath).length === 0) {
    errors.push(`${instancePath}: satisfies forbidden not schema`);
  }
  if (schema.if) {
    const conditionMatches = validateSchemaInstance(
      instance,
      schema.if,
      rootSchema,
      instancePath,
    ).length === 0;
    if (conditionMatches && schema.then) {
      errors.push(...validateSchemaInstance(instance, schema.then, rootSchema, instancePath));
    }
    if (!conditionMatches && schema.else) {
      errors.push(...validateSchemaInstance(instance, schema.else, rootSchema, instancePath));
    }
  }

  if (Object.hasOwn(schema, "const") && !deepEqual(instance, schema.const)) {
    errors.push(`${instancePath}: expected constant ${JSON.stringify(schema.const)}`);
  }
  if (schema.enum && !schema.enum.some((value) => deepEqual(instance, value))) {
    errors.push(`${instancePath}: value is outside enum`);
  }

  if (schema.type) {
    const allowedTypes = Array.isArray(schema.type) ? schema.type : [schema.type];
    if (!allowedTypes.some((type) => typeMatches(instance, type))) {
      errors.push(`${instancePath}: expected type ${allowedTypes.join("|")}, got ${jsonType(instance)}`);
      return errors;
    }
  }

  if (typeof instance === "string") {
    if (schema.minLength !== undefined && instance.length < schema.minLength) {
      errors.push(`${instancePath}: shorter than minLength ${schema.minLength}`);
    }
    if (schema.pattern && !(new RegExp(schema.pattern)).test(instance)) {
      errors.push(`${instancePath}: does not match ${schema.pattern}`);
    }
  }

  if (typeof instance === "number" && schema.minimum !== undefined && instance < schema.minimum) {
    errors.push(`${instancePath}: lower than minimum ${schema.minimum}`);
  }

  if (Array.isArray(instance)) {
    if (schema.minItems !== undefined && instance.length < schema.minItems) {
      errors.push(`${instancePath}: has fewer than ${schema.minItems} items`);
    }
    if (schema.uniqueItems === true) {
      const identities = instance.map((value) => JSON.stringify(value));
      if (!unique(identities)) errors.push(`${instancePath}: items are not unique`);
    }
    if (schema.items) {
      instance.forEach((value, index) => {
        errors.push(...validateSchemaInstance(
          value,
          schema.items,
          rootSchema,
          `${instancePath}[${index}]`,
        ));
      });
    }
  }

  if (instance !== null && typeof instance === "object" && !Array.isArray(instance)) {
    const properties = schema.properties ?? {};
    for (const requiredProperty of schema.required ?? []) {
      if (!Object.hasOwn(instance, requiredProperty)) {
        errors.push(`${instancePath}: missing required property ${requiredProperty}`);
      }
    }
    for (const [key, value] of Object.entries(instance)) {
      if (Object.hasOwn(properties, key)) {
        errors.push(...validateSchemaInstance(
          value,
          properties[key],
          rootSchema,
          `${instancePath}.${key}`,
        ));
      } else if (schema.additionalProperties === false) {
        errors.push(`${instancePath}: unexpected property ${key}`);
      } else if (
        schema.additionalProperties &&
        typeof schema.additionalProperties === "object"
      ) {
        errors.push(...validateSchemaInstance(
          value,
          schema.additionalProperties,
          rootSchema,
          `${instancePath}.${key}`,
        ));
      }
    }
  }

  return errors;
}

const manifest = parseJson(manifestPath, "DSF-V001");
const ontology = parseJson(ontologyPath, "DSF-V002");
const method = parseJson(methodPath, "DSF-V032");

if (!manifest || !ontology || !method) {
  process.stdout.write(`${JSON.stringify({
    schema_version: "domainspec-v2.formalization-validation/v1",
    status: "block",
    authority_effect: "none",
    checks,
    blockers,
  }, null, 2)}\n`);
  process.exitCode = 1;
} else {
  const sourceIds = manifest.source_identities.map((source) => source.source_id);
  const sourcePaths = manifest.source_identities.map((source) => source.path);
  const sourcePathSet = new Set(sourcePaths);
  const artifactIds = manifest.artifacts.map((artifact) => artifact.artifact_id);
  const artifactPaths = manifest.artifacts.map((artifact) =>
    `${manifest.package_root}/${artifact.path}`
  );
  const boundReferencePathSet = new Set([...sourcePaths, ...artifactPaths]);
  const nodeIds = ontology.nodes.map((node) => node.concept_id);
  const nodeIdSet = new Set(nodeIds);
  const relationIds = ontology.relations.map((edge) => edge.relation_id);
  const relationIdSet = new Set(relationIds);
  const viewIds = ontology.views.map((view) => view.view_id);
  const invariantIds = ontology.invariants.map((item) => item.invariant_id);
  const residueIds = ontology.residue.map((item) => item.residue_id);
  const roleIds = method.roles.map((role) => role.role_id);
  const roleIdSet = new Set(roleIds);
  const methodArtifactIds = method.artifact_catalog.map((artifact) => artifact.artifact_id);
  const methodArtifactIdSet = new Set(methodArtifactIds);
  const stageIds = method.stages.map((stage) => stage.stage_id);
  const stageIdSet = new Set(stageIds);
  const stateIds = method.session_states.map((state) => state.state_id);
  const stateIdSet = new Set(stateIds);
  const outcomeIds = method.outcome_semantics.map((outcome) => outcome.outcome_id);
  const changeRuleIds = method.change_rules.map((rule) => rule.change_rule_id);
  const layerIds = method.implementation_layers.map((layer) => layer.layer_id);
  const layerIdSet = new Set(layerIds);
  const openDecisionIds = method.open_decisions.map((decision) => decision.decision_id);

  check(
    "DSF-V003",
    manifest.package_id === "domainspec-v2.formalization" &&
      manifest.package_owner === "projects/domainspec-v2" &&
      manifest.package_root === "projects/domainspec-v2/formalization" &&
      manifest.phase === "contracts-authored",
    "manifest identifies DomainSpec as the formalization package owner",
  );
  check(
    "DSF-V004",
    manifest.ontology_type === "business-system-bridge" &&
      manifest.ontology_type_alias === "formalization-bridge" &&
      ontology.ontology_type === "business-system-bridge" &&
      ontology.ontology_type_alias === "formalization-bridge" &&
      sameSet(manifest.branches, ["business", "system", "bridge"]) &&
      sameSet(ontology.branches, ["business", "system", "bridge"]),
    "package uses the formalization-bridge alias over the reusable business-system-bridge type",
  );
  check(
    "DSF-V005",
    manifest.visibility === "private" &&
      ontology.visibility === "private" &&
      manifest.authority_effect === "none" &&
      ontology.authority_effect === "none",
    "package and ontology are private candidates with no authority effect",
  );
  check(
    "DSF-V006",
    manifest.canonical_format === "application/json" &&
      manifest.human_views_are_canonical === false,
    "JSON is canonical and human views are supporting only",
  );
  check(
    "DSF-V007",
    unique(sourceIds) && unique(sourcePaths),
    "source identities and paths are unique",
  );

  const sourceFailures = [];
  for (const source of manifest.source_identities) {
    const sourcePath = resolve(repositoryRoot, source.path);
    if (!isInside(sourcePath, repositoryRoot) || !existsSync(sourcePath)) {
      sourceFailures.push(`${source.source_id}: missing or outside repository`);
      continue;
    }
    const actualSize = statSync(sourcePath).size;
    const actualDigest = sha256(sourcePath);
    if (actualSize !== source.size || actualDigest !== source.sha256) {
      sourceFailures.push(
        `${source.source_id}: expected ${source.sha256}/${source.size}, got ${actualDigest}/${actualSize}`,
      );
    }
  }
  check(
    "DSF-V008",
    sourceFailures.length === 0,
    sourceFailures.length === 0
      ? `${manifest.source_identities.length} source identities match exact bytes`
      : sourceFailures.join("; "),
  );

  const artifactFailures = [];
  for (const artifact of manifest.artifacts) {
    const artifactPath = resolve(packageRoot, artifact.path);
    if (!isInside(artifactPath, packageRoot) || !existsSync(artifactPath)) {
      artifactFailures.push(`${artifact.artifact_id}: missing or outside package`);
    }
    if (artifact.canonical === true && !artifact.path.toLowerCase().endsWith(".json")) {
      artifactFailures.push(`${artifact.artifact_id}: canonical artifacts must be JSON`);
    }
    if (artifact.kind === "legacy-evidence" && artifact.canonical !== false) {
      artifactFailures.push(`${artifact.artifact_id}: legacy evidence cannot be canonical`);
    }
  }
  check(
    "DSF-V009",
    unique(artifactIds) && artifactFailures.length === 0,
    artifactFailures.length === 0
      ? `${manifest.artifacts.length} unique declared artifacts exist inside the package`
      : artifactFailures.join("; "),
  );

  const packageSchemaPath = resolve(packageRoot, manifest.schema_ref);
  const ontologySchemaPath = resolve(dirname(ontologyPath), ontology.schema_ref);
  const methodSchemaPath = resolve(dirname(methodPath), method.schema_ref);
  const packageSchema = parseJson(packageSchemaPath, "DSF-V010");
  const ontologySchema = parseJson(ontologySchemaPath, "DSF-V011");
  const methodSchema = parseJson(methodSchemaPath, "DSF-V033");
  const schemaMarkerValid = packageSchema?.$schema === "https://json-schema.org/draft/2020-12/schema" &&
    ontologySchema?.$schema === "https://json-schema.org/draft/2020-12/schema" &&
    methodSchema?.$schema === "https://json-schema.org/draft/2020-12/schema";
  check(
    "DSF-V012",
    schemaMarkerValid,
    "all three declared schemas use Draft 2020-12",
  );

  let packageSchemaErrors = [];
  let ontologySchemaErrors = [];
  let methodSchemaErrors = [];
  try {
    if (packageSchema) {
      packageSchemaErrors = validateSchemaInstance(manifest, packageSchema, packageSchema);
    }
    if (ontologySchema) {
      ontologySchemaErrors = validateSchemaInstance(ontology, ontologySchema, ontologySchema);
    }
    if (methodSchema) {
      methodSchemaErrors = validateSchemaInstance(method, methodSchema, methodSchema);
    }
  } catch (error) {
    packageSchemaErrors.push(error.message);
  }
  check(
    "DSF-V013",
    packageSchemaErrors.length === 0,
    packageSchemaErrors.length === 0
      ? "package manifest conforms to its JSON Schema"
      : packageSchemaErrors.join("; "),
  );
  check(
    "DSF-V014",
    ontologySchemaErrors.length === 0,
    ontologySchemaErrors.length === 0
      ? "formalization ontology conforms to its JSON Schema"
      : ontologySchemaErrors.join("; "),
  );
  check(
    "DSF-V034",
    methodSchemaErrors.length === 0,
    methodSchemaErrors.length === 0
      ? "formalization method conforms to its JSON Schema"
      : methodSchemaErrors.join("; "),
  );
  check(
    "DSF-V015",
    resolve(dirname(ontologyPath), ontology.package_ref) === manifestPath,
    "ontology resolves to the DomainSpec formalization package manifest",
  );
  check(
    "DSF-V016",
    ontology.model_origin.model_id === "cyberalchemy-v2.ontology-model" &&
      ontology.model_origin.source_refs.every((path) => sourcePathSet.has(path)),
    "CyberAlchemy-v2 model origin is explicit and exact-source-bound",
  );
  check(
    "DSF-V017",
    ontology.model_delta.adopted_contract_fields.length > 0 &&
      ontology.model_delta.domain_extensions.length > 0 &&
      ontology.model_delta.deferred_items.length > 0 &&
      ontology.model_delta.forbidden_inferences.length > 0,
    "adopted fields, DomainSpec extensions, deferrals, and forbidden inferences are explicit",
  );
  check("DSF-V018", unique(nodeIds), "concept identities are unique");
  check("DSF-V019", unique(relationIds), "relation identities are unique");
  check("DSF-V020", unique(viewIds), "view identities are unique");
  check("DSF-V021", unique(invariantIds), "invariant identities are unique");
  check("DSF-V022", unique(residueIds), "residue identities are unique");

  const nodeFailures = [];
  for (const node of ontology.nodes) {
    if (!node.concept_id.startsWith("formalization.")) {
      nodeFailures.push(`${node.concept_id}: concept identity is outside the generic formalization namespace`);
    }
    if (!node.source_refs.every((path) => boundReferencePathSet.has(path))) {
      nodeFailures.push(`${node.concept_id}: source_refs include an unbound concrete path`);
    }
    if (!nonEmptyString(node.definition?.formal) ||
        !nonEmptyString(node.definition?.plain_language) ||
        !nonEmptyString(node.definition?.domain_context)) {
      nodeFailures.push(`${node.concept_id}: three definition voices are incomplete`);
    }
    if (!nonEmptyString(node.challenge_contract?.challenge_response) ||
        !nonEmptyString(node.challenge_contract?.owner_route) ||
        !nonEmptyString(node.challenge_contract?.resolution_gate) ||
        !nonEmptyString(node.challenge_contract?.challenge_residue_route)) {
      nodeFailures.push(`${node.concept_id}: challenge contract is incomplete`);
    }
  }
  check(
    "DSF-V023",
    nodeFailures.length === 0,
    nodeFailures.length === 0
      ? `${ontology.nodes.length} generic nodes carry source-bound CyberAlchemy-v2 contracts and three definition voices`
      : nodeFailures.join("; "),
  );

  const relationFailures = [];
  for (const edge of ontology.relations) {
    if (!nodeIdSet.has(edge.source_concept) || !nodeIdSet.has(edge.target_concept)) {
      relationFailures.push(`${edge.relation_id}: endpoint is not a declared concept`);
    }
    if (!edge.evidence_refs.every((path) => boundReferencePathSet.has(path))) {
      relationFailures.push(`${edge.relation_id}: evidence_refs include an unbound concrete path`);
    }
    if (edge.authority_effect !== "none") {
      relationFailures.push(`${edge.relation_id}: authority effect must remain none`);
    }
    if (edge.value_effect === "value-constraining" && edge.cycle_policy !== "acyclic") {
      relationFailures.push(`${edge.relation_id}: value-constraining relations must be acyclic`);
    }
  }
  check(
    "DSF-V024",
    relationFailures.length === 0,
    relationFailures.length === 0
      ? `${ontology.relations.length} relations have closed endpoints, exact evidence, safe cycles, and no authority effect`
      : relationFailures.join("; "),
  );

  const viewFailures = [];
  const viewByBranch = new Map(ontology.views.map((view) => [view.branch, view]));
  if (!sameSet([...viewByBranch.keys()], ["business", "system", "bridge"])) {
    viewFailures.push("exactly one business, system, and bridge view is required");
  }
  for (const view of ontology.views) {
    if (!view.node_refs.every((nodeRef) => nodeIdSet.has(nodeRef))) {
      viewFailures.push(`${view.view_id}: unknown node reference`);
    }
    if (!view.relation_refs.every((edgeRef) => relationIdSet.has(edgeRef))) {
      viewFailures.push(`${view.view_id}: unknown relation reference`);
    }
    for (const edgeRef of view.relation_refs) {
      const edge = ontology.relations.find((candidate) => candidate.relation_id === edgeRef);
      if (edge && (!view.node_refs.includes(edge.source_concept) || !view.node_refs.includes(edge.target_concept))) {
        viewFailures.push(`${view.view_id}: relation ${edgeRef} endpoints are not both present in the view`);
      }
    }
  }
  for (const node of ontology.nodes) {
    if (!viewByBranch.get(node.branch_affinity)?.node_refs.includes(node.concept_id)) {
      viewFailures.push(`${node.concept_id}: missing from its ${node.branch_affinity} affinity view`);
    }
  }
  const relationViewRefs = ontology.views.flatMap((view) => view.relation_refs);
  if (!unique(relationViewRefs) || !sameSet(relationViewRefs, relationIds)) {
    viewFailures.push("every relation must occur exactly once in its declared branch view");
  }
  for (const edge of ontology.relations) {
    if (!viewByBranch.get(edge.branch_view)?.relation_refs.includes(edge.relation_id)) {
      viewFailures.push(`${edge.relation_id}: missing from declared ${edge.branch_view} view`);
    }
  }
  check(
    "DSF-V025",
    viewFailures.length === 0,
    viewFailures.length === 0
      ? "business, system, and bridge views close over their nodes and relations without becoming authority"
      : viewFailures.join("; "),
  );

  const expectedOwners = [
    "domain-projects",
    "projects/domainspec-v2/formalization",
    "Define",
    "TDE",
    "validation-governance",
    "formal-providers",
    "EVF",
  ];
  const actualOwners = manifest.ownership_boundaries.map((boundary) => boundary.owner);
  check(
    "DSF-V026",
    unique(actualOwners) && sameSet(actualOwners, expectedOwners),
    "ownership boundaries separate domain meaning, authoring, formalization, derivation, provider checks, and evidence joins",
  );
  check(
    "DSF-V027",
    ontology.invariants.every((item) =>
      nonEmptyString(item.statement) &&
      nonEmptyString(item.formal) &&
      item.status === "candidate" &&
      nonEmptyString(item.failure_result)
    ),
    `${ontology.invariants.length} candidate invariants have formal readings and explicit failure results`,
  );
  check(
    "DSF-V028",
    ontology.residue.every((item) =>
      item.status === "open" &&
      nonEmptyString(item.description) &&
      nonEmptyString(item.owner_route) &&
      item.blocks.length > 0
    ),
    `${ontology.residue.length} unresolved design choices remain explicit and owner-routed`,
  );
  check(
    "DSF-V029",
    manifest.package_boundary.deferred.includes("Auth R3 example") &&
      !ontology.nodes.some((node) => node.concept_id.startsWith("auth.")) &&
      !ontology.nodes.some((node) => node.concept_id.startsWith("auth-foundation.")),
    "Auth remains a deferred example rather than the formalization package owner or ontology namespace",
  );
  check(
    "DSF-V030",
    sourcePathSet.has("projects/domainspec-v2/formalization/DomainSpecEdgeSignature.lean") &&
      manifest.artifacts.some((artifact) =>
        artifact.path === "DomainSpecEdgeSignature.lean" &&
        artifact.kind === "legacy-evidence" &&
        artifact.canonical === false
      ) &&
      ontology.nodes.some((node) =>
        node.concept_id === "formalization.legacy-provider-snapshot" &&
        node.candidate_status === "projected"
      ),
    "the imported Lean file remains exact, noncanonical legacy provider evidence",
  );
  check(
    "DSF-V031",
    manifest.claim_ceiling.includes("proves no business claim") &&
      ontology.forbidden_collapses.length > 0,
    "claim ceiling and proof, authority, runtime, and production non-collapses are explicit",
  );

  check(
    "DSF-V035",
    resolve(dirname(methodPath), method.package_ref) === manifestPath &&
      resolve(dirname(methodPath), method.ontology_ref) === ontologyPath &&
      method.authority_effect === "none",
    "working method resolves to its package and ontology and grants no authority",
  );

  const methodArtifactFailures = [];
  for (const artifact of method.artifact_catalog) {
    const concept = ontology.nodes.find((node) => node.concept_id === artifact.ontology_concept_ref);
    const ownerRole = method.roles.find((role) => role.role_id === artifact.owner_role_ref);
    if (!concept) {
      methodArtifactFailures.push(`${artifact.artifact_id}: unknown ontology concept`);
    }
    if (!ownerRole) {
      methodArtifactFailures.push(`${artifact.artifact_id}: unknown owner role`);
    }
    if (concept && ownerRole && concept.owner_route !== ownerRole.owner_route) {
      methodArtifactFailures.push(
        `${artifact.artifact_id}: method owner ${ownerRole.owner_route} differs from ontology owner ${concept.owner_route}`,
      );
    }
    if (artifact.availability === "existing" && artifact.schema_ref !== null) {
      const schemaPath = resolve(repositoryRoot, artifact.schema_ref);
      if (!isInside(schemaPath, repositoryRoot) || !existsSync(schemaPath)) {
        methodArtifactFailures.push(`${artifact.artifact_id}: existing schema is missing`);
      }
    }
  }
  check(
    "DSF-V036",
    unique(roleIds) && unique(methodArtifactIds) && methodArtifactFailures.length === 0,
    methodArtifactFailures.length === 0
      ? `${method.roles.length} roles and ${method.artifact_catalog.length} method artifacts align with ontology ownership and references`
      : methodArtifactFailures.join("; "),
  );

  const stageFailures = [];
  const expectedStageOrders = method.stages.map((_, index) => index);
  if (!deepEqual(method.stages.map((stage) => stage.order), expectedStageOrders)) {
    stageFailures.push("stage order must be contiguous from zero");
  }
  for (const stage of method.stages) {
    if (!stage.owner_role_refs.every((roleRef) => roleIdSet.has(roleRef))) {
      stageFailures.push(`${stage.stage_id}: unknown owner role reference`);
    }
    const artifactRefs = [...stage.input_artifact_refs, ...stage.output_artifact_refs];
    if (!artifactRefs.every((artifactRef) => methodArtifactIdSet.has(artifactRef))) {
      stageFailures.push(`${stage.stage_id}: unknown artifact reference`);
    }
    if (stage.next_stage !== null && !stageIdSet.has(stage.next_stage)) {
      stageFailures.push(`${stage.stage_id}: unknown next stage`);
    }
    if (stage.authority_effect !== "none") {
      stageFailures.push(`${stage.stage_id}: authority effect must be none`);
    }
  }
  for (const [index, stage] of method.stages.entries()) {
    const expectedNext = index === method.stages.length - 1
      ? null
      : method.stages[index + 1].stage_id;
    if (stage.next_stage !== expectedNext) {
      stageFailures.push(`${stage.stage_id}: next stage is not the contiguous successor`);
    }
  }
  check(
    "DSF-V037",
    unique(stageIds) && stageFailures.length === 0,
    stageFailures.length === 0
      ? `${method.stages.length} working stages form one closed, authority-free sequence`
      : stageFailures.join("; "),
  );

  const stateFailures = [];
  for (const state of method.session_states) {
    if (!state.allowed_next.every((stateRef) => stateIdSet.has(stateRef))) {
      stateFailures.push(`${state.state_id}: unknown next state`);
    }
    if (state.terminal && state.allowed_next.length > 0) {
      stateFailures.push(`${state.state_id}: terminal state has outgoing transitions`);
    }
  }
  check(
    "DSF-V038",
    unique(stateIds) && stateFailures.length === 0,
    stateFailures.length === 0
      ? `${method.session_states.length} visible authoring states have closed transitions`
      : stateFailures.join("; "),
  );

  const requiredOutcomes = [
    "PASS_BOUNDED",
    "NON_PASS",
    "UNSUPPORTED",
    "INDETERMINATE",
    "STALE",
    "MISSING",
    "FAILED",
    "BLOCKED",
  ];
  check(
    "DSF-V039",
    unique(outcomeIds) &&
      sameSet(outcomeIds, requiredOutcomes) &&
      method.outcome_semantics.filter((outcome) => outcome.can_satisfy_obligation).map((outcome) => outcome.outcome_id).join() === "PASS_BOUNDED",
    "only PASS_BOUNDED can satisfy an obligation; all non-pass outcomes remain distinct",
  );

  const layerFailures = [];
  const expectedLayerOrders = method.implementation_layers.map((_, index) => index);
  if (!deepEqual(method.implementation_layers.map((layer) => layer.order), expectedLayerOrders)) {
    layerFailures.push("layer order must be contiguous from zero");
  }
  for (const [index, layer] of method.implementation_layers.entries()) {
    const expectedBuildsOn = index === 0 ? null : method.implementation_layers[index - 1].layer_id;
    if (layer.builds_on !== expectedBuildsOn) {
      layerFailures.push(`${layer.layer_id}: builds_on must name the previous layer`);
    }
    if (!layer.included_stage_refs.every((stageRef) => stageIdSet.has(stageRef))) {
      layerFailures.push(`${layer.layer_id}: unknown stage reference`);
    }
  }
  const l0 = method.implementation_layers.find((layer) => layer.layer_id === "L0");
  if (!l0 || !sameSet(l0.included_stage_refs, ["DSF-S0", "DSF-S1", "DSF-S3"])) {
    layerFailures.push("L0 must stop at a reviewed definition-bound FormalClaim source candidate; optional InterpretationModel work is external");
  }
  check(
    "DSF-V040",
    unique(layerIds) && layerFailures.length === 0,
    layerFailures.length === 0
      ? `${method.implementation_layers.length} progressive layers preserve a minimum meaning-to-claim L0 boundary`
      : layerFailures.join("; "),
  );

  check(
    "DSF-V041",
    unique(changeRuleIds) &&
      method.change_rules.some((rule) => rule.effect === "new-formal-claim") &&
      method.change_rules.some((rule) => rule.effect === "new-projection-version") &&
      method.change_rules.some((rule) => rule.effect === "new-provider-evidence") &&
      method.change_rules.some((rule) => rule.effect === "new-evf-join") &&
      unique(openDecisionIds) &&
      method.next_action.layer_ref === "L0" &&
      layerIdSet.has(method.next_action.layer_ref),
    "change rules separate semantic, projection, provider, and evidence identities and route next work to L0",
  );

  const providerDecision = method.open_decisions.find((decision) => decision.decision_id === "DSF-MD04");
  const evidenceJoinStage = method.stages.find((stage) => stage.stage_id === "DSF-S7");
  const requiredEvidenceJoinInputs = [
    "artifact.formal-claim-source",
    "artifact.capability-assessment",
    "artifact.neutral-obligation-set",
    "artifact.projection",
    "artifact.preservation-binding",
    "artifact.native-source-bundle",
    "artifact.formal-claim-lean-binding",
    "artifact.provider-runtime-binding",
    "artifact.theorem-request",
    "artifact.provider-evidence",
    "artifact.theorem-evidence",
  ];
  check(
    "DSF-V042",
    providerDecision?.owner_route === "EVF" &&
      evidenceJoinStage !== undefined &&
      requiredEvidenceJoinInputs.every((artifactRef) => evidenceJoinStage.input_artifact_refs.includes(artifactRef)),
    "EVF owns actual provider selection and receives the complete exact-input evidence set",
  );

  const declaredSchemaFailures = [];
  const declaredSchemas = new Map();
  for (const artifact of manifest.artifacts.filter((item) => item.kind === "schema")) {
    const schemaPath = resolve(packageRoot, artifact.path);
    try {
      const schema = JSON.parse(readFileSync(schemaPath, "utf8"));
      declaredSchemas.set(artifact.path, schema);
      if (schema.$schema !== "https://json-schema.org/draft/2020-12/schema") {
        declaredSchemaFailures.push(`${artifact.artifact_id}: not Draft 2020-12`);
      }
      if (!nonEmptyString(schema.$id) || schema.type !== "object") {
        declaredSchemaFailures.push(`${artifact.artifact_id}: missing $id or object root`);
      }
    } catch (error) {
      declaredSchemaFailures.push(`${artifact.artifact_id}: ${error.message}`);
    }
  }
  check(
    "DSF-V043",
    declaredSchemaFailures.length === 0,
    declaredSchemaFailures.length === 0
      ? `${declaredSchemas.size} declared JSON Schemas parse and use Draft 2020-12`
      : declaredSchemaFailures.join("; "),
  );

  const candidateInstanceIds = [
    "domainspec.formalization-contract-set",
    "domainspec.formal-language-profile-registry",
    "domainspec.define-formalization-wizard",
    "domainspec.formalization-definition-registry",
    "domainspec.formalization-definition-index",
    "domainspec.formalization-definition-drift-audit",
  ];
  const candidateInstanceFailures = [];
  const candidateInstances = new Map();
  for (const artifactId of candidateInstanceIds) {
    const artifact = manifest.artifacts.find((item) => item.artifact_id === artifactId);
    if (!artifact || artifact.schema_ref === null) {
      candidateInstanceFailures.push(`${artifactId}: missing artifact or schema_ref`);
      continue;
    }
    try {
      const instancePath = resolve(packageRoot, artifact.path);
      const schemaPath = resolve(packageRoot, artifact.schema_ref);
      const instance = JSON.parse(readFileSync(instancePath, "utf8"));
      const schema = JSON.parse(readFileSync(schemaPath, "utf8"));
      candidateInstances.set(artifactId, instance);
      const errors = validateSchemaInstance(instance, schema, schema);
      if (errors.length > 0) {
        candidateInstanceFailures.push(`${artifactId}: ${errors.join("; ")}`);
      }
    } catch (error) {
      candidateInstanceFailures.push(`${artifactId}: ${error.message}`);
    }
  }
  check(
    "DSF-V044",
    candidateInstanceFailures.length === 0,
    candidateInstanceFailures.length === 0
      ? "contract set, profile registry, and Define wizard conform to their schemas"
      : candidateInstanceFailures.join("; "),
  );

  const definitionRegistry = candidateInstances.get("domainspec.formalization-definition-registry");
  const definitionIndex = candidateInstances.get("domainspec.formalization-definition-index");
  const definitionDriftAudit = candidateInstances.get("domainspec.formalization-definition-drift-audit");
  const definitionExactRefFailures = [];
  for (const [label, exactRef] of [
    ["definition-index.registry_ref", definitionIndex?.registry_ref],
    ["definition-drift-audit.registry_ref", definitionDriftAudit?.registry_ref],
    ...((definitionRegistry?.authority_model_refs ?? []).map((ref, index) =>
      [`definition-registry.authority_model_refs[${index}]`, ref]
    )),
  ]) {
    if (!exactRef) {
      definitionExactRefFailures.push(`${label}: missing`);
      continue;
    }
    const target = resolve(repositoryRoot, exactRef.path);
    if (!isInside(target, repositoryRoot) || !existsSync(target) ||
        sha256(target) !== exactRef.sha256 || statSync(target).size !== exactRef.size_bytes ||
        exactRef.current !== true) {
      definitionExactRefFailures.push(`${label}: exact bytes or currentness mismatch`);
    }
  }
  check(
    "DSF-V053",
    definitionExactRefFailures.length === 0,
    definitionExactRefFailures.length === 0
      ? "definition registry, index, drift audit, and parent authorities exact-bind current bytes"
      : definitionExactRefFailures.join("; "),
  );

  const definitions = definitionRegistry?.definitions ?? [];
  const definitionIndexFailures = [];
  const exactOntologyProjectionIds = new Set([
    "DSF-D02", "DSF-D03", "DSF-D05", "DSF-D09", "DSF-D10", "DSF-D11", "DSF-D12",
  ]);
  if (definitions.length !== 26 || definitionIndex?.entries?.length !== 26) {
    definitionIndexFailures.push("registry and index must each contain 26 critical terms");
  }
  const definitionIds = definitions.map((definition) => definition.definition_id);
  const definitionTerms = definitions.map((definition) => definition.term.toLowerCase());
  const allAliases = definitions.flatMap((definition) =>
    definition.aliases.map((alias) => alias.toLowerCase())
  );
  if (!unique(definitionIds) || !unique(definitionTerms) || !unique(allAliases)) {
    definitionIndexFailures.push("definition IDs, terms, and aliases must be unique");
  }
  for (const [index, definition] of definitions.entries()) {
    const entry = definitionIndex?.entries?.[index];
    if (!entry || entry.definition_id !== definition.definition_id ||
        entry.term !== definition.term || !deepEqual(entry.aliases, definition.aliases) ||
        entry.definition_pointer !== `#/definitions/${index}`) {
      definitionIndexFailures.push(`${definition.definition_id}: index entry differs from registry`);
    }
    const concept = ontology.nodes.find((node) =>
      node.concept_id === definition.ontology_concept_ref
    );
    if (!concept || !nonEmptyString(concept.definition.formal) ||
        !nonEmptyString(concept.definition.plain_language) ||
        !nonEmptyString(concept.definition.domain_context)) {
      definitionIndexFailures.push(`${definition.definition_id}: ontology three-voice projection is missing`);
    } else if (exactOntologyProjectionIds.has(definition.definition_id) &&
        (concept.definition.formal !== definition.normative_voice ||
         concept.definition.plain_language !== definition.plain_language ||
         concept.definition.domain_context !== definition.domain_context)) {
      definitionIndexFailures.push(`${definition.definition_id}: new critical-term ontology projection differs from registry`);
    }
  }
  check(
    "DSF-V054",
    definitionIndexFailures.length === 0,
    definitionIndexFailures.length === 0
      ? "26 critical terms have unique IDs and aliases, deterministic index entries, complete ontology projections, and exact projections for the seven newly closed terms"
      : definitionIndexFailures.join("; "),
  );

  const driftFindings = definitionDriftAudit?.findings ?? [];
  const driftSummary = definitionDriftAudit?.summary;
  const repairedCount = driftFindings.filter((finding) => finding.status === "repaired").length;
  const historicalCount = driftFindings.filter((finding) => finding.status === "contained-historical").length;
  const ownerGateCount = driftFindings.filter((finding) =>
    finding.status === "candidate-repair-awaiting-owner-gate"
  ).length;
  check(
    "DSF-V055",
    driftSummary?.total === driftFindings.length &&
      driftSummary?.repaired === repairedCount &&
      driftSummary?.contained_historical === historicalCount &&
      driftSummary?.open_owner_gate === ownerGateCount &&
      driftSummary?.undefined_critical_terms === 0 &&
      driftSummary?.conflicting_live_consumers === 0 &&
      driftFindings.every((finding) =>
        finding.owner_gate_required ===
          (finding.status === "candidate-repair-awaiting-owner-gate")
      ),
    "drift audit counts close over every finding: seven repaired, one historical, one explicit owner gate, and no undefined or conflicting live critical terms",
  );

  const contractSet = candidateInstances.get("domainspec.formalization-contract-set");
  const requiredContractIds = [
    "FormalizationDefinitionRegistry/v1-candidate",
    "BusinessMeaning/v1-candidate",
    "BusinessMeaning/v2-candidate",
    "InterpretationModel/v1-candidate",
    "EvaluationContext/v1-candidate",
    "FormalClaimSourcePayload/v2",
    "FormalClaimSource/v3-candidate",
    "FormalClaimDefinitionBinding/v1-candidate",
    "FormalClaimSource/v4-candidate",
    "FormalClaimEnvelope/v1-candidate",
    "FormalLanguageProfileRegistry/v1-candidate",
    "FormalClaimCapabilityAssessment/v1-candidate",
    "NeutralObligationSet/v1-candidate",
    "FormalizationProjection/v1-candidate",
    "PreservationBinding/v1-candidate",
    "NativeSourceBundle/v1-candidate",
    "ProviderRuntimeBinding/v1-candidate",
    "ProviderEvidenceBinding/v1-candidate",
    "FormalClaimLeanBinding/v1-candidate",
    "TheoremObligationRequest/v1-candidate",
    "TheoremEvidenceBinding/v1-candidate",
    "EvfEvidenceJoin/v1-candidate",
    "AuthoringSession/v1-candidate",
    "DefineFormalizationWizard/v1-candidate",
    "FormalizationCasePackage/v1-candidate",
    "FormalizationCasePackage/v2-candidate",
  ];
  const contractIds = contractSet?.contracts?.map((contract) => contract.contract_id) ?? [];
  const v3Compatibility = contractSet?.compatibility_edges?.find((edge) =>
    edge.from_contract === "FormalClaimSource/v3-candidate" &&
    edge.to_contract === "FormalClaimSourcePayload/v2"
  );
  const v4Compatibility = contractSet?.compatibility_edges?.find((edge) =>
    edge.from_contract === "FormalClaimSource/v4-candidate" &&
    edge.to_contract === "FormalClaimSourcePayload/v2"
  );
  check(
    "DSF-V045",
    contractSet !== undefined &&
      unique(contractIds) &&
      sameSet(contractIds, requiredContractIds) &&
      sameSet(contractSet.outcome_algebra, requiredOutcomes) &&
      v3Compatibility?.status === "adapter-required" &&
      v4Compatibility?.status === "adapter-required",
    "candidate contract identifiers cover definition-bound v4, the declared execution and theorem paths, preserve typed outcomes, and keep v3/v4 behind explicit v2 adapter boundaries",
  );

  const profiles = candidateInstances.get("domainspec.formal-language-profile-registry");
  const profileIds = profiles?.profiles?.map((profile) => profile.profile_id) ?? [];
  const requiredProfiles = [
    "lean-dtt",
    "fol-core",
    "smt-sfol",
    "tla-tlc",
    "alloy-relational",
    "souffle-datalog",
  ];
  const leanProfile = profiles?.profiles?.find((profile) => profile.profile_id === "lean-dtt");
  check(
    "DSF-V046",
    unique(profileIds) &&
      sameSet(profileIds, requiredProfiles) &&
      leanProfile?.tde_behavior === "carry-exact-handles-only" &&
      leanProfile?.provider_route === "evf-theorem" &&
      profiles?.authority_effect === "none",
    "candidate profile registry covers discussed formalisms while keeping Lean on the EVF theorem route",
  );

  const wizard = candidateInstances.get("domainspec.define-formalization-wizard");
  const wizardStages = wizard?.steps?.map((step) => step.method_stage) ?? [];
  check(
    "DSF-V047",
    wizard?.coordination?.canonical_state === "authoring-session-json" &&
      wizard?.coordination?.ipc_required === false &&
      sameSet(wizard?.coordination?.views ?? [], ["cli", "chat"]) &&
      sameSet(wizardStages, ["DSF-S0", "DSF-S1", "DSF-S2", "DSF-S3"]),
    "Define wizard keeps one JSON state visible in CLI and chat without requiring IPC for L0",
  );

  const requiredIntegrationSources = [
    "domainspec.formal-claim-v2",
    "evf.current-architecture",
    "tde.multiformalism-spec-r4",
    "tde.multiformalism-source-contracts-r4",
  ];
  check(
    "DSF-V048",
    requiredIntegrationSources.every((sourceId) => sourceIds.includes(sourceId)),
    "FormalClaim v2, current EVF architecture, and current TDE candidate contracts are exact source bindings",
  );

  const schemaBackedMethodArtifacts = method.artifact_catalog.filter((artifact) =>
    artifact.artifact_id !== "artifact.formal-claim-source"
  );
  check(
    "DSF-V049",
    schemaBackedMethodArtifacts.every((artifact) =>
      artifact.availability === "existing" &&
      artifact.schema_ref !== null &&
      existsSync(resolve(repositoryRoot, artifact.schema_ref))
    ),
    "every new method artifact has a concrete package-local candidate schema",
  );

  const contractSchemaFailures = [];
  for (const contract of contractSet?.contracts ?? []) {
    const schemaPath = contract.schema_path.startsWith("projects/")
      ? resolve(repositoryRoot, contract.schema_path)
      : resolve(packageRoot, contract.schema_path);
    if (!isInside(schemaPath, repositoryRoot) || !existsSync(schemaPath)) {
      contractSchemaFailures.push(`${contract.contract_id}: missing schema ${contract.schema_path}`);
    }
  }
  check(
    "DSF-V050",
    contractSchemaFailures.length === 0,
    contractSchemaFailures.length === 0
      ? `${contractSet?.contracts?.length ?? 0} contract registry schema paths resolve to concrete files`
      : contractSchemaFailures.join("; "),
  );

  const fixturePath = resolve(packageRoot, "fixtures/contract-fixtures.json");
  const fixtureSchemaPath = resolve(packageRoot, "schemas/contract-fixture-matrix.schema.json");
  let fixtureMatrix = null;
  const fixtureMatrixFailures = [];
  try {
    fixtureMatrix = JSON.parse(readFileSync(fixturePath, "utf8"));
    const fixtureSchema = JSON.parse(readFileSync(fixtureSchemaPath, "utf8"));
    fixtureMatrixFailures.push(...validateSchemaInstance(
      fixtureMatrix,
      fixtureSchema,
      fixtureSchema,
    ));
  } catch (error) {
    fixtureMatrixFailures.push(error.message);
  }
  check(
    "DSF-V051",
    fixtureMatrixFailures.length === 0,
    fixtureMatrixFailures.length === 0
      ? "contract fixture matrix conforms to its JSON Schema"
      : fixtureMatrixFailures.join("; "),
  );

  const fixtureFailures = [];
  const testedSchemas = [];
  const fixtureClasses = [];
  const fixtureCaseIds = [];
  for (const fixtureCase of fixtureMatrix?.cases ?? []) {
    fixtureCaseIds.push(fixtureCase.case_id);
    fixtureClasses.push(fixtureCase.class);
    testedSchemas.push(fixtureCase.schema_path);
    try {
      const base = fixtureMatrix.bases[fixtureCase.base_ref];
      if (base === undefined) throw new Error(`unknown base_ref ${fixtureCase.base_ref}`);
      const instance = materializeFixture(base, fixtureMatrix.macros);
      applyFixtureMutation(instance, fixtureCase.mutation, fixtureMatrix.macros);
      const fixtureContractSchemaPath = resolve(packageRoot, fixtureCase.schema_path);
      const fixtureContractSchema = JSON.parse(readFileSync(fixtureContractSchemaPath, "utf8"));
      const errors = validateSchemaInstance(
        instance,
        fixtureContractSchema,
        fixtureContractSchema,
      );
      const actualValid = errors.length === 0;
      if (actualValid !== fixtureCase.expected_valid) {
        fixtureFailures.push(
          `${fixtureCase.case_id}: expected valid=${fixtureCase.expected_valid}, got ${actualValid}; ${errors.join("; ")}`,
        );
      } else if (
        fixtureCase.expected_error_contains !== null &&
        !errors.some((error) => error.includes(fixtureCase.expected_error_contains))
      ) {
        fixtureFailures.push(
          `${fixtureCase.case_id}: missing expected diagnostic ${fixtureCase.expected_error_contains}; ${errors.join("; ")}`,
        );
      }
    } catch (error) {
      fixtureFailures.push(`${fixtureCase.case_id}: ${error.message}`);
    }
  }
  const requiredFixtureClasses = [
    "positive",
    "exact-cause-negative",
    "stale",
    "unknown",
    "duplicate",
    "malformed",
    "timeout",
    "ceiling",
  ];
  const requiredFixtureSchemas = [
    "schemas/business-meaning.schema.json",
    "schemas/business-meaning.v2-candidate.schema.json",
    "schemas/interpretation-model.schema.json",
    "schemas/evaluation-context.schema.json",
    "schemas/formal-claim-source-candidate.schema.json",
    "schemas/formal-claim-definition-binding.schema.json",
    "schemas/formal-claim-source-v4-candidate.schema.json",
    "schemas/formal-claim-envelope.schema.json",
    "schemas/authoring-session.schema.json",
    "schemas/formal-claim-capability-assessment.schema.json",
    "schemas/neutral-obligation-set.schema.json",
    "schemas/formalization-projection.schema.json",
    "schemas/preservation-binding.schema.json",
    "schemas/native-source-bundle.schema.json",
    "schemas/provider-runtime-binding.schema.json",
    "schemas/provider-evidence-binding.schema.json",
    "schemas/formal-claim-lean-binding.schema.json",
    "schemas/theorem-obligation-request.schema.json",
    "schemas/theorem-evidence-binding.schema.json",
    "schemas/evf-evidence-join.schema.json",
    "schemas/formalization-case-package.schema.json",
    "schemas/formalization-case-package.v2-candidate.schema.json",
  ];
  const requiredBoundaryCaseIds = [
    "formalclaim-current-with-stale-meaning",
    "formalclaim-v4-rejects-interpretation-model",
    "definition-binding-rejects-name-inference",
    "claim-envelope-rejects-authority-collapse",
    "claim-envelope-rejects-reference-expansion",
    "evaluation-context-positive-without-interpretation",
    "case-package-v2-claim-ready-without-interpretation",
    "case-package-v2-admitted-without-admission",
    "provider-evidence-runtime-missing",
    "evf-pass-with-stale-claim-ref",
    "case-package-positive-l1-pass",
    "case-package-pass-without-current-join",
  ];
  check(
    "DSF-V052",
    unique(fixtureCaseIds) &&
      requiredFixtureClasses.every((fixtureClass) => fixtureClasses.includes(fixtureClass)) &&
      requiredFixtureSchemas.every((schemaPath) => testedSchemas.includes(schemaPath)) &&
      requiredBoundaryCaseIds.every((caseId) => fixtureCaseIds.includes(caseId)) &&
      fixtureFailures.length === 0,
    fixtureFailures.length === 0
      ? `${fixtureCaseIds.length} semantic fixtures cover ${new Set(testedSchemas).size} schemas, all required failure classes, and the exact currentness/runtime boundaries`
      : fixtureFailures.join("; "),
  );

  const artifactInventory = manifest.artifacts
    .map((artifact) => {
      const artifactPath = resolve(packageRoot, artifact.path);
      return {
        artifact_id: artifact.artifact_id,
        path: artifact.path,
        sha256: sha256(artifactPath),
        size_bytes: statSync(artifactPath).size,
      };
    })
    .sort((left, right) => left.artifact_id.localeCompare(right.artifact_id));
  const artifactSetDigest = createHash("sha256")
    .update(JSON.stringify(artifactInventory))
    .digest("hex");

  const result = {
    schema_version: "domainspec-v2.formalization-validation/v1",
    status: blockers.length === 0 ? "pass" : "block",
    authority_effect: "none",
    package_id: manifest.package_id,
    ontology_id: ontology.ontology_id,
    bound_digests: {
      package_sha256: sha256(manifestPath),
      ontology_sha256: sha256(ontologyPath),
      method_sha256: sha256(methodPath),
      validator_sha256: sha256(validatorPath),
      contract_set_sha256: sha256(resolve(packageRoot, "contracts/formalization-contract-set.json")),
      profile_registry_sha256: sha256(resolve(packageRoot, "profiles/formal-language-profiles.json")),
      define_wizard_sha256: sha256(resolve(packageRoot, "authoring/define-wizard.json")),
      artifact_set_sha256: artifactSetDigest,
    },
    artifact_inventory: artifactInventory,
    counts: {
      sources: manifest.source_identities.length,
      artifacts: manifest.artifacts.length,
      nodes: ontology.nodes.length,
      relations: ontology.relations.length,
      views: ontology.views.length,
      invariants: ontology.invariants.length,
      residue: ontology.residue.length,
      method_roles: method.roles.length,
      method_artifacts: method.artifact_catalog.length,
      method_stages: method.stages.length,
      method_states: method.session_states.length,
      method_outcomes: method.outcome_semantics.length,
      method_layers: method.implementation_layers.length,
      method_open_decisions: method.open_decisions.length,
      checks: checks.length,
      blockers: blockers.length,
    },
    checks,
    blockers,
    claim_ceiling: manifest.claim_ceiling,
  };

  const receiptFlagIndex = process.argv.indexOf("--receipt");
  if (receiptFlagIndex !== -1) {
    const receiptArgument = process.argv[receiptFlagIndex + 1];
    if (!receiptArgument) throw new Error("--receipt requires a path");
    const receiptPath = isAbsolute(receiptArgument)
      ? resolve(receiptArgument)
      : resolve(repositoryRoot, receiptArgument);
    const receiptsRoot = resolve(packageRoot, "receipts");
    if (!isInside(receiptPath, receiptsRoot)) {
      throw new Error("receipt path must be inside projects/domainspec-v2/formalization/receipts");
    }
    if (existsSync(receiptPath)) {
      throw new Error(`refusing to overwrite receipt: ${receiptPath}`);
    }
    mkdirSync(dirname(receiptPath), { recursive: true });
    writeFileSync(
      receiptPath,
      `${JSON.stringify({ ...result, validated_at: new Date().toISOString() }, null, 2)}\n`,
      "utf8",
    );
    result.receipt = relative(repositoryRoot, receiptPath);
  }

  process.stdout.write(`${JSON.stringify(result, null, 2)}\n`);
  if (result.status !== "pass") process.exitCode = 1;
}
