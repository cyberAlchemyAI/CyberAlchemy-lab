/** Optional TLA+ control-topology projection of one checked Core Commerce Workflow.
 * Each edge is a possible declared route, not a verified runtime transition.
 * Guards, observations, effects, persistence and recovery remain unmodeled.
 * Open Questions: docs/COMMERCE-CONTRACTS.md#open-questions. */
import {createHash} from 'node:crypto';
import {dataDigest} from '../profile-engine/contracts.js';
import {coreFreeze} from './commerce-core-syntax.js';
import {pinCoreImplementation} from './commerce-core-physical.js';
import type {CoreCommerceSourceOwner,CoreCommerceSourceCapture} from './commerce-core-source-owner.js';
import type {CoreCommerceSemanticOwner,CoreCommerceSemanticCapture} from './commerce-core-semantic-owner.js';
import type {CommerceWorkflowCoordinationBindingV1} from './commerce-workflow-coordination-binding-v1.js';
import type {CommerceApplicationAssemblyV1} from './commerce-application-assembly-v1.js';
import {exportCoreCommerceFormalStructureV1} from './commerce-core-formal-structure-v1.js';

export class CoreCommerceFormalTemporalErrorV1 extends Error {
 constructor(readonly code:'UnsupportedTopology'|'InvalidModel') {super(code);this.name='CoreCommerceFormalTemporalErrorV1';}
}
const fail=(code:CoreCommerceFormalTemporalErrorV1['code']):never=>{throw new CoreCommerceFormalTemporalErrorV1(code);};
const sha=(value:string)=>createHash('sha256').update(value).digest('hex');
const pin=pinCoreImplementation(import.meta.url,[]);
type LocationKind='persisted-state'|'step'|'control-target'|'terminal'|'restart'|'stopped';
type EdgeKind='select-resume'|'remote-branch'|'local-next'|'review-suspend'|'restart-choice';
type Location=Readonly<{atom:string;name:string;kind:LocationKind}>;
type Edge=Readonly<{from:string;to:string;kind:EdgeKind;source:string;guard_omitted:boolean;observation_commit_omitted:boolean}>;

export interface CoreCommerceFormalTemporalV1 {
 readonly schema_version:'craft.core-commerce-formal-temporal/v1-candidate';
 readonly language:'tla+';
 readonly scope:'possible-declared-control-routes-of-one-checked-original-workflow';
 readonly application:string;readonly workflow:string;
 readonly source_capture_sha256:string;readonly executable_sha256:string;readonly family_sha256:string;
 readonly workflow_contract_sha256:string;readonly structure_sha256:string;readonly exporter_code_sha256:string;
 readonly locations:readonly Location[];readonly edges:readonly Edge[];
 readonly tla:string;readonly tla_sha256:string;
 readonly unsupported_semantics:readonly ['guard-and-require-evaluation','outcome-feasibility','observation-commit','provider-and-entry-effects','persistence-and-cas','recovery-fencing','auth-and-event-delivery','fairness','model-checker-proof'];
 readonly authority_effect:'none';
 readonly claim_ceiling:'source-selected-possible-control-routes-only-no-executable-temporal-equivalence';
}

/** Source names stay in the adjacent metadata; the module uses fixed atoms. */
function renderTla(locations:readonly Location[],edges:readonly Edge[],persisted:readonly string[],
 identity:Readonly<{source:string;executable:string;family:string;workflow:string;structure:string;exporter:string}>):string {
 const quoted=(value:string)=>`"${value}"`;
 const set=(values:readonly string[])=>`{${values.map(quoted).join(', ')}}`;
 return [
  '---- MODULE CoreCommercePossibleRoutes ----',
  `\\* source_capture_sha256=${identity.source}`,
  `\\* executable_sha256=${identity.executable}`,
  `\\* family_sha256=${identity.family}`,
  `\\* workflow_contract_sha256=${identity.workflow}`,
  `\\* structure_sha256=${identity.structure}`,
  `\\* exporter_code_sha256=${identity.exporter}`,
  '\\* This is an over-approximation of declared control routes, not the workflow runtime.',
  '\\* Edge guards, outcome feasibility, observation commits, effects, persistence,',
  '\\* fencing, Auth, event delivery, and fairness are not represented.',
  '\\* Init chooses an arbitrary declared persisted state as a snapshot boundary.',
  '\\* A restart edge chooses any declared persisted state; it does not prove recovery.',
  '\\* No model checking or executable-equivalence claim is made.',
  `Locations == ${set(locations.map(row=>row.atom))}`,
  `PersistedLocations == ${set(persisted)}`,
  'VARIABLE cursor',
  'Init == cursor \\in PersistedLocations',
  'Next ==',
  ...edges.map((edge,index)=>`  ${index===0?'':'\\/ '}((cursor = ${quoted(edge.from)}) /\\ (cursor' = ${quoted(edge.to)}))`),
  'TypeOK == cursor \\in Locations',
  'Spec == Init /\\ [][Next]_cursor',
  '====',
  '',
 ].join('\n');
}

/** The structural exporter first validates the exact branded source, checked
 * Workflow contract and selected five-service application/profile. */
export function exportCoreCommerceFormalTemporalV1(
 sources:CoreCommerceSourceOwner,capture:CoreCommerceSourceCapture,
 semantics:CoreCommerceSemanticOwner,semantic:CoreCommerceSemanticCapture,
 binding:CommerceWorkflowCoordinationBindingV1,assembly:CommerceApplicationAssemblyV1,
):CoreCommerceFormalTemporalV1 {
 pin.assertCurrent();
 const structure=exportCoreCommerceFormalStructureV1(sources,capture,semantics,semantic,binding,assembly);
 const contract=binding.inspect().workflow;
 const locations:Location[]=[];
 const names=new Map<string,string>();
 const add=(kind:LocationKind,name:string)=>{
  const key=`${kind}\0${name}`;
  if(names.has(key))fail('UnsupportedTopology');
  const atom=`L${locations.length}`;locations.push({atom,name,kind});names.set(key,atom);return atom;
 };
 for(const row of structure.persisted_states)add('persisted-state',row.name);
 for(const row of structure.steps)add('step',row.name);
 for(const row of structure.control_targets)add('control-target',row.name);
 for(const row of structure.terminals)add('terminal',row.name);
 const restart=add('restart','restart-boundary'),stopped=add('stopped','stopped-worker');
 const find=(kind:LocationKind,name:string)=>{
  const result=names.get(`${kind}\0${name}`);
  if(!result)throw new CoreCommerceFormalTemporalErrorV1('UnsupportedTopology');
  return result;
 };
 const target=(action:string,name:string|null,category:string|null)=>{
  if(action==='resume')return restart;
  if(action==='stop-this-worker')return stopped;
  if(name===null)fail('UnsupportedTopology');
  if(action==='step')return find('step',name!);
  if(action==='finish')return find('terminal',name!);
  if(action==='suspend')return find(category==='persisted-state'?'persisted-state':'control-target',name!);
  return fail('UnsupportedTopology');
 };
 const edges:Edge[]=[];
 const push=(from:string,to:string,kind:EdgeKind,source:string,guard_omitted:boolean,observation_commit_omitted:boolean)=>{
  edges.push({from,to,kind,source,guard_omitted,observation_commit_omitted});
 };
 for(const row of structure.resume)push(find('persisted-state',row.from_state),
  target(row.action,row.target,row.suspend_category),'select-resume',row.from_state,row.guarded,false);
 for(const row of structure.steps){
  if(row.kind==='local-observation'){
   if(row.next===null)throw new CoreCommerceFormalTemporalErrorV1('UnsupportedTopology');
   push(find('step',row.name),find('step',row.next),'local-next',row.name,false,true);
  }
  if(row.kind==='review'){
   const reviewed=contract.steps.filter(step=>step.name===row.name);
   const review=reviewed[0];
   if(reviewed.length!==1||!review||review.kind!=='review')throw new CoreCommerceFormalTemporalErrorV1('UnsupportedTopology');
   const action=review.suspend;
   if(action.kind!=='suspend')throw new CoreCommerceFormalTemporalErrorV1('UnsupportedTopology');
   push(find('step',row.name),target(action.kind,action.target,action.category),'review-suspend',row.name,true,false);
  }
 }
 for(const row of structure.branches)push(find('step',row.from),target(row.action,row.target,row.suspend_category),
  'remote-branch',`${row.from}/${row.channel}/${row.variant??''}`,true,row.observes);
 const persisted=structure.persisted_states.map(row=>find('persisted-state',row.name));
 if(persisted.length===0||locations.length>256||edges.length>512)fail('UnsupportedTopology');
 for(const state of persisted)push(restart,state,'restart-choice','restart-boundary',true,false);
 const tla=renderTla(locations,edges,persisted,{source:structure.source_capture_sha256,
  executable:structure.executable_sha256,family:structure.family_sha256,
  workflow:structure.workflow_contract_sha256,structure:structure.structure_sha256,exporter:pin.sha256});
 const result:CoreCommerceFormalTemporalV1=coreFreeze({
  schema_version:'craft.core-commerce-formal-temporal/v1-candidate' as const,language:'tla+' as const,
  scope:'possible-declared-control-routes-of-one-checked-original-workflow' as const,
  application:structure.application,workflow:structure.workflow,
  source_capture_sha256:structure.source_capture_sha256,executable_sha256:structure.executable_sha256,
  family_sha256:structure.family_sha256,workflow_contract_sha256:structure.workflow_contract_sha256,
  structure_sha256:structure.structure_sha256,exporter_code_sha256:pin.sha256,locations,edges,tla,tla_sha256:sha(tla),
  unsupported_semantics:['guard-and-require-evaluation','outcome-feasibility','observation-commit',
   'provider-and-entry-effects','persistence-and-cas','recovery-fencing','auth-and-event-delivery','fairness','model-checker-proof'] as const,
  authority_effect:'none' as const,
  claim_ceiling:'source-selected-possible-control-routes-only-no-executable-temporal-equivalence' as const,
 });
 sources.assertCurrent(capture);semantics.assertCurrent(semantic);binding.assertCurrent();assembly.assertCurrent();pin.assertCurrent();
 return result;
}

export function assertCoreCommerceFormalTemporalCurrentV1(
 sources:CoreCommerceSourceOwner,capture:CoreCommerceSourceCapture,
 semantics:CoreCommerceSemanticOwner,semantic:CoreCommerceSemanticCapture,
 binding:CommerceWorkflowCoordinationBindingV1,assembly:CommerceApplicationAssemblyV1,
 model:CoreCommerceFormalTemporalV1,
):void {
 if(!model||typeof model!=='object'||typeof model.tla!=='string'||model.tla_sha256!==sha(model.tla)||
  dataDigest(model)!==dataDigest(exportCoreCommerceFormalTemporalV1(sources,capture,semantics,semantic,binding,assembly)))
  fail('InvalidModel');
}
