/** R07 redacted bounded native observations and separate local quality scopes.
 * Open Questions: ../../README.md#open-questions. */
import {assert,capture,canonical,closed,count,freeze,sha256,text} from '../shared.mjs';
const schema='craft.runtime-observation/v1';
const transitions=new Set(['prepared','authorized','dispatched','returned','refused','incomplete','unavailable','unknown','review','committed','cancelled','reconciled','denied','retired']);
const categories=new Set(['work','model','provider','access']);
const codes=new Set(['InvalidContract','ResourceLimit','PermissionDenied','SourceRevoked','ProviderUnavailable','OperationFailed','StaleOwner','Timeout','Cancelled']);
const kinds=new Set(['observed','estimated','unknown']);
const boundDefaults=Object.freeze({capacity:256,eventBytes:4096,retentionMs:86400000,maxDrain:64});
export const OBSERVATION_IDENTITY=Object.freeze({abi:'craft.observations/v1',version:'1.0.0',payload:'closed-redacted-metadata',authoritative_records:'original-store-owners'});
/** Host binds the actual selected runtime's immutable identity. Only the opaque
 * emitter is passed into generated/native execution; public event input cannot
 * supply tenant, mode, resource or application labels. */
export function createObservationSink(options={}){
 const now=options.now??Date.now;assert(typeof now==='function','InvalidContract','trusted clock');
 const bounds={...boundDefaults,...capture(options.bounds??{})};assert(Object.keys(bounds).every(k=>Object.hasOwn(boundDefaults,k)),'InvalidContract','closed observation bounds');
 count(bounds.capacity,'capacity',65536);count(bounds.eventBytes,'eventBytes',16384);count(bounds.retentionMs,'retentionMs',604800000);count(bounds.maxDrain,'maxDrain',1024);assert(bounds.capacity>0&&bounds.eventBytes>=256&&bounds.maxDrain>0,'InvalidContract','positive observation bounds');
 const queue=[];let dropped=0,sequence=0,closedSink=false;const bindings=new WeakMap();
 const live=()=>assert(!closedSink,'StaleOwner','sink closed'),prune=()=>{const expiry=now()-bounds.retentionMs;while(queue.length&&queue[0].at_ms<expiry){queue.shift();dropped++;}};
 const emit=(emitter,raw)=>{live();const owner=bindings.get(emitter);assert(owner,'ForeignOwner','original observation emitter');owner.assertCurrent();
  const event=closed(raw,['category','transition','correlation_id','code','usage'],['category','transition','correlation_id']);assert(categories.has(event.category)&&transitions.has(event.transition),'InvalidContract','finite transition event');text(event.correlation_id,'correlation',128);
  if(event.code!==undefined)assert(codes.has(event.code),'InvalidContract','redacted finite code');
  let usage;if(event.usage!==undefined){const u=closed(event.usage,['kind','input_units','output_units','maximum_units'],['kind']);assert(kinds.has(u.kind),'InvalidContract','usage kind');for(const k of ['input_units','output_units','maximum_units'])if(u[k]!==undefined)count(u[k],k);if(u.kind==='unknown')assert(u.input_units===undefined&&u.output_units===undefined,'InvalidContract','unknown usage is not observed zero');usage=u;}
  const entry=freeze({schema_version:schema,sequence:++sequence,at_ms:count(now(),'clock'),runtime:owner.identity,category:event.category,transition:event.transition,correlation_sha256:sha256(event.correlation_id),...(event.code?{code:event.code}:{}),...(usage?{usage}:{})});
  assert(Buffer.byteLength(canonical(entry))<=bounds.eventBytes,'ResourceLimit','redacted event bound');prune();if(queue.length>=bounds.capacity){dropped++;return freeze({accepted:false,reason:'optional-observation-overflow'});}queue.push(entry);return freeze({accepted:true,sequence:entry.sequence});
 };
 return Object.freeze({
  bindRuntime(runtime){live();assert(runtime&&typeof runtime.inspect==='function'&&typeof runtime.assertCurrent==='function','ForeignOwner','actual selected runtime owner');runtime.assertCurrent();
   const selected=closed(runtime.inspect(),['runtime_id','tenant','application','resource_id','mode']);for(const k of ['runtime_id','tenant','application','resource_id'])text(selected[k],k);assert(['fixture','local','provider'].includes(selected.mode),'InvalidContract','actual runtime mode');
   const identity=freeze({runtime_sha256:sha256(selected.runtime_id),tenant_sha256:sha256(selected.tenant),application:selected.application,resource_sha256:sha256(selected.resource_id),mode:selected.mode});
   const emitter=Object.freeze({emit:event=>emit(emitter,event)});bindings.set(emitter,{identity,assertCurrent:()=>{runtime.assertCurrent();assert(canonical(runtime.inspect())===canonical(selected),'StaleOwner','runtime identity changed');}});return emitter;
  },
  drain(max=bounds.maxDrain){live();count(max,'drain',bounds.maxDrain);prune();return freeze(queue.splice(0,max));},
  inspect(){live();prune();return freeze({identity:OBSERVATION_IDENTITY,bounds,pending:queue.length,dropped,authoritative_records:'not-owned-by-observation-sink'});},
  close(){closedSink=true;queue.length=0;},
 });
}
/** Native execution supplies the bound emitter, not a caller success label. */
export async function observeTransition(emitter,metadata,operation){
 assert(emitter&&typeof emitter.emit==='function'&&typeof operation==='function','InvalidContract','observation binding');const {category,correlation_id}=closed(metadata,['category','correlation_id']);
 const safeEmit=event=>{try{emitter.emit(event);}catch{/* optional diagnostics never replace original operation/store outcome */}};
 safeEmit({category,transition:'dispatched',correlation_id});try{const result=await operation();safeEmit({category,transition:'returned',correlation_id});return result;}catch(error){safeEmit({category,transition:'unknown',correlation_id,code:codes.has(error?.code)?error.code:'OperationFailed'});throw error;}
}
export function evaluateQuality({kind,cases,threshold}){
 assert(['fixture-correctness','parser','retrieval','citation','business-extraction'].includes(kind),'InvalidContract','local quality kind only; real-model qualification is separate');
 const rows=capture(cases);assert(Array.isArray(rows)&&rows.length>0&&rows.length<=10000,'InvalidContract','labelled case denominator');const t=closed(threshold,['numerator','denominator']);count(t.numerator);count(t.denominator);assert(t.denominator>0&&t.numerator<=t.denominator,'InvalidContract','threshold ratio');
 const ids=new Set();let passed=0;for(const row of rows){const c=closed(row,['id','expected','actual','status']);text(c.id,'case id');assert(!ids.has(c.id),'InvalidContract','unique case labels');ids.add(c.id);assert(['returned','refused','invalid','unavailable'].includes(c.status),'InvalidContract','case outcome');if(c.status==='returned'&&canonical(c.expected)===canonical(c.actual))passed++;}
 return freeze({schema_version:'craft.local-quality/v1',kind,scope:'local-labelled-cases;no-real-model-claim',passed,total:rows.length,threshold:t,status:BigInt(passed)*BigInt(t.denominator)>=BigInt(rows.length)*BigInt(t.numerator)?'passed':'failed',dataset_sha256:sha256(canonical(rows))});
}
