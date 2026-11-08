import fs from "node:fs";
import path from "node:path";
import { TextDecoder } from "node:util";

import { createCheckedInterchange } from "../assurance/checked-interchange.js";
import { createCompiledProjectCertificate } from "../compilation/certificate.js";
import { planProjectBuild } from "../generation/project-build.js";
import { MAX_SOURCE_FILE_BYTES, readBoundedFileSync } from "../input/limits.js";
import { loadCompiledProjectGraph } from "../input/project-model.js";
import { canonicalJson, sha256 } from "../input/source-manifest.js";
import { compileSystemIntegrationManifest } from "../system-integration/compiler.js";
import type { SystemIntegrationBindingManifestV1 } from "../system-integration/types.js";
import {
  decodeDeploymentRecipeRequest,
  deploymentRecipeRequestSha256,
  plannedRecipeArtifact,
  recipeArtifactInventory,
  recipeFail,
  type DeploymentRecipeArtifactV1,
  type DeploymentRecipeComponentV1,
  type DeploymentRecipeManifestV1,
  type DeploymentRecipeMessageV1,
  type DeploymentRecipePlanV1,
  type DeploymentRecipeReceiptV1,
  type DeploymentRecipeRequestV1,
  type PlannedDeploymentRecipeArtifactV1,
} from "./contracts.js";
import {
  renderAwsEcsFargatePostgresRecipe,
  validateAwsRecipePolicy,
} from "./targets/aws-ecs-fargate-postgres-v1.js";

const MAX_RECIPE_INPUT_FILES = 4_096;
const MAX_RECIPE_INPUT_BYTES = 64 * 1024 * 1024;
const FORBIDDEN_INPUT = /(?:^|\/)(?:\.env(?:\..*)?|\.npmrc|\.yarnrc(?:\.yml)?|\.pypirc|\.netrc|\.docker\/config\.json|\.aws\/(?:credentials|config)|\.kube\/config|terraform\.tfstate(?:\..*)?|.*\.(?:pem|key|p12|pfx)|id_(?:rsa|ecdsa|ed25519))$/i;
const FORBIDDEN_DIRECTORY = /(?:^|\/)(?:\.git|node_modules|\.terraform)(?:\/|$)/i;
const UTF8 = new TextDecoder("utf-8", { fatal: true });

interface InventoriedTextFile extends DeploymentRecipeArtifactV1 { readonly content: string }

function realDirectory(root: string, pointer: string): string {
  if (!path.isAbsolute(root) || path.resolve(root) !== root) recipeFail("MTCLI_RECIPE_ROOT", pointer, "root must be normalized and absolute");
  let stats: fs.Stats;
  try { stats = fs.lstatSync(root); } catch { recipeFail("MTCLI_RECIPE_ROOT", pointer, "root does not exist"); }
  if (!stats.isDirectory() || stats.isSymbolicLink() || fs.realpathSync(root) !== root) recipeFail("MTCLI_RECIPE_ROOT", pointer, "root must be one real directory without a symbolic link");
  return root;
}

function containedDirectory(root: string, relativePath: string, pointer: string): string {
  const absolute = path.resolve(root, relativePath);
  const relative = path.relative(root, absolute);
  if (relative.startsWith("..") || path.isAbsolute(relative)) recipeFail("MTCLI_RECIPE_PATH", pointer, "path escapes consumer root");
  return realDirectory(absolute, pointer);
}

function inventoryTextTree(root: string, relativeToConsumer: string, pointer: string, filter?: (relativePath: string) => boolean): readonly InventoriedTextFile[] {
  const files: InventoriedTextFile[] = [];
  let total = 0;
  const walk = (directory: string): void => {
    const entries = fs.readdirSync(directory, { withFileTypes: true }).sort((left, right) => left.name.localeCompare(right.name));
    for (const entry of entries) {
      const absolute = path.join(directory, entry.name);
      const relative = path.relative(root, absolute).split(path.sep).join("/");
      const stats = fs.lstatSync(absolute);
      if (stats.isSymbolicLink()) recipeFail("MTCLI_RECIPE_INPUT_SYMLINK", `${pointer}/${relative}`, "recipe inputs cannot contain symbolic links");
      if (entry.isDirectory()) {
        if (FORBIDDEN_DIRECTORY.test(relative)) recipeFail("MTCLI_RECIPE_SENSITIVE_INPUT", `${pointer}/${relative}`, "repository metadata, dependency trees, and Terraform working directories are forbidden");
        walk(absolute); continue;
      }
      if (!entry.isFile() || !stats.isFile() || fs.realpathSync(absolute) !== absolute) recipeFail("MTCLI_RECIPE_INPUT_KIND", `${pointer}/${relative}`, "recipe inputs must contain only real regular files and directories");
      if (filter && !filter(relative)) recipeFail("MTCLI_RECIPE_MIGRATION_KIND", `${pointer}/${relative}`, "domain migration roots may contain only .sql files");
      const consumerRelative = `${relativeToConsumer}/${relative}`;
      if (FORBIDDEN_INPUT.test(consumerRelative)) recipeFail("MTCLI_RECIPE_SENSITIVE_INPUT", `${pointer}/${relative}`, "secret-like or Terraform-state input is forbidden");
      if (stats.size > MAX_SOURCE_FILE_BYTES) recipeFail("MTCLI_RECIPE_INPUT_SIZE", `${pointer}/${relative}`, `input exceeds ${MAX_SOURCE_FILE_BYTES} bytes`);
      const bytes = readBoundedFileSync(absolute, MAX_SOURCE_FILE_BYTES);
      total += bytes.length;
      if (total > MAX_RECIPE_INPUT_BYTES) recipeFail("MTCLI_RECIPE_INPUT_SIZE", pointer, `input tree exceeds ${MAX_RECIPE_INPUT_BYTES} bytes`);
      let content: string;
      try { content = UTF8.decode(bytes); } catch { recipeFail("MTCLI_RECIPE_INPUT_ENCODING", `${pointer}/${relative}`, "the first recipe target accepts UTF-8 text inputs only"); }
      files.push(Object.freeze({ relative_path: consumerRelative, content, size_bytes: bytes.length, sha256: sha256(bytes) }));
      if (files.length > MAX_RECIPE_INPUT_FILES) recipeFail("MTCLI_RECIPE_INPUT_COUNT", pointer, `input tree exceeds ${MAX_RECIPE_INPUT_FILES} files`);
    }
  };
  walk(root);
  return Object.freeze(files);
}

function readIntegrationManifest(sourceRoot: string, bindingSetId: string): SystemIntegrationBindingManifestV1 {
  const relative = `integrations/${bindingSetId}.json`;
  const absolute = path.resolve(sourceRoot, relative);
  if (path.relative(sourceRoot, absolute).startsWith("..")) recipeFail("MTCLI_RECIPE_BINDING", `/integration_binding_ids/${bindingSetId}`, "binding path escapes source root");
  let stats: fs.Stats;
  try { stats = fs.lstatSync(absolute); } catch { recipeFail("MTCLI_RECIPE_BINDING", `/integration_binding_ids/${bindingSetId}`, "integration binding is missing"); }
  if (!stats.isFile() || stats.isSymbolicLink() || fs.realpathSync(absolute) !== absolute) recipeFail("MTCLI_RECIPE_BINDING", `/integration_binding_ids/${bindingSetId}`, "integration binding must be a real regular file");
  let value: unknown;
  try { value = JSON.parse(readBoundedFileSync(absolute).toString("utf8")); } catch { recipeFail("MTCLI_RECIPE_BINDING", `/integration_binding_ids/${bindingSetId}`, "integration binding is not valid bounded JSON"); }
  const manifest = compileSystemIntegrationManifest(value, "typescript");
  if (manifest.binding_set_id !== bindingSetId) recipeFail("MTCLI_RECIPE_BINDING", `/integration_binding_ids/${bindingSetId}`, "integration binding identity differs from its selected ID");
  return manifest;
}

function applicationArtifacts(consumerRoot: string, request: DeploymentRecipeRequestV1): { readonly planned: readonly PlannedDeploymentRecipeArtifactV1[]; readonly inputs: readonly DeploymentRecipeArtifactV1[] } {
  const applicationRoot = containedDirectory(consumerRoot, request.application.source_root, "/application/source_root");
  const inputs = inventoryTextTree(applicationRoot, request.application.source_root, "/application/source_root");
  const relativeFiles = new Set(inputs.map(({ relative_path }) => relative_path.slice(request.application.source_root.length + 1)));
  if (!relativeFiles.has("package.json")) recipeFail("MTCLI_RECIPE_APPLICATION", "/application/source_root", "application root requires package.json");
  if (request.application.lockfile !== "package-lock.json" || !relativeFiles.has(request.application.lockfile)) recipeFail("MTCLI_RECIPE_APPLICATION", "/application/lockfile", "TypeScript recipe requires package-lock.json at the application root");
  const packageFile = inputs.find(({ relative_path }) => relative_path === `${request.application.source_root}/package.json`)!;
  let packageValue: Record<string, unknown>;
  try { packageValue = JSON.parse(packageFile.content) as Record<string, unknown>; } catch { recipeFail("MTCLI_RECIPE_APPLICATION", "/application/source_root/package.json", "application package.json is invalid"); }
  const scripts = packageValue.scripts;
  if (scripts === null || typeof scripts !== "object" || Array.isArray(scripts) || typeof (scripts as Record<string, unknown>).build !== "string") recipeFail("MTCLI_RECIPE_APPLICATION", "/application/source_root/package.json", "application package.json requires a build script");
  const planned = inputs.map((artifact) => plannedRecipeArtifact(`application/${artifact.relative_path.slice(request.application.source_root.length + 1)}`, artifact.content));
  return Object.freeze({ planned: Object.freeze(planned), inputs: Object.freeze(inputs.map(({ content: ignored, ...artifact }) => Object.freeze(artifact))) });
}

function migrationArtifacts(consumerRoot: string, request: DeploymentRecipeRequestV1): { readonly planned: readonly PlannedDeploymentRecipeArtifactV1[]; readonly inputs: readonly DeploymentRecipeArtifactV1[] } {
  const migrationRoot = containedDirectory(consumerRoot, request.application.domain_migrations_root, "/application/domain_migrations_root");
  const inputs = inventoryTextTree(migrationRoot, request.application.domain_migrations_root, "/application/domain_migrations_root", (relative) => relative.endsWith(".sql"));
  if (inputs.length === 0) recipeFail("MTCLI_RECIPE_MIGRATIONS", "/application/domain_migrations_root", "at least one domain migration is required");
  const planned = inputs.map((artifact) => plannedRecipeArtifact(`database/domain/${artifact.relative_path.slice(request.application.domain_migrations_root.length + 1)}`, artifact.content));
  const inventory = inputs.map(({ content: ignored, ...artifact }) => Object.freeze(artifact));
  planned.push(plannedRecipeArtifact("database/domain-migrations.manifest.json", `${canonicalJson({ schema_version: "domainspec.domain-migration-manifest/v1", artifacts: inventory, authority_effect: "none" })}\n`));
  return Object.freeze({ planned: Object.freeze(planned), inputs: Object.freeze(inventory) });
}

function appendUnique(target: PlannedDeploymentRecipeArtifactV1[], paths: Set<string>, artifact: PlannedDeploymentRecipeArtifactV1): void {
  if (paths.has(artifact.relative_path)) recipeFail("MTCLI_RECIPE_COLLISION", `/artifacts/${artifact.relative_path}`, "recipe artifact paths collide");
  paths.add(artifact.relative_path); target.push(artifact);
}

export function planDeploymentRecipe(sourceRoot: string, requestValue: unknown, consumerRootValue: string): DeploymentRecipePlanV1 {
  const request = decodeDeploymentRecipeRequest(requestValue);
  const consumerRoot = realDirectory(consumerRootValue, "/consumer-root");
  const graph = loadCompiledProjectGraph(sourceRoot);
  const certificate = createCompiledProjectCertificate(graph);
  const interchange = createCheckedInterchange(graph);
  const manifests = request.integration_binding_ids.map((id) => readIntegrationManifest(graph.project_root, id));
  const selectedNodes = new Set<string>();
  const selectedEdges = new Set<string>();
  const apiEvidence = new Set<string>();
  const workerEvidence = new Set<string>();
  const postgresEvidence = new Set<string>();
  const outboxEvidence = new Set<string>();
  const channelEvidence = new Set<string>();
  const publisherEvidence = new Set<string>();
  const consumerEvidence = new Set<string>();
  const messagePlans: DeploymentRecipeMessageV1[] = [];
  for (const manifest of manifests) {
    const subject = graph.nodes.find(({ selector }) => selector === manifest.subject_ref);
    if (!subject || subject.kind !== "Operation") recipeFail("MTCLI_RECIPE_BINDING_SUBJECT", `/integration_binding_ids/${manifest.binding_set_id}`, "recipe integration subject must be one compiled Operation");
    selectedNodes.add(subject.selector);
    const bindings = manifest.canonical_bindings as Record<string, unknown>;
    const persistence = bindings.persistence_bindings as readonly Record<string, unknown>[];
    const transactions = bindings.transaction_guarantee_bindings as readonly Record<string, unknown>[];
    if (!Array.isArray(persistence) || persistence.length === 0) recipeFail("MTCLI_RECIPE_PERSISTENCE", `/integration_binding_ids/${manifest.binding_set_id}`, "PostgreSQL recipe requires a persistence binding");
    if (!Array.isArray(transactions) || transactions.length === 0 || transactions.some((binding) => !Array.isArray(binding.selected_guarantees) || !(binding.selected_guarantees as readonly unknown[]).includes("atomicity") || !Array.isArray(binding.participant_refs) || !(binding.participant_refs as readonly unknown[]).some((entry) => typeof entry === "string" && entry.includes("outbox")))) {
      recipeFail("MTCLI_RECIPE_TRANSACTION", `/integration_binding_ids/${manifest.binding_set_id}`, "transactional outbox recipe requires atomicity and an outbox participant");
    }
    for (const binding of persistence) postgresEvidence.add(`binding:${String(binding.binding_id)}`);
    for (const binding of transactions) outboxEvidence.add(`binding:${String(binding.binding_id)}`);
    const exposes = graph.relationships.filter(({ relationship, target }) => relationship === "exposes" && `${target.feature_id}:${target.node_id}` === subject.selector);
    if (exposes.length === 0 || exposes.some(({ source }) => source.kind !== "Interface")) recipeFail("MTCLI_RECIPE_API_EVIDENCE", `/integration_binding_ids/${manifest.binding_set_id}`, "API component requires Interface exposes Operation evidence");
    for (const edge of exposes) { selectedEdges.add(edge.edge_id); selectedNodes.add(`${edge.source.feature_id}:${edge.source.node_id}`); apiEvidence.add(`edge:${edge.edge_id}`); }
    const produces = graph.relationships.filter(({ relationship, source }) => relationship === "produces" && `${source.feature_id}:${source.node_id}` === subject.selector);
    if (produces.length === 0 || produces.some(({ target }) => target.kind !== "Event")) recipeFail("MTCLI_RECIPE_WORKER_EVIDENCE", `/integration_binding_ids/${manifest.binding_set_id}`, "outbox worker requires Operation produces Event evidence");
    for (const edge of produces) { selectedEdges.add(edge.edge_id); selectedNodes.add(`${edge.target.feature_id}:${edge.target.node_id}`); workerEvidence.add(`edge:${edge.edge_id}`); }
    const channels = bindings.message_channels as readonly Record<string, unknown>[];
    const transports = bindings.transport_bindings as readonly Record<string, unknown>[];
    const deliveryPolicies = bindings.delivery_policies as readonly Record<string, unknown>[];
    const failurePolicies = bindings.transport_failure_policies as readonly Record<string, unknown>[];
    if (!Array.isArray(channels) || !Array.isArray(transports) || transports.length === 0 || !Array.isArray(deliveryPolicies) || !Array.isArray(failurePolicies)) recipeFail("MTCLI_RECIPE_MESSAGE_BINDING", `/integration_binding_ids/${manifest.binding_set_id}`, "SQS recipe requires a closed message transport binding");
    for (const transport of transports) {
      const operationRef = String(transport.operation_ref);
      const eventRef = String(transport.event_ref);
      if (operationRef !== subject.selector) recipeFail("MTCLI_RECIPE_MESSAGE_PUBLISHER", `/integration_binding_ids/${manifest.binding_set_id}`, "transport publisher must equal the selected Operation subject");
      const event = graph.nodes.find(({ selector }) => selector === eventRef);
      if (!event || event.kind !== "Event") recipeFail("MTCLI_RECIPE_MESSAGE_EVENT", `/integration_binding_ids/${manifest.binding_set_id}`, `transport Event is not compiled:${eventRef}`);
      const producesEdge = graph.relationships.find(({ relationship, source, target }) => relationship === "produces" && `${source.feature_id}:${source.node_id}` === operationRef && `${target.feature_id}:${target.node_id}` === eventRef);
      if (!producesEdge) recipeFail("MTCLI_RECIPE_MESSAGE_PRODUCES", `/integration_binding_ids/${manifest.binding_set_id}`, "message transport requires the exact Operation produces Event edge");
      const channel = channels.find(({ channel_id }) => channel_id === transport.channel_ref);
      const delivery = deliveryPolicies.find(({ policy_id }) => policy_id === transport.delivery_policy_ref);
      const failure = failurePolicies.find(({ policy_id }) => policy_id === transport.failure_policy_ref);
      if (!channel || channel.purpose !== "delivery" || !delivery || !failure) recipeFail("MTCLI_RECIPE_MESSAGE_BINDING", `/integration_binding_ids/${manifest.binding_set_id}`, "message transport references an incomplete channel or policy");
      const consumers = channel.consumer_operation_refs as readonly unknown[];
      if (!Array.isArray(consumers) || consumers.length === 0) recipeFail("MTCLI_RECIPE_MESSAGE_CONSUMER", `/integration_binding_ids/${manifest.binding_set_id}`, "message channel requires at least one consumer Operation");
      const consumerRefs = consumers.map(String).sort();
      for (const consumerRef of consumerRefs) {
        const consumer = graph.nodes.find(({ selector }) => selector === consumerRef);
        if (!consumer || consumer.kind !== "Operation") recipeFail("MTCLI_RECIPE_MESSAGE_CONSUMER", `/integration_binding_ids/${manifest.binding_set_id}`, `message consumer is not a compiled Operation:${consumerRef}`);
        const trigger = graph.relationships.find(({ relationship, source, target }) => relationship === "triggers-cross" && `${source.feature_id}:${source.node_id}` === eventRef && `${target.feature_id}:${target.node_id}` === consumerRef);
        if (!trigger) recipeFail("MTCLI_RECIPE_MESSAGE_TRIGGER", `/integration_binding_ids/${manifest.binding_set_id}`, `message consumer lacks Event triggers-cross Operation evidence:${consumerRef}`);
        selectedEdges.add(trigger.edge_id); selectedNodes.add(consumerRef); consumerEvidence.add(`edge:${trigger.edge_id}`);
      }
      selectedEdges.add(producesEdge.edge_id); selectedNodes.add(eventRef);
      channelEvidence.add(`channel:${String(channel.channel_id)}`); channelEvidence.add(`channel:${String(delivery.dead_letter_channel_ref)}`);
      publisherEvidence.add(`binding:${String(transport.binding_id)}`); publisherEvidence.add(`edge:${producesEdge.edge_id}`);
      const deadLetter = channels.find(({ channel_id }) => channel_id === delivery.dead_letter_channel_ref);
      if (!deadLetter || deadLetter.purpose !== "dead-letter") recipeFail("MTCLI_RECIPE_MESSAGE_BINDING", `/integration_binding_ids/${manifest.binding_set_id}`, "delivery policy requires one dead-letter channel");
      messagePlans.push(Object.freeze({ transport_binding_id: String(transport.binding_id), event_ref: eventRef, publisher_operation_ref: operationRef, consumer_operation_refs: Object.freeze(consumerRefs), channel_id: String(channel.channel_id), dead_letter_channel_id: String(deadLetter.channel_id), visibility_timeout_seconds: Number(delivery.visibility_timeout_seconds), retention_seconds: Number(delivery.retention_seconds), max_receive_count: Number(delivery.max_receive_count), publish_max_attempts: Number(failure.max_attempts), envelope_profile_ref: "envelope:domainspec-event-json-v1" as const, deduplication_owner_ref: "consumer:inbox-message-id" as const }));
    }
  }
  if (messagePlans.length !== 1) recipeFail("MTCLI_RECIPE_MESSAGE_CARDINALITY", "/integration_binding_ids", "the first SQS recipe target requires exactly one message transport binding");
  const messaging = messagePlans[0]!;
  const components: readonly DeploymentRecipeComponentV1[] = Object.freeze([
    Object.freeze({ component: "api", evidence_refs: Object.freeze([...apiEvidence].sort()) }),
    Object.freeze({ component: "outbox-worker", evidence_refs: Object.freeze([...workerEvidence].sort()) }),
    Object.freeze({ component: "postgresql", evidence_refs: Object.freeze([...postgresEvidence].sort()) }),
    Object.freeze({ component: "transactional-outbox", evidence_refs: Object.freeze([...outboxEvidence].sort()) }),
    Object.freeze({ component: "message-channel", evidence_refs: Object.freeze([...channelEvidence].sort()) }),
    Object.freeze({ component: "message-publisher", evidence_refs: Object.freeze([...publisherEvidence].sort()) }),
    Object.freeze({ component: "message-consumer", evidence_refs: Object.freeze([...consumerEvidence].sort()) }),
  ]);
  const application = applicationArtifacts(consumerRoot, request);
  const migrations = migrationArtifacts(consumerRoot, request);
  const projectBuild = planProjectBuild(graph.project_root, "typescript");
  const artifacts: PlannedDeploymentRecipeArtifactV1[] = [];
  const paths = new Set<string>();
  for (const artifact of application.planned) appendUnique(artifacts, paths, artifact);
  for (const artifact of projectBuild.artifacts) appendUnique(artifacts, paths, plannedRecipeArtifact(`application/${artifact.relative_path}`, artifact.content));
  appendUnique(artifacts, paths, plannedRecipeArtifact("application/.domainspec/project-build.json", `${canonicalJson(projectBuild.receipt)}\n`));
  for (const artifact of migrations.planned) appendUnique(artifacts, paths, artifact);
  const bindingDigests = manifests.map(({ binding_digest }) => binding_digest).sort();
  const targetArtifacts = renderAwsEcsFargatePostgresRecipe(request, bindingDigests, messaging);
  validateAwsRecipePolicy(targetArtifacts);
  const targetImplementationSha256 = sha256(canonicalJson(recipeArtifactInventory(targetArtifacts)));
  for (const artifact of targetArtifacts) appendUnique(artifacts, paths, artifact);
  artifacts.sort((left, right) => left.relative_path.localeCompare(right.relative_path));
  const inputArtifacts = Object.freeze([...application.inputs, ...migrations.inputs].sort((left, right) => left.relative_path.localeCompare(right.relative_path)));
  const payloadInventory = recipeArtifactInventory(artifacts);
  const manifestBody = {
    schema_version: "domainspec.deployment-recipe-manifest/v1" as const,
    request_id: request.request_id,
    target: request.target,
    project_id: graph.project_id,
    source_manifest_sha256: graph.source_manifest.manifest_sha256,
    compiled_certificate_sha256: certificate.certificate_sha256,
    checked_interchange_sha256: interchange.interchange_sha256,
    request_sha256: deploymentRecipeRequestSha256(request),
    target_implementation_sha256: targetImplementationSha256,
    selected_node_selectors: Object.freeze([...selectedNodes].sort()),
    selected_relationship_edge_ids: Object.freeze([...selectedEdges].sort()),
    selected_binding_ids: Object.freeze(manifests.map(({ binding_set_id }) => binding_set_id).sort()),
    selected_bindings: Object.freeze(manifests
      .map(({ binding_set_id, binding_digest }) => Object.freeze({ binding_set_id, binding_digest }))
      .sort((left, right) => left.binding_set_id.localeCompare(right.binding_set_id))),
    components: Object.freeze(components.map(({ component }) => component)),
    input_artifacts: inputArtifacts,
    artifacts: payloadInventory,
    authority_effect: "none" as const,
  };
  const manifest: DeploymentRecipeManifestV1 = Object.freeze({ ...manifestBody, manifest_sha256: sha256(canonicalJson(manifestBody)) });
  const manifestArtifact = plannedRecipeArtifact("deployment-manifest.json", `${canonicalJson(manifest)}\n`);
  appendUnique(artifacts, paths, manifestArtifact);
  artifacts.sort((left, right) => left.relative_path.localeCompare(right.relative_path));
  const planIdentity = Object.freeze({ schema_version: "domainspec.deployment-recipe-plan/v1", manifest_sha256: manifest.manifest_sha256, artifacts: recipeArtifactInventory(artifacts), authority_effect: "none" });
  const planSha256 = sha256(canonicalJson(planIdentity));
  const receiptBody = {
    schema_version: "domainspec.deployment-recipe-receipt/v1" as const,
    request_id: request.request_id,
    target: request.target,
    project_id: graph.project_id,
    source_manifest_sha256: graph.source_manifest.manifest_sha256,
    compiled_certificate_sha256: certificate.certificate_sha256,
    checked_interchange_sha256: interchange.interchange_sha256,
    request_sha256: deploymentRecipeRequestSha256(request),
    target_implementation_sha256: targetImplementationSha256,
    manifest_sha256: manifest.manifest_sha256,
    plan_sha256: planSha256,
    artifact_count: artifacts.length + 1,
    authority_effect: "none" as const,
  };
  const receipt: DeploymentRecipeReceiptV1 = Object.freeze({ ...receiptBody, receipt_sha256: sha256(canonicalJson(receiptBody)) });
  appendUnique(artifacts, paths, plannedRecipeArtifact(".domainspec/deployment-recipe-receipt.json", `${canonicalJson(receipt)}\n`));
  artifacts.sort((left, right) => left.relative_path.localeCompare(right.relative_path));
  return Object.freeze({ schema_version: "domainspec.deployment-recipe-plan/v1", request, consumer_root: consumerRoot, components, messaging, manifest, receipt, artifacts: Object.freeze(artifacts), plan_sha256: planSha256, authority_effect: "none" });
}

export function deploymentRecipePlanSummary(plan: DeploymentRecipePlanV1): Readonly<Record<string, unknown>> {
  return Object.freeze({
    schema_version: plan.schema_version,
    request_id: plan.request.request_id,
    target: plan.request.target,
    project_id: plan.manifest.project_id,
    source_manifest_sha256: plan.manifest.source_manifest_sha256,
    components: Object.freeze(plan.components.map(({ component, evidence_refs }) => Object.freeze({ component, evidence_refs }))),
    messaging: plan.messaging,
    artifact_count: plan.artifacts.length,
    artifacts: recipeArtifactInventory(plan.artifacts),
    manifest_sha256: plan.manifest.manifest_sha256,
    plan_sha256: plan.plan_sha256,
    receipt_sha256: plan.receipt.receipt_sha256,
    authority_effect: "none",
  });
}
