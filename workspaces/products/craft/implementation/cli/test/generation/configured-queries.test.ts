import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {createRequire} from 'node:module';
import {execFileSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import test from 'node:test';
import {loadCompiledProjectGraph} from '../../src/input/project-model.ts';
import {createCompiledProjectCertificate} from '../../src/compilation/certificate.ts';
import {compileCompositionBoundary,COMPOSITION_BOUNDARY_VERSION,COMPOSITION_BOUNDARY_CONTRACT_SHA256} from '../../src/input/composition-boundary.ts';
import {compileSelectedProjectFields,EXACT_PROJECT_FIELD_SELECTION_VERSION,EXACT_FIELD_CONTRACT_SHA256} from '../../src/input/compiled-field-model.ts';
import {planConfiguredQueries,CONFIGURED_QUERY_VERSION,type ConfiguredQuerySelection} from '../../src/generation/configured-queries.ts';
import {renderStructuredRule} from '../../src/generation/configured-rule-values.ts';
import {createStructuredValueRenderer} from '../../src/generation/configured-value-types.ts';
import {EXACT_UINT64_PROFILE} from '../../src/generation/exact-uint64.ts';
import {planCompiledProjectBuild} from '../../src/generation/project-build.ts';
import {sha256,canonicalJson} from '../../src/input/source-manifest.ts';

const project=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../../../..'),pkg=path.join(project,'development/reconciliation-v1/profile-compiler-reconciliation');
const bytes=(p:string)=>fs.readFileSync(p,'utf8'),read=(p:string)=>JSON.parse(bytes(p));
const sources={configuration:bytes(path.join(pkg,'configuration.json')),base:bytes(path.join(project,'development/implementation-conformance/ontology-experiment/profiles/base-domain.profile.json')),
  typescript:bytes(path.join(project,'development/implementation-conformance/ontology-experiment/profiles/typescript-strict.profile.json')),query_contract:bytes(path.join(pkg,'query-generation-contract.json'))};
const boundaryContract=bytes(path.join(project,'development/reconciliation-v1/contracts/composition-boundary.json')),fieldContract=bytes(path.join(project,'development/reconciliation-v1/contracts/exact-field-and-reference-model.json'));
const scalar=(name='String')=>({kind:'scalar',name}),named=(id:string)=>({kind:'named',selector:'alpha:'+id}),wrap=(kind:string,element:any)=>({kind,element});
const property=(owner:string,name:string,type:any,identity=false)=>({name,type,identity,cardinality:type.kind==='optional'?'optional':type.kind==='list'?'many':type.kind==='set'?'many-unique':'one',meaning:name,ontology_property:'FIXTURE-'+owner+'#'+name});
const field=(name:string)=>({kind:'field',name}),param=(name:string)=>({kind:'parameter',name}),cmp=(op:string,left:any,right:any)=>({op,left,right});
const params={min:0,enabled:true,label:'unused'};
const allProjection=['id','label','amount','active','money','items','labels','customer','state','choice','note'];
const specs:any={
  all:{filter:null,order_by:null,limit:null,projection:allProjection,filter_expression:'true'},
  amount:{filter:{op:'all',terms:[cmp('gte',field('amount'),param('min')),cmp('eq',field('active'),param('enabled'))]},order_by:{field:'amount',direction:'asc'},limit:2,projection:allProjection,filter_expression:'((row["amount"] >= p0) && (ruleBool.key(row["active"]) === ruleBool.key(p1)))'},
  label:{filter:cmp('eq',field('label'),param('label')),order_by:{field:'label',direction:'desc'},limit:null,projection:['id','label'],filter_expression:'(ruleString.key(row["label"]) === ruleString.key(p2))'},
  sorted:{filter:null,order_by:{field:'label',direction:'asc'},limit:null,projection:['id','label'],filter_expression:'true'},
  enabled:{filter:cmp('gte',field('active'),param('enabled')),order_by:{field:'active',direction:'desc'},limit:null,projection:['id','active'],filter_expression:'(Number(row["active"]) >= Number(p1))'},
  predicate:{filter:{op:'any',terms:[{op:'all',terms:[cmp('lt',field('amount'),{kind:'literal',type:'UInt64',value:10}),cmp('gt',field('amount'),{kind:'literal',type:'UInt64',value:5}),cmp('lte',field('amount'),param('min'))]},{op:'not',term:cmp('eq',field('active'),{kind:'literal',type:'Bool',value:true})}]},order_by:null,limit:null,projection:['id'],filter_expression:'(((row["amount"] < 10n) && (row["amount"] > 5n) && (row["amount"] <= p0)) || !((ruleBool.key(row["active"]) === ruleBool.key(true))))'},
  identity:{filter:cmp('eq',field('customer'),field('other_customer')),order_by:null,limit:null,projection:['id']},
  value:{filter:cmp('eq',field('money'),field('other_money')),order_by:null,limit:null,projection:['id']},
  optional:{filter:cmp('eq',field('note'),field('other_note')),order_by:null,limit:null,projection:['id','note']},
  list:{filter:cmp('eq',field('items'),field('other_items')),order_by:null,limit:null,projection:['id','items']},
};
function fixture(t:any){
  const temp=fs.mkdtempSync(path.join(os.tmpdir(),'ds-queries-'));t.after(()=>fs.rmSync(temp,{recursive:true,force:true}));
  const source=path.join(temp,'source');fs.cpSync(path.join(project,'impl/cli/fixtures/input-roots/canonical-project'),source,{recursive:true});
  const write=(p:string,v:any)=>{const f=path.join(source,p);fs.mkdirSync(path.dirname(f),{recursive:true});fs.writeFileSync(f,JSON.stringify(v,null,2)+'\n');};
  const feature=read(path.join(source,'specs/alpha/feature.json'));
  const node=(id:string,kind:string,body:any)=>{feature.nodes.push(id);write('specs/alpha/nodes/'+id+'.json',{schema_version:'domainspec.node/v1',feature_id:'alpha',node_id:id,kind,body:{description:id,...body}});};
  const record=(id:string,kind:string,fields:any[])=>node(id,kind,{fields:fields.map(f=>f.name),...(kind==='Value Object'?{invariant_refs:['alpha:valid-read-value']}:{}),typed_contract:{schema_version:'domainspec.typed-record/v1',ontology_node:'FIXTURE-'+id.toUpperCase(),properties:fields}});
  node('valid-read-value','Rule',{predicate:'structured:domainspec.typed-rule/v1',typed_contract:{schema_version:'domainspec.typed-rule/v1',ontology_rule:'FIXTURE-VALID-READ-VALUE',parameters:[{name:'value',type:scalar('UInt64')}],expression:{op:'eq',left:{op:'literal',type:'Bool',value:false},right:{op:'literal',type:'Bool',value:true}}}});
  record('money','Value Object',[property('MONEY','amount',scalar('UInt64')),property('MONEY','currency',scalar())]);
  record('query-customer','Entity',[property('QUERY-CUSTOMER','id',scalar(),true),property('QUERY-CUSTOMER','label',scalar())]);
  node('status','Enum',{values:['Pending','Ready'],typed_contract:{schema_version:'domainspec.typed-sum/v1',ontology_node:'FIXTURE-STATUS',variants:[{name:'Pending',ontology_variant:'FIXTURE-STATUS#Pending',payload:null},{name:'Ready',ontology_variant:'FIXTURE-STATUS#Ready',payload:null}]}});
  const sum={kind:'sum',variants:[{name:'None',ontology_variant:'FIXTURE-CHOICE#None',payload:null},{name:'Amount',ontology_variant:'FIXTURE-CHOICE#Amount',payload:scalar('UInt64')},{name:'Money',ontology_variant:'FIXTURE-CHOICE#Money',payload:named('money')}]};
  record('order','Entity',[property('ORDER','id',scalar(),true),property('ORDER','label',scalar()),property('ORDER','amount',scalar('UInt64')),property('ORDER','active',scalar('Bool')),
    ...['money','other_money'].map(n=>property('ORDER',n,named('money'))),...['customer','other_customer'].map(n=>property('ORDER',n,named('query-customer'))),
    ...['items','other_items'].map(n=>property('ORDER',n,wrap('list',named('money')))),property('ORDER','labels',wrap('set',scalar())),property('ORDER','state',named('status')),property('ORDER','choice',sum),
    ...['note','other_note'].map(n=>property('ORDER',n,wrap('optional',scalar())))]);
  const contracts:any={};
  for(const [id,s] of Object.entries(specs) as [string,any][]){
    const node_id='read-'+id,edge_id=node_id+'-reads-order';feature.edges.push(edge_id);
    const c={schema_version:'domainspec.typed-query/v1',ontology_query:'FIXTURE-READ-'+id.toUpperCase(),source:'alpha:order',inputs:[{name:'min',type:scalar('UInt64')},{name:'enabled',type:scalar('Bool')},{name:'label',type:scalar()}],filter:s.filter,projection:s.projection,order_by:s.order_by,limit:s.limit};contracts['alpha:'+node_id]=c;
    node(node_id,'Query',{reads:['alpha:order'],typed_contract:c});
    write('specs/alpha/edges/'+edge_id+'.json',{schema_version:'domainspec.edge/v1',feature_id:'alpha',edge_id,relationship:'reads',source_node_id:node_id,target_node_id:'order',scope:'feature'});
  }
  write('specs/alpha/feature.json',feature);
  const graph=loadCompiledProjectGraph(source),graph_sha256=createCompiledProjectCertificate(graph).graph_sha256;
  const boundary=compileCompositionBoundary(graph,{schema_version:COMPOSITION_BOUNDARY_VERSION,contract_sha256:COMPOSITION_BOUNDARY_CONTRACT_SHA256,graph_sha256},boundaryContract);
  const fields=compileSelectedProjectFields(graph,{schema_version:EXACT_PROJECT_FIELD_SELECTION_VERSION,contract_sha256:EXACT_FIELD_CONTRACT_SHA256,graph_sha256,roots:['alpha:order'],bindings:[]},fieldContract);
  const selection:ConfiguredQuerySelection={schema_version:CONFIGURED_QUERY_VERSION,language:'typescript',value_profile:EXACT_UINT64_PROFILE,boundary_sha256:boundary.boundary_sha256,field_compilation_sha256:fields.compilation_sha256,module_root:'commerce',roots:Object.keys(contracts)};
  return {temp,source,write,graph,boundary,fields,selection,contracts,plan:()=>planConfiguredQueries(boundary,fields,selection,sources)};
}
const money=(amount:any=4)=>({amount,currency:'GBP'});
const row=(id='order-a',amount:any=10,label='a'):any=>({id,amount,label,active:true,money:money(),other_money:money(),customer:{id:'customer',label:'a'},other_customer:{id:'customer',label:'b'},items:[money(1),money(1)],other_items:[money(1),money(1)],labels:['z','a'],state:{variant:'Ready'},choice:{variant:'Money',payload:money('18446744073709551615')}});
const frozen=(v:any)=>{if(v&&typeof v==='object'){assert.ok(Object.isFrozen(v));for(const d of Object.values(Object.getOwnPropertyDescriptors(v))){assert.ok('value' in d);frozen(d.value);}}};
function native(root:string,plan:ReturnType<typeof planConfiguredQueries>){
  for(const a of plan.artifacts){const f=path.join(root,a.relative_path);fs.mkdirSync(path.dirname(f),{recursive:true});fs.writeFileSync(f,a.content);}
  const toolchain=read(path.resolve(project,'../../toolchains/node-typescript/toolchain.json')),image=nativeToolchainImage(toolchain.container_image);
  const args=['run','--rm','--pull','never','--network','none','--read-only','--cap-drop','ALL','--security-opt','no-new-privileges','--user',`${process.getuid!()}:${process.getgid!()}`,'--mount',`type=bind,source=${root},target=${root}`,'--workdir',root,image];
  assert.equal(execFileSync('docker',[...args,'tsc','--version'],{encoding:'utf8'}).trim(),'Version '+toolchain.typescript);
  const compile=()=>execFileSync('docker',[...args,'tsc','--ignoreConfig','--strict','--skipLibCheck','--declaration','--target','ES2022','--module','commonjs','--rootDir',path.join(root,plan.selection.module_root,'features'),'--outDir',path.join(root,'js'),...plan.artifacts.map(a=>path.join(root,a.relative_path))],{encoding:'utf8'});compile();
  const module=(id:string)=>plan.modules.find(m=>m.selector==='alpha:read-'+id)!,js=(id:string)=>path.join(root,'js/alpha/src/application/queries/read-'+id+'.js');
  const load=(id:string)=>createRequire(import.meta.url)(js(id))[module(id).callable];
  const observe=()=>{
    const expected=plan.modules.map(m=>{const id=m.selector.replace('alpha:read-',''),s=specs[id];const f=s.filter;
      return {path:path.join(root,m.provider_path),inputs:['min','enabled','label'],projection:s.projection,order_by:s.order_by,order_type:s.order_by?.field==='active'?'Bool':s.order_by?.field==='amount'?'UInt64':'String',limit:s.limit,
        ...(s.filter_expression!==undefined?{filter_expression:s.filter_expression}:{filter_pattern:'^\\((R[0-9]+Value)\\.key\\(row\\["'+f.left.name+'"\\]\\)===\\1\\.key\\(row\\["'+f.right.name+'"\\]\\)\\)$'})};});
    fs.writeFileSync(path.join(root,'tsconfig.json'),JSON.stringify({compilerOptions:{target:'ES2022',module:'NodeNext',strict:true,noEmit:true},files:expected.map(e=>e.path)}));fs.writeFileSync(path.join(root,'expected.json'),JSON.stringify(expected));
    const observer=path.join(project,'impl/cli/tools/observe-configured-queries.mjs');
    const supportObserver=path.join(project,'impl/cli/tools/structured-rule-support-observer.mjs');
    try{return JSON.parse(execFileSync('docker',[...args.slice(0,-1),'--mount',`type=bind,source=${observer},target=/observer.mjs,readonly`,'--mount',`type=bind,source=${supportObserver},target=/structured-rule-support-observer.mjs,readonly`,image,'node','/observer.mjs',path.join(root,'tsconfig.json'),path.join(root,'expected.json')],{encoding:'utf8'}));}catch(e){const error=e as any;if(error.status===1&&error.stdout)return JSON.parse(error.stdout);throw e;}
  };
  return {compile,load,js,module,observe};
}

test('Query plan binds checked fields and preserves source, layout, extension and previous compiler behavior',t=>{
  const f=fixture(t),p=f.plan(),old=planCompiledProjectBuild(f.graph,'typescript');
  assert.equal(p.modules.length,10);assert.equal(p.artifacts.length,20);assert.deepEqual(f.plan(),p);
  assert.deepEqual(planConfiguredQueries(f.boundary,f.fields,{...f.selection,roots:[...f.selection.roots].reverse()},sources),p);
  const alternate=planConfiguredQueries(f.boundary,f.fields,{...f.selection,module_root:'alternate'},sources);assert.deepEqual(alternate.artifacts.map(a=>a.content),p.artifacts.map(a=>a.content));
  const subset=planConfiguredQueries(f.boundary,f.fields,{...f.selection,roots:['alpha:read-all']},sources);assert.deepEqual(subset.artifacts,p.artifacts.filter(a=>a.relative_path.includes('/read-all.')));
  assert.deepEqual(planCompiledProjectBuild(f.graph,'typescript'),old);const {plan_sha256,...body}=p;assert.equal(plan_sha256,sha256(canonicalJson(body)));
  for(const m of p.modules){const {descriptor_sha256,...d}=m.descriptor;assert.equal(descriptor_sha256,sha256(canonicalJson(d)));assert.equal(d.provider.sha256,p.artifacts.find(a=>a.relative_path===m.provider_path)!.sha256);assert.equal(d.result_fields.map(f=>f.name).join(','),f.contracts[m.selector].projection.join(','));frozen(m.descriptor);}
  fs.renameSync(f.source,path.join(f.temp,'relocated'));assert.deepEqual(f.plan(),p);
});

test('Query providers emit only structured-value support used by their specialized program',t=>{
  void t;
  const values=createStructuredValueRenderer({declarations:[{selector:'billing:customer',kind:'Entity',contract:{properties:[property('CUSTOMER','id',scalar('UInt64'),true),property('CUSTOMER','name',scalar())]}}]} as any,(message:string):never=>{throw new Error(message);});
  values.ensure({kind:'list',element:{kind:'named',selector:'billing:customer'}});
  const content=values.source();
  assert.match(content,/const ruleString:/);
  assert.match(content,/const ruleUInt64:/);
  assert.match(content,/const ruleSequence/);
  assert.doesNotMatch(content,/const ruleBool:/);
  assert.doesNotMatch(content,/const ruleOptional/);
  assert.doesNotMatch(content,/const ruleToSet/);
  assert.doesNotMatch(content,/const ruleSum/);
});

test('Query rejects forged boundaries, stale fields, unsupported selection and unchecked operand compatibility',t=>{
  const f=fixture(t);
  for(const patch of [{schema_version:'future'},{language:'rust'},{value_profile:'number'},{boundary_sha256:'stale'},{field_compilation_sha256:'stale'},{roots:[]},{roots:['alpha:read-all','alpha:read-all']},{roots:['alpha:order']},{module_root:'../escape'},{module_root:'con'},{ignore_errors:true}])assert.throws(()=>planConfiguredQueries(f.boundary,f.fields,{...f.selection,...patch} as any,sources));
  assert.throws(()=>planConfiguredQueries(structuredClone(f.boundary),f.fields,f.selection,sources));assert.throws(()=>planConfiguredQueries(f.boundary,structuredClone(f.fields),f.selection,sources));
  for(const key of Object.keys(sources))assert.throws(()=>planConfiguredQueries(f.boundary,f.fields,f.selection,{...sources,[key]:(sources as any)[key]+' '}),/source drift/);
  let gets=0;assert.throws(()=>planConfiguredQueries(f.boundary,f.fields,{...f.selection,get roots(){gets++;return [];}},sources));assert.equal(gets,0);
  const mutate=(change:(c:any)=>void)=>{const file='specs/alpha/nodes/read-all.json',node=read(path.join(f.source,file));change(node.body.typed_contract);f.write(file,node);const graph=loadCompiledProjectGraph(f.source),digest=createCompiledProjectCertificate(graph).graph_sha256;
    const b=compileCompositionBoundary(graph,{schema_version:COMPOSITION_BOUNDARY_VERSION,contract_sha256:COMPOSITION_BOUNDARY_CONTRACT_SHA256,graph_sha256:digest},boundaryContract);
    const fields=compileSelectedProjectFields(graph,{...f.fields.selection,graph_sha256:digest},fieldContract);
    assert.throws(()=>planConfiguredQueries(b,f.fields,{...f.selection,boundary_sha256:b.boundary_sha256},sources),/cross-graph/);
    assert.throws(()=>planConfiguredQueries(b,fields,{...f.selection,boundary_sha256:b.boundary_sha256,field_compilation_sha256:fields.compilation_sha256},sources),/comparison type mismatch|ordering requires/);};
  mutate(c=>{c.filter=cmp('eq',field('amount'),param('label'));});
  mutate(c=>{c.filter=null;c.order_by={field:'note',direction:'asc'};});
});

test('Native Query preserves full-width order, repeated rows, nested values and read-model immutability',t=>{
  const f=fixture(t),p=f.plan(),n=native(path.join(f.temp,'native'),p),a=row('same','18446744073709551615','z'),b=row('same','9007199254740992','a'),c=row('other',2,'b');
  const caller=[a,b,c],before=structuredClone(caller),out=n.load('amount')(caller,{...params,min:'9007199254740992'});
  assert.deepEqual(out.map((x:any)=>x.amount),[9007199254740992n,18446744073709551615n]);assert.deepEqual(out.map((x:any)=>x.id),['same','same']);
  assert.equal(out[1].choice.payload.amount,18446744073709551615n);assert.equal(out[0].note,null);assert.deepEqual(out[0].labels,['a','z']);assert.equal(out[0].items.length,2);
  assert.deepEqual(caller,before);assert.equal(Object.isFrozen(caller),false);assert.equal(Object.isFrozen(a.money),false);frozen(out);
  a.money.amount=999;a.items[0].amount=999;assert.equal(out[1].money.amount,4n);assert.equal(out[1].items[0].amount,1n);assert.throws(()=>{out[0].money.amount=5n;});
  assert.deepEqual(Object.keys(out[0]),allProjection);assert.equal('other_customer' in out[0],false);
  const ties=[row('first',1),row('second',1),row('third',1)];assert.deepEqual(n.load('amount')(ties,params).map((x:any)=>x.id),['first','second']);
  assert.deepEqual(n.load('all')([],params),[]);assert.deepEqual(n.load('label')(caller,{...params,label:'absent'}),[]);
  const unicode=['é','e\u0301','😀','\ue000'].map((x,i)=>row(String(i),1,x));assert.deepEqual(n.load('sorted')(unicode,params).map((r:any)=>r.label),unicode.map(r=>r.label).sort());
  const truth=[row('true'),{...row('false'),active:false}];assert.deepEqual(n.load('enabled')(truth,{...params,enabled:false}).map((r:any)=>r.id),['true','false']);
  const predicateRows=[5,6,8,9,10].map(v=>row(String(v),v));predicateRows.push({...row('inactive',0),active:false});assert.deepEqual(n.load('predicate')(predicateRows,{...params,min:8}).map((r:any)=>r.id),['6','8','inactive']);
  const choices=[{variant:'None'},{variant:'Amount',payload:'18446744073709551615'},{variant:'Money',payload:money(0)}];assert.deepEqual(n.load('all')(choices.map(choice=>({...row(),choice})),params).map((r:any)=>r.choice),[{variant:'None'},{variant:'Amount',payload:18446744073709551615n},{variant:'Money',payload:money(0n)}]);
  assert.ok(fs.existsSync(n.js('all').replace(/\.js$/,'.d.ts')),'native declaration output is usable');
  for(const m of p.modules){const fn=n.load(m.selector.replace('alpha:read-',''));assert.ok(Object.isFrozen(fn));assert.deepEqual(fn.descriptor,m.descriptor);frozen(fn.descriptor);}
  const script=`const f=require(${JSON.stringify(n.js('all'))})[${JSON.stringify(n.module('all').callable)}];const result=f(${JSON.stringify([row()])},${JSON.stringify(params)});process.stdout.write(JSON.stringify({pid:process.pid,result},(_,v)=>typeof v==='bigint'?v.toString():v));`;
  const run=()=>JSON.parse(execFileSync(process.execPath,['-e',script],{encoding:'utf8'}));const first=run(),second=run();assert.notEqual(first.pid,second.pid);assert.deepEqual(first.result,second.result);
});

test('Query equality retains Entity identity, value semantics, optional absence and list occurrences',t=>{
  const f=fixture(t),n=native(path.join(f.temp,'equal'),f.plan()),a=row(),b=row('b');
  assert.equal(n.load('identity')([a],params).length,1,'different customer labels do not change identity');b.other_customer.id='other';assert.equal(n.load('identity')([b],params).length,0);
  b.other_money.currency='USD';assert.equal(n.load('value')([a,b],params).length,1,'Value Object compares nonidentity fields');
  b.other_items=[money(1)];assert.equal(n.load('list')([a,b],params).length,1,'list occurrences are preserved');
  b.items=[money(1),money(2)];b.other_items=[money(2),money(1)];assert.equal(n.load('list')([b],params).length,0,'list order is preserved');
  b.note='present';assert.equal(n.load('optional')([a,b],params).length,1);assert.equal(n.load('optional')([a],params)[0].note,null);
  assert.equal(n.load('all')([a],params).length,1,'declared false Value Object invariant is not executed by Query normalization');
});

test('Query validates complete inert inputs without coercion, getter reads, hidden writes or mutable aliases',t=>{
  const f=fixture(t),n=native(path.join(f.temp,'hostile'),f.plan()),query=n.load('all');let calls=0;
  const getter={...row(),get amount(){calls++;return 4;}};assert.throws(()=>query([getter],params),/QUERY_INPUT/);assert.equal(calls,0);
  const getterParam={...params,get min(){calls++;return 0;}};assert.throws(()=>query([row()],getterParam),/QUERY_INPUT/);assert.equal(calls,0);
  const sparse:any=[];sparse.length=1;const arr:any=[row()];Object.defineProperty(arr,'0',{get(){calls++;return row();},enumerable:true});
  for(const bad of [null,{},sparse,arr,Object.assign([row()],{extra:1})])assert.throws(()=>query(bad,params),/QUERY_INPUT/);assert.equal(calls,0);
  for(const patch of [{amount:'01'},{amount:'18446744073709551616'},{active:1},{labels:['x','x']},{state:{variant:'Unknown'}},{choice:{variant:'None',payload:1}},{money:{amount:1}},{items:[{amount:1,currency:'GBP',extra:true}]},{other_money:{amount:1,currency:null}}])assert.throws(()=>query([{...row(),...patch}],params),/QUERY_INPUT/);
  for(const bad of [{...params,extra:1},{...params,label:undefined},{...params,min:Infinity},null,Object.create(params)])assert.throws(()=>query([row()],bad),/QUERY_INPUT/);
  const boxed={valueOf(){calls++;return 0;}};assert.throws(()=>query([row()],{...params,min:boxed}),/QUERY_INPUT/);assert.equal(calls,0);
  const all=row();delete all.id;assert.throws(()=>query([all],params),/QUERY_INPUT/);
  assert.throws(()=>n.load('amount')([{...row(),amount:0,other_money:{amount:'bad',currency:'GBP'}}],{...params,min:10}),/QUERY_INPUT/,'even filtered-out rows validate');
  const observed=row();let writes=0;const proxy=new Proxy(observed,{set(){writes++;return false;},defineProperty(){writes++;return false;},deleteProperty(){writes++;return false;}});query([proxy],params);assert.equal(writes,0,'bounded instrumented input observes no attempted source write');
});

test('Independent native Query observer rejects compiling filter, order, projection and effect mutations',t=>{
  const f=fixture(t),p=f.plan(),root=path.join(f.temp,'observed'),n=native(root,p);assert.equal(n.observe().result,'pass');
  const m=n.module('amount'),a=p.artifacts.find(a=>a.relative_path===m.provider_path)!;
  const mutants=[a.content.replace('row["amount"] >= p0','row["amount"] <= p0'),a.content.replace('selected.slice(0,2)','selected.slice(0,1)'),a.content.replace('["label"]:row["label"]','["label"]:row["id"]'),a.content.replace(' ? -1 : ',' ? 1 : '),a.content.replace('  return Object.freeze(selected.map','  Date.now();\n  return Object.freeze(selected.map'),a.content.replace('  return Object.freeze(selected.map','  (globalThis as any).changed=true;\n  return Object.freeze(selected.map'),a.content.replace('  return Object.freeze(selected.map','  queueMicrotask(()=>{});\n  return Object.freeze(selected.map'),
    a.content+'const extra=Object.defineProperty(Object.prototype,"changed",{value:true});\n',a.content+'const R999Value=Object.freeze(Object.prototype);\n',
    a.content.replace('const d=ruleData(input,["amount","currency"]);','(input as Record<string,unknown>)["amount"]=0n; const d=ruleData(input,["amount","currency"]);')];
  for(const mutant of mutants){assert.notEqual(mutant,a.content);fs.writeFileSync(path.join(root,m.provider_path),mutant);n.compile();assert.equal(n.observe().result,'fail');}
});

test('Shared structured-value extraction emits only the Rule capabilities the program uses',()=>{
  const scalar=(name:string)=>({kind:'scalar',name}),named=(selector:string)=>({kind:'named',selector}),prop=(name:string,type:any,identity=false)=>({name,type,identity});
  const declarations=[{selector:'demo:money',kind:'Value Object',contract:{properties:[prop('amount',scalar('UInt64')),prop('currency',scalar('String'))]}},{selector:'demo:state',kind:'Enum',contract:{variants:[{name:'None',ontology_variant:'DEMO-STATE#None',payload:null},{name:'Paid',ontology_variant:'DEMO-STATE#Paid',payload:named('demo:money')}]}},{selector:'demo:order',kind:'Entity',contract:{properties:[prop('id',scalar('String'),true),prop('enabled',scalar('Bool')),prop('money',named('demo:money')),prop('state',named('demo:state')),prop('note',{kind:'optional',element:scalar('String')}),prop('items',{kind:'list',element:named('demo:money')}),prop('tags',{kind:'set',element:scalar('String')})]}}];
  const rule={parameters:[{name:'value',type:named('demo:order')}],expression:{op:'eq',left:{op:'path',root:'value',properties:[]},right:{op:'path',root:'value',properties:[]}}};
  const source=renderStructuredRule(rule as any,{selector:'demo:equal',closure_sha256:'fixture',callable:'ruleEqual',imports:[]} as any,{declarations} as any);
  assert.deepEqual([...source.matchAll(/\/\/ structured-rule-capability:([^\n]+)/g)].map(match=>match[1]),['base','String','Bool','UInt64','optional','sequence','sum']);
  assert.doesNotMatch(source,/structured-rule-capability:to-set/);
});

import {nativeToolchainImage} from '../helpers/native-toolchain-image.ts';
