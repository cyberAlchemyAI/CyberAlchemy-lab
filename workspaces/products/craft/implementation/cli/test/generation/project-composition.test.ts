import assert from 'node:assert/strict';
import test from 'node:test';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {spawnSync} from 'node:child_process';
import {repositoryToolchain} from '../helpers/local-toolchain.ts';
import {renderRustComposition} from '../../src/generation/rust-composition.js';
import {compileDeclarativeFunction} from '../../src/typed-backend/declarative-function.js';
import {compileProjectComposition} from '../../src/input/project-composition.js';
import {compileProject,createCompiledProjectCertificate} from '../../src/compilation/certificate.js';
import {validateProjectRoot, loadProjectNode, selectCompiledProjectNode} from '../../src/input/project-model.js';
import {planInstantiation} from '../../src/generation/plan-instantiation.js';
import {validateSourceManifest,sha256} from '../../src/input/source-manifest.js';
import {planProjectBuild,planCompiledProjectBuild,publishProjectBuild,verifyProjectBuild} from '../../src/generation/project-build.js';
import {normalizeCompositionOntology, COMPOSITION_ONTOLOGY_SCHEMA} from '../../src/input/composition-ontology.js';
import {planProjectInstantiation} from '../../src/generation/project-instantiation.js';
import {createCheckedInterchange} from '../../src/assurance/checked-interchange.js';
const profile='domainspec.typescript-exact-uint64/v1';
test('generated Rust preserves Int literals across the full safe-integer range',t=>{
 const root=fs.mkdtempSync(path.join(os.tmpdir(),'ds-rust-int-'));
 t.after(()=>fs.rmSync(root,{recursive:true,force:true}));
 const values={aboveI32:2147483648,belowI32:-2147483649,maxSafe:Number.MAX_SAFE_INTEGER,minSafe:Number.MIN_SAFE_INTEGER};
 const s=fixture();
 s.contract.records.Output=Object.fromEntries(Object.keys(values).map(name=>[name,'Int']));
 s.contract.nodes[0].fields=Object.fromEntries(Object.entries(values).map(([name,value])=>[name,{op:'literal',value}]));
 const {contract}=compileDeclarativeFunction(s.contract);
 const artifacts=renderRustComposition(contract,{});
 for(const [name,content] of Object.entries(artifacts)){
  const file=path.join(root,name);fs.mkdirSync(path.dirname(file),{recursive:true});fs.writeFileSync(file,content);
 }
 for(const [name,content] of Object.entries({'function.json':{},'ontology.json':{},'bindings.json':[],'composition.json':contract}))fs.writeFileSync(path.join(root,name),JSON.stringify(content));
 fs.writeFileSync(path.join(root,'source.alch'),s.source_text);
 fs.appendFileSync(path.join(root,'src/lib.rs'),`\n#[test]\nfn safe_integer_literals_roundtrip(){let mut context=Context::new(json!({}),false);let expected:Value=serde_json::from_str(r#"${JSON.stringify(values)}"#).unwrap();assert_eq!(context.execute().unwrap(),expected);}\n`);
 const result=spawnSync(repositoryToolchain(),['cargo','test','--offline','--lib','--quiet'],{cwd:root,encoding:'utf8',timeout:240000,env:{...process.env,CARGO_TARGET_DIR:process.env.CARGO_TARGET_DIR??path.join(root,'target')}});
 assert.equal(result.status,0,`${result.error??''}\n${result.stdout}\n${result.stderr}`);
});
function fixture(){
 const contract:any={schema_version:'domainspec.declarative-function/v1',records:{Input:{value:'String'},Output:{value:'String'}},roots:{input:'Input'},calculations:{},nodes:[{id:'Emit',kind:'Mapping',ontology:'TEST-EMIT',meaning:'Copy the input value.',target:'Output',fields:{value:{op:'path',path:['input','value']}}}],assertions:[],results:[{condition:{op:'literal',value:true},value:{op:'path',path:['Emit']}}],output:'Output'};
 const model={schemas:{Input:{value:{type:'string'}},Output:{value:{type:'string'}}},integrations:{},flows:{},endpoint:{id:'Endpoint',result:'Result',target:'node-http',runtime:'node>=26.8.1',method:'POST',path:'/copy',input:'Input',output:'Output',authEnv:'TOKEN',maxBytes:1024,timeout:1000,statuses:{ok:200},errors:{},errorStatus:422}};
 const source_text='fixture source\n',source={path:'fixture.alch',sha256:sha256(source_text)},location={...source,line:1};
 const nodes=['Input','Output','Emit','Endpoint','Result'].map(name=>({name,id:'TEST-'+name.toUpperCase(),source:location,meaning:{text:name==='Emit'?'Copy the input value.':name},...(name==='Input'||name==='Output'?{record_type:contract.records[name],constraints:model.schemas[name]}:{}),...(name==='Emit'?{typed_contract:contract.nodes[0]}:{}),...(name==='Endpoint'?{binding:model.endpoint}:{}),...(name==='Result'?{assertions:[],cases:contract.results}:{})}));
 const references=[['Emit','Output','maps-to'],['Emit','Input','depends-on'],['Endpoint','Result','exposes'],['Endpoint','Input','input'],['Endpoint','Output','output'],['Result','Output','returns'],['Result','Emit','depends-on']].map(([from,to,role])=>({source:'TEST-'+from!.toUpperCase(),target:'TEST-'+to!.toUpperCase(),role,evidence:location}));
 const ontology={schema_version:'alchlang.derived-ontology/v1',source,nodes,references,composition_trace:compileDeclarativeFunction(contract).trace,status:'generated-scaffold',authority_effect:'none',ontology_admitted:false};
 return {schema_version:'domainspec.project-composition/v1',id:'copy',source_text,contract,core_bindings:{},model,bindings:[],ontology};
}
function project(t:any){const root=fs.mkdtempSync(path.join(os.tmpdir(),'ds-composition-'));t.after(()=>fs.rmSync(root,{recursive:true,force:true}));const source=path.join(root,'source');fs.cpSync(path.resolve(import.meta.dirname,'../../fixtures/input-roots/canonical-project'),source,{recursive:true});const p=JSON.parse(fs.readFileSync(path.join(source,'project.json'),'utf8'));fs.writeFileSync(path.join(source,'project.json'),JSON.stringify({...p,schema_version:'domainspec.project/v2',compositions:['copy']}));fs.mkdirSync(path.join(source,'compositions'));fs.writeFileSync(path.join(source,'compositions/copy.json'),JSON.stringify(fixture()));return {root,source};}
test('legacy and shared ontology inputs preserve behavior while keeping distinct provenance', async () => {
 const legacy=fixture(), shared:any=structuredClone(legacy);
 shared.ontology=normalizeCompositionOntology(shared.ontology);
 const direct:any=structuredClone(shared);
 direct.ontology.source_format='domainspec-json';
 direct.source_text=JSON.stringify(direct.contract,null,2)+'\n';
 const source={path:'contract.json',sha256:sha256(direct.source_text)};
 direct.ontology.source=source;
 for(const node of direct.ontology.nodes)node.source={...source,line:1};
 for(const ref of direct.ontology.references)ref.evidence={...source,line:1};
 const compiled=[legacy,shared,direct].map(s=>compileProjectComposition(s,[]));
 for(const c of compiled){
  assert.deepEqual(c.dependency_graph,compiled[0]!.dependency_graph);
  assert.equal(c.artifacts['behavior.mjs'],compiled[0]!.artifacts['behavior.mjs']);
  const api=await import('data:text/javascript;base64,'+Buffer.from(c.artifacts['behavior.mjs']!).toString('base64'));
  assert.deepEqual(api.execute({input:{value:'shared'}},{}),{value:'shared'});
 }
 assert.equal(JSON.parse(compiled[0]!.artifacts['ontology.json']!).schema_version,'alchlang.derived-ontology/v1');
 assert.equal(JSON.parse(compiled[1]!.artifacts['ontology.json']!).schema_version,COMPOSITION_ONTOLOGY_SCHEMA);
 assert.equal(compiled[2]!.artifacts['source.json'],direct.source_text);
 assert.equal(compiled[2]!.artifacts['source.alch'],undefined);
 for(const mutate of [
  (s:any)=>s.ontology.schema_version='unknown',
  (s:any)=>s.ontology.source_format='unknown',
  (s:any)=>s.ontology.references.pop(),
  (s:any)=>s.ontology.nodes.find((n:any)=>n.name==='Emit').meaning.text='different meaning',
  (s:any)=>s.ontology.source.sha256='0'.repeat(64),
  (s:any)=>s.ontology.ontology_admitted=true,
  (s:any)=>s.source_text='not JSON',
  (s:any)=>s.source_text='{}',
 ]){const changed=structuredClone(direct);mutate(changed);assert.throws(()=>compileProjectComposition(changed,[]),/DS_PROJECT_COMPOSITION/);}
});
test('project generation uses the compiled snapshot after source removal', t => {
 const {source}=project(t),graph=compileProject(source).graph;
 const expected=planProjectBuild(source,'typescript',profile);
 fs.rmSync(source,{recursive:true});
 assert.deepEqual(planCompiledProjectBuild(graph,'typescript',profile),expected);
 assert.throws(()=>planProjectBuild(source,'typescript',profile));
});
test('snapshot selection preserves typed closures and realization bytes', t => {
 const root=fs.mkdtempSync(path.join(os.tmpdir(),'ds-typed-snapshot-'));
 t.after(()=>fs.rmSync(root,{recursive:true,force:true}));
 const source=path.join(root,'source');
 fs.cpSync(path.resolve(import.meta.dirname,'../fixtures/capacity-decision'),source,{recursive:true});
 const graph=compileProject(source).graph;
 for(const n of graph.nodes){
  const expected=planInstantiation(loadProjectNode(source,n.selector),'rust');
  assert.deepEqual(planInstantiation(selectCompiledProjectNode(graph,n.selector),'rust'),expected,n.selector);
 }
 const expected=planProjectBuild(source,'rust');
 fs.rmSync(source,{recursive:true});
 assert.deepEqual(planCompiledProjectBuild(graph,'rust'),expected);
});
test('snapshot generation rejects fabricated and mutated source-bound graphs', t => {
 const {source}=project(t),graph=compileProject(source).graph;
 assert.throws(()=>planCompiledProjectBuild(structuredClone(graph),'typescript',profile),/unvalidated or changed/);
 graph.compositions![0]!.source.model.endpoint.timeout=2000;
 assert.throws(()=>planCompiledProjectBuild(graph,'typescript',profile),/unvalidated or changed/);
});
test('composition participates in source manifest, graph certificate and standard build/verify',async t=>{
 const {root,source}=project(t),compiled=compileProject(source);assert.equal(compiled.graph.compositions?.length,1);validateSourceManifest(validateProjectRoot(source));
 const plan=planProjectBuild(source,'typescript',profile),target=path.join(root,'build');publishProjectBuild(plan,target);assert.equal(verifyProjectBuild(source,'typescript',target,profile).result,'pass');
 const behavior=fs.readFileSync(path.join(target,'compositions/copy/behavior.mjs'),'utf8');const api=await import('data:text/javascript;base64,'+Buffer.from(behavior).toString('base64'));assert.deepEqual(api.execute({input:{value:'hello'}},{}),{value:'hello'});
 for(const file of ['behavior.mjs','ontology.json','bindings.json','function.json','composition.json','source.alch']){const p=path.join(target,'compositions/copy',file),bytes=fs.readFileSync(p);fs.appendFileSync(p,' ');assert.equal(verifyProjectBuild(source,'typescript',target,profile).result,'fail',file);fs.writeFileSync(p,bytes);}
 const changed=fixture();changed.model.endpoint.timeout=999;changed.ontology.nodes.find(n=>n.name==='Endpoint')!.binding=changed.model.endpoint;fs.writeFileSync(path.join(source,'compositions/copy.json'),JSON.stringify(changed));assert.notEqual(compileProject(source).certificate.graph_sha256,compiled.certificate.graph_sha256);assert.equal(verifyProjectBuild(source,'typescript',target,profile).result,'fail');
});
test('composition rejects missing sources, symbolic sources and unsupported generation/assurance paths',t=>{
 const {source}=project(t),graph=compileProject(source).graph;
 assert.throws(()=>planProjectBuild(source,'typescript'),/composition requires/);assert.throws(()=>planProjectBuild(source,'python'),/composition requires/);assert.throws(()=>planProjectInstantiation(source,['typescript']),/use build/);assert.throws(()=>createCheckedInterchange(graph),/does not yet cover/);
 const altered=structuredClone(graph);delete (altered as any).compositions;assert.throws(()=>createCompiledProjectCertificate(altered),/omitted/);
 graph.compositions![0]!.artifacts['behavior.mjs']='return 1';assert.throws(()=>createCompiledProjectCertificate(graph),/stale compiled/);
 const p=path.join(source,'compositions/copy.json');fs.renameSync(p,p+'.old');assert.throws(()=>validateProjectRoot(source),/declared source is missing/);fs.symlinkSync(p+'.old',p);assert.throws(()=>validateProjectRoot(source),/symbolic links/);
});
test('composition validates typed behavior, endpoint contracts and exact ontology dependencies',()=>{
 for(const mutate of [
  (s:any)=>s.contract.nodes[0].fields.value.path=['input','missing'],(s:any)=>s.contract.roots.extra='Input',
  (s:any)=>s.model.endpoint.output='Input',(s:any)=>s.model.schemas.Input.value.type='integer',
  (s:any)=>s.model.schemas.Input.value.const=123,(s:any)=>s.model.endpoint.authEnv='inline secret',
  (s:any)=>s.model.endpoint.target='unsupported',(s:any)=>s.model.flows.hidden=[],
  (s:any)=>s.ontology.ontology_admitted=true,(s:any)=>s.source_text+='drift',
  (s:any)=>s.ontology.references.pop(),(s:any)=>s.ontology.references[0].role='enforces',
  (s:any)=>s.ontology.nodes[0].record_type={value:'Int'},
 ]){const s=fixture();mutate(s);assert.throws(()=>compileProjectComposition(s,[]),/DS_PROJECT_COMPOSITION|DS_DECLARATIVE/);}
});

test('Rust composition is target-bound and verified as a native Cargo package',t=>{
 const {source,root}=project(t),s=fixture();s.model.endpoint.target='rust-http';s.model.endpoint.runtime='rust>=1.94';fs.writeFileSync(path.join(source,'compositions/copy.json'),JSON.stringify(s));
 const unsupported=structuredClone(s) as any;unsupported.model.schemas.Input.value.pattern='(?=a)';unsupported.ontology.nodes.find((n:any)=>n.name==='Input').constraints=unsupported.model.schemas.Input;assert.throws(()=>compileProjectComposition(unsupported,[]),/unsupported Rust pattern/);
 const compiled=compileProject(source);assert.ok(compiled.graph.compositions?.[0]?.artifacts['src/lib.rs']?.includes('fn n_Emit'));
 assert.equal(compiled.graph.compositions?.[0]?.artifacts['behavior.mjs'],undefined);
 assert.throws(()=>planProjectBuild(source,'typescript',profile),/declared target/);
 const plan=planProjectBuild(source,'rust'),out=path.join(root,'rust');publishProjectBuild(plan,out);assert.equal(verifyProjectBuild(source,'rust',out).result,'pass');
 fs.appendFileSync(path.join(out,'compositions/copy/src/lib.rs'),'// changed');assert.equal(verifyProjectBuild(source,'rust',out).result,'fail');
});

test('application layout binds relocated paths, preserves behavior and detects provenance drift',async t=>{
 const {root,source}=project(t),layout='domainspec.application-layout/v1' as const;
 const plan=planProjectBuild(source,'typescript',profile,layout),out=path.join(root,'application');
 assert.equal(publishProjectBuild(plan,out).receipt_path,'evidence/project-build.json');
 assert.equal(verifyProjectBuild(source,'typescript',out,profile,layout).result,'pass');
 assert.equal(verifyProjectBuild(source,'typescript',out,profile).result,'fail');
 assert.ok(plan.artifacts.every(a=>!a.relative_path.startsWith('src/')&&!a.relative_path.startsWith('compositions/')));
 const behavior=fs.readFileSync(path.join(out,'app/copy/behavior.mjs'),'utf8');
 const api=await import('data:text/javascript;base64,'+Buffer.from(behavior).toString('base64'));
 assert.deepEqual(api.execute({input:{value:'relocated'}},{}),{value:'relocated'});
 const moved=path.join(root,'moved');fs.renameSync(out,moved);
 assert.equal(verifyProjectBuild(source,'typescript',moved,profile,layout).result,'pass');
 fs.appendFileSync(path.join(moved,'provenance/copy/ontology.json'),' ');
 assert.equal(verifyProjectBuild(source,'typescript',moved,profile,layout).result,'fail');
 assert.throws(()=>planProjectBuild(source,'typescript',profile,'unknown' as any),/DS_OUTPUT_LAYOUT/);
});

test('application Rust layout separates runtime and binds each emitted file',t=>{
 const {source,root}=project(t),s=fixture();s.model.endpoint.target='rust-http';s.model.endpoint.runtime='rust>=1.94';
 fs.writeFileSync(path.join(source,'compositions/copy.json'),JSON.stringify(s));
 const layout='domainspec.application-layout/v1' as const,plan=planProjectBuild(source,'rust',undefined,layout),out=path.join(root,'application');
 publishProjectBuild(plan,out);
 const lib=fs.readFileSync(path.join(out,'app/copy/src/lib.rs'),'utf8');
 assert.ok(lib.includes('include!("../../../runtime/copy/runtime.rs")'));assert.ok(!lib.includes('struct Context'));
 assert.equal(verifyProjectBuild(source,'rust',out,undefined,layout).result,'pass');
 fs.appendFileSync(path.join(out,'runtime/copy/runtime.rs'),'// altered\n');
 assert.equal(verifyProjectBuild(source,'rust',out,undefined,layout).result,'fail');
});
