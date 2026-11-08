import {canonicalJson,sha256} from '../input/source-manifest.js';
import {assertSelectedReconciledProject,selectedReconciledIdentity,type SelectedReconciledProject} from './selected-reconciled-project.js';
import {selectReconciledProjectArtifacts} from './reconciled-project-layout.js';
import {assertRequestApplicationBindingV1,type RequestApplicationBindingV1} from '../system-integration/application-binding-v1.js';
import {freezeRequestApplication,requestApplicationFail} from '../system-integration/request-application-source-v1.js';
import {validateOperationRequestContracts,typescriptRuntimeMappingArtifact,operationRequestArtifact,typescriptRequestHandlerArtifact,mergeWholeApplicationArtifactsV1} from './whole-application-v1.js';
import type {PlannedArtifact} from './contracts.js';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {captureJson,dataDigest} from '../profile-engine/contracts.js';
import {checkU0WireConfiguration,type U0WireConfiguration} from '../profile-engine/u0-realization-contract.js';
import {decodeRequestApplicationSourceV2,type RequestApplicationIntentSourceV2} from '../system-integration/request-application-source-v1.js';
import type {U0FileArtifactV2,U0TypedClosureOriginV2} from '../profile-engine/business-authoring-stages-v2.js';

/** Provider-free plan, distinct from WholeApplicationPlanV1.
 * Open questions: profile/native/installed joins BA07–18. */
export interface RequestApplicationPlanV1 {
 readonly schema_version:'domainspec.request-application-plan/v1-candidate';readonly language:'typescript';readonly project_id:string;
 readonly domain_source_manifest_sha256:string;readonly request_source_sha256:string;readonly binding_sha256:string;
 readonly application_plan_sha256:string;readonly application_graph_sha256:string;
 readonly artifacts:readonly PlannedArtifact[];
 readonly path_owners:readonly Readonly<{relative_path:string;owner:'reconciled-application'|'request-application-composer';sha256:string}>[];
 readonly handlers:readonly Readonly<{intent_id:string;mapping_binding_ref:string;operation_ref:string;operation_module:string}>[];
 readonly native_type_dependencies:readonly string[];readonly runtime_guarantees_observed:false;readonly authority_effect:'none';readonly claim_ceiling:'formation-and-static-compilation-only';readonly plan_sha256:string;
}
const plans=new WeakMap<object,{digest:string;application:SelectedReconciledProject;binding:RequestApplicationBindingV1}>();
export function assertRequestApplicationPlanV1(value:unknown):asserts value is RequestApplicationPlanV1 {
 const state=value&&typeof value==='object'?plans.get(value):undefined;
 if(!state||state.digest!==sha256(canonicalJson(value)))return requestApplicationFail('DS_REQUEST_APPLICATION_PLAN_SNAPSHOT','/plan','use registered minimal plan');
 assertSelectedReconciledProject(state.application);assertRequestApplicationBindingV1(state.binding);
}
export function composeRequestApplicationPlanV1(application:SelectedReconciledProject,binding:RequestApplicationBindingV1):RequestApplicationPlanV1 {
 assertSelectedReconciledProject(application);assertRequestApplicationBindingV1(binding);
 const identity=selectedReconciledIdentity(application);
 if(application.selection.language!=='typescript'||identity.source_manifest_sha256!==binding.domain_source_manifest_sha256||application.plan_sha256!==binding.application_plan_sha256)requestApplicationFail('DS_REQUEST_APPLICATION_PLAN_JOIN','/plan','exact registered application/binding join required');
 const view=selectReconciledProjectArtifacts(application),graph=binding.application_graph;
 validateOperationRequestContracts(application,graph.operation_requests,graph.runtime_bindings);
 const handler=typescriptRequestHandlerArtifact(view,binding),runtime=typescriptRuntimeMappingArtifact(view,graph.runtime_bindings),requests=operationRequestArtifact('typescript',view,graph.operation_requests);
 // Reuse checked ownership/import closure without relabeling this plan as a whole certificate.
 const graphContent=canonicalJson(graph)+'\n',graphArtifact={relative_path:'.domainspec/application-graph.json',content:graphContent,sha256:sha256(graphContent),size_bytes:Buffer.byteLength(graphContent)};
 const extra=[handler,runtime,requests,graphArtifact],merged=mergeWholeApplicationArtifactsV1([...view.artifacts.map(artifact=>({artifact,owner:'reconciled-application' as const})),...extra.map(artifact=>({artifact,owner:'whole-application-composer' as const}))]);
 const handlers=binding.source.entries.map(entry=>{
  const bindingId=graph.runtime_bindings.find(r=>r.source_pointer==='/entries/'+binding.source.entries.indexOf(entry))!.binding_id;
  const modules=view.modules.filter(m=>{const row=m as {selector?:string;qualified_selectors?:readonly string[];exports?:readonly {name:string;kind:string}[]};return (row.selector===entry.operation_ref||row.qualified_selectors?.includes(entry.operation_ref))&&row.exports?.some(e=>e.kind==='type'&&e.name==='OperationInput')&&!m.relative_path.includes('.provider.')&&!m.relative_path.includes('/_providers/');});
  if(modules.length!==1)requestApplicationFail('DS_REQUEST_APPLICATION_NATIVE_EXPORT',entry.id,'exact Operation export required');
  return {intent_id:entry.id,mapping_binding_ref:bindingId,operation_ref:entry.operation_ref,operation_module:modules[0]!.relative_path};
 });
 const body={schema_version:'domainspec.request-application-plan/v1-candidate' as const,language:'typescript' as const,project_id:identity.project_id,domain_source_manifest_sha256:identity.source_manifest_sha256,request_source_sha256:binding.request_source_sha256,binding_sha256:binding.binding_sha256,application_plan_sha256:application.plan_sha256,application_graph_sha256:graph.graph_sha256,artifacts:merged.artifacts,path_owners:merged.path_owners.map(row=>({...row,owner:row.owner==='reconciled-application'?'reconciled-application' as const:'request-application-composer' as const})),handlers,native_type_dependencies:merged.artifacts.filter(a=>a.relative_path.endsWith('.ts')).map(a=>a.relative_path),runtime_guarantees_observed:false as const,authority_effect:'none' as const,claim_ceiling:'formation-and-static-compilation-only' as const};
 const result=freezeRequestApplication({...body,plan_sha256:sha256(canonicalJson(body))});plans.set(result,{digest:sha256(canonicalJson(result)),application,binding});return result;
}

/** Finite successor composition data. Only the Q01 private owner can bind actual
 * generated/native custody. Open Questions: U08 successful joined witness. */
export const REQUEST_APPLICATION_PLAN_V2_MODULE_URL=import.meta.url;
export interface DirectRequestBindingDataV2 {
 readonly executable_sha256:string;readonly capture_sha256:string;readonly basis_sha256:string;
 readonly callable:U0FileArtifactV2;readonly infrastructure_handler:U0FileArtifactV2;
 readonly configuration:U0WireConfiguration;readonly rejection_code:string;
 readonly business_graph_sha256:string;readonly entity_ref:string;readonly closures:readonly U0TypedClosureOriginV2[];
}
export interface DirectRequestPlanDataV2 {
 readonly kind:'direct-request-application-plan-data-v2';readonly source:RequestApplicationIntentSourceV2;
 readonly graph:Readonly<Record<string,unknown>>;readonly request_graph_sha256:string;
 readonly entry:Readonly<{path:string;content:string;sha256:string}>;
 readonly graph_file:Readonly<{path:string;content:string;sha256:string}>;
 readonly plan_sha256:string;readonly authority_effect:'none';
}
export function composeDirectRequestApplicationPlanDataV2(input:RequestApplicationIntentSourceV2,bindingInput:DirectRequestBindingDataV2):DirectRequestPlanDataV2 {
 const source=decodeRequestApplicationSourceV2(input),binding=captureJson(bindingInput) as unknown as DirectRequestBindingDataV2;
 const fail=(message:string):never=>requestApplicationFail('DS_REQUEST_APPLICATION_DIRECT_PLAN','/plan-v2',message);
 if(!binding||typeof binding!=='object'||Object.keys(binding).sort().join(',')!==['executable_sha256','capture_sha256','basis_sha256','callable','infrastructure_handler','configuration','rejection_code','business_graph_sha256','entity_ref','closures'].sort().join(','))fail('closed binding data required');
 for(const key of ['executable_sha256','capture_sha256','basis_sha256','business_graph_sha256']as const)if(typeof binding[key]!=='string'||!/^[a-f0-9]{64}$/.test(binding[key]))fail('actual digest reference shape required');
 if(binding.executable_sha256!==source.executable_sha256)fail('original executable identity differs');
 for(const artifact of [binding.callable,binding.infrastructure_handler])if(!artifact||Object.keys(artifact).sort().join(',')!=='bytes,path,sha256'||typeof artifact.path!=='string'||!path.isAbsolute(artifact.path)||path.normalize(artifact.path)!==artifact.path||/[\\\u0000-\u001f\u007f]/.test(artifact.path)||typeof artifact.sha256!=='string'||!/^[a-f0-9]{64}$/.test(artifact.sha256)||!Number.isSafeInteger(artifact.bytes)||artifact.bytes<1||artifact.bytes>16777216)fail('bounded actual artifact reference required');
 const configuration=checkU0WireConfiguration(binding.configuration);
 if(typeof binding.rejection_code!=='string'||!binding.rejection_code||binding.rejection_code.length>8192||[...binding.rejection_code].length>4096||/[\uD800-\uDFFF]/u.test(binding.rejection_code))fail('exact authored scalar rejection code required');
 const entry=source.entries[0]!;
 const expected=[['Entity',binding.entity_ref],['Rule',entry.rule_ref],['Operation',entry.operation_ref],['Interface',entry.interface_ref],['Mapping',entry.mappings.input],['Mapping',entry.mappings.output]] as const;
 if(typeof binding.entity_ref!=='string'||!/^[a-z][a-z0-9]*(?:-[a-z0-9]+)*:[a-z][a-z0-9]*(?:-[a-z0-9]+)*$/.test(binding.entity_ref)||new Set(expected.map(row=>row[1])).size!==6)fail('six distinct selected role identities required');
 if(!Array.isArray(binding.closures)||binding.closures.length!==6)fail('all six original typed roles required');
 for(const [role,selector]of expected){
  const matches=binding.closures.filter(c=>c.role===role&&c.selector===selector);
  if(matches.length!==1||typeof matches[0]!.typed_closure_sha256!=='string'||!/^[a-f0-9]{64}$/.test(matches[0]!.typed_closure_sha256)||!Array.isArray(matches[0]!.origins)||!matches[0]!.origins.some(origin=>origin.source===entry.origins[0]!.source&&origin.sha256===source.source_sha256))fail('original role closure/origin correspondence required');
 }
 const graph=captureJson({schema_version:'domainspec.direct-request-graph/v2-candidate',model_id:source.model_id,source_sha256:source.source_sha256,executable_sha256:source.executable_sha256,capture_sha256:binding.capture_sha256,basis_sha256:binding.basis_sha256,business_graph_sha256:binding.business_graph_sha256,entry,entity_ref:binding.entity_ref,closures:binding.closures,callable:binding.callable,infrastructure_handler:binding.infrastructure_handler,configuration,authority_effect:'none'}) as unknown as Readonly<Record<string,unknown>>;
 const graphContent=canonicalJson(graph)+'\n',graphHash=sha256(graphContent);
 const planHash=dataDigest({graph_sha256:graphHash,rejection_code:binding.rejection_code,wire:configuration});
 const directory=path.dirname(binding.callable.path),entryPath=path.join(directory,'u0-entry-'+planHash+'.mjs'),graphPath=path.join(directory,'u0-request-'+planHash+'.json');
 const content='// Generated finite U0 entry; source/profile/native plan '+planHash+'\n'+
  'import {invoke} from '+JSON.stringify(pathToFileURL(binding.callable.path).href)+';\n'+
  'import {createU0HttpHandler} from '+JSON.stringify(pathToFileURL(binding.infrastructure_handler.path).href)+';\n'+
  'export {invoke as boundInvoke};\n'+
  'export const handler = createU0HttpHandler(invoke, '+JSON.stringify(configuration)+', '+JSON.stringify({rejection_code:binding.rejection_code})+');\n';
 return captureJson({kind:'direct-request-application-plan-data-v2',source,graph,request_graph_sha256:graphHash,entry:{path:entryPath,content,sha256:sha256(content)},graph_file:{path:graphPath,content:graphContent,sha256:graphHash},plan_sha256:planHash,authority_effect:'none'}) as unknown as DirectRequestPlanDataV2;
}
