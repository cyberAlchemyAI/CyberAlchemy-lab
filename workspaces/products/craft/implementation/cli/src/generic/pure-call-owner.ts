import {assertGenericInternalExecutionToken,type GenericInternalExecutionToken} from './execution-session.js';
/** Actual generic callsite custody, consumed by reference execution and emission.
 * Open Questions: docs/GENERIC-APPLICATIONS.md#open-questions. */
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {pinCoreImplementation} from '../commerce/commerce-core-physical.js';
import {dataDigest,captureJson} from '../profile-engine/contracts.js';
import {coreFreeze,coreSourceFail as fail} from '../commerce/commerce-core-syntax.js';
import {assertGenericComputationDomainOwner,type GenericComputationDomainOwner,type GenericComputationDomainHandle} from './computation-domain.js';
import type {ValueTypeV1} from '../commerce/commerce-data-v1.js';
const ext=path.extname(fileURLToPath(import.meta.url)),pin=pinCoreImplementation(import.meta.url,['computation-domain'+ext]);
const at={path:'generic-call',start:0,end:0};
export interface GenericPureCallHandle{readonly kind:'original-generic-pure-call/v1-candidate'}
export function createGenericPureCallOwner(domain:GenericComputationDomainOwner,handle:GenericComputationDomainHandle){
 return createCallOwner(()=>{pin.assertCurrent();assertGenericComputationDomainOwner(domain);domain.assertCurrent(handle);},domain.inspect(handle));
}
export function createGenericKeyedPureCallOwner(token:GenericInternalExecutionToken){const selected=assertGenericInternalExecutionToken(token);return createCallOwner(()=>{pin.assertCurrent();assertGenericInternalExecutionToken(token);},selected.inspection);}
function createCallOwner(parentCurrent:()=>void,inspection:Pick<ReturnType<GenericComputationDomainOwner['inspect']>,'contract'|'environment'|'source_capture_sha256'|'contract_sha256'>){
 parentCurrent();const rows=new WeakMap<object,{path:string;declaration:string;predicate:ValueTypeV1|null;inspection:Readonly<Record<string,unknown>>}>();
 const current=(h:GenericPureCallHandle)=>{parentCurrent();const r=h&&typeof h==='object'?rows.get(h):undefined;if(!r)fail('ForeignOwner',at,'exact original generic call handle required');return r;};
 const register=(path:string,declaration:string,predicate:ValueTypeV1|null)=>{const callee=inspection.contract.functions.find(f=>f.name===declaration);if(!callee)fail('UnknownReference',at,'actual checked callee required');const binding=inspection.environment.calls.find(c=>c.path===path);
  const data=coreFreeze({path,declaration,kind:predicate?'declared-collection-predicate':'original-expression-callsite',source_capture_sha256:inspection.source_capture_sha256,domain_sha256:inspection.contract_sha256,call_code_epoch_sha256:pin.sha256,schema_version:inspection.contract.schema_version,semantics_revision:inspection.contract.semantics_revision,limits_sha256:dataDigest(inspection.contract.limits),callee_sha256:dataDigest(callee),parameters:callee.parameters,result:callee.result,rounding:callee.rounding,evaluation_order:binding?.evaluation_order??'declared-unary-collection-rule',predicate});
  const h=Object.freeze({kind:'original-generic-pure-call/v1-candidate' as const});rows.set(h,{path,declaration,predicate,inspection:data});current(h);return h;};
 return Object.freeze({bind(path:string){if(typeof path!=='string')fail('InvalidContract',at,'actual expression path required');const c=inspection.environment.calls.find(c=>c.path===path);if(!c)fail('UnknownReference',at,'path is not an original checked pure callsite');return register(path,c.declaration,null);},bindPredicate(type:ValueTypeV1){const t=captureJson(type) as unknown as ValueTypeV1,p=inspection.contract.values.collection_predicates.find(p=>dataDigest(p.type)===dataDigest(t));if(!p)fail('UnknownReference',at,'actual checked type predicate association required');const f=inspection.contract.functions.find(f=>f.name===p.rule)!;if(f.kind!=='Rule'||f.parameters.length!==1||dataDigest(f.parameters[0]!.type)!==dataDigest(p.type)||f.result.kind!=='scalar'||f.result.name!=='Bool')fail('InvalidContract',at,'checked unary Bool Rule association required');return register('@predicate:'+dataDigest(p.type),p.rule,p.type);},inspect(h:GenericPureCallHandle){return current(h).inspection;},assertCurrent(h:GenericPureCallHandle){current(h);},assertCall(h:GenericPureCallHandle,path:string,callee:string){const r=current(h);if(r.predicate||r.path!==path||r.declaration!==callee)fail('ForeignOwner',at,'call must match exact source path and callee');},assertPredicate(h:GenericPureCallHandle,type:ValueTypeV1,callee:string){const r=current(h);if(!r.predicate||dataDigest(type)!==dataDigest(r.predicate)||r.declaration!==callee)fail('ForeignOwner',at,'predicate must match exact declared type and unary Rule');}});
}
