import {spawnSync} from 'node:child_process';
import {digest} from './verified-projection.mjs';
export function validateSchemaBatch(documents){
 const schemas={};const values=[];
 const walk=value=>{if(value&&typeof value==='object')for(const [key,member]of Object.entries(value)){
  if(key==='$ref'&&!member.startsWith('#'))throw Error('unqualified-schema-reference');walk(member);
 }};
 for(const {schema,bytes}of documents){
  walk(schema);const id=digest(Buffer.from(JSON.stringify(schema)));schemas[id]=schema;
  values.push({schema:id,value:JSON.parse(Buffer.from(bytes))});
 }
 const child=spawnSync('python3',['-B','-c',
 'import json,sys,jsonschema; x=json.load(sys.stdin); v={k:jsonschema.Draft202012Validator(s) for k,s in x["schemas"].items()}; [jsonschema.Draft202012Validator.check_schema(s) for s in x["schemas"].values()]; [v[item["schema"]].validate(item["value"]) for item in x["values"]]'],
 {input:JSON.stringify({schemas,values}),encoding:'utf8',maxBuffer:2*1024*1024});
 if(child.status!==0)throw Error('schema-validation-failed: '+(child.stderr||child.error).toString().slice(-1200));
 return documents.map(item=>digest(item.bytes));
}
export function validateSchema(schema,bytes){return validateSchemaBatch([{schema,bytes}])[0];}
