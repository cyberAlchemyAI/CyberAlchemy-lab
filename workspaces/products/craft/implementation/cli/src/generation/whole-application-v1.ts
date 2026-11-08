import path from "node:path";

import { loadCompiledProjectGraph } from "../input/project-model.js";
import { canonicalJson, sha256 } from "../input/source-manifest.js";
import {
  assertApplicationIntegrationBinding,
  validateApplicationIntegrationBinding,
  type ApplicationIntegrationBindingV1,
} from "../system-integration/application-binding-v1.js";
import {
  assertEmbeddedIntegrationContribution,
  planEmbeddedIntegrationContributionV1,
  type EmbeddedIntegrationContributionV1,
} from "../system-integration/embedded-generation-v1.js";
import type { IntegrationGenerationSourceV2 } from "../system-integration/generation-v2.js";
import type { IntegrationGenerationLanguage } from "../system-integration/integration-project-layout-v1.js";
import type { PlannedArtifact } from "./contracts.js";
import { selectReconciledProjectArtifacts, selectComposedReconciledProjectArtifacts } from "./reconciled-project-layout.js";
import { planCompiledComposedReconciledProject, type ComposedReconciledProjectPlan, type ComposedReconciledCompilationSelection } from "./reconciled-project.js";
import { outputImport } from "./output-layout.js";
import { renderApplicationRequestHandlers } from "./application-request-handlers.js";
import {
  isReconciledPythonProject,
  isReconciledRustProject,
  planCompiledSelectedReconciledProject,
  selectedReconciledIdentity,
  type SelectedReconciledCompilation,
  type SelectedReconciledProject,
} from "./selected-reconciled-project.js";

export interface WholeApplicationPathOwnerV1 {
  readonly relative_path: string;
  readonly owner: "reconciled-application" | "embedded-integration" | "whole-application-composer";
  readonly sha256: string;
}

export interface WholeApplicationPlanV1 {
  readonly schema_version: "domainspec.whole-application-plan/v1-candidate";
  readonly language: IntegrationGenerationLanguage;
  readonly project_id: string;
  readonly domain_source_manifest_sha256: string;
  readonly integration_source_sha256: string;
  readonly integration_semantic_manifest_sha256: string;
  readonly selection_sha256: string;
  readonly application_plan_sha256: string;
  readonly integration_plan_sha256: string;
  readonly integration_contribution_sha256: string;
  readonly binding_sha256: string;
  readonly application_graph_sha256: string;
  readonly artifacts: readonly PlannedArtifact[];
  readonly path_owners: readonly WholeApplicationPathOwnerV1[];
  readonly native_type_dependencies: readonly string[];
  readonly runtime_guarantees_observed: false;
  readonly claim_ceiling: "formation-and-static-compilation-only";
  readonly authority_effect: "none";
  readonly plan_sha256: string;
}

export class WholeApplicationPlanError extends Error {
  readonly exitCode = 22;
  constructor(readonly code: string, readonly pointer: string, message: string) {
    super(`${code}:${pointer}:${message}`);
    this.name = "WholeApplicationPlanError";
  }
}

type ProjectArtifactView = ReturnType<typeof selectReconciledProjectArtifacts>;
type OwnedArtifact = Readonly<{ artifact: PlannedArtifact; owner: WholeApplicationPathOwnerV1["owner"] }>;
type ApplicationModuleView = Readonly<{
  relative_path: string;
  selector?: string;
  kind?: string;
  qualified_selectors?: readonly string[];
  exports?: readonly Readonly<{ name: string; kind: string }>[];
  bindings?: readonly string[];
}>;
type RuntimeMappingBinding = ApplicationIntegrationBindingV1["application_graph"]["runtime_bindings"][number];
const plans = new WeakMap<WholeApplicationPlanV1, string>();

function fail(code: string, pointer: string, message: string): never {
  throw new WholeApplicationPlanError(code, pointer, message);
}

function freeze<T>(value: T): T {
  if (value !== null && typeof value === "object" && !Object.isFrozen(value)) {
    Object.freeze(value);
    for (const child of Object.values(value as Record<string, unknown>)) freeze(child);
  }
  return value;
}

function artifact(relativePath: string, content: string): PlannedArtifact {
  return freeze({ relative_path: relativePath, content, size_bytes: Buffer.byteLength(content), sha256: sha256(content) });
}

function applicationGraphArtifact(binding: ApplicationIntegrationBindingV1): PlannedArtifact {
  return artifact(".domainspec/application-graph.json", `${canonicalJson(binding.application_graph)}\n`);
}

function safePath(value: string, pointer: string): void {
  if (!value || value.startsWith("/") || value.includes("\\") || path.posix.normalize(value) !== value || value.split("/").includes("..")) {
    fail("DS_WHOLE_APPLICATION_PATH", pointer, `unsafe artifact path:${value}`);
  }
}

function rootManifest(contribution: EmbeddedIntegrationContributionV1, applicationView: ProjectArtifactView, projectId: string): PlannedArtifact {
  if (contribution.root_manifest_contribution.manifest_kind !== contribution.language) fail("DS_WHOLE_APPLICATION_LANGUAGE", "/integration_contribution/root_manifest_contribution", "manifest kind must match contribution language");
  if (contribution.language === "typescript") {
    const include = [...new Set(["src/**/*.ts", "migrations/**/*.ts", ...contribution.root_manifest_contribution.source_globs])].sort();
    const content = `${canonicalJson({ compilerOptions: { target: "ES2022", module: "NodeNext", moduleResolution: "NodeNext", strict: true, noEmit: true, noUnusedLocals: true, noUnusedParameters: true }, include })}\n`;
    return artifact("tsconfig.json", content);
  }
  if (contribution.language === "python") {
    const name = projectId.toLocaleLowerCase("en-US").replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "") || "domainspec-application";
    return artifact("pyproject.toml", `[project]\nname = ${JSON.stringify(name)}\nversion = "0.0.0"\nrequires-python = ">=3.11"\n`);
  }
  const source = applicationView.artifacts.find(item => item.relative_path === "Cargo.toml");
  if (!source) fail("DS_WHOLE_APPLICATION_ROOT_MANIFEST", "/application/artifacts/Cargo.toml", "Rust application plan has no Cargo manifest");
  return artifact("Cargo.toml", source.content);
}

function nodeCryptoDeclaration(): PlannedArtifact {
  return artifact("src/types/node-crypto.d.ts", "declare module \"node:crypto\" {\n  interface Hash { update(data: string): Hash; digest(encoding: \"hex\"): string; }\n  export function createHash(algorithm: \"sha256\"): Hash;\n}\n");
}

function applicationModules(applicationView: ProjectArtifactView): readonly ApplicationModuleView[] {
  return applicationView.modules as readonly ApplicationModuleView[];
}

function modulesForBinding(applicationView: ProjectArtifactView, binding: ApplicationIntegrationBindingV1): readonly Readonly<{ selector: string; module: ApplicationModuleView }>[] {
  const modules = applicationModules(applicationView);
  return [...new Set(binding.references.map(item => item.selector))].sort().map(selector => {
    const candidates = modules.filter(item => item.selector === selector || item.qualified_selectors?.includes(selector));
    const selected = candidates.sort((left, right) => Number(left.relative_path.includes("/_providers/") || left.relative_path.includes(".provider.")) - Number(right.relative_path.includes("/_providers/") || right.relative_path.includes(".provider.")) || left.relative_path.localeCompare(right.relative_path))[0];
    if (!selected) fail("DS_WHOLE_APPLICATION_TYPED_BINDING", `/binding/${selector}`, "no generated application module for bound selector");
    return freeze({ selector, module: selected });
  });
}

function typescriptDomainBindingArtifact(applicationView: ProjectArtifactView, binding: ApplicationIntegrationBindingV1): PlannedArtifact {
  const relativePath = "src/integrations/domain-bindings.ts";
  const modules = applicationModules(applicationView);
  const selectors = [...new Set(binding.references.map(item => item.selector))].sort();
  const imports: string[] = [];
  const types: string[] = [];
  const descriptors: Readonly<{ selector: string; module_path: string; exported_types: readonly string[]; exported_values: readonly string[] }>[] = selectors.map((selector, index) => {
    const candidates = modules.filter(item => item.qualified_selectors?.includes(selector) && item.exports?.length);
    const selected = candidates.sort((left, right) => Number(left.relative_path.endsWith(".provider.ts")) - Number(right.relative_path.endsWith(".provider.ts")) || Number(!left.exports?.some(row => row.kind === "type")) - Number(!right.exports?.some(row => row.kind === "type")) || left.relative_path.localeCompare(right.relative_path))[0];
    if (!selected) fail("DS_WHOLE_APPLICATION_TYPED_BINDING", `/binding/${selector}`, "no generated TypeScript surface for bound selector");
    const exported = selected.exports!.filter(item => item.kind === "type").map(item => item.name).sort();
    const values = selected.exports!.filter(item => item.kind === "value").map(item => item.name).sort();
    const namespace = `Application${index}`;
    imports.push(`import * as ${namespace} from ${JSON.stringify(outputImport(relativePath, selected.relative_path).replace(/\.ts$/, ".js"))};`);
    types.push(...exported.map(name => `${namespace}.${name}`));
    return freeze({ selector, module_path: selected.relative_path, exported_types: Object.freeze(exported), exported_values: Object.freeze(values) });
  });
  const union = [...new Set(types)].join(" | ") || "never";
  const namespaces = selectors.map((_selector, index) => `Application${index}`).join(",");
  const content = `${imports.join("\n")}\nexport type ApplicationInput=${union};\nexport type ApplicationResult=${union};\nexport const APPLICATION_INTEGRATION_MODULES=Object.freeze([${namespaces}]);\nexport const APPLICATION_INTEGRATION_BINDINGS=${canonicalJson(descriptors)} as const;\n`;
  return artifact(relativePath, content);
}

function pythonPackage(applicationView: ProjectArtifactView): string {
  const roots = applicationView.artifacts.map(item => /^src\/([a-z][a-z0-9_]*)\/__init__\.py$/.exec(item.relative_path)?.[1]).filter((item): item is string => item !== undefined);
  if (new Set(roots).size !== 1) fail("DS_WHOLE_APPLICATION_PYTHON_ROOT", "/application/artifacts", "Python application must have exactly one source package root");
  return roots[0]!;
}

function pythonModule(relativePath: string): string {
  if (!relativePath.startsWith("src/") || !relativePath.endsWith(".py")) fail("DS_WHOLE_APPLICATION_PYTHON_MODULE", `/application/artifacts/${relativePath}`, "bound Python module must be under src and end in .py");
  return relativePath.slice(4, -3).split("/").join(".").replace(/\.__init__$/, "");
}

function pascal(value: string): string {
  return value.split(/[-_:]+/).filter(Boolean).map(part => `${part[0]!.toUpperCase()}${part.slice(1)}`).join("");
}

function snake(value: string): string {
  const result = value.replace(/[^A-Za-z0-9]+/g, "_").replace(/^_+|_+$/g, "").toLocaleLowerCase("en-US");
  if (!result || !/^[a-z]/.test(result)) fail("DS_WHOLE_APPLICATION_RUNTIME_MAPPING", `/application_graph/runtime_bindings/${value}`, "binding id does not form a native invocation symbol");
  return result;
}

function pythonDataType(row: Readonly<{ selector: string; module: ApplicationModuleView }>, applicationView: ProjectArtifactView): string {
  const source = applicationView.artifacts.find(item => item.relative_path === row.module.relative_path)?.content ?? "";
  const local = pascal(row.selector.split(":")[1]!);
  const candidates = [`${local}Snapshot`, local, `${local}Case`];
  const selected = candidates.find(name => new RegExp(`\\bclass\\s+${name}\\b`).test(source));
  if (!selected) fail("DS_WHOLE_APPLICATION_PYTHON_TYPE", `/binding/${row.selector}`, "no generated Python application type for data selector");
  return selected;
}

function pythonDomainBindingArtifact(applicationView: ProjectArtifactView, binding: ApplicationIntegrationBindingV1): PlannedArtifact {
  const root = pythonPackage(applicationView);
  const rows = modulesForBinding(applicationView, binding);
  const imports = rows.map((row, index) => `import ${pythonModule(row.module.relative_path)} as _application_${index}`);
  const dataSelectors = [...new Set(binding.references.filter(item => item.reference_kind === "data" || item.reference_kind === "public-contract").map(item => item.reference))].sort();
  const typeImports = dataSelectors.map((reference, index) => {
    const [selector, contract] = reference.split("#");
    const row = rows.find(item => item.selector === selector)!;
    const type = contract === undefined ? pythonDataType(row, applicationView) : `Contract_${contract.replaceAll("-", "_")}`;
    return `from ${pythonModule(row.module.relative_path)} import ${type} as _ApplicationType${index}`;
  });
  const union = dataSelectors.length ? dataSelectors.map((_selector, index) => `_ApplicationType${index}`).join(" | ") : "object";
  const descriptors = rows.map(row => ({ selector: row.selector, module_path: row.module.relative_path }));
  const content = `${imports.join("\n")}\n${typeImports.join("\n")}\nimport json as _json\n\nApplicationInput = ${union}\nApplicationResult = ${union}\nAPPLICATION_INTEGRATION_MODULES = (${rows.map((_row, index) => `_application_${index}`).join(", ")},)\nAPPLICATION_INTEGRATION_BINDINGS = _json.loads(${JSON.stringify(canonicalJson(descriptors))})\n`;
  return artifact(`src/${root}/integrations/domain_bindings.py`, content);
}

function rustModule(relativePath: string): string {
  if (!relativePath.startsWith("src/") || !relativePath.endsWith(".rs")) fail("DS_WHOLE_APPLICATION_RUST_MODULE", `/application/artifacts/${relativePath}`, "bound Rust module must be under src and end in .rs");
  return `crate::${relativePath.slice(4, -3).split("/").filter(part => part !== "mod").join("::")}`;
}

function rustDomainBindingArtifact(applicationView: ProjectArtifactView, binding: ApplicationIntegrationBindingV1): PlannedArtifact {
  const rows = modulesForBinding(applicationView, binding);
  const dataSelectors = [...new Set(binding.references.filter(item => item.reference_kind === "data" || item.reference_kind === "public-contract").map(item => item.reference))].sort();
  const dataRows = dataSelectors.map(reference => rows.find(item => item.selector === reference.split("#")[0])!);
  const imports = dataRows.map((row, index) => `use ${rustModule(row.module.relative_path)} as application_${index};`);
  const variants = dataSelectors.map((reference, index) => {
    const [selector, contract] = reference.split("#");
    return `    ${pascal(reference.replace("#", ":"))}(application_${index}::${pascal(contract ?? selector!.split(":")[1]!)}),`;
  });
  const descriptors = rows.map(row => JSON.stringify(`${row.selector}:${row.module.relative_path}`));
  const content = `${imports.join("\n")}\n\npub enum ApplicationValue {\n${variants.join("\n")}\n}\npub type ApplicationInput = ApplicationValue;\npub type ApplicationResult = ApplicationValue;\npub const APPLICATION_INTEGRATION_BINDINGS: &[&str] = &[${descriptors.join(",")}];\n`;
  return artifact("src/integrations/domain_bindings.rs", content);
}

function domainBindingArtifact(language: IntegrationGenerationLanguage, applicationView: ProjectArtifactView, binding: ApplicationIntegrationBindingV1): PlannedArtifact {
  return language === "typescript" ? typescriptDomainBindingArtifact(applicationView, binding) : language === "python" ? pythonDomainBindingArtifact(applicationView, binding) : rustDomainBindingArtifact(applicationView, binding);
}

type OperationRequestContract = ApplicationIntegrationBindingV1["application_graph"]["operation_requests"][number];

export function validateOperationRequestContracts(applicationPlan: Pick<SelectedReconciledProject | ComposedReconciledProjectPlan, "selection">, rows: readonly OperationRequestContract[], runtimeBindings: readonly RuntimeMappingBinding[]): void {
  const operations = applicationPlan.selection.operations as readonly Readonly<{
    selector: string;
    inputs: readonly Readonly<{ name: string; type: unknown }>[];
    events: readonly Readonly<{ parameter: string }>[];
  }>[];
  for (const row of rows) {
    const operation = operations.find(candidate => candidate.selector === row.operation_ref);
    if (!operation) fail("DS_WHOLE_APPLICATION_OPERATION_REQUEST", `/application_graph/operation_requests/${row.request_ref}`, "selected Operation contract is missing");
    const expectedNames = [...operation.inputs.map(input => input.name), ...operation.events.map(event => event.parameter)].sort();
    for (const binding of row.bindings) {
      const actualNames = binding.parameters.map(parameter => parameter.parameter).sort();
      if (canonicalJson(actualNames) !== canonicalJson(expectedNames)) {
        fail("DS_WHOLE_APPLICATION_OPERATION_REQUEST", `/application_graph/operation_requests/${row.request_ref}/bindings/${binding.mapping_binding_ref}/parameters`, `request parameters must exactly cover:${expectedNames.join(",")}`);
      }
      const runtime = runtimeBindings.find(candidate => candidate.binding_id === binding.mapping_binding_ref);
      if (!runtime) fail("DS_WHOLE_APPLICATION_OPERATION_REQUEST", `/application_graph/runtime_bindings/${binding.mapping_binding_ref}`, "request Mapping binding is missing");
      for (const parameter of binding.parameters) {
        if (parameter.source.kind === "source-body" && parameter.source.path.length === 0) {
          fail("DS_WHOLE_APPLICATION_OPERATION_REQUEST", `/application_graph/operation_requests/${row.request_ref}/bindings/${binding.mapping_binding_ref}/parameters/${parameter.parameter}`, "source-body request parameters require an explicit path");
        }
        if (parameter.source.kind !== "mapping-result") continue;
        if (parameter.source.path.length !== 0) fail("DS_WHOLE_APPLICATION_OPERATION_REQUEST", `/application_graph/operation_requests/${row.request_ref}/bindings/${binding.mapping_binding_ref}/parameters/${parameter.parameter}`, "nested Mapping-result request projection is not supported");
        const input = operation.inputs.find(candidate => candidate.name === parameter.parameter);
        if (!input || canonicalJson(input.type) !== canonicalJson(runtime.result_type)) {
          fail("DS_WHOLE_APPLICATION_OPERATION_REQUEST", `/application_graph/operation_requests/${row.request_ref}/bindings/${binding.mapping_binding_ref}/parameters/${parameter.parameter}`, "Mapping result type does not equal the selected Operation input type");
        }
      }
    }
  }
}

function operationModule(applicationView: ProjectArtifactView, operationRef: string, language: IntegrationGenerationLanguage): ApplicationModuleView {
  const modules = applicationModules(applicationView);
  const candidates = modules.filter(item => {
    if (language === "rust") return item.selector === operationRef && item.kind === "Operation";
    const owns = item.selector === operationRef || item.qualified_selectors?.includes(operationRef);
    const exposesInput = language === "typescript" ? item.exports?.some(row => row.kind === "type" && row.name === "OperationInput") : item.bindings?.includes("OperationInput");
    return owns && exposesInput && !item.relative_path.includes("/_providers/") && !item.relative_path.includes(".provider.");
  });
  if (candidates.length !== 1) fail("DS_WHOLE_APPLICATION_OPERATION_REQUEST", `/application_graph/operation_requests/${operationRef}`, `expected one generated Operation request module, received:${candidates.length}`);
  return candidates[0]!;
}

export function operationRequestArtifact(language: IntegrationGenerationLanguage, applicationView: ProjectArtifactView, rows: readonly OperationRequestContract[]): PlannedArtifact {
  if (rows.length === 0) fail("DS_WHOLE_APPLICATION_OPERATION_REQUEST", "/application_graph/operation_requests", "whole application has no explicit Operation Request contract");
  const descriptors = rows.map(row => ({ ...row, native_type: `${pascal(row.operation_ref)}Request` }));
  if (language === "typescript") {
    const relativePath = "src/integrations/operation-requests.ts";
    const imports = rows.map((row, index) => `import type {OperationInput as OperationRequest${index}} from ${JSON.stringify(outputImport(relativePath, operationModule(applicationView, row.operation_ref, language).relative_path).replace(/\.ts$/, ".js"))};`);
    const aliases = rows.map((row, index) => `export type ${pascal(row.operation_ref)}Request=OperationRequest${index};`);
    const map = rows.map((row, index) => `${JSON.stringify(row.request_ref)}:OperationRequest${index}`).join(";");
    return artifact(relativePath, `${imports.join("\n")}\n${aliases.join("\n")}\nexport interface OperationRequestTypes {${map}}\nexport const OPERATION_REQUEST_CONTRACTS=${canonicalJson(descriptors)} as const;\n`);
  }
  if (language === "python") {
    const root = pythonPackage(applicationView);
    const imports = rows.map((row, index) => `from ${pythonModule(operationModule(applicationView, row.operation_ref, language).relative_path)} import OperationInput as _OperationRequest${index}`);
    const aliases = rows.map((row, index) => `${pascal(row.operation_ref)}Request = _OperationRequest${index}`);
    return artifact(`src/${root}/integrations/operation_requests.py`, `${imports.join("\n")}\nimport json as _json\n\n${aliases.join("\n")}\nOPERATION_REQUEST_TYPES = {${rows.map((row, index) => `${JSON.stringify(row.request_ref)}: _OperationRequest${index}`).join(", ")}}\nOPERATION_REQUEST_CONTRACTS = _json.loads(${JSON.stringify(canonicalJson(descriptors))})\n`);
  }
  const exports = rows.map(row => `pub use ${rustModule(operationModule(applicationView, row.operation_ref, language).relative_path)}::${pascal(row.operation_ref.split(":")[1]!)}Request as ${pascal(row.operation_ref)}Request;`);
  return artifact("src/integrations/operation_requests.rs", `${exports.join("\n")}\npub const OPERATION_REQUEST_CONTRACTS_JSON:&str=r###"${canonicalJson(descriptors)}"###;\n`);
}

export function typescriptRequestHandlerArtifact(applicationView: ProjectArtifactView, binding: Pick<ApplicationIntegrationBindingV1,'application_graph'> | Readonly<{application_graph:Pick<ApplicationIntegrationBindingV1['application_graph'],'operation_requests'|'runtime_bindings'>}>): PlannedArtifact {
  const relativePath = "src/integrations/application-request-handlers.ts";
  const requests = binding.application_graph.operation_requests;
  const modules = requests.map(request => {
    const module = operationModule(applicationView, request.operation_ref, "typescript");
    const callables = module.exports?.filter(item => item.kind === "value" && /^operation[A-Z]/.test(item.name)) ?? [];
    if (callables.length !== 1) fail("DS_WHOLE_APPLICATION_OPERATION_REQUEST", request.request_ref, "expected one exact Operation callable");
    return { operation_ref: request.operation_ref, relative_path: module.relative_path, callable: callables[0]!.name };
  });
  return artifact(relativePath, renderApplicationRequestHandlers(relativePath, requests, binding.application_graph.runtime_bindings, modules));
}

function runtimeMappingModules(applicationView: ProjectArtifactView, bindings: readonly RuntimeMappingBinding[]): readonly Readonly<{ selector: string; module: ApplicationModuleView }>[] {
  const modules = applicationModules(applicationView);
  return [...new Set(bindings.map(item => item.mapping_ref))].sort().map(selector => {
    const candidates = modules.filter(item =>
      (item.selector === selector || item.qualified_selectors?.includes(selector))
      && item.relative_path.includes("/mappings/")
      && !item.relative_path.includes("/_providers/")
      && !item.relative_path.includes(".provider."),
    );
    if (candidates.length !== 1) fail("DS_WHOLE_APPLICATION_RUNTIME_MAPPING", `/application_graph/runtime_bindings/${selector}`, `expected one generated Mapping module, received:${candidates.length}`);
    return freeze({ selector, module: candidates[0]! });
  });
}

function sourceArtifact(applicationView: ProjectArtifactView, module: ApplicationModuleView, pointer: string): PlannedArtifact {
  const source = applicationView.artifacts.find(item => item.relative_path === module.relative_path);
  if (!source) return fail("DS_WHOLE_APPLICATION_RUNTIME_MAPPING", pointer, `generated Mapping source is absent:${module.relative_path}`);
  return source;
}

export function typescriptRuntimeMappingArtifact(applicationView: ProjectArtifactView, bindings: readonly RuntimeMappingBinding[]): PlannedArtifact {
  const relativePath = "src/integrations/runtime-bindings.ts";
  const rows = runtimeMappingModules(applicationView, bindings).map((row, index) => {
    const callables = row.module.exports?.filter(item => item.kind === "value" && /^mapping[A-Z]/.test(item.name)).map(item => item.name) ?? [];
    if (callables.length !== 1) fail("DS_WHOLE_APPLICATION_RUNTIME_MAPPING", `/application_graph/runtime_bindings/${row.selector}`, `expected one exported TypeScript Mapping callable, received:${callables.length}`);
    return freeze({ ...row, alias: `mapping_${index}`, callable: callables[0]! });
  });
  const imports = rows.map(row => `import {${row.callable} as ${row.alias}} from ${JSON.stringify(outputImport(relativePath, row.module.relative_path).replace(/\.ts$/, ".js"))};`);
  const registry = rows.map(row => `${JSON.stringify(row.selector)}:${row.alias}`).join(",");
  const invokers = bindings.map(binding => {
    const row = rows.find(candidate => candidate.selector === binding.mapping_ref)!;
    return freeze({ binding, row, symbol: `invoke${pascal(binding.binding_id)}` });
  });
  const collision = invokers.find((item, index) => invokers.findIndex(candidate => candidate.symbol === item.symbol) !== index);
  if (collision) fail("DS_WHOLE_APPLICATION_RUNTIME_MAPPING", `/application_graph/runtime_bindings/${collision.binding.binding_id}`, `binding invocation symbol collision:${collision.symbol}`);
  const declarations = invokers.map(item => `export const ${item.symbol}=(parameters:Parameters<typeof ${item.row.alias}>[0]):ReturnType<typeof ${item.row.alias}>=>${item.row.alias}(parameters);`);
  const invocationRegistry = invokers.map(item => `${JSON.stringify(item.binding.binding_id)}:${item.symbol}`).join(",");
  const content = `${imports.join("\n")}\nexport const RUNTIME_MAPPINGS=Object.freeze({${registry}});\nexport type RuntimeMappingRef=keyof typeof RUNTIME_MAPPINGS;\n${declarations.join("\n")}\nexport const RUNTIME_MAPPING_INVOCATIONS=Object.freeze({${invocationRegistry}});\nexport type RuntimeMappingBindingRef=keyof typeof RUNTIME_MAPPING_INVOCATIONS;\nexport const RUNTIME_MAPPING_BINDINGS=${canonicalJson(bindings)} as const;\n`;
  return artifact(relativePath, content);
}

function pythonRuntimeMappingArtifact(applicationView: ProjectArtifactView, bindings: readonly RuntimeMappingBinding[]): PlannedArtifact {
  const root = pythonPackage(applicationView);
  const rows = runtimeMappingModules(applicationView, bindings).map((row, index) => {
    const source = sourceArtifact(applicationView, row.module, `/application_graph/runtime_bindings/${row.selector}`);
    const exported = /__all__\s*=\s*\[\s*["'](mapping_[a-z0-9_]+)["']\s*\]/.exec(source.content)?.[1];
    if (!exported) fail("DS_WHOLE_APPLICATION_RUNTIME_MAPPING", `/application_graph/runtime_bindings/${row.selector}`, "expected one exported Python Mapping callable");
    return freeze({ ...row, alias: `_mapping_${index}`, callable: exported });
  });
  const imports = rows.map(row => `from ${pythonModule(row.module.relative_path)} import ${row.callable} as ${row.alias}`);
  const registry = rows.map(row => `${JSON.stringify(row.selector)}: ${row.alias}`).join(", ");
  const invokers = bindings.map(binding => {
    const row = rows.find(candidate => candidate.selector === binding.mapping_ref)!;
    return freeze({ binding, row, symbol: `invoke_${snake(binding.binding_id)}` });
  });
  const collision = invokers.find((item, index) => invokers.findIndex(candidate => candidate.symbol === item.symbol) !== index);
  if (collision) fail("DS_WHOLE_APPLICATION_RUNTIME_MAPPING", `/application_graph/runtime_bindings/${collision.binding.binding_id}`, `binding invocation symbol collision:${collision.symbol}`);
  const declarations = invokers.map(item => `def ${item.symbol}(parameters):\n    return ${item.row.alias}(parameters)`);
  const invocationRegistry = invokers.map(item => `${JSON.stringify(item.binding.binding_id)}: ${item.symbol}`).join(", ");
  const content = `from types import MappingProxyType as _MappingProxyType\nimport json as _json\n${imports.join("\n")}\n\nRUNTIME_MAPPINGS = _MappingProxyType({${registry}})\n\n${declarations.join("\n\n")}\n\nRUNTIME_MAPPING_INVOCATIONS = _MappingProxyType({${invocationRegistry}})\nRUNTIME_MAPPING_BINDINGS = tuple(_json.loads(${JSON.stringify(canonicalJson(bindings))}))\n`;
  return artifact(`src/${root}/integrations/runtime_bindings.py`, content);
}

function rustString(value: string): string {
  return JSON.stringify(value);
}

function rustRuntimeMappingArtifact(applicationView: ProjectArtifactView, bindings: readonly RuntimeMappingBinding[]): PlannedArtifact {
  const rows = runtimeMappingModules(applicationView, bindings).map((row, index) => {
    const source = sourceArtifact(applicationView, row.module, `/application_graph/runtime_bindings/${row.selector}`);
    const callables = [...source.content.matchAll(/\bpub\s+fn\s+([a-z][a-z0-9_]*)\s*\(/g)].map(match => match[1]!);
    if (callables.length !== 1) fail("DS_WHOLE_APPLICATION_RUNTIME_MAPPING", `/application_graph/runtime_bindings/${row.selector}`, `expected one exported Rust Mapping callable, received:${callables.length}`);
    return freeze({ ...row, alias: `mapping_${index}`, callable: callables[0]! });
  });
  const exports = rows.map(row => `pub use ${rustModule(row.module.relative_path)}::${row.callable} as ${row.alias};`);
  const invokers = bindings.map(binding => {
    const row = rows.find(candidate => candidate.selector === binding.mapping_ref)!;
    return freeze({ binding, row, symbol: `invoke_${snake(binding.binding_id)}` });
  });
  const collision = invokers.find((item, index) => invokers.findIndex(candidate => candidate.symbol === item.symbol) !== index);
  if (collision) fail("DS_WHOLE_APPLICATION_RUNTIME_MAPPING", `/application_graph/runtime_bindings/${collision.binding.binding_id}`, `binding invocation symbol collision:${collision.symbol}`);
  const invocationExports = invokers.map(item => `pub use ${rustModule(item.row.module.relative_path)}::${item.row.callable} as ${item.symbol};`);
  const inputConstants: string[] = [];
  const bindingRows = bindings.map((binding, bindingIndex) => {
    const inputName = `RUNTIME_MAPPING_INPUTS_${bindingIndex}`;
    const invocation = invokers[bindingIndex]!;
    inputConstants.push(`const ${inputName}: &[RuntimeMappingInputBinding] = &[${binding.inputs.map(input => `RuntimeMappingInputBinding { parameter: ${rustString(input.parameter)}, value_type_json: ${rustString(canonicalJson(input.value_type))}, source_kind: ${rustString(input.source.kind)}, source_reference: ${rustString(input.source.reference)}, source_path: &[${input.source.path.map(rustString).join(",")}], }`).join(",")}];`);
    return `RuntimeMappingBinding { binding_id: ${rustString(binding.binding_id)}, invocation_symbol: ${rustString(invocation.symbol)}, mapping_ref: ${rustString(binding.mapping_ref)}, direction: ${rustString(binding.direction)}, source_ref: ${rustString(binding.source_ref)}, target_ref: ${rustString(binding.target_ref)}, inputs: ${inputName}, result_type_json: ${rustString(canonicalJson(binding.result_type))}, total: ${String(binding.total)}, source_pointer: ${rustString(binding.source_pointer)}, }`;
  });
  const content = `${exports.join("\n")}\n${invocationExports.join("\n")}\n\n#[derive(Clone, Copy, Debug, PartialEq, Eq)]\npub struct RuntimeMappingInputBinding {\n    pub parameter: &'static str,\n    pub value_type_json: &'static str,\n    pub source_kind: &'static str,\n    pub source_reference: &'static str,\n    pub source_path: &'static [&'static str],\n}\n\n#[derive(Clone, Copy, Debug, PartialEq, Eq)]\npub struct RuntimeMappingBinding {\n    pub binding_id: &'static str,\n    pub invocation_symbol: &'static str,\n    pub mapping_ref: &'static str,\n    pub direction: &'static str,\n    pub source_ref: &'static str,\n    pub target_ref: &'static str,\n    pub inputs: &'static [RuntimeMappingInputBinding],\n    pub result_type_json: &'static str,\n    pub total: bool,\n    pub source_pointer: &'static str,\n}\n\n${inputConstants.join("\n")}\npub const RUNTIME_MAPPING_BINDINGS: &[RuntimeMappingBinding] = &[${bindingRows.join(",")}];\n`;
  return artifact("src/integrations/runtime_bindings.rs", content);
}

function runtimeMappingArtifact(language: IntegrationGenerationLanguage, applicationView: ProjectArtifactView, binding: ApplicationIntegrationBindingV1): PlannedArtifact {
  const rows = binding.application_graph.runtime_bindings;
  if (rows.length === 0) fail("DS_WHOLE_APPLICATION_RUNTIME_MAPPING", "/application_graph/runtime_bindings", "whole application has no runtime Mapping bindings");
  return language === "typescript" ? typescriptRuntimeMappingArtifact(applicationView, rows) : language === "python" ? pythonRuntimeMappingArtifact(applicationView, rows) : rustRuntimeMappingArtifact(applicationView, rows);
}

function resolveImport(from: string, specifier: string, paths: ReadonlySet<string>): string | null {
  const joined = path.posix.normalize(path.posix.join(path.posix.dirname(from), specifier));
  const candidates = [joined, `${joined}.ts`, `${joined}/index.ts`, joined.endsWith(".js") ? `${joined.slice(0, -3)}.ts` : joined];
  return candidates.find(candidate => paths.has(candidate)) ?? null;
}

export function validateWholeApplicationImportClosureV1(artifacts: readonly PlannedArtifact[]): void {
  const paths = new Set(artifacts.map(item => item.relative_path));
  const expression = /(?:\bfrom\s+|\bimport\s*\(\s*)["'](\.[^"']+)["']/g;
  for (const item of artifacts.filter(row => row.relative_path.endsWith(".ts"))) {
    for (const match of item.content.matchAll(expression)) {
      const specifier = match[1]!;
      if (resolveImport(item.relative_path, specifier, paths) === null) fail("DS_WHOLE_APPLICATION_IMPORT", `/artifacts/${item.relative_path}`, `unresolved relative import:${specifier}`);
    }
  }
}

export function mergeWholeApplicationArtifactsV1(rows: readonly OwnedArtifact[]): Readonly<{
  artifacts: readonly PlannedArtifact[];
  path_owners: readonly WholeApplicationPathOwnerV1[];
}> {
  const owned = [...rows].sort((left, right) => left.artifact.relative_path.localeCompare(right.artifact.relative_path));
  const exact = new Map<string, OwnedArtifact>();
  const folded = new Map<string, string>();
  for (const row of owned) {
    safePath(row.artifact.relative_path, `/artifacts/${row.artifact.relative_path}`);
    const prior = exact.get(row.artifact.relative_path);
    if (prior) fail("DS_WHOLE_APPLICATION_COLLISION", `/artifacts/${row.artifact.relative_path}`, `path owned by both ${prior.owner} and ${row.owner}`);
    const foldedPath = row.artifact.relative_path.toLocaleLowerCase("en-US");
    const foldedPrior = folded.get(foldedPath);
    if (foldedPrior !== undefined) fail("DS_WHOLE_APPLICATION_CASE_COLLISION", `/artifacts/${row.artifact.relative_path}`, `case-folded collision with:${foldedPrior}`);
    exact.set(row.artifact.relative_path, row);
    folded.set(foldedPath, row.artifact.relative_path);
  }
  const artifacts = Object.freeze(owned.map(row => row.artifact));
  validateWholeApplicationImportClosureV1(artifacts);
  return freeze({ artifacts, path_owners: Object.freeze(owned.map(row => freeze({ relative_path: row.artifact.relative_path, owner: row.owner, sha256: row.artifact.sha256 }))) });
}

function reartifact(value: PlannedArtifact, relativePath: string, transform?: (content: string) => string): PlannedArtifact {
  return artifact(relativePath, transform ? transform(value.content) : value.content);
}

function pythonIntegrationArtifacts(applicationView: ProjectArtifactView, contribution: EmbeddedIntegrationContributionV1): readonly PlannedArtifact[] {
  const root = pythonPackage(applicationView);
  return Object.freeze(contribution.owned_artifacts.map(item => {
    const relativePath = item.relative_path.startsWith("src/") ? `src/${root}/${item.relative_path.slice(4)}` : item.relative_path;
    const rewrite = item.relative_path === "src/features/integration/application/contracts.py"
      ? (content: string) => `from ${root}.integrations.domain_bindings import ApplicationInput, ApplicationResult\n${content.replaceAll("Mapping[str, object]", "ApplicationInput").replaceAll("-> object", "-> ApplicationResult")}`
      : undefined;
    return reartifact(item, relativePath, rewrite);
  }));
}

function pythonIndexes(applicationView: ProjectArtifactView, artifacts: readonly PlannedArtifact[], bindingArtifact: PlannedArtifact): readonly PlannedArtifact[] {
  const root = pythonPackage(applicationView);
  const occupied = new Set([...applicationView.artifacts, ...artifacts, bindingArtifact].map(item => item.relative_path));
  const required = new Set<string>();
  for (const item of [...artifacts, bindingArtifact].filter(row => row.relative_path.startsWith(`src/${root}/`) && row.relative_path.endsWith(".py"))) {
    let directory = path.posix.dirname(item.relative_path);
    while (directory.startsWith(`src/${root}`)) {
      required.add(`${directory}/__init__.py`);
      if (directory === `src/${root}`) break;
      directory = path.posix.dirname(directory);
    }
  }
  return Object.freeze([...required].filter(relativePath => !occupied.has(relativePath)).sort().map(relativePath => artifact(relativePath, "")));
}

function mergedRustModule(relativePath: string, sources: readonly PlannedArtifact[], additions: readonly string[] = []): PlannedArtifact {
  const lines = [...sources.flatMap(item => item.content.split("\n")), ...additions].map(line => line.trim()).filter(Boolean);
  return artifact(relativePath, `${[...new Set(lines)].sort().join("\n")}\n`);
}

function ownedArtifacts(
  language: IntegrationGenerationLanguage,
  applicationView: ProjectArtifactView,
  contribution: EmbeddedIntegrationContributionV1,
  binding: ApplicationIntegrationBindingV1,
  projectId: string,
): readonly OwnedArtifact[] {
  const manifest = rootManifest(contribution, applicationView, projectId);
  const bindings = domainBindingArtifact(language, applicationView, binding);
  const runtimeBindings = runtimeMappingArtifact(language, applicationView, binding);
  const operationRequests = operationRequestArtifact(language, applicationView, binding.application_graph.operation_requests);
  const applicationGraph = applicationGraphArtifact(binding);
  if (language === "typescript") return Object.freeze([
    ...applicationView.artifacts.map(item => ({ artifact: item, owner: "reconciled-application" as const })),
    ...contribution.owned_artifacts.map(item => ({ artifact: item, owner: "embedded-integration" as const })),
    { artifact: manifest, owner: "whole-application-composer" as const },
    { artifact: nodeCryptoDeclaration(), owner: "whole-application-composer" as const },
    { artifact: bindings, owner: "whole-application-composer" as const },
    { artifact: runtimeBindings, owner: "whole-application-composer" as const },
    { artifact: operationRequests, owner: "whole-application-composer" as const },
    { artifact: typescriptRequestHandlerArtifact(applicationView, binding), owner: "whole-application-composer" as const },
    { artifact: applicationGraph, owner: "whole-application-composer" as const },
  ]);
  if (language === "python") {
    const projected = pythonIntegrationArtifacts(applicationView, contribution);
    const indexes = pythonIndexes(applicationView, projected, operationRequests);
    return Object.freeze([
      ...applicationView.artifacts.map(item => ({ artifact: item, owner: "reconciled-application" as const })),
      ...projected.map(item => ({ artifact: item, owner: "embedded-integration" as const })),
      { artifact: manifest, owner: "whole-application-composer" as const },
      { artifact: bindings, owner: "whole-application-composer" as const },
      { artifact: runtimeBindings, owner: "whole-application-composer" as const },
      { artifact: operationRequests, owner: "whole-application-composer" as const },
      { artifact: applicationGraph, owner: "whole-application-composer" as const },
      ...indexes.map(item => ({ artifact: item, owner: "whole-application-composer" as const })),
    ]);
  }
  const applicationStructural = new Set(["Cargo.toml", "src/lib.rs", "src/features/mod.rs"]);
  const integrationStructural = new Set(["src/lib.rs", "src/features/mod.rs", "src/integrations/mod.rs"]);
  const appByPath = new Map(applicationView.artifacts.map(item => [item.relative_path, item]));
  const integrationByPath = new Map(contribution.owned_artifacts.map(item => [item.relative_path, item]));
  const lib = mergedRustModule("src/lib.rs", [appByPath.get("src/lib.rs"), integrationByPath.get("src/lib.rs")].filter((item): item is PlannedArtifact => item !== undefined));
  const features = mergedRustModule("src/features/mod.rs", [appByPath.get("src/features/mod.rs"), integrationByPath.get("src/features/mod.rs")].filter((item): item is PlannedArtifact => item !== undefined));
  const integrations = mergedRustModule("src/integrations/mod.rs", [integrationByPath.get("src/integrations/mod.rs")].filter((item): item is PlannedArtifact => item !== undefined), ["pub mod domain_bindings;", "pub mod operation_requests;", "pub mod runtime_bindings;"]);
  return Object.freeze([
    ...applicationView.artifacts.filter(item => !applicationStructural.has(item.relative_path)).map(item => ({ artifact: item, owner: "reconciled-application" as const })),
    ...contribution.owned_artifacts.filter(item => !integrationStructural.has(item.relative_path)).map(item => ({ artifact: item, owner: "embedded-integration" as const })),
    ...[manifest, lib, features, integrations, bindings, runtimeBindings, operationRequests, applicationGraph].map(item => ({ artifact: item, owner: "whole-application-composer" as const })),
  ]);
}

function applicationLanguage(plan: SelectedReconciledProject): IntegrationGenerationLanguage {
  return isReconciledPythonProject(plan) ? "python" : isReconciledRustProject(plan) ? "rust" : "typescript";
}

export function assertWholeApplicationPlan(value: unknown): asserts value is WholeApplicationPlanV1 {
  if (value === null || typeof value !== "object" || plans.get(value as WholeApplicationPlanV1) !== sha256(canonicalJson(value))) {
    fail("DS_WHOLE_APPLICATION_SNAPSHOT", "/plan", "plan was not formed by the current process or has changed");
  }
}

export function composeWholeApplicationPlanV1(
  applicationPlan: SelectedReconciledProject,
  integrationContribution: EmbeddedIntegrationContributionV1,
  binding: ApplicationIntegrationBindingV1,
): WholeApplicationPlanV1 {
  const identity = selectedReconciledIdentity(applicationPlan);
  const applicationView: ProjectArtifactView = selectReconciledProjectArtifacts(applicationPlan);
  const language = applicationLanguage(applicationPlan);
  return composeCheckedWholeApplication(applicationPlan, applicationView, identity, language, integrationContribution, binding);
}

/** Explicit composed TypeScript entry point; never casts a v2 plan to v1. */
export function composeComposedWholeApplicationPlan(
  applicationPlan: ComposedReconciledProjectPlan,
  integrationContribution: EmbeddedIntegrationContributionV1,
  binding: ApplicationIntegrationBindingV1,
): WholeApplicationPlanV1 {
  const applicationView = selectComposedReconciledProjectArtifacts(applicationPlan);
  const resolved = applicationPlan.resolved;
  const identity = {project_id: resolved.certificate.project_id, resolved_plan_sha256: resolved.plan_sha256, source_manifest_sha256: resolved.semantic_sources.manifest_sha256};
  return composeCheckedWholeApplication(applicationPlan, applicationView, identity, "typescript", integrationContribution, binding);
}

function composeCheckedWholeApplication(
  applicationPlan: SelectedReconciledProject | ComposedReconciledProjectPlan,
  applicationView: ProjectArtifactView,
  identity: ReturnType<typeof selectedReconciledIdentity>,
  language: IntegrationGenerationLanguage,
  integrationContribution: EmbeddedIntegrationContributionV1,
  binding: ApplicationIntegrationBindingV1,
): WholeApplicationPlanV1 {
  assertEmbeddedIntegrationContribution(integrationContribution);
  assertApplicationIntegrationBinding(binding);
  if (language !== integrationContribution.language) fail("DS_WHOLE_APPLICATION_LANGUAGE", "/integration_contribution/language", "application and integration contribution languages differ");
  if (identity.source_manifest_sha256 !== binding.domain_source_manifest_sha256) fail("DS_WHOLE_APPLICATION_BINDING", "/binding/domain_source_manifest_sha256", "binding does not belong to the application plan");
  if (integrationContribution.source_sha256 !== binding.integration_source_sha256) fail("DS_WHOLE_APPLICATION_BINDING", "/binding/integration_source_sha256", "binding does not belong to the integration contribution");
  validateOperationRequestContracts(applicationPlan, binding.application_graph.operation_requests, binding.application_graph.runtime_bindings);
  const owned = ownedArtifacts(language, applicationView, integrationContribution, binding, identity.project_id);
  const merged = mergeWholeApplicationArtifactsV1(owned);
  const body = {
    schema_version: "domainspec.whole-application-plan/v1-candidate" as const,
    language,
    project_id: identity.project_id,
    domain_source_manifest_sha256: identity.source_manifest_sha256,
    integration_source_sha256: binding.integration_source_sha256,
    integration_semantic_manifest_sha256: binding.integration_semantic_manifest_sha256,
    selection_sha256: sha256(canonicalJson(applicationPlan.selection)),
    application_plan_sha256: applicationView.view_sha256,
    integration_plan_sha256: integrationContribution.standalone_plan_sha256,
    integration_contribution_sha256: integrationContribution.contribution_sha256,
    binding_sha256: binding.binding_sha256,
    application_graph_sha256: binding.application_graph.graph_sha256,
    artifacts: merged.artifacts,
    path_owners: merged.path_owners,
    native_type_dependencies: Object.freeze(language === "typescript" ? ["node:crypto"] : []),
    runtime_guarantees_observed: false as const,
    claim_ceiling: "formation-and-static-compilation-only" as const,
    authority_effect: "none" as const,
  };
  const result = freeze({ ...body, plan_sha256: sha256(canonicalJson(body)) });
  plans.set(result, sha256(canonicalJson(result)));
  return result;
}

export function planWholeApplicationV1(projectRoot: string, selection: SelectedReconciledCompilation, integrationSource: IntegrationGenerationSourceV2): WholeApplicationPlanV1 {
  const graph = loadCompiledProjectGraph(projectRoot);
  const binding = validateApplicationIntegrationBinding(graph, integrationSource);
  const application = planCompiledSelectedReconciledProject(graph, selection);
  const integration = planEmbeddedIntegrationContributionV1(integrationSource, selection.language);
  return composeWholeApplicationPlanV1(application, integration, binding);
}

export function planComposedWholeApplication(projectRoot: string, selection: ComposedReconciledCompilationSelection, integrationSource: IntegrationGenerationSourceV2): WholeApplicationPlanV1 {
  const graph = loadCompiledProjectGraph(projectRoot);
  const application = planCompiledComposedReconciledProject(graph, selection);
  const binding = validateApplicationIntegrationBinding(graph, integrationSource);
  const integration = planEmbeddedIntegrationContributionV1(integrationSource, "typescript");
  return composeComposedWholeApplicationPlan(application, integration, binding);
}
