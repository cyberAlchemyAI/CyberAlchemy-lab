/** Original Commerce DemoPay callsite binding only. No port, dispatch permit,
 * provider observation, or native basis is issued here.
 * Open Questions: docs/COMMERCE-NATIVE-V1.md#open-questions. */
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {dataDigest} from '../profile-engine/contracts.js';
import {pinCoreImplementation} from './commerce-core-physical.js';
import {assertCoreCommerceSourceOwner,type CoreCommerceSourceOwner,type CoreCommerceSourceCapture} from './commerce-core-source-owner.js';
import {assertCoreCommerceSemanticOwner,type CoreCommerceSemanticOwner,type CoreCommerceSemanticCapture} from './commerce-core-semantic-owner.js';
import {assertCoreCommerceStageSourceOwner,type CoreCommerceStageSourceOwner} from './commerce-core-stage-owner.js';
import {assertCommerceLocalPlanOwnerV1,type CommerceLocalPlanOwnerV1,type CommerceLocalOperationHandleV1} from './commerce-local-plan-owner-v1.js';
import {assertCommerceBindingAssemblyOwnerV1,type CommerceBindingAssemblyOwnerV1} from './commerce-binding-assembly-v1.js';
import {assertCommerceSourceInvocationOwnerV1,type CommerceSourceInvocationOwnerV1} from './commerce-source-invocation-owner-v1.js';
import type {CommerceBindingAssemblyHandle,CommerceSourceHandle,CommerceOperationInvocationHandle} from './commerce-stages-v1.js';
import type {OperationCallV1} from './commerce-data-v1.js';

const ext=path.extname(fileURLToPath(import.meta.url));
const pin=pinCoreImplementation(import.meta.url,['commerce-core-physical'+ext,'commerce-core-source-owner'+ext,'commerce-core-semantic-owner'+ext,'commerce-core-stage-owner'+ext,'commerce-local-plan-owner-v1'+ext,'commerce-binding-assembly-v1'+ext,'commerce-source-invocation-owner-v1'+ext,'../profile-engine/contracts'+ext]);
export class CommerceDemoPaySourceSiteErrorV1 extends Error {constructor(readonly code:string){super(code);this.name='CommerceDemoPaySourceSiteErrorV1';}}
const bad=(code:string):never=>{throw new CommerceDemoPaySourceSiteErrorV1(code);};
export interface CommerceDemoPaySourceSiteV1 {readonly kind:'original-commerce-demopay-source-site/v1-candidate'}
export interface CommerceDemoPaySourceSiteInspectionV1 {
 readonly parent_operation:string;readonly service:'payments';readonly source_path:string;
 readonly target:'Shop.DemoPay.Capture'|'Shop.DemoPay.InspectCapture';readonly method:'Capture'|'InspectCapture';
 readonly interface_ref:'Shop.DemoPay.PaymentProvider';readonly protocol_id:'DemoPay-v1';
 readonly binding_path:string;readonly binding_sha256:string;readonly source_capture_sha256:string;
 readonly selected_family_sha256:string;readonly parent_plan_sha256:string;
 readonly qualification:'original-source-profile-remote-site-only;no-invocation-frame-intent-port-or-provider-effect';readonly authority_effect:'none';
}
export interface CommerceDemoPaySourceSiteOwnerV1 {
 paths(parent:CommerceLocalOperationHandleV1):readonly string[];
 bind(parent:CommerceLocalOperationHandleV1,sourcePath:string):CommerceDemoPaySourceSiteV1;
 inspect(site:CommerceDemoPaySourceSiteV1):CommerceDemoPaySourceSiteInspectionV1;
 assertInvocation(site:CommerceDemoPaySourceSiteV1,owner:CommerceSourceInvocationOwnerV1,invocation:CommerceOperationInvocationHandle):void;
 assertCurrent():void;dispose():void;
}
type Site={parent:CommerceLocalOperationHandleV1;view:CommerceDemoPaySourceSiteInspectionV1};
const owners=new WeakSet<object>();
export function assertCommerceDemoPaySourceSiteOwnerV1(owner:CommerceDemoPaySourceSiteOwnerV1):void {if(!owner||typeof owner!=='object'||!owners.has(owner))bad('ForeignOwner');owner.assertCurrent();}

export function createCommerceDemoPaySourceSiteOwnerV1(
 sources:CoreCommerceSourceOwner,capture:CoreCommerceSourceCapture,
 semantics:CoreCommerceSemanticOwner,semantic:CoreCommerceSemanticCapture,
 stage:CoreCommerceStageSourceOwner,source:CommerceSourceHandle,
 plans:CommerceLocalPlanOwnerV1,
 assemblies:CommerceBindingAssemblyOwnerV1,assembly:CommerceBindingAssemblyHandle,
):CommerceDemoPaySourceSiteOwnerV1 {
 assertCoreCommerceSourceOwner(sources);assertCoreCommerceSemanticOwner(semantics);
 assertCoreCommerceStageSourceOwner(stage);assertCommerceLocalPlanOwnerV1(plans);
 assertCommerceBindingAssemblyOwnerV1(assemblies);pin.assertCurrent();semantics.assertSource(semantic,capture);
 const captured=sources.inspect(capture),checked=semantics.inspect(semantic),staged=stage.inspect(source),selected=assemblies.inspect(assembly);
 if(captured.capture_sha256!==checked.source_capture_sha256||captured.capture_sha256!==staged.source_sha256||captured.capture_sha256!==selected.selection.source_capture_sha256)bad('ForeignSource');
 if(!selected.selection.native_requirements.some(r=>r.primitive_id==='demo-pay-v1'&&r.abi==='craft.demopay-client/v1-candidate'))bad('UnsupportedFamily');
 const iface=checked.interfaces.find(i=>i.name==='Shop.DemoPay.PaymentProvider'&&i.kind==='external')??bad('MissingProviderInterface');
 const binding='profiles/demopay-wire.json';
 if(!iface.dependencies.includes(binding))bad('ForeignBinding');
 const file=captured.files.find(f=>f.path===binding)??bad('ForeignBinding');
 const effect=checked.effects.find(e=>e.operation.module+'.'+e.operation.name==='Shop.DemoPay.Capture');
 const query=checked.reads.find(r=>r.query.module+'.'+r.query.name==='Shop.DemoPay.InspectCapture');
 if(!effect||effect.protocol?.kind!=='native-capture'||effect.protocol.interface!==iface.name||effect.protocol.binding_path!==binding||effect.protocol.invocation!=='requires-original-external-producer'||!query||query.kind!=='native-protocol'||query.interface!==iface.name||query.method!=='InspectCapture'||query.protocol!=='DemoPay-v1'||query.binding_path!==binding)bad('ProtocolMismatch');
 const bindingData=JSON.parse(file.text) as {schema_version?:string;protocol?:string;source_module?:string};
 if(bindingData.schema_version!=='craft.demopay-wire/v1-candidate'||bindingData.protocol!=='DemoPay-v1'||bindingData.source_module!=='Shop.DemoPay@1')bad('ProtocolMismatch');
 let disposed=false;const sites=new WeakMap<object,Site>();
 const current=()=>{if(disposed)bad('DisposedOwner');pin.assertCurrent();sources.assertCurrent(capture);semantics.assertSource(semantic,capture);stage.assertCurrent(source);plans.assertCurrent();assemblies.assertCurrent(assembly);};
 const calls=(parent:CommerceLocalOperationHandleV1)=>{
  current();const op=plans.inspectOperation(parent);
  if(op.source_capture_sha256!==captured.capture_sha256||op.plan.service!=='payments')bad('ForeignParent');
  const out:{path:string;call:OperationCallV1}[]=[];let visited=0;
  const walk=(value:unknown,p:string,depth:number):void=>{
   if(++visited>65536||depth>128||p.length>8192)bad('SourceBound');
   if(!value||typeof value!=='object')return;
   if(Array.isArray(value)){value.forEach((v,i)=>walk(v,p+'['+i+']',depth+1));return;}
   for(const [key,v] of Object.entries(value)){
    const at=p+'.'+key;
    if(key==='call'&&v&&typeof v==='object'&&'target'in v&&'role'in v){
     const call=v as OperationCallV1;
     if(call.entry===null&&call.authorization==='original-local-context-forwarding-required'&&
       (call.target==='Shop.DemoPay.Capture'&&call.role==='Operation'||call.target==='Shop.DemoPay.InspectCapture'&&call.role==='Query'))out.push({path:at,call});
    }
    walk(v,at,depth+1);
   }
  };
  walk(op.plan,'$',0);return {op,out};
 };
 const owned=(site:CommerceDemoPaySourceSiteV1):Site=>{current();const row=site&&typeof site==='object'?sites.get(site):undefined;if(!row)bad('ForeignSite');const present=row!;const {op,out}=calls(present.parent);if(op.plan_sha256!==present.view.parent_plan_sha256||!out.some(x=>x.path===present.view.source_path&&x.call.target===present.view.target))bad('StaleSite');return present;};
 const implementation:CommerceDemoPaySourceSiteOwnerV1={
  paths(parent){return Object.freeze(calls(parent).out.map(x=>x.path));},
  bind(parent,sourcePath){const {op,out}=calls(parent),found=out.find(x=>x.path===sourcePath);if(!found)bad('UnknownSourceSite');const selectedCall=found!;
   const method=selectedCall.call.target==='Shop.DemoPay.Capture'?'Capture':'InspectCapture';
   const target=method==='Capture'?effect:query;
   if(!target||dataDigest(selectedCall.call.result)!==dataDigest(method==='Capture'?effect!.result:query!.output)||selectedCall.call.arguments.length!==target.parameters.length||selectedCall.call.arguments.some((a,i)=>a.parameter!==target.parameters[i]!.name))bad('ProtocolMismatch');
   const view:CommerceDemoPaySourceSiteInspectionV1=Object.freeze({parent_operation:op.operation,service:'payments',source_path:sourcePath,target:selectedCall.call.target as CommerceDemoPaySourceSiteInspectionV1['target'],method,interface_ref:'Shop.DemoPay.PaymentProvider',protocol_id:'DemoPay-v1',binding_path:binding,binding_sha256:file.sha256,source_capture_sha256:captured.capture_sha256,selected_family_sha256:selected.selected_family_sha256,parent_plan_sha256:op.plan_sha256,qualification:'original-source-profile-remote-site-only;no-invocation-frame-intent-port-or-provider-effect',authority_effect:'none'});
   const h=Object.freeze({kind:'original-commerce-demopay-source-site/v1-candidate' as const});sites.set(h,{parent,view});return h;
  },
  inspect(site){return owned(site).view;},
  assertInvocation(site,invocations,invocation){const row=owned(site);assertCommerceSourceInvocationOwnerV1(invocations);invocations.assertTarget(invocation,plans,row.view.source_capture_sha256,row.view.parent_operation);},
  assertCurrent:current,dispose(){disposed=true;},
 };const owner=Object.freeze(implementation);owners.add(owner);current();return owner;
}
