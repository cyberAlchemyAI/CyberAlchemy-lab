import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {execFileSync} from 'node:child_process';
import test from 'node:test';
import {recordWitnessFixture} from '../helpers/record-witness-project.ts';
import {loadCompiledProjectGraph} from '../../src/input/project-model.ts';
import {planCompiledReconciledProject} from '../../src/generation/reconciled-project.ts';
import {createCrossGeneratorBoundary} from '../../src/verification/reconciled-cross-generator-boundary.ts';
import {createCrossGeneratorOwnedValueControls,crossGeneratorOwnedValueProbe,checkCrossGeneratorOwnedValueObservations} from '../../src/verification/reconciled-cross-generator-owned-values.ts';
import {CROSS_GENERATOR_OWNED_VALUES_RUNNER} from '../../src/verification/reconciled-cross-generator-owned-values-runner.ts';
const project=path.resolve(import.meta.dirname,'../../../..'),base=path.join(project,'development/reconciliation-v1/profile-compiler-reconciliation');
const definition=fs.readFileSync(path.join(base,'cross-generator-owned-values-contract.json'),'utf8'),boundaryDefinition=fs.readFileSync(path.join(base,'cross-generator-verification-contract.json'),'utf8');
type Fixture=ReturnType<typeof recordWitnessFixture>;
function controls(f:Fixture){
 const graph=loadCompiledProjectGraph(f.source),plan=planCompiledReconciledProject(graph,f.selection),boundary=createCrossGeneratorBoundary(graph,plan,boundaryDefinition);
 return {graph,plan,boundary,c:createCrossGeneratorOwnedValueControls(graph,plan,boundary,definition)};
}
function native(f:Fixture){
 const {graph,plan,boundary,c}=controls(f),probe=crossGeneratorOwnedValueProbe(c);
 const source=path.join(f.root,'generated-source'),output=path.join(f.root,'native'),input=path.join(f.root,'probe.json'),runner=path.join(f.root,'runner.mjs');
 fs.mkdirSync(source);fs.mkdirSync(output);fs.writeFileSync(path.join(f.root,'package.json'),'{"type":"commonjs"}');
 const paths=[...new Set(probe.rows.flatMap(r=>r.modules.map(m=>m.relative_path)))].sort();
 for(const p of paths){const a=plan.resolved.artifacts.find(a=>a.relative_path===p)!;const file=path.join(source,p);fs.mkdirSync(path.dirname(file),{recursive:true});fs.writeFileSync(file,a.content);}
 const config=path.join(f.root,'compiler.json');fs.writeFileSync(config,JSON.stringify({compilerOptions:{strict:true,skipLibCheck:true,target:'ES2022',module:'CommonJS',rootDir:source,outDir:output,types:[],noEmitOnError:true},files:paths.map(p=>path.join(source,p))}));
 fs.writeFileSync(input,JSON.stringify(probe));fs.writeFileSync(runner,CROSS_GENERATOR_OWNED_VALUES_RUNNER);
 const image=nativeToolchainImage();assert.equal(image, NATIVE_TEST_IMAGE_ID);
 const docker=['run','--rm','--pull','never','--network','none','--read-only','--cap-drop','ALL','--security-opt','no-new-privileges','--user',process.getuid!()+':'+process.getgid!(),'--mount','type=bind,source='+f.root+',target='+f.root,'--workdir',f.root,image];
 const command=(args:string[])=>{try{return execFileSync('docker',[...docker,...args],{encoding:'utf8',stdio:'pipe',timeout:60000,maxBuffer:16777216});}catch(e:any){throw Error(String(e.stdout)+String(e.stderr));}};
 const compile=()=>command(['tsc','--project',config,'--pretty','false']);
 const observe=()=>JSON.parse(command(['node','--permission','--allow-fs-read='+f.root,'--disable-proto=throw',runner,input,output]));
 compile();return {graph,plan,boundary,c,probe,source,output,paths,input,runner,compile,observe};
}
function checked(n:ReturnType<typeof native>){
 const observation=n.observe();
 for(const row of n.c.rows)if(row.state==='ready'){
  const actual=observation.rows.find((r:any)=>r.selector===row.selector);
  for(let i=0;i<row.cases.length;i++)assert.deepEqual(actual.cases[i],row.cases[i]!.expected,row.selector+' '+row.cases[i]!.id);
 }
 return {observation,result:checkCrossGeneratorOwnedValueObservations(n.c,observation)};
}
test('owned field controls preserve complete source occurrence coverage and omit expected answers from probes',t=>{
 const f=recordWitnessFixture(t),{graph,plan,boundary,c}=controls(f),probe=crossGeneratorOwnedValueProbe(c);
 assert.equal(c.rows.find(r=>r.selector==='alpha:money')!.state,'inapplicable');
 const customer=c.rows.find(r=>r.selector==='alpha:customer')!;assert.equal(customer.state,'ready');if(customer.state!=='ready')throw Error('unavailable');
 assert.equal(customer.protocol.length,1);assert.deepEqual(customer.ownership_coverage[0]!.modes,['clone-named','foreign-named','owned','raw-named']);
 assert.ok(customer.cases.length>0);assert.ok(Object.isFrozen(customer.cases));assert.ok(!JSON.stringify(probe).includes('"expected"'));
 assert.throws(()=>crossGeneratorOwnedValueProbe(structuredClone(c)),/registered/);
 assert.throws(()=>createCrossGeneratorOwnedValueControls(graph,plan,boundary,definition+'\n'),/definition drift/);
 assert.throws(()=>createCrossGeneratorOwnedValueControls(graph,plan,structuredClone(boundary),definition),/registered/);
});
test('original factories consume owned values and reject raw cloned and foreign objects in both module roots',t=>{
 for(const module_root of ['domain','application/domain']){
  const f=recordWitnessFixture(t);f.selection={...f.selection,module_root} as typeof f.selection;
  const n=native(f),{result}=checked(n);assert.equal(result.tested_factory_count,1);assert.deepEqual(result.remaining,[]);
  t.diagnostic(JSON.stringify({module_root,...result}));
 }
});
test('duplicate ownership calls cannot hide behind unchanged native factory outcomes',t=>{
 const n=native(recordWitnessFixture(t)),{observation:baseline}=checked(n);
 const relative=n.paths.find(p=>p.endsWith('/customer.ts'))!,file=path.join(n.source,relative),source=fs.readFileSync(file,'utf8');
 const mutant=source.replace('if(!provider.isOwned(input))','if(!(provider.isOwned(input),provider.isOwned(input)))');
 assert.notEqual(mutant,source);fs.writeFileSync(file,mutant);n.compile();const actual=n.observe();
 assert.deepEqual(actual.rows.map((r:any)=>r.cases.map(({calls,...c}:any)=>c)),baseline.rows.map((r:any)=>r.cases.map(({calls,...c}:any)=>c)));
 assert.throws(()=>checkCrossGeneratorOwnedValueObservations(n.c,actual),/native observation mismatch/);
 fs.writeFileSync(file,source);n.compile();checked(n);
});
test('incomplete or active native evidence never passes the owned-value protocol',t=>{
 const n=native(recordWitnessFixture(t)),{observation}=checked(n);
 const mutations=[
  (v:any)=>v.rows.pop(),(v:any)=>v.rows.push(v.rows[0]),(v:any)=>v.rows[0].cases.pop(),(v:any)=>v.rows[0].cases.reverse(),
  (v:any)=>v.rows[0].cases[0].calls.pop(),(v:any)=>{v.rows[0].cases[0].calls[0].input_paths=[['wrong']];},
  (v:any)=>{v.rows[0].cases[0].calls[0].provider='foreign:value';},(v:any)=>{v.controls_sha256='0'.repeat(64);},
  (v:any)=>{v.rows[0].cases[0].input_changed=true;},(v:any)=>{v.rows[0].cases[0].getter_reads=1;}
 ];
 for(const mutate of mutations){const changed=structuredClone(observation);mutate(changed);assert.throws(()=>checkCrossGeneratorOwnedValueObservations(n.c,changed),/native observation mismatch/);}
 let reads=0;const active={};Object.defineProperty(active,'rows',{enumerable:true,get(){reads++;return [];}});assert.throws(()=>checkCrossGeneratorOwnedValueObservations(n.c,active));assert.equal(reads,0);
 fs.writeFileSync(n.input,JSON.stringify({controls_sha256:n.c.controls_sha256,rows:[]}));assert.throws(()=>n.observe(),/OWNED_PROBE_EMPTY/);
 t.diagnostic(JSON.stringify({observation_mutants:mutations.length,active_reads:reads}));
});

function mixed(f:Fixture){
 const featureFile=path.join(f.source,'specs/alpha/feature.json'),feature=JSON.parse(fs.readFileSync(featureFile,'utf8'));
 const add=(id:string,kind:string,body:any)=>{feature.nodes.push(id);fs.writeFileSync(path.join(f.source,'specs/alpha/nodes/'+id+'.json'),JSON.stringify({schema_version:'domainspec.node/v1',feature_id:'alpha',node_id:id,kind,body}));};
 const named=(id:string)=>({kind:'named',selector:'alpha:'+id}),wrap=(kind:string,element:any)=>({kind,element});
 add('status','Enum',{description:'Status',values:['Open','Closed'],typed_contract:{schema_version:'domainspec.typed-sum/v1',ontology_node:'TEST-STATUS',variants:['Open','Closed'].map(name=>({name,payload:null,ontology_variant:'TEST-STATUS#'+name}))}});
 const variants=[{name:'None',payload:null,ontology_variant:'TEST-AMOUNT-CHOICE#None'},{name:'Amount',payload:named('money'),ontology_variant:'TEST-AMOUNT-CHOICE#Amount'}];
 add('amount-choice','Enum',{description:'Amount choice',values:variants.map(v=>v.name),typed_contract:{schema_version:'domainspec.typed-sum/v1',ontology_node:'TEST-AMOUNT-CHOICE',variants}});
 const fields:any[]=[['credit',named('money')],['credit_again',named('money')],['inline',{kind:'sum',variants}],['list',wrap('list',named('money'))],['named',named('amount-choice')],['optional',wrap('optional',named('money'))],['person',named('customer')],['set',wrap('set',named('money'))],['status',named('status')],['status_again',named('status')],['status_list',wrap('list',named('status'))]];
 add('money-box','Value Object',{description:'Owned values across collection and sum boundaries',invariant_refs:['alpha:nonempty'],fields:fields.map(([name])=>name),typed_contract:{schema_version:'domainspec.typed-record/v1',ontology_node:'TEST-MONEY-BOX',properties:fields.map(([name,type])=>({name,type,ontology_property:'TEST-MONEY-BOX#'+name,identity:false,cardinality:type.kind==='optional'?'optional':type.kind==='list'?'many':type.kind==='set'?'many-unique':'one',meaning:name}))}});
 f.selection.factories.push({selector:'alpha:money-box',base_validators:[{rule:'alpha:nonempty',arguments:[{parameter:'value',path:['person','id']}]}],extensions:[]} as any);
 fs.writeFileSync(featureFile,JSON.stringify(feature));
}
test('owned provider calls preserve repeated fields, Enum aliases, collections, sums and embedded Entity identity',t=>{
 const f=recordWitnessFixture(t);mixed(f);const n=native(f),{observation,result}=checked(n);
 assert.equal(result.tested_factory_count,2);assert.deepEqual(result.remaining,[]);
 const row=n.c.rows.find(r=>r.selector==='alpha:money-box')!;assert.equal(row.state,'ready');if(row.state!=='ready')throw Error('unavailable');
 assert.equal(row.protocol.length,11);assert.ok(row.ownership_coverage.every(c=>c.modes.length===4));
 const actual=observation.rows.find((r:any)=>r.selector===row.selector);
 assert.ok(actual.cases.some((c:any)=>c.calls.some((call:any)=>call.provider==='alpha:status'&&call.input_paths.length>=2)));
 assert.ok(actual.cases.some((c:any)=>c.calls.some((call:any)=>call.method==='key'&&call.provider==='alpha:customer')));
 assert.ok(actual.cases.some((c:any)=>c.calls.some((call:any)=>call.provider==='alpha:amount-choice')));
 const relative=n.paths.find(p=>p.endsWith('/money-box.ts'))!,file=path.join(n.source,relative),original=fs.readFileSync(file,'utf8');
 const mutants=[
  ['duplicate-key',(s:string)=>s.replaceAll('provider.key(value)','(provider.key(value),provider.key(value))')],
  ['wrong-equal-field-identity',(s:string)=>s.replace('field0Value.key(fields["credit"])','field0Value.key(fields["credit_again"])')]
 ] as const;
 for(const [name,mutate]of mutants){
  const changed=mutate(original);assert.notEqual(changed,original,name);fs.writeFileSync(file,changed);n.compile();
  const observed=n.observe();assert.throws(()=>checkCrossGeneratorOwnedValueObservations(n.c,observed),/native observation mismatch/,name);
  if(name==='duplicate-key')assert.deepEqual(observed.rows.map((r:any)=>r.cases.map(({calls,...c}:any)=>c)),observation.rows.map((r:any)=>r.cases.map(({calls,...c}:any)=>c)));
 }
 fs.writeFileSync(file,original);n.compile();checked(n);
 t.diagnostic(JSON.stringify({...result,owned_occurrences:row.protocol.length,extra_compiling_mutants:mutants.length}));
});
test('unavailable and capacity-exhausted owned families retain the whole denominator without native probes',t=>{
 const unavailable=controls(recordWitnessFixture(t,true)).c;
 assert.equal(unavailable.rows.find(r=>r.selector==='alpha:customer')!.state,'not_evaluable');
 assert.deepEqual(crossGeneratorOwnedValueProbe(unavailable).rows,[]);
 assert.throws(()=>checkCrossGeneratorOwnedValueObservations(unavailable,{controls_sha256:unavailable.controls_sha256,rows:[]}),/no executable/);
 const f=recordWitnessFixture(t),file=path.join(f.source,'specs/alpha/nodes/customer.json'),node=JSON.parse(fs.readFileSync(file,'utf8'));
 for(let i=0;i<48;i++){const name='owned_'+i;node.body.fields.push(name);node.body.typed_contract.properties.push({name,type:{kind:'named',selector:'alpha:money'},ontology_property:'TEST-CUSTOMER#'+name,identity:false,cardinality:'one',meaning:name});}
 fs.writeFileSync(file,JSON.stringify(node));
 f.selection.factories.find((x:import('../../src/generation/configured-factories.ts').FactoryBinding)=>x.selector==='alpha:customer')!.base_validators=[{rule:'alpha:nonempty',arguments:[{parameter:'value',field:'id'}]}] as any;
 const c=controls(f).c,row=c.rows.find(r=>r.selector==='alpha:customer')!;
 assert.equal(row.state,'not_evaluable');if(row.state!=='not_evaluable')throw Error('unexpected');
 assert.match(row.reason,/capacity/);assert.equal('cases'in row,false);assert.deepEqual(crossGeneratorOwnedValueProbe(c).rows,[]);
 t.diagnostic(JSON.stringify({whole_family_unavailable:true,capacity_reason:row.reason}));
});

import {nativeToolchainImage, NATIVE_TEST_IMAGE_ID} from '../helpers/native-toolchain-image.ts';
