// Registered empty-effects settlement. No persistence, publication, provider or durability claim.
// Open questions: docs/BUSINESS-APPLICATIONS.md. Each invocation owns a fresh transaction.
export interface EmptyEffectsBatch {readonly writes:readonly never[];readonly events:readonly never[]}
export interface EmptyEffectsReceipt {readonly status:'committed'|'rejected'|'indeterminate'}
export interface EmptyEffectsTransaction {read(request:never):Promise<never>;commit(batch:EmptyEffectsBatch):Promise<EmptyEffectsReceipt>;rollback():Promise<void>}
export interface EmptyEffectsStore {begin():Promise<EmptyEffectsTransaction>}
export function createEmptyEffectsStore():EmptyEffectsStore {
 return Object.freeze({begin:async()=>{
  let state:'open'|'committed'|'rolled-back'='open';
  return Object.freeze({
   read:async(_request:never):Promise<never>=>{throw new TypeError('EMPTY_EFFECTS_READ_UNSUPPORTED');},
   commit:async(batch:EmptyEffectsBatch):Promise<EmptyEffectsReceipt>=>{
    if(state!=='open')return Object.freeze({status:'rejected'});
    if(!batch||typeof batch!=='object'||Array.isArray(batch))throw new TypeError('EMPTY_EFFECTS_BATCH');
    const fields=Object.getOwnPropertyDescriptors(batch);
    if(Reflect.ownKeys(fields).length!==2||!fields.writes||!fields.events||!('value' in fields.writes)||!('value' in fields.events)||!Array.isArray(fields.writes.value)||!Array.isArray(fields.events.value))throw new TypeError('EMPTY_EFFECTS_BATCH');
    if(fields.writes.value.length||fields.events.value.length)return Object.freeze({status:'rejected'});
    state='committed';return Object.freeze({status:'committed'});
   },
   rollback:async():Promise<void>=>{if(state==='committed')throw new TypeError('EMPTY_EFFECTS_ALREADY_SETTLED');state='rolled-back';},
  });
 }});
}
