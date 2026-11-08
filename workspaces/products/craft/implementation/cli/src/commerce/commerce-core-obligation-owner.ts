/** Original source/semantic correspondence, not runtime or formal proof.
 * Open Questions: docs/COMMERCE-OBLIGATIONS.md#open-questions. */
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {dataDigest} from '../profile-engine/contracts.js';
import {coreFreeze,coreSourceFail as fail,coreSourceDescendants,type CoreSourceRange} from './commerce-core-syntax.js';
import {assertCoreCommerceSourceOwner,type CoreCommerceSourceOwner,type CoreCommerceSourceCapture} from './commerce-core-source-owner.js';
import {assertCoreCommerceSemanticOwner,type CoreCommerceSemanticOwner,type CoreCommerceSemanticCapture} from './commerce-core-semantic-owner.js';
import {pinCoreImplementation} from './commerce-core-physical.js';
import type {CoreCommerceDeclaration,CoreCommerceReconstruction} from './commerce-core-reconstruction.js';
const extension=path.extname(fileURLToPath(import.meta.url));
const pin=pinCoreImplementation(import.meta.url,['commerce-core-physical'+extension,'commerce-core-interface-semantics'+extension,'../profile-engine/contracts'+extension]);
const where={path:'application.alch',start:0,end:0};
export interface CoreCommerceObligationCapture {readonly kind:'original-core-commerce-obligation-capture/v1-candidate'}
export interface CoreCheckedSourceObligation {
 readonly id:string;readonly declaration:string;readonly kind:string;readonly span:CoreSourceRange;
 readonly checker:'pure-source'|'value-source'|'read-source'|'effect-source'|'workflow-source'|'entry-source'|'interface-source';
 readonly correspondence:'typed-declaration-check-covers-source-subtree'|'exact-interface-clause-source-check';
 readonly status:'source-statically-checked';readonly runtime_qualified:false;
}
export interface CoreCommerceObligationInspection {
 readonly kind:'core-commerce-obligation-inspection/v1-candidate';readonly application:string;
 readonly source_capture_sha256:string;readonly semantic_code_epoch_sha256:string;readonly obligation_code_epoch_sha256:string;
 readonly executable_sha256:string;readonly assurance_sha256:string;
 readonly services:CoreCommerceReconstruction['services'];readonly ownership:CoreCommerceReconstruction['ownership'];
 readonly source_checks:readonly CoreCheckedSourceObligation[];
 readonly implementation_requirements:readonly {readonly declaration:string;readonly task:string;readonly status:'required-not-witnessed-by-source-accounting'}[];
 readonly counts:Readonly<{declarations:number;optional_claims:number;source_obligations:number;implementation_requirements:number}>;
 readonly qualification:'source-correspondence-only;no-runtime-formal-proof-or-task-completion';readonly runtime_qualified:false;readonly authority_effect:'none';
}
export interface CoreCommerceObligationOwner {
 prepare(source:CoreCommerceSourceCapture,semantic:CoreCommerceSemanticCapture):CoreCommerceObligationCapture;
 inspect(handle:CoreCommerceObligationCapture):CoreCommerceObligationInspection;
 assertCurrent(handle:CoreCommerceObligationCapture):void;
 assertProposal(handle:CoreCommerceObligationCapture,proposal:unknown):void;
 dispose(handle:CoreCommerceObligationCapture):void;
}
const registries=new WeakSet<object>();
export function assertCoreCommerceObligationOwner(owner:CoreCommerceObligationOwner):void {
 if(!owner||typeof owner!=='object'||!registries.has(owner))fail('ForeignOwner',where,'original obligation owner required');
}
// These are original plan follow-on assignments, not evidence that those tasks
// have or have not completed elsewhere. This owner witnesses static source only.
function followOn(d:CoreCommerceDeclaration):readonly string[]{
 switch(d.surface){
  case'Rule':case'Calculation':case'Mapping':case'Policy':case'StateMachine':return ['EC08','EC13'];
  case'Entity':return ['EC09','EC15','EC17'];
  case'ValueObject':case'Enum':return ['EC09'];
  case'Event':return ['EC09','EC29','EC30'];
  case'Query':return ['EC15','EC16','EC20'];
  case'Operation':return ['EC15','EC17','EC18'];
  case'Workflow':return ['EC28','EC29','EC30'];
  case'Entry':return ['EC21','EC22','EC23'];
  case'FormalClaim':return [];
  default:return [];
 }
}
export function createCoreCommerceObligationOwner(sources:CoreCommerceSourceOwner,semantics:CoreCommerceSemanticOwner):CoreCommerceObligationOwner {
 assertCoreCommerceSourceOwner(sources);assertCoreCommerceSemanticOwner(semantics);pin.assertCurrent();
 const owned=new WeakMap<object,{source:CoreCommerceSourceCapture;semantic:CoreCommerceSemanticCapture;inspection:CoreCommerceObligationInspection;disposed:boolean}>();
 const state=(handle:CoreCommerceObligationCapture)=>{
  const row=handle&&typeof handle==='object'?owned.get(handle):undefined;
  if(!row)fail('ForeignOwner',where,'original obligation handle from this exact owner required');
  if(row.disposed)fail('DisposedOwner',where,'obligation handle disposed');
  pin.assertCurrent();sources.assertCurrent(row.source);semantics.assertSource(row.semantic,row.source);return row;
 };
 const owner:CoreCommerceObligationOwner=Object.freeze({
  prepare(source:CoreCommerceSourceCapture,semantic:CoreCommerceSemanticCapture){
   pin.assertCurrent();semantics.assertSource(semantic,source);const original=sources.inspect(source),checked=semantics.inspect(semantic),model=original.reconstruction;
   if(checked.source_capture_sha256!==original.capture_sha256||dataDigest(model.ownership)!==dataDigest(checked.ownership))fail('InvalidContract',where,'exact original source and semantic ownership must correspond');
   const declarations=new Map(model.modules.flatMap(m=>m.declarations.map(d=>[d.id,d] as const)));
   const checkers=new Map<string,CoreCheckedSourceObligation['checker']>();
   const add=(name:string,checker:CoreCheckedSourceObligation['checker'])=>{if(!declarations.has(name)||checkers.has(name))fail('InvalidContract',where,'checked declaration correspondence must be unique and exact');checkers.set(name,checker);};
   for(const d of checked.pure.declarations)add(d.name,'pure-source');
   for(const d of checked.pure.value_declarations)add(d.name,'value-source');
   for(const d of checked.pure.source_refinements)add(d.name,'value-source');
   for(const d of checked.reads)add(d.query.module+'.'+d.query.name,'read-source');
   for(const d of checked.effects)add(d.operation.module+'.'+d.operation.name,'effect-source');
   for(const d of checked.workflows)add(d.workflow.module+'.'+d.workflow.name,'workflow-source');
   for(const d of checked.entries)add(d.id,'entry-source');
   for(const d of checked.interfaces)add(d.name,'interface-source');
   const executable=[...declarations.values()].filter(d=>d.surface!=='FormalClaim');
   if(checkers.size!==executable.length||executable.some(d=>!checkers.has(d.id)))fail('MissingMapping',where,'every executable declaration needs an actual semantic checker');
   const source_checks:CoreCheckedSourceObligation[]=[],seen=new Set<string>();
   for(const obligation of model.obligations){
    const d=declarations.get(obligation.declaration)!,s=obligation.span;
    if(!d||seen.has(obligation.id))fail('InvalidContract',s,'unique original source obligation required');seen.add(obligation.id);
    const matches=coreSourceDescendants(d.syntax,obligation.kind).filter(n=>n.rule===obligation.kind&&n.path===s.path&&n.start===s.start&&n.end===s.end);
    // The traversal includes the root. Comparing identity, role and exact source
    // span avoids accepting a same-shaped expression from another declaration.
    if(matches.length!==1||obligation.id!==d.id+'#'+obligation.kind+':'+s.start+':'+s.end)fail('InvalidContract',s,'obligation must correspond to one exact original syntax node');
    if(obligation.kind==='interface-clause'){
     const rows=checked.interfaces.find(i=>i.name===d.id)!.clauses.filter(c=>c.span.path===s.path&&c.span.start===s.start&&c.span.end===s.end);
     if(rows.length!==1)fail('MissingMapping',s,'exact eagerly checked Interface clause required');
    }
    source_checks.push({id:obligation.id,declaration:d.id,kind:obligation.kind,span:s,checker:checkers.get(d.id)!,correspondence:obligation.kind==='interface-clause'?'exact-interface-clause-source-check':'typed-declaration-check-covers-source-subtree',status:'source-statically-checked',runtime_qualified:false});
   }
   const implementation_requirements=executable.flatMap(d=>{
    const tasks=d.surface==='Interface'?checked.interfaces.find(i=>i.name===d.id)!.implementation_tasks:d.surface==='Entry'&&checked.entries.find(e=>e.id===d.id)!.interaction==='event'?['EC21','EC22','EC29','EC30']:followOn(d);
    return [...new Set(tasks)].map(task=>({declaration:d.id,task,status:'required-not-witnessed-by-source-accounting' as const}));
   });
   const inspection:CoreCommerceObligationInspection=coreFreeze({kind:'core-commerce-obligation-inspection/v1-candidate',application:checked.application,source_capture_sha256:original.capture_sha256,semantic_code_epoch_sha256:checked.semantic_code_epoch_sha256,obligation_code_epoch_sha256:pin.sha256,executable_sha256:checked.executable_sha256,assurance_sha256:checked.assurance_sha256,services:model.services,ownership:model.ownership,source_checks,implementation_requirements,counts:{declarations:executable.length,optional_claims:declarations.size-executable.length,source_obligations:source_checks.length,implementation_requirements:implementation_requirements.length},qualification:'source-correspondence-only;no-runtime-formal-proof-or-task-completion',runtime_qualified:false,authority_effect:'none'});
   const handle=Object.freeze({kind:'original-core-commerce-obligation-capture/v1-candidate' as const});owned.set(handle,{source,semantic,inspection,disposed:false});state(handle);return handle;
  },
  inspect(handle:CoreCommerceObligationCapture){return state(handle).inspection;},
  assertCurrent(handle:CoreCommerceObligationCapture){state(handle);},
  assertProposal(handle:CoreCommerceObligationCapture,proposal:unknown){const expected=state(handle).inspection;if(dataDigest(proposal)!==dataDigest(expected))fail('InvalidContract',where,'proposal must exactly match original checked correspondence; display data cannot restore custody');},
  dispose(handle:CoreCommerceObligationCapture){state(handle).disposed=true;},
 });registries.add(owner);return owner;
}
