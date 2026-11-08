import assert from 'node:assert/strict';
import test from 'node:test';
import {createRequire,syncBuiltinESMExports} from 'node:module';
import {evaluateProfile,type TypedTable} from '../../src/profile-engine/evaluate.ts';
import {PROFILE_ROLE_CONTRACTS,type ProfilePackage} from '../../src/profile-engine/contracts.ts';

// Open questions: PE07 actual checked carrier joins. This is finite metadata evaluation.
const pack=(rules:any[],budget:any={}):ProfilePackage=>({schema_version:'craft.profile-package/v1',id:'GenericPackage',version:'1.0.0',engine:'craft.profile-engine/v1',conflict_policy:'reject',dependencies:[],capabilities:[{role:'http-entry',descriptor_ref:PROFILE_ROLE_CONTRACTS['http-entry'].descriptor_ref,recipe_ref:PROFILE_ROLE_CONTRACTS['http-entry'].recipe_ref}],budgets:{operations:1000,rows:100,join_pairs:100,depth:16,bytes:65536,...budget},rules,assets:[]});
const tables:Record<string,TypedTable>={intents:{fields:{id:'string',kind:'string'},rows:[{id:'quote',kind:'public'},{id:'terms',kind:'public'}]},bindings:{fields:{id:'string',source:'string'},rows:[{id:'quote',source:'quote.alch'},{id:'terms',source:'terms.alch'}]}};
const pipeline=[{id:'select',op:'select',from:'intents',as:'selected',where:{field:['kind'],equals:'public'}},{id:'join',op:'join',left:'selected',right:'bindings',on:{left:['id'],right:['id']},cardinality:'one',as:'joined'},{id:'project',op:'project',from:'joined',as:'entries',fields:{id:{field:['left','id']},source:{field:['right','source']},route:{concat:[{literal:'/'},{field:['left','id']}]}}},{id:'emit',op:'emit',from:'entries',role:'http-entry',fields:{id:{field:['id']},source:{field:['source']},route:{field:['route']}}}];
test('typed select, join, project and emission are deterministic',()=>{
 const a=evaluateProfile(pack(pipeline),tables),b=evaluateProfile(pack(pipeline),tables);assert.equal(a.sha256,b.sha256);assert.deepEqual(a.emissions.map(e=>({...e.fields})),[{id:'quote',source:'quote.alch',route:'/quote'},{id:'terms',source:'terms.alch',route:'/terms'}]);assert.equal(a.join_pairs,4);
});
test('defaults and require-one preserve exact typed values and reject ambiguous cardinality',()=>{
 const value=evaluateProfile(pack([{id:'defaults',op:'defaults',as:'config',values:{method:'POST'}},{id:'one',op:'require-one',from:'config',as:'only'}]),{});assert.equal(value.tables.only!.rows[0]!.method,'POST');
 assert.throws(()=>evaluateProfile(pack([{id:'one',op:'require-one',from:'intents',as:'only'}]),tables),/PROFILE_CARDINALITY/);
 assert.throws(()=>evaluateProfile(pack([{id:'defaults',op:'defaults',as:'intents',values:{id:'changed'}}]),tables),/PROFILE_TABLE_CONFLICT/);
});
test('static typing rejects missing fields even in an empty table, wrong comparisons and joins',()=>{
 const empty={intents:{fields:{id:'string'},rows:[]}} as Record<string,TypedTable>;
 assert.throws(()=>evaluateProfile(pack([{id:'project',op:'project',from:'intents',as:'out',fields:{value:{field:['missing']}}}]),empty),/PROFILE_FIELD_UNKNOWN/);
 assert.throws(()=>evaluateProfile(pack([{id:'select',op:'select',from:'intents',as:'out',where:{field:['id'],equals:3}}]),tables),/PROFILE_SELECT_TYPE/);
 assert.throws(()=>evaluateProfile(pack(pipeline),{...tables,bindings:{fields:{id:'number',source:'string'},rows:[]}}),/PROFILE_JOIN_TYPE/);
 assert.throws(()=>evaluateProfile(pack([{id:'project',op:'project',from:'intents',as:'out',fields:{value:{concat:[{literal:7}]}}}]),tables),/PROFILE_CONCAT_TYPE/);
});
test('required joins reject missing or ambiguous bindings',()=>{
 assert.throws(()=>evaluateProfile(pack(pipeline),{...tables,bindings:{...tables.bindings!,rows:[]}}),/PROFILE_JOIN_AMBIGUOUS/);
 assert.throws(()=>evaluateProfile(pack(pipeline),{...tables,bindings:{...tables.bindings!,rows:[...tables.bindings!.rows,...tables.bindings!.rows]}}),/PROFILE_JOIN_AMBIGUOUS/);
});
test('bounded graph traversal preserves typed reachability and rejects cycles/unknown targets',()=>{
 const nodes={fields:{id:'string'},rows:[{id:'A'},{id:'B'},{id:'C'}]} as TypedTable;
 const edges={fields:{from:'string',to:'string'},rows:[{from:'A',to:'B'},{from:'B',to:'C'}]} as TypedTable;
 const rules=[{id:'walk',op:'traverse',from:'nodes',edges:'edges',as:'walked',max_depth:3}];const result=evaluateProfile(pack(rules),{nodes,edges});assert.equal(result.tables.walked!.rows.length,3);
 assert.throws(()=>evaluateProfile(pack(rules),{nodes,edges:{...edges,rows:[...edges.rows,{from:'C',to:'A'}]}}),/PROFILE_TRAVERSE_CYCLE/);
 assert.throws(()=>evaluateProfile(pack(rules),{nodes,edges:{...edges,rows:[{from:'A',to:'unknown'}]}}),/PROFILE_TRAVERSE_TARGET/);
 assert.throws(()=>evaluateProfile(pack([{...rules[0],max_depth:1}]),{nodes,edges}),/PROFILE_TRAVERSE_DEPTH/);
});
test('operation, join-product, row and byte budgets are enforced',()=>{
 for(const [limit,value,code] of [['operations',1,'PROFILE_OPERATION_BUDGET'],['join_pairs',1,'PROFILE_JOIN_BUDGET'],['rows',1,'PROFILE_OUTPUT_BUDGET'],['bytes',1,'PROFILE_OUTPUT_BUDGET']] as const)assert.throws(()=>evaluateProfile(pack(pipeline,{[limit]:value}),tables),new RegExp(code));
});
test('evaluation performs no filesystem, network or process operations',()=>{
 const require=createRequire(import.meta.url),undo:Array<()=>void>=[];let attempts=0;
 const trap=(object:any,key:string)=>{const old=object[key];object[key]=()=>{attempts++;throw Error('FORBIDDEN:'+key);};undo.push(()=>object[key]=old);};
 for(const key of ['readFileSync','writeFileSync','mkdirSync','openSync','statSync'])trap(require('node:fs'),key);for(const key of ['execFileSync','spawnSync','exec','spawn'])trap(require('node:child_process'),key);trap(globalThis,'fetch');syncBuiltinESMExports();
 try{assert.equal(evaluateProfile(pack(pipeline),tables).emissions.length,2);assert.equal(attempts,0);}finally{for(const restore of undo)restore();syncBuiltinESMExports();}
});

test('registered carrier fields and selector type vocabulary reject unsupported metadata',()=>{
 assert.throws(()=>evaluateProfile(pack([{id:'emit',op:'emit',from:'intents',role:'http-entry',fields:{id:{literal:7},source:{literal:'x.alch'},route:{literal:'/x'}}}]),tables),/PROFILE_CARRIER_FIELD_TYPE/);
 assert.throws(()=>evaluateProfile(pack([{id:'emit',op:'emit',from:'intents',role:'http-entry',fields:{id:{field:['id']},source:{literal:'x.alch'},route:{literal:'/x'},native_business_code:{literal:'execute'}}}]),tables),/PROFILE_CARRIER_FIELD_UNKNOWN/);
 assert.throws(()=>evaluateProfile(pack([{id:'defaults',op:'defaults',as:'config',values:{method:'POST'}}]),{bad:{fields:{id:'javascript' as any},rows:[]}}),/PROFILE_TABLE_SCHEMA_TYPE/);
});
