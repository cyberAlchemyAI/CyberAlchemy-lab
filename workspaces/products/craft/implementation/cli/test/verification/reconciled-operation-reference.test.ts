import assert from 'node:assert/strict';
import fs from 'node:fs';import os from 'node:os';import path from 'node:path';import test from 'node:test';
import {execFileSync} from 'node:child_process';import {createRequire} from 'node:module';
import {publicSelection} from '../helpers/composition-project.ts';
import {loadCompiledProjectGraph} from '../../src/input/project-model.ts';
import {planCompiledReconciledProject} from '../../src/generation/reconciled-project.ts';
import {createReconciledSemanticControls} from '../../src/verification/reconciled-semantic-controls.ts';
import {createRecordFreeOperationReference,OperationReferenceUnsupported,type OperationFixtureMode} from '../../src/verification/reconciled-operation-reference.ts';
import {OPERATION_FIXTURE_RUNNER} from '../../src/verification/reconciled-operation-fixture.ts';
const project=path.resolve(import.meta.dirname,'../../../..');
const scalar=(name='UInt64'):any=>({kind:'scalar',name}),valuePath=(root:string):any=>({op:'path',root,properties:[]});
function fixture(t:any,type=scalar(),moduleRoot='domain'){
 const temp=fs.mkdtempSync(path.join(os.tmpdir(),'ds-operation-reference-')),source=path.join(temp,'source'),nodes:string[]=[],edges:string[]=[];
 t.after(()=>fs.rmSync(temp,{recursive:true,force:true}));
 const write=(p:string,v:any)=>{const f=path.join(source,p);fs.mkdirSync(path.dirname(f),{recursive:true});fs.writeFileSync(f,JSON.stringify(v)+'\n');};
 const node=(id:string,kind:string,body:any)=>{if(!nodes.includes(id))nodes.push(id);write('specs/alpha/nodes/'+id+'.json',{schema_version:'domainspec.node/v1',feature_id:'alpha',node_id:id,kind,body:{description:id,...body}});};
 const edge=(from:string,relationship:string,to:string)=>{const edge_id=from+'-'+relationship+'-'+to;if(!edges.includes(edge_id))edges.push(edge_id);write('specs/alpha/edges/'+edge_id+'.json',{schema_version:'domainspec.edge/v1',feature_id:'alpha',edge_id,relationship,source_node_id:from,target_node_id:to,scope:'feature'});};
 const rule=(id:string,name:string,type:any,expression:any)=>node(id,'Rule',{predicate:'structured:domainspec.typed-rule/v2',typed_contract:{schema_version:'domainspec.typed-rule/v2',ontology_rule:'TEST-'+id.toUpperCase(),parameters:[{name,type}],expression}});
 rule('enabled','enabled',scalar('Bool'),{op:'eq',left:valuePath('enabled'),right:{op:'literal',type:'Bool',value:true}});
 rule('positive','amount',scalar(),{op:'lt',left:{op:'literal',type:'UInt64',value:'0'},right:valuePath('amount')});
 if(JSON.stringify(type).includes('alpha:status'))node('status','Enum',{values:['None','Some'],typed_contract:{schema_version:'domainspec.typed-sum/v1',ontology_node:'TEST-STATUS',variants:[{name:'None',ontology_variant:'TEST-STATUS#None',payload:null},{name:'Some',ontology_variant:'TEST-STATUS#Some',payload:scalar()}]}});
 node('perform','Operation',{reads:[],writes:[],effects:[],guard:'enabled',failure_continuation:'return-error'});
 edge('enabled','enforces','perform');edge('positive','enforces','perform');
 const inputs=[{name:'value',type},{name:'enabled',type:scalar('Bool')},{name:'amount',type:scalar()}];
 const binding={...publicSelection(moduleRoot).operations[0],selector:'alpha:perform',inputs,guards:[{selector:'alpha:enabled',arguments:[{parameter:'enabled',value:valuePath('enabled')}]},{selector:'alpha:positive',arguments:[{parameter:'amount',value:valuePath('amount')}]}],result:{type,value:valuePath('value')}};
 node('api','Interface',{typed_contract:{schema_version:'domainspec.typed-interface/v1',ontology_interface:'TEST-API',boundary_kind:'external',version_policy:{schema_version:'domainspec.interface-version-policy/v1',mode:'backward',direction:'consumer-to-provider',provider_version:'1.2.3'},contracts:[{contract_id:'request',ontology_contract:'TEST-REQUEST',fields:inputs.map(p=>({...p,meaning:p.name,ontology_field:'TEST-REQUEST#'+p.name}))}],operations:[{operation_id:'perform',operation_ref:'alpha:perform',request:{kind:'contract',contract_id:'request'},result:type}]}});
 edge('api','exposes','perform');
 const save=()=>{write('project.json',{schema_version:'domainspec.project/v1',project_id:'operation-reference',features:['alpha'],cross_feature_edges:[]});write('specs/alpha/feature.json',{schema_version:'domainspec.feature/v1',feature_id:'alpha',nodes,edges});};save();
 const selection={...publicSelection(moduleRoot),factories:[],operations:[binding]},graph=loadCompiledProjectGraph(source),plan=planCompiledReconciledProject(graph,selection);
 const reference=createRecordFreeOperationReference(graph,binding),samples=reference.facts.samples(type);
 const recipe=(v=samples[0]!,enabled=true,amount='1'):any=>({tag:'fields',fields:{value:v,enabled:{tag:'scalar',value:enabled},amount:{tag:'scalar',value:amount}}});
 return {temp,source,selection,graph,plan,reference,recipe,type,samples,node,edge,save};
}
function cases(f:ReturnType<typeof fixture>){
 const result:any[]=[],add=(recipe:any,mode:OperationFixtureMode='committed',capture=false)=>result.push({recipe,mode,capture,expected:f.reference.expected(recipe,mode)});
 f.samples.forEach(v=>{add(f.recipe(v));add(f.recipe(v),'committed',true);});
 for(const mode of ['committed','rejected','indeterminate','begin-throw','commit-throw','rollback-throw','receipt-empty','receipt-unknown','receipt-extra','receipt-null','receipt-getter','receipt-inherited','receipt-symbol','receipt-hidden','receipt-array','receipt-undefined'] as OperationFixtureMode[]){
  add(f.recipe(),mode);add(f.recipe(f.samples[0],false,'0'),mode);
 }
 add(f.recipe(f.samples[0],true,'0'));add(f.recipe(), 'committed',true);
 for(const bad of f.reference.facts.negative(f.type,f.samples[0]!))add(f.recipe(bad));
 for(const mode of ['null','array','inherited','extra','symbol','getter','non-enumerable','missing-field','frozen','null-prototype'])add(f.reference.facts.bad(f.recipe(),mode,'enabled'));
 return result;
}
function nativeProgram(f:ReturnType<typeof fixture>,n:any){
 return `import fs from 'node:fs';import path from 'node:path';import {execFileSync} from 'node:child_process';import {pathToFileURL} from 'node:url';
 import {loadCompiledProjectGraph,planCompiledReconciledProject,executeReconciledVerification} from './dist/index.js';
 const graph=loadCompiledProjectGraph(${JSON.stringify(f.source)}),plan=planCompiledReconciledProject(graph,${JSON.stringify(f.selection)}),root=${JSON.stringify(path.join(f.temp,'native'))};
 for(const a of plan.resolved.artifacts){const file=path.join(root,a.relative_path);fs.mkdirSync(path.dirname(file),{recursive:true});fs.writeFileSync(file,a.content);}
 fs.writeFileSync(path.join(root,'package.json'),'{"type":"module"}');
 const config=path.join(root,'compiler.json');fs.writeFileSync(config,JSON.stringify({compilerOptions:{strict:true,skipLibCheck:true,target:'ES2022',module:'NodeNext',declaration:true,rootDir:'.',outDir:'compiled',types:[]},files:plan.resolved.artifacts.filter(a=>a.relative_path.endsWith('.ts')).map(a=>a.relative_path)}));
 execFileSync(process.execPath,[${JSON.stringify(n.options.typescript_root+'/bin/tsc')},'--project',config],{encoding:'utf8'});
 fs.writeFileSync(path.join(root,'fixture.mjs'),${JSON.stringify(OPERATION_FIXTURE_RUNNER)});
 const {observeOperationFixture}=await import(pathToFileURL(path.join(root,'fixture.mjs')).href);
 const module=plan.resolved.modules.find(m=>m.qualified_selectors.includes('alpha:perform')&&m.exports.some(e=>e.name==='operationPerform')),file=path.join(root,'compiled',module.relative_path.replace(/\\.ts$/,'.js'));
 const native=await import(pathToFileURL(file).href),fn=native.operationPerform;
 const samples=${JSON.stringify(cases(f))};
 const observe=(call,c)=>observeOperationFixture(call,c.recipe,c.mode,c.capture?(input=>{input.enabled=false;input.amount='0';if(input.value&&typeof input.value==='object'){if(Array.isArray(input.value))input.value.splice(0,input.value.length);else input.value.variant='None';}else input.value='changed';}):null);
 `;
}

test('record-free Operation reference refuses effectful and owned-record coverage instead of inventing providers',t=>{
 const f=fixture(t),semantic=createReconciledSemanticControls(f.graph,f.plan);
 assert.equal(f.graph.nodes.some(n=>n.kind==='Entity'||n.kind==='Value Object'||n.kind==='Enum'),false);
 assert.equal(semantic.rows.find(r=>r.kind==='Interface')!.state,'ready');
 assert.equal(semantic.rows.find(r=>r.kind==='Operation')!.state,'ready');
 for(const key of ['reads','writes','events'] as const){
  const b=structuredClone(f.selection.operations[0]);
  if(key==='reads')b.reads=[{slot:'row',target:'alpha:row',parameter:'row',key:valuePath('amount')}];
  if(key==='writes')b.writes=[{slot:'row',target:'alpha:row',mode:'create',value:valuePath('value')}];
  if(key==='events')b.events=[{slot:'event',target:'alpha:event',parameter:'event'}];
  assert.throws(()=>createRecordFreeOperationReference(f.graph,b),OperationReferenceUnsupported);
 }
 f.node('row','Entity',{fields:['id'],typed_contract:{schema_version:'domainspec.typed-record/v1',ontology_node:'TEST-ROW',properties:[{name:'id',type:scalar(),identity:true,cardinality:'one',meaning:'id',ontology_property:'TEST-ROW#id'}]}});f.save();
 const graph=loadCompiledProjectGraph(f.source),b=structuredClone(f.selection.operations[0]);b.inputs[0].type={kind:'named',selector:'alpha:row'};b.result.type=b.inputs[0].type;
 assert.throws(()=>createRecordFreeOperationReference(graph,b),/owned record alpha:row/);
});
test('native scalar Operation matches independent inputs, guard order, receipt uncertainty and deferred settlement; Interface needs no Entity',t=>{
 const f=fixture(t),n=nativeContext(f),result=n.run(nativeProgram(f,n)+`
 const actual=[];for(const c of samples)actual.push(await observe(fn,c));
 const report=executeReconciledVerification(graph,plan,${JSON.stringify(n.options)});
 console.log(JSON.stringify({actual,report}));
 `);
 assert.deepEqual(result.actual,cases(f).map(c=>c.expected));
 const semantic=result.report.checks.find((c:any)=>c.id==='selected-generator-semantic-controls');
 assert.equal(semantic.evidence.interface_signature_count,1,JSON.stringify(semantic));
 assert.equal(semantic.result,'pass',JSON.stringify(semantic));
 assert.deepEqual(semantic.evidence.remaining,[]);
 assert.equal(result.report.checks.find((c:any)=>c.id==='verification-workspace-cleanup').result,'pass');
});
test('native Enum and composed scalar/Enum Operations require no dummy record and preserve exact value carriers',async t=>{
 const en={kind:'named',selector:'alpha:status'},types=[scalar('String'),scalar('Bool'),en,{kind:'optional',element:scalar()},{kind:'list',element:scalar()},{kind:'set',element:scalar()},{kind:'list',element:en},{kind:'set',element:en},{kind:'sum',variants:[{name:'Absent',ontology_variant:'TEST-INLINE#Absent',payload:null},{name:'Present',ontology_variant:'TEST-INLINE#Present',payload:scalar()}]}];
 for(const [i,type]of types.entries())await t.test('shape-'+i,t=>{
  const f=fixture(t,type,i%2?'relocated/root':'domain'),n=nativeContext(f),result=n.run(nativeProgram(f,n)+`const actual=[];for(const c of samples)actual.push(await observe(fn,c));console.log(JSON.stringify(actual));`);
  assert.equal(f.graph.nodes.some(n=>n.kind==='Entity'||n.kind==='Value Object'),false);
  assert.deepEqual(result,cases(f).map(c=>c.expected));
 });
});
test('independent Operation fixture rejects compiling settlement, guard, capture, ownership and outcome mutants',t=>{
 const f=fixture(t,{kind:'named',selector:'alpha:status'}),n=nativeContext(f),result=n.run(nativeProgram(f,n)+`
 const provider=file.replace(/\\.js$/,'.provider.js'),original=fs.readFileSync(provider,'utf8'),reports=[];
 const wrappers={
  'deferred-capture':'async(p,d)=>{await Promise.resolve();return originalExecute(p,d);}',
  'early-begin':'async(p,d)=>{d.store.begin();return Object.freeze({status:"committed",value:p.value});}',
  'early-commit':'async(p,d)=>originalExecute(p,{store:{begin:async()=>{const tx=await d.store.begin();return {...tx,commit:async b=>{tx.commit(b);return {status:"committed"};}};}}})',
  'twice-commit':'async(p,d)=>originalExecute(p,{store:{begin:async()=>{const tx=await d.store.begin();return {...tx,commit:async b=>{await tx.commit(b);return tx.commit(b);}};}}})',
  'rollback-after-commit':'async(p,d)=>originalExecute(p,{store:{begin:async()=>{const tx=await d.store.begin();return {...tx,commit:async b=>{try{return await tx.commit(b);}finally{await tx.rollback();}}};}}})',
  'skip-rollback':'async(p,d)=>originalExecute(p,{store:{begin:async()=>({...await d.store.begin(),rollback:async()=>{}})}})',
  'early-rollback':'async(p,d)=>originalExecute(p,{store:{begin:async()=>{const tx=await d.store.begin();return {...tx,rollback:async()=>{tx.rollback();}};}}})',
  'unexpected-read':'async(p,d)=>originalExecute(p,{store:{begin:async()=>{const tx=await d.store.begin();return {...tx,commit:async b=>{await tx.read({});return tx.commit(b);}};}}})',
  'extra-batch':'async(p,d)=>originalExecute(p,{store:{begin:async()=>{const tx=await d.store.begin();return {...tx,commit:async b=>tx.commit(Object.freeze({...b,extra:true}))};}}})',
  'mutable-batch':'async(p,d)=>originalExecute(p,{store:{begin:async()=>{const tx=await d.store.begin();return {...tx,commit:async b=>tx.commit({...b})};}}})',
  'extra-outcome':'async(p,d)=>Object.freeze({...await originalExecute(p,d),extra:true})',
  'mutable-outcome':'async(p,d)=>({...await originalExecute(p,d)})',
  'missing-outcome':'async(p,d)=>{const r=await originalExecute(p,d);return Object.freeze({status:r.status});}',
  'collapse-rejected':'async(p,d)=>{const r=await originalExecute(p,d);return Object.freeze({...r,status:r.status==="rejected"?"failed":r.status});}',
  'collapse-uncertain':'async(p,d)=>{const r=await originalExecute(p,d);return Object.freeze({...r,status:r.status==="indeterminate"?"rejected":r.status});}',
  'cleanup-claim':'async(p,d)=>{const r=await originalExecute(p,d);return Object.freeze({...r,...("cleanupFailed" in r?{cleanupFailed:false}:{})});}',
  'wrong-continuation':'async(p,d)=>{const r=await originalExecute(p,d);return Object.freeze({...r,...("continuation" in r?{continuation:"retry"}:{})});}',
  'wrong-value':'async(p,d)=>{const r=await originalExecute(p,d);return Object.freeze({...r,...(r.status==="committed"?{value:Object.freeze({variant:"None"})}:{})});}',
  'wrong-carrier':'async(p,d)=>{const r=await originalExecute(p,d);return Object.freeze({...r,...(r.status==="committed"&&r.value.variant==="Some"?{value:Object.freeze({variant:"Some",payload:String(r.value.payload)})}:{})});}',
  'input-write':'async(p,d)=>{if(p&&typeof p==="object")p.enabled=false;return originalExecute(p,d);}',
  'getter-read':'async(p,d)=>{if(p&&typeof p==="object")void p.enabled;return originalExecute(p,d);}'
 };
 // Deliberately broken ports may reject after the mutant has returned early.
 const unhandled=[];process.on('unhandledRejection',e=>unhandled.push(String(e)));
 for(const mode of [...Object.keys(wrappers),'skip-first-guard','reverse-guards','remove-freeze']){
  let changed;
  if(wrappers[mode])changed=original.replace('export const execute =','const originalExecute =')+'\\nexport const execute='+wrappers[mode]+';\\n';
  else if(mode==='skip-first-guard')changed=original.replace('if (!guard0(','if (false && !guard0(');
  else if(mode==='remove-freeze')changed=original.replaceAll('Object.freeze(','Object(');
  else{
   const checks=[...original.matchAll(/if \\(!guard[0-9]+\\([^]*?return abort\\([^;]+;/g)];
   if(checks.length!==2)throw Error('guard mutation target');changed=original.replace(checks[0][0],'__FIRST__').replace(checks[1][0],checks[0][0]).replace('__FIRST__',checks[1][0]);
  }
  if(changed===original||changed.includes('export const execute =')&&wrappers[mode])throw Error('mutation not applied:'+mode);
  fs.writeFileSync(provider,changed);execFileSync(process.execPath,['--check',provider],{encoding:'utf8'});
  const mutant=(await import(pathToFileURL(provider).href+'?mutant='+mode)).execute;
  let detected=false,caseIndex=-1,reason=null;
  for(const [index,c]of samples.entries()){
   try{const actual=await observe(mutant,c);if(JSON.stringify(actual)!==JSON.stringify(c.expected)){detected=true;caseIndex=index;break;}}
   catch(e){detected=true;caseIndex=index;reason=e.message;break;}
  }
  reports.push({mode,detected,caseIndex,reason});
 }
 fs.writeFileSync(provider,original);
 console.log(JSON.stringify({reports}));
 `);
 assert.equal(result.reports.length,24);
 for(const r of result.reports)assert.equal(r.detected,true,JSON.stringify(r));
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
