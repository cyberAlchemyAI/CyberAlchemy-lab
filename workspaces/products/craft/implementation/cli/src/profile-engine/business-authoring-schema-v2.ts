import {readFileSync} from 'node:fs';
import {captureJson,canonicalJson,ProfileRejected,reject,type Json} from './contracts.js';
import type {BusinessSpecDataV2} from './business-authoring-protocol-v2.js';
import type {BusinessCaptureManifestV2,BusinessReviewSubjectV2,BusinessDecisionV2,BusinessAuthoringLockV2} from './business-authoring-identity-protocol-v2.js';
/** Finite fixed owner schemas only; schema capture is data, not registered custody.
 * Open Questions: docs/BUSINESS-IDENTITIES-V2.md. */
export const BUSINESS_AUTHORING_SCHEMAS_V2=Object.freeze({spec:'business-spec-v2.schema.json',capture:'business-capture-v2.schema.json',review:'business-review-v2.schema.json',decision:'business-decision-v2.schema.json',lock:'business-authoring-lock-v2.schema.json'});
export interface BusinessContractDataV2 {spec:BusinessSpecDataV2;capture:BusinessCaptureManifestV2;review:BusinessReviewSubjectV2;decision:BusinessDecisionV2;lock:BusinessAuthoringLockV2}
type Schema=Readonly<Record<string,any>>;
const schemas=Object.fromEntries(Object.entries(BUSINESS_AUTHORING_SCHEMAS_V2).map(([name,file])=>[name,JSON.parse(readFileSync(new URL('../../contracts/'+file,import.meta.url),'utf8'))])) as Record<keyof BusinessContractDataV2,Schema>;
function check(s:Schema,value:Json,root:Schema,at:string,depth:number):void {
 if(depth>128)reject('BUSINESS_V2_SCHEMA_BUDGET',at,'fixed schema depth exceeded');
 if(s.$ref){const match=/^#\/\$defs\/([A-Za-z][A-Za-z0-9_]*)$/.exec(s.$ref);if(!match||!Object.hasOwn(root.$defs??{},match[1]!))reject('BUSINESS_V2_SCHEMA_REF',at,'fixed local owner reference required');return check(root.$defs[match![1]!],value,root,at,depth+1);}
 if(s.oneOf){let count=0;for(const variant of s.oneOf){try{check(variant,value,root,at,depth+1);count++;}catch(e){if(!(e instanceof ProfileRejected))throw e;}}if(count!==1)reject('BUSINESS_V2_SCHEMA_VARIANT',at,'one exact variant required');return;}
 if(Object.hasOwn(s,'const')&&canonicalJson(value)!==canonicalJson(s.const))reject('BUSINESS_V2_SCHEMA_CONST',at,'wrong fixed contract');
 if(s.enum&&!s.enum.some((v:Json)=>canonicalJson(value)===canonicalJson(v)))reject('BUSINESS_V2_SCHEMA_ENUM',at,'unsupported value');
 const object=value!==null&&typeof value==='object'&&!Array.isArray(value),kind=Array.isArray(value)?'array':value===null?'null':typeof value;
 const allowed=s.type===undefined?[]:Array.isArray(s.type)?s.type:[s.type];
 if(allowed.length&&!allowed.some((k:string)=>k==='integer'?typeof value==='number'&&Number.isSafeInteger(value):k===kind))reject('BUSINESS_V2_SCHEMA_TYPE',at,'incorrect type');
 if(typeof value==='string'){
  if(/[\uD800-\uDFFF]/u.test(value))reject('BUSINESS_V2_SCHEMA_UNICODE',at,'Unicode scalar string required');
  const length=[...value].length;
  if(s.minLength!==undefined&&length<s.minLength||s.maxLength!==undefined&&length>s.maxLength||s.pattern&&!new RegExp(s.pattern,'u').test(value))reject('BUSINESS_V2_SCHEMA_VALUE',at,'string outside fixed contract');
 }
 if(typeof value==='number'&&(s.minimum!==undefined&&value<s.minimum||s.maximum!==undefined&&value>s.maximum))reject('BUSINESS_V2_SCHEMA_LIMIT',at,'number outside fixed domain');
 if(Array.isArray(value)){
  if(s.minItems!==undefined&&value.length<s.minItems||s.maxItems!==undefined&&value.length>s.maxItems)reject('BUSINESS_V2_SCHEMA_LIMIT',at,'array outside fixed bounds');
  if(s.uniqueItems&&new Set(value.map(canonicalJson)).size!==value.length)reject('BUSINESS_V2_SCHEMA_DUPLICATE',at,'duplicate member');
  if(s.items)value.forEach((v,i)=>check(s.items,v,root,at+'/'+i,depth+1));
 }
 if(object){const data=value as Record<string,Json>;
  for(const field of s.required??[])if(!Object.hasOwn(data,field))reject('BUSINESS_V2_SCHEMA_REQUIRED',at+'/'+field,'required field missing');
  for(const field of Object.keys(data)){
   if(Object.hasOwn(s.properties??{},field))check(s.properties[field],data[field]!,root,at+'/'+field,depth+1);
   else if(s.additionalProperties===false)reject('BUSINESS_V2_SCHEMA_UNKNOWN',at+'/'+field,'unknown field or executable hook');
   else if(s.additionalProperties&&typeof s.additionalProperties==='object')check(s.additionalProperties,data[field]!,root,at+'/'+field,depth+1);
  }
 }
}
export function validateBusinessAuthoringContractV2<K extends keyof BusinessContractDataV2>(name:K,input:unknown):BusinessContractDataV2[K] {
 if(!Object.hasOwn(schemas,name))reject('BUSINESS_V2_SCHEMA_REF','/','unknown fixed schema');
 const data=captureJson(input);check(schemas[name],data,schemas[name],'',0);return data as unknown as BusinessContractDataV2[K];
}
