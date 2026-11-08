/** Checked C13 Workflow composition over an already checked C12 application.
 * This is an inert source projection; worker, journal, Auth and recovery owners
 * must separately bind the exact projection before effects.
 * Open Questions: docs/GENERIC-APPLICATIONS.md#open-questions. */
import {dataDigest} from '../profile-engine/contracts.js';
import {coreFreeze,coreSourceFail as fail,coreSourceChildren as children,coreSourceChild as child,coreSourceDescendants as descendants,coreSourceTokens as tokens,coreSourceText as text} from '../commerce/commerce-core-syntax.js';
import {createCoreValueTypes} from '../commerce/commerce-core-types.js';
import {coreValueAstType} from '../commerce/commerce-core-pure.js';
import type {CoreCommerceReconstruction,CoreCommerceDeclaration} from '../commerce/commerce-core-reconstruction.js';
import type {CoreCommerceSourceInspection} from '../commerce/commerce-core-source-owner.js';
import {parseCoreCommerceJson} from '../commerce/commerce-core-source-owner.js';
import type {GenericEventTransactionApplicationV1} from './event-data-v1.js';
import type {GenericEventProfile} from './profile-resolver.js';
import {resolveGenericEventProfile} from './profile-resolver.js';
import {createGenericEventTransactionSourceContract} from './transaction-source.js';
import {posix as path} from 'node:path';
import {GENERIC_EVENT_EXTERNAL_WRITE_CAPABILITIES} from './composition-capabilities.js';

export const GENERIC_WORKFLOW_CAPABILITIES=Object.freeze([...GENERIC_EVENT_EXTERNAL_WRITE_CAPABILITIES,'Workflow','recoverable-workflow'] as const);
export interface GenericWorkflowProfileV1 {
 readonly schema_version:'craft.generic-workflow-profile/v1-candidate'|'craft.generic-workflow-profile/v2';
 readonly workflow:string;
 readonly base_event_profile_sha256:string;
 readonly capabilities:readonly string[];
 readonly recovery:'needed-compensations-only/reverse-completion-v1';
 readonly storage:'service-owned-fenced-workflow-journal/v1-candidate';
 readonly stages?:readonly Readonly<{name:string;kind:'local'|'model'|'document'|'index'|'provider'|'agent-run';continuation_entry:string;maximum_attempts:number;deadline_ms:number;capability_binding?:string;capability_sha256?:string;stage_result_type?:string}>[];
}
export interface GenericWorkflowStepV1 {
 readonly name:string;
 readonly kind:'local-command'|'provider-command'|'event-await'|'model-command'|'document-command'|'index-command'|'agent-run-command';
 readonly entry:string;
 readonly entry_contract_sha256:string;
 readonly parameters?:readonly import('../commerce/commerce-data-v1.js').BinderV1[];
 readonly source_site:string;
 readonly compensation_entry?:string;
 readonly compensation_contract_sha256?:string;
 readonly compensation_parameters?:readonly import('../commerce/commerce-data-v1.js').BinderV1[];
 readonly provider_write_bindings?:readonly string[];
 readonly on_unknown?:'resume-original-command';
 readonly on_definite_failure?:'compensate';
 readonly provider_failure_compensation_precondition?:'proven-no-provider-effect';
 readonly event_binding?:string;
 readonly event_binding_sha256?:string;
 readonly continuation_entry?:string;
 readonly continuation_contract_sha256?:string;
 readonly continuation_parameters?:readonly import('../commerce/commerce-data-v1.js').BinderV1[];
 readonly maximum_attempts?:number;
 readonly deadline_ms?:number;
 readonly capability_binding?:string;
 readonly capability_sha256?:string;
}
export interface GenericWorkflowSourceContractV1 {
 readonly schema_version:'craft.generic-workflow-source/v1-candidate';
 readonly workflow:string;
 readonly service:string;
 readonly source_site:string;
 readonly source_capture_sha256:string;
 /** Content identity of the complete checked closure, independent of capture directory/inodes. */
 readonly source_closure_sha256:string;
 readonly profile_sha256:string;
 readonly base_application_sha256:string;
 readonly parameters:readonly import('../commerce/commerce-data-v1.js').BinderV1[];
 readonly correlation:string;
 readonly durable_state:string;
 readonly start_entry:string;
 readonly start_entry_contract_sha256:string;
 readonly start_parameters:readonly import('../commerce/commerce-data-v1.js').BinderV1[];
 readonly steps:readonly GenericWorkflowStepV1[];
 readonly compensation_order:readonly string[];
 readonly recovery:'needed-compensations-only/reverse-completion-v1';
 readonly authority_effect:'none';
}
const words=(n:{readonly children:readonly unknown[]})=>tokens(n as any).filter(t=>t.layout===null).map(t=>t.token);
const site=(d:CoreCommerceDeclaration)=>`${d.syntax.path}:${d.syntax.start}:${d.syntax.end}`;
const NAME=/^[A-Za-z_][A-Za-z0-9_]*$/;

/** V2 keeps the original Event-mode transaction owner but does not require an
 * unused provider or Event. Technical stages bind explicit original host ports;
 * only checked authored continuation Operations select business progression. */
function checkFiniteWorkflow(reconstruction:CoreCommerceReconstruction,application:GenericEventTransactionApplicationV1,baseProfile:GenericEventProfile,profile:GenericWorkflowProfileV1,capture:string,closure:string):GenericWorkflowSourceContractV1{
 const all=reconstruction.modules.flatMap(m=>m.declarations),at=all[0]?.syntax??{path:'workflow.alch',start:0,end:0};
 if(application.admission_mode!=='event-handoff-entry'||baseProfile.schema_version!=='craft.generic-event-profile/v1-candidate'||
   Object.keys(profile).sort().join(',')!=='base_event_profile_sha256,capabilities,recovery,schema_version,stages,storage,workflow'||
   profile.base_event_profile_sha256!==dataDigest(baseProfile)||dataDigest(profile.capabilities)!==dataDigest([...baseProfile.capabilities,'Workflow','recoverable-workflow'])||
   profile.storage!=='service-owned-fenced-workflow-journal/v1-candidate'||profile.recovery!=='needed-compensations-only/reverse-completion-v1'||!Array.isArray(profile.stages)||profile.stages.length<1||profile.stages.length>64)
  fail('InvalidContract',at,'exact bounded finite Workflow V2 profile required');
 const workflow=all.find(d=>d.id===profile.workflow&&d.surface==='Workflow'&&d.syntax.rule==='generic-workflow-declaration');
 if(!workflow||all.filter(d=>d.surface==='Workflow').length!==1)fail('MissingMapping',at,'one selected authored Workflow required');
 const owner=words(child(workflow.syntax,'step-name'))[0]!,owned=(id:string)=>reconstruction.ownership.find(o=>o.declaration===id)?.service;
 if(!NAME.test(owner)||owned(workflow.id)!==owner)fail('InvalidContract',workflow.syntax,'Workflow owner must match source ownership');
 const types=createCoreValueTypes(reconstruction),parameters=workflow.parameters.map(p=>({name:p.name,type:coreValueAstType(types.type(workflow.module,p.type,p.span))}));
 const resolve=(name:string,surface:CoreCommerceDeclaration['surface'],where=workflow.syntax)=>{const d=all.find(d=>d.id===(all.some(x=>x.id===workflow.module+'.'+name)?workflow.module+'.'+name:name));if(!d||d.surface!==surface)fail('UnknownReference',where,'exact authored '+surface+' required: '+name);return d;};
 const direct=children(workflow.syntax,'qualified-name'),state=resolve(text(direct[0]!),'Entity'),start=resolve(text(direct[1]!),'Entry');
 const correlation=words(workflow.syntax)[words(workflow.syntax).indexOf('correlation')+1]!,parameter=parameters.find(p=>p.name===correlation);
 if(!parameter||parameter.type.kind!=='scalar'&&parameter.type.kind!=='refinement'||owned(state.id)!==owner||!state.identity.includes(correlation)||!state.fields.some(f=>f.name===correlation&&dataDigest(coreValueAstType(types.type(state.module,f.type,f.span)))===dataDigest(parameter.type)))fail('InvalidContract',workflow.syntax,'typed owner state/correlation required');
 const command=(d:CoreCommerceDeclaration,principal:'customer'|'operator',extras:ReadonlyMap<string,import('../commerce/commerce-data-v1.js').ValueTypeV1>=new Map())=>{
  const e=application.entries.find(e=>e.entry===d.id&&e.interaction==='request-response');
  if(!e||e.target_role!=='Operation'||e.target!==d.invokes||e.service!==owner||owned(d.id)!==owner||e.access.principal_kind!==principal||!application.stateful_operations.some(o=>o.operation===e.target))fail('MissingMapping',d.syntax,'exact protected owner transactional '+principal+' Entry required');
  for(const p of e.parameters){const value=extras.get(p.name)??parameters.find(x=>x.name===p.name)?.type;if(!value||dataDigest(value)!==dataDigest(p.type))fail('TypeMismatch',d.syntax,'Workflow Entry parameter must bind checked input/result: '+p.name);}
  return e;
 };
 const checkedStart=command(start,'customer'),nodes=[...descendants(workflow.syntax,'local-workflow-step'),...descendants(workflow.syntax,'plain-workflow-step')].sort((a,b)=>a.start-b.start);
 if(descendants(workflow.syntax,'provider-workflow-step').length||descendants(workflow.syntax,'event-workflow-step').length||nodes.length!==profile.stages.length||new Set(profile.stages.map(s=>s.name)).size!==profile.stages.length)fail('InvalidContract',workflow.syntax,'V2 uses finite invokes steps; waits are authored continuation decisions');
 const steps:GenericWorkflowStepV1[]=nodes.map(n=>{
  const name=words(child(n,'step-name'))[0]!,s=profile.stages!.find(s=>s.name===name);
  if(!s||!NAME.test(name)||!['local','model','document','index','provider','agent-run'].includes(s.kind)||!Number.isSafeInteger(s.maximum_attempts)||s.maximum_attempts<1||s.maximum_attempts>8||!Number.isSafeInteger(s.deadline_ms)||s.deadline_ms<1||s.deadline_ms>300000)fail('InvalidContract',n,'bounded exact finite stage required');
  const allowed=['name','kind','continuation_entry','maximum_attempts','deadline_ms',...(s.kind==='local'?[]:['capability_binding','capability_sha256','stage_result_type'])].sort();
  if(Object.keys(s).sort().join(',')!==allowed.join(',')||s.kind!=='local'&&(!s.capability_binding||!s.stage_result_type||typeof s.capability_sha256!=='string'||!/^[0-9a-f]{64}$/.test(s.capability_sha256)))fail('InvalidContract',n,'nonlocal stage requires exact selected binding/descriptor digest/result type; no fallback');
  const names=children(n,'qualified-name'),entry=command(resolve(text(names[0]!),'Entry',n),'operator',new Map([['stageAttempt',{kind:'scalar',name:'UInt64'}]]));
  if(entry.entry===checkedStart.entry)fail('InvalidContract',n,'public start and worker stage Entries must differ');
  const result=s.kind==='local'?entry.result:coreValueAstType(types.type(workflow.module,{kind:'named',name:s.stage_result_type!},n));
  const continuation=command(resolve(s.continuation_entry,'Entry',n),'operator',new Map([['stageResult',result],['stageAttempt',{kind:'scalar',name:'UInt64'}],['stageRevision',{kind:'scalar',name:'UInt64'}]]));
  const hasExternal=(value:unknown):boolean=>!!value&&typeof value==='object'&&((value as {kind?:string}).kind==='write-external'||(value as {kind?:string}).kind==='read-external'||Object.values(value).some(hasExternal));
  if([entry,continuation].some(e=>hasExternal(application.stateful_operations.find(o=>o.operation===e.target)?.preflight)))fail('UnsupportedCapability',n,'finite stage request/continuation commands are local; external effects use the selected original stage port');
  if(continuation.entry===entry.entry||!continuation.parameters.some(p=>p.name==='stageResult')||continuation.result.kind!=='record')fail('InvalidContract',n,'separate typed stageResult continuation Operation required');
  const decision=resolve(continuation.result.name,'Entity',n);
  if(!decision.fields.some(f=>f.name==='kind'))fail('TypeMismatch',n,'persisted continuation Entity requires finite decision kind');
  let compensation:ReturnType<typeof command>|undefined;
  if(names[1])compensation=command(resolve(text(names[1]),'Entry',n),'operator');
  return {name,kind:s.kind==='local'?'local-command':s.kind==='provider'?'provider-command':s.kind==='model'?'model-command':s.kind==='document'?'document-command':s.kind==='index'?'index-command':'agent-run-command',entry:entry.entry,entry_contract_sha256:dataDigest(entry),parameters:entry.parameters,source_site:`${n.path}:${n.start}:${n.end}`,continuation_entry:continuation.entry,continuation_contract_sha256:dataDigest(continuation),continuation_parameters:continuation.parameters,maximum_attempts:s.maximum_attempts,deadline_ms:s.deadline_ms,...(s.capability_binding?{capability_binding:s.capability_binding,capability_sha256:s.capability_sha256!}:{}),...(compensation?{compensation_entry:compensation.entry,compensation_contract_sha256:dataDigest(compensation),compensation_parameters:compensation.parameters}:{})};
 });
 if(new Set(steps.map(s=>s.name)).size!==steps.length)fail('DuplicateSymbol',workflow.syntax,'unique finite stage names required');
 const bindings=new Map<string,string>();for(const step of steps)if(step.capability_binding){const prior=bindings.get(step.capability_binding);if(prior&&prior!==step.capability_sha256)fail('InvalidContract',workflow.syntax,'one selected binding cannot change descriptor within a Workflow');bindings.set(step.capability_binding,step.capability_sha256!);}
 return coreFreeze({schema_version:'craft.generic-workflow-source/v1-candidate',workflow:workflow.id,service:owner,source_site:site(workflow),source_capture_sha256:capture,source_closure_sha256:closure,profile_sha256:dataDigest(profile),base_application_sha256:dataDigest(application),parameters,correlation,durable_state:state.id,start_entry:checkedStart.entry,start_entry_contract_sha256:dataDigest(checkedStart),start_parameters:checkedStart.parameters,steps,compensation_order:steps.filter(s=>s.compensation_entry).map(s=>s.name).reverse(),recovery:profile.recovery,authority_effect:'none'});
}

export function checkGenericWorkflowSource(reconstruction:CoreCommerceReconstruction,application:GenericEventTransactionApplicationV1,baseProfile:GenericEventProfile,profile:GenericWorkflowProfileV1,sourceCaptureSha256:string,sourceClosureSha256=sourceCaptureSha256):GenericWorkflowSourceContractV1{
 const all=reconstruction.modules.flatMap(m=>m.declarations),at=all[0]?.syntax??{path:'workflow.alch',start:0,end:0};
 if(profile?.schema_version==='craft.generic-workflow-profile/v2')return checkFiniteWorkflow(reconstruction,application,baseProfile,profile,sourceCaptureSha256,sourceClosureSha256);
 if(application.admission_mode!=='event-handoff-entry'||!application.write_bindings.length||!application.event_bindings.length||baseProfile.schema_version!=='craft.generic-event-profile/v1-candidate'||dataDigest(baseProfile.capabilities)!==dataDigest(GENERIC_EVENT_EXTERNAL_WRITE_CAPABILITIES))fail('UnsupportedCapability',at,'C13 requires the checked cumulative C11+C12 application and exact base profile');
 if(!profile||profile.schema_version!=='craft.generic-workflow-profile/v1-candidate'||Object.keys(profile).sort().join(',')!=='base_event_profile_sha256,capabilities,recovery,schema_version,storage,workflow'||profile.base_event_profile_sha256!==dataDigest(baseProfile)||dataDigest(profile.capabilities)!==dataDigest(GENERIC_WORKFLOW_CAPABILITIES)||profile.recovery!=='needed-compensations-only/reverse-completion-v1'||profile.storage!=='service-owned-fenced-workflow-journal/v1-candidate')fail('InvalidContract',at,'exact cumulative Workflow profile required');
 const workflows=all.filter(d=>d.surface==='Workflow'&&d.syntax.rule==='generic-workflow-declaration');
 if(workflows.length!==1||workflows[0]!.id!==profile.workflow)fail('MissingMapping',at,'profile selects exactly one authored generic Workflow');
 const workflow=workflows[0]!,owner=words(child(workflow.syntax,'step-name'))[0]!,owned=(id:string)=>reconstruction.ownership.find(o=>o.declaration===id)?.service;
 if(!NAME.test(owner)||owned(workflow.id)!==owner||!reconstruction.services.some(s=>s.service===owner))fail('InvalidContract',workflow.syntax,'Workflow owner must equal its declared service');
 const resolve=(name:string,role:CoreCommerceDeclaration['surface'],where=workflow.syntax)=>{const id=all.some(d=>d.id===workflow.module+'.'+name)?workflow.module+'.'+name:name;const d=all.find(d=>d.id===id);if(!d||d.surface!==role)fail('UnknownReference',where,`Workflow requires exact ${role} ${name}`);return d;};
 const types=createCoreValueTypes(reconstruction),sourceParameters=workflow.parameters.map(p=>({name:p.name,type:types.type(workflow.module,p.type,p.span)})),parameters=sourceParameters.map(p=>({name:p.name,type:coreValueAstType(p.type)}));
 const direct=children(workflow.syntax,'qualified-name');
 const declaredCorrelation=words(workflow.syntax)[words(workflow.syntax).indexOf('correlation')+1]!;
 const parameter=sourceParameters.find(p=>p.name===declaredCorrelation);
 if(!parameter||parameter.type.kind!=='UInt64'&&parameter.type.kind!=='refinement')fail('TypeMismatch',workflow.syntax,'correlation must select one bounded scalar Workflow input');
 const state=resolve(text(direct[0]!), 'Entity'),start=resolve(text(direct[1]!), 'Entry');
 if(owned(state.id)!==owner||owned(start.id)!==owner||!state.identity.includes(declaredCorrelation)||!state.fields.some(f=>f.name===declaredCorrelation&&dataDigest(types.type(state.module,f.type,f.span))===dataDigest(parameter.type)))fail('InvalidContract',workflow.syntax,'durable Workflow state must be service owned and keyed by the typed correlation');
 const appEntry=(d:CoreCommerceDeclaration)=>application.entries.find(e=>e.entry===d.id&&e.interaction==='request-response');
 const checkedEntry=(d:CoreCommerceDeclaration,principal:'customer'|'operator')=>{const e=appEntry(d);if(!e||e.service!==owned(d.id)||e.target!==d.invokes||e.target_role!=='Operation'||e.access.principal_kind!==principal)fail('MissingMapping',d.syntax,'Workflow Entry must bind an exact checked protected '+principal+' command');for(const p of e.parameters){const input=parameters.find(x=>x.name===p.name);if(!input||dataDigest(input.type)!==dataDigest(p.type))fail('TypeMismatch',d.syntax,'Workflow input must supply exact typed Entry parameter '+p.name);}return e;};
 const checkedStart=checkedEntry(start,'customer'),local=descendants(workflow.syntax,'local-workflow-step'),provider=descendants(workflow.syntax,'provider-workflow-step'),event=descendants(workflow.syntax,'event-workflow-step');
 if(!application.stateful_operations.some(o=>o.operation===checkedStart.target))fail('InvalidContract',start.syntax,'Workflow start must be a checked durable customer command');
 if(local.length!==1||provider.length!==1||event.length!==1)fail('InvalidContract',workflow.syntax,'one local, provider and Event step in declared order required');
 const names=[...local,...provider,...event].map(n=>words(child(n,'step-name'))[0]!);if(new Set(names).size!==3)fail('DuplicateSymbol',workflow.syntax,'Workflow step names must be unique');if(names.some(n=>!NAME.test(n)))fail('InvalidContract',workflow.syntax,'workflow step names must fit the durable journal identity');
 const localNames=children(local[0]!,'qualified-name'),localEntry=resolve(text(localNames[0]!),'Entry',local[0]!),compensation=resolve(text(localNames[1]!),'Entry',local[0]!);
 const checkedLocal=checkedEntry(localEntry,'operator'),checkedCompensation=checkedEntry(compensation,'operator');
 if(checkedStart.entry===checkedLocal.entry||owned(localEntry.id)!==owner||owned(compensation.id)!==owner||checkedLocal.entry===checkedCompensation.entry||!application.stateful_operations.some(o=>o.operation===checkedLocal.target)||!application.stateful_operations.some(o=>o.operation===checkedCompensation.target))fail('InvalidContract',local[0]!,'local and compensation must be distinct checked worker commands; public start is separate');
 const providerEntry=resolve(text(child(provider[0]!,'qualified-name')),'Entry',provider[0]!),checkedProvider=checkedEntry(providerEntry,'operator'),providerOperation=application.stateful_operations.find(o=>o.operation===checkedProvider.target);
 if(owned(providerEntry.id)!==owner||!providerOperation)fail('InvalidContract',provider[0]!,'provider command must be a checked owner command');
 const writes=new Set<string>();const walk=(v:unknown)=>{if(!v||typeof v!=='object')return;if((v as any).kind==='write-external'){const ref=(v as any).call?.binding_ref;if(typeof ref==='string')writes.add(ref);}for(const child of Object.values(v))if(typeof child==='object')walk(child);};for(const s of providerOperation.preflight)walk(s);
 if(!writes.size||[...writes].some(id=>!application.write_bindings.some(b=>b.id===id)))fail('MissingMapping',provider[0]!,'provider command must bind a checked durable external write');
 const eventNames=children(event[0]!,'qualified-name'),eventDecl=resolve(text(eventNames[0]!),'Event',event[0]!),receiver=resolve(text(eventNames[1]!),'Entry',event[0]!);
 const binding=application.event_bindings.find(b=>b.event_selector===eventDecl.id&&b.target_entry===receiver.id&&b.producer_operation===checkedProvider.target),receiverEntry=application.entries.find(e=>e.entry===receiver.id&&e.interaction==='event');
 if(!binding||!receiverEntry||receiverEntry.service!==binding.target_service||owned(receiver.id)!==binding.target_service)fail('MissingMapping',event[0]!,'Event await must bind exact checked producer, handoff and protected receiver');
 const steps:GenericWorkflowStepV1[]=[
  {name:names[0]!,kind:'local-command',entry:checkedLocal.entry,entry_contract_sha256:dataDigest(checkedLocal),parameters:checkedLocal.parameters,source_site:`${local[0]!.path}:${local[0]!.start}:${local[0]!.end}`,compensation_entry:checkedCompensation.entry,compensation_contract_sha256:dataDigest(checkedCompensation),compensation_parameters:checkedCompensation.parameters},
  {name:names[1]!,kind:'provider-command',entry:checkedProvider.entry,entry_contract_sha256:dataDigest(checkedProvider),parameters:checkedProvider.parameters,source_site:`${provider[0]!.path}:${provider[0]!.start}:${provider[0]!.end}`,provider_write_bindings:[...writes].sort(),on_unknown:'resume-original-command',on_definite_failure:'compensate',provider_failure_compensation_precondition:'proven-no-provider-effect'},
  {name:names[2]!,kind:'event-await',entry:receiverEntry.entry,entry_contract_sha256:dataDigest(receiverEntry),source_site:`${event[0]!.path}:${event[0]!.start}:${event[0]!.end}`,event_binding:binding.id,event_binding_sha256:dataDigest(binding)},
 ];
 return coreFreeze({schema_version:'craft.generic-workflow-source/v1-candidate',workflow:workflow.id,service:owner,source_site:site(workflow),source_capture_sha256:sourceCaptureSha256,source_closure_sha256:sourceClosureSha256,profile_sha256:dataDigest(profile),base_application_sha256:dataDigest(application),parameters,correlation:declaredCorrelation,durable_state:state.id,start_entry:checkedStart.entry,start_entry_contract_sha256:dataDigest(checkedStart),start_parameters:checkedStart.parameters,steps,compensation_order:[names[0]!],recovery:profile.recovery,authority_effect:'none'});
}

/** Reconstructs from one original physical C12 capture. Both selected profile
 * files must occur as captured references in that same source closure. */
export function createGenericWorkflowSourceContract(capture:CoreCommerceSourceInspection){
 if(capture.capture_mode!=='event-handoff-entry')fail('InvalidContract',{path:capture.application_path,start:0,end:0},'Workflow requires original Event-mode source capture');
 const projection=createGenericEventTransactionSourceContract(capture),app=projection.contract;
 const all=capture.reconstruction.modules.flatMap(m=>m.declarations),workflow=all.find(d=>d.surface==='Workflow'&&d.syntax.rule==='generic-workflow-declaration');
 if(!workflow||all.filter(d=>d.surface==='Workflow'&&d.syntax.rule==='generic-workflow-declaration').length!==1)fail('MissingMapping',{path:capture.application_path,start:0,end:0},'one authored Workflow required');
 const reference=text(child(workflow.syntax,'reference')),profilePath=path.normalize(path.join(path.dirname(workflow.syntax.path),reference));
 if(!profilePath.startsWith('contracts/')||!profilePath.endsWith('.json')||profilePath.includes('..'))fail('InvalidContract',workflow.syntax,'Workflow profile must name an authored captured contract');
 const profileFile=capture.files.find(f=>f.path===profilePath);if(!profileFile)fail('MissingMapping',workflow.syntax,'Workflow profile reference absent from original capture');
 const profile=parseCoreCommerceJson(profileFile.text,profileFile.path) as GenericWorkflowProfileV1;
 const root=all.find(d=>d.interface_kind==='application-composition');if(!root)fail('MissingMapping',workflow.syntax,'application composition root required');
 const parameterClause=children(root.syntax,'interface-clause').find(n=>words(n)[0]==='parameters');if(!parameterClause)fail('MissingMapping',root.syntax,'selected C12 profile reference required');
 const basePath=text(descendants(parameterClause,'reference')[0]!),baseFile=capture.files.find(f=>f.path===basePath);if(!baseFile)fail('MissingMapping',parameterClause,'selected C12 profile absent from original capture');
 const base=resolveGenericEventProfile(baseFile.text,baseFile.path,app.limits,app.transaction_bounds);
 // Original physical custody remains capture.capture_sha256. Durable recovery
 // also needs a reproducible identity: public prepare reconstructs the exact
 // closure in fresh logical/expanded directories on every process start.
 const sourceClosureSha256=dataDigest({schema_version:'craft.generic-workflow-source-closure/v1',
  capture_mode:capture.capture_mode,application_path:capture.application_path,
  files:capture.files.map(({path,sha256,bytes})=>({path,sha256,bytes})).sort((a,b)=>a.path<b.path?-1:a.path>b.path?1:0)});
 const contract=checkGenericWorkflowSource(capture.reconstruction,app,base,profile,capture.capture_sha256,sourceClosureSha256);
 const executable_semantics_sha256=dataDigest({base:projection.derivation.executable_semantics_sha256,workflow:contract});
 return coreFreeze({contract,base_application:app,profile,assurance:projection.assurance,derivation:{schema_version:'craft.generic-workflow-derivation/v1-candidate',admission_capabilities_sha256:dataDigest(GENERIC_WORKFLOW_CAPABILITIES),source_capture_sha256:capture.capture_sha256,profile_sha256:contract.profile_sha256,base_application_sha256:contract.base_application_sha256,executable_semantics_sha256,authority_effect:'none' as const}});
}

export function inspectGenericWorkflowSource(capture:CoreCommerceSourceInspection){
 const checked=createGenericWorkflowSourceContract(capture);
 return coreFreeze({kind:'generic-workflow-semantic-inspection/v1-candidate' as const,admission_mode:'recoverable-workflow-entry' as const,workflows:[checked.contract],entries:checked.base_application.entries,event_bindings:checked.base_application.event_bindings,write_bindings:checked.base_application.write_bindings,derivation:checked.derivation,authority_effect:'none' as const});
}
