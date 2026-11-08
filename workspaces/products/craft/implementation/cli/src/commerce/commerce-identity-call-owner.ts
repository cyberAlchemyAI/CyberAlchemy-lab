/** Original native observation source bindings; no invocation/auth/commit owner.
 * Open Questions: docs/COMMERCE-NATIVE-IDENTITY.md#open-questions. */
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {types as host} from 'node:util';
import {captureJson,dataDigest} from '../profile-engine/contracts.js';
import {coreFreeze,coreSourceFail as fail} from './commerce-core-syntax.js';
import {pinCoreImplementation} from './commerce-core-physical.js';
import {assertCoreCommerceSourceOwner,type CoreCommerceSourceOwner,type CoreCommerceSourceCapture} from './commerce-core-source-owner.js';
import {assertCoreCommerceStageSourceOwner,createCoreCommerceSemanticStageComponent,type CoreCommerceStageSourceOwner} from './commerce-core-stage-owner.js';
import {assertCommerceComputationDomainOwner,type CommerceComputationDomainOwner,type CommerceComputationDomainHandle} from './commerce-computation-domain.js';
import {createCoreContextCatalog} from './commerce-core-context.js';
import {createCoreValueTypes} from './commerce-core-types.js';
import {coreValueAstType} from './commerce-core-pure.js';
import type {CommerceSourceHandle} from './commerce-stages-v1.js';
import type {EffectPlanV1,WorkflowContractV1,FlowExprV1,ValueTypeV1,SourceIdentityV1,SourceSpanV1} from './commerce-data-v1.js';
const ext=path.extname(fileURLToPath(import.meta.url)),pin=pinCoreImplementation(import.meta.url,['commerce-core-source-owner'+ext,'commerce-core-stage-owner'+ext,'commerce-core-context'+ext,'commerce-core-types'+ext,'commerce-core-pure'+ext,'commerce-computation-domain'+ext,'../profile-engine/contracts'+ext]),where={path:'application.alch',start:0,end:0};
export type CommerceIdentityRole=EffectPlanV1|WorkflowContractV1;
type Observation=Extract<FlowExprV1,{op:'native_observation'}>;
export interface CommerceIdentityCallHandle {readonly kind:'original-commerce-identity-source-call/v1-candidate'}
export interface CommerceIdentityCallInspection {
 readonly kind:'commerce-source-identity-call/v1-candidate';readonly key:string;readonly caller:string;readonly service:string;
 readonly source:SourceIdentityV1;readonly span:SourceSpanV1;readonly source_capture_sha256:string;readonly role_sha256:string;readonly expression_path:string;
 readonly observation:Observation;readonly signature:Readonly<Record<string,unknown>>;
 readonly parameters:readonly {readonly name:string;readonly type:ValueTypeV1;readonly finite:readonly string[]|null;readonly literal:Extract<FlowExprV1,{op:'literal'}>|null}[];
 readonly event_schema:{readonly name:string;readonly version:1}|null;readonly event_targets:readonly {readonly name:string;readonly version:1}[];
 readonly code_epoch_sha256:string;readonly qualification:'source-native-observation-component-only;not-operation-invocation-or-private-identity-context';readonly authority_effect:'none';
}
export interface CommerceIdentityCallOwner {
 paths(plan:CommerceIdentityRole):readonly string[];bind(plan:CommerceIdentityRole,expressionPath:string):CommerceIdentityCallHandle;
 inspect(handle:CommerceIdentityCallHandle):CommerceIdentityCallInspection;assertCurrent(handle:CommerceIdentityCallHandle):void;dispose(handle:CommerceIdentityCallHandle):void;
 inspectMany(handles:readonly CommerceIdentityCallHandle[]):readonly CommerceIdentityCallInspection[];
 assertCurrentSet(handles:readonly CommerceIdentityCallHandle[]):void;
 sourceDomain():ReturnType<CommerceComputationDomainOwner['inspect']>;
}
const registered=new WeakSet<object>();
export function assertCommerceIdentityCallOwner(owner:CommerceIdentityCallOwner):void{if(!owner||typeof owner!=='object'||!registered.has(owner))fail('ForeignOwner',where,'original identity source-call owner required');}
function layout(plan:CommerceIdentityRole){
 const found:{path:string;node:Observation;binding:string|null}[]=[];let nodes=0;
 const walk=(v:any,p:string,binding:string|null,depth:number)=>{if(!v||typeof v!=='object')return;if(++nodes>65536||depth>128)fail('ResourceLimit',where,'bounded native source layout required');
  if(v.op==='native_observation'&&v.abi==='craft.commerce-identity/v1-candidate')found.push({path:p,node:v,binding});
  if(Array.isArray(v))v.forEach((x,i)=>walk(x,p+'['+i+']',binding,depth+1));else for(const [name,x]of Object.entries(v))walk(x,p+'.'+name,v.kind==='let'&&name==='value'?v.name:binding,depth+1);
 };walk(plan,'$',null,0);return found;
}
export function createCommerceIdentityCallOwner(sources:CoreCommerceSourceOwner,capture:CoreCommerceSourceCapture,stage:CoreCommerceStageSourceOwner,source:CommerceSourceHandle,domain:CommerceComputationDomainOwner,baseline:CommerceComputationDomainHandle):CommerceIdentityCallOwner {
 assertCoreCommerceSourceOwner(sources);assertCoreCommerceStageSourceOwner(stage);assertCommerceComputationDomainOwner(domain);sources.assertCurrent(capture);stage.assertCurrent(source);domain.assertCurrent(baseline);pin.assertCurrent();
 const original=sources.inspect(capture),parent=stage.inspect(source),checkedDomain=domain.inspect(baseline);if(original.capture_sha256!==parent.source_sha256||parent.source_sha256!==checkedDomain.source_capture_sha256)fail('ForeignOwner',where,'all genuine original parents must capture the same current source');
 const types=createCoreValueTypes(original.reconstruction),catalog=createCoreContextCatalog(types,original.files.filter(f=>f.path.endsWith('.json'))),component=createCoreCommerceSemanticStageComponent(stage,source),owned=new WeakMap<object,{inspection:CommerceIdentityCallInspection;disposed:boolean}>();
 const currentParents=()=>{pin.assertCurrent();sources.assertCurrent(capture);stage.assertCurrent(source);domain.assertCurrent(baseline);};
 const checked=(proposal:CommerceIdentityRole):CommerceIdentityRole=>{currentParents();const plan=captureJson(proposal) as unknown as CommerceIdentityRole;
  const result=plan.schema_version==='craft.commerce-effects/v1-candidate'?component.checkEffects(plan,{...checkedDomain.contract.values,root:plan.result}):plan.schema_version==='craft.commerce-workflow/v1-candidate'?component.checkWorkflow(plan,stage.moduleContracts(source).flatMap(m=>m.entries)):null;
  if(!result)fail('InvalidContract',where,'original Operation or Workflow plan required');if(!result.ok){const d=result.diagnostics[0]!;fail(d.code,d,d.message);}return result.value;
 };
 const current=(h:CommerceIdentityCallHandle)=>{const row=h&&typeof h==='object'?owned.get(h):undefined;if(!row)fail('ForeignOwner',where,'identity source-call token from this exact factory required');if(row.disposed)fail('DisposedOwner',where,'identity source-call disposed');currentParents();return row;};
 const currentSet=(handles:readonly CommerceIdentityCallHandle[])=>{
  if(host.isProxy(handles)||!Array.isArray(handles)||Object.getPrototypeOf(handles)!==Array.prototype)fail('InvalidContract',where,'inert source-call token collection required');const n=Object.getOwnPropertyDescriptor(handles,'length')!.value;if(n>256||Reflect.ownKeys(handles).length!==n+1)fail('InvalidContract',where,'bounded dense source-call token collection required');
  const rows:{inspection:CommerceIdentityCallInspection;disposed:boolean}[]=[];for(let i=0;i<n;i++){const d=Object.getOwnPropertyDescriptor(handles,String(i));if(!d||!d.enumerable||!Object.hasOwn(d,'value'))fail('InvalidContract',where,'inert source-call collection required');const h=d.value,row=h&&typeof h==='object'?owned.get(h):undefined;if(!row)fail('ForeignOwner',where,'every source-call token must belong to this exact factory');if(row.disposed)fail('DisposedOwner',where,'source-call collection contains a disposed token');rows.push(row);}
  // All rows belong to this factory's same immutable original parent closure.
  // Check that closure once, while retaining each token/revocation check.
  currentParents();return rows;
 };
 const owner:CommerceIdentityCallOwner=Object.freeze({paths(proposal:CommerceIdentityRole){return coreFreeze(layout(checked(proposal)).map(x=>x.path));},bind(proposal:CommerceIdentityRole,expressionPath:string){
  const plan=checked(proposal);if(typeof expressionPath!=='string'||expressionPath.length>8192)fail('InvalidContract',where,'bounded original native expression path required');const row=layout(plan).find(x=>x.path===expressionPath);if(!row)fail('UnknownReference',where,'original identity native observation required');
  const selector='operation'in plan?plan.operation:plan.workflow,module=stage.moduleContracts(source).find(m=>m.source.module===selector.module),declaration=module?.declarations.find(d=>dataDigest(d.selector)===dataDigest(selector));if(!module||!declaration||!plan.service)fail('UnknownReference',where,'original service-owned caller required');
  const contextDecl=types.declarations.get(row.node.source_type);if(!contextDecl)fail('UnknownReference',where,'original source context declaration required');const context=catalog.require(contextDecl),signature=context.methods.get(row.node.method);if(!signature||context.abi!=='craft.commerce-identity/v1-candidate'||signature.parameters.length!==row.node.arguments.length)fail('UnsupportedCapability',where,'exact identity native ABI/signature required');
  const typeOf=(v:FlowExprV1):ValueTypeV1=>{
   if(v.op==='var'){const b=plan.parameters.find(p=>p.name===v.name);if(b)return b.type;}
   if(v.op==='field'){const t=typeOf(v.value);if(t.kind==='record'){const r=checkedDomain.contract.values.records.find(r=>r.name===t.name),f=r?.fields[v.field];if(f)return f;}}
   if(v.op==='literal')return v.type;if(v.op==='record')return {kind:'record',name:v.type_name};if(v.op==='call'){const f=checkedDomain.contract.functions.find(f=>f.name===v.declaration);if(f)return f.result;}
   return fail('UnsupportedCapability',where,'selected Event argument requires a source-resolved value type;no caller-supplied schema');
  };
  let event_schema:CommerceIdentityCallInspection['event_schema']=null;
  const parameters=signature.parameters.map((p,i)=>{const annotation=catalog.annotation(p.annotation,context,where,signature),argument=row.node.arguments[i]!;let type:ValueTypeV1;
   if(annotation.kind==='selected-event'){type=typeOf(argument.value);const resolved=type,r=resolved.kind==='record'?checkedDomain.contract.values.records.find(r=>r.name===resolved.name):null;if(!r||r.role!=='Event'||r.event_version!==1||!r.name.startsWith(annotation.module+'.'))fail('UnsupportedCapability',where,'exact declared Event@1 argument required');event_schema={name:r.name,version:1};}
   else type=coreValueAstType(annotation.type);
   if(p.name!==argument.parameter||p.name===null)fail('InvalidContract',where,'named source native argument order required');return {name:p.name,type,finite:annotation.kind==='finite-text'?annotation.values:null,literal:argument.value.op==='literal'?argument.value:null};
  });
  const event_targets:{name:string;version:1}[]=[];
  if(row.node.method==='eventMetadata'){
   if(!row.binding)fail('UnsupportedCapability',where,'event metadata must retain its original source binding');
   const visit=(v:any)=>{if(!v||typeof v!=='object')return;if(v.kind==='mutation'&&v.operation==='record-event'&&v.fields.some((f:any)=>f.name==='metadata'&&f.value.expression.op==='var'&&f.value.expression.name===row.binding)){const event=checkedDomain.contract.values.records.find(r=>r.name===v.target);if(!event||event.role!=='Event'||event.event_version!==1)fail('InvalidContract',where,'metadata consumer must be a checked Event@1');if(!event_targets.some(e=>e.name===event.name))event_targets.push({name:event.name,version:1});}for(const x of Object.values(v))if(x&&typeof x==='object')visit(x);};visit(plan);
   if(!event_targets.length)fail('UnsupportedCapability',where,'metadata has no checked original Event producer use');
   if(parameters[0]?.literal?.value!==plan.service)fail('InvalidContract',where,'event producer must equal actual source target service');
  }
  const subject={kind:'commerce-source-identity-call/v1-candidate' as const,caller:selector.module+'.'+selector.name,service:plan.service,source:module.source,span:declaration.span,source_capture_sha256:parent.source_sha256,role_sha256:dataDigest(plan),expression_path:expressionPath,observation:row.node,signature:signature.raw,parameters,event_schema,event_targets,code_epoch_sha256:pin.sha256,qualification:'source-native-observation-component-only;not-operation-invocation-or-private-identity-context' as const,authority_effect:'none' as const};
  const inspection:CommerceIdentityCallInspection=coreFreeze({...subject,key:dataDigest(subject)}),h=Object.freeze({kind:'original-commerce-identity-source-call/v1-candidate' as const});owned.set(h,{inspection,disposed:false});current(h);return h;
 },inspect(h:CommerceIdentityCallHandle){return current(h).inspection;},inspectMany(handles:readonly CommerceIdentityCallHandle[]){return Object.freeze(currentSet(handles).map(r=>r.inspection));},assertCurrentSet(handles:readonly CommerceIdentityCallHandle[]){currentSet(handles);},assertCurrent(h:CommerceIdentityCallHandle){current(h);},dispose(h:CommerceIdentityCallHandle){current(h).disposed=true;},sourceDomain(){currentParents();return domain.inspect(baseline);}});registered.add(owner);return owner;
}
