import {readFileSync} from 'node:fs';
import {captureJson,canonicalJson,reject,ProfileRejected,type Json} from './contracts.js';
/** Fixed owner schemas only. Shape is not a registered handle or acceptance.
 * Open questions: docs/BUSINESS-AUTHORING-CONTRACTS.md. */
export const BUSINESS_AUTHORING_SCHEMAS = Object.freeze({
 technicalProfile:'technical-profile-source-v1.schema.json',spec:'business-spec-v1.schema.json',project:'business-authoring-project-v1.schema.json',
 review:'business-review-v1.schema.json',decision:'business-decision-v1.schema.json',
 lock:'business-authoring-lock-v1.schema.json',ledger:'business-lowering-v1.schema.json',
 wire:'operation-json-post-v1.schema.json',package:'profile-package-v3.schema.json',
});
export type BusinessAuthoringSchemaName = keyof typeof BUSINESS_AUTHORING_SCHEMAS;
const schemas=Object.fromEntries(Object.entries(BUSINESS_AUTHORING_SCHEMAS).map(([key,file])=>[key,JSON.parse(readFileSync(new URL('../../contracts/'+file,import.meta.url),'utf8'))])) as Record<BusinessAuthoringSchemaName,Record<string,any>>;
function check(s:Record<string,any>,v:Json,root:Record<string,any>,at:string,depth:number):void {
 if(depth>128)reject('BUSINESS_SCHEMA_BUDGET',at,'schema validation depth exceeded');
 if(s.$ref){const match=/^#\/\$defs\/([A-Za-z][A-Za-z0-9_]*)$/.exec(String(s.$ref));if(!match||!Object.hasOwn(root.$defs??{},match[1]!))reject('BUSINESS_SCHEMA_REF',at,'fixed local schema reference required');return check(root.$defs[match[1]!],v,root,at,depth+1);}
 if(s.oneOf){let count=0;for(const alternative of s.oneOf){try{check(alternative,v,root,at,depth+1);count++;}catch(error){if(!(error instanceof ProfileRejected))throw error;}}if(count!==1)reject('BUSINESS_SCHEMA_VARIANT',at,'one exact variant required');return;}
 if(Object.hasOwn(s,'const')&&canonicalJson(v)!==canonicalJson(s.const))reject('BUSINESS_SCHEMA_CONST',at,'wrong contract version or fixed capability');
 if(s.enum&&!s.enum.some((x:Json)=>canonicalJson(x)===canonicalJson(v)))reject('BUSINESS_SCHEMA_ENUM',at,'unsupported vocabulary');
 const object=v!==null&&typeof v==='object'&&!Array.isArray(v),kind=Array.isArray(v)?'array':v===null?'null':typeof v;
 const kinds=s.type===undefined?[]:Array.isArray(s.type)?s.type:[s.type];
 if(kinds.length&&!kinds.some((k:string)=>k==='integer'?typeof v==='number'&&Number.isSafeInteger(v):k===kind))reject('BUSINESS_SCHEMA_TYPE',at,'incorrect type');
 if(typeof v==='string'&&(s.minLength!==undefined&&v.length<s.minLength||s.maxLength!==undefined&&v.length>s.maxLength||s.pattern&&!new RegExp(s.pattern,'u').test(v)))reject('BUSINESS_SCHEMA_VALUE',at,'invalid string/identifier/path');
 if(typeof v==='number'&&(s.minimum!==undefined&&v<s.minimum||s.maximum!==undefined&&v>s.maximum))reject('BUSINESS_SCHEMA_LIMIT',at,'number outside bounds');
 if(Array.isArray(v)){
  if(s.minItems!==undefined&&v.length<s.minItems||s.maxItems!==undefined&&v.length>s.maxItems)reject('BUSINESS_SCHEMA_LIMIT',at,'array outside bounds');
  if(s.uniqueItems&&new Set(v.map(canonicalJson)).size!==v.length)reject('BUSINESS_SCHEMA_DUPLICATE',at,'duplicate entry');
  if(s.items)v.forEach((child,i)=>check(s.items,child,root,at+'/'+i,depth+1));
 }
 if(object){const data=v as Record<string,Json>,keys=Object.keys(data);
  if(s.minProperties!==undefined&&keys.length<s.minProperties||s.maxProperties!==undefined&&keys.length>s.maxProperties)reject('BUSINESS_SCHEMA_LIMIT',at,'object outside bounds');
  for(const key of s.required??[])if(!Object.hasOwn(data,key))reject('BUSINESS_SCHEMA_REQUIRED',at+'/'+key,'missing field');
  for(const key of keys){if(s.propertyNames)check(s.propertyNames,key,root,at+'/'+key,depth+1);
   if(Object.hasOwn(s.properties??{},key))check(s.properties[key],data[key]!,root,at+'/'+key,depth+1);
   else if(s.additionalProperties===false)reject('BUSINESS_SCHEMA_UNKNOWN',at+'/'+key,'unknown field or executable hook');
   else if(s.additionalProperties&&typeof s.additionalProperties==='object')check(s.additionalProperties,data[key]!,root,at+'/'+key,depth+1);
  }
 }
}
export function validateBusinessAuthoringContract<T>(name:BusinessAuthoringSchemaName,input:unknown):T {
 if(!Object.hasOwn(schemas,name))reject('BUSINESS_SCHEMA_REF','/','unknown fixed owner schema');
 const data=captureJson(input);check(schemas[name],data,schemas[name],'',0);return data as T;
}
