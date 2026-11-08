import assert from 'node:assert/strict';
import test from 'node:test';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {spawnSync} from 'node:child_process';
import {repositoryToolchain} from '../helpers/local-toolchain.ts';
import {compileDeclarativeFunction,DECLARATIVE_FUNCTION_INPUTS_PROFILE as V2} from '../../src/typed-backend/declarative-function.js';
import {renderRustComposition} from '../../src/generation/rust-composition.js';
import {compileProjectComposition} from '../../src/input/project-composition.js';
import {compileProject} from '../../src/compilation/certificate.js';
import {compileCompositionBoundary,COMPOSITION_BOUNDARY_VERSION,COMPOSITION_BOUNDARY_CONTRACT_SHA256} from '../../src/input/composition-boundary.js';
import {planProjectBuild,planCompiledProjectBuild} from '../../src/generation/project-build.js';
import {sha256,canonicalJson} from '../../src/input/source-manifest.js';
import {COMPOSITION_ONTOLOGY_SCHEMA} from '../../src/input/composition-ontology.js';
const p=(...path:string[]):any=>({op:'path',path}),lit=(value:any):any=>({op:'literal',value}),call=(name:string,...args:any[]):any=>({op:'call',name,args});
const legacy:any={"schema_version":"domainspec.declarative-function/v1","records":{"Input":{"value":"String"},"Output":{"value":"String"}},"roots":{"input":"Input"},"calculations":{},"nodes":[{"id":"Emit","kind":"Mapping","ontology":"TEST-EMIT","meaning":"Copy the value.","input":{"name":"value","type":"String"},"target":"Output","fields":{"value":{"op":"path","path":["value"]}}}],"assertions":[],"results":[{"condition":{"op":"literal","value":true},"value":{"op":"call","name":"Emit","args":[{"op":"path","path":["input","value"]}]}}],"output":"Output"};
function fixture():any{return {
 schema_version:V2,records:{Input:{id:'String',total:'String',fee:'String',note:'String?'},Output:{id:'String',total:'String',again:'String',fee:'String',note:'String'}},
 roots:{input:'Input'},calculations:{},
 nodes:[{id:'Summary',kind:'Mapping',ontology:'TEST-SUMMARY',meaning:'Project the order and explicitly supplied amounts.',inputs:[{name:'order',type:'Input'},{name:'total',type:'UInt64'},{name:'fee',type:'UInt64'},{name:'note',type:'String?'}],target:'Output',
 fields:{id:p('order','id'),total:call('text',p('total')),again:call('text',p('total')),fee:call('text',p('fee')),note:call('coalesce',p('note'),lit('none'))}}],
 assertions:[],results:[{condition:lit(true),value:call('Summary',p('input'),call('uint64',p('input','total')),call('uint64',p('input','fee')),p('input','note'))}],output:'Output'
};}
const input={id:'order-1',total:'18446744073709551615',fee:'9007199254740993',note:null};
const expected={id:'order-1',total:input.total,again:input.total,fee:input.fee,note:'none'};
const load=async(c:any)=>import('data:text/javascript;base64,'+Buffer.from(compileDeclarativeFunction(c).source).toString('base64'));
function composition(){
 const contract=fixture();
 const schemas={Input:{id:{type:'string'},total:{type:'string'},fee:{type:'string'},note:{type:'string',nullable:true}},Output:Object.fromEntries(Object.keys(contract.records.Output).map(k=>[k,{type:'string'}]))};
 const model:any={schemas,integrations:{},flows:{},endpoint:{id:'Endpoint',result:'Result',target:'node-http',runtime:'node>=26.8.1',method:'POST',path:'/summary',input:'Input',output:'Output',authEnv:'TOKEN',maxBytes:2048,timeout:1000,statuses:{ok:200},errors:{},errorStatus:422}};
 const source_text=JSON.stringify(contract,null,2)+'\n',source={path:'contract.json',sha256:sha256(source_text)},location={...source,line:1};
 const nodes=['Input','Output','Summary','Endpoint','Result'].map(name=>({name,id:'TEST-'+name.toUpperCase(),source:location,meaning:{text:name==='Summary'?contract.nodes[0].meaning:name},
 ...(name==='Input'||name==='Output'?{record_type:contract.records[name],constraints:(schemas as any)[name]}:{}),...(name==='Summary'?{typed_contract:contract.nodes[0]}:{}),...(name==='Endpoint'?{binding:model.endpoint}:{}),...(name==='Result'?{assertions:[],cases:contract.results}:{})}));
 const refs=[['Summary','Output','maps-to'],['Summary','Input','maps-from'],['Endpoint','Result','exposes'],['Endpoint','Input','input'],['Endpoint','Output','output'],['Result','Output','returns'],['Result','Summary','calls'],['Result','Input','depends-on']];
 const references=refs.map(([from,to,role])=>({source:'TEST-'+from!.toUpperCase(),target:'TEST-'+to!.toUpperCase(),role,evidence:location}));
 return {schema_version:'domainspec.project-composition/v1',id:'summary',source_text,contract,core_bindings:{},model,bindings:[],ontology:{schema_version:COMPOSITION_ONTOLOGY_SCHEMA,source_format:'domainspec-json',source,nodes,references,composition_trace:compileDeclarativeFunction(contract).trace,status:'generated-scaffold',authority_effect:'none',ontology_admitted:false}};
}
test('v1 single-input source, trace and Rust artifacts remain byte-identical',()=>{
 const c=compileDeclarativeFunction(legacy);
 assert.equal(sha256(c.source),'d4eda3ea09d0c026927b16fa6b31b446b31db9586fe93e1a0ee9fde8e87ff405');
 assert.equal(sha256(canonicalJson(c.trace)),'b1b6719041ccaf8bceb00fe29df42c6e3cb1e40a48933ea230812f5e84c14051');
 assert.equal(sha256(canonicalJson(renderRustComposition(legacy,{}))),'37ba83ce4a4d6106214ff4dd6e1e80c006ca9669ca1cdba9f7d2bbf66fa3b171');
 const v1=structuredClone(legacy);v1.nodes[0].inputs=[v1.nodes[0].input];delete v1.nodes[0].input;assert.throws(()=>compileDeclarativeFunction(v1),/contract keys/);
});
test('v2 Mapping receives computed values explicitly and preserves exact amounts and nullable defaults',async()=>{
 const c=fixture(),compiled=compileDeclarativeFunction(c),api=await load(c),events:any[]=[];let calculations=0;
 assert.deepEqual(api.execute({input},{evaluateCalculation(){calculations++;throw Error('hidden Calculation');}},(e:any)=>events.push(e)),expected);
 assert.equal(calculations,0);assert.equal(events.filter(e=>e.kind==='node-start'&&e.declaration==='Summary').length,1);
 assert.deepEqual(api.execute({input:{...input,note:'kept'}},{}),{...expected,note:'kept'});
 assert.deepEqual(compiled,compileDeclarativeFunction(structuredClone(c)));
 const trace:any=compiled.trace;assert.deepEqual(trace.nodes[0].inputs,c.nodes[0].inputs);assert.deepEqual(trace.nodes[0].dependencies,[]);
 assert.equal(trace.nodes[0].evaluation,'left-to-right-once-per-argument-per-call');
 assert.equal(compiled.source.includes('api.evaluateCalculation('),false);assert.equal(input.total,expected.total);
});
test('v2 rejects missing, extra, shadowed, sparse, accessor and wrongly typed Mapping arguments',()=>{
 const mutations=[
  (c:any)=>delete c.nodes[0].inputs,
  (c:any)=>c.nodes[0].input={name:'old',type:'Input'},
  (c:any)=>c.nodes[0].inputs.push(c.nodes[0].inputs[0]),
  (c:any)=>c.nodes[0].inputs[0].name='input',
  (c:any)=>c.nodes[0].inputs[0].name='Summary',
  (c:any)=>c.nodes[0].inputs[0].name='constructor',
  (c:any)=>c.nodes[0].inputs[0].type='Missing',
  (c:any)=>c.nodes[0].inputs[1].default=0,
  (c:any)=>delete c.nodes[0].inputs[1],
  (c:any)=>c.nodes[0].inputs.extra=true,
  (c:any)=>c.results[0].value.args.pop(),
  (c:any)=>c.results[0].value.args.push(lit(null)),
  (c:any)=>c.results[0].value.args[1]=lit('wrong'),
  (c:any)=>c.results[0].value.args[1]=lit(null),
  (c:any)=>c.results[0].value=p('Summary'),
  (c:any)=>c.nodes[0].fields.note=p('note','value'),
  (c:any)=>delete c.nodes[0].fields.id,
  (c:any)=>c.nodes[0].fields.unknown=lit('no'),
  (c:any)=>c.schema_version='domainspec.declarative-function/v999'
 ];
 for(const change of mutations){const c=fixture();change(c);assert.throws(()=>compileDeclarativeFunction(c),/DS_DECLARATIVE/);}
 let gets=0;const c=fixture();Object.defineProperty(c.nodes[0].inputs,'1',{get(){gets++;return {name:'total',type:'UInt64'};},enumerable:true});
 assert.throws(()=>compileDeclarativeFunction(c),/dense mapping inputs/);assert.equal(gets,0);
});
test('explicit Calculation arguments evaluate once in order, while repeated call occurrences remain distinct',async()=>{
 const c=fixture();c.calculations={Price:['amount'],Fee:['amount']};
 c.results[0].value.args[1]=call('Price',call('uint64',p('input','total')));
 c.results[0].value.args[2]=call('Fee',call('uint64',p('input','fee')));
 const order:string[]=[],api=await load(c),bindings={evaluateCalculation(name:string,args:any){order.push(name);return args.amount;}};
 assert.deepEqual(api.execute({input},bindings),expected);assert.deepEqual(order,['Price','Fee'],'two uses of total do not repeat Price');
 c.nodes.push({id:'Twice',kind:'Mapping',ontology:'TEST-TWICE',meaning:'Two explicit call occurrences.',inputs:[],target:'Output',fields:{id:lit('twice'),total:call('text',call('Price',call('uint64',p('input','total')))),again:call('text',call('Price',call('uint64',p('input','total')))),fee:lit('0'),note:lit('none')}});
 c.results[0].value=p('Twice');order.length=0;(await load(c)).execute({input},bindings);assert.deepEqual(order,['Price','Price']);
 const trace:any=compileDeclarativeFunction(c).trace;assert.deepEqual(trace.nodes.find((n:any)=>n.id==='Twice').dependencies,['Price']);assert.equal(trace.nodes.find((n:any)=>n.id==='Twice').evaluation,'invocation-local-memoized');
 const failing=fixture();failing.calculations={Price:['amount'],Fee:['amount']};failing.results[0].value.args=[p('input'),call('Price',call('uint64',p('input','total'))),call('Fee',call('uint64',p('input','fee'))),lit(null)];
 let later=0;assert.throws((await load(failing)).execute.bind(null,{input},{evaluateCalculation(name:string){if(name==='Price')throw Error('PRICE_FAILED');later++;return 1n;}}),/PRICE_FAILED/);assert.equal(later,0);
});
test('guard availability checks actual arguments and does not mistake formal inputs for guarded roots',async()=>{
 const c=fixture();c.roots.remote='Input';c.bindings=[{name:'remote',condition:lit(false)}];c.results[0].value.args[0]=p('remote');
 assert.throws(()=>compileDeclarativeFunction(c),/unguarded binding output/);
 c.results[0].value.args[0]=p('input');assert.deepEqual((await load(c)).execute({input},{}),expected);
 c.nodes[0].inputs[0].name='remote';assert.throws(()=>compileDeclarativeFunction(c),/shadowed input/);
});
test('compiling Node mutations expose argument swaps, lost defaults and dropped reuse',async()=>{
 const source=compileDeclarativeFunction(fixture()).source;
 const mutants=[
  source.replace('n_Summary = (v_order,v_total,v_fee,v_note)','n_Summary = (v_order,v_fee,v_total,v_note)'),
  source.replace('"again": v_total.toString()','"again": v_fee.toString()'),
  source.replace('v_note ?? "none"','v_note ?? "changed"')
 ];
 for(const mutant of mutants){assert.notEqual(mutant,source);const api=await import('data:text/javascript;base64,'+Buffer.from(mutant).toString('base64'));assert.notDeepEqual(api.execute({input},{}),expected);}
});
test('direct JSON project composition keeps typed inputs separate from canonical domain edges',async t=>{
 const s=composition(),compiled=compileProjectComposition(s,[]);const api=await import('data:text/javascript;base64,'+Buffer.from(compiled.artifacts['behavior.mjs']!).toString('base64'));
 assert.deepEqual(api.execute({input},{}),expected);assert.equal(compiled.artifacts['source.json'],s.source_text);
 const bad=structuredClone(s);bad.ontology.references=bad.ontology.references.filter(r=>r.role!=='maps-from');assert.throws(()=>compileProjectComposition(bad,[]),/dependency set/);
 const stale=structuredClone(s);stale.ontology.composition_trace={};assert.throws(()=>compileProjectComposition(stale,[]),/composition trace/);
 const repeated=composition();repeated.contract.nodes[0].inputs.push({name:'backup',type:'Input?'});repeated.contract.results[0].value.args.push(p('input'));
 repeated.source_text=JSON.stringify(repeated.contract,null,2)+'\n';repeated.ontology.source.sha256=sha256(repeated.source_text);for(const n of repeated.ontology.nodes)n.source.sha256=repeated.ontology.source.sha256;for(const r of repeated.ontology.references)r.evidence.sha256=repeated.ontology.source.sha256;
 repeated.ontology.composition_trace=compileDeclarativeFunction(repeated.contract).trace;assert.doesNotThrow(()=>compileProjectComposition(repeated,[]),'two formals with one record type retain separate typed slots and one maps-from relation');
 const root=fs.mkdtempSync(path.join(os.tmpdir(),'ds-mapping-project-'));t.after(()=>fs.rmSync(root,{recursive:true,force:true}));
 const source=path.join(root,'source');fs.cpSync(path.resolve(import.meta.dirname,'../../fixtures/input-roots/canonical-project'),source,{recursive:true});
 const write=(name:string,v:any)=>{const f=path.join(source,name);fs.mkdirSync(path.dirname(f),{recursive:true});fs.writeFileSync(f,JSON.stringify(v));};
 const project=JSON.parse(fs.readFileSync(path.join(source,'project.json'),'utf8'));write('project.json',{...project,schema_version:'domainspec.project/v2',compositions:['summary']});write('compositions/summary.json',s);
 const result=compileProject(source),graph=result.graph,profile='domainspec.typescript-exact-uint64/v1';
 assert.deepEqual(planProjectBuild(source,'typescript',profile),planCompiledProjectBuild(graph,'typescript',profile));
 const contract=fs.readFileSync(path.resolve(import.meta.dirname,'../../../../development/reconciliation-v1/contracts/composition-boundary.json'),'utf8');
 const boundary=compileCompositionBoundary(graph,{schema_version:COMPOSITION_BOUNDARY_VERSION,contract_sha256:COMPOSITION_BOUNDARY_CONTRACT_SHA256,graph_sha256:result.certificate.graph_sha256},contract);
 assert.equal(boundary.domain_graph.relationships.some((r:any)=>['maps-from','maps-to','calls'].includes(r.relationship)),false);
 assert.ok(boundary.composition_graphs[0]!.references.some((r:any)=>r.role==='maps-from'));
 assert.equal(boundary.bridges.length,0,'formal inputs do not invent bridges');
 fs.renameSync(source,path.join(root,'relocated'));assert.ok(planCompiledProjectBuild(graph,'typescript',profile).artifacts.length>0);
});
test('native Rust consumes all Mapping arguments in order and preserves the Node result',t=>{
 const root=fs.mkdtempSync(path.join(os.tmpdir(),'ds-mapping-rust-'));t.after(()=>fs.rmSync(root,{recursive:true,force:true}));
 const c=fixture(),artifacts=renderRustComposition(compileDeclarativeFunction(c).contract,{});
 for(const [name,content]of Object.entries(artifacts)){const f=path.join(root,name);fs.mkdirSync(path.dirname(f),{recursive:true});fs.writeFileSync(f,content);}
 for(const [name,content]of Object.entries({'function.json':{},'ontology.json':{},'bindings.json':[],'composition.json':c}))fs.writeFileSync(path.join(root,name),JSON.stringify(content));
 fs.writeFileSync(path.join(root,'source.alch'),'direct JSON fixture');
 fs.appendFileSync(path.join(root,'src/lib.rs'),'\n#[test]\nfn explicit_mapping_inputs(){let mut context=Context::new(json!('+JSON.stringify(input)+'),false);assert_eq!(context.execute().unwrap(),json!('+JSON.stringify(expected)+'));}\n');
 const r=spawnSync(repositoryToolchain(),['cargo','test','--offline','--lib','--quiet'],{cwd:root,encoding:'utf8',timeout:240000,env:{...process.env,CARGO_TARGET_DIR:process.env.CARGO_TARGET_DIR??path.join(root,'target')}});
 assert.equal(r.status,0,String(r.error??'')+'\n'+r.stdout+'\n'+r.stderr);
 const library=path.join(root,'src/lib.rs'),original=fs.readFileSync(library,'utf8'),mutant=original.replaceAll('v_total.clone()','v_fee.clone()');assert.notEqual(mutant,original);fs.writeFileSync(library,mutant);
 const negative=spawnSync(repositoryToolchain(),['cargo','test','--offline','--lib','--quiet'],{cwd:root,encoding:'utf8',timeout:240000,env:{...process.env,CARGO_TARGET_DIR:process.env.CARGO_TARGET_DIR??path.join(root,'target')}});
 assert.equal(negative.status,101);assert.match(negative.stdout,/explicit_mapping_inputs --- FAILED/,'mutant compiles but fails the independent native result assertion');assert.doesNotMatch(negative.stderr,/error\[E[0-9]+\]/);
});
