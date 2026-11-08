import {captureJson,canonicalJson,dataDigest,reject,validateProfilePackage,type Json,type Expression,type ProfilePackage,type Role} from './contracts.js';
import {validateProfilePackageInput,type ProfilePackageV2} from './contracts-v2.js';
import {validateProfilePackageV3,type ProfilePackageV3} from './contracts-v3.js';

/** Pure finite metadata evaluation; semantic carrier checks occur in compose.
 * Open questions: PE07 registered carriers; no graph admission follows from tables. */
export type ValueType='string'|'number'|'boolean'|'null'|'json'|Readonly<{record:Readonly<Record<string,ValueType>>}>|Readonly<{array:ValueType}>;
export interface TypedTable {readonly fields:Readonly<Record<string,ValueType>>;readonly rows:readonly Readonly<Record<string,Json>>[]}
export interface Emission {readonly rule:string;readonly role:Role;readonly fields:Readonly<Record<string,Json>>;readonly types:Readonly<Record<string,ValueType>>}
export interface Evaluation {readonly emissions:readonly Emission[];readonly tables:Readonly<Record<string,TypedTable>>;readonly operations:number;readonly join_pairs:number;readonly sha256:string}
const own=(o:object,k:string)=>Object.hasOwn(o,k);
function checkType(type:ValueType,depth=0):void {if(depth>64)reject('PROFILE_TABLE_SCHEMA_DEPTH','/','selector schema depth exceeded');if(typeof type==='string'){if(!['string','number','boolean','null','json'].includes(type))reject('PROFILE_TABLE_SCHEMA_TYPE','/','unknown selector type');return;}if(!type||typeof type!=='object'||Object.keys(type).length!==1)reject('PROFILE_TABLE_SCHEMA_TYPE','/','one declared type constructor required');if('array' in type)checkType(type.array,depth+1);else if('record' in type&&type.record&&typeof type.record==='object'&&!Array.isArray(type.record))for(const t of Object.values(type.record))checkType(t,depth+1);else reject('PROFILE_TABLE_SCHEMA_TYPE','/','record/array type required');}
function typeOf(v:Json):ValueType {if(v===null)return 'null';if(Array.isArray(v)){const types=v.map(typeOf);return {array:types.length&&types.every(t=>dataDigest(t)===dataDigest(types[0]))?types[0]!:'json'};}if(typeof v==='object')return {record:Object.fromEntries(Object.entries(v).map(([k,value])=>[k,typeOf(value)]))};return typeof v as 'string'|'number'|'boolean';}
function conforms(v:Json,type:ValueType):boolean {
 if(type==='json')return true;if(typeof type==='string')return type==='null'?v===null:typeof v===type;
 if('array' in type)return Array.isArray(v)&&v.every(x=>conforms(x,type.array));
 return v!==null&&typeof v==='object'&&!Array.isArray(v)&&Object.keys(v).length===Object.keys(type.record).length&&Object.entries(type.record).every(([k,t])=>own(v,k)&&conforms((v as Record<string,Json>)[k]!,t));
}
function fieldType(fields:Readonly<Record<string,ValueType>>,parts:readonly string[]):ValueType {
 let current:ValueType={record:fields};for(const part of parts){if(typeof current==='string'||!('record' in current)||!own(current.record,part))reject('PROFILE_FIELD_UNKNOWN',parts.join('.'),'field must exist in declared selector schema');current=current.record[part]!;}return current;
}
function expressionType(e:Expression,fields:Readonly<Record<string,ValueType>>):ValueType {
 if('literal' in e)return typeOf(e.literal);if('field' in e)return fieldType(fields,e.field);
 for(const child of e.concat)if(expressionType(child,fields)!=='string')reject('PROFILE_CONCAT_TYPE','/concat','metadata concatenation accepts strings only');return 'string';
}
function read(row:Readonly<Record<string,Json>>,parts:readonly string[]):Json {let value:Json=row;for(const p of parts){if(value===null||typeof value!=='object'||Array.isArray(value)||!own(value,p))reject('PROFILE_FIELD_UNKNOWN',parts.join('.'),'missing required metadata field');value=(value as Record<string,Json>)[p]!;}return value;}

const roleFields:Readonly<Record<Role,Readonly<{required:Readonly<Record<string,ValueType>>;optional:Readonly<Record<string,ValueType>>}>>>=Object.freeze({
 'domain-function':{required:{id:'string',source:'string',output_prefix:'string'},optional:{technical:'json'}},
 'http-entry':{required:{id:'string',source:'string',route:'string'},optional:{method:'string',intent_ref:'string',component_id:'string',technical:'json',template_ref:'string',artifact_path:'string'}},
 'http-dispatch':{required:{id:'string',artifact_path:'string'},optional:{template_ref:'string',technical:'json'}},
 'shared-http-port':{required:{id:'string',artifact_path:'string'},optional:{template_ref:'string',technical:'json'}},
 'external-read':{required:{id:'string',source:'string'},optional:{intent_ref:'string',technical:'json'}},
 'application-operation':{required:{id:'string',project_ref:'string',selector:'string'},optional:{artifact_path:'string',technical:'json',route:'string'}},
 'environment':{required:{id:'string',slot:'string',source:'string'},optional:{technical:'json'}},
 'operational-expectation':{required:{id:'string',declaration:'json'},optional:{}},
});
function checkEmissionTypes(role:Role,fields:Readonly<Record<string,ValueType>>,rule:string):void {
 const schema=roleFields[role];for(const [key,type] of Object.entries(schema.required)){if(!own(fields,key))reject('PROFILE_CARRIER_FIELD_REQUIRED',rule,`missing ${role}.${key}`);if(type!=='json'&&dataDigest(fields[key])!==dataDigest(type))reject('PROFILE_CARRIER_FIELD_TYPE',rule,`${role}.${key} has incompatible type`);}
 for(const [key,type] of Object.entries(fields)){const expected=schema.required[key]??schema.optional[key];if(!expected)reject('PROFILE_CARRIER_FIELD_UNKNOWN',rule,`unknown ${role}.${key}`);if(expected!=='json'&&dataDigest(type)!==dataDigest(expected))reject('PROFILE_CARRIER_FIELD_TYPE',rule,`${role}.${key} has incompatible type`);}
}

export function evaluateProfile(input:ProfilePackage|ProfilePackageV2|ProfilePackageV3,inputTables:Readonly<Record<string,TypedTable>>):Evaluation {
 const pack=input.schema_version==='craft.profile-package/v3-candidate'?validateProfilePackageV3(input):validateProfilePackageInput(input),captured=captureJson(inputTables) as unknown as Readonly<Record<string,TypedTable>>;
 const tables:Record<string,TypedTable>=Object.create(null),emissions:Emission[]=[];let operations=0,pairs=0,bytes=0,rows=0;
 const step=(n=1)=>{operations+=n;if(operations>pack.budgets.operations)reject('PROFILE_OPERATION_BUDGET','/','operation budget exhausted');};
 const add=(name:string,table:TypedTable)=>{if(own(tables,name))reject('PROFILE_TABLE_CONFLICT',name,'one table owner required');rows+=table.rows.length;bytes+=Buffer.byteLength(canonicalJson(captureJson(table)));if(rows>pack.budgets.rows||bytes>pack.budgets.bytes)reject('PROFILE_OUTPUT_BUDGET',name,'row/byte budget exhausted');tables[name]=Object.freeze({fields:table.fields,rows:Object.freeze([...table.rows])});};
 for(const [name,table] of Object.entries(captured)){
  if(!table||!table.fields||!Array.isArray(table.rows))reject('PROFILE_TABLE_SHAPE',name,'declared fields and rows required');
  checkType({record:table.fields});
  for(const row of table.rows){step();if(!conforms(row,{record:table.fields}))reject('PROFILE_TABLE_TYPE',name,'row differs from declared selector schema');}add(name,table);
 }
 const get=(name:string):TypedTable=>{if(!own(tables,name))reject('PROFILE_TABLE_UNKNOWN',name,'unknown table');return tables[name]!;};
 const expr=(e:Expression,row:Readonly<Record<string,Json>>):Json=>{step();if('literal' in e)return e.literal;if('field' in e)return read(row,e.field);return e.concat.map(c=>expr(c,row)).join('');};
 const projected=(fields:Readonly<Record<string,Expression>>,table:TypedTable)=>{const types=Object.fromEntries(Object.entries(fields).map(([k,e])=>[k,expressionType(e,table.fields)]));const out=table.rows.map(row=>Object.freeze(Object.fromEntries(Object.entries(fields).map(([k,e])=>[k,expr(e,row)]))));return {fields:types,rows:out};};
 for(const rule of pack.rules){step();
  switch(rule.op){
   case 'select':{const source=get(rule.from);if(rule.where){const t=fieldType(source.fields,rule.where.field);if(!conforms(rule.where.equals,t))reject('PROFILE_SELECT_TYPE',rule.id,'selector comparison type differs');}add(rule.as,{fields:source.fields,rows:source.rows.filter(row=>{step();return !rule.where||canonicalJson(read(row,rule.where.field))===canonicalJson(rule.where.equals);})});break;}
   case 'project':add(rule.as,projected(rule.fields,get(rule.from)));break;
   case 'defaults':{add(rule.as,{fields:Object.fromEntries(Object.entries(rule.values).map(([k,v])=>[k,typeOf(v)])),rows:[rule.values]});break;}
   case 'require-one':{const source=get(rule.from);if(source.rows.length!==1)reject('PROFILE_CARDINALITY',rule.id,'exactly one row required');add(rule.as,source);break;}
   case 'join':{const left=get(rule.left),right=get(rule.right);if(!['string','number','boolean','null'].includes(String(fieldType(left.fields,rule.on.left))))reject('PROFILE_JOIN_KEY_UNSUPPORTED',rule.id,'join keys must be scalar metadata');if(dataDigest(fieldType(left.fields,rule.on.left))!==dataDigest(fieldType(right.fields,rule.on.right)))reject('PROFILE_JOIN_TYPE',rule.id,'join key types differ');const out:Readonly<Record<string,Json>>[]=[];
    for(const l of left.rows){const matches:Readonly<Record<string,Json>>[]=[];for(const r of right.rows){step();if(++pairs>pack.budgets.join_pairs)reject('PROFILE_JOIN_BUDGET',rule.id,'join-product budget exhausted');if(canonicalJson(read(l,rule.on.left))===canonicalJson(read(r,rule.on.right)))matches.push(r);}
     if(rule.cardinality==='one'&&matches.length!==1)reject('PROFILE_JOIN_AMBIGUOUS',rule.id,'required join must resolve exactly one row');for(const r of matches)out.push(Object.freeze({left:l,right:r}));}
    add(rule.as,{fields:{left:{record:left.fields},right:{record:right.fields}},rows:out});break;}
   case 'traverse':{const source=get(rule.from),edges=get(rule.edges);if(fieldType(source.fields,['id'])!=='string'||fieldType(edges.fields,['from'])!=='string'||fieldType(edges.fields,['to'])!=='string')reject('PROFILE_TRAVERSE_TYPE',rule.id,'id/from/to must be strings');const nodes=new Map<string,Readonly<Record<string,Json>>>();for(const row of source.rows){const id=read(row,['id']) as string;if(nodes.has(id))reject('PROFILE_TRAVERSE_DUPLICATE',rule.id,'unique node ids required');nodes.set(id,row);}const out:Readonly<Record<string,Json>>[]=[];for(const edge of edges.rows)if(!nodes.has(read(edge,['from']) as string)||!nodes.has(read(edge,['to']) as string))reject('PROFILE_TRAVERSE_TARGET',rule.id,'all edge endpoints must resolve');
    for(const root of source.rows){const queue:[string,number,readonly string[]][]=[[read(root,['id']) as string,0,[]]],seen=new Set<string>();while(queue.length){step();const [id,depth,ancestors]=queue.shift()!;if(ancestors.includes(id))reject('PROFILE_TRAVERSE_CYCLE',rule.id,'cycle in traversal');if(seen.has(id))continue;seen.add(id);if(depth>rule.max_depth||depth>pack.budgets.depth)reject('PROFILE_TRAVERSE_DEPTH',rule.id,'traversal depth exhausted');if(!nodes.has(id))reject('PROFILE_TRAVERSE_TARGET',id,'unknown edge target');if(depth)out.push(Object.freeze({root:read(root,['id']),node:nodes.get(id)!}));for(const edge of edges.rows){step();if(read(edge,['from'])===id)queue.push([read(edge,['to']) as string,depth+1,[...ancestors,id]]);}}}
    add(rule.as,{fields:{root:'string',node:{record:source.fields}},rows:out});break;}
   case 'emit':{const source=get(rule.from),out=projected(rule.fields,source);checkEmissionTypes(rule.role,out.fields,rule.id);for(const fields of out.rows){step();bytes+=Buffer.byteLength(canonicalJson(fields));if(emissions.length>=pack.budgets.rows||bytes>pack.budgets.bytes)reject('PROFILE_OUTPUT_BUDGET',rule.id,'emission budget exhausted');emissions.push(Object.freeze({rule:rule.id,role:rule.role,fields,types:out.fields}));}break;}
  }
 }
 const result={emissions:Object.freeze(emissions),tables:Object.freeze(tables),operations,join_pairs:pairs};return Object.freeze({...result,sha256:dataDigest(result)});
}
