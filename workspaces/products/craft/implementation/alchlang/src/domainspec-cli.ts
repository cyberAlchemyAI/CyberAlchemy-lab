import type {U0RuntimeBridgeV4} from './u0-runtime-bridge.js';
import type {BusinessApplicationInput} from './business-application-protocol.js';
import { createHash } from "node:crypto";
import { existsSync, readFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

export const DOMAINSPEC_PACKAGE = "@domainspec-v2/cli" as const;
export const DOMAINSPEC_VERSION = "1.3.0" as const;

// These are the fields consumed by AlchLang's projection, not a second graph schema.
export interface DomainSpecGraph {
  project_root: string;
  project_id: string;
  nodes: Array<{ selector: string; kind: string; meta_type_id: string; body: unknown }>;
  relationships: Array<{ edge_id: string; relationship: string; source: { feature_id: string; node_id: string }; target: { feature_id: string; node_id: string } }>;
  source_manifest: { manifest_sha256: string; sources?: readonly { relative_path: string; sha256: string; size_bytes: number }[] };
  authority_effect: "none";
}
export interface DomainSpecIo { stdout(value: string): void; stderr(value: string): void }
export interface DomainSpecCompiler {
  profileEngine:{
    captureGenericNativeProfileArtifact?(directory:string):any;
    inspectGenericNativeProfileArtifact?(artifact:any):any;
    createTechnicalProfileCompositionOwner?(options:any):any;
    createTechnicalErrorPresentationApplicationOwner?(options:any):any;
    createGenericErrorPresentationBinding?(options:any):any;
    inspectGenericErrorPresentation?(binding:any):any;
    createGenericHttpCompositionOwner?():any;
    createTechnicalProfileServiceArchitectureOwner?(options:any):any;
    resolveTechnicalApplicationInputRoles?(options:any):any;
    validateTechnicalApplicationInputs?(value:unknown,contract:any):any;
    createTechnicalBusinessBindingOwner?(owner:any,handle:any):any;
    createTechnicalProfileSourceOwner?():{prepare(input:{sourceRoot:string;manifestPath:string}):any;prepareCompiled(artifactPath:string):any;inspect(handle:any):any;inspectErrorPresentation(handle:any):any;publishSelection(handle:any,output:string):any;publishArchitecture(handle:any,repositoryRoot:string,output:string):any;dispose(handle:any):void};
    createBusinessU0RuntimeV4?(options?:{readonly frontend_root?:string}):Promise<U0RuntimeBridgeV4>;
    publishBusinessAuthoringDirectory?(target:string,files:readonly {relative_path:string;content:string}[],prefix:string,validate:(stage:string)=>void):unknown;
    validateProfileProject(input:unknown):any;
    validateProfileProjectInput(input:unknown):any;
    loadProfileProjectV2(project:string,identity:{engine:readonly {key:string;path:string}[];tools:readonly {key:string;path:string}[];additionalSources?:readonly {key:string;path:string}[]},lock?:unknown):any;
    prepareBusinessInputV2(snapshot:any):BusinessApplicationInput;
    assertBusinessInputV2Current(input:BusinessApplicationInput):void;
    prepareAuthoringBusinessInput?(accepted:unknown,requests:unknown,compatibility:unknown):BusinessApplicationInput;
    assertAuthoringBusinessInputCurrent?(input:BusinessApplicationInput):void;
    dataDigest(input:unknown):string;
    captureJson(input:unknown):any;
    prepareApplicationCallable(graph:unknown,whole:unknown,binding:unknown,intent:any,assertCurrent:()=>void):any;
    loadProfileProject(project:string,identity:{engine:readonly {key:string;path:string}[];tools:readonly {key:string;path:string}[];additionalSources?:readonly {key:string;path:string}[]},lock?:unknown):any;
    selectProfileConfiguration(snapshot:any):any;
    profileTechnicalSelections(selection:any):readonly any[];
    profileApplicationSelections(selection:any):readonly {intent_id:string;route:string;request_bytes:number;timeout_ms:number}[];
    compileRequestApplicationBindingV1(graph:unknown,source:unknown,plan:unknown):any;
    composeRequestApplicationPlanV1(plan:unknown,binding:unknown):any;
    prepareRequestApplicationCallable(graph:unknown,plan:unknown,binding:unknown,intent:unknown,lineage:unknown,assertCurrent:()=>void):any;
    assertBusinessApplicationPlanCurrent(graph:unknown,plan:unknown):void;
    assertProfileBusinessInputCurrent(input:any):void;
    composeProfile(selection:any,functions:readonly any[],applications?:readonly any[]):any;
    assertCheckedCompositionCurrent(composition:any):void;
    renderProfilePlan(composition:any):Readonly<Record<string,string>>;
    projectProfileViews(composition:any):any;
    compileProfileDomainFiles(snapshot:any,files:Readonly<Record<string,string>>,compiler:string):Readonly<Record<string,string>>;
    qualifyNativeFiles(snapshot:any,files:Readonly<Record<string,string>>,compiler:string):any;
    completeProfileOutput(snapshot:any,files:Readonly<Record<string,string>>,qualification:any,target:string):any;
    verifyProfileOutput(snapshot:any,target:string,files:Readonly<Record<string,string>>):any;
  };
  planCompiledProjectBuild(graph:unknown,language:"typescript",realization:string,layout:string):{artifacts:readonly {relative_path:string;content:string;sha256:string;size_bytes:number}[];receipt:Record<string,unknown>};
  checkComputationContract(value: unknown): any;
  bindComputationSource(value: unknown, options: any): any;
  unwrapComputationSource(value: unknown): any;
  evaluateComputationJson(checked: any, input: string): {ok: boolean; [key: string]: unknown};
  buildComputationArtifacts(value: unknown, source: any, output: string): any;
  verifyComputationArtifacts(value: unknown, source: any, output: string): any;
  composeApplicationArtifacts(plan: any, source: unknown, binding: unknown): { language: "typescript" | "python" | "rust"; artifacts: readonly { relative_path: string; content: string; sha256: string; size_bytes: number }[]; plan_sha256: string; runtime_guarantees_observed: false; authority_effect: "none" };
  composeProviderApplicationArtifacts(whole: unknown, selection: unknown, source: unknown, route?: Readonly<{ method: "POST"; path: string }>): { language: "typescript" | "python" | "rust"; artifacts: readonly { relative_path: string; content: string; sha256: string; size_bytes: number }[]; plan_sha256: string; whole_application_plan_sha256: string; provider_selection_sha256: string; runtime_guarantees_observed: false; authority_effect: "none" };
  compileApplicationRuntimeBinding(graph: DomainSpecGraph, source: unknown, providers: unknown, selection: unknown): any;
  compileProviderRuntimeProfile(input: unknown, requirements: unknown): { selection: { language: "typescript" | "python" | "rust"; [key: string]: unknown }; requirements: Record<string, string>; selection_sha256: string; requirements_sha256: string; runtime_guarantees_observed: false; authority_effect: "none" };
  compileExternalApiRuntimeBindings(graph: DomainSpecGraph, input: unknown, selection: unknown): any;
  compileExternalApiComposition(input: unknown): any;
  compileMessagingRuntimeBindings(graph: DomainSpecGraph, input: unknown, selection: unknown): any;
  compileMessagingComposition(input: unknown): any;
  compilePersistenceComposition(input: unknown): any;
  integrationDefinitionPackSha256: string;
  decodeReconciledCompilationSelection(input: unknown): any;
  planApplicationRealization(graph: DomainSpecGraph, selection: unknown): { plan: any; view: { artifacts: readonly { relative_path: string; content: string; sha256: string; size_bytes: number }[]; [key: string]: unknown } };
  compileFormalConditionBindings(graph: DomainSpecGraph, input: unknown, sources: ReadonlyMap<string, Buffer>): unknown;
  loadApplicationOntology(input:unknown,root:string):any;
  checkApplicationOntology(input:unknown,root:string):any;
  buildApplicationOntology(input:unknown,root:string,output:string):any;
  compileRequestCustody(value:unknown):{contract:any;trace:any};
  compileStreamLifecycle(value:unknown):{contract:any;trace:any};
  compileOutboundComposition(value:unknown):{contract:any;output:any;trace:any};
  normalizeCompositionOntology(value: unknown): Record<string, unknown>;
  compileEventBindings(value: unknown, language: "typescript" | "rust"): { manifest: unknown; source: string };
  supportsExactUInt64: boolean;
  applicationPaths: Readonly<Record<string,string>>;
  outputImport(from:string,to:string):string;
  applicationLayoutId: string;
  compileDeclarativeFunction(value:unknown):{source:string;contract:unknown;trace:unknown};
  binding: { package: typeof DOMAINSPEC_PACKAGE; version: typeof DOMAINSPEC_VERSION; package_root: string; package_sha256: string; entry_sha256: string };
  compileProject(sourceRoot: string): { graph: DomainSpecGraph; certificate: { compiler: { package: string; version: string }; authority_effect: "none" } };
  runCli(args: readonly string[], io?: DomainSpecIo): number;
}

export function findDomainSpecPackageRoot(entryPath:string):string|undefined {
  let current=path.dirname(path.resolve(entryPath));
  for(;;){
    const manifestPath=path.join(current,'package.json');
    if(existsSync(manifestPath)){
      try{if(JSON.parse(readFileSync(manifestPath,'utf8')).name===DOMAINSPEC_PACKAGE)return current;}catch{}
    }
    const parent=path.dirname(current);if(parent===current)return undefined;current=parent;
  }
}

export function defaultDomainSpecPackageRoot(): string {
  if(process.env.ALCHLANG_DOMAINSPEC_PACKAGE_ROOT)return path.resolve(process.env.ALCHLANG_DOMAINSPEC_PACKAGE_ROOT);
  try{
    const installed=findDomainSpecPackageRoot(fileURLToPath(import.meta.resolve(DOMAINSPEC_PACKAGE)));
    if(installed)return installed;
  }catch{}
  const frontendManifest=JSON.parse(readFileSync(new URL('../package.json',import.meta.url),'utf8'));
  if(frontendManifest.name==='@cyberalchemy/alchlang')throw new Error('DOMAINSPEC_INSTALLED_PEER_REQUIRED: install the matching @domainspec-v2/cli peer or explicitly select ALCHLANG_DOMAINSPEC_PACKAGE_ROOT');
  const checkout = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../../../../../../..");
  return resolveDomainSpecPackageRoot(checkout);
}

/** Resolve the repository-owned Craft compiler; other layouts require an explicit binding. */
export function resolveDomainSpecPackageRoot(checkout: string, explicitRoot?: string): string {
  if (explicitRoot) return path.resolve(explicitRoot);
  const craftRoot = path.join(path.resolve(checkout), "craft/projects/domainspec-v2/impl/cli");
  if (!existsSync(path.join(craftRoot, "package.json"))) {
    throw new Error("DOMAINSPEC_PACKAGE_MISSING: expected the Craft compiler or set ALCHLANG_DOMAINSPEC_PACKAGE_ROOT");
  }
  return craftRoot;
}

export async function loadDomainSpecCompiler(packageRoot = defaultDomainSpecPackageRoot()): Promise<DomainSpecCompiler> {
  const root = path.resolve(packageRoot);
  const packageBytes = readFileSync(path.join(root, "package.json"));
  const manifest = JSON.parse(packageBytes.toString("utf8"));
  if (manifest.name !== DOMAINSPEC_PACKAGE || manifest.version !== DOMAINSPEC_VERSION) {
    throw new Error(`DOMAINSPEC_VERSION_MISMATCH: expected ${DOMAINSPEC_PACKAGE}@${DOMAINSPEC_VERSION}; got ${manifest.name}@${manifest.version}`);
  }
  const entry = manifest.exports?.["."]?.import;
  if (typeof entry !== "string" || !entry.startsWith("./") || path.relative(root, path.resolve(root, entry)).startsWith("..")) {
    throw new Error("DOMAINSPEC_PUBLIC_ENTRY_REQUIRED: package must export its public ESM entry");
  }
  const entryPath = path.resolve(root, entry);
  let entryBytes: Buffer;
  try { entryBytes = readFileSync(entryPath); }
  catch { throw new Error(`DOMAINSPEC_BUILD_REQUIRED: build ${root} before using AlchLang`); }
  const api = await import(pathToFileURL(entryPath).href);
  if (api.CLI_PACKAGE_NAME !== DOMAINSPEC_PACKAGE || api.CLI_VERSION !== DOMAINSPEC_VERSION || typeof api.compileProject !== "function" || typeof api.runCli !== "function") {
    throw new Error(`DOMAINSPEC_BUILD_MISMATCH: rebuild ${DOMAINSPEC_PACKAGE}@${DOMAINSPEC_VERSION}; manifest and built public API disagree`);
  }
  let version = "";
  const versionCode = api.runCli(["--version"], { stdout(value: string) { version += value; }, stderr() {} });
  if (versionCode !== 0 || version.trim() !== DOMAINSPEC_VERSION) throw new Error("DOMAINSPEC_BUILD_MISMATCH: CLI version does not match public API");
  const sha256 = (bytes: Buffer) => createHash("sha256").update(bytes).digest("hex");
  const requireLayout=()=>{if(api.APPLICATION_LAYOUT?.id!=="domainspec.application-layout/v1" || !api.APPLICATION_PATHS || typeof api.outputImport!=="function")throw Error("DOMAINSPEC_APPLICATION_LAYOUT_BUILD_REQUIRED");};
  const decodeExecutionSelection=(input:unknown)=>{
    const version=input&&typeof input==='object'?Object.getOwnPropertyDescriptor(input,'schema_version'):undefined;
    const decode=version?.value==='domainspec.reconciled-compilation/v2-candidate'?api.decodeComposedReconciledCompilationSelection:api.decodeSelectedReconciledCompilation;
    if(typeof decode!=='function')throw Error('DOMAINSPEC_REALIZATION_BUILD_REQUIRED');
    return decode(input);
  };
  const computationApi = (name: string) => {if (typeof api[name] !== "function") throw Error("DOMAINSPEC_COMPUTATION_BUILD_REQUIRED:" + name); return api[name];};
  return {
    profileEngine:api.profileEngine,
    planCompiledProjectBuild(graph,language,realization,layout){if(typeof api.planCompiledProjectBuild!=="function")throw Error("DOMAINSPEC_BUILD_PLAN_REQUIRED");return api.planCompiledProjectBuild(graph,language,realization,layout);},
    bindComputationSource(value, options) {return computationApi("bindComputationSource")(value, options);},
    unwrapComputationSource(value) {return computationApi("unwrapComputationSource")(value);},
    checkComputationContract(value) {return computationApi("checkComputationContract")(value);},
    evaluateComputationJson(checked, input) {return computationApi("evaluateComputationJson")(checked, input);},
    buildComputationArtifacts(value, source, output) {return computationApi("buildComputationArtifacts")(value, source, output);},
    verifyComputationArtifacts(value, source, output) {return computationApi("verifyComputationArtifacts")(value, source, output);},
    composeApplicationArtifacts(plan, source, binding) {
      if (typeof api.assertSelectedReconciledProject !== "function" || typeof api.planEmbeddedIntegrationContributionV1 !== "function") throw Error("DOMAINSPEC_WHOLE_APPLICATION_BUILD_REQUIRED");
      const compose = plan.selection.schema_version === "domainspec.reconciled-compilation/v2-candidate"
        ? api.composeComposedWholeApplicationPlan : api.composeWholeApplicationPlanV1;
      if (typeof compose !== "function") throw Error("DOMAINSPEC_WHOLE_APPLICATION_BUILD_REQUIRED");
      if (plan.selection.schema_version === "domainspec.reconciled-compilation/v2-candidate") api.assertReconciledProjectPlan(plan);
      else api.assertSelectedReconciledProject(plan);
      const contribution = api.planEmbeddedIntegrationContributionV1(source, plan.selection.language);
      return compose(plan, contribution, binding);
    },
    composeProviderApplicationArtifacts(whole, selection, source, route) {
      if (typeof api.composeProviderApplicationV1 !== "function") throw Error("DOMAINSPEC_PROVIDER_APPLICATION_BUILD_REQUIRED");
      return api.composeProviderApplicationV1(whole, selection, source, route);
    },
    compileApplicationRuntimeBinding(graph, source, providers, selection) {
      if (typeof api.compileApplicationRuntimeBindingV1 !== "function") throw Error("DOMAINSPEC_APPLICATION_RUNTIME_BUILD_REQUIRED");
      const result = api.compileApplicationRuntimeBindingV1(graph, source, providers);
      const executable = decodeExecutionSelection(selection);
      if (executable.language !== result.language) throw Error("DOMAINSPEC_APPLICATION_RUNTIME_TARGET");
      api.validateOperationRequestContracts({ selection: executable }, result.binding.application_graph.operation_requests, result.binding.application_graph.runtime_bindings);
      return result;
    },
    compileProviderRuntimeProfile(input, requirements) {
      if (typeof api.resolveProviderRuntimeProfileV1 !== "function") throw Error("DOMAINSPEC_RUNTIME_PROFILE_BUILD_REQUIRED");
      return api.resolveProviderRuntimeProfileV1(input, requirements);
    },
    compileExternalApiRuntimeBindings(graph, input, selection) {
      if (typeof api.compileExternalApiRuntimeBindingsV1 !== "function" || typeof api.validateOperationRequestContracts !== "function") throw Error("DOMAINSPEC_EXTERNAL_API_JOIN_BUILD_REQUIRED");
      const joined = api.compileExternalApiRuntimeBindingsV1(graph, input);
      api.validateOperationRequestContracts({ selection: decodeExecutionSelection(selection) }, joined.operation_requests, joined.runtime_bindings);
      return joined;
    },
    compileExternalApiComposition(input) {
      if (typeof api.compileExternalApiCompositionV2 !== "function") throw Error("DOMAINSPEC_EXTERNAL_API_BUILD_REQUIRED");
      return api.compileExternalApiCompositionV2(input);
    },
    compileMessagingRuntimeBindings(graph, input, selection) {
      if (typeof api.compileMessagingRuntimeBindingsV1 !== "function" || typeof api.validateOperationRequestContracts !== "function") throw Error("DOMAINSPEC_MESSAGING_JOIN_BUILD_REQUIRED");
      const joined = api.compileMessagingRuntimeBindingsV1(graph, input);
      api.validateOperationRequestContracts({ selection: decodeExecutionSelection(selection) }, joined.operation_requests, joined.runtime_bindings);
      return joined;
    },
    compileMessagingComposition(input) {
      if (typeof api.compileMessagingCompositionV2 !== "function") throw Error("DOMAINSPEC_MESSAGING_BUILD_REQUIRED");
      return api.compileMessagingCompositionV2(input);
    },
    compilePersistenceComposition(input) {
      if (typeof api.compilePersistenceCompositionV2 !== "function") throw Error("DOMAINSPEC_PERSISTENCE_BUILD_REQUIRED");
      return api.compilePersistenceCompositionV2(input);
    },
    get integrationDefinitionPackSha256() {
      if (typeof api.SYSTEM_INTEGRATION_DEFINITION_PACK_SHA256 !== "string") throw Error("DOMAINSPEC_INTEGRATION_DEFINITION_BUILD_REQUIRED");
      return api.SYSTEM_INTEGRATION_DEFINITION_PACK_SHA256;
    },
    decodeReconciledCompilationSelection(input) {
      return decodeExecutionSelection(input);
    },
    planApplicationRealization(graph, selection) {
      if (typeof api.planCompiledSelectedReconciledProject !== "function" || typeof api.selectSelectedReconciledArtifacts !== "function") throw Error("DOMAINSPEC_REALIZATION_BUILD_REQUIRED");
      const decoded=decodeExecutionSelection(selection);
      const generate=decoded.schema_version==='domainspec.reconciled-compilation/v2-candidate'?api.planCompiledComposedReconciledProject:api.planCompiledSelectedReconciledProject;
      if(typeof generate!=='function')throw Error('DOMAINSPEC_REALIZATION_BUILD_REQUIRED');
      const plan = generate(graph, decoded);
      const select=decoded.schema_version==='domainspec.reconciled-compilation/v2-candidate'?api.selectReconciledArtifacts:api.selectSelectedReconciledArtifacts;
      if(typeof select!=='function')throw Error('DOMAINSPEC_REALIZATION_BUILD_REQUIRED');
      return { plan, view: select(plan) };
    },
    compileFormalConditionBindings(graph, input, sources) {
      if (typeof api.compileFormalConditionBindings !== "function") throw Error("DOMAINSPEC_FORMAL_BINDING_BUILD_REQUIRED");
      return api.compileFormalConditionBindings(graph, input, sources);
    },
    loadApplicationOntology(input,root){if(typeof api.loadApplicationOntology!=="function")throw Error("DOMAINSPEC_APPLICATION_BUILD_REQUIRED");return api.loadApplicationOntology(input,root);},
    checkApplicationOntology(input,root){if(typeof api.checkApplicationOntology!=="function")throw Error("DOMAINSPEC_APPLICATION_BUILD_REQUIRED");return api.checkApplicationOntology(input,root);},
    buildApplicationOntology(input,root,output){if(typeof api.buildApplicationOntology!=="function")throw Error("DOMAINSPEC_APPLICATION_BUILD_REQUIRED");return api.buildApplicationOntology(input,root,output);},
    compileRequestCustody(value) {if(typeof api.compileRequestCustody!=="function")throw Error("DOMAINSPEC_CUSTODY_BUILD_REQUIRED");return api.compileRequestCustody(value);},
    compileStreamLifecycle(value) {if(typeof api.compileStreamLifecycle!=="function")throw Error("DOMAINSPEC_STREAM_BUILD_REQUIRED");return api.compileStreamLifecycle(value);},
    compileOutboundComposition(value) {
      if(typeof api.compileOutboundComposition!=="function")throw Error("DOMAINSPEC_OUTBOUND_BUILD_REQUIRED");
      return api.compileOutboundComposition(value);
    },
    normalizeCompositionOntology(value) {
      if (api.COMPOSITION_ONTOLOGY_SCHEMA !== "domainspec.composition-ontology/v1" || typeof api.normalizeCompositionOntology !== "function") throw Error("DOMAINSPEC_COMPOSITION_ONTOLOGY_BUILD_REQUIRED");
      return api.normalizeCompositionOntology(value);
    },
    compileEventBindings(value, language) {
      if (typeof api.compileSystemIntegrationManifest !== "function" || typeof api.renderSystemIntegrationContract !== "function") throw Error("DOMAINSPEC_MESSAGE_BUILD_REQUIRED");
      const manifest = api.compileSystemIntegrationManifest(value, language);
      return { manifest, source: api.renderSystemIntegrationContract(manifest) };
    },
    get applicationPaths() {
      if(api.APPLICATION_LAYOUT?.id!=="domainspec.application-layout/v1" || !api.APPLICATION_PATHS || typeof api.outputImport!=="function")throw Error("DOMAINSPEC_APPLICATION_LAYOUT_BUILD_REQUIRED");
      return api.APPLICATION_PATHS;
    },
    get applicationLayoutId(){requireLayout();return api.APPLICATION_LAYOUT.id;},
    outputImport(from,to){requireLayout();return api.outputImport(from,to);},
    supportsExactUInt64: api.EXACT_UINT64_PROFILE === "domainspec.typescript-exact-uint64/v1",
    compileDeclarativeFunction(value) {
      if(api.DECLARATIVE_FUNCTION_PROFILE!=="domainspec.declarative-function/v1"||typeof api.compileDeclarativeFunction!=="function")throw Error("DOMAINSPEC_DECLARATIVE_BUILD_REQUIRED");
      return api.compileDeclarativeFunction(value);
    },
    binding: { package: DOMAINSPEC_PACKAGE, version: DOMAINSPEC_VERSION, package_root: root, package_sha256: sha256(packageBytes), entry_sha256: sha256(entryBytes) },
    compileProject(sourceRoot) {
      const result = api.compileProject(path.resolve(sourceRoot));
      if (result.certificate?.compiler?.package !== DOMAINSPEC_PACKAGE || result.certificate?.compiler?.version !== DOMAINSPEC_VERSION || result.certificate?.authority_effect !== "none" || result.graph?.authority_effect !== "none") {
        throw new Error("DOMAINSPEC_CERTIFICATE_MISMATCH: compilation is not bound to the selected compiler");
      }
      return result;
    },
    runCli(args, io) { return api.runCli(args, io); },
  };
}

// Deliberately excludes experimental execution, source authoring and deployment recipes.
const COMPILER_COMMANDS = new Set(["application-check", "application-build", "--version", "--help", "capabilities", "doctor", "lint", "receipt", "compile", "build", "verify", "instantiate", "instantiate-project", "verify-project", "formalize", "formalize-check", "certify", "certify-check"]);
export async function runDomainSpecCli(args: readonly string[], io?: DomainSpecIo, packageRoot?: string): Promise<number> {
  const command = args[0] ?? "--help";
  if (!COMPILER_COMMANDS.has(command)) throw new Error(`DOMAINSPEC_COMMAND_UNSUPPORTED:${command}`);
  const compiler = await loadDomainSpecCompiler(packageRoot);
  return compiler.runCli(args.length ? args : ["--help"], io);
}
