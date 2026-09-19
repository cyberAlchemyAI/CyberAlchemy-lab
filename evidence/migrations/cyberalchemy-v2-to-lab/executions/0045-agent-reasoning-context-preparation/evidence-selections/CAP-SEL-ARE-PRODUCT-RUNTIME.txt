import {createHash} from "node:crypto";
import {readFileSync, readdirSync, statSync} from "node:fs";
import {resolve} from "node:path";
import {fileURLToPath} from "node:url";

import {loadRepositoryProfile} from "../packages/codex-app-server-wrapper/index.mjs";

export const productRoot = resolve(fileURLToPath(new URL("..", import.meta.url)));
export const repositoryRoot = resolve(productRoot, "../../..");

function readJson(path) {
  return JSON.parse(readFileSync(path, "utf8"));
}

function directory(path) {
  try { return statSync(path).isDirectory(); } catch { return false; }
}

function sha256(bytes) {
  return createHash("sha256").update(bytes).digest("hex");
}

function collectFiles(root, exclusions, output = []) {
  for (const entry of readdirSync(root, {withFileTypes: true}).sort((a, b) => a.name.localeCompare(b.name))) {
    const path = resolve(root, entry.name);
    const repositoryPath = path.slice(repositoryRoot.length).replaceAll("\\", "/");
    if (exclusions.some((exclusion) => `${repositoryPath}/`.includes(exclusion))) continue;
    if (entry.isDirectory()) collectFiles(path, exclusions, output);
    else if (entry.isFile()) output.push(path);
  }
  return output;
}

export function materializeProductClosure() {
  const profile = readJson(resolve(productRoot, "product.json"));
  const files = profile.source_roots.flatMap((root) => collectFiles(resolve(repositoryRoot, root), profile.closure_exclusions));
  const entries = files.map((path) => {
    const bytes = readFileSync(path);
    return {path: path.slice(repositoryRoot.length + 1).replaceAll("\\", "/"), bytes: bytes.length, sha256: sha256(bytes)};
  }).sort((a, b) => a.path.localeCompare(b.path));
  const material = {schema_version: "are.product-source-closure/v1", product_id: profile.product_id, product_version: profile.version, files: entries, authority_effect: "none"};
  return Object.freeze({...material, closure_digest: sha256(JSON.stringify(material))});
}

export function inspectProduct(options = {}) {
  const profilePath = resolve(productRoot, "product.json");
  const profile = readJson(profilePath);
  const problems = [];
  if (profile.schema_version !== "are.product-profile/v1") problems.push("product.schema-version-invalid");
  if (profile.status !== "stability-candidate") problems.push("product.status-invalid");
  if (profile.authority_effect !== "none") problems.push("product.authority-effect-invalid");
  const componentStates = profile.components.map((component) => {
    const path = resolve(productRoot, component.path);
    const present = directory(path);
    if (component.required && !present) problems.push(`product.component-missing:${component.component_id}`);
    let packageName = null;
    try { packageName = readJson(resolve(path, "package.json")).name ?? null; } catch {
      if (component.required) problems.push(`product.component-package-invalid:${component.component_id}`);
    }
    return {component_id: component.component_id, path, present, package_name: packageName};
  });
  const integrationStates = profile.integrations.map((integration) => {
    const path = resolve(productRoot, integration.path);
    const present = directory(path);
    if (integration.required && !present) problems.push(`product.integration-missing:${integration.integration_id}`);
    return {integration_id: integration.integration_id, path, present};
  });
  const loaded = loadRepositoryProfile(resolve(productRoot, profile.repository_profile), repositoryRoot);
  if (!loaded.ok) problems.push(...(loaded.reason_codes ?? ["product.repository-profile-invalid"]));
  const runtimeMatches = process.versions.node === profile.node_runtime;
  if (options.require_exact_runtime === true && !runtimeMatches) problems.push("product.node-runtime-mismatch");
  const sourceClosure = materializeProductClosure();
  return Object.freeze({
    schema_version: "are.product-health/v1",
    status: problems.length === 0 ? "PASS" : "FAIL",
    product_id: profile.product_id,
    product_version: profile.version,
    product_status: profile.status,
    node: {expected: profile.node_runtime, observed: process.versions.node, exact_match: runtimeMatches},
    repository_profile: {path: resolve(productRoot, profile.repository_profile), verified: loaded.ok === true, profile_id: loaded.ok ? loaded.value.profile_id : null},
    components: componentStates,
    integrations: integrationStates,
    source_closure: {closure_digest: sourceClosure.closure_digest, file_count: sourceClosure.files.length, total_bytes: sourceClosure.files.reduce((sum, entry) => sum + entry.bytes, 0)},
    reason_codes: [...new Set(problems)].sort(),
    authority_effect: "none",
  });
}
