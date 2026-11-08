/** Native R01 metadata specialization. Kept separate from typed value capture.
 * Differential tests compare this emitted function with inspectOperationSettlement.
 */
export const WORKFLOW_SETTLEMENT_SUPPORT = String.raw`
export interface OperationSettlement {
 readonly commit_status:'committed'|'not-committed'|'indeterminate';
 readonly origin:'returned'|'invalid-return'|'threw'|'not-started';
 readonly status:'committed'|'failed'|'rejected'|'indeterminate'|null;
 readonly stage:string|null;readonly code:string|null;readonly continuation:string|null;
 readonly cleanup_failed:boolean|null;readonly result_validation:'not-performed';
}
const fail=(message:string):never=>{throw new TypeError('WORKFLOW_RUNTIME:'+message);};
const own=(value:unknown,names:readonly string[]):Record<string,PropertyDescriptor>=>{
 if(!value||typeof value!=='object'||Array.isArray(value)||![Object.prototype,null].includes(Object.getPrototypeOf(value)))return fail('plain object');
 const keys=Reflect.ownKeys(value);
 if(keys.length!==names.length||keys.some(k=>typeof k!=='string'||!names.includes(k)))return fail('closed fields');
 const d=Object.getOwnPropertyDescriptors(value);
 if(Object.values(d).some(p=>!Object.hasOwn(p,'value')||!p.enumerable))return fail('inert fields');return d;
};
const text=(v:unknown):v is string=>typeof v==='string'&&v.length>0&&v.length<=2048;
const identity=(v:unknown):string=>typeof v==='string'&&v.length<=256&&/^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$/.exec(v)?.[0]===v?v:fail('identity');
const unknown=(origin:'invalid-return'|'threw'):OperationSettlement=>Object.freeze({commit_status:'indeterminate',origin,status:null,stage:null,code:null,continuation:null,cleanup_failed:null,result_validation:'not-performed'});
const notStarted=():OperationSettlement=>Object.freeze({commit_status:'not-committed',origin:'not-started',status:null,stage:'argument-materialization',code:'ARGUMENT_MATERIALIZATION_FAILED',continuation:null,cleanup_failed:null,result_validation:'not-performed'});
export function inspectOperationSettlement(value:unknown,expectedContinuation:string):OperationSettlement{
 if(!text(expectedContinuation))return fail('continuation');
 try{
  const sd=value&&typeof value==='object'?Object.getOwnPropertyDescriptor(value,'status'):undefined;
  if(!sd||!Object.hasOwn(sd,'value')||!sd.enumerable)return unknown('invalid-return');
  if(sd.value==='committed'){
   own(value,['status','value']);
   return Object.freeze({commit_status:'committed',origin:'returned',status:'committed',stage:null,code:null,continuation:null,cleanup_failed:null,result_validation:'not-performed'});
  }
  const d=own(value,['status','stage','code','continuation','cleanupFailed']);
  const status=d.status!.value,stage=d.stage!.value,code=d.code!.value,cleanup=d.cleanupFailed!.value;
  if(!text(stage)||!text(code)||d.continuation!.value!==expectedContinuation||typeof cleanup!=='boolean')return unknown('invalid-return');
  let valid=false;
  if(stage==='commit')valid=!cleanup&&(status==='rejected'&&code==='COMMIT_REJECTED'||status==='indeterminate'&&['COMMIT_INDETERMINATE','INVALID_COMMIT_RECEIPT','COMMIT_UNCERTAIN'].includes(code));
  else if(stage==='input')valid=status==='failed'&&code==='OPERATION_INPUT'&&!cleanup;
  else if(stage==='begin')valid=status==='failed'&&code==='BEGIN_FAILED'&&!cleanup;
  else if(['read','guard','write-validation','event','result'].includes(stage))valid=status==='failed'&&code==='OPERATION_FAILED'||stage==='read'&&status==='failed'&&['READ_NOT_FOUND','READ_IDENTITY_MISMATCH'].includes(code)||stage==='guard'&&status==='rejected'&&/^RULE_REJECTED:[a-z][a-z0-9-]*:[a-z][a-z0-9-]*$/.test(code);
  if(!valid)return unknown('invalid-return');
  return Object.freeze({commit_status:status==='indeterminate'?'indeterminate':'not-committed',origin:'returned',status,stage,code,continuation:expectedContinuation,cleanup_failed:cleanup,result_validation:'not-performed'});
 }catch{return unknown('invalid-return');}
}
const freeze=<T>(v:T):T=>{if(v&&typeof v==='object'&&!Object.isFrozen(v)){Object.values(v).forEach(freeze);Object.freeze(v);}return v;};
const canonical=(v:unknown):string=>{
 if(Array.isArray(v))return '['+v.map(canonical).join(',')+']';
 if(v!==null&&typeof v==='object'){const d=v as Record<string,unknown>;return '{'+Object.keys(d).sort().map(k=>JSON.stringify(k)+':'+canonical(d[k])).join(',')+'}';}
 return JSON.stringify(v);
};
const digest=(v:unknown):string=>createHash('sha256').update(canonical(v)).digest('hex');
`;

