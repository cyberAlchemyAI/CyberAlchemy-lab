/** Shared source API over original Core custody; source-bound component data.
 * No selected/native/early/application owner is created by this adapter.
 * Open Questions: docs/COMMERCE-STAGE-API.md#open-questions. */
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {captureJson,dataDigest} from '../profile-engine/contracts.js';
import {coreFreeze,coreSourceFail as fail,CoreCommerceSourceError} from './commerce-core-syntax.js';
import {assertCoreCommerceSourceOwner,type CoreCommerceSourceOwner,type CoreCommerceSourceCapture} from './commerce-core-source-owner.js';
import {assertCoreCommerceSemanticOwner,type CoreCommerceSemanticOwner,type CoreCommerceSemanticCapture} from './commerce-core-semantic-owner.js';
import {pinCoreImplementation} from './commerce-core-physical.js';
import {projectCoreCommerceStageData,coreCommerceValueSchema} from './commerce-core-stage-data.js';
import {createCoreCommerceComputationContract} from './commerce-core-pure-contract.js';
import type {CommerceSourceOwner,CommerceSourceHandle,CommerceSourceInspection,CommerceSemanticComponent,CommerceResult} from './commerce-stages-v1.js';
import type {ModuleContractV1,ComputationContractV1,ReadPlanV1,EffectPlanV1,WorkflowContractV1,EntryContractV1} from './commerce-data-v1.js';
const extension=path.extname(fileURLToPath(import.meta.url)),pin=pinCoreImplementation(import.meta.url,['commerce-core-stage-data'+extension,'commerce-core-physical'+extension,'commerce-core-pure-contract'+extension,'commerce-stages-v1'+extension]);
const where={path:'application.alch',start:0,end:0};
export interface CoreCommerceStageSourceOwner extends CommerceSourceOwner {moduleContracts(source:CommerceSourceHandle):readonly ModuleContractV1[]}
type State={source:CoreCommerceSourceCapture;semantic:CoreCommerceSemanticCapture;inspection:CommerceSourceInspection;projection:ReturnType<typeof projectCoreCommerceStageData>;disposed:boolean};
type Record={sources:CoreCommerceSourceOwner;semantics:CoreCommerceSemanticOwner;current:(h:CommerceSourceHandle)=>State};
const registered=new WeakMap<object,Record>();
export function assertCoreCommerceStageSourceOwner(owner:CoreCommerceStageSourceOwner):void {if(!owner||typeof owner!=='object'||!registered.has(owner))fail('ForeignOwner',where,'original Core source-stage owner factory required');}
export function createCoreCommerceStageSourceOwner(sources:CoreCommerceSourceOwner,semantics:CoreCommerceSemanticOwner):CoreCommerceStageSourceOwner {
 assertCoreCommerceSourceOwner(sources);assertCoreCommerceSemanticOwner(semantics);pin.assertCurrent();const owned=new WeakMap<object,State>();
 const current=(handle:CommerceSourceHandle)=>{const row=handle&&typeof handle==='object'?owned.get(handle):undefined;if(!row)fail('ForeignOwner',where,'original source-stage handle from this exact factory required');if(row.disposed)fail('DisposedOwner',where,'source-stage handle disposed');pin.assertCurrent();semantics.assertSource(row.semantic,row.source);return row;};
 const owner:CoreCommerceStageSourceOwner=Object.freeze({async prepare(root:string,applicationRelativePath:string){
  pin.assertCurrent();const source=sources.prepare(root,applicationRelativePath);let semantic:CoreCommerceSemanticCapture|undefined;
  try{semantic=semantics.check(source);const capture=sources.inspect(source),checked=semantics.inspect(semantic),projection=projectCoreCommerceStageData(capture,checked);
   const inspection:CommerceSourceInspection=coreFreeze({stage:'original-core-commerce-source',source_sha256:capture.capture_sha256,profile_sha256:null,native_basis_sha256:null,output_sha256:null,authority_effect:'none',application:projection.application,modules:projection.modules.map(m=>({identity:m.source,text:capture.files.find(f=>f.path===m.source.artifact.path)!.text}))});
   // The shared phantom brand is erased. The cast only types a newly minted
   // token; actual custody is its private entry and original physical parents.
   const handle=Object.freeze({kind:'original-core-commerce-stage-source/v1-candidate'}) as unknown as CommerceSourceHandle;
   owned.set(handle,{source,semantic,inspection,projection,disposed:false});current(handle);return handle;
  }catch(error){if(semantic)try{semantics.dispose(semantic);}catch{}try{sources.dispose(source);}catch{}throw error;}
 },inspect(handle:CommerceSourceHandle){return current(handle).inspection;},moduleContracts(handle:CommerceSourceHandle){return current(handle).projection.modules;},assertCurrent(handle:CommerceSourceHandle){current(handle);},dispose(handle:CommerceSourceHandle){const s=current(handle);s.disposed=true;semantics.dispose(s.semantic);sources.dispose(s.source);}});
 registered.set(owner,{sources,semantics,current});return owner;
}
export function createCoreCommerceSemanticStageComponent(owner:CoreCommerceStageSourceOwner,source:CommerceSourceHandle):CommerceSemanticComponent {
 assertCoreCommerceStageSourceOwner(owner);const record=registered.get(owner)!;record.current(source);
 const result=<T>(run:()=>T):CommerceResult<T>=>{try{return coreFreeze({ok:true,value:run()});}catch(error){if(error instanceof CoreCommerceSourceError)return coreFreeze({ok:false,diagnostics:error.diagnostics});return coreFreeze({ok:false,diagnostics:[{code:'InvalidContract',...where,message:'inert exact source-corresponding component data required'}]});}};
 const exact=<T>(proposed:unknown,actual:T):T=>{if(dataDigest(proposed)!==dataDigest(actual))fail('InvalidContract',where,'component data differs from original independently checked source');return actual;};
 const inspected=()=>{const s=record.current(source);return {s,semantic:record.semantics.inspect(s.semantic)};};
 const role=<T extends ReadPlanV1|EffectPlanV1|WorkflowContractV1>(proposal:T,key:'query'|'operation'|'workflow',rows:readonly T[]):T=>{
  const p=captureJson(proposal) as any,selector=p?.[key];if(!selector||typeof selector.module!=='string'||typeof selector.name!=='string')fail('InvalidContract',where,'exact closed source selector required');
  const actual=rows.find(r=>dataDigest((r as any)[key])===dataDigest(selector));if(!actual)fail('UnknownReference',where,'role not in original checked source closure');return exact(p,actual);
 };
 return Object.freeze({
  checkModule(module:ModuleContractV1,closure:readonly ModuleContractV1[]){return result(()=>{const {s}=inspected(),p=captureJson(module) as any,c=captureJson(closure) as unknown as ModuleContractV1[];if(!Array.isArray(c)||c.some(m=>!m?.source||typeof m.source.module!=='string'))fail('InvalidContract',where,'complete source module contract closure required');
   const sorted=(rows:readonly ModuleContractV1[])=>[...rows].sort((a,b)=>a.source.module<b.source.module?-1:a.source.module>b.source.module?1:0);exact(sorted(c),sorted(s.projection.modules));const actual=s.projection.modules.find(m=>m.source.module===p?.source?.module);if(!actual)fail('UnknownReference',where,'module not in original source closure');return exact(p,actual);});},
  checkComputation(contract:ComputationContractV1){return result(()=>{const {s}=inspected(),p=captureJson(contract) as any;if(typeof p?.source_node!=='string')fail('InvalidContract',where,'exact pure source declaration required');if(!s.projection.limits)fail('MissingMapping',where,'computation checking requires explicit captured computation-bounds');const captured=record.sources.inspect(s.source),paths=new Set(captured.reconstruction.modules.map(m=>m.path));return exact(p,createCoreCommerceComputationContract(captured.files.filter(f=>paths.has(f.path)),p.source_node,s.projection.limits));});},
  checkRead(plan:ReadPlanV1,values:Parameters<CommerceSemanticComponent['checkRead']>[1]){return result(()=>{const {semantic}=inspected(),actual=role(plan,'query',semantic.reads);exact(values,coreCommerceValueSchema(semantic.pure,actual.output));return actual;});},
  checkEffects(plan:EffectPlanV1,values:Parameters<CommerceSemanticComponent['checkEffects']>[1]){return result(()=>{const {semantic}=inspected(),actual=role(plan,'operation',semantic.effects);exact(values,coreCommerceValueSchema(semantic.pure,actual.result));return actual;});},
  checkWorkflow(plan:WorkflowContractV1,entries:readonly EntryContractV1[]){return result(()=>{const {semantic}=inspected(),actual=role(plan,'workflow',semantic.workflows);exact(entries,semantic.entries);return actual;});},
 });
}
