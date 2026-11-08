import assert from 'node:assert/strict';
import fs from 'node:fs';import path from 'node:path';import test from 'node:test';import {execFileSync} from 'node:child_process';
import {operationFixture,valueOperationFixture} from '../helpers/cross-generator-operation.ts';
import {publicFixture,publicSelection} from '../helpers/composition-project.ts';
import {planCompiledReconciledProject} from '../../src/generation/reconciled-project.ts';
import {createCrossGeneratorBoundary} from '../../src/verification/reconciled-cross-generator-boundary.ts';
import {createCrossGeneratorOperationControls,checkCrossGeneratorOperationObservations,crossGeneratorOperationProbe,expandOperationProtocolRecipe} from '../../src/verification/reconciled-cross-generator-operation.ts';
import {CROSS_GENERATOR_OPERATION_RUNNER} from '../../src/verification/reconciled-cross-generator-operation-runner.ts';
import {canonicalJson} from '../../src/input/source-manifest.ts';
const project=path.resolve(import.meta.dirname,'../../../..'),base=path.join(project,'development/reconciliation-v1/profile-compiler-reconciliation');
const definition=fs.readFileSync(path.join(base,'cross-generator-operation-contract.json'),'utf8'),protocol=fs.readFileSync(path.join(base,'cross-generator-operation-protocol-contract.json'),'utf8'),boundaryDefinition=fs.readFileSync(path.join(base,'cross-generator-verification-contract.json'),'utf8');
type Fixture=Pick<ReturnType<typeof operationFixture>,'root'|'compile'>;
function controls(f:Fixture){
 const {graph,plan}=f.compile(),boundary=createCrossGeneratorBoundary(graph,plan,boundaryDefinition);
 return {graph,plan,boundary,controls:createCrossGeneratorOperationControls(graph,plan,boundary,definition,protocol)};
}
function expected(c:ReturnType<typeof controls>['controls']){
 return {controls_sha256:c.controls_sha256,rows:c.rows.flatMap(r=>r.state!=='ready'?[]:[{selector:r.selector,initialization:r.initialization,identity:r.identity,descriptor:r.descriptor,cases:r.cases.map(v=>({id:v.id,...v.expected}))}])};
}
function native(t:any,f:Fixture){
 const c=controls(f),root=path.join(f.root,'protocol-native'),src=path.join(root,'source'),out=path.join(root,'compiled');
 assert.ok(c.controls.rows.length);assert.ok(c.controls.rows.every(r=>r.state==='ready'),JSON.stringify(c.controls.rows.map(r=>({selector:r.selector,state:r.state,...(r.state!=='ready'?{reason:r.reason}:{cases:r.cases.length})}))));
 const modules=[...new Map(c.controls.rows.flatMap(r=>r.modules).map(m=>[m.relative_path,m])).values()];
 fs.mkdirSync(root);
 for(const m of modules){const a=c.plan.resolved.artifacts.find(a=>a.relative_path===m.relative_path)!,file=path.join(src,m.relative_path);fs.mkdirSync(path.dirname(file),{recursive:true});fs.writeFileSync(file,a.content);}
 const config=path.join(root,'tsconfig.json'),runner=path.join(root,'observer.mjs'),input=path.join(root,'input.json');
 fs.writeFileSync(config,JSON.stringify({compilerOptions:{strict:true,skipLibCheck:true,target:'ES2022',module:'CommonJS',rootDir:src,outDir:out,types:[]},files:modules.map(m=>path.join(src,m.relative_path))}));
 fs.writeFileSync(runner,CROSS_GENERATOR_OPERATION_RUNNER);fs.writeFileSync(input,JSON.stringify(crossGeneratorOperationProbe(c.controls)));
 const image=nativeToolchainImage();assert.equal(image, NATIVE_TEST_IMAGE_ID);
 const docker=['run','--rm','--pull','never','--network','none','--read-only','--cap-drop','ALL','--security-opt','no-new-privileges','--user',process.getuid!()+':'+process.getgid!(),'--mount','type=bind,source='+f.root+',target='+f.root,'--workdir',root,image];
 const command=(args:string[])=>{try{return execFileSync('docker',[...docker,...args],{encoding:'utf8',timeout:60000,maxBuffer:16777216});}catch(e:any){throw Error([e.message,e.stdout,e.stderr].filter(Boolean).join('\n'));}};
 const compile=()=>command(['tsc','--project',config]);compile();
 const observe=()=>JSON.parse(command(['node',runner,input,out]));
 const verify=(observed:any)=>{
  const wanted=expected(c.controls);
  for(const [i,row]of wanted.rows.entries()){
   const got=observed.rows[i];assert.deepEqual(got.initialization,row.initialization);assert.deepEqual(got.identity,row.identity);assert.deepEqual(got.descriptor,row.descriptor);
   for(const [j,value]of row.cases.entries())if(canonicalJson(got.cases[j])!==canonicalJson(value))assert.deepEqual(got.cases[j],value,'first mismatching case '+value.id+' index '+j);
  }
  return checkCrossGeneratorOperationObservations(c.controls,observed);
 };
 return {...c,root,src,out,compile,observe,verify};
}
test('source Operation call protocol binds every complete case and original ownership links',t=>{
 const c=controls(operationFixture(t)),row=c.controls.rows[0]!;
 assert.equal(row.state,'ready',row.state!=='ready'?row.reason:'');if(row.state!=='ready')return;
 assert.ok(row.cases.length>100);assert.equal(row.initialization.length,3);assert.equal(row.identity.events.length,1);
 assert.ok(row.cases.some(c=>c.expected.calls.some(call=>call.method==='event')));
 assert.ok(row.cases.some(c=>c.expected.calls.some(call=>call.method==='fromVariant')));
 assert.ok(row.cases.some(c=>c.expected.calls.length===0));
 assert.ok(JSON.stringify(row.cases).includes('owned:case-'));
 assert.equal(checkCrossGeneratorOperationObservations(c.controls,expected(c.controls)).tested_operation_count,1);
 assert.ok(!JSON.stringify(crossGeneratorOperationProbe(c.controls)).includes('"expected"'));
 for(const change of [(v:any)=>v.rows.pop(),(v:any)=>v.rows[0].initialization.pop(),(v:any)=>v.rows[0].identity.operation=false,(v:any)=>v.rows[0].cases.pop(),(v:any)=>v.rows[0].cases.find((c:any)=>c.calls.length).calls[0].input_changed=true,(v:any)=>v.rows[0].cases.find((c:any)=>c.calls.length).calls[0].arity=99]){
  const bad=structuredClone(expected(c.controls));change(bad);assert.throws(()=>checkCrossGeneratorOperationObservations(c.controls,bad),/observation mismatch/);
 }
 assert.throws(()=>crossGeneratorOperationProbe(structuredClone(c.controls)),/registered/);
 assert.throws(()=>createCrossGeneratorOperationControls(c.graph,c.plan,c.boundary,definition,protocol+' '),/definition drift/);
 assert.throws(()=>expandOperationProtocolRecipe([{tag:'ref',value:'0'}],0),/recipe reference/);
 t.diagnostic(JSON.stringify({cases:row.cases.length,calls:row.cases.reduce((n,c)=>n+c.expected.calls.length,0),controls_sha256:c.controls.controls_sha256}));
});
test('original compound Operation provider calls match source expectations in both module roots',async t=>{
 for(const layout of ['domain','application/domain'])await t.test(layout,t=>{
  const n=native(t,operationFixture(t,layout)),result=n.verify(n.observe());t.diagnostic(JSON.stringify({...result,layout}));
 });
});
test('original Enum-only and scalar Operations need no synthetic record or Event',t=>{
 const n=native(t,valueOperationFixture(t,'application/domain'));n.verify(n.observe());
 const f=publicFixture(t),s=native(t,{root:f.root,compile:()=>({graph:f.graph,plan:planCompiledReconciledProject(f.graph,publicSelection())})});
 const result=s.verify(s.observe());assert.equal(result.tested_operation_count,2);
});
test('strict-compiling duplicate direct calls and replaced wrapper identity cannot hide behind unchanged outcomes',t=>{
 const n=native(t,operationFixture(t)),row=n.controls.rows[0]!,provider=path.join(n.src,row.provider_path),original=fs.readFileSync(provider,'utf8');
 const baseline=n.observe();n.verify(baseline);
 const mutants=[
  original.replace(/if\(!((guard\d+)\(\{[^\n]+\}\))\)/,'if(!($1,$1))'),
  original.replace(/(own\d+\(write0\);)/,'$1$1'),
  original.replace(/(const own\d+Factory=(ownedImport\d+)\(\);)/,'$2();$1'),
  original.replace(/(ownedImport\d+\.fromVariant\(v\.variant\))/,'($1,$1)')
 ];
 for(const mutant of mutants){
  assert.notEqual(mutant,original);fs.writeFileSync(provider,mutant);n.compile();const observed=n.observe();
  assert.deepEqual(observed.rows.map((r:any)=>r.cases.map((c:any)=>c.semantic.outcome)),baseline.rows.map((r:any)=>r.cases.map((c:any)=>c.semantic.outcome)));
  assert.throws(()=>checkCrossGeneratorOperationObservations(n.controls,observed),/observation mismatch/);
 }
 fs.writeFileSync(provider,original);
 const wrapper=path.join(n.src,row.relative_path),old=fs.readFileSync(wrapper,'utf8'),changed=old.replace('Object.assign(execute,','Object.assign((...args:Parameters<typeof execute>)=>execute(...args),');
 assert.notEqual(old,changed);fs.writeFileSync(wrapper,changed);n.compile();const observed=n.observe();
 assert.deepEqual(observed.rows.map((r:any)=>r.cases.map((c:any)=>c.semantic)),baseline.rows.map((r:any)=>r.cases.map((c:any)=>c.semantic)));
 assert.equal(observed.rows[0].identity.operation,false);assert.throws(()=>checkCrossGeneratorOperationObservations(n.controls,observed),/observation mismatch/);
});

test('missing ownership calls, wrong clock identity and replaced Event wrappers are rejected',t=>{
 const n=native(t,operationFixture(t)),row=n.controls.rows[0]!,file=path.join(n.src,row.provider_path),original=fs.readFileSync(file,'utf8');
 const baseline=n.observe();n.verify(baseline);
 const missing=original.replace(/own\d+\(write0\);/,'');
 assert.notEqual(missing,original);fs.writeFileSync(file,missing);n.compile();
 const omitted=n.observe();assert.throws(()=>checkCrossGeneratorOperationObservations(n.controls,omitted),/observation mismatch/);
 assert.ok(omitted.rows[0].cases.some((c:any,i:number)=>canonicalJson(c.semantic)===canonicalJson(baseline.rows[0].cases[i].semantic)&&canonicalJson(c.calls)!==canonicalJson(baseline.rows[0].cases[i].calls)));
 const swapped=original.replace(/(const event1=[^\n]+)clocks\["audit-fact"\]/,'$1clocks["posted-fact"]');
 assert.notEqual(swapped,original);fs.writeFileSync(file,swapped);n.compile();const clocks=n.observe();
 assert.throws(()=>checkCrossGeneratorOperationObservations(n.controls,clocks),/observation mismatch/);
 assert.ok(clocks.rows[0].cases.some((c:any,i:number)=>canonicalJson(c.semantic.outcome)===canonicalJson(baseline.rows[0].cases[i].semantic.outcome)&&canonicalJson(c.calls)!==canonicalJson(baseline.rows[0].cases[i].calls)));
 fs.writeFileSync(file,original);
 const event=row.modules.find(m=>m.role==='event-wrapper')!,wrapper=path.join(n.src,event.relative_path),old=fs.readFileSync(wrapper,'utf8');
 const changed=old.replace('Object.assign(make,','Object.assign((...args:Parameters<typeof make>)=>make(...args),');
 assert.notEqual(changed,old);fs.writeFileSync(wrapper,changed);n.compile();const observed=n.observe();
 assert.deepEqual(observed.rows[0].cases,baseline.rows[0].cases);
 assert.equal(observed.rows[0].identity.events[0].original,false);
 assert.throws(()=>checkCrossGeneratorOperationObservations(n.controls,observed),/observation mismatch/);
});

test('reusing an original owned return across cases cannot hide behind equal fields',t=>{
 const n=native(t,operationFixture(t)),row=n.controls.rows[0]!,factory=row.modules.find(m=>m.role==='factory'&&m.selector==='commerce:detail')!;
 const baseline=n.observe();n.verify(baseline);
 const file=path.join(n.src,factory.relative_path),old=fs.readFileSync(file,'utf8');
 const changed=old.replace("create:(input:unknown):Result=>construct('create',input),",
  "create:(()=>{const cache=new Map<string,Result>();return (input:unknown):Result=>{const fresh=construct('create',input);if(!fresh.ok)return fresh;const key=fresh.value.hash();const previous=cache.get(key);if(previous)return previous;cache.set(key,fresh);return fresh;};})(),");
 assert.notEqual(changed,old);fs.writeFileSync(file,changed);n.compile();const observed=n.observe();
 assert.deepEqual(observed.rows[0].cases.map((c:any)=>c.semantic),baseline.rows[0].cases.map((c:any)=>c.semantic));
 assert.throws(()=>checkCrossGeneratorOperationObservations(n.controls,observed),/observation mismatch/);
 assert.ok(observed.rows[0].cases.some((c:any,i:number)=>canonicalJson(c.calls)!==canonicalJson(baseline.rows[0].cases[i].calls)));
});

test('equal but distinct owned Enum values do not satisfy singleton identity',t=>{
 const n=native(t,valueOperationFixture(t)),row=n.controls.rows[0]!,component=row.modules.find(m=>m.role==='enum-component')!;
 n.verify(n.observe());
 const file=path.join(n.src,component.relative_path),old=fs.readFileSync(file,'utf8');
 const changed=old.replace('return cases[value as keyof typeof cases];','const copy=Object.freeze({...cases[value as keyof typeof cases]});ownership.add(copy);return copy;');
 assert.notEqual(changed,old);fs.writeFileSync(file,changed);n.compile();const observed=n.observe();
 assert.ok(JSON.stringify(observed).includes('OPERATION_PROBE_ENUM_SINGLETON'));
 assert.throws(()=>checkCrossGeneratorOperationObservations(n.controls,observed),/observation mismatch/);
});

import {nativeToolchainImage, NATIVE_TEST_IMAGE_ID} from '../helpers/native-toolchain-image.ts';
