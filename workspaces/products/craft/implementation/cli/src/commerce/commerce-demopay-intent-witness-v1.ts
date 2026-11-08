/** Read-only join of an original DemoPay source site and an actual committed
 * Payments row. This is not a dispatch permit or provider observation.
 * Open Questions: docs/COMMERCE-NATIVE-V1.md#open-questions. */
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {types as host} from 'node:util';
import {createHash} from 'node:crypto';
import {pinCoreImplementation} from './commerce-core-physical.js';
import {assertCommerceDemoPaySourceSiteOwnerV1,type CommerceDemoPaySourceSiteOwnerV1,type CommerceDemoPaySourceSiteV1} from './commerce-demopay-source-site-v1.js';
import {assertCommerceServiceStorageOwnerV1,type CommerceServiceStorageOwnerV1} from './commerce-service-storage-v1.js';

const ext=path.extname(fileURLToPath(import.meta.url));
const pin=pinCoreImplementation(import.meta.url,['commerce-core-physical'+ext,'commerce-demopay-source-site-v1'+ext,'commerce-service-storage-v1'+ext]);
export class CommerceDemoPayIntentWitnessErrorV1 extends Error {constructor(readonly code:string){super(code);this.name='CommerceDemoPayIntentWitnessErrorV1';}}
const bad=(code:string):never=>{throw new CommerceDemoPayIntentWitnessErrorV1(code);};
export interface CommerceDemoPayIntentWitnessV1 {readonly kind:'original-commerce-demopay-durable-intent-witness/v1-candidate'}
export interface CommerceDemoPayIntentRequestV1 {readonly attemptKey:string;readonly orderId:string;readonly amountMinor:bigint;readonly currency:'USD';readonly requestFingerprint:string}
export interface CommerceDemoPayIntentInspectionV1 {
 readonly site:string;readonly target:'Shop.DemoPay.Capture'|'Shop.DemoPay.InspectCapture';
 readonly request:CommerceDemoPayIntentRequestV1;readonly dispatch_state:'Prepared'|'Dispatched';
 readonly payment_status:string;readonly version:bigint;readonly store_id:string;
 readonly source_capture_sha256:string;readonly selected_family_sha256:string;
 readonly qualification:'original-source-and-committed-row-observation-only;no-command-owner-or-provider-dispatch-permit';readonly authority_effect:'none';
}
export interface CommerceDemoPayIntentWitnessOwnerV1 {
 observe(site:CommerceDemoPaySourceSiteV1,request:CommerceDemoPayIntentRequestV1,expected:'Prepared'|'Dispatched'):CommerceDemoPayIntentWitnessV1;
 inspect(witness:CommerceDemoPayIntentWitnessV1):CommerceDemoPayIntentInspectionV1;
 assertCurrent():void;dispose():void;
}
type Row={site:CommerceDemoPaySourceSiteV1;request:CommerceDemoPayIntentRequestV1;expected:'Prepared'|'Dispatched';row_sha256:string;inspection:CommerceDemoPayIntentInspectionV1};
const owners=new WeakSet<object>();
export function assertCommerceDemoPayIntentWitnessOwnerV1(owner:CommerceDemoPayIntentWitnessOwnerV1):void {if(!owner||typeof owner!=='object'||!owners.has(owner))bad('ForeignOwner');owner.assertCurrent();}
function closedRequest(input:CommerceDemoPayIntentRequestV1):void {
 const keys=['attemptKey','orderId','amountMinor','currency','requestFingerprint'];
 if(!input||typeof input!=='object'||Array.isArray(input)||host.isProxy(input)||![Object.prototype,null].includes(Object.getPrototypeOf(input))||Reflect.ownKeys(input).length!==keys.length)bad('InvalidRequest');
 const descriptors=Object.getOwnPropertyDescriptors(input);
 if(keys.some(k=>!descriptors[k]?.enumerable||!Object.hasOwn(descriptors[k]!,'value')))bad('InvalidRequest');
 if(![input.attemptKey,input.orderId].every(v=>typeof v==='string'&&v.length>0&&Buffer.byteLength(v,'utf8')<=128)||typeof input.amountMinor!=='bigint'||input.amountMinor<0n||input.amountMinor>18446744073709551615n||input.currency!=='USD'||typeof input.requestFingerprint!=='string'||!/^[a-f0-9]{64}$/.test(input.requestFingerprint))bad('InvalidRequest');
}
export function createCommerceDemoPayIntentWitnessOwnerV1(sites:CommerceDemoPaySourceSiteOwnerV1,storage:CommerceServiceStorageOwnerV1):CommerceDemoPayIntentWitnessOwnerV1 {
 assertCommerceDemoPaySourceSiteOwnerV1(sites);assertCommerceServiceStorageOwnerV1(storage);pin.assertCurrent();
 const selected=storage.inspect(),witnesses=new WeakMap<object,Row>();
 if(selected.service!=='payments')bad('ForeignStore');
 let disposed=false;
 const current=()=>{if(disposed)bad('DisposedOwner');pin.assertCurrent();sites.assertCurrent();storage.assertCurrent();const now=storage.inspect();if(now.store_id!==selected.store_id||now.service!=='payments'||now.source_capture_sha256!==selected.source_capture_sha256||now.family_sha256!==selected.family_sha256||now.schema_sha256!==selected.schema_sha256)bad('StaleStore');};
 const read=(site:CommerceDemoPaySourceSiteV1,request:CommerceDemoPayIntentRequestV1,expected:'Prepared'|'Dispatched')=>{
  current();closedRequest(request);if(expected!=='Prepared'&&expected!=='Dispatched')bad('InvalidState');
  const source=sites.inspect(site);
  if(source.service!=='payments'||source.source_capture_sha256!==selected.source_capture_sha256||source.selected_family_sha256!==selected.family_sha256)bad('ForeignSite');
  const value=storage.inspectStoredRecord('Payments.PaymentAttempt',0,{attemptKey:request.attemptKey});
  if(!value||typeof value!=='object'||Array.isArray(value))bad('MissingIntent');
  const row=value as Record<string,unknown>;
  for(const key of ['attemptKey','orderId','amountMinor','currency','requestFingerprint'] as const)if(row[key]!==request[key])bad('ForeignRequest');
  if(row.dispatchState!==expected)bad('WrongDispatchState');
  if(typeof row.version!=='bigint'||row.version<1n||expected==='Prepared'&&(row.status!=='Intent'||row.version!==1n)||expected==='Dispatched'&&(row.version<2n||!['Pending','Unknown','Captured','Declined','Conflict'].includes(String(row.status))))bad('InvalidPersistedState');
  const row_sha256=createHash('sha256').update(JSON.stringify(value,(_key,member)=>typeof member==='bigint'?{uint64:member.toString()}:member)).digest('hex');
  current();return {source,row,row_sha256};
 };
 const implementation:CommerceDemoPayIntentWitnessOwnerV1={
  observe(site,request,expected){const selectedRow=read(site,request,expected);
   const copied=Object.freeze({...request});
   const inspection:CommerceDemoPayIntentInspectionV1=Object.freeze({site:selectedRow.source.source_path,target:selectedRow.source.target,request:copied,dispatch_state:expected,payment_status:String(selectedRow.row.status),version:selectedRow.row.version as bigint,store_id:selected.store_id,source_capture_sha256:selected.source_capture_sha256,selected_family_sha256:selected.family_sha256,qualification:'original-source-and-committed-row-observation-only;no-command-owner-or-provider-dispatch-permit',authority_effect:'none'});
   const handle=Object.freeze({kind:'original-commerce-demopay-durable-intent-witness/v1-candidate' as const});witnesses.set(handle,{site,request:copied,expected,row_sha256:selectedRow.row_sha256,inspection});return handle;
  },
  inspect(handle){current();const row=handle&&typeof handle==='object'?witnesses.get(handle):undefined;if(!row)bad('ForeignWitness');const fresh=read(row!.site,row!.request,row!.expected);if(fresh.row_sha256!==row!.row_sha256)bad('StaleIntent');return row!.inspection;},
  assertCurrent:current,dispose(){disposed=true;},
 };const owner=Object.freeze(implementation);owners.add(owner);current();return owner;
}
