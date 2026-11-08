import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {execFileSync} from 'node:child_process';
import test from 'node:test';
import {recordWitnessFixture} from '../helpers/record-witness-project.ts';
import {loadCompiledProjectGraph} from '../../src/input/project-model.ts';
import {planCompiledReconciledProject} from '../../src/generation/reconciled-project.ts';
import {createFactoryControls} from '../../src/verification/reconciled-factory-controls.ts';
import {createCrossGeneratorBoundary} from '../../src/verification/reconciled-cross-generator-boundary.ts';
import {createCrossGeneratorFactoryControls, crossGeneratorFactoryProbe, checkCrossGeneratorFactoryObservations} from '../../src/verification/reconciled-cross-generator-factory.ts';
import {CROSS_GENERATOR_FACTORY_RUNNER} from '../../src/verification/reconciled-cross-generator-factory-runner.ts';
import type {FactoryBinding} from '../../src/generation/configured-factories.ts';
const project=path.resolve(import.meta.dirname,'../../../..'),base=path.join(project,'development/reconciliation-v1/profile-compiler-reconciliation');
const definition=fs.readFileSync(path.join(base,'cross-generator-factory-contract.json'),'utf8'),boundaryDefinition=fs.readFileSync(path.join(base,'cross-generator-verification-contract.json'),'utf8');
type Fixture=ReturnType<typeof recordWitnessFixture>;
function controls(f:Fixture){
 const graph=loadCompiledProjectGraph(f.source),plan=planCompiledReconciledProject(graph,f.selection),boundary=createCrossGeneratorBoundary(graph,plan,boundaryDefinition);
 return {graph,plan,boundary,c:createCrossGeneratorFactoryControls(graph,plan,boundary,definition)};
}
function native(f:Fixture){
 const {graph,plan,boundary,c}=controls(f),probe=crossGeneratorFactoryProbe(c);
 const source=path.join(f.root,'generated-source'),output=path.join(f.root,'native'),input=path.join(f.root,'probe.json'),runner=path.join(f.root,'runner.mjs');
 fs.mkdirSync(source);fs.mkdirSync(output);fs.writeFileSync(path.join(f.root,'package.json'),'{"type":"commonjs"}');
 const paths=[...new Set(probe.rows.flatMap(r=>r.modules.map(m=>m.relative_path)))].sort();
 for(const p of paths){const a=plan.resolved.artifacts.find(a=>a.relative_path===p)!;const file=path.join(source,p);fs.mkdirSync(path.dirname(file),{recursive:true});fs.writeFileSync(file,a.content);}
 const config=path.join(f.root,'compiler.json');fs.writeFileSync(config,JSON.stringify({compilerOptions:{strict:true,skipLibCheck:true,target:'ES2022',module:'CommonJS',rootDir:source,outDir:output,types:[],noEmitOnError:true},files:paths.map(p=>path.join(source,p))}));
 fs.writeFileSync(input,JSON.stringify(probe));fs.writeFileSync(runner,CROSS_GENERATOR_FACTORY_RUNNER);
 const image=nativeToolchainImage();assert.equal(image, NATIVE_TEST_IMAGE_ID);
 const docker=['run','--rm','--pull','never','--network','none','--read-only','--cap-drop','ALL','--security-opt','no-new-privileges','--user',process.getuid!()+':'+process.getgid!(),'--mount','type=bind,source='+f.root+',target='+f.root,'--workdir',f.root,image];
 const command=(args:string[])=>{try{return execFileSync('docker',[...docker,...args],{encoding:'utf8',stdio:'pipe',timeout:60000,maxBuffer:16777216});}catch(e:any){throw Error(String(e.stdout)+String(e.stderr));}};
 const compile=()=>command(['tsc','--project',config,'--pretty','false']);
 const observe=()=>JSON.parse(command(['node','--permission','--allow-fs-read='+f.root,'--disable-proto=throw',runner,input,output]));
 compile();return {graph,plan,boundary,c,probe,source,output,paths,input,runner,compile,observe};
}


function configureExtensions(f:Fixture,ids:string[]){
 const original=JSON.parse(fs.readFileSync(path.join(f.source,'specs/alpha/nodes/budget.json'),'utf8'));
 const featureFile=path.join(f.source,'specs/alpha/feature.json'),feature=JSON.parse(fs.readFileSync(featureFile,'utf8'));
 for(const id of ids){const node=structuredClone(original);node.node_id=id;node.body.description=id;node.body.typed_contract.ontology_rule='TEST-'+id.toUpperCase();node.body.typed_contract.expression={op:'rule_ref',selector:'alpha:budget',arguments:node.body.typed_contract.parameters.map((p:any)=>({parameter:p.name,value:{op:'path',root:p.name,properties:[]}}))};fs.writeFileSync(path.join(f.source,'specs/alpha/nodes/'+id+'.json'),JSON.stringify(node));feature.nodes.push(id);}
 fs.writeFileSync(featureFile,JSON.stringify(feature));
 const money=f.selection.factories.find((x:FactoryBinding)=>x.selector==='alpha:money')! as any;
 money.extensions=ids.map(id=>({id,validators:[{rule:'alpha:'+id,arguments:structuredClone(money.base_validators[0].arguments)}]}));
}

test('extension occurrences, order and structured fields survive actual factory calls',t=>{
 const f=recordWitnessFixture(t),file=path.join(f.source,'specs/alpha/nodes/money.json'),raw=JSON.parse(fs.readFileSync(file,'utf8'));
 const fields=[
  ['note',{kind:'optional',element:{kind:'scalar',name:'String'}}],
  ['tags',{kind:'set',element:{kind:'scalar',name:'String'}}],
  ['choice',{kind:'sum',variants:[{name:'None',payload:null,ontology_variant:'TEST-MONEY-CHOICE#None'},{name:'Amount',payload:{kind:'scalar',name:'UInt64'},ontology_variant:'TEST-MONEY-CHOICE#Amount'}]}],
 ] as const;
 for(const [name,type] of fields){raw.body.fields.push(name);raw.body.typed_contract.properties.push({name,type,ontology_property:'TEST-MONEY#'+name,identity:false,cardinality:type.kind==='optional'?'optional':type.kind==='set'?'many-unique':'one',meaning:name});}
 fs.writeFileSync(file,JSON.stringify(raw));
 const customerFile=path.join(f.source,'specs/alpha/nodes/customer-valid.json'),customer=JSON.parse(fs.readFileSync(customerFile,'utf8'));
 // Repeated nested calls remain separate occurrences even when their arguments match.
 customer.body.typed_contract.expression.terms.splice(1,0,structuredClone(customer.body.typed_contract.expression.terms[0]));fs.writeFileSync(customerFile,JSON.stringify(customer));
 configureExtensions(f,['first','second']);
 const n=native(f),actual=n.observe(),result=checkCrossGeneratorFactoryObservations(n.c,actual);
 assert.equal(result.tested_factory_count,2);assert.deepEqual(result.remaining,[]);
 const source=n.c.rows.find(r=>r.selector==='alpha:money')!;if(source.state!=='ready')throw Error(source.reason);
 const chains=new Set(source.cases.map(c=>JSON.parse(c.values[0]!).chain.join(',')));
 assert.ok(chains.has('first,second'));assert.ok(chains.has('second,first'));
 assert.equal(source.validator_outcomes.length,3);assert.ok(source.validator_outcomes.every(v=>v.outcomes.includes(true)));
 const target=actual.rows.find((r:any)=>r.selector==='alpha:money');
 assert.ok(target.cases.some((c:any)=>c.calls.length===5&&c.calls[2].selector==='alpha:budget'&&c.calls[2].parent===1&&c.calls[4].selector==='alpha:budget'&&c.calls[4].parent===3));
 assert.ok(actual.rows.find((r:any)=>r.selector==='alpha:customer').cases.some((c:any)=>c.calls.length===5&&c.calls[3].parent===2&&c.calls[4].parent===2));
 t.diagnostic(JSON.stringify({structured_extensions:true,...result}));
});

test('strict-compiling call and argument mutants cannot hide behind unchanged factory-reported traces',t=>{
 const f=recordWitnessFixture(t),n=native(f),baseline=n.observe();checkCrossGeneratorFactoryObservations(n.c,baseline);
 const module=(name:string)=>n.paths.find(p=>p.endsWith('/'+name+'.ts'))!;
 const money=module('money'),customer=module('customer'),budget=module('budget');
 const originals=new Map([money,customer,budget].map(p=>[p,fs.readFileSync(path.join(n.source,p),'utf8')]));
 const mutations:[string,string,(s:string)=>string,boolean][]=[
  ['omitted-equivalent-predicate',money,s=>s.replace('validator0({["amount"]:fields["amount"],["approved"]:fields["approved"]})','(fields["amount"]>0n && fields["approved"])'),true],
  ['duplicate',customer,s=>s.replace('validator.validate(fields) === true','(validator.validate(fields),validator.validate(fields)) === true'),true],
  ['same-result-wrong-argument',customer,s=>s.replace('["amount"]:fields["credit"].fields["amount"]','["amount"]:2n'),true],
  ['same-result-eager-call',customer,s=>s.replace('    for (const validator of validators) {','    validators[0]!.validate(fields);\n    for (const validator of validators) {'),true],
  ['wrong-argument',money,s=>s.replace('["approved"]:fields["approved"]','["approved"]:true'),false],
  ['changed-predicate',budget,s=>s.replace('(0n < p0)','(1n < p0)'),false],
 ];
 let unchangedReports=0;
 for(const [name,p,mutate,unchanged] of mutations){
  for(const [file,value]of originals)fs.writeFileSync(path.join(n.source,file),value);
  const value=mutate(originals.get(p)!);assert.notEqual(value,originals.get(p),name);fs.writeFileSync(path.join(n.source,p),value);n.compile();
  const actual=n.observe();assert.throws(()=>checkCrossGeneratorFactoryObservations(n.c,actual),/native observation mismatch/,name);
  if(unchanged){assert.deepEqual(actual.rows.map((r:any)=>r.cases.map(({calls,...c}:any)=>c)),baseline.rows.map((r:any)=>r.cases.map(({calls,...c}:any)=>c)),name+' retains old factory-report observation');unchangedReports++;}
 }
 for(const [file,value]of originals)fs.writeFileSync(path.join(n.source,file),value);n.compile();checkCrossGeneratorFactoryObservations(n.c,n.observe());
 t.diagnostic(JSON.stringify({strict_compiling_mutants:mutations.length,unchanged_factory_report_mutants:unchangedReports}));
});

test('native observations reject missing, reordered, duplicated, foreign and active evidence',t=>{
 const f=recordWitnessFixture(t),n=native(f),baseline=n.observe();checkCrossGeneratorFactoryObservations(n.c,baseline);
 const calls=(v:any)=>v.rows.find((r:any)=>r.selector==='alpha:customer').cases.find((c:any)=>c.calls.length===4).calls;
 const mutations=[
  (v:any)=>v.rows.pop(),(v:any)=>v.rows.reverse(),(v:any)=>v.rows.push(v.rows[0]),(v:any)=>v.rows[0].cases.pop(),
  (v:any)=>v.rows[0].cases.reverse(),(v:any)=>v.rows[0].cases.push(v.rows[0].cases[0]),
  (v:any)=>{v.controls_sha256='0'.repeat(64);},(v:any)=>{v.extra=true;},
  (v:any)=>calls(v).pop(),(v:any)=>calls(v).reverse(),(v:any)=>{calls(v)[3].parent=null;},
  (v:any)=>{calls(v)[0].input=['null'];},(v:any)=>{calls(v)[0].result=false;},
  (v:any)=>{calls(v)[0].arity=2;},(v:any)=>{v.rows[0].cases[0].getter_reads=1;},(v:any)=>{v.rows[0].cases[0].input_changed=true;},
 ];
 for(const mutate of mutations){const value=structuredClone(baseline);mutate(value);assert.throws(()=>checkCrossGeneratorFactoryObservations(n.c,value),/native observation mismatch/);}
 let reads=0;const active={};Object.defineProperty(active,'rows',{enumerable:true,get(){reads++;return baseline.rows;}});
 assert.throws(()=>checkCrossGeneratorFactoryObservations(n.c,active));assert.equal(reads,0);
 assert.throws(()=>checkCrossGeneratorFactoryObservations(structuredClone(n.c),baseline),/registered/);
 fs.writeFileSync(n.input,JSON.stringify({controls_sha256:n.c.controls_sha256,rows:[]}));assert.throws(()=>n.observe(),/FACTORY_PROBE_EMPTY/);
 t.diagnostic(JSON.stringify({observation_rejections:mutations.length,active_output_reads:reads,empty_probe_rejected:true}));
});

test('extension-capacity exhaustion never returns a checked prefix',t=>{
 const f=recordWitnessFixture(t);configureExtensions(f,Array.from({length:8},(_,i)=>'extension-'+i));
 const c=controls(f).c,row=c.rows.find(r=>r.selector==='alpha:money')!;
 assert.equal(row.state,'not_evaluable');if(row.state==='not_evaluable')assert.match(row.reason,/capacity/);
 assert.equal('cases' in row,false);assert.equal(crossGeneratorFactoryProbe(c).rows.some(r=>r.selector===row.selector),false);
});


test('a Rule reached from another caller cannot hide an unvisited protocol edge',t=>{
 const f=recordWitnessFixture(t),file=path.join(f.source,'specs/alpha/nodes/budget.json'),raw=JSON.parse(fs.readFileSync(file,'utf8'));
 raw.body.typed_contract.expression={op:'all',terms:[raw.body.typed_contract.expression,{op:'any',terms:[
  {op:'eq',left:{op:'literal',type:'Bool',value:true},right:{op:'literal',type:'Bool',value:true}},
  {op:'rule_ref',selector:'alpha:allowed',arguments:[{parameter:'value',value:{op:'literal',type:'String',value:'approved'}}]},
 ]}]};fs.writeFileSync(file,JSON.stringify(raw));
 const {c}=controls(f),row=c.rows.find(r=>r.selector==='alpha:customer')!;
 assert.equal(row.state,'not_evaluable','allowed is reached by customer-valid, never through budget');
 if(row.state==='not_evaluable')assert.match(row.reason,/unvisited.*edge/);
 assert.equal(c.coverage.some(e=>e.factory_selectors.includes('alpha:customer')),false);
 assert.equal(crossGeneratorFactoryProbe(c).rows.some(r=>r.selector==='alpha:customer'),false);
});


test('source factory protocols retain lifecycle cases, exact nested arguments and complete edge accounting',t=>{
 const f=recordWitnessFixture(t),{graph,plan,boundary,c}=controls(f);
 assert.equal(c.rows.length,2);
 for(const row of c.rows){
  if(row.state!=='ready')throw Error(row.reason);
  assert.equal(row.state,'ready');
  const old=createFactoryControls(graph.nodes.find(n=>n.selector===row.selector)!,graph,plan);
  if(old.state!=='ready')throw Error(old.reason);assert.equal(old.state,'ready');
  assert.deepEqual(row.cases.map(({expected,...input})=>({...input,expected:expected.outcome})),old.cases);
  assert.ok(row.cases.some(c=>c.expected.calls.length));
  assert.ok(row.protocol_edge_visits.every(e=>e.calls>0));
  assert.equal(row.protocol_edge_visits.reduce((n,e)=>n+e.calls,0),row.cases.reduce((n,c)=>n+c.expected.calls.length,0));
  for(const c of row.cases){const result=c.expected.outcome.kind==='value'?JSON.parse(c.expected.outcome.value):null;if(result?.failure_codes.includes('INVALID_FIELDS')||result?.failure_codes.includes('INVALID_PREVIOUS')||c.expected.outcome.kind==='error')assert.deepEqual(c.expected.calls,[]);}
 }
 const customer=c.rows.find(r=>r.selector==='alpha:customer')!;if(customer.state!=='ready')throw Error(customer.reason);
 assert.ok(customer.cases.some(c=>c.expected.calls.some(call=>call.parent!==null)));
 assert.deepEqual(customer.validator_outcomes.find(v=>v.occurrence==='base:1')!.outcomes,[true],'nested Money already enforces the same budget predicate');
 assert.deepEqual(c.coverage.map(e=>e.edge_sha256),boundary.edges.map(e=>e.edge_sha256));
 assert.ok(c.coverage.some(e=>e.status==='not_evaluable'),'owned-field imports are not claimed as Rule-call evidence');
 const probe=crossGeneratorFactoryProbe(c);assert.equal(JSON.stringify(probe).includes('"expected"'),false);
 assert.throws(()=>crossGeneratorFactoryProbe(structuredClone(c)),/registered/);
 assert.throws(()=>createCrossGeneratorFactoryControls(graph,plan,structuredClone(boundary),definition),/registered/);
 assert.throws(()=>createCrossGeneratorFactoryControls(graph,plan,boundary,definition+' '),/definition drift/);
 const foreign=controls(recordWitnessFixture(t,false,'other/domain'));assert.throws(()=>createCrossGeneratorFactoryControls(graph,plan,foreign.boundary,definition),/foreign boundary/);
});

test('native original factory calls match independent source traces in both module roots without counting helper construction',t=>{
 for(const moduleRoot of ['domain','application/domain']){
  const f=recordWitnessFixture(t,false,moduleRoot),n=native(f),observation=n.observe(),result=checkCrossGeneratorFactoryObservations(n.c,observation);
  assert.equal(result.tested_factory_count,2);assert.equal(result.tested_case_count,290);assert.equal(result.tested_call_count,311);
  assert.deepEqual(result.remaining,[]);assert.equal(result.public_cross_generator_behavior,'not_evaluable');
  const customer=observation.rows.find((r:any)=>r.selector==='alpha:customer');
  const accepted=customer.cases.find((c:any)=>c.outcome.kind==='value'&&JSON.parse(c.outcome.value).ok);
  assert.equal(accepted.calls.length,4,'one nonempty, one budget, customer-valid and nested allowed, not helper/copy calls');
  assert.equal(accepted.calls[3].parent,2);
  for(const c of customer.cases){assert.equal(c.getter_reads,0);assert.equal(c.input_changed,false);}
  t.diagnostic(JSON.stringify({module_root:moduleRoot,...result,native_modules:n.paths.length,controls_sha256:n.c.controls_sha256}));
 }
});

test('unavailable owned inputs and unvisited source Rules retain whole factory families',t=>{
 const impossible=controls(recordWitnessFixture(t,true));assert.ok(impossible.c.rows.every(r=>r.state==='not_evaluable'));
 assert.equal(crossGeneratorFactoryProbe(impossible.c).rows.length,0);
 assert.throws(()=>checkCrossGeneratorFactoryObservations(impossible.c,{controls_sha256:impossible.c.controls_sha256,rows:[]}),/no executable/);
 const f=recordWitnessFixture(t),file=path.join(f.source,'specs/alpha/nodes/customer-valid.json'),raw=JSON.parse(fs.readFileSync(file,'utf8'));
 raw.body.typed_contract.expression={op:'any',terms:[{op:'eq',left:{op:'literal',type:'Bool',value:true},right:{op:'literal',type:'Bool',value:true}},raw.body.typed_contract.expression]};fs.writeFileSync(file,JSON.stringify(raw));
 const c=controls(f).c,row=c.rows.find(r=>r.selector==='alpha:customer')!;assert.equal(row.state,'not_evaluable');if(row.state==='not_evaluable')assert.match(row.reason,/unvisited/);
 assert.equal(crossGeneratorFactoryProbe(c).rows.some(r=>r.selector==='alpha:customer'),false);
});

import {nativeToolchainImage, NATIVE_TEST_IMAGE_ID} from '../helpers/native-toolchain-image.ts';
