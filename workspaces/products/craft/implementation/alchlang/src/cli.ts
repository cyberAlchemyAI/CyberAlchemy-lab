#!/usr/bin/env node
import {runBusinessAuthoringCommand} from './business-authoring-project.js';
import {runProfileProjectCommand} from './profile-engine.js';
import {runAlchComputationCommand} from './commands/computation.js';
import {buildCustody,checkCustody} from './custody-builder.js';
import {checkApplication,buildApplication} from "./application-contract.js";
import {buildStream,checkStream} from './stream-builder.js';
import {buildOutbound,checkOutbound} from './outbound-composition.js';
import {buildQueryIteration,checkQueryIteration} from './query-iteration.js';
import {buildEventProfile, compileEventProfile} from "./event-profile.js";
import {traceFunction} from "./trace-command.js";
import {checkFunction, buildFunction, inspectFunctionOntology} from "./function-builder.js";
import { DOMAINSPEC_PROFILE, EXACT_PROFILE } from "./domainspec-profile.js";
import { buildDomainSpec, checkDomainSpec } from "./domainspec-project-writer.js";
import { runDomainSpecCli } from "./domainspec-cli.js";
import { readFileSync } from "node:fs";
import path from "node:path";
import { MemoryActionAdapter } from "./adapters.js";
import { SqliteTransactionalOutboxActionAdapter } from "./effect-adapters.js";
import { compileCarrier } from "./index.js";
import { loadAlchLangSource } from "./source-file.js";
import { executeAction } from "./runtime.js";
import { validateAtomicStateAndOutboxRequest } from "./sqlite-outbox-runtime.js";
import { DurableOutboxWorker, DurableSqliteTransactionalOutbox, type DurableOutboxRecord, type DurableOutboxTransport, type DurableOutboxStatus } from "./durable-outbox-runtime.js";
import { FetchOutboxHttpClient, HttpOutboxTransport } from "./outbox-integrations.js";
import { writeCompilation } from "./writer.js";
import { listOperationPatterns, requireGeneratablePattern } from "./pattern-registry.js";
import { writeRegistryCompilation } from "./registry-compiler.js";
import { buildService, compileService } from "./service-builder.js";
import {buildSemanticContract,checkSemanticContract,compileSemanticContract} from './semantic-contract.js';
import {buildModuleConfiguration,checkModuleConfiguration,compileModuleConfiguration} from './module-configuration.js';
import {runCli, requireOptionalFeature} from './optional-features.js';
import {selectAlchSourceProfile} from './profile-architecture.js';
import {qualifyBehavioralClaim, type BehavioralClaim} from './behavioral-qualification.js';
import {checkFormalClaimSourceIntake,rejectFormalClaimFormationRequest} from './formal-claim-source-intake.js';

function option(args: string[], name: string): string | undefined { const index = args.indexOf(name); return index === -1 ? undefined : args[index + 1]; }
function positiveInteger(value: string | undefined, fallback: number): number {
  if (value === undefined) return fallback;
  const parsed = Number(value);
  if (!Number.isSafeInteger(parsed) || parsed < 1) throw new Error(`INVALID_POSITIVE_INTEGER:${value}`);
  return parsed;
}
function usage(exitCode = 2): never {
  const print = exitCode === 0 ? console.log : console.error;
  print('Business authoring: alchlang business --help');
  print('Profile source: alchlang profile check-source|compile-source <source.profile.json> [--source-root <directory>] [--out <new-directory>]\n  alchlang profile generate-source <selection.json> [--children <catalog.json>] [--native-artifacts <catalog.json>] [--business <business.alch> --business-profile <profile.json> --http-profile <http.json>] [--implementation-root <directory>] --out <new-directory>\nProfile projects:\n  alchlang profile select|check|plan|generate|view|verify <project.json> [--lock <lock.json>] [--out <directory>]\n  Native checked generation; claims remain unproved. Local hosting, TDE, EVF and publication deferred.');
  print("Pure computation:\n  alchlang computation check|build|verify|run <absolute-source.alch> [--out <absolute-directory>] [--input <absolute-json>] [--entry <declaredCalculation>]");
  print("FormalClaim formation:\n  alchlang check-formal-claim < request.json (exact claim_ref, root_directory, selected_profile)");
  print("Application profile:\n  alchlang check <application.alch> [--application-bindings <relative-file>] [--entry <id>]\n  alchlang build|verify <application.alch> --out <directory> [--application-bindings <relative-file>] [--entry <id>]");
  print("Behavioral qualification:\n  alchlang qualify <source.alch> --claim closed-state-model|executable-runtime");
  print("Usage:\n  alchlang check|build <service.alch> [--out <new-directory>]\n  alchlang check|ontology <semantic-contract.alch>\n  alchlang build <semantic-contract.alch> --out <new-directory>\n  alchlang conformance <file.alch> --fixtures <file.json> --out <new-directory>\n  alchlang trace <file.alch> --input <input.json>\n  alchlang ontology <file.alch>\n  alchlang explain <file.alch> <declaration>\n  alchlang check <domain.alch> --profile domainspec-1.0.0 [--bindings file]\n  alchlang emit-domainspec <domain.alch> --out <new-directory> [--bindings file]\n  alchlang build <domain.alch> --backend domainspec --language typescript --out <new-directory> [--bindings file]\n  alchlang domainspec <compiler-command> [arguments]\n  domainspec check <domain.alch> --backend local-compat\n  domainspec build <domain.alch> --backend local-compat [--out generated] [--force]\n  domainspec run <domain.alch> <action> --actor <actor> --facts '<json>' --grant <boundary> --adapter memory\n  domainspec run <domain.alch> <action> --actor <actor> --facts '<json>' --grant <boundary> --binding sqlite-transactional-outbox --database <path> --effect-request-file <json>\n  domainspec outbox pending|status --database <path> [--status pending|leased|published|dead]\n  domainspec outbox dispatch --database <path> --transport stdout --worker-id <id> [--now <ISO>]\n  domainspec outbox dispatch --database <path> --transport http --worker-id <id> --endpoint <url> --allow-origin <origin> --confirm-network-dispatch <origin>\n  domainspec outbox requeue-dead --database <path> --message-id <id> --now <ISO>\n  domainspec registry build --config <registry-compiler.config.json>\n  domainspec patterns [--available|--blocked]\n  domainspec pattern <pattern-id>\n\nCanonical source files use .alch. A fenced .md file is supported only for legacy compatibility.");
  process.exit(exitCode);
}

export async function main(): Promise<void> {
  const [, , command, ...args] = process.argv;
  if(command==='business'){process.exitCode=await runBusinessAuthoringCommand(args,{stdout:value=>console.log(value),stderr:value=>console.error(value)});return;}
  if(command==='profile'){process.exitCode=await runProfileProjectCommand(args,{stdout:value=>console.log(value),stderr:value=>console.error(value)});return;}
  if (command === "computation") {process.exitCode = await runAlchComputationCommand(args); return;}
  if ((command === "--help" || command === "-h") && !args.length) usage(0);
  if (command === "--version" && !args.length) {
    const manifest = JSON.parse(readFileSync(new URL("../package.json", import.meta.url), "utf8"));
    console.log(manifest.version);
    return;
  }
  if (command === "check-formal-claim") {
    if (args.length) {
      console.log(JSON.stringify(rejectFormalClaimFormationRequest("FORMATION_REQUEST_ARGUMENT")));
      process.exitCode = 2;
      return;
    }
    const chunks: Buffer[] = [];
    let size = 0;
    for await (const chunk of process.stdin) {
      const bytes = Buffer.isBuffer(chunk) ? chunk : Buffer.from(chunk);
      size += bytes.length;
      if (size > 1048576) {
        console.log(JSON.stringify(rejectFormalClaimFormationRequest("FORMATION_REQUEST_SIZE")));
        process.exitCode = 2;
        return;
      }
      chunks.push(bytes);
    }
    let request: unknown;
    try { request = JSON.parse(new TextDecoder("utf-8", {fatal:true}).decode(Buffer.concat(chunks))); }
    catch { request = null; }
    const formation = checkFormalClaimSourceIntake(request);
    console.log(JSON.stringify(formation));
    if (formation.status !== "checked") process.exitCode = formation.status === "unsupported" ? 3 : 2;
    return;
  }
  const sourceText=args[0]&&!args[0].startsWith("--")&&[".alch",".md"].includes(path.extname(args[0]).toLowerCase())?readFileSync(args[0],"utf8"):undefined;
  const sourceProfile=sourceText===undefined?undefined:selectAlchSourceProfile(sourceText);
  const profileIs=(...ids:string[])=>sourceProfile!==undefined&&ids.includes(sourceProfile.profile.id);
  if (command === "qualify") {
    if (args.length !== 3 || !sourceText || args[1] !== "--claim"
      || !["closed-state-model", "executable-runtime"].includes(args[2]!)) throw Error("ALCH_BEHAVIOR_ARGUMENT");
    console.log(JSON.stringify(qualifyBehavioralClaim(sourceText, args[2] as BehavioralClaim), null, 2));
    return;
  }
  const sourceCommands=new Set(["check","build","verify","trace","ontology","explain","conformance"]);
  if(sourceProfile&&sourceCommands.has(command!)&&!sourceProfile.profile.commands.includes(command!))throw Error(`ALCH_PROFILE_COMMAND_UNSUPPORTED:${sourceProfile.profile.id}:${command}`);
  if (["check", "build", "verify"].includes(command) && args[0] && !args[0].startsWith("--") && profileIs("application-v1")) {
    const allowed = new Set(["--application-bindings", "--entry", ...(command === "check" ? [] : ["--out"])]), seen = new Set<string>();
    for (let i = 1; i < args.length; i += 2) {
      if (!allowed.has(args[i]!) || seen.has(args[i]!) || !args[i + 1] || args[i + 1]!.startsWith("--")) throw Error("APPLICATION_FILE_ARGUMENT");
      seen.add(args[i]!);
    }
    const options = { companion: option(args, "--application-bindings"), entry: option(args, "--entry") };
    const { checkApplicationFile } = await import("./application-file-check.js");
    if (command === "check") console.log(JSON.stringify(await checkApplicationFile(args[0], options), null, 2));
    else {
      const out = option(args, "--out"); if (!out) throw Error("APPLICATION_FILE_ARGUMENT: --out required");
      const { buildApplicationFile, verifyApplicationFile } = await import("./application-file-build.js");
      console.log(JSON.stringify(await (command === "build" ? buildApplicationFile : verifyApplicationFile)(args[0], out, options), null, 2));
    }
    return;
  }
  if(['check','build','ontology'].includes(command) && args[0] && !args[0].startsWith('--') && profileIs('module-configuration-v1', 'module-configuration-v2')){
    if(command==='build'){if(args.length!==3||args[1]!=='--out')throw Error('MODULE_CONFIGURATION_ARGUMENT: build <file.alch> --out <new-directory>');console.log(JSON.stringify(buildModuleConfiguration(args[0],args[2]),null,2));}
    else {if(args.length!==1)throw Error('MODULE_CONFIGURATION_ARGUMENT');console.log(JSON.stringify(command==='ontology'?compileModuleConfiguration(args[0]).ontology:checkModuleConfiguration(args[0]),null,2));}
    return;
  }
  if(['check','build','ontology'].includes(command) && args[0] && !args[0].startsWith('--') && profileIs('bound-application-v1')){
    if(command==='build'){if(args.length!==3||args[1]!=='--out')throw Error('APPLICATION_ARGUMENT');console.log(JSON.stringify(await buildApplication(args[0],args[2])));}
    else {if(args.length!==1)throw Error('APPLICATION_ARGUMENT');const result=await checkApplication(args[0]);console.log(JSON.stringify(command==='ontology'?result.plan:result,null,2));}return;
  }

  if(['check','build'].includes(command)&&args[0]&&!args[0].startsWith('--')&&profileIs('request-custody-v1')){
    if(command==='check'){if(args.length!==1)throw Error('CUSTODY_ARGUMENT');console.log(JSON.stringify(await checkCustody(args[0])));}
    else {if(args.length!==3||args[1]!=='--out')throw Error('CUSTODY_ARGUMENT');console.log(JSON.stringify(await buildCustody(args[0],args[2])));}return;
  }
  if(['check','build'].includes(command)&&args[0]&&!args[0].startsWith('--')&&profileIs('response-stream-v1')){
    if(command==='check'){if(args.length!==1)throw Error('STREAM_ARGUMENT');console.log(JSON.stringify(await checkStream(args[0])));}
    else {if(args.length!==3||args[1]!=='--out')throw Error('STREAM_ARGUMENT');console.log(JSON.stringify(await buildStream(args[0],args[2])));}return;
  }
  if(['check','build','ontology'].includes(command)&&args[0]&&!args[0].startsWith('--')&&profileIs('semantic-contract-v1')){
    if(command==='build'){if(args.length!==3||args[1]!=='--out')throw Error('SEMANTIC_CONTRACT_ARGUMENT: build <file.alch> --out <new-directory>');console.log(JSON.stringify(await buildSemanticContract(args[0],args[2]),null,2));}
    else {if(args.length!==1)throw Error('SEMANTIC_CONTRACT_ARGUMENT');console.log(JSON.stringify(command==='ontology'?(await compileSemanticContract(args[0])).ontology:await checkSemanticContract(args[0]),null,2));}
    return;
  }
  if(['check','build'].includes(command)&&args[0]&&!args[0].startsWith('--')&&profileIs('outbound-invocation-v1')){
    if(command==='check'){if(args.length!==1)throw Error('OUTBOUND_ARGUMENT');console.log(JSON.stringify(await checkOutbound(args[0])));}
    else {if(args.length!==3||args[1]!=='--out')throw Error('OUTBOUND_ARGUMENT');console.log(JSON.stringify(await buildOutbound(args[0],args[2])));}return;
  }
  if(['check','build','ontology'].includes(command) && args[0] && !args[0].startsWith('--') && profileIs('service-v1')){
    if(/^assembly public-routes-v1$/m.test(sourceText!)){
      const {buildServiceRoutes,checkServiceRoutes}=await import('./service-routes.js');
      if(command==='build'){if(args.length!==3||args[1]!=='--out')throw Error('SERVICE_ARGUMENT');console.log(JSON.stringify(await buildServiceRoutes(args[0],args[2])));}
      else {if(command!=='check'||args.length!==1)throw Error('SERVICE_ARGUMENT: public routes support check/build');console.log(JSON.stringify(await checkServiceRoutes(args[0])));}return;
    }
    if(command==='build'){if(args.length!==3||args[1]!=='--out')throw Error('SERVICE_ARGUMENT: build <service.alch> --out <new-directory>');console.log(JSON.stringify(await buildService(args[0],args[2])));}
    else {if(args.length!==1)throw Error('SERVICE_ARGUMENT');const compiled=compileService(args[0]);console.log(JSON.stringify(command==='ontology'?compiled.ontology:{status:'valid',profile:'service-v1',service:compiled.service.id,entries:compiled.entries.map(entry=>({id:entry.id,...entry.route,input:entry.input,output:entry.output})),authority_effect:'none'},null,2));}
    return;
  }
  if (['check','build','ontology','explain'].includes(command) && args[0] && !args[0].startsWith('--') && profileIs('semantic-host-v1')) {
    requireOptionalFeature('rust');
    const {buildSemanticHost,compileSemanticHost}=await import('./semantic-host.js');
    if(command==='build'){if(args.length!==3||args[1]!=='--out')throw Error('SEMANTIC_ARGUMENT');console.log(JSON.stringify(await buildSemanticHost(args[0],args[2])));}
    else {if(args.length!==1)throw Error('SEMANTIC_ARGUMENT');const plan=await compileSemanticHost(readFileSync(args[0],'utf8'));console.log(JSON.stringify(command==='check'?{status:'valid',profile:'semantic-host-v1',authority_effect:'none'}:plan.ontology,null,2));}return;
  }

  if (["check","build","ontology"].includes(command) && args[0] && !args[0].startsWith('--') && profileIs('ontology-host-v1')) {
    requireOptionalFeature('local-host');
    const {buildOntologyHost,compileOntologyHost}=await import('./ontology-host.js');
    if(command==='build'){if(args.length!==3||args[1]!=='--out')throw Error('ONTOLOGY_HOST_ARGUMENT');console.log(JSON.stringify(await buildOntologyHost(args[0],args[2])));}
    else {if(args.length!==1)throw Error('ONTOLOGY_HOST_ARGUMENT');const plan=await compileOntologyHost(readFileSync(args[0],'utf8'));console.log(JSON.stringify(command==='ontology'?plan.ontology:{status:'valid',profile:'ontology-host-v1',schemas:plan.schemas,authority_effect:'none'},null,2));}
    return;
  }
  if (["check", "build"].includes(command) && args[0] && !args[0].startsWith("--") && profileIs('local-host-migration-v1')) {
    requireOptionalFeature('local-host');
    const {buildStateMigration,compileStateMigration}=await import('./state-migration.js');
    if(command==='check') {if(args.length!==1)throw Error('MIGRATION_ARGUMENT');console.log(JSON.stringify({status:'valid',...(await compileStateMigration(readFileSync(args[0],'utf8'))).manifest}));}
    else {if(args.length!==3||args[1]!=='--out')throw Error('MIGRATION_ARGUMENT');console.log(JSON.stringify(await buildStateMigration(args[0],args[2])));}
    return;
  }
  if (["check", "build"].includes(command) && args[0] && !args[0].startsWith("--") && profileIs('local-host-v1')) {
    requireOptionalFeature('local-host');
    const {buildLocalHost,compileLocalHost}=await import('./local-host.js');
    if (command === 'check') {
      if (args.length !== 1) throw Error('LOCAL_HOST_ARGUMENT');
      console.log(JSON.stringify({status: 'valid', ...(await compileLocalHost(readFileSync(args[0], 'utf8'))).deployment}));
    } else {
      if (args.length !== 3 || args[1] !== '--out') throw Error('LOCAL_HOST_ARGUMENT');
      console.log(JSON.stringify(await buildLocalHost(args[0], args[2])));
    }
    return;
  }
  if (["check", "build"].includes(command) && args[0] && !args[0].startsWith("--") && profileIs('event-execution-v1')) {
    requireOptionalFeature('rust');
    const {buildEventExecution,compileEventExecution}=await import('./event-execution.js');
    if (command === "check") {if(args.length!==1)throw Error("EVENT_ARGUMENT");await compileEventExecution(readFileSync(args[0],"utf8"));console.log(JSON.stringify({status:"valid",profile:"event-execution-v1"}));}
    else {if(args.length!==3||args[1]!=="--out")throw Error("EVENT_ARGUMENT");console.log(JSON.stringify(await buildEventExecution(args[0],args[2])));}
    return;
  }
  if (["check", "build"].includes(command) && args[0] && !args[0].startsWith("--") && profileIs('event-function-v1')) {
    if (command === "check") {
      if (args.length !== 1) throw Error("EVENT_ARGUMENT");
      const result = await compileEventProfile(readFileSync(args[0], "utf8"));
      console.log(JSON.stringify({status:"valid",profile:result.profile,domain_id:result.domain_id,authority_effect:"none"}));
    } else {
      if (args.length !== 3 || args[1] !== "--out") throw Error("EVENT_ARGUMENT: build <file.alch> --out <new-directory>");
      console.log(JSON.stringify(await buildEventProfile(args[0], args[2])));
    }
    return;
  }
  if(command==='conformance'){
    requireOptionalFeature('rust');
    const {runConformance}=await import('./conformance.js');
    if(args.length!==5||args[1]!=='--fixtures'||args[3]!=='--out')throw Error('CONFORMANCE_ARGUMENT: conformance <file.alch> --fixtures <file.json> --out <new-directory>');
    const report=await runConformance(args[0],args[2],args[4]);console.log(JSON.stringify({status:report.status,count:report.count,report:path.resolve(args[4],'report.json')},null,2));if(report.status!=='pass')process.exitCode=1;return;
  }
  if(command==='trace'){
    if(args.length!==3||args[1]!=='--input'||args[0].startsWith('--')||args[2].startsWith('--'))throw Error('TRACE_ARGUMENT: trace <file.alch> --input <input.json>');
    const rust=/^  target rust-http$/m.test(readFileSync(args[0],'utf8'));
    if(rust)requireOptionalFeature('rust');
    const result=await (rust?(await import('./rust-function-builder.js')).traceRustFunction(args[0],args[2]):traceFunction(args[0],args[2]));console.log(JSON.stringify(result,null,2));if(result.outcome.status==='failed')process.exitCode=1;return;
  }
  if(command==='ontology'||command==='explain'){
    if(args.length!==(command==='ontology'?1:2)||args.some(a=>a.startsWith('--')))throw Error('ONTOLOGY_ARGUMENT: ontology <file.alch> | explain <file.alch> <declaration>');
    console.log(JSON.stringify(await inspectFunctionOntology(args[0],command==='explain'?args[1]:undefined),null,2));return;
  }
  if (['check','build'].includes(command) && args[0] && !args[0].startsWith('--') && profileIs('query-iteration-v1')) {
    if(command==='check'){if(args.length!==1)throw Error('QUERY_ITERATION_ARGUMENT');console.log(JSON.stringify(await checkQueryIteration(args[0])));}
    else {if(args.length!==3||args[1]!=='--out')throw Error('QUERY_ITERATION_ARGUMENT');console.log(JSON.stringify(await buildQueryIteration(args[0],args[2])));}return;
  }
  if (["check","build"].includes(command) && args[0] && !args[0].startsWith("--") && profileIs('function-v1','declarative-function-v1')) {
    const allowed=new Set(command==="build"?["--out","--target"]:["--target"]),seen=new Set<string>();
    for(let i=1;i<args.length;i+=2){if(!allowed.has(args[i])||seen.has(args[i])||!args[i+1]||args[i+1].startsWith("--"))throw Error("FUNCTION_ARGUMENT");seen.add(args[i]);}
    if(option(args,"--target") && !["node-http","rust-http"].includes(option(args,"--target")!))throw Error("FUNCTION_TARGET");
    const rustTarget=(option(args,"--target")??(/^  target rust-http$/m.test(readFileSync(args[0],"utf8"))?"rust-http":"node-http"))==="rust-http";
    if(rustTarget)requireOptionalFeature('rust');
    if(command==="build"&&option(args,"--target")==="node-http"&&/^  target rust-http$/m.test(readFileSync(args[0],"utf8")))throw Error("FUNCTION_TARGET: Rust source cannot select the Node target");
    if(command==="check")console.log(JSON.stringify(await checkFunction(args[0],option(args,"--target")),null,2));
    else {const out=option(args,"--out");if(!out)throw Error("FUNCTION_OUTPUT_REQUIRED");console.log(JSON.stringify(await (rustTarget?(await import('./rust-function-builder.js')).buildRustFunction(args[0],out):buildFunction(args[0],out)),null,2));}
    return;
  }
  if (command === "domainspec") {
    process.exitCode = await runDomainSpecCli(args);
    return;
  }
  if (command === "registry" && args[0] === "build") {
    const config = option(args, "--config"); if (!config) usage();
    const result = writeRegistryCompilation(config);
    console.log(JSON.stringify({ status: "built", patterns: result.registry.patterns.length, available: result.registry.patterns.filter((pattern) => pattern.availability === "available").length, authority_effect: "none" }, null, 2));
    return;
  }
  if (command === "patterns") {
    const filter = args.includes("--available") ? "available" : args.includes("--blocked") ? "blocked" : "all";
    console.log(JSON.stringify({ schema_version: "cav2.alchlang.operation-pattern-list/v1-candidate", patterns: listOperationPatterns(filter), authority_effect: "none" }, null, 2));
    return;
  }
  if (command === "pattern") {
    const patternId = args[0]; if (!patternId) usage();
    console.log(JSON.stringify({ status: "generatable", pattern: requireGeneratablePattern(patternId), authority_effect: "none" }, null, 2));
    return;
  }
  if (command === "emit-domainspec" || ["build", "check"].includes(command) && option(args, "--backend") !== "local-compat") {
    const sourcePath=args[0]; if(!sourcePath || sourcePath.startsWith("--"))usage();
    const profile=option(args,"--profile"); const backend=option(args,"--backend") ?? "domainspec";const language=option(args,"--language");
    if(profile && ![DOMAINSPEC_PROFILE,EXACT_PROFILE].includes(profile) || backend && backend!=="domainspec" || language && language!=="typescript")throw new Error("DS_PROFILE_UNSUPPORTED");
    const allowed=new Set(["--backend","--profile","--bindings",...(command==="build"?["--backend","--language","--out"]:command==="emit-domainspec"?["--out"]:[])]);
    const seen=new Set<string>();
    for(let i=1;i<args.length;i+=2){if(seen.has(args[i]) || !allowed.has(args[i]) || !args[i+1] || args[i+1].startsWith("--"))throw new Error(`DS_ARGUMENT:${args[i]}`);seen.add(args[i]);}
    if(command==="build" && backend!=="domainspec")throw new Error("DS_BACKEND_REQUIRED");
    const options={bindingsPath:option(args,"--bindings"),profile};
    if(command==="build"&&option(args,"--target")==="node-http"&&/^  target rust-http$/m.test(readFileSync(args[0],"utf8")))throw Error("FUNCTION_TARGET: Rust source cannot select the Node target");
    if(command==="check")console.log(JSON.stringify(await checkDomainSpec(sourcePath,options),null,2));
    else {const out=option(args,"--out");if(!out)throw new Error("DS_OUTPUT_REQUIRED");console.log(JSON.stringify(await buildDomainSpec(sourcePath,out,{...options,generate:command==="build"}),null,2));}
    return;
  }
  if (["check", "build"].includes(command)) {
    const allowed = new Set(command === "build" ? ["--backend", "--out", "--force"] : ["--backend"]);
    const seen = new Set<string>();
    for (let i = 1; i < args.length; i++) {
      const flag = args[i];
      if (!allowed.has(flag) || seen.has(flag)) throw Error(`LOCAL_COMPAT_ARGUMENT:${flag}`);
      seen.add(flag);
      if (flag !== "--force" && (!args[++i] || args[i].startsWith("--"))) throw Error(`LOCAL_COMPAT_ARGUMENT:${flag}`);
    }
    if (option(args, "--backend") !== "local-compat") throw Error("LOCAL_COMPAT_BACKEND_REQUIRED");
  }
  if (command === "check") {
    const sourcePath = args[0]; if (!sourcePath || sourcePath.startsWith("--")) usage();
    const loaded = loadAlchLangSource(sourcePath);
    for (const diagnostic of loaded.diagnostics) console.error(`${diagnostic.code}: ${diagnostic.message}`);
    const result = compileCarrier(loaded.carrier);
    console.log(JSON.stringify({ status: "valid", source: loaded.source_path, file_format: loaded.file_format, domain_id: result.plan.model.domain_id, plan_digest: result.plan_digest, authority_effect: "none" }, null, 2));
    return;
  }
  if (command === "build") {
    const sourcePath = args[0]; if (!sourcePath || sourcePath.startsWith("--")) usage();
    const parsed = loadAlchLangSource(sourcePath);
    for (const diagnostic of parsed.diagnostics) console.error(`${diagnostic.code}: ${diagnostic.message}`);
    const result = compileCarrier(parsed.carrier);
    const receipt = writeCompilation(result, option(args, "--out") ?? path.resolve(process.cwd(), "generated"), { force: args.includes("--force"), carrier: parsed.carrier });
    console.log(JSON.stringify({ status: "built", source: path.resolve(sourcePath), ...receipt, authority_effect: "none" }, null, 2));
    return;
  }
  if (command === "outbox") {
    const operation = args[0];
    const databasePath = option(args, "--database");
    if (!databasePath || !["pending","status","dispatch","requeue-dead"].includes(operation ?? "")) usage();
    const limit = positiveInteger(option(args, "--limit"), 100);
    const outbox = new DurableSqliteTransactionalOutbox(databasePath);
    try {
      if (operation === "pending" || operation === "status") {
        const selected = option(args,"--status") as DurableOutboxStatus|undefined;
        if(selected && !["pending","leased","published","dead"].includes(selected)) throw new Error(`OUTBOX_STATUS_INVALID:${selected}`);
        console.log(JSON.stringify({ status: "inspected", database: path.resolve(databasePath), messages: outbox.records(selected??(operation==="pending"?"pending":undefined),limit), stats: outbox.stats(), schema_version:outbox.schemaVersion(), authority_effect: "none" }, null, 2));
        return;
      }
      if(operation === "requeue-dead"){const id=option(args,"--message-id"),now=option(args,"--now");if(!id||!now)usage();outbox.requeueDead(id,now);console.log(JSON.stringify({status:"requeued",message_id:id,stats:outbox.stats(),authority_effect:"local-sqlite-write"},null,2));return;}
      const transportId = option(args, "--transport");
      const workerId=option(args,"--worker-id");if(!workerId)usage();const now=option(args,"--now")??new Date().toISOString();
      const collected:DurableOutboxRecord[]=[];let transport:DurableOutboxTransport;let authorityEffect="local-stdout-only";
      if(transportId==="stdout")transport={async publish(message){collected.push(structuredClone(message));}};
      else if(transportId==="http"){const endpoint=option(args,"--endpoint"),origin=option(args,"--allow-origin"),confirmation=option(args,"--confirm-network-dispatch");if(!endpoint||!origin||confirmation!==origin||new URL(endpoint).origin!==origin)throw new Error("OUTBOX_HTTP_CONFIRMATION_REQUIRED");transport=new HttpOutboxTransport(endpoint,new FetchOutboxHttpClient([origin]));authorityEffect="explicit-confirmed-http-dispatch";}
      else throw new Error(`OUTBOX_TRANSPORT_UNSUPPORTED:${transportId??"missing"}`);
      const result = await new DurableOutboxWorker(outbox,transport,{workerId,clock:()=>now,leaseMs:positiveInteger(option(args,"--lease-ms"),30000),retryBaseMs:positiveInteger(option(args,"--retry-base-ms"),1000)}).dispatch(limit);
      console.log(JSON.stringify({ status: "dispatched", transport: transportId, messages: collected, result, stats: outbox.stats(), authority_effect: authorityEffect }, null, 2));
      return;
    } finally {
      outbox.close();
    }
  }
  if (command === "run") {
    const [sourcePath, actionId] = args; if (!sourcePath || !actionId) usage();
    const actor = option(args, "--actor"); const factsText = option(args, "--facts"); const grant = option(args, "--grant");
    if (!actor || !factsText || !grant) usage();
    const parsed = loadAlchLangSource(sourcePath); const compiled = compileCarrier(parsed.carrier);
    const action = compiled.plan.model.actions.find((item) => item.id === actionId); if (!action) throw new Error(`ACTION_NOT_FOUND:${actionId}`);
    const bindingId = option(args, "--binding");
    if (bindingId) {
      const databasePath = option(args, "--database"); const requestPath = option(args, "--effect-request-file");
      if (!databasePath || !requestPath) usage();
      const effectRequest: unknown = JSON.parse(readFileSync(requestPath, "utf8"));
      validateAtomicStateAndOutboxRequest(effectRequest);
      const failpointText = option(args, "--failpoint");
      if (failpointText && failpointText !== "after-state-write") throw new Error(`OUTBOX_FAILPOINT_UNSUPPORTED:${failpointText}`);
      const adapter = SqliteTransactionalOutboxActionAdapter.open({ model: compiled.plan.model, actionId, bindingId, databasePath, effectRequest, failpoint: failpointText as "after-state-write" | undefined });
      try {
        const result = await executeAction(compiled.plan.model, { action_id: actionId, actor_ref: actor, facts: JSON.parse(factsText), authority_grants: [grant] }, { [actionId]: adapter });
        console.log(JSON.stringify({ ...result, database: path.resolve(databasePath), outbox: adapter.outbox.stats(), authority_effect: "local-sqlite-write" }, null, 2));
      } finally {
        adapter.close();
      }
      return;
    }
    if (action.performs.length > 0) throw new Error(`EFFECT_BINDING_REQUIRED:${actionId}`);
    if (option(args, "--adapter") !== "memory") throw new Error(`ACTION_ADAPTER_REQUIRED:${actionId}`);
    const adapter = new MemoryActionAdapter({ outcome: "completed", emitted_events: action.outcome_refs });
    const result = await executeAction(compiled.plan.model, { action_id: actionId, actor_ref: actor, facts: JSON.parse(factsText), authority_grants: [grant] }, { [actionId]: adapter });
    console.log(JSON.stringify({ ...result, authority_effect: "none" }, null, 2));
    return;
  }
  usage();
}

runCli(import.meta.url, main);
