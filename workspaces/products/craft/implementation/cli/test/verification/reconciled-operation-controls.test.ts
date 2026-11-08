import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {createRequire} from 'node:module';
import {execFileSync} from 'node:child_process';
import test from 'node:test';
import {loadCompiledProjectGraph} from '../../src/input/project-model.ts';
import {createCompiledProjectCertificate} from '../../src/compilation/certificate.ts';
import {compileCompositionBoundary,COMPOSITION_BOUNDARY_VERSION,COMPOSITION_BOUNDARY_CONTRACT_SHA256} from '../../src/input/composition-boundary.ts';
import {compileSelectedProjectFields,EXACT_PROJECT_FIELD_SELECTION_VERSION,EXACT_FIELD_CONTRACT_SHA256} from '../../src/input/compiled-field-model.ts';
import {compileOperationActionBindings,OPERATION_ACTION_BINDINGS_VERSION} from '../../src/typed-operation/action-bindings.ts';
import {planConfiguredOperations,CONFIGURED_OPERATION_VERSION} from '../../src/generation/configured-operations.ts';
import {canonicalJson,sha256} from '../../src/input/source-manifest.ts';

const project=path.resolve(import.meta.dirname,'../../../..'),base='development/reconciliation-v1/profile-compiler-reconciliation/';
const bytes=(p:string)=>fs.readFileSync(path.join(project,p),'utf8'),read=(p:string)=>JSON.parse(fs.readFileSync(p,'utf8'));
const rules={configuration:bytes(base+'configuration.json'),base:bytes('development/implementation-conformance/ontology-experiment/profiles/base-domain.profile.json'),typescript:bytes('development/implementation-conformance/ontology-experiment/profiles/typescript-strict.profile.json'),
  rule_contract:bytes(base+'string-order-rule-contract.json'),collection_contract:bytes(base+'rule-collection-value-contract.json'),predicate_contract:bytes(base+'rule-collection-predicate-contract.json'),numeric_contract:bytes(base+'rule-numeric-contract.json'),exact_contract:bytes(base+'rule-exact-contract.json'),literal_contract:bytes(base+'rule-exact-literal-contract.json'),structured_contract:bytes(base+'rule-structured-value-contract.json'),field_contract:bytes('development/reconciliation-v1/contracts/exact-field-and-reference-model.json')};
const sources={operation_contract:bytes(base+'operation-generation-contract.json'),factory_contract:bytes(base+'factory-structured-rule-contract.json'),enum_provider:bytes('impl/architecture-conformance/typescript/runtime/enum/index.ts'),rules,
  events:{configuration:rules.configuration,base:rules.base,typescript:rules.typescript,event_contract:bytes(base+'event-generation-contract.json')}};
const boundarySource=bytes('development/reconciliation-v1/contracts/composition-boundary.json'),actionSource=bytes(base+'operation-action-contract.json');
const scalar=(name='String'):any=>({kind:'scalar',name}),named=(id:string):any=>({kind:'named',selector:'commerce:'+id});
const at=(root:string,...properties:string[]):any=>({op:'path',root,properties}),lit=(type:string,value:any):any=>({op:'literal',type,value});
const arg=(parameter:string,value:any)=>({parameter,value});
function fixture(t:any){
  const temp=fs.mkdtempSync(path.join(os.tmpdir(),'ds-operations-'));t.after(()=>fs.rmSync(temp,{recursive:true,force:true}));
  const source=path.join(temp,'source'),nodes:string[]=[],edges:string[]=[];
  const write=(p:string,v:any)=>{const f=path.join(source,p);fs.mkdirSync(path.dirname(f),{recursive:true});fs.writeFileSync(f,JSON.stringify(v,null,2));};
  const node=(id:string,kind:string,body:any)=>{nodes.push(id);write('specs/commerce/nodes/'+id+'.json',{schema_version:'domainspec.node/v1',feature_id:'commerce',node_id:id,kind,body:{description:id,...body}});};
  const edge=(id:string,relationship:string,from:string,to:string)=>{edges.push(id);write('specs/commerce/edges/'+id+'.json',{schema_version:'domainspec.edge/v1',edge_id:id,feature_id:'commerce',relationship,source_node_id:from,target_node_id:to,scope:'feature'});};
  const rule=(id:string,parameters:any[],expression:any)=>node(id,'Rule',{predicate:'structured:domainspec.typed-rule/v2',typed_contract:{schema_version:'domainspec.typed-rule/v2',ontology_rule:'FIXTURE-'+id.toUpperCase(),parameters,expression}});
  const property=(id:string,name:string,type:any,identity=false)=>({ontology_property:'FIXTURE-'+id.toUpperCase()+'#'+name,name,type,identity,meaning:name,cardinality:type.kind==='optional'?'optional':type.kind==='list'?'many':type.kind==='set'?'many-unique':'one'});
  rule('positive',[{name:'amount',type:scalar('UInt64')}],{op:'lt',left:lit('UInt64','0'),right:at('amount')});
  rule('can-post',[{name:'current',type:named('account')},{name:'amount',type:scalar('UInt64')}],{op:'lt',left:at('amount'),right:at('current','FIXTURE-ACCOUNT#balance')});
  rule('receipt-matches',[{name:'expected',type:scalar('UInt64')},{name:'actual',type:scalar('UInt64')}],{op:'eq',left:at('expected'),right:at('actual')});
  node('detail','Value Object',{fields:['amount'],invariant_refs:['commerce:positive'],typed_contract:{schema_version:'domainspec.typed-record/v1',ontology_node:'FIXTURE-DETAIL',properties:[property('detail','amount',scalar('UInt64'))]}});
  node('status','Enum',{values:['Ready','Draft'],typed_contract:{schema_version:'domainspec.typed-sum/v1',ontology_node:'FIXTURE-STATUS',variants:['Ready','Draft'].map(name=>({name,ontology_variant:'FIXTURE-STATUS#'+name,payload:null}))}});
  const choice={kind:'sum',variants:[{name:'None',ontology_variant:'FIXTURE-CHOICE#None',payload:null},{name:'Some',ontology_variant:'FIXTURE-CHOICE#Some',payload:named('detail')}]};
  const props=[property('account','id',scalar(),true),property('account','balance',scalar('UInt64')),property('account','detail',named('detail')),property('account','labels',{kind:'set',element:scalar()}),property('account','status',named('status')),property('account','choice',choice)];
  node('account','Entity',{fields:props.map(p=>p.name),typed_contract:{schema_version:'domainspec.typed-record/v1',ontology_node:'FIXTURE-ACCOUNT',properties:props}});
  node('receipt','Entity',{fields:['id','amount'],typed_contract:{schema_version:'domainspec.typed-record/v1',ontology_node:'FIXTURE-RECEIPT',properties:[property('receipt','id',scalar(),true),property('receipt','amount',scalar('UInt64'))]}});
  node('posted','Event',{event_type:'posted',version:'1',occurrence_id:{field_id:'occurrence-id',type_ref:{kind:'primitive',name:'uuid'},required:true},occurred_at_policy:'generated',payload:[{field_id:'account-id',type_ref:{kind:'reference',selector:'commerce:account'},required:true},{field_id:'amount',type_ref:{kind:'primitive',name:'integer'},required:true}]});
  node('post','Operation',{reads:['current-account'],writes:['account-state','receipt-state'],effects:['posted-fact','audit-fact'],guard:'can-post',failure_continuation:'return-post-error'});
  edge('post-reads-account','reads','post','account');edge('post-creates-receipt','creates','post','receipt');edge('post-produces-posted','produces','post','posted');edge('can-post-enforces-post','enforces','can-post','post');edge('receipt-matches-enforces-post','enforces','receipt-matches','post');
  const save=()=>{write('project.json',{schema_version:'domainspec.project/v1',project_id:'native-operations',features:['commerce'],cross_feature_edges:[]});write('specs/commerce/feature.json',{schema_version:'domainspec.feature/v1',feature_id:'commerce',nodes,edges});};save();
  const bindings:any={schema_version:OPERATION_ACTION_BINDINGS_VERSION,selector:'commerce:post',inputs:[{name:'account_id',type:scalar()},{name:'amount',type:scalar('UInt64')},{name:'replacement',type:named('account')},{name:'receipt',type:named('receipt')},{name:'response',type:scalar()}],
    reads:[{slot:'current-account',target:'commerce:account',parameter:'current',key:at('account_id')}],
    guards:[{selector:'commerce:can-post',arguments:[arg('current',at('current')),arg('amount',at('amount'))]},{selector:'commerce:receipt-matches',arguments:[arg('expected',at('amount')),arg('actual',at('receipt','FIXTURE-RECEIPT#amount'))]}],
    writes:[{slot:'account-state',target:'commerce:account',mode:'replace',value:at('replacement')},{slot:'receipt-state',target:'commerce:receipt',mode:'create',value:at('receipt')}],
    events:[{slot:'posted-fact',target:'commerce:posted',parameter:'posted_input'},{slot:'audit-fact',target:'commerce:posted',parameter:'audit_input'}],result:{type:scalar(),value:at('response')},atomicity:'state-and-outbox',continuation:'awaited-settlement'};
  const factories=['account','receipt','detail'].map(id=>({selector:'commerce:'+id,base_validators:[{rule:'commerce:positive',arguments:[{parameter:'amount',field:id==='account'?'balance':'amount'}]}],extensions:[]}));
  const compile=()=>{
    const graph=loadCompiledProjectGraph(source),certificate=createCompiledProjectCertificate(graph),boundary=compileCompositionBoundary(graph,{schema_version:COMPOSITION_BOUNDARY_VERSION,contract_sha256:COMPOSITION_BOUNDARY_CONTRACT_SHA256,graph_sha256:certificate.graph_sha256},boundarySource);
    const fields=compileSelectedProjectFields(graph,{schema_version:EXACT_PROJECT_FIELD_SELECTION_VERSION,contract_sha256:EXACT_FIELD_CONTRACT_SHA256,graph_sha256:certificate.graph_sha256,roots:['commerce:account','commerce:receipt'],bindings:[]},rules.field_contract);
    const action=compileOperationActionBindings(graph,boundary,fields,bindings,actionSource),selection:any={schema_version:CONFIGURED_OPERATION_VERSION,language:'typescript',module_root:'application',actions:[action],factories};
    return {graph,boundary,fields,action,selection,plan:()=>planConfiguredOperations(graph,boundary,fields,selection,sources)};
  };
  return {temp,source,write,node,edge,save,bindings,factories,compile,...compile()};
}
const account=(balance:any='100')=>({id:'account-a',balance,detail:{amount:'2'},labels:['b','a'],status:{variant:'Ready'},choice:{variant:'Some',payload:{amount:'3'}}});
const input=()=>({account_id:'account-a',amount:'10',replacement:account('90'),receipt:{id:'receipt-a',amount:'10'},response:'accepted',posted_input:{occurrence:{'occurrence-id':'one'},payload:{'account-id':'account-a',amount:'10'}},audit_input:{occurrence:{'occurrence-id':'two'},payload:{'account-id':'account-a',amount:'10'}}});
function native(root:string,plan:any){
  for(const a of plan.artifacts){const p=path.join(root,a.relative_path);fs.mkdirSync(path.dirname(p),{recursive:true});fs.writeFileSync(p,a.content);}
  const chain=read(path.resolve(project,'../../toolchains/node-typescript/toolchain.json')),image=nativeToolchainImage(chain.container_image);
  const docker=['run','--rm','--pull','never','--network','none','--read-only','--cap-drop','ALL','--security-opt','no-new-privileges','--user',process.getuid!()+':'+process.getgid!(),'--mount','type=bind,source='+root+',target='+root,'--workdir',root,image];
  const compile=()=>execFileSync('docker',[...docker,'tsc','--ignoreConfig','--strict','--skipLibCheck','--declaration','--target','ES2022','--module','commonjs','--rootDir',root,'--outDir',path.join(root,'js'),...plan.artifacts.map((a:any)=>path.join(root,a.relative_path))],{encoding:'utf8'});compile();
  const m=plan.modules[0],js=path.join(root,'js',m.relative_path.replace(/\.ts$/,'.js')),load=()=>createRequire(import.meta.url)(js)[m.callable];
  return {root,plan,compile,load,docker,image,js,module:m};
}

import {publicSelection} from '../helpers/composition-project.ts';
import {planCompiledReconciledProject} from '../../src/generation/reconciled-project.ts';
import {createOperationBinding} from '../../src/verification/reconciled-operation-binding.ts';
import {createOperationCases} from '../../src/verification/reconciled-operation-cases.ts';
import {OPERATION_SEMANTIC_RUNNER} from '../../src/verification/reconciled-operation-runner.ts';
import {pathToFileURL} from 'node:url';
import {createOperationControls,createOperationEffectAudit} from '../../src/verification/reconciled-operation-controls.ts';
import {SEMANTIC_RUNNER,createReconciledSemanticControls} from '../../src/verification/reconciled-semantic-controls.ts';
import {workflowFixture} from '../helpers/workflow-verification.ts';
import {mixedWorkflowPublicFixture} from '../helpers/workflow-public-mixed.ts';

// Complete source-bound successor digests after typed Event materialization.
// Historical optimization/selection diagnostics are not current qualification.
// These are preservation controls, not replacements for independent native tests.
test('Operation preparation preserves every scalar and nested case byte',t=>{
 for(const [make,counts,digest] of [
  [workflowFixture,[64,64],'2ab3054bf0dfdc4f22724869e7f53511f3e20456592551f2e5036f9dc47a5e52'],
  [mixedWorkflowPublicFixture,[1810,1813,1810,1813],'fcf43890242d5fe1a87b73536aca7c224a31282b0767a2fd2ce6ae006bd0cb50']
 ] as const){
  const f=make(t),plan=planCompiledReconciledProject(f.graph,f.selection);
  const rows=f.graph.nodes.filter(n=>n.kind==='Operation').map(n=>createOperationCases(f.graph,plan,createOperationBinding(n,f.graph,plan)));
  assert.deepEqual(rows.map(r=>r.cases.length),counts);
  assert.equal(sha256(canonicalJson(rows)),digest);
 }
});
test('Operation preparation preserves multi-input, guard rejection, read/write and capacity cases',t=>{
 const multi=simpleFixture(t,1),effectful=fixture(t);
 const rows=[
  {graph:multi.graph,plan:multi.plan,count:166,digest:'9cced559ea294a26ad730f5df2e5e394e859db34a1f8412dc90a89e942c2fdae'},
  {graph:effectful.graph,plan:publicPlan(effectful),count:1903,digest:'a0be2819f1eaa590dbf56d0840f7d6c383d474c1ff46bcbf28af426dffdd2d49'}
 ];
 for(const {graph,plan,count,digest}of rows){
  const binding=createOperationBinding(graph.nodes.find(n=>n.kind==='Operation')!,graph,plan),cases=createOperationCases(graph,plan,binding);
  assert.equal(cases.cases.length,count);assert.equal(sha256(canonicalJson(cases)),digest);
 }
 const bounded=simpleFixture(t,127),binding=createOperationBinding(bounded.graph.nodes.find(n=>n.kind==='Operation')!,bounded.graph,bounded.plan);
 assert.throws(()=>createOperationCases(bounded.graph,bounded.plan,binding),{message:'bounded Operation serialized cases exceed 8 MiB'});
});
test('shared native imports permit duplicate type/value targets but reject conflicting resolutions',t=>{
 const temp=fs.mkdtempSync(path.join(os.tmpdir(),'ds-operation-imports-'));t.after(()=>fs.rmSync(temp,{recursive:true,force:true}));
 fs.writeFileSync(path.join(temp,'package.json'),'{"type":"module"}');
 fs.writeFileSync(path.join(temp,'shared.js'),'export const value=1;');
 fs.writeFileSync(path.join(temp,'root.js'),'import {value} from "./shared.js";export const operation=()=>value;');
 const script=path.join(temp,'runner.mjs'),file=path.join(temp,'cases.json');fs.writeFileSync(script,SEMANTIC_RUNNER);
 const edge={specifier:'./shared.js',target_path:'shared.ts'},row={selector:'alpha:one',adapter:'operation',relative_path:'root.ts',callable:'operation',recipes:[],cases:[],native_imports:[{relative_path:'root.ts',imports:[edge,edge]},{relative_path:'shared.ts',imports:[]}]};
 const run=(rows:any[])=>{fs.writeFileSync(file,JSON.stringify({rows}));return execFileSync(process.execPath,[script,file,temp],{encoding:'utf8',stdio:['ignore','pipe','pipe']});};
 assert.deepEqual(JSON.parse(run([row,{...row,selector:'alpha:two',native_imports:[{relative_path:'shared.ts',imports:[]},{relative_path:'root.ts',imports:[edge]}]}])),[{selector:'alpha:one',cases:[]},{selector:'alpha:two',cases:[]}]);
 const conflicting={...edge,target_path:'other.ts'};
 assert.throws(()=>run([{...row,native_imports:[{relative_path:'root.ts',imports:[edge,conflicting]}]}]),/SEMANTIC_NATIVE_IMPORT_CONFLICT/);
 assert.throws(()=>run([row,{...row,selector:'alpha:two',native_imports:[{relative_path:'root.ts',imports:[conflicting]}]}]),/SEMANTIC_NATIVE_IMPORT_CONFLICT/);
});
function simpleFixture(t:any,extra=0){
 const temp=fs.mkdtempSync(path.join(os.tmpdir(),'ds-operation-controls-'));t.after(()=>fs.rmSync(temp,{recursive:true,force:true}));
 const source=path.join(temp,'source'),write=(p:string,v:any)=>{const f=path.join(source,p);fs.mkdirSync(path.dirname(f),{recursive:true});fs.writeFileSync(f,JSON.stringify(v));};
 write('project.json',{schema_version:'domainspec.project/v1',project_id:'operation-controls',features:['alpha'],cross_feature_edges:[]});
 write('specs/alpha/feature.json',{schema_version:'domainspec.feature/v1',feature_id:'alpha',nodes:['positive','perform'],edges:['positive-enforces-perform']});
 write('specs/alpha/nodes/positive.json',{schema_version:'domainspec.node/v1',feature_id:'alpha',node_id:'positive',kind:'Rule',body:{description:'positive',predicate:'structured:domainspec.typed-rule/v2',typed_contract:{schema_version:'domainspec.typed-rule/v2',ontology_rule:'TEST-POSITIVE',parameters:[{name:'amount',type:scalar('UInt64')}],expression:{op:'lt',left:lit('UInt64','0'),right:at('amount')}}}});
 write('specs/alpha/nodes/perform.json',{schema_version:'domainspec.node/v1',feature_id:'alpha',node_id:'perform',kind:'Operation',body:{description:'perform',reads:[],writes:[],effects:[],guard:'positive',failure_continuation:'return-error'}});
 write('specs/alpha/edges/positive-enforces-perform.json',{schema_version:'domainspec.edge/v1',feature_id:'alpha',edge_id:'positive-enforces-perform',relationship:'enforces',source_node_id:'positive',target_node_id:'perform',scope:'feature'});
 const binding={...publicSelection().operations[0],inputs:[{name:'amount',type:scalar('UInt64')},...Array.from({length:extra},(_,i)=>({name:'field_'+i,type:scalar()}))],guards:[{selector:'alpha:positive',arguments:[arg('amount',at('amount'))]}]};
 const selection={...publicSelection(),factories:[],operations:[binding]},graph=loadCompiledProjectGraph(source),plan=planCompiledReconciledProject(graph,selection);
 return {temp,source,selection,graph,plan};
}
test('Operation capacities retain the whole node as not_evaluable without dropping source audits',t=>{
 const f=simpleFixture(t,127),node=f.graph.nodes.find(n=>n.kind==='Operation')!,row=createOperationControls(node,f.graph,f.plan),audit=createOperationEffectAudit(f.graph,f.plan);
 assert.equal(row.state,'not_evaluable',JSON.stringify(row).slice(0,1000));
 assert.equal('cases' in row,false);assert.match((row as any).reason,/capacity|8 MiB/);
 assert.deepEqual(audit.roots,['alpha:perform']);assert.ok(audit.module_paths.some(p=>p.endsWith('perform.provider.ts')));
});
test('project Operation capacity retains every source node and audits rejected whole closures',t=>{
 const f=fixture(t),operations=[f.bindings],factories=[...f.factories],features=['commerce','commerce-two','commerce-three'];
 for(const feature of features.slice(1)){
  const copy=(v:any)=>JSON.parse(JSON.stringify(v).replaceAll('commerce:',feature+':').replaceAll('FIXTURE-',feature.toUpperCase()+'-FIXTURE-'));
  for(const kind of ['nodes','edges'])for(const file of fs.readdirSync(path.join(f.source,'specs/commerce',kind))){const node=copy(read(path.join(f.source,'specs/commerce',kind,file)));node.feature_id=feature;if(kind==='edges')node.edge_id=feature+'-'+node.edge_id;f.write('specs/'+feature+'/'+kind+'/'+(kind==='edges'?node.edge_id+'.json':file),node);}
  const manifest=read(path.join(f.source,'specs/commerce/feature.json'));manifest.feature_id=feature;manifest.edges=manifest.edges.map((id:string)=>feature+'-'+id);f.write('specs/'+feature+'/feature.json',manifest);
  operations.push(copy(f.bindings));factories.push(...copy(f.factories));
 }
 const projectFile=read(path.join(f.source,'project.json'));projectFile.features=features;f.write('project.json',projectFile);
 const graph=loadCompiledProjectGraph(f.source),plan=planCompiledReconciledProject(graph,{...publicSelection('application'),factories,operations}),controls=createReconciledSemanticControls(graph,plan),rows=controls.rows.filter(r=>r.kind==='Operation'),audit=createOperationEffectAudit(graph,plan);
 assert.equal(rows.length,3);assert.equal(controls.node_count,graph.nodes.length);
 assert.ok(rows.some(r=>r.state==='ready'));assert.ok(rows.some(r=>r.state==='not_evaluable'));
 for(const row of rows)if(row.state==='not_evaluable'){assert.match(row.reason,/bounded semantic case capacity/);assert.equal('cases' in row,false);assert.ok(audit.module_paths.some(p=>p.includes('/features/'+row.selector.split(':')[0]+'/')&&p.endsWith('/post.provider.ts')));}
 assert.deepEqual(audit.roots,rows.map(r=>r.selector).sort());
 assert.equal(controls.case_count,controls.rows.reduce((total,r)=>total+(r.state==='ready'?r.cases.length:0),0));
 assert.ok(Buffer.byteLength(canonicalJson(controls.rows.filter(r=>r.state==='ready')))<8388608);
});
test('public Operation controls support Enum-only owned results without a dummy record or factory',t=>{
 const f=simpleFixture(t),feature=path.join(f.source,'specs/alpha/feature.json'),manifest=read(feature);manifest.nodes.push('status');fs.writeFileSync(feature,JSON.stringify(manifest));
 fs.writeFileSync(path.join(f.source,'specs/alpha/nodes/status.json'),JSON.stringify({schema_version:'domainspec.node/v1',feature_id:'alpha',node_id:'status',kind:'Enum',body:{description:'status',values:['None','Some'],typed_contract:{schema_version:'domainspec.typed-sum/v1',ontology_node:'TEST-STATUS',variants:[{name:'None',ontology_variant:'TEST-STATUS#None',payload:null},{name:'Some',ontology_variant:'TEST-STATUS#Some',payload:scalar('UInt64')}]}}}));
 const type={kind:'named',selector:'alpha:status'},operation=f.selection.operations[0],selection={...f.selection,operations:[{...operation,inputs:[...operation.inputs,{name:'status',type}],result:{type,value:at('status')}}]},n=nativeContext(f);
 const result=n.run(`import cp from 'node:child_process';import {syncBuiltinESMExports} from 'node:module';import {loadCompiledProjectGraph,planCompiledReconciledProject,executeReconciledVerification} from './dist/index.js';
 const graph=loadCompiledProjectGraph(${JSON.stringify(f.source)}),plan=planCompiledReconciledProject(graph,${JSON.stringify(selection)}),tools=${JSON.stringify(n.options)},original=cp.spawnSync;
 cp.spawnSync=(command,args,settings)=>command===tools.lean_executable?{status:1,stdout:'',stderr:'isolated Enum-only semantic coverage; not Lean evidence'}:original(command,args,settings);syncBuiltinESMExports();
 try{console.log(JSON.stringify({kinds:graph.nodes.map(n=>n.kind),report:executeReconciledVerification(graph,plan,tools)}));}finally{cp.spawnSync=original;syncBuiltinESMExports();}`);
 assert.equal(result.kinds.some((k:string)=>['Entity','Value Object'].includes(k)),false);
 for(const id of ['operation-source-effect-audit','operation-native-effect-audit','operation-effect-audit-currentness','selected-generator-semantic-controls','verification-workspace-cleanup'])assert.equal(result.report.checks.find((c:any)=>c.id===id)?.result,'pass',JSON.stringify(result.report.checks));
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
 const run=(body:string)=>{const file=path.join(f.temp,'client.mjs');fs.writeFileSync(file,body);try{return JSON.parse(execFileSync('docker',[...docker,'node',file],{encoding:'utf8',timeout:600000,maxBuffer:32*1024*1024}));}catch(e:any){throw Error(String(e.code??'')+':'+String(e.stdout)+String(e.stderr));}};
 return {run,options};
}
test('public verification runs effectful Operation controls with source and native audit custody',t=>{
 const f=fixture(t),n=nativeContext(f),selection={...publicSelection('application'),factories:f.factories,operations:[f.bindings]};
 const result=n.run(`import {loadCompiledProjectGraph,planCompiledReconciledProject,executeReconciledVerification} from './dist/index.js';
 const graph=loadCompiledProjectGraph(${JSON.stringify(f.source)}),plan=planCompiledReconciledProject(graph,${JSON.stringify(selection)});
 console.log(JSON.stringify(executeReconciledVerification(graph,plan,${JSON.stringify(n.options)})));`);
 for(const id of ['operation-source-effect-audit','operation-native-effect-audit','operation-effect-audit-currentness','selected-generator-semantic-controls','verification-workspace-cleanup'])assert.equal(result.checks.find((c:any)=>c.id===id)?.result,'pass',JSON.stringify(result.checks.filter((c:any)=>c.result!=='pass')));
 t.diagnostic(JSON.stringify({checks:result.checks.length,operation_cases:result.checks.find((c:any)=>c.id==='selected-generator-semantic-controls').evidence.tested?.find((n:any)=>n.kind==='Operation')?.case_count}));
});
function publicPlan(f:ReturnType<typeof fixture>,root='application'){
 return planCompiledReconciledProject(f.graph,{...publicSelection(root),factories:f.factories,operations:[f.bindings]});
}
test('Operation public controls reject compiling behavior, binding, effects and audit custody mutations',t=>{
 const f=simpleFixture(t),n=nativeContext(f),reports=n.run(`import fs from 'node:fs';import path from 'node:path';import cp from 'node:child_process';import {syncBuiltinESMExports} from 'node:module';
 import {loadCompiledProjectGraph,planCompiledReconciledProject,executeReconciledVerification} from './dist/index.js';
 const source=${JSON.stringify(f.source)},selection=${JSON.stringify(f.selection)},tools=${JSON.stringify(n.options)},original=cp.spawnSync,reports=[];
 for(const mode of ['clean','result','guard','commit-await','descriptor','static-import','date','class','object-write','dynamic-import','source-date','source-omit','native-phase','native-hash','source-script','native-script','native-input','late-audit','late-module']){
  let calls=0,script='',changed=false;
  cp.spawnSync=(command,args,settings)=>{
   if(command===tools.lean_executable)return {status:1,stdout:'',stderr:'isolated Operation mutation; not Lean evidence'};
   if(args.includes('--permission'))calls++;
   const config=args[args.indexOf('--project')+1],provider='domain/features/alpha/src/application/operations/perform.provider';
   if(mode==='source-date'&&args.includes('--project')&&String(config).endsWith('/native/tsconfig.json')){fs.appendFileSync(path.join(path.dirname(config),provider+'.ts'),'\\nvoid Date.now();\\n');changed=true;}
   const result=original(command,args,settings);
   if(result.status===0&&args.includes('--project')&&String(config).endsWith('/semantic/compiler.json')&&['result','guard','commit-await','descriptor','static-import','date','class','object-write','dynamic-import'].includes(mode)){
    let file=path.join(path.dirname(config),'modules',provider+'.js');if(mode==='descriptor')file=file.replace('.provider.js','.js');
    const old=fs.readFileSync(file,'utf8');let next=old;
    if(mode==='result')next=old.replace('value: result','value: 0n');
    if(mode==='guard')next=old.replace(/if \\(!guard0\\(/,'if (false && !guard0(');
    if(mode==='commit-await')next=old.replace('await transaction.commit(batch)','transaction.commit(batch)');
    if(mode==='descriptor')next=old.replace('awaited-explicit-outcome','unawaited-outcome');
    if(mode==='static-import')next=old+'\\nimport "node:fs";\\n';
    if(mode==='date')next=old+'\\nvoid Date.now();\\n';
    if(mode==='class')next=old+'\\nclass UnexpectedDomainClass {}\\n';
    if(mode==='object-write')next=old+'\\nObject["defineProperty"]({},"leak",{value:1});\\n';
    if(mode==='dynamic-import')next=old+'\\nimport("node:fs").catch(()=>{});\\n';
    if(next===old)throw Error('Operation mutant not installed:'+mode);changed=true;fs.writeFileSync(file,next);
    const syntax=original(process.execPath,['--check',file],{encoding:'utf8',timeout:60000});if(syntax.status!==0)throw Error('Operation mutant syntax:'+mode+':'+syntax.stderr);
   }
   const audit=args.find(a=>String(a).endsWith('/operation-effects.mjs'));
   if(audit&&result.status===0){
    script=audit;const o=JSON.parse(result.stdout);
    if(mode==='source-omit'&&o.phase==='source'){o.modules.pop();result.stdout=JSON.stringify(o);changed=true;}
    if(mode==='native-phase'&&o.phase==='native'){o.phase='source';result.stdout=JSON.stringify(o);changed=true;}
    if(mode==='native-hash'&&o.phase==='native'){o.modules[0].source_sha256='0'.repeat(64);result.stdout=JSON.stringify(o);changed=true;}
    if(mode===o.phase+'-script'){fs.appendFileSync(audit,'\\n// changed\\n');changed=true;}
    if(mode==='native-input'&&o.phase==='native'){const input=args.find(a=>String(a).endsWith('.json'));fs.appendFileSync(input,' ');changed=true;}
   }
   if(args.includes('--permission')&&result.status===0){
    if(mode==='late-audit'){fs.appendFileSync(script,'\\n// late drift\\n');changed=true;}
    if(mode==='late-module'){fs.appendFileSync(path.join(settings.cwd,'modules',provider+'.js'),' ');changed=true;}
   }
   return result;
  };syncBuiltinESMExports();
  try{const graph=loadCompiledProjectGraph(source),plan=planCompiledReconciledProject(graph,selection),report=executeReconciledVerification(graph,plan,tools);reports.push({mode,report,calls,changed});}finally{cp.spawnSync=original;syncBuiltinESMExports();}
 }console.log(JSON.stringify(reports));`);
 for(const {mode,report,calls,changed} of reports){
  const check=(id:string)=>report.checks.find((c:any)=>c.id===id),semantic=check('selected-generator-semantic-controls');
  assert.ok(mode==='clean'||changed,'mutation reached: '+mode);
  if(mode==='clean'){assert.equal(semantic.result,'pass',JSON.stringify(semantic));assert.ok(calls>0);}
  else if(['result','guard','commit-await','descriptor','static-import'].includes(mode)){assert.equal(semantic.result,'fail',mode+':'+JSON.stringify(semantic));assert.ok(calls>0,mode);assert.match(semantic.reason,mode==='static-import'?/OPERATION_NATIVE_IMPORT_BOUNDARY/:mode==='commit-await'?/observation mismatch|semantic process rejected[\s\S]*fixture-commit/:/observation mismatch/,mode);}
  else if(['date','class','object-write','dynamic-import'].includes(mode)){assert.equal(check('operation-native-effect-audit').result,'fail',mode);assert.equal(calls,0,mode);}
  else if(mode==='late-audit'){assert.ok(calls>0);assert.equal(check('operation-effect-audit-currentness').result,'fail');for(const id of ['operation-source-effect-audit','operation-native-effect-audit','selected-generator-semantic-controls'])assert.equal(check(id).result,'not_evaluable',id);}
  else if(mode==='late-module'){assert.ok(calls>0);assert.equal(check('semantic-workspace-currentness').result,'fail');assert.equal(semantic.result,'not_evaluable');}
  else{assert.equal(calls,0,mode);assert.equal(check(mode.startsWith('source')?'operation-source-effect-audit':'operation-native-effect-audit').result,'fail',mode);}
  assert.equal(check('verification-workspace-cleanup').result,'pass',mode);
 }
 t.diagnostic('18 altered programs/evidence cases rejected; clean semantic control passed. Lean intentionally isolated.');
});
test('Operation Enum support exceptions retain exact source pins and native audit currentness',t=>{
 const f=fixture(t),n=nativeContext(f),selection={...publicSelection('application'),factories:f.factories,operations:[f.bindings]},reports=n.run(`import fs from 'node:fs';import path from 'node:path';import cp from 'node:child_process';import {syncBuiltinESMExports} from 'node:module';
 import {loadCompiledProjectGraph,planCompiledReconciledProject,executeReconciledVerification} from './dist/index.js';
 const source=${JSON.stringify(f.source)},selection=${JSON.stringify(selection)},tools=${JSON.stringify(n.options)},original=cp.spawnSync,reports=[];
 for(const mode of ['source-pin','native-class','late-support']){
  let calls=0,changed=false;cp.spawnSync=(command,args,settings)=>{
   if(command===tools.lean_executable)return {status:1,stdout:'',stderr:'isolated Operation support audit; not Lean evidence'};
   const config=args[args.indexOf('--project')+1];if(args.includes('--permission'))calls++;
   if(mode==='source-pin'&&args.includes('--project')&&String(config).endsWith('/native/tsconfig.json')){fs.appendFileSync(path.join(path.dirname(config),'application/runtime/enum.ts'),' ');changed=true;}
   const result=original(command,args,settings);
   if(mode==='native-class'&&result.status===0&&args.includes('--project')&&String(config).endsWith('/semantic/compiler.json')){fs.appendFileSync(path.join(path.dirname(config),'modules/application/runtime/enum.js'),'\\nclass UnselectedSupportClass {}\\n');changed=true;}
   if(mode==='late-support'&&args.includes('--permission')&&result.status===0){fs.appendFileSync(path.join(settings.cwd,'modules/application/runtime/enum.js'),' ');changed=true;}
   return result;
  };syncBuiltinESMExports();
  try{const graph=loadCompiledProjectGraph(source),plan=planCompiledReconciledProject(graph,selection),report=executeReconciledVerification(graph,plan,tools);reports.push({mode,report,calls,changed});}finally{cp.spawnSync=original;syncBuiltinESMExports();}
 }console.log(JSON.stringify(reports));`);
 for(const {mode,report,calls,changed} of reports){
  assert.ok(changed,mode);const check=(id:string)=>report.checks.find((c:any)=>c.id===id);
  if(mode==='late-support'){assert.ok(calls>0);assert.equal(check('semantic-workspace-currentness').result,'fail');assert.equal(check('operation-native-effect-audit').result,'not_evaluable');assert.equal(check('selected-generator-semantic-controls').result,'not_evaluable');}
  else{assert.equal(calls,0);assert.equal(check(mode==='source-pin'?'operation-source-effect-audit':'operation-native-effect-audit').result,'fail',mode);}
  assert.equal(check('verification-workspace-cleanup').result,'pass');
 }
});
test('source-derived Operation cases execute through the data-only semantic adapter',async t=>{
 const f=fixture(t),plan=publicPlan(f),binding=createOperationBinding(f.graph.nodes.find(n=>n.kind==='Operation')!,f.graph,plan),controls=createOperationCases(f.graph,plan,binding);
 const n=native(f.temp,{...f.plan(),artifacts:plan.resolved.artifacts}),row={selector:'commerce:post',...binding,...controls,cases:[{id:'binding',mode:'operation-descriptor',format:'string',values:[],expected:{kind:'value',value:canonicalJson(binding.descriptor)}},...controls.cases]};
 const p=path.join(f.temp,'semantic.mjs');fs.writeFileSync(p,`import {pathToFileURL} from 'node:url';import path from 'node:path';const enumImport=p=>import(pathToFileURL(path.join(${JSON.stringify(path.join(n.root,'js'))},p.replace(/\\.ts$/,'.js'))).href);\n`+OPERATION_SEMANTIC_RUNNER+'\nexport {observeOperation};');
 const {observeOperation}=await import(pathToFileURL(p).href),observed=await observeOperation(row);
 assert.deepEqual(observed,{selector:row.selector,cases:row.cases.map(c=>({id:c.id,outcome:c.expected,getter_reads:0,input_changed:false}))});
 assert.ok(controls.cases.length>50);t.diagnostic(JSON.stringify({cases:row.cases.length,recipes:row.recipes.length,serialized_bytes:Buffer.byteLength(canonicalJson(row))}));
});
test('Operation binding reconstructs exact native descriptor and restricts actual selected dependency closure',t=>{
 const f=fixture(t),plan=publicPlan(f),node=f.graph.nodes.find(n=>n.kind==='Operation')!,binding=createOperationBinding(node,f.graph,plan);
 const n=native(f.temp,{...f.plan(),artifacts:plan.resolved.artifacts}),fn=n.load();
 assert.deepEqual(fn.descriptor,binding.descriptor);
 assert.equal(binding.module_paths.includes('application/runtime/enum.ts'),true);
 assert.equal(binding.native_imports.length,binding.module_paths.length);
 assert.ok(binding.native_imports.every(m=>m.imports.every(i=>binding.module_paths.includes(i.target_path))));
 assert.throws(()=>createOperationBinding(node,f.graph,structuredClone(plan)),/registered reconciled project required/);
 assert.throws(()=>createOperationBinding({...node},f.graph,plan),/source Operation required/);
 const again=createOperationBinding(node,f.graph,plan);assert.deepEqual(again,binding);
});
test('Operation bindings retain relocated paths and source-dependent exact metadata',t=>{
 const f=fixture(t),plan=publicPlan(f,'relocated/domain'),binding=createOperationBinding(f.graph.nodes.find(n=>n.kind==='Operation')!,f.graph,plan);
 assert.ok(binding.module_paths.every(p=>p.startsWith('relocated/domain/')));
 assert.equal(binding.descriptor.provider_durability_claim,false);
 assert.equal(binding.descriptor.publication,false);
 assert.equal(binding.descriptor.bindings.events.length,2);
 const p='specs/commerce/nodes/posted.json',event=read(path.join(f.source,p));event.body.version='2';f.write(p,event);
 const next={...f,...f.compile()},nextPlan=publicPlan(next,'relocated/domain'),changed=createOperationBinding(next.graph.nodes.find(n=>n.kind==='Operation')!,next.graph,nextPlan);
 assert.notEqual(changed.descriptor.event_plan_sha256,binding.descriptor.event_plan_sha256);
 assert.notEqual(changed.descriptor.action_sha256,binding.descriptor.action_sha256);
 assert.throws(()=>createOperationBinding(next.graph.nodes.find(n=>n.kind==='Operation')!,next.graph,plan),/cross-graph plan/);
});

import {nativeToolchainImage, NATIVE_TEST_IMAGE_ID} from '../helpers/native-toolchain-image.ts';
