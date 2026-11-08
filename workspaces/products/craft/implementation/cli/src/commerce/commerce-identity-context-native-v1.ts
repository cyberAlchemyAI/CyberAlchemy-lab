/** Source-bound identity producer context over the original generated component.
 * Open Questions: docs/COMMERCE-NATIVE-IDENTITY.md#open-questions. */
import {createCommerceIdentityComponentOwner} from './commerce-identity-component.js';
import {assertCommerceIdentityCallOwner,type CommerceIdentityCallOwner,type CommerceIdentityCallHandle} from './commerce-identity-call-owner.js';
import {assertCommerceSourceInvocationOwnerV1,type CommerceSourceInvocationOwnerV1} from './commerce-source-invocation-owner-v1.js';
import type {CoreCommerceStageSourceOwner} from './commerce-core-stage-owner.js';
import type {CommerceComputationDomainOwner,CommerceComputationDomainHandle} from './commerce-computation-domain.js';
import type {CommerceSourceHandle,CommerceOperationInvocationHandle} from './commerce-stages-v1.js';
import type {CommerceCallsiteHandle,CommerceIdentityHandle,CommerceIdentityProducersV1,IdentityContextNativeV1} from './commerce-native-v1.js';

const methods=['checkoutFingerprint','newOrderId','commandId','eventMetadata','stockLinesFingerprint','stockCommandFingerprint','captureFingerprint','taggedCommandIdentity','eventFingerprint','confirmedOrderFingerprint','orderActionFingerprint','clockEpochMs'] as const satisfies readonly (keyof CommerceIdentityProducersV1)[];
export class CommerceIdentityContextErrorV1 extends Error {
 constructor(readonly code:'ForeignOwner'|'ForeignCallsite'|'ForeignInvocation'|'UnboundMethod'|'DisposedOwner'|'ProducerValueRejected') {super(code);this.name='CommerceIdentityContextErrorV1';}
}
function bad(code:CommerceIdentityContextErrorV1['code']):never {throw new CommerceIdentityContextErrorV1(code);}

/** The source-call wrapper is issued only after a real captured call is present
 * in the generated component. It never accepts a caller-authored ABI record. */
export interface CommerceIdentityContextNativeOwnerV1 extends IdentityContextNativeV1 {
 bindOriginalCallsite(call:CommerceIdentityCallHandle):CommerceCallsiteHandle;
 inspect():Readonly<{kind:'original-source-identity-context-native/v1-candidate';source_calls:number;qualification:'identity-native-context-only;not-application-composition';authority_effect:'none'}>;
 dispose():void;
}

export async function createCommerceIdentityContextNativeV1(
 calls:CommerceIdentityCallOwner,stage:CoreCommerceStageSourceOwner,source:CommerceSourceHandle,
 domain:CommerceComputationDomainOwner,baseline:CommerceComputationDomainHandle,
 invocations:CommerceSourceInvocationOwnerV1,sourceCalls:readonly CommerceIdentityCallHandle[],directory:string,
):Promise<CommerceIdentityContextNativeOwnerV1> {
 assertCommerceIdentityCallOwner(calls);assertCommerceSourceInvocationOwnerV1(invocations);
 const components=createCommerceIdentityComponentOwner(calls,stage,source,domain,baseline);
 const component=await components.materialize(sourceCalls,directory);
 const materialized=new Set(components.inspect(component).manifest.source_bindings.map(b=>b.key));
 const callsites=new WeakMap<object,CommerceIdentityCallHandle>();
 const issued=new WeakMap<object,{invocation:CommerceOperationInvocationHandle;call:CommerceIdentityCallHandle;method:string}>();
 let disposed=false;
 const current=()=>{if(disposed)bad('DisposedOwner');components.assertCurrent(component);invocations.assertCurrent();};
 const sourceCall=(h:CommerceCallsiteHandle)=>{current();const call=h&&typeof h==='object'?callsites.get(h):undefined;if(!call)bad('ForeignCallsite');calls.assertCurrent(call);return call;};
 const identity=(h:CommerceIdentityHandle)=>{current();const row=h&&typeof h==='object'?issued.get(h):undefined;if(!row)bad('ForeignOwner');invocations.assertCurrent(row.invocation);calls.assertCurrent(row.call);return row;};
 const match=(invocation:CommerceOperationInvocationHandle,call:CommerceIdentityCallHandle)=>{
  const target=invocations.inspect(invocation),binding=calls.inspect(call);
  if(target.role!=='Operation'||target.operation!==binding.caller||target.service!==binding.service||target.source_sha256!==binding.source_capture_sha256)bad('ForeignInvocation');
  if(!materialized.has(binding.key))bad('ForeignCallsite');
  return binding;
 };
 const owner:CommerceIdentityContextNativeOwnerV1=Object.freeze({
  bindOriginalCallsite(call:CommerceIdentityCallHandle){current();const binding=calls.inspect(call);if(!materialized.has(binding.key))bad('ForeignCallsite');const h=Object.freeze({kind:'original-bound-identity-callsite/v1-candidate'}) as unknown as CommerceCallsiteHandle;callsites.set(h,call);return h;},
  createCommerceIdentityProducers(invocation:CommerceOperationInvocationHandle,sourceCallHandle:CommerceCallsiteHandle){
   const call=sourceCall(sourceCallHandle),binding=match(invocation,call),method=binding.observation.method;
   if(!methods.some(m=>m===method))bad('ForeignCallsite');
   const h:Record<string,unknown>={kind:'private-source-callsite-producers'};
   for(const name of methods)Object.defineProperty(h,name,{value:function(this:CommerceIdentityHandle,...args:unknown[]){
    if((this as unknown)!==h)bad('ForeignOwner');const row=identity(this);if(row.method!==name)bad('UnboundMethod');match(row.invocation,row.call);
    const result=components.evaluateBoundParameters(component,row.call,args);
    if(!result.ok)bad('ProducerValueRejected');return result.value;
   },enumerable:true});
   Object.freeze(h);issued.set(h,{invocation,call,method});return h as unknown as CommerceIdentityHandle;
  },
  assertCommerceIdentityContextCurrent(producers:CommerceIdentityHandle,invocation:CommerceOperationInvocationHandle){const row=identity(producers);if(row.invocation!==invocation)bad('ForeignInvocation');match(invocation,row.call);},
  inspect(){current();return Object.freeze({kind:'original-source-identity-context-native/v1-candidate' as const,source_calls:materialized.size,qualification:'identity-native-context-only;not-application-composition' as const,authority_effect:'none' as const});},
  dispose(){if(disposed)return;disposed=true;components.dispose(component);},
 });
 return owner;
}
