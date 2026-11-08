import {openSqliteRequestCustody} from '../../../../../../../craft/projects/domainspec-v2/impl/cli/dist/runtime/sqlite-request-custody.js';
import {createMemoryRequestCustody} from '../../../../../../../craft/projects/domainspec-v2/impl/cli/dist/runtime/request-custody.js';
// Native memory binding only; policy/identity configuration is generated. Open Questions: custody/README.md.
export function createIdempotentDispatcher({custodyFactory,policy,token,durable,...options}){
 if(typeof custodyFactory!=='function')throw Object.assign(Error('CUSTODY_BINDING_REQUIRED'),{code:'CUSTODY_BINDING_REQUIRED'});
 // Optional legacy policy handler injection remains for compatibility fixtures.
 const createStore=durable?Object.assign(options=>openSqliteRequestCustody({...options,path:durable.path,key:durable.key,reconciliation:durable.reconciliation}),{backend:'bounded-sqlite'}):createMemoryRequestCustody;
 return custodyFactory({...options,createStore,...(durable?{clock:Date.now}:{}),...(policy?{policy:async input=>{const response=await policy(new Request('http://localhost/internal/idempotency-decision',{method:'POST',headers:{authorization:'Bearer '+token,'content-type':'application/json'},body:JSON.stringify(input)}),{INFERENCE_INTERNAL_TOKEN:token});return response.json();}}:{})});
}
