import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {execFileSync} from 'node:child_process';
import {createRequire} from 'node:module';
import {fileURLToPath} from 'node:url';
import test from 'node:test';
import {loadCompiledProjectGraph} from '../../src/input/project-model.ts';
import {planConfiguredRules,STRUCTURED_RULE_VERSION,EXACT_LITERAL_RULE_VERSION} from '../../src/generation/configured-rules.ts';
import {EXACT_UINT64_PROFILE} from '../../src/generation/exact-uint64.ts';
import {canonicalJson,sha256} from '../../src/input/source-manifest.ts';

const project=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../../../..');
const base='development/reconciliation-v1/profile-compiler-reconciliation/';
const read=(p:string)=>fs.readFileSync(path.join(project,p),'utf8');
const sources={configuration:read(base+'configuration.json'),
  base:read('development/implementation-conformance/ontology-experiment/profiles/base-domain.profile.json'),
  typescript:read('development/implementation-conformance/ontology-experiment/profiles/typescript-strict.profile.json'),
  rule_contract:read(base+'string-order-rule-contract.json'),collection_contract:read(base+'rule-collection-value-contract.json'),
  predicate_contract:read(base+'rule-collection-predicate-contract.json'),numeric_contract:read(base+'rule-numeric-contract.json'),
  exact_contract:read(base+'rule-exact-contract.json'),literal_contract:read(base+'rule-exact-literal-contract.json'),
  structured_contract:read(base+'rule-structured-value-contract.json'),
  field_contract:read('development/reconciliation-v1/contracts/exact-field-and-reference-model.json')};
const scalar=(name='String')=>({kind:'scalar',name});
const named=(id:string)=>({kind:'named',selector:'commerce:'+id});
const wrap=(kind:string,element:any)=>({kind,element});
const at=(root:string,...properties:string[])=>({op:'path',root,properties});
const lit=(type:string,value:any)=>({op:'literal',type,value});
const eq=(left:any,right:any)=>({op:'eq',left,right});
const sum={kind:'sum',variants:[{name:'None',ontology_variant:'FIXTURE-RESULT#None',payload:null},{name:'Amount',ontology_variant:'FIXTURE-RESULT#Amount',payload:scalar('UInt64')},{name:'Money',ontology_variant:'FIXTURE-RESULT#Money',payload:named('money')}]};
const property=(owner:string,name:string,type:any,identity=false)=>({name,type,identity,cardinality:type.kind==='optional'?'optional':type.kind==='list'?'many':type.kind==='set'?'many-unique':'one',meaning:name,ontology_property:'FIXTURE-'+owner+'#'+name});
function fixture(t:any){
  const temp=fs.mkdtempSync(path.join(os.tmpdir(),'pcr-rule-values-'));t.after(()=>fs.rmSync(temp,{recursive:true,force:true}));
  const source=path.join(temp,'source'),nodes:string[]=[],rules:Record<string,any>={};
  const write=(p:string,value:any)=>{const file=path.join(source,p);fs.mkdirSync(path.dirname(file),{recursive:true});fs.writeFileSync(file,JSON.stringify(value,null,2)+'\n');};
  const node=(id:string,kind:string,body:any)=>{nodes.push(id);write('specs/commerce/nodes/'+id+'.json',{schema_version:'domainspec.node/v1',feature_id:'commerce',node_id:id,kind,body:{description:id,...body}});};
  const record=(id:string,kind:string,properties:any[])=>node(id,kind,{fields:properties.map(p=>p.name),...(kind==='Value Object'?{invariant_refs:['commerce:valid']}:{ }),typed_contract:{schema_version:'domainspec.typed-record/v1',ontology_node:'FIXTURE-'+id.toUpperCase(),properties}});
  record('money','Value Object',[property('MONEY','amount',scalar('UInt64')),property('MONEY','currency',scalar()),property('MONEY','note',wrap('optional',scalar()))]);
  record('customer','Entity',[property('CUSTOMER','id',scalar(),true),property('CUSTOMER','label',scalar()),property('CUSTOMER','balance',named('money'))]);
node('status','Enum',{values:['Pending','Ready'],typed_contract:{schema_version:'domainspec.typed-sum/v1',ontology_node:'FIXTURE-STATUS',variants:[{name:'Pending',ontology_variant:'FIXTURE-STATUS#Pending',payload:null},{name:'Ready',ontology_variant:'FIXTURE-STATUS#Ready',payload:null}]}});
  const rule=(id:string,parameters:any[],expression:any)=>{rules[id]={parameters,expression};node(id,'Rule',{predicate:'structured:domainspec.typed-rule/v1',typed_contract:{schema_version:'domainspec.typed-rule/v2',ontology_rule:'RULE-'+id.toUpperCase(),parameters,expression}});};
  const param=(name:string,type:any)=>({name,type});
  rule('valid',[param('value',scalar())],{op:'not',term:eq(at('value'),lit('String',''))});
  for(const [id,type] of Object.entries({entity:named('customer'),value:named('money'),status:named('status'),optional:wrap('optional',scalar('UInt64')),sum,nested:wrap('list',wrap('set',named('money')))})){
    rule('equal-'+id,[param('left',type),param('right',type)],eq(at('left'),at('right')));
  }
  rule('ready',[param('status',named('status'))],eq(at('status'),{op:'variant',selector:'FIXTURE-STATUS#Ready'}));
  rule('balance',[param('customer',named('customer')),param('cap',scalar('UInt64'))],{op:'lt',left:at('customer','FIXTURE-CUSTOMER#balance','FIXTURE-MONEY#amount'),right:at('cap')});
  rule('forward',[param('customer',named('customer')),param('cap',scalar('UInt64'))],{op:'rule_ref',selector:'commerce:balance',arguments:[{parameter:'customer',value:at('customer')},{parameter:'cap',value:at('cap')}]});
  for(const kind of ['list','set']){
    rule('project-'+kind,[param('customers',wrap(kind,named('customer'))),param('labels',wrap(kind,scalar()))],eq(at('customers','FIXTURE-CUSTOMER#label'),at('labels')));
    rule('contains-'+kind,[param('customers',wrap(kind,named('customer'))),param('customer',named('customer'))],{op:'contains',left:at('customers'),right:at('customer')});
  }
  rule('unique',[param('customers',wrap('list',named('customer')))],{op:'unique',binding:'c',collection:at('customers'),where:eq(at('c','FIXTURE-CUSTOMER#balance'),at('c','FIXTURE-CUSTOMER#balance'))});
  rule('exists',[param('customers',wrap('list',named('customer')))],{op:'exists',binding:'c',collection:at('customers'),where:{op:'lt',left:at('c','FIXTURE-CUSTOMER#balance','FIXTURE-MONEY#amount'),right:lit('UInt64','18446744073709551615')}});
  rule('one',[param('customers',wrap('list',named('customer')))],{op:'exactly_one',binding:'c',collection:at('customers'),where:eq(at('c','FIXTURE-CUSTOMER#label'),lit('String','Alex'))});
  rule('image',[param('customers',wrap('list',named('customer'))),param('labels',wrap('set',scalar()))],{op:'set_equal',left:{op:'to_set',value:at('customers','FIXTURE-CUSTOMER#label')},right:at('labels')});
  write('project.json',{schema_version:'domainspec.project/v1',project_id:'structured-rules',features:['commerce'],cross_feature_edges:[]});
  write('specs/commerce/feature.json',{schema_version:'domainspec.feature/v1',feature_id:'commerce',nodes,edges:[]});
  const selection={schema_version:STRUCTURED_RULE_VERSION,language:'typescript',module_root:'application',value_profile:EXACT_UINT64_PROFILE,roots:Object.keys(rules).map(id=>'commerce:'+id)} as const;
  const graph=loadCompiledProjectGraph(source),plan=planConfiguredRules(graph,selection,sources);
  return {temp,source,write,selection,graph,plan,rules};
}
const file=(id:string)=>'application/features/commerce/src/domain/rules/'+id+'.ts';
const callable=(id:string)=>'rule'+id.split('-').map(w=>w[0]!.toUpperCase()+w.slice(1)).join('');
function native(root:string,artifacts:readonly {relative_path:string;content:string}[]){
  for(const a of artifacts){const p=path.join(root,a.relative_path);fs.mkdirSync(path.dirname(p),{recursive:true});fs.writeFileSync(p,a.content,{flag:'wx'});}
  const chain=JSON.parse(read('../../toolchains/node-typescript/toolchain.json'));
  const image=nativeToolchainImage(chain.container_image);
  const args=['run','--rm','--pull','never','--network','none','--read-only','--cap-drop','ALL','--security-opt','no-new-privileges','--user',process.getuid!()+':'+process.getgid!(),'--mount','type=bind,source='+root+',target='+root,'--workdir',root,image,'tsc'];
  assert.equal(execFileSync('docker',[...args,'--version'],{encoding:'utf8'}).trim(),'Version '+chain.typescript);
  const compile=(extra:string[]=[])=>execFileSync('docker',[...args,'--ignoreConfig','--strict','--skipLibCheck','--target','ES2022','--module','commonjs','--declaration','--rootDir',root,'--outDir',path.join(root,'js'),...artifacts.map(a=>path.join(root,a.relative_path)),...extra],{encoding:'utf8',stdio:'pipe'});
  try{compile();}catch(e){throw new Error(String((e as any).stdout));}
  const run=(id:string,args:any)=>createRequire(import.meta.url)(path.join(root,'js',file(id).replace(/\.ts$/,'.js')))[callable(id)](args);
  return {run,compile,image};
}
const money=(amount:any=2,currency='GBP',patch:object={})=>({amount,currency,...patch});
const customer=(id='a',label='Alex',balance=money())=>({id,label,balance});

function observe(root:string,image:string,rules:Record<string,any>){
  const expected=Object.entries(rules).map(([id,r])=>({path:file(id),callable:callable(id),parameters:r.parameters.map((p:any)=>p.name),
    imports:id==='forward'?[{path:'./balance.js',symbol:'ruleBalance',local:'dependency0'}]:[],
    ...(id==='balance'?{return_expression:'(p0["balance"]["amount"] < p1)'}:{})}));
  fs.writeFileSync(path.join(root,'tsconfig.json'),JSON.stringify({compilerOptions:{target:'ES2022',module:'NodeNext',strict:true,noEmit:true},files:expected.map(e=>e.path)}));
  fs.writeFileSync(path.join(root,'expected.json'),JSON.stringify(expected));
  const observer=path.join(project,'impl/cli/tools/observe-configured-rule-values.mjs');
  const supportObserver=path.join(project,'impl/cli/tools/structured-rule-support-observer.mjs');
  const args=['run','--rm','--pull','never','--network','none','--read-only','--cap-drop','ALL','--security-opt','no-new-privileges','--tmpfs','/tmp','--user',process.getuid!()+':'+process.getgid!(),'--mount','type=bind,source='+root+',target='+root+',readonly','--mount','type=bind,source='+observer+',target=/observer.mjs,readonly','--mount','type=bind,source='+supportObserver+',target=/structured-rule-support-observer.mjs,readonly',image,'node','/observer.mjs',path.join(root,'tsconfig.json'),path.join(root,'expected.json')];
  try{return JSON.parse(execFileSync('docker',args,{encoding:'utf8',stdio:'pipe'}));}catch(e){if((e as any).status===1&& (e as any).stdout)return JSON.parse((e as any).stdout);throw e;}
}

test('PCR-06 independent native AST and negative types verify structured Rule boundaries',t=>{
  const f=fixture(t),root=path.join(f.temp,'observed'),n=native(root,f.plan.artifacts);
  assert.deepEqual(observe(root,n.image,f.rules).errors,[]);
  const consumer=path.join(root,'consumer.ts');
  fs.writeFileSync(consumer,[
    'import {ruleEqualSum} from "./'+file('equal-sum').replace(/\.ts$/,'.js')+'";',
    'import {ruleEqualOptional} from "./'+file('equal-optional').replace(/\.ts$/,'.js')+'";',
    'import {ruleEqualValue} from "./'+file('equal-value').replace(/\.ts$/,'.js')+'";',
    'ruleEqualSum({left:{variant:"Amount",payload:2n},right:{variant:"None"}});',
    'ruleEqualValue({left:{amount:"18446744073709551615",currency:"GBP"},right:{amount:2n,currency:"GBP",note:null}});',
    '// @ts-expect-error missing required sum payload',
    'ruleEqualSum({left:{variant:"Amount"},right:{variant:"None"}});',
    '// @ts-expect-error optional formal arguments are still required',
    'ruleEqualOptional({left:null});',
    '// @ts-expect-error numeric field cannot be Boolean',
    'ruleEqualValue({left:{amount:true,currency:"GBP"},right:{amount:2,currency:"GBP"}});',
  ].join('\n'));n.compile([consumer]);
  fs.appendFileSync(consumer,'\nruleEqualOptional({left:null});');
  assert.throws(()=>n.compile([consumer]),(e:any)=>/right.*missing|Property 'right'/.test(String(e.stdout)));
});

test('PCR-06 compiling mutations separate AST validation from semantic evidence',t=>{
  const f=fixture(t);
  const mutate=(id:string,from:string,to:string)=>f.plan.artifacts.map(a=>{
    if(a.relative_path!==file(id))return a;assert.ok(a.content.includes(from));return {...a,content:a.content.replace(from,to)};
  });
  const reversed=path.join(f.temp,'reversed'),nr=native(reversed,mutate('balance','(p0["balance"]["amount"] < p1)','(p0["balance"]["amount"] > p1)'));
  assert.ok(observe(reversed,nr.image,f.rules).errors.some((e:string)=>e.startsWith('expression:')));
  assert.equal(nr.run('balance',{customer:customer(),cap:3}),false);
  const collapsed=path.join(f.temp,'collapsed'),nc=native(collapsed,mutate('equal-entity','rulePart(value)',"rulePart('collapsed')"));
  assert.ok(observe(collapsed,nc.image,f.rules).errors.some((e:string)=>e.startsWith('support-drift:')));
  assert.equal(nc.run('equal-entity',{left:customer('a'),right:customer('b')}),true);
  // Identity versus state is a semantic property, outside this AST observer's claim.
  const identity=path.join(f.temp,'identity'),ni=native(identity,mutate('equal-entity','.key(value["id"])','.key(value["label"])'));
  assert.deepEqual(observe(identity,ni.image,f.rules).errors,[]);
  assert.equal(ni.run('equal-entity',{left:customer('a'),right:customer('b')}),true);
});

test('PCR-06 structured Rules bind checked declarations deterministically without widening legacy selections',t=>{
  const f=fixture(t),p=f.plan;
  assert.equal(p.schema_version,'domainspec.configured-rules-plan/v8-candidate');
  assert.equal(p.authority_effect,'none');assert.ok((p as any).field_model_sha256);
  assert.deepEqual(planConfiguredRules(f.graph,f.selection,sources),p);
  const {plan_sha256,...body}=p;assert.equal(plan_sha256,sha256(canonicalJson(body)));
  assert.deepEqual(planConfiguredRules(f.graph,{...f.selection,roots:[...f.selection.roots].reverse()},sources),p);
  const {structured_contract,field_contract,...old}=sources;
  assert.throws(()=>planConfiguredRules(f.graph,{...f.selection,schema_version:EXACT_LITERAL_RULE_VERSION},old),/Rule|parameter|dependency/);
  for(const key of Object.keys(sources))assert.throws(()=>planConfiguredRules(f.graph,f.selection,{...sources,[key]:(sources as any)[key]+' '}),/drift/);
  fs.renameSync(f.source,path.join(f.temp,'moved'));
  assert.deepEqual(planConfiguredRules(f.graph,f.selection,sources),p);
  assert.deepEqual(planConfiguredRules(loadCompiledProjectGraph(path.join(f.temp,'moved')),f.selection,sources),p);
  assert.throws(()=>planConfiguredRules(structuredClone(f.graph),f.selection,sources),/unvalidated|changed/);
});

test('PCR-06 native structured Rules preserve identity value optional sum and exact-number distinctions',t=>{
  const f=fixture(t),n=native(path.join(f.temp,'native'),f.plan.artifacts),r=n.run;
  assert.equal(r('equal-entity',{left:customer(),right:customer('a','Changed',money(9))}),true);
  assert.equal(r('equal-entity',{left:customer(),right:customer('b')}),false);
  assert.equal(r('equal-value',{left:money(),right:money('2','GBP',{note:null})}),true);
  for(const other of [money(3),money(2,'USD'),money(2,'GBP',{note:''})])assert.equal(r('equal-value',{left:money(),right:other}),false);
  assert.equal(r('equal-value',{left:money(1,'é'),right:money(1,'e\u0301')}),false);
  assert.equal(r('equal-value',{left:money('18446744073709551615'),right:money(18446744073709551615n)}),true);
  assert.equal(r('equal-value',{left:money('9007199254740992'),right:money('9007199254740993')}),false);
  assert.equal(r('equal-optional',{left:null,right:0}),false);assert.equal(r('equal-optional',{left:2n,right:'2'}),true);
  assert.throws(()=>r('equal-optional',{left:null}),/RULE_INPUT/);
  assert.equal(r('equal-sum',{left:{variant:'Money',payload:money()},right:{variant:'Money',payload:money('2')}}),true);
  assert.equal(r('equal-sum',{left:{variant:'None'},right:{variant:'Amount',payload:0}}),false);
  assert.equal(r('equal-status',{left:{variant:'Pending'},right:{variant:'Ready'}}),false);
  assert.equal(r('ready',{status:{variant:'Ready'}}),true);assert.equal(r('ready',{status:{variant:'Pending'}}),false);
  assert.equal(r('equal-nested',{left:[[money(),money(3)]],right:[[money(3),money('2')]]}),true);
  assert.equal(r('equal-nested',{left:[[money()],[money(3)]],right:[[money(3)],[money()]]}),false);
  assert.equal(r('forward',{customer:customer('a','Alex',money('18446744073709551614')),cap:'18446744073709551615'}),true);
  assert.equal(r('forward',{customer:customer('a','Alex',money('18446744073709551615')),cap:'18446744073709551615'}),false);
});

test('PCR-06 collection predicates and projections preserve occurrences versus membership',t=>{
  const f=fixture(t),r=native(path.join(f.temp,'collections'),f.plan.artifacts).run;
  const a=customer(),b=customer('b'),c=customer('c','Other',money(3));
  assert.equal(r('project-list',{customers:[a,b],labels:['Alex','Alex']}),true);
  assert.equal(r('project-list',{customers:[a,b],labels:['Alex']}),false);
  assert.equal(r('project-set',{customers:[a,b],labels:['Alex']}),true);
  assert.equal(r('project-set',{customers:[a,c],labels:['Other','Alex']}),true);
  assert.equal(r('image',{customers:[a,b,c],labels:['Alex','Other']}),true);
  for(const kind of ['list','set'])assert.equal(r('contains-'+kind,{customers:[a,b],customer:customer('a','Different')}),true);
  assert.throws(()=>r('contains-set',{customers:[a,customer('a','Changed')],customer:a}),/RULE_INPUT/);
  assert.equal(r('unique',{customers:[a,b]}),false);assert.equal(r('unique',{customers:[a,c]}),true);
  assert.equal(r('exists',{customers:[]}),false);assert.equal(r('exists',{customers:[a]}),true);
  assert.equal(r('one',{customers:[a,c]}),true);assert.equal(r('one',{customers:[a,b]}),false);
  const original=[a,b];r('project-list',{customers:original,labels:['Alex','Alex']});assert.deepEqual(original,[a,b]);assert.equal(Object.isFrozen(a),false);
});

test('PCR-06 closed recursive inputs reject hostile data without evaluating accessors',t=>{
  const f=fixture(t),r=native(path.join(f.temp,'hostile'),f.plan.artifacts).run;
  let calls=0;const accessor=Object.defineProperty(money(),'amount',{get(){calls++;return 2;},enumerable:true});
  const hidden=Object.defineProperty(money(),'hidden',{value:1});
  const symbol=Object.assign(money(),{[Symbol('x')]:1});
  for(const bad of [accessor,hidden,symbol,{...money(),extra:1},Object.create(money()),{currency:'GBP'},money('02'),money('2\n'),money(-1),money(2.5),money(Number.MAX_SAFE_INTEGER+1),money('18446744073709551616'),money(true)]){
    assert.throws(()=>r('equal-value',{left:bad,right:money()}),/RULE_INPUT/);
  }
  assert.equal(calls,0);
  const badArray=[customer()];Object.defineProperty(badArray,'0',{get(){calls++;return customer();},enumerable:true});
  for(const customers of [badArray,Array(1),Object.assign([customer()],{extra:1})])assert.throws(()=>r('exists',{customers}),/RULE_INPUT/);
  for(const left of [{variant:'None',payload:null},{variant:'Amount'},{variant:'other'},{variant:'Money',payload:{...money(),note:undefined}}])assert.throws(()=>r('equal-sum',{left,right:{variant:'None'}}),/RULE_INPUT/);
  assert.equal(calls,0);
  assert.equal(r('equal-value',{left:Object.assign(Object.create(null),money()),right:money()}),true);
});

import {nativeToolchainImage} from '../helpers/native-toolchain-image.ts';
