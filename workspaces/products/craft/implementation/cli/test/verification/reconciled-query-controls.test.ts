import assert from 'node:assert/strict';
import fs from 'node:fs';import os from 'node:os';import path from 'node:path';import test from 'node:test';
import {execFileSync} from 'node:child_process';import {createRequire} from 'node:module';
import {publicSelection} from '../helpers/composition-project.ts';
import {loadCompiledProjectGraph} from '../../src/input/project-model.ts';
import {planCompiledReconciledProject} from '../../src/generation/reconciled-project.ts';
import {createReconciledSemanticControls} from '../../src/verification/reconciled-semantic-controls.ts';
const project=path.resolve(import.meta.dirname,'../../../..');
const scalar=(name='String'):any=>({kind:'scalar',name}),named=(id:string):any=>({kind:'named',selector:'alpha:'+id}),wrap=(kind:string,element:any):any=>({kind,element});
const property=(name:string,type:any,identity=false):any=>({name,type,identity,cardinality:type.kind==='optional'?'optional':type.kind==='list'?'many':type.kind==='set'?'many-unique':'one',meaning:name,ontology_property:'TEST-ROW#'+name});
const field=(name:string):any=>({kind:'field',name}),param=(name:string):any=>({kind:'parameter',name}),literal=(type:string,value:string|number|boolean):any=>({kind:'literal',type,value}),cmp=(op:string,left:any,right:any):any=>({op,left,right});
function fixture(t:any,moduleRoot='domain',minimal=false){
 const temp=fs.mkdtempSync(path.join(os.tmpdir(),'ds-query-controls-')),source=path.join(temp,'source'),nodes:string[]=[],edges:string[]=[],contracts:any={};
 t.after(()=>fs.rmSync(temp,{recursive:true,force:true}));
 const write=(p:string,v:any)=>{const f=path.join(source,p);fs.mkdirSync(path.dirname(f),{recursive:true});fs.writeFileSync(f,JSON.stringify(v)+'\n');};
 const node=(id:string,kind:string,body:any)=>{if(!nodes.includes(id))nodes.push(id);write('specs/alpha/nodes/'+id+'.json',{schema_version:'domainspec.node/v1',feature_id:'alpha',node_id:id,kind,body:{description:id,...body}});};
 const edge=(from:string,relationship:string,to:string)=>{const edge_id=from+'-'+relationship+'-'+to;if(!edges.includes(edge_id))edges.push(edge_id);write('specs/alpha/edges/'+edge_id+'.json',{schema_version:'domainspec.edge/v1',feature_id:'alpha',edge_id,relationship,source_node_id:from,target_node_id:to,scope:'feature'});};
 node('valid','Rule',{predicate:'structured:domainspec.typed-rule/v2',typed_contract:{schema_version:'domainspec.typed-rule/v2',ontology_rule:'TEST-VALID',parameters:[{name:'value',type:scalar()}],expression:{op:'eq',left:{op:'path',root:'value',properties:[]},right:{op:'path',root:'value',properties:[]}}}});
 const properties=[property('id',scalar(),true),property('amount',scalar('UInt64')),property('label',scalar()),property('active',scalar('Bool')),property('note',wrap('optional',scalar()))];
 node('row','Entity',{fields:properties.map(p=>p.name),typed_contract:{schema_version:'domainspec.typed-record/v1',ontology_node:'TEST-ROW',properties}});
 const query=(id:string,c:any)=>{if(minimal&&id!=='all')return;contracts[id]=c;node(id,'Query',{reads:['alpha:row'],typed_contract:c});edge(id,'reads','row');};
 const c={schema_version:'domainspec.typed-query/v1',ontology_query:'TEST-QUERY',source:'alpha:row',inputs:[],filter:null,projection:properties.map(p=>p.name),order_by:null,limit:null};
 query('all',{...c,inputs:[{name:'unused',type:scalar()}]});
 query('ordered',{...c,inputs:[{name:'min',type:scalar('UInt64')},{name:'unused',type:scalar()}],filter:cmp('gte',field('amount'),param('min')),order_by:{field:'amount',direction:'asc'},limit:2});
 query('labels',{...c,filter:cmp('lt',field('label'),literal('String','\ue000')),order_by:{field:'label',direction:'desc'}});
 query('booleans',{...c,filter:cmp('gte',field('active'),literal('Bool',false)),order_by:{field:'active',direction:'asc'}});
 query('compound',{...c,inputs:[{name:'min',type:scalar('UInt64')}],filter:{op:'any',terms:[{op:'all',terms:[cmp('gt',field('amount'),literal('UInt64',5)),cmp('lte',field('amount'),param('min'))]},{op:'not',term:cmp('eq',field('active'),literal('Bool',true))}]},limit:1});
 query('always',{...c,filter:{op:'all',terms:[cmp('eq',literal('Bool',true),literal('Bool',true))]}});query('never',{...c,filter:{op:'any',terms:[cmp('eq',literal('Bool',true),literal('Bool',false))]}});query('partial',{...c,projection:['note','id'],limit:1});
 const save=()=>{write('project.json',{schema_version:'domainspec.project/v1',project_id:'query-controls',features:['alpha'],cross_feature_edges:[]});write('specs/alpha/feature.json',{schema_version:'domainspec.feature/v1',feature_id:'alpha',nodes,edges});};save();
 const selection={...publicSelection(moduleRoot),factories:[{selector:'alpha:row',base_validators:[{rule:'alpha:valid',arguments:[{parameter:'value',field:'id'}]}],extensions:[]}],operations:[]};
 const graph=loadCompiledProjectGraph(source),plan=planCompiledReconciledProject(graph,selection);
 return {temp,source,selection,graph,plan,node,edge,query,save,write,contracts,properties};
}
test('optional Query controls retain absence, projection, cardinality failure and v2 descriptor identity',t=>{
 const f=fixture(t,'domain',true);
 f.query('all',{...f.contracts.all,schema_version:'domainspec.typed-query/v2',result_cardinality:'optional'});f.save();
 const graph=loadCompiledProjectGraph(f.source),plan=planCompiledReconciledProject(graph,f.selection),controls=createReconciledSemanticControls(graph,plan);
 const row:any=controls.rows.find(r=>r.selector==='alpha:all');assert.equal(row.state,'ready');assert.equal(row.result_cardinality,'optional');
 const descriptor=JSON.parse(row.cases.find((c:any)=>c.mode==='query-descriptor').expected.value);
 assert.equal(descriptor.protocol_id,'typescript.bound-query/v2-candidate');assert.equal(descriptor.result_cardinality,'optional');
 assert.deepEqual(descriptor.failures,['QUERY_INPUT','QUERY_CARDINALITY']);
 assert.ok(row.cases.some((c:any)=>c.expected.kind==='value'&&c.expected.value==='null'));
 assert.ok(row.cases.some((c:any)=>c.mode==='query'&&c.expected.kind==='value'&&c.expected.value!=='null'));
 assert.ok(row.cases.some((c:any)=>c.expected.kind==='error'&&c.expected.message==='QUERY_CARDINALITY'));
 assert.ok(row.cases.some((c:any)=>c.expected.kind==='error'&&c.expected.message==='QUERY_INPUT'));
});

test('native optional Query verification rejects cardinality, shape and validation-order mutants',t=>{
 const f=fixture(t,'domain',true),n=nativeContext(f);
 const reports=n.run(`import fs from 'node:fs';import path from 'node:path';import cp from 'node:child_process';import {syncBuiltinESMExports} from 'node:module';
 import {loadCompiledProjectGraph,planCompiledReconciledProject,executeReconciledVerification} from './dist/index.js';
 const source=${JSON.stringify(f.source)},selection=${JSON.stringify(f.selection)},tools=${JSON.stringify(n.options)},reports=[],original=cp.spawnSync;
 const file=path.join(source,'specs/alpha/nodes/all.json'),node=JSON.parse(fs.readFileSync(file,'utf8'));
 node.body.typed_contract.filter={op:'eq',left:{kind:'field',name:'active'},right:{kind:'literal',type:'Bool',value:true}};
 for(const mode of ['optional','first-match','list-wrapper','empty-list','undefined','wrong-error','mutable','validation-order','v2-list']){
  node.body.typed_contract.schema_version='domainspec.typed-query/v2';node.body.typed_contract.result_cardinality=mode==='v2-list'?'list':'optional';fs.writeFileSync(file,JSON.stringify(node));
  let mutated=false;
  cp.spawnSync=(command,args,settings)=>{
   if(command===tools.lean_executable&&!['optional','v2-list'].includes(mode))return {status:1,stdout:'',stderr:'isolated Query semantic-control mutation check'};
   const result=original(command,args,settings),config=args[args.indexOf('--project')+1];
   if(result.status===0&&args.includes('--project')&&String(config).endsWith('/semantic/compiler.json')&&!['optional','v2-list'].includes(mode)){
    const provider=path.join(path.dirname(config),'modules/domain/features/alpha/src/application/queries/all.provider.js');
    const before=fs.readFileSync(provider,'utf8'),start=before.indexOf('export const query ='),prefix=before.slice(0,start);let body=before.slice(start);
    if(mode==='first-match')body=body.replace('selected.length > 1','false');
    if(mode==='list-wrapper')body=body.replace(/return Object.freeze\\((\\{[^;]+\\})\\);/,'return Object.freeze([Object.freeze($1)]);');
    if(mode==='empty-list')body=body.replace('return null;','return Object.freeze([]);');
    if(mode==='undefined')body=body.replace('return null;','return undefined;');
    if(mode==='wrong-error')body=body.replace("'QUERY_CARDINALITY'","'QUERY_INPUT'");
    if(mode==='mutable')body=body.replace('return Object.freeze({','return ({');
    if(mode==='validation-order')body=body.replace('const d =',"if(Array.isArray(rows)&&rows.length>1)throw new TypeError('QUERY_CARDINALITY'); const d =");
    const after=prefix+body;if(after===before)throw Error('MUTANT_NOT_APPLIED:'+mode);fs.writeFileSync(provider,after);mutated=true;
   }return result;
  };syncBuiltinESMExports();
  try{const graph=loadCompiledProjectGraph(source),plan=planCompiledReconciledProject(graph,selection),report=executeReconciledVerification(graph,plan,tools);
   reports.push({mode,mutated,result:report.result,checks:report.checks.filter(c=>c.result!=='pass'),semantic:report.checks.find(c=>c.id==='selected-generator-semantic-controls'),cleanup:report.checks.find(c=>c.id==='verification-workspace-cleanup')});
  }finally{cp.spawnSync=original;syncBuiltinESMExports();}
 }console.log(JSON.stringify(reports));`);
 assert.equal(reports.length,9);
 for(const row of reports){
  assert.equal(row.cleanup.result,'pass',JSON.stringify(row));
  if(['optional','v2-list'].includes(row.mode)){
   assert.equal(row.semantic.result,'pass',JSON.stringify(row));
   // This isolated fixture supplies neither an output target nor cross-family
   // evidence. Require the exact residual checks; never call the full report pass.
   assert.equal(row.result,'incomplete',JSON.stringify(row));
   assert.deepEqual(row.checks.map((c:any)=>[c.id,c.result]).sort(),[
    ['cross-generator-behavior','not_evaluable'],['exact-output-currentness','not_evaluable'],['safe-output-separate-from-planning','not_evaluable'],
   ]);
  }
  else{assert.equal(row.mutated,true,row.mode);assert.equal(row.semantic.result,'fail',JSON.stringify(row));}
 }
});

test('Query source controls retain explicit full-row semantics, finite occurrences and exact relocated bindings',t=>{
 const f=fixture(t),controls=createReconciledSemanticControls(f.graph,f.plan),rows=controls.rows.filter(r=>r.kind==='Query') as any[];
 assert.equal(rows.length,8);for(const r of rows){assert.equal(r.state,'ready',r.selector+':'+r.reason);assert.equal(r.cases[0].mode,'query-descriptor');assert.ok(r.module_paths.every((p:string)=>p.includes('/queries/')));assert.ok(r.cases.some((c:any)=>c.expected.kind==='error'));}
 assert.equal(controls.not_evaluable_count,0);
 const other=fixture(t,'other/root'),moved=createReconciledSemanticControls(other.graph,other.plan);
 for(const r of rows)assert.deepEqual(r.cases.filter((c:any)=>c.mode==='query'),(moved.rows.find(m=>m.selector===r.selector) as any).cases.filter((c:any)=>c.mode==='query'));
 for(const filter of [{op:'all',terms:[]},{op:'any',terms:[]}]){f.query('all',{...f.contracts.all,filter});f.save();assert.throws(()=>loadCompiledProjectGraph(f.source),/logical predicate requires terms/);}
});
test('native Query verification observes all selected source nodes and independent source/native audit custody',t=>{
 const f=fixture(t),n=nativeContext(f),report=n.run(`import {loadCompiledProjectGraph,planCompiledReconciledProject,executeReconciledVerification} from './dist/index.js';
 const graph=loadCompiledProjectGraph(${JSON.stringify(f.source)}),plan=planCompiledReconciledProject(graph,${JSON.stringify(f.selection)});console.log(JSON.stringify(executeReconciledVerification(graph,plan,${JSON.stringify(n.options)})));`);
 const check=(id:string)=>report.checks.find((c:any)=>c.id===id),semantic=check('selected-generator-semantic-controls');
 assert.equal(semantic.result,'pass',JSON.stringify(semantic));assert.equal(semantic.evidence.tested.filter((r:any)=>r.kind==='Query').length,8);assert.equal(semantic.evidence.remaining.length,0);
 for(const phase of ['source','native']){assert.equal(check('query-'+phase+'-effect-audit').result,'pass',JSON.stringify(check('query-'+phase+'-effect-audit')));assert.equal(check('query-'+phase+'-effect-audit').evidence.selectors.length,8);}
 assert.equal(check('query-effect-audit-currentness').result,'pass');assert.equal(check('verification-workspace-cleanup').result,'pass');
});
test('compiling Query semantic and binding mutations, hidden effects and late drift cannot pass',t=>{
 const f=fixture(t),n=nativeContext(f),reports=n.run(`import fs from 'node:fs';import path from 'node:path';import {createHash} from 'node:crypto';import cp from 'node:child_process';import {syncBuiltinESMExports} from 'node:module';
 import {loadCompiledProjectGraph,planCompiledReconciledProject,executeReconciledVerification} from './dist/index.js';
 const source=${JSON.stringify(f.source)},selection=${JSON.stringify(f.selection)},tools=${JSON.stringify(n.options)},original=cp.spawnSync,reports=[];
 for(const mode of ["filter","drop-filter","order","ties","limit","early-limit","occurrences","field-substitution","field-order","omit","extra","root-freeze","primitive","unused-input","unchecked-rows","empty-validation","input-write","alias","binding-source","binding-target","binding-effect","binding-filter","binding-freeze","binding-getter","binding-cycle","static-import","caught-import","global","prototype","object-write","bracket-write","source-global","late"]){
  let nativeCalls=0;
  cp.spawnSync=(command,args,settings)=>{
   if(command===tools.lean_executable)return {status:1,stdout:'',stderr:'injected Lean failure for Query semantic isolation'};
   if(args.includes('--permission'))nativeCalls++;
   const config=args[args.indexOf('--project')+1];
   if(mode==='source-global'&&args.includes('--project')&&String(config).endsWith('/native/tsconfig.json'))fs.appendFileSync(path.join(path.dirname(config),'domain/features/alpha/src/application/queries/ordered.provider.ts'),'\\nvoid Date.now();\\n');
   const result=original(command,args,settings);
   if(result.status===0&&args.includes('--project')&&String(config).endsWith('/semantic/compiler.json')&&!['source-global','late'].includes(mode)){
    const folder=path.join(path.dirname(config),'modules/domain/features/alpha/src/application/queries'),id='ordered';
    const file=path.join(folder,id+(mode.startsWith('binding-')?'':'.provider')+'.js'),old=fs.readFileSync(file,'utf8'),start=old.indexOf('export const query ='),prefix=old.slice(0,start),body=old.slice(start);let changed=old;
    const edit=(a,b)=>{changed=prefix+body.replace(a,b);};
    if(mode==='filter')edit('row["amount"] >= p0','row["amount"] <= p0');
    if(mode==='drop-filter')edit('row["amount"] >= p0','true');
    if(mode==='order')edit(' ? -1 : ',' ? 1 : ');
    if(mode==='ties')edit(' : 0);',' : -1);');
    if(mode==='limit')edit('selected.slice(0, 2)','selected.slice(0, 1)');
    if(mode==='early-limit')edit('.normalize(rows)','.normalize(rows).slice(0, 2)');
    if(mode==='occurrences')edit('selected.slice(0, 2)','selected.slice(0, 2).filter((r,i,a)=>a.findIndex(x=>x.id===r.id)===i)');
    if(mode==='field-substitution')edit('["label"]: row["label"]','["label"]: row["id"]');
    if(mode==='field-order')edit('["id"]: row["id"], ["amount"]: row["amount"]','["amount"]: row["amount"], ["id"]: row["id"]');
    if(mode==='omit')edit(', ["label"]: row["label"]','');
    if(mode==='extra')edit('["label"]: row["label"]','["label"]: row["label"], extra: true');
    if(mode==='root-freeze')edit('return Object.freeze(selected.map','return Object(selected.map');
    if(mode==='primitive')edit('["amount"]: row["amount"]','["amount"]: Number(row["amount"])');
    if(mode==='unused-input')edit(/const p1 = [^;]+;/,'const p1 = d["unused"].value;');
    if(mode==='unchecked-rows')edit(/const snapshots = [^;]+;/,'const snapshots = rows;');
    if(mode==='empty-validation')edit('    const d =','    if(rows.length===0)return Object.freeze([]);\\n    const d =');
    if(mode==='input-write')edit('    const d =','    if(rows.length)rows[0].id="changed";\\n    const d =');
    if(mode==='alias')edit(/return Object.freeze\\(selected.map[\\s\\S]+?;\\n/,'return Object.freeze(rows);\\n');
    if(['binding-source','binding-target','binding-effect','binding-filter'].includes(mode)){
     const cases=JSON.parse(fs.readFileSync(path.join(path.dirname(config),'cases.json'),'utf8')),d=JSON.parse(cases.rows.find(r=>r.selector==='alpha:'+id).cases.find(c=>c.mode==='query-descriptor').expected.value);
     if(mode==='binding-source')d.contract_sha256='0'.repeat(64);if(mode==='binding-target')d.read_targets[0].selector='alpha:other';if(mode==='binding-effect')d.effect_contract='execute';if(mode==='binding-filter')d.filter=null;
     delete d.descriptor_sha256;const canonical=v=>JSON.stringify(v,(_,x)=>x&&typeof x==='object'&&!Array.isArray(x)?Object.fromEntries(Object.entries(x).sort(([a],[b])=>a<b?-1:a>b?1:0)):x);d.descriptor_sha256=createHash('sha256').update(canonical(d)).digest('hex');
     changed='import {query} from "./'+id+'.provider.js";const freeze=v=>{if(v&&typeof v==="object"){Object.values(v).forEach(freeze);Object.freeze(v);}return v;};export const query'+id[0].toUpperCase()+id.slice(1)+'=Object.freeze(Object.assign(query,{descriptor:freeze('+JSON.stringify(d)+')}));';
    }
    if(mode==='binding-freeze')changed=old.replace('Object.freeze(Object.assign(query,','Object(Object.assign(query,');
    if(mode==='binding-getter')changed='import {query} from "./ordered.provider.js";export const queryOrdered=Object.freeze(Object.defineProperty(query,"descriptor",{enumerable:true,get(){throw new Error("GETTER_EXECUTED");}}));';
    if(mode==='binding-cycle')changed='import {query} from "./ordered.provider.js";const d={};d.self=d;Object.freeze(d);export const queryOrdered=Object.freeze(Object.assign(query,{descriptor:d}));';
    if(mode==='static-import')changed=old+'\\nimport "./all.js";\\n';
    if(mode==='caught-import')changed=old+'\\nimport("./all.js").catch(()=>{});\\n';
    if(mode==='global')changed=old+'\\nglobalThis.queryLeak=1;\\n';
    if(mode==='prototype')changed=old+'\\nObject.freeze(Object.prototype);\\n';
    if(mode==='object-write')changed=old+'\\nObject.defineProperty(Object.prototype,"queryLeak",{value:1});\\n';
    if(mode==='bracket-write')changed=old+'\\nObject["defineProperty"](Object["prototype"],"queryLeak",{value:1});\\n';
    if(changed===old)throw Error('Query mutant not installed:'+mode+':'+old.slice(-2000));fs.writeFileSync(file,changed);
    const syntax=original(process.execPath,['--check',file],{encoding:'utf8',timeout:60000});if(syntax.status!==0)throw Error('Query mutant syntax:'+mode+':'+syntax.stderr);
   }
   if(mode==='late'&&args.includes('--permission')&&result.status===0)fs.appendFileSync(path.join(settings.cwd,'modules/domain/features/alpha/src/application/queries/ordered.provider.js'),' ');
   return result;
  };syncBuiltinESMExports();
  try{const graph=loadCompiledProjectGraph(source),plan=planCompiledReconciledProject(graph,selection);reports.push({mode,report:executeReconciledVerification(graph,plan,tools),nativeCalls});}finally{cp.spawnSync=original;syncBuiltinESMExports();}
 }
 console.log(JSON.stringify(reports));`);
 for(const {mode,report,nativeCalls}of reports){
  const check=(id:string)=>report.checks.find((c:any)=>c.id===id),semantic=check('selected-generator-semantic-controls');
  if(mode==='source-global'){assert.equal(check('query-source-effect-audit').result,'fail',mode);assert.equal(nativeCalls,0);}
  else if(mode==='late'){assert.equal(check('semantic-workspace-currentness').result,'fail');assert.equal(semantic.result,'not_evaluable');assert.equal(check('query-native-effect-audit').result,'not_evaluable');}
  else if(['binding-getter','caught-import','global','prototype','object-write','bracket-write'].includes(mode)){assert.equal(check('query-native-effect-audit').result,'fail',mode);assert.equal(nativeCalls,0);}
  else{assert.equal(semantic.result,'fail',mode+':'+semantic.reason);assert.ok(nativeCalls>0,mode);assert.match(semantic.reason,mode==='static-import'?/QUERY_NATIVE_IMPORT_BOUNDARY/:/observation mismatch/,mode);}
  assert.equal(check('verification-workspace-cleanup').result,'pass',mode);
 }
});
test('Query audit evidence substitution and artifact drift cannot authorize semantic execution',t=>{
 const f=fixture(t),n=nativeContext(f),reports=n.run(`import fs from 'node:fs';import cp from 'node:child_process';import {syncBuiltinESMExports} from 'node:module';
 import {loadCompiledProjectGraph,planCompiledReconciledProject,executeReconciledVerification} from './dist/index.js';
 const source=${JSON.stringify(f.source)},selection=${JSON.stringify(f.selection)},tools=${JSON.stringify(n.options)},original=cp.spawnSync,reports=[];
 for(const mode of ['source-omit','native-phase','native-hash','source-script','native-script','late']){
  let calls=0,script='';
  cp.spawnSync=(command,args,settings)=>{
   if(command===tools.lean_executable)return {status:1,stdout:'',stderr:'isolated audit custody'};
   if(args.includes('--permission'))calls++;
   const result=original(command,args,settings),file=args.find(a=>String(a).endsWith('/query-effects.mjs'));
   if(file&&result.status===0){
    script=file;const o=JSON.parse(result.stdout);
    if(mode==='source-omit'&&o.phase==='source'){o.modules.pop();result.stdout=JSON.stringify(o);}
    if(mode==='native-phase'&&o.phase==='native'){o.phase='source';result.stdout=JSON.stringify(o);}
    if(mode==='native-hash'&&o.phase==='native'){o.modules[0].source_sha256='0'.repeat(64);result.stdout=JSON.stringify(o);}
    if(mode===o.phase+'-script')fs.appendFileSync(file,'\\n// changed\\n');
   }
   if(mode==='late'&&args.includes('--permission')&&result.status===0)fs.appendFileSync(script,'\\n// late drift\\n');
   return result;
  };syncBuiltinESMExports();
  try{const graph=loadCompiledProjectGraph(source),plan=planCompiledReconciledProject(graph,selection);reports.push({mode,callsBefore:calls,report:executeReconciledVerification(graph,plan,tools),callsAfter:()=>calls});reports.at(-1).callsAfter=calls;}finally{cp.spawnSync=original;syncBuiltinESMExports();}
 }console.log(JSON.stringify(reports));`);
 for(const {mode,report,callsAfter}of reports){
  const check=(id:string)=>report.checks.find((c:any)=>c.id===id);
  if(mode==='late'){assert.ok(callsAfter>0);assert.equal(check('query-effect-audit-currentness').result,'fail');for(const id of ['query-source-effect-audit','query-native-effect-audit','selected-generator-semantic-controls'])assert.equal(check(id).result,'not_evaluable',id);}
  else{assert.equal(callsAfter,0,mode);assert.equal(check(mode.startsWith('source')?'query-source-effect-audit':'query-native-effect-audit').result,'fail',mode);}
  assert.equal(check('verification-workspace-cleanup').result,'pass');
 }
});
test('Query capacity preserves the entire source node and still audits its source effects',t=>{
 const f=fixture(t),c={...f.contracts.all,ontology_query:'TEST-CAPACITY',limit:4096};f.query('capacity',c);f.save();
 const n=nativeContext(f),reports=n.run(`import fs from 'node:fs';import path from 'node:path';import cp from 'node:child_process';import {syncBuiltinESMExports} from 'node:module';
 import {loadCompiledProjectGraph,planCompiledReconciledProject,executeReconciledVerification} from './dist/index.js';
 const source=${JSON.stringify(f.source)},selection=${JSON.stringify(f.selection)},tools=${JSON.stringify(n.options)},original=cp.spawnSync,reports=[];
 for(const mode of ['clean','forbidden','literal']){
  let calls=0;cp.spawnSync=(command,args,settings)=>{
   if(command===tools.lean_executable)return {status:1,stdout:'',stderr:'isolated capacity'};
   if(args.includes('--permission'))calls++;const config=args[args.indexOf('--project')+1];
   if(mode==='forbidden'&&args.includes('--project')&&String(config).endsWith('/native/tsconfig.json'))fs.appendFileSync(path.join(path.dirname(config),'domain/features/alpha/src/application/queries/capacity.provider.ts'),'\\nvoid Date.now();\\n');
   const result=original(command,args,settings);
   if(mode==='literal'&&result.status===0&&args.includes('--project')&&String(config).endsWith('/semantic/compiler.json'))fs.appendFileSync(path.join(path.dirname(config),'modules/domain/features/alpha/src/application/queries/all.provider.js'),'\\n// Date globalThis Promise\\nvoid "Object.defineProperty";\\n');
   return result;
  };syncBuiltinESMExports();
  try{const graph=loadCompiledProjectGraph(source),plan=planCompiledReconciledProject(graph,selection),report=executeReconciledVerification(graph,plan,tools);reports.push({mode,report,calls});}finally{cp.spawnSync=original;syncBuiltinESMExports();}
 }console.log(JSON.stringify(reports));`);
 for(const {mode,report,calls}of reports){
  const check=(id:string)=>report.checks.find((c:any)=>c.id===id),row=report.semantic_coverage.rows.find((r:any)=>r.selector==='alpha:capacity');
  assert.equal(row.adapter_status,'not_evaluable');assert.equal(Object.hasOwn(row,'case_count'),false);
  if(mode==='forbidden'){assert.equal(check('query-source-effect-audit').result,'fail');assert.equal(calls,0);}
  else{assert.equal(check('query-source-effect-audit').result,'pass');assert.ok(check('query-source-effect-audit').evidence.selectors.includes('alpha:capacity'));assert.ok(!check('query-native-effect-audit').evidence.selectors.includes('alpha:capacity'));assert.ok(calls>0);}
 }
});
test('native Query projections and equality preserve every structured shape without factory witnesses',t=>{
 const f=fixture(t,'domain',true);
 f.node('invalid-value','Rule',{predicate:'structured:domainspec.typed-rule/v2',typed_contract:{schema_version:'domainspec.typed-rule/v2',ontology_rule:'TEST-INVALID-VALUE',parameters:[{name:'value',type:scalar()}],expression:{op:'eq',left:{op:'literal',type:'Bool',value:false},right:{op:'literal',type:'Bool',value:true}}}});
 f.node('component','Value Object',{fields:['code','enabled'],invariant_refs:['alpha:invalid-value'],typed_contract:{schema_version:'domainspec.typed-record/v1',ontology_node:'TEST-COMPONENT',properties:[property('code',scalar()),property('enabled',scalar('Bool'))].map(p=>({...p,ontology_property:'TEST-COMPONENT#'+p.name}))}});
 f.node('child','Entity',{fields:['id','label'],typed_contract:{schema_version:'domainspec.typed-record/v1',ontology_node:'TEST-CHILD',properties:[property('id',scalar(),true),property('label',scalar())].map(p=>({...p,ontology_property:'TEST-CHILD#'+p.name}))}});
 f.node('status','Enum',{values:['None','Some'],typed_contract:{schema_version:'domainspec.typed-sum/v1',ontology_node:'TEST-STATUS',variants:[{name:'None',ontology_variant:'TEST-STATUS#None',payload:null},{name:'Some',ontology_variant:'TEST-STATUS#Some',payload:scalar('Bool')}]}});f.save();
 f.selection.factories.push({selector:'alpha:component',base_validators:[{rule:'alpha:invalid-value',arguments:[{parameter:'value',field:'code'}]}],extensions:[]},{selector:'alpha:child',base_validators:[{rule:'alpha:valid',arguments:[{parameter:'value',field:'id'}]}],extensions:[]});
 const variants=[scalar(),scalar('UInt64'),scalar('Bool'),wrap('optional',scalar('UInt64')),wrap('list',scalar('UInt64')),wrap('set',scalar('UInt64')),{kind:'sum',variants:[{name:'None',ontology_variant:'TEST-CHOICE#None',payload:null},{name:'Amount',ontology_variant:'TEST-CHOICE#Amount',payload:scalar('UInt64')}]},named('child'),named('component'),named('status'),wrap('list',named('component')),wrap('set',named('component'))];
 const n=nativeContext(f),reports=n.run(`import fs from 'node:fs';import path from 'node:path';import cp from 'node:child_process';import {syncBuiltinESMExports} from 'node:module';import {isDeepStrictEqual} from 'node:util';
 import {loadCompiledProjectGraph,planCompiledReconciledProject,executeReconciledVerification} from './dist/index.js';
 const source=${JSON.stringify(f.source)},selection=${JSON.stringify(f.selection)},tools=${JSON.stringify(n.options)},variants=${JSON.stringify(variants)},reports=[],original=cp.spawnSync;
 const file=id=>path.join(source,'specs/alpha/nodes/'+id+'.json'),row=JSON.parse(fs.readFileSync(file('row'),'utf8')),query=JSON.parse(fs.readFileSync(file('all'),'utf8'));
 for(const [index,type]of variants.entries()){
  const properties=[row.body.typed_contract.properties.find(p=>p.name==='id'),...['value','other'].map(name=>({name,type,identity:false,cardinality:type.kind==='optional'?'optional':type.kind==='list'?'many':type.kind==='set'?'many-unique':'one',meaning:name,ontology_property:'TEST-ROW#'+name}))];
  row.body.fields=properties.map(p=>p.name);row.body.typed_contract.properties=properties;query.body.typed_contract.inputs=[];query.body.typed_contract.projection=['id','value'];query.body.typed_contract.filter={op:'eq',left:{kind:'field',name:'value'},right:{kind:'field',name:'other'}};
  fs.writeFileSync(file('row'),JSON.stringify(row));fs.writeFileSync(file('all'),JSON.stringify(query));let mismatch=null;
  cp.spawnSync=(command,args,settings)=>{if(command===tools.lean_executable)return {status:1,stdout:'',stderr:'isolated structural Query controls'};const result=original(command,args,settings);
   if(args.includes('--permission')&&result.status===0){const planned=JSON.parse(fs.readFileSync(args.find(a=>String(a).endsWith('/cases.json')),'utf8')),observed=JSON.parse(result.stdout);
    for(const row of planned.rows){const o=observed.find(o=>o.selector===row.selector);for(const c of row.cases){const actual=o?.cases.find(x=>x.id===c.id);if(!isDeepStrictEqual(c.expected,actual?.outcome)){mismatch={selector:row.selector,id:c.id,expected:c.expected,actual};break;}}if(mismatch)break;}
   }return result;};syncBuiltinESMExports();
  try{const graph=loadCompiledProjectGraph(source),plan=planCompiledReconciledProject(graph,selection),report=executeReconciledVerification(graph,plan,tools);reports.push({index,semantic:report.checks.find(c=>c.id==='selected-generator-semantic-controls'),coverage:report.semantic_coverage.rows.find(r=>r.selector==='alpha:all'),mismatch});}finally{cp.spawnSync=original;syncBuiltinESMExports();}
 }console.log(JSON.stringify(reports));`);
 assert.equal(reports.length,variants.length);
 for(const r of reports){assert.equal(r.mismatch,null,JSON.stringify(r));assert.equal(r.coverage.adapter_status,'ready',JSON.stringify(r));assert.equal(r.semantic.executed,true,JSON.stringify(r));assert.ok(r.semantic.evidence.tested.some((x:any)=>x.selector==='alpha:all'),JSON.stringify(r));assert.ok(r.semantic.evidence.remaining.some((x:any)=>x.selector==='alpha:component'));}
});
test('native Queries run while every domain factory, Rule, Calculation and endpoint module is poisoned',t=>{
 const f=fixture(t);f.node('computed','Calculation',{inputs:['left','right'],typed_contract:{schema_version:'domainspec.typed-calculation/v2',ontology_calculation:'TEST-COMPUTED',inputs:['left','right'].map(name=>({name,type:scalar('UInt64')})),result:scalar('UInt64'),division_rounding:'reject',expression:{op:'add',left:{op:'input',name:'left'},right:{op:'input',name:'right'}}}});f.save();
 const n=nativeContext(f),result=n.run(`import assert from 'node:assert/strict';import fs from 'node:fs';import path from 'node:path';import {execFileSync,spawnSync} from 'node:child_process';
 import {loadCompiledProjectGraph,planCompiledReconciledProject} from './dist/index.js';
 const graph=loadCompiledProjectGraph(${JSON.stringify(f.source)}),plan=planCompiledReconciledProject(graph,${JSON.stringify(f.selection)}),tools=${JSON.stringify(n.options)},source=path.resolve('products'),output=path.resolve('compiled-products');fs.mkdirSync(source);fs.writeFileSync(path.join(source,'package.json'),'{"type":"module"}');
 for(const a of plan.resolved.artifacts){const file=path.join(source,a.relative_path);fs.mkdirSync(path.dirname(file),{recursive:true});fs.writeFileSync(file,a.content);}
 const config=path.join(source,'tsconfig.json');fs.writeFileSync(config,JSON.stringify({compilerOptions:{strict:true,skipLibCheck:true,target:'ES2022',module:'NodeNext',moduleResolution:'NodeNext',rootDir:source,outDir:output,types:['node'],typeRoots:[tools.node_type_root]},files:plan.resolved.modules.map(m=>path.join(source,m.relative_path))}));
 execFileSync(process.execPath,[path.join(tools.typescript_root,'bin/tsc'),'--project',config],{encoding:'utf8',timeout:60000});fs.writeFileSync(path.join(output,'package.json'),'{"type":"module"}');
 const poisoned=plan.resolved.modules.filter(m=>m.qualified_selectors.some(s=>!['Query'].includes(graph.nodes.find(n=>n.selector===s).kind)));
 for(const m of poisoned)fs.writeFileSync(path.join(output,m.relative_path.replace(/\\.ts$/,'.js')),'throw new Error("UNDECLARED_MODULE_LOADED");\\n');
 const module=id=>plan.resolved.modules.find(m=>m.qualified_selectors.includes('alpha:'+id)&&m.exports.some(e=>e.name==='query'+id[0].toUpperCase()+id.slice(1))),filename=id=>path.join(output,module(id).relative_path.replace(/\\.ts$/,'.js'));
 const client=path.resolve('query-client.mjs');
 const program=['import assert from "node:assert/strict";','import {queryAll} from '+JSON.stringify(filename('all'))+';','import {queryOrdered} from '+JSON.stringify(filename('ordered'))+';',
 'const row=(id,amount,label="x")=>({id,amount,label,active:true});const input=[row("same","18446744073709551615"),row("same","9007199254740993"),row("other","18446744073709551615")];',
 'const result=queryOrdered(input,{min:"9007199254740993",unused:"ok"});assert.deepEqual(result.map(r=>r.amount),[9007199254740993n,18446744073709551615n]);assert.deepEqual(result.map(r=>r.id),["same","same"]);assert.equal(result[0].note,null);',
 'const ties=[row("first","1"),row("second","1"),row("third","1")];assert.deepEqual(queryOrdered(ties,{min:0,unused:"ok"}).map(r=>r.id),["first","second"]);assert.deepEqual(queryAll(ties,{unused:"ok"}).map(r=>r.id),["first","second","third"]);',
 'assert.throws(()=>queryOrdered([...ties,{...row("bad","0"),active:1}],{min:0,unused:"ok"}),/QUERY_INPUT/);assert.throws(()=>queryOrdered([],{min:0}),/QUERY_INPUT/);',
 'assert.ok(Object.isFrozen(result)&&result.every(Object.isFrozen));assert.equal("extend" in result[0],false);input[1].id="changed";assert.equal(result[0].id,"same");console.log("query-isolation-pass");'].join(String.fromCharCode(10));fs.writeFileSync(client,program);
 const baseline=execFileSync(process.execPath,[client],{encoding:'utf8',timeout:60000}).trim();
 const provider=path.join(output,module('ordered').relative_path.replace(/\\.ts$/,'.provider.js')),dependency=path.join(output,poisoned.find(m=>m.qualified_selectors.includes('alpha:computed')).relative_path.replace(/\\.ts$/,'.js'));let specifier=path.relative(path.dirname(provider),dependency).split(path.sep).join('/');if(!specifier.startsWith('.'))specifier='./'+specifier;
 fs.appendFileSync(provider,'\\nimport '+JSON.stringify(specifier)+';\\n');const negative=spawnSync(process.execPath,[client],{encoding:'utf8',timeout:60000});assert.notEqual(negative.status,0);assert.match(negative.stderr,/UNDECLARED_MODULE_LOADED/);
 console.log(JSON.stringify({baseline,poisoned:poisoned.length,negative:true}));`);
 assert.equal(result.baseline,'query-isolation-pass');assert.ok(result.poisoned>0);assert.equal(result.negative,true);
});
function nativeContext(f:any){
 const cliRoot=path.join(project,'impl/cli'),src=path.join(cliRoot,'src'),dist=path.join(f.temp,'dist');
 const require=createRequire(import.meta.url),types=require.resolve('@types/node/package.json',{paths:process.execArgv.filter(a=>a.endsWith('loader.mjs')).map(p=>path.dirname(p))}),deps=path.dirname(path.dirname(path.dirname(types)));
 const undici = path.dirname(createRequire(fs.realpathSync(types)).resolve('undici-types/package.json'));
 const leanRoot=path.dirname(path.dirname(process.env.DOMAINSPEC_LEAN!));assert.ok(path.isAbsolute(leanRoot),'explicit installed Lean required');
 const image=nativeToolchainImage();
 assert.equal(image,NATIVE_TEST_IMAGE_ID);
 const docker=['run','--rm','--pull','never','--network','none','--read-only','--cap-drop','ALL','--security-opt','no-new-privileges','--user',process.getuid!()+':'+process.getgid!(),'--mount','type=bind,source='+cliRoot+',target='+cliRoot+',readonly','--mount','type=bind,source='+deps+',target='+deps+',readonly','--mount','type=bind,source='+undici+',target='+undici+',readonly','--mount','type=bind,source='+leanRoot+',target='+leanRoot+',readonly','--mount','type=bind,source='+f.temp+',target='+f.temp,'--workdir',f.temp,'--env','TMPDIR='+path.join(f.temp,'scratch'),image];
 fs.mkdirSync(path.join(f.temp,'scratch'));fs.writeFileSync(path.join(f.temp,'package.json'),JSON.stringify({type:'module'}));
 try{execFileSync('docker',[...docker,'tsc','--ignoreConfig','--strict','--skipLibCheck','--declaration','--types','node','--typeRoots',path.join(deps,'@types'),'--target','ES2022','--module','NodeNext','--rootDir',src,'--outDir',dist,path.join(src,'index.ts')],{encoding:'utf8'});}catch(e:any){throw Error(String(e.stdout)+String(e.stderr));}
 const options={typescript_root:'/opt/node-toolchain/node_modules/typescript',node_type_root:path.join(deps,'@types'),lean_executable:path.join(leanRoot,'bin','lean')};
 const run=(body:string)=>{const file=path.join(f.temp,'client.mjs');fs.writeFileSync(file,body);try{return JSON.parse(execFileSync('docker',[...docker,'node',file],{encoding:'utf8',timeout:180000,maxBuffer:32*1024*1024}));}catch(e:any){throw Error(String(e.stdout)+String(e.stderr));}};
 return {run,options};
}

import {nativeToolchainImage, NATIVE_TEST_IMAGE_ID} from '../helpers/native-toolchain-image.ts';
