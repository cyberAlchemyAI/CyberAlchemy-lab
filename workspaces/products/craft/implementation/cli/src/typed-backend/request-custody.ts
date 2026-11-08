import {validateCompositionShape} from './outbound-composition.js';
// Candidate normalized custody binding. Open Questions: ../../REQUEST-CUSTODY.md.
export const REQUEST_CUSTODY_PROFILE='domainspec.request-custody/v1-candidate';
const fail=(s:string):never=>{throw Error('REQUEST_CUSTODY: '+s);};
export function compileRequestCustody(value:unknown){
 const c:any=structuredClone(value);
 const closed=(v:any,keys:string[])=>{if(!v||typeof v!=='object'||Array.isArray(v)||Object.keys(v).some(k=>!keys.includes(k))||keys.some(k=>!Object.hasOwn(v,k)))fail('closed contract');};
 closed(c,['schema_version','limits','identity','decisions','lifecycle','module']);
 if(c.schema_version!==REQUEST_CUSTODY_PROFILE)fail('profile');
 closed(c.limits,['retention_ms','max_entries','max_bytes','reservation_ms']);
 for(const [k,max] of Object.entries({retention_ms:86400000,max_entries:10000,max_bytes:65536,reservation_ms:30000}))if(!Number.isSafeInteger(c.limits[k])||c.limits[k]<1||c.limits[k]>max)fail('limits');
 closed(c.identity,['version','request','payload','scope','request_id','stream','defaults','exclude']);
 for(const k of ['version','request','payload','scope','request_id','stream'])if(typeof c.identity[k]!=='string'||!/^[_a-zA-Z][_a-zA-Z0-9-]{0,63}$/.test(c.identity[k])||['__proto__','prototype','constructor'].includes(c.identity[k]))fail('identity');
 if(new Set([c.identity.scope,c.identity.request_id,c.identity.stream]).size!==3)fail('identity fields collide');
 if(c.identity.request===c.identity.payload)fail('identity collision');
 if(!Array.isArray(c.identity.exclude)||c.identity.exclude.length!==1||c.identity.exclude[0]!==c.identity.request_id)fail('exclude only caller identity');
 if(!c.identity.defaults||Array.isArray(c.identity.defaults)||typeof c.identity.defaults!=='object'||Object.keys(c.identity.defaults).length>16)fail('defaults');
 for(const [k,v]of Object.entries(c.identity.defaults))if(!/^[_a-zA-Z][_a-zA-Z0-9]{0,63}$/.test(k)||['__proto__','prototype','constructor',c.identity.scope,c.identity.request_id].includes(k)||!['string','boolean','number'].includes(typeof v)||(typeof v==='number'&&!Number.isFinite(v)))fail('default');
 if(c.identity.defaults[c.identity.stream]!==false)fail('stream default');
 closed(c.decisions,['execute','replay','reject']);
 if(c.decisions.execute!=='execute'||c.decisions.replay!=='replay')fail('decision');
 closed(c.decisions.reject,['conflict','in_progress','stream_not_replayable','previous_failure']);
 const codes=['IDEMPOTENCY_CONFLICT','REQUEST_IN_PROGRESS','STREAM_NOT_REPLAYABLE','PREVIOUS_REQUEST_FAILED'];
 if(['conflict','in_progress','stream_not_replayable','previous_failure'].some((k,n)=>c.decisions.reject[k]!==codes[n]))fail('decision mapping');
 closed(c.lifecycle,['attempts','outcome','expiry','backend']);
 if(c.lifecycle.attempts!==1||c.lifecycle.outcome!=='write-once'||c.lifecycle.expiry!=='outcome-and-transport-settled'||!['bounded-memory','bounded-sqlite'].includes(c.lifecycle.backend))fail('lifecycle');
 closed(c.module,['input','output']);validateCompositionShape(c.module.input);validateCompositionShape(c.module.output);if(c.module.input.optional||c.module.input.nullable||c.module.output.optional||c.module.output.nullable)fail('required policy interfaces');
 const input=c.module.input?.type,output=c.module.output?.type;
 if(!input||typeof input!=='object'||!output||typeof output!=='object')fail('policy shape');
 const fields=['exists','matches','pending','stream','succeeded'];
 if(Object.keys(input).length!==5||fields.some(k=>input[k]?.type!=='boolean'||input[k]?.optional||input[k]?.nullable)||output.status?.type!=='string'||output.status.optional||output.status.nullable)fail('policy signature');
 return {contract:c,trace:{profile:REQUEST_CUSTODY_PROFILE,identity:c.identity,lifecycle:c.lifecycle,authority_effect:'none'}};
}
