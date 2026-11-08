import {ruleEligibleSubmission as guard0} from "../../domain/rules/eligible-submission.js";
import {createSubmissionFactory as ownedImport1} from "../../domain/entities/submission.js";
// structured-rule-capability:base
type RuleProtocol<T> = Readonly<{normalize:(input:unknown)=>T;key:(value:T)=>string}>;
const rulePart = (value:string):string=>value.length+':'+value;
const ruleData = (input:unknown,allowed:readonly string[]):Record<string,PropertyDescriptor>=>{
  if(input===null||typeof input!=='object'||Array.isArray(input)||![Object.prototype,null].includes(Object.getPrototypeOf(input))) throw new TypeError('OPERATION_INPUT');
  const descriptors=Object.getOwnPropertyDescriptors(input);
  if(Reflect.ownKeys(descriptors).some(key=>typeof key!=='string'||!allowed.includes(key))||Object.values(descriptors).some(d=>!Object.hasOwn(d,'value')||!d.enumerable)) throw new TypeError('OPERATION_INPUT');
  return descriptors;
};
// structured-rule-capability:Bool
const ruleBool:RuleProtocol<boolean> = Object.freeze({normalize:(input:unknown):boolean=>{if(typeof input!=='boolean')throw new TypeError('OPERATION_INPUT');return input;},key:(value:boolean):string=>rulePart('Bool')+rulePart(value?'1':'0')});
// structured-rule-capability:UInt64
const ruleUInt64:RuleProtocol<bigint> = Object.freeze({
  normalize:(input:unknown):bigint=>{
    let value:bigint;
    if(typeof input==='bigint')value=input;
    else if(typeof input==='number'&&Number.isSafeInteger(input))value=BigInt(input);
    else if(typeof input==='string'&&input.length<=20&&/^(0|[1-9][0-9]*)$/.exec(input)?.[0]===input)value=BigInt(input);
    else throw new TypeError('OPERATION_INPUT');
    if(value<0n||value>18446744073709551615n)throw new TypeError('OPERATION_INPUT');
    return value;
  },key:(value:bigint):string=>rulePart('UInt64')+rulePart(String(value)),
});
// end structured Rule support
type R2 = Readonly<{readonly "accepted":boolean;readonly "id":bigint}>;
type R2Input = Readonly<{readonly "accepted":boolean;readonly "id":bigint|number|string}>;
const R2Value:RuleProtocol<R2> = Object.freeze({
  normalize:(input:unknown):R2=>{
    const d=ruleData(input,["accepted","id"]);
    return Object.freeze({["accepted"]:ruleBool.normalize(Object.hasOwn(d,"accepted")?d["accepted"]!.value:undefined),["id"]:ruleUInt64.normalize(Object.hasOwn(d,"id")?d["id"]!.value:undefined)});
  },key:(value:R2):string=>rulePart("Entity")+rulePart("lab:submission")+rulePart("id")+rulePart(ruleUInt64.key(value["id"])),
});
const own2=(v:bigint)=>(v);
const own3=(v:boolean)=>(v);
const own0Factory=ownedImport1();
const own0=(v:R2)=>{const result=own0Factory.create({["id"]:own2(v["id"]),["accepted"]:own3(v["accepted"])});if(!result.ok)throw new TypeError("OPERATION_VALUE:"+result.failure_codes.join(","));return result.value;};
const captureData=(input:unknown):unknown=>{
  let count=0;
  const copy=(v:unknown,depth:number):unknown=>{
    if(++count>20000||depth>64)throw new TypeError("OPERATION_INPUT");
    if(v===null||typeof v==="string"||typeof v==="boolean"||typeof v==="bigint"||typeof v==="number"&&Number.isFinite(v))return v;
    if(!v||typeof v!=="object")throw new TypeError("OPERATION_INPUT");
    const array=Array.isArray(v),proto=Object.getPrototypeOf(v);
    if(array?proto!==Array.prototype:proto!==Object.prototype&&proto!==null)throw new TypeError("OPERATION_INPUT");
    const d=Object.getOwnPropertyDescriptors(v),keys=Reflect.ownKeys(d);
    if(keys.length>2048)throw new TypeError("OPERATION_INPUT");
    if(array){const length=d.length!.value;if(length>1024||keys.length!==length+1)throw new TypeError("OPERATION_INPUT");const result:unknown[]=[];for(let i=0;i<length;i++){const p=d[String(i)];if(!p||!Object.hasOwn(p,"value")||!p.enumerable)throw new TypeError("OPERATION_INPUT");result.push(copy(p.value,depth+1));}return Object.freeze(result);}
    const result:Record<string,unknown>=Object.create(null);
    for(const k of keys){const p=d[k as string];if(typeof k!=="string"||!p||!Object.hasOwn(p,"value")||!p.enumerable)throw new TypeError("OPERATION_INPUT");result[k]=copy(p.value,depth+1);}return Object.freeze(result);
  };return copy(input,0);
};
export type OperationInput=Readonly<{readonly "request":R2Input}>;
export type OperationValue=R2;
export type ReadRequest=Readonly<{slot:"lab:submission";target:"lab:submission";key:bigint}>;
export type WriteIntent=Readonly<{slot:"lab:submission";target:"lab:submission";mode:"replace";value:R2}>;
export type EventIntent=never;
export type OperationBatch=Readonly<{writes:readonly WriteIntent[];events:readonly EventIntent[]}>;
export type CommitReceipt=Readonly<{status:"committed"|"rejected"|"indeterminate"}>;
export type Transaction=Readonly<{read:(request:ReadRequest)=>Promise<unknown>;commit:(batch:OperationBatch)=>Promise<CommitReceipt>;rollback:()=>Promise<void>}>;
export type OperationDependencies=Readonly<{store:Readonly<{begin:()=>Promise<Transaction>}>}>;
export type OperationFailure=Readonly<{status:"rejected"|"failed"|"indeterminate";stage:string;code:string;continuation:"return-submission-error";cleanupFailed:boolean}>;
export type OperationOutcome=Readonly<{status:"committed";value:OperationValue}>|OperationFailure;
export const execute=async (parameters:OperationInput,dependencies:OperationDependencies):Promise<OperationOutcome>=>{
  let stage="input";
  const failure=(status:OperationFailure["status"],code:string,cleanupFailed=false):OperationFailure=>Object.freeze({status,stage,code,continuation:"return-submission-error",cleanupFailed});
  let captured:Record<string,unknown>;
  let p0:R2;
  try {captured=captureData(parameters) as Record<string,unknown>;const d=ruleData(captured,["request"]);if(Object.keys(d).length!==1)throw new TypeError("OPERATION_INPUT");
    p0=R2Value.normalize(d["request"]!.value);
  }catch{return failure("failed","OPERATION_INPUT");}
  stage="begin";let transaction:Transaction;
  try{transaction=await dependencies.store.begin();}catch{return failure("failed","BEGIN_FAILED");}
  const abort=async(status:OperationFailure["status"],code:string):Promise<OperationFailure>=>{try{await transaction.rollback();return failure(status,code);}catch{return failure(status,code,true);}};
  let commitAttempted=false;
  try{
    stage="read";
    const key0=ruleUInt64.normalize(p0["id"]);
    const raw0=await transaction.read(Object.freeze({slot:"lab:submission",target:"lab:submission",key:key0}));
    if(raw0===null)return abort("failed","READ_NOT_FOUND");
    const read0=R2Value.normalize(raw0);
    if(ruleUInt64.key(read0["id"])!==ruleUInt64.key(key0))return abort("failed","READ_IDENTITY_MISMATCH");
    stage="guard";
    if(!guard0({["submission"]:read0}))return abort("rejected","RULE_REJECTED:lab:eligible-submission");
    stage="write-validation";
    const write0=R2Value.normalize(p0);
    own0(write0);
    if(ruleUInt64.key(write0["id"])!==ruleUInt64.key(key0))return abort("failed","WRITE_IDENTITY_MISMATCH");
    stage="event";
    stage="result";const result=R2Value.normalize(p0);
    own0(result);
    const batch:OperationBatch=Object.freeze({writes:Object.freeze([Object.freeze({slot:"lab:submission",target:"lab:submission",mode:"replace",value:write0})]),events:Object.freeze([])});
    stage="commit";commitAttempted=true;
    const receipt=await transaction.commit(batch);
    const d=ruleData(receipt,["status"]);if(Object.keys(d).length!==1)return failure("indeterminate","INVALID_COMMIT_RECEIPT");
    if(d.status!.value==="committed")return Object.freeze({status:"committed",value:result});
    if(d.status!.value==="rejected")return failure("rejected","COMMIT_REJECTED");
    return failure("indeterminate",d.status!.value==="indeterminate"?"COMMIT_INDETERMINATE":"INVALID_COMMIT_RECEIPT");
  }catch{return commitAttempted?failure("indeterminate","COMMIT_UNCERTAIN"):abort("failed","OPERATION_FAILED");}
};
