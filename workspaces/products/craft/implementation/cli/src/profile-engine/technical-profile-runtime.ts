/** Finite checked profile-runtime join. Installation is trusted native/operator
 * code, like the existing native-host configure seam. Remote callers provide
 * actor/input only; observations and decisions never come from remote metadata.
 * Original action owners retain Auth, disclosure, effects and settlement.
 * Open Questions: docs/TECHNICAL-PROFILE-SOURCE.md#open-questions.
 */
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {pinCoreImplementation} from '../commerce/commerce-core-physical.js';
import {captureJson} from './contracts.js';
import {coreSha256} from '../commerce/commerce-core-syntax.js';
import {assertTechnicalProfileSourceOwner,type CheckedTechnicalProfileSource,createTechnicalProfileSourceOwner} from './technical-profile-source.js';
import {validateTechnicalProfileDecision,type TechnicalDecisionAction} from './technical-profile-decisions.js';
import {assertTechnicalNativeRealizationOwner,createTechnicalNativeRealizationOwner,type CheckedTechnicalNativeRealization} from './technical-profile-native.js';

const ext=path.extname(fileURLToPath(import.meta.url)),pin=pinCoreImplementation(import.meta.url,['technical-profile-source'+ext,'technical-profile-native'+ext,'technical-profile-decisions'+ext,'../generic/native-profile-resource'+ext]);
export const TECHNICAL_ACTION_OPERATIONS=Object.freeze({Dispatch:'dispatch',Renew:'renew',WaitForRefresh:'wait',RecoverRefresh:'recover-refresh',InspectOriginal:'inspect',Backoff:'backoff',Reauthorize:'reauthorize',Finish:'replay',Halt:'halt'} as const);
export type TechnicalActionOperation=typeof TECHNICAL_ACTION_OPERATIONS[TechnicalDecisionAction];
export interface TechnicalProfileActionOwner {readonly kind:'original-technical-profile-action-owner/v1'}
export interface TechnicalProfileRuntimeInvocation {readonly kind:'original-technical-profile-runtime-invocation/v1'}
export interface TechnicalProfileRuntimeFrame {readonly entry:{readonly input:unknown};readonly owner:{readonly context:Readonly<Record<string,unknown>>;readonly observation:Readonly<Record<string,unknown>>}}
export interface TechnicalProfileActionOwnerConfiguration {
 readonly realizationOwner:ReturnType<typeof createTechnicalNativeRealizationOwner>;
 readonly realization:CheckedTechnicalNativeRealization;
 readonly nativeInstance:unknown;
 readonly operations:readonly TechnicalActionOperation[];
 /** Trusted implementation hooks over actual original resources, never source
  * callbacks or remote-provided authority predicates. */
 readonly open:(actor:unknown,input:Uint8Array,settings:{readonly deadline_ms:number;readonly signal?:AbortSignal})=>Promise<object>|object;
 readonly capture:(original:object)=>Promise<TechnicalProfileRuntimeFrame>|TechnicalProfileRuntimeFrame;
 readonly assertCurrent:(original:object)=>Promise<void>|void;
 readonly invoke:(original:object,operation:TechnicalActionOperation,request:{readonly decision:{readonly action:TechnicalDecisionAction;readonly delayMs:string};readonly projections:Readonly<Record<string,unknown>>})=>Promise<unknown>|unknown;
 readonly closeInvocation?:(original:object)=>Promise<void>|void;
}
const resources=new WeakMap<object,TechnicalProfileActionOwnerConfiguration>();
/** Only the trusted installer calls this; source envelopes cannot construct
 * owners, execute callbacks or turn a Boolean into a native capability. */
export function createTechnicalProfileActionOwner(configuration:TechnicalProfileActionOwnerConfiguration):TechnicalProfileActionOwner {
 pin.assertCurrent();assertTechnicalNativeRealizationOwner(configuration.realizationOwner);configuration.realizationOwner.assertCurrent(configuration.realization);configuration.realizationOwner.assertInstance(configuration.realization,configuration.nativeInstance);
 if(!Array.isArray(configuration.operations)||!configuration.operations.length||new Set(configuration.operations).size!==configuration.operations.length||configuration.operations.some(v=>!Object.values(TECHNICAL_ACTION_OPERATIONS).includes(v))||['open','capture','assertCurrent','invoke'].some(k=>typeof (configuration as unknown as Record<string,unknown>)[k]!=='function'))throw new Error('Exact installed original action owner required');
 const owner=Object.freeze({kind:'original-technical-profile-action-owner/v1' as const});resources.set(owner,Object.freeze({...configuration,operations:Object.freeze([...configuration.operations])}));return owner;
}
function resource(owner:TechnicalProfileActionOwner){pin.assertCurrent();const r=resources.get(owner);if(!r)throw new Error('Original registered action owner required');r.realizationOwner.assertCurrent(r.realization);r.realizationOwner.assertInstance(r.realization,r.nativeInstance);return r;}
function project(frame:TechnicalProfileRuntimeFrame,from:string):unknown {
 if(!/^(?:entry\.input|owner\.context|owner\.observation)\.[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)*$/.test(from))throw new Error('Declared bounded runtime reference required');
 let current:unknown=frame;for(const key of from.split('.')){if(!current||typeof current!=='object'||!Object.hasOwn(current,key))throw new Error('Missing original runtime argument '+from);current=(current as Record<string,unknown>)[key];}
 return captureJson(current);
}
export function createTechnicalProfileRuntime(options:{readonly sourceOwner:ReturnType<typeof createTechnicalProfileSourceOwner>;readonly source:CheckedTechnicalProfileSource;readonly owners:ReadonlyMap<string,TechnicalProfileActionOwner>;readonly now?:()=>number}) {
 assertTechnicalProfileSourceOwner(options.sourceOwner);options.sourceOwner.assertCurrent(options.source);
 const target=options.sourceOwner.inspect(options.source).target;if(target?.consumer!=='craft.technical-profile-runtime/v1'||target.package_schema!=='craft.technical-profile-runtime/v1')throw new Error('Exact technical runtime consumer required; architecture packages cannot widen effects');
 const owners=new Map(options.owners),bindings=options.sourceOwner.inspectRuntimeBindings(options.source) as readonly Record<string,any>[],now=options.now??Date.now;
 const current=()=>{options.sourceOwner.assertCurrent(options.source);for(const [id,o]of owners){const r=resource(o);r.realizationOwner.assertSource(r.realization,options.sourceOwner,options.source,id);}};
 current();
 const decisions=bindings.filter(b=>b.kind==='decision');
 for(const b of decisions){if(!owners.has(b.binding))throw new Error('Missing original context owner '+b.binding);const original=resource(owners.get(b.binding)!);if(!original.realizationOwner.inspect(original.realization).operations.includes(b.operation))throw new Error('Selected original native operation unavailable '+b.operation);for(const [action,h]of Object.entries(b.handlers) as [TechnicalDecisionAction,{owner:string;operation:TechnicalActionOperation}][]){if(TECHNICAL_ACTION_OPERATIONS[action]!==h.operation)throw new Error('Action/handler mismatch');const selected=owners.get(h.owner);if(!selected||!resource(selected).operations.includes(h.operation))throw new Error('Selected original handler unavailable '+h.owner+':'+h.operation);}for(const arg of Object.values(b.arguments) as {from:string}[])if(!arg.from.startsWith('owner.context.')&&!arg.from.startsWith('owner.observation.'))throw new Error('Decision inputs require original owner provenance');}
 type Row={binding:Record<string,any>;actor:unknown;input:Uint8Array;input_sha256:string;settings:{deadline_ms:number;signal?:AbortSignal};contexts:Map<string,object>;retired:boolean;busy:boolean;completion?:Promise<void>;complete?:()=>void};
 const invocations=new WeakMap<object,Row>(),activeRows=new Set<Row>();let closed=false;
 const retire=async(r:Row)=>{r.retired=true;activeRows.delete(r);for(const [id,original]of r.contexts)try{await resources.get(owners.get(id)!)?.closeInvocation?.(original);}catch{/* cleanup cannot relabel an already observed effect */}};
 const row=(inv:TechnicalProfileRuntimeInvocation)=>{current();const r=invocations.get(inv);if(!r||r.retired||closed)throw new Error('Fresh original profile invocation required');if(r.settings.signal?.aborted||now()>=r.settings.deadline_ms)throw new Error('Profile invocation cancelled or deadline expired');return r;};
 const context=async(r:Row,id:string)=>{const configured=resource(owners.get(id)!);let original=r.contexts.get(id);if(!original){original=await configured.open(r.actor,new Uint8Array(r.input),r.settings);if(!original||typeof original!=='object')throw new Error('Original owner invocation required');r.contexts.set(id,original);current();}await configured.assertCurrent(original);current();if(r.settings.signal?.aborted||now()>=r.settings.deadline_ms)throw new Error('Profile invocation cancelled or deadline expired');return {configured,original};};
 return Object.freeze({
  async open(binding:string,actor:unknown,input:Uint8Array,settings:{readonly deadline_ms:number;readonly signal?:AbortSignal}):Promise<TechnicalProfileRuntimeInvocation>{
   current();if(closed||!(input instanceof Uint8Array)||input.byteLength>65536||!Number.isSafeInteger(settings.deadline_ms)||settings.deadline_ms<=now()||settings.deadline_ms-now()>300000||settings.signal!==undefined&&!(settings.signal instanceof AbortSignal))throw new Error('Bounded profile invocation required');
   const matches=decisions.filter(b=>b.binding===binding);if(matches.length!==1)throw new Error('One declared decision binding required');
   const r:Row={binding:matches[0]!,actor,input:new Uint8Array(input),input_sha256:coreSha256(input),settings:{deadline_ms:settings.deadline_ms,...(settings.signal?{signal:settings.signal}:{})},contexts:new Map(),retired:false,busy:false};
   try{await context(r,binding);}catch(error){await retire(r);throw error;}activeRows.add(r);const inv=Object.freeze({kind:'original-technical-profile-runtime-invocation/v1' as const});invocations.set(inv,r);return inv;
  },
  async execute(inv:TechnicalProfileRuntimeInvocation){const r=row(inv);if(r.busy)throw new Error('Profile invocation already executing');r.busy=true;r.completion=new Promise<void>(resolve=>{r.complete=resolve;});let action:TechnicalDecisionAction|undefined,invoked=false;
   try{
    const root=await context(r,r.binding.binding),frame=captureJson(await root.configured.capture(root.original)) as unknown as TechnicalProfileRuntimeFrame;await root.configured.assertCurrent(root.original);row(inv);
    const args=Object.fromEntries(Object.entries(r.binding.arguments).map(([k,v]:[string,any])=>[k,project(frame,v.from)]));
    const decoded=options.sourceOwner.evaluateRuntime(options.source,r.binding.selector,args) as any;
    if(decoded?.tag==='Rejected'||decoded?.tag==='Failed')return Object.freeze({kind:'denied' as const,reason:decoded.fields.code,retain_original:true});
    const selected=validateTechnicalProfileDecision(decoded?.tag==='Returned'?decoded.fields.value:decoded);action=selected.action;
    const projections:Record<string,unknown>=Object.create(null);
    if(action==='Dispatch')for(const b of bindings.filter(b=>b.binding===r.binding.binding&&b.operation===r.binding.operation&&b.kind!=='decision')){
     const input=Object.fromEntries(Object.entries(b.arguments).map(([k,v]:[string,any])=>[k,project(frame,v.from)])),value=options.sourceOwner.evaluateRuntime(options.source,b.mapping??b.rule,input);
     if(b.kind==='guard'&&value!==true)return Object.freeze({kind:'denied' as const,reason:'runtime-guard-rejected',retain_original:true});
     if(b.kind==='projection')projections[b.mapping]=value;
    }
    const handler=r.binding.handlers[action];if(!handler||TECHNICAL_ACTION_OPERATIONS[action]!==handler.operation)throw new Error('Unadmitted decision handler');
    const selectedOwner=await context(r,handler.owner);await root.configured.assertCurrent(root.original);row(inv);
    if(action==='Backoff'&&BigInt(selected.delayMs)>=BigInt(Math.max(0,r.settings.deadline_ms-now())))return Object.freeze({kind:'denied' as const,reason:'retry-delay-exceeds-deadline',retain_original:true});
    // The trusted original owner consumes the action; this adapter never sleeps,
    // retries or creates an alternate provider/attempt on its own.
    invoked=true;const outcome=await selectedOwner.configured.invoke(selectedOwner.original,handler.operation,{decision:selected,projections:Object.freeze(projections)});
    await selectedOwner.configured.assertCurrent(selectedOwner.original);await root.configured.assertCurrent(root.original);row(inv);
    return Object.freeze({kind:'observed' as const,action,operation:handler.operation,outcome,retain_original:true,input_sha256:r.input_sha256});
   }catch(error){return Object.freeze({kind:invoked&&(action==='Dispatch'||action==='Renew')?'unknown' as const:'denied' as const,...(action?{action}:{}),reason:error instanceof Error?error.message:'original-owner-unavailable',retain_original:true});}
   finally{await retire(r);r.complete?.();}
  },
  assertCurrent(inv:TechnicalProfileRuntimeInvocation){row(inv);},
  async close(){closed=true;await Promise.all([...activeRows].map(r=>r.busy?r.completion:retire(r)));},
 });
}
