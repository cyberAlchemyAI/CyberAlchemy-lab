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
function queryFixture(t:any,moduleRoot='domain',minimal=false){
 const temp=fs.mkdtempSync(path.join(os.tmpdir(),'ds-interface-controls-')),source=path.join(temp,'source'),nodes:string[]=[],edges:string[]=[],contracts:any={};
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

const local=(contract_id:string):any=>({kind:'contract',contract_id});
const publicField=(name:string,type:any):any=>({name,type,ontology_field:'TEST-PUBLIC#'+name,meaning:name});
function interfaceContract(mode='backward',version='1.2.3'):any{
 const response={contract_id:'response',ontology_contract:'TEST-RESPONSE',fields:[publicField('id',scalar()),publicField('count',scalar('UInt64')),publicField('memo',wrap('optional',scalar()))]};
 return {schema_version:'domainspec.typed-interface/v1',ontology_interface:'TEST-API',boundary_kind:'external',version_policy:{schema_version:'domainspec.interface-version-policy/v1',mode,direction:'consumer-to-provider',provider_version:version},
 contracts:[{contract_id:'request',ontology_contract:'TEST-REQUEST',fields:[publicField('id',scalar())]},response,{...structuredClone(response),contract_id:'shadow',ontology_contract:'TEST-SHADOW'},{contract_id:'empty',ontology_contract:'TEST-EMPTY',fields:[]}],
 operations:[{operation_id:'find',operation_ref:'alpha:all',request:local('request'),result:wrap('optional',local('response'))}]};
}
function fixture(t:any,moduleRoot='domain',single=false){
 const f=queryFixture(t,moduleRoot,true);
 const api=(id:string,c:any)=>{const query=id+'-find';f.node(query,'Query',{reads:['alpha:row'],typed_contract:f.contracts.all});f.edge(query,'reads','row');c.operations=c.operations.map((o:any)=>({...o,operation_ref:'alpha:'+query}));f.node(id,'Interface',{typed_contract:c});f.edge(id,'exposes',query);};
 api('api',interfaceContract());if(!single){api('exact',interfaceContract('exact','9007199254740993123.99999999999999999999.2'));api('zero',interfaceContract('backward','0.2.3'));}
 f.save();const graph=loadCompiledProjectGraph(f.source),plan=planCompiledReconciledProject(graph,f.selection);return {...f,api,graph,plan};
}
test('Interface source controls preserve every public and endpoint protocol, qualified identities and relocated signatures',t=>{
 const f=fixture(t),controls=createReconciledSemanticControls(f.graph,f.plan),rows=controls.rows.filter(r=>r.kind==='Interface') as any[];
 assert.equal(rows.length,3);assert.equal(controls.not_evaluable_count,0,JSON.stringify(controls.rows.filter(r=>r.state==='not_evaluable')));
 for(const r of rows){assert.equal(r.state,'ready',r.reason);assert.equal(r.module_paths.length,1);assert.equal(r.native_imports[0].imports.length,0);assert.ok(r.cases.some((c:any)=>c.mode==='interface-version'));assert.ok(r.cases.some((c:any)=>c.expected.kind==='error'));assert.match(r.signature_source,/ExpectedInterface/);}
 const other=fixture(t,'relocated/root'),moved=createReconciledSemanticControls(other.graph,other.plan);
 for(const r of rows)assert.deepEqual(r.cases.filter((c:any)=>c.mode==='interface-value'||c.mode==='interface-version'),(moved.rows.find(x=>x.selector===r.selector) as any).cases.filter((c:any)=>c.mode==='interface-value'||c.mode==='interface-version'));
 const api=rows.find(r=>r.selector==='alpha:api'),normal=api.cases.filter((c:any)=>c.mode==='interface-value'&&c.expected.kind==='value'),response=normal.find((c:any)=>c.values[1]==='public'&&c.values[2]==='response'),shadow=normal.find((c:any)=>c.values[1]==='public'&&c.values[2]==='shadow');
 assert.deepEqual(JSON.parse(response.expected.value).normalized,JSON.parse(shadow.expected.value).normalized);assert.notEqual(JSON.parse(response.expected.value).key,JSON.parse(shadow.expected.value).key);
});
test('native public verification checks Interface values, versions, structural signatures and independent source/native audit custody',t=>{
 const f=fixture(t),n=nativeContext(f),report=n.run(`import fs from 'node:fs';import cp from 'node:child_process';import {syncBuiltinESMExports} from 'node:module';import {isDeepStrictEqual} from 'node:util';
 import {loadCompiledProjectGraph,planCompiledReconciledProject,executeReconciledVerification} from './dist/index.js';
 const graph=loadCompiledProjectGraph(${JSON.stringify(f.source)}),plan=planCompiledReconciledProject(graph,${JSON.stringify(f.selection)}),original=cp.spawnSync;let mismatch=null;
 cp.spawnSync=(command,args,settings)=>{const result=original(command,args,settings);if(args.includes('--permission')&&result.status===0){const planned=JSON.parse(fs.readFileSync(args.find(a=>String(a).endsWith('/cases.json')),'utf8')),actual=JSON.parse(result.stdout);for(const r of planned.rows){for(const c of r.cases){const a=actual.find(a=>a.selector===r.selector)?.cases.find(a=>a.id===c.id);if(!isDeepStrictEqual(c.expected,a?.outcome)){mismatch={selector:r.selector,case:c,actual:a};break;}}if(mismatch)break;}}return result;};syncBuiltinESMExports();
 const report=executeReconciledVerification(graph,plan,${JSON.stringify(n.options)});cp.spawnSync=original;syncBuiltinESMExports();console.log(JSON.stringify({report,mismatch}));`);
 const check=(id:string)=>report.report.checks.find((c:any)=>c.id===id),semantic=check('selected-generator-semantic-controls');
 assert.equal(report.mismatch,null,JSON.stringify(report.mismatch));assert.equal(semantic.result,'pass',JSON.stringify(semantic));assert.equal(semantic.evidence.interface_signature_count,3);assert.equal(semantic.evidence.remaining.length,0);
 for(const phase of ['source','native']){assert.equal(check('interface-'+phase+'-effect-audit').result,'pass',JSON.stringify(check('interface-'+phase+'-effect-audit')));assert.equal(check('interface-'+phase+'-effect-audit').evidence.selectors.length,3);}
 assert.equal(check('interface-effect-audit-currentness').result,'pass');assert.equal(check('verification-workspace-cleanup').result,'pass');
});

test('compiling Interface value, identity, version and binding mutants, effects and signature drift cannot pass',t=>{
 const f=fixture(t,'domain',true),n=nativeContext(f),reports=n.run(`import fs from 'node:fs';import path from 'node:path';import cp from 'node:child_process';import {syncBuiltinESMExports} from 'node:module';
 import {loadCompiledProjectGraph,planCompiledReconciledProject,executeReconciledVerification} from './dist/index.js';
 const source=${JSON.stringify(f.source)},selection=${JSON.stringify(f.selection)},tools=${JSON.stringify(n.options)},original=cp.spawnSync,reports=[];
 for(const mode of ['field','primitive','omit','extra','mutable','alias','key','identity','optional','validation','endpoint','surface-omit','surface-freeze','version-all','version-none','version-major','version-coercion','binding-source','binding-field','binding-contract','binding-effect','binding-freeze','binding-cycle','version-descriptor','static-import','caught-import','global','prototype','object-write','source-global','signature-type','signature-readonly','signature-erasure','signature-config','late-signature','late']){
  let calls=0,signatureCalls=0,signatureResult=null;
  cp.spawnSync=(command,args,settings)=>{
   if(command===tools.lean_executable)return {status:1,stdout:'',stderr:'isolated Interface mutation'};
   if(args.includes('--permission'))calls++;const config=args[args.indexOf('--project')+1];
   if(mode==='source-global'&&args.includes('--project')&&String(config).endsWith('/native/tsconfig.json'))fs.appendFileSync(path.join(path.dirname(config),'domain/features/alpha/src/application/interfaces/api.ts'),'\\nvoid Date.now();\\n');
   const signature=args.includes('--project')&&String(config).endsWith('/semantic/signatures.json');
   if(signature){
    signatureCalls++;const base=path.dirname(config),file=path.join(base,'../native/domain/features/alpha/src/application/interfaces/api.ts');
    if(mode==='signature-type'){const s=fs.readFileSync(file,'utf8');fs.writeFileSync(file,s.replace(/export type Interface=[^\\n]+/,'export type Interface=Readonly<{readonly \"find\":(request:any)=>Promise<any>}>;'));}
    if(mode==='signature-readonly'){const s=fs.readFileSync(file,'utf8');fs.writeFileSync(file,s.replace(/export type Interface=[^\\n]+/,'export type Interface={\"find\":(request:PublicContracts[\"request\"])=>Promise<PublicContracts[\"response\"]|null>};'));}
    if(mode==='signature-erasure')fs.writeFileSync(path.join(base,'signatures/0.ts'),'export {};\\n');
    if(mode==='signature-config'){const c=JSON.parse(fs.readFileSync(config,'utf8'));c.compilerOptions.noCheck=true;fs.writeFileSync(config,JSON.stringify(c));}
   }
   const result=original(command,args,settings);if(signature)signatureResult=result.status;
   if(result.status===0&&args.includes('--project')&&String(config).endsWith('/semantic/compiler.json')&&!mode.startsWith('signature-')&&!mode.startsWith('late')&&mode!=='source-global'){
    const file=path.join(path.dirname(config),'modules/domain/features/alpha/src/application/interfaces/api.js'),old=fs.readFileSync(file,'utf8');let changed=old;
    const wrap=(normalize,key='p.key')=>{
     changed=old.replace('export const publicContracts =','const originalPublicContracts =')+'\\nconst p=originalPublicContracts.response;export const publicContracts=Object.freeze({...originalPublicContracts,response:Object.freeze({normalize:'+normalize+',key:'+key+'})});\\n';
    };
    if(mode==='field')wrap('input=>Object.freeze({...p.normalize(input),count:0n})');
    if(mode==='primitive')wrap('input=>Object.freeze({...p.normalize(input),count:Number(p.normalize(input).count)})');
    if(mode==='omit')wrap('input=>{const {memo,...rest}=p.normalize(input);return Object.freeze(rest);}');
    if(mode==='extra')wrap('input=>Object.freeze({...p.normalize(input),extra:true})');
    if(mode==='mutable')wrap('input=>({...p.normalize(input)})');
    if(mode==='alias')wrap('input=>{p.normalize(input);return Object.freeze(input);}');
    if(mode==='key')wrap('p.normalize','value=>\"collapsed\"');
    if(mode==='identity')wrap('p.normalize','value=>originalPublicContracts.shadow.key(value)');
    if(mode==='optional')wrap('input=>p.normalize({...input,memo:input.memo??\"\"})');
    if(mode==='validation')wrap('input=>p.normalize({id:input.id,count:input.count,memo:input.memo??null})');
    if(mode==='endpoint')changed=old.replace('export const endpointValues =','const originalEndpointValues =')+'\\nexport const endpointValues=Object.freeze({...originalEndpointValues,find:Object.freeze({request:originalEndpointValues.find.result,result:originalEndpointValues.find.request})});\\n';
    if(mode==='surface-omit')changed=old.replace('export const publicContracts =','const originalPublicContracts =')+'\\nconst {shadow,...rest}=originalPublicContracts;export const publicContracts=Object.freeze(rest);\\n';
    if(mode==='surface-freeze')changed=old.replace('export const publicContracts = Object.freeze(','export const publicContracts = Object(');
    if(['version-all','version-none','version-major','version-coercion'].includes(mode)){
     const body=mode==='version-all'?'v=>true':mode==='version-none'?'v=>false':mode==='version-major'?'v=>typeof v===\"string\"&&originalAcceptsVersion(\"1.\"+v.split(\".\").slice(1).join(\".\"))':'v=>originalAcceptsVersion(String(v))';
     changed=old.replace('export const acceptsVersion =','const originalAcceptsVersion =')+'\\nexport const acceptsVersion='+body+';\\n';
    }
    if(mode.startsWith('binding-')||mode==='version-descriptor'){
     const cases=JSON.parse(fs.readFileSync(path.join(path.dirname(config),'cases.json'),'utf8')),row=cases.rows.find(r=>r.selector==='alpha:api'),kind=mode==='version-descriptor'?'interface-version-descriptor':'interface-descriptor',d=JSON.parse(row.cases.find(c=>c.mode===kind).expected.value),name=mode==='version-descriptor'?'versionPolicy':'descriptor';
     if(mode==='binding-source')d.source.sha256='0'.repeat(64);if(mode==='binding-field')d.field_compilation_sha256='0'.repeat(64);if(mode==='binding-contract')d.contract_sha256='0'.repeat(64);if(mode==='binding-effect')d.invariant_execution='performed';if(mode==='version-descriptor')d.mode='exact';
     const suffix=mode==='binding-cycle'?'const d={};d.self=d;export const descriptor=Object.freeze(d);':('export const '+name+'='+(mode==='binding-freeze'?'Object':'freeze')+'('+JSON.stringify(d)+');');
     changed=old.replace('export const '+name+' =','const originalDescriptor =')+'\\nconst freeze=v=>{if(v&&typeof v===\"object\"){Object.values(v).forEach(freeze);Object.freeze(v);}return v;};'+suffix+'\\n';
    }
    if(mode==='static-import')changed=old+'\\nimport \"../queries/all.js\";\\n';
    if(mode==='caught-import')changed=old+'\\nimport(\"../queries/all.js\").catch(()=>{});\\n';
    if(mode==='global')changed=old+'\\nglobalThis.interfaceLeak=1;\\n';
    if(mode==='prototype')changed=old+'\\nObject.freeze(Object.prototype);\\n';
    if(mode==='object-write')changed=old+'\\nObject[\"defineProperty\"](Object[\"prototype\"],\"interfaceLeak\",{value:1});\\n';
    if(changed===old)throw Error('Interface mutant not installed:'+mode);fs.writeFileSync(file,changed);
    const syntax=original(process.execPath,['--check',file],{encoding:'utf8',timeout:60000});if(syntax.status!==0)throw Error('Interface mutant syntax:'+mode+':'+syntax.stderr);
   }
   if(args.includes('--permission')&&result.status===0&&mode.startsWith('late'))fs.appendFileSync(path.join(settings.cwd,mode==='late-signature'?'signatures/0.ts':'modules/domain/features/alpha/src/application/interfaces/api.js'),' ');
   return result;
  };syncBuiltinESMExports();
  try{const graph=loadCompiledProjectGraph(source),plan=planCompiledReconciledProject(graph,selection),report=executeReconciledVerification(graph,plan,tools);reports.push({mode,report,calls,signatureCalls,signatureResult});}finally{cp.spawnSync=original;syncBuiltinESMExports();}
 }console.log(JSON.stringify(reports));`);
 for(const {mode,report,calls,signatureCalls,signatureResult}of reports){
  const check=(id:string)=>report.checks.find((c:any)=>c.id===id),semantic=check('selected-generator-semantic-controls');
  if(mode==='source-global'){assert.equal(check('interface-source-effect-audit').result,'fail',mode);assert.equal(calls,0);}
  else if(mode.startsWith('late')){assert.equal(check('semantic-workspace-currentness').result,'fail',mode);assert.equal(semantic.result,'not_evaluable',mode);assert.equal(check('interface-native-effect-audit').result,'not_evaluable',mode);}
  else if(['caught-import','global','prototype','object-write'].includes(mode)){assert.equal(check('interface-native-effect-audit').result,'fail',mode);assert.equal(calls,0);}
  else if(mode.startsWith('signature-')){assert.equal(signatureCalls,1,mode);assert.equal(calls,0,mode);assert.equal(semantic.result,'fail',mode+':'+semantic.reason);if(['signature-type','signature-readonly'].includes(mode)){assert.notEqual(signatureResult,0,mode);assert.match(semantic.reason,/TS2344/,mode);}else assert.match(semantic.reason,/INTERFACE_SIGNATURE/,mode);}
  else{assert.equal(semantic.result,'fail',mode+':'+semantic.reason);assert.ok(calls>0,mode);assert.match(semantic.reason,mode==='static-import'?/INTERFACE_NATIVE_IMPORT_BOUNDARY/:/observation mismatch/,mode);}
  assert.equal(check('verification-workspace-cleanup').result,'pass',mode);
 }
});
test('Interface audit evidence substitution and artifact drift cannot authorize semantic execution',t=>{
 const f=fixture(t,'domain',true),n=nativeContext(f),reports=n.run(`import fs from 'node:fs';import cp from 'node:child_process';import {syncBuiltinESMExports} from 'node:module';
 import {loadCompiledProjectGraph,planCompiledReconciledProject,executeReconciledVerification} from './dist/index.js';
 const source=${JSON.stringify(f.source)},selection=${JSON.stringify(f.selection)},tools=${JSON.stringify(n.options)},original=cp.spawnSync,reports=[];
 for(const mode of ['source-omit','native-phase','native-hash','source-script','native-script','late']){
  let calls=0,script='';
  cp.spawnSync=(command,args,settings)=>{
   if(command===tools.lean_executable)return {status:1,stdout:'',stderr:'isolated audit custody'};
   if(args.includes('--permission'))calls++;
   const result=original(command,args,settings),file=args.find(a=>String(a).endsWith('/interface-effects.mjs'));
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
  if(mode==='late'){assert.ok(callsAfter>0);assert.equal(check('interface-effect-audit-currentness').result,'fail');for(const id of ['interface-source-effect-audit','interface-native-effect-audit','selected-generator-semantic-controls'])assert.equal(check(id).result,'not_evaluable',id);}
  else{assert.equal(callsAfter,0,mode);assert.equal(check(mode.startsWith('source')?'interface-source-effect-audit':'interface-native-effect-audit').result,'fail',mode);}
  assert.equal(check('verification-workspace-cleanup').result,'pass');
 }
});

test('Interface capacity retains all public contracts and source audit without certifying a passing prefix',t=>{
 const f=fixture(t,'domain',true),contract=interfaceContract();
 contract.contracts=Array.from({length:128},(_,i)=>({contract_id:'value-'+i,ontology_contract:'TEST-VALUE-'+i,fields:[publicField('amount',scalar('UInt64'))]}));
 contract.operations[0].request=scalar();contract.operations[0].result=local('value-0');f.api('capacity',contract);f.save();
 const n=nativeContext(f),reports=n.run(`import fs from 'node:fs';import path from 'node:path';import cp from 'node:child_process';import {syncBuiltinESMExports} from 'node:module';
 import {loadCompiledProjectGraph,planCompiledReconciledProject,executeReconciledVerification} from './dist/index.js';
 const source=${JSON.stringify(f.source)},selection=${JSON.stringify(f.selection)},tools=${JSON.stringify(n.options)},original=cp.spawnSync,reports=[];
 for(const mode of ['clean','forbidden','literal']){
  let calls=0;cp.spawnSync=(command,args,settings)=>{
   if(command===tools.lean_executable)return {status:1,stdout:'',stderr:'isolated Interface capacity'};if(args.includes('--permission'))calls++;const config=args[args.indexOf('--project')+1];
   if(mode==='forbidden'&&args.includes('--project')&&String(config).endsWith('/native/tsconfig.json'))fs.appendFileSync(path.join(path.dirname(config),'domain/features/alpha/src/application/interfaces/capacity.ts'),'\\nvoid Date.now();\\n');
   const result=original(command,args,settings);
   if(mode==='literal'&&result.status===0&&args.includes('--project')&&String(config).endsWith('/semantic/compiler.json'))fs.appendFileSync(path.join(path.dirname(config),'modules/domain/features/alpha/src/application/interfaces/api.js'),'\\nvoid \"process Date Promise eval import\"; // globalThis fetch\\n');
   return result;
  };syncBuiltinESMExports();
  try{const graph=loadCompiledProjectGraph(source),plan=planCompiledReconciledProject(graph,selection);reports.push({mode,report:executeReconciledVerification(graph,plan,tools),calls});}finally{cp.spawnSync=original;syncBuiltinESMExports();}
 }console.log(JSON.stringify(reports));`);
 for(const {mode,report,calls}of reports){
  const check=(id:string)=>report.checks.find((c:any)=>c.id===id),coverage=report.semantic_coverage.rows.find((r:any)=>r.selector==='alpha:capacity');
  assert.equal(coverage.adapter_status,'not_evaluable',JSON.stringify(coverage));assert.equal(Object.hasOwn(coverage,'case_count'),false);assert.match(coverage.reason,/bounded Interface/);
  if(mode==='forbidden'){assert.equal(check('interface-source-effect-audit').result,'fail');assert.equal(calls,0);}
  else{assert.equal(check('interface-source-effect-audit').result,'pass',JSON.stringify(check('interface-source-effect-audit')));assert.ok(check('interface-source-effect-audit').evidence.selectors.includes('alpha:capacity'));assert.equal(check('interface-native-effect-audit').result,'pass');assert.equal(check('interface-native-effect-audit').evidence.selectors.includes('alpha:capacity'),false);const semantic=check('selected-generator-semantic-controls');assert.equal(semantic.result,'not_evaluable');assert.ok(semantic.evidence.tested.some((r:any)=>r.selector==='alpha:api'));assert.ok(semantic.evidence.remaining.some((r:any)=>r.selector==='alpha:capacity'));assert.ok(calls>0);}
  assert.equal(check('verification-workspace-cleanup').result,'pass');
 }
});

test('native Interface public and endpoint shapes remain exact without factory witnesses or version coercion',t=>{
 const f=fixture(t,'domain',true);
 f.node('invalid-value','Rule',{predicate:'structured:domainspec.typed-rule/v2',typed_contract:{schema_version:'domainspec.typed-rule/v2',ontology_rule:'TEST-INVALID-VALUE',parameters:[{name:'value',type:scalar()}],expression:{op:'eq',left:{op:'literal',type:'Bool',value:false},right:{op:'literal',type:'Bool',value:true}}}});
 f.node('component','Value Object',{fields:['code','enabled'],invariant_refs:['alpha:invalid-value'],typed_contract:{schema_version:'domainspec.typed-record/v1',ontology_node:'TEST-COMPONENT',properties:[property('code',scalar()),property('enabled',scalar('Bool'))].map(p=>({...p,ontology_property:'TEST-COMPONENT#'+p.name}))}});
 f.node('status','Enum',{values:['None','Some'],typed_contract:{schema_version:'domainspec.typed-sum/v1',ontology_node:'TEST-STATUS',variants:[{name:'None',ontology_variant:'TEST-STATUS#None',payload:null},{name:'Some',ontology_variant:'TEST-STATUS#Some',payload:scalar('Bool')}]}});f.save();
 f.selection.factories.push({selector:'alpha:component',base_validators:[{rule:'alpha:invalid-value',arguments:[{parameter:'value',field:'code'}]}],extensions:[]});

 const variants=[scalar(),scalar('UInt64'),scalar('Bool'),wrap('optional',scalar('UInt64')),wrap('list',scalar('UInt64')),wrap('set',scalar('UInt64')),{kind:'sum',variants:[{name:'None',ontology_variant:'TEST-CHOICE#None',payload:null},{name:'Some',ontology_variant:'TEST-CHOICE#Some',payload:local('detail')}]},named('component'),named('status'),wrap('list',named('component')),wrap('set',named('component')),local('detail'),wrap('list',local('detail')),wrap('set',local('detail')),wrap('optional',local('detail'))];
 const n=nativeContext(f),reports=n.run(`import fs from 'node:fs';import path from 'node:path';import cp from 'node:child_process';import {syncBuiltinESMExports} from 'node:module';import {isDeepStrictEqual} from 'node:util';
 import {loadCompiledProjectGraph,planCompiledReconciledProject,executeReconciledVerification} from './dist/index.js';
 const source=${JSON.stringify(f.source)},selection=${JSON.stringify(f.selection)},tools=${JSON.stringify(n.options)},variants=${JSON.stringify(variants)},original=cp.spawnSync,reports=[],file=path.join(source,'specs/alpha/nodes/api.json'),node=JSON.parse(fs.readFileSync(file,'utf8'));
 for(const [index,type]of variants.entries()){
  const c=node.body.typed_contract;
  c.contracts=[{contract_id:'detail',ontology_contract:'TEST-DETAIL',fields:[{name:'amount',type:{kind:'scalar',name:'UInt64'},ontology_field:'TEST-DETAIL#amount',meaning:'amount'}]},{contract_id:'response',ontology_contract:'TEST-RESPONSE',fields:[{name:'value',type,ontology_field:'TEST-RESPONSE#value',meaning:'value'}]}];
  c.operations[0].request=type;c.operations[0].result={kind:'contract',contract_id:'response'};
  c.version_policy.mode=index%2?'exact':'backward';c.version_policy.provider_version=index>7?'9'.repeat(64)+'.'+'9'.repeat(64)+'.'+'9'.repeat(64):index%2?'0.0.0':'1.2.3';
  fs.writeFileSync(file,JSON.stringify(node));let mismatch=null;
  cp.spawnSync=(command,args,settings)=>{
   if(command===tools.lean_executable)return {status:1,stdout:'',stderr:'isolated Interface shapes'};const result=original(command,args,settings);
   if(args.includes('--permission')&&result.status===0){const planned=JSON.parse(fs.readFileSync(args.find(a=>String(a).endsWith('/cases.json')),'utf8')),actual=JSON.parse(result.stdout);for(const r of planned.rows){for(const c of r.cases){const a=actual.find(a=>a.selector===r.selector)?.cases.find(a=>a.id===c.id);if(!isDeepStrictEqual(c.expected,a?.outcome)){mismatch={selector:r.selector,case:c,actual:a};break;}}if(mismatch)break;}}
   return result;
  };syncBuiltinESMExports();
  try{const graph=loadCompiledProjectGraph(source),plan=planCompiledReconciledProject(graph,selection),report=executeReconciledVerification(graph,plan,tools);reports.push({index,mismatch,semantic:report.checks.find(c=>c.id==='selected-generator-semantic-controls'),coverage:report.semantic_coverage.rows.find(r=>r.selector==='alpha:api')});}finally{cp.spawnSync=original;syncBuiltinESMExports();}
 }console.log(JSON.stringify(reports));`);
 assert.equal(reports.length,variants.length);
 for(const r of reports){assert.equal(r.mismatch,null,JSON.stringify(r));assert.equal(r.coverage.adapter_status,'ready',JSON.stringify(r));assert.equal(r.semantic.executed,true,JSON.stringify(r));assert.equal(r.semantic.evidence.interface_signature_count,1,JSON.stringify(r));assert.ok(r.semantic.evidence.tested.some((x:any)=>x.selector==='alpha:api'),JSON.stringify(r));assert.ok(r.semantic.evidence.remaining.some((x:any)=>x.selector==='alpha:component'),JSON.stringify(r));}
});
test('native Interface values work while every domain and application member module is poisoned',t=>{
 const f=fixture(t);f.node('computed','Calculation',{inputs:['left','right'],typed_contract:{schema_version:'domainspec.typed-calculation/v2',ontology_calculation:'TEST-COMPUTED',inputs:['left','right'].map(name=>({name,type:scalar('UInt64')})),result:scalar('UInt64'),division_rounding:'reject',expression:{op:'add',left:{op:'input',name:'left'},right:{op:'input',name:'right'}}}});f.save();
 const n=nativeContext(f),result=n.run(`import assert from 'node:assert/strict';import fs from 'node:fs';import path from 'node:path';import {execFileSync,spawnSync} from 'node:child_process';
 import {loadCompiledProjectGraph,planCompiledReconciledProject} from './dist/index.js';
 const graph=loadCompiledProjectGraph(${JSON.stringify(f.source)}),plan=planCompiledReconciledProject(graph,${JSON.stringify(f.selection)}),tools=${JSON.stringify(n.options)},source=path.resolve('products'),output=path.resolve('compiled-products');fs.mkdirSync(source);fs.writeFileSync(path.join(source,'package.json'),'{"type":"module"}');
 for(const a of plan.resolved.artifacts){const file=path.join(source,a.relative_path);fs.mkdirSync(path.dirname(file),{recursive:true});fs.writeFileSync(file,a.content);}
 const config=path.join(source,'tsconfig.json');fs.writeFileSync(config,JSON.stringify({compilerOptions:{strict:true,skipLibCheck:true,target:'ES2022',module:'NodeNext',moduleResolution:'NodeNext',rootDir:source,outDir:output,types:['node'],typeRoots:[tools.node_type_root]},files:plan.resolved.modules.map(m=>path.join(source,m.relative_path))}));
 execFileSync(process.execPath,[path.join(tools.typescript_root,'bin/tsc'),'--project',config],{encoding:'utf8',timeout:60000});fs.writeFileSync(path.join(output,'package.json'),'{"type":"module"}');
 const poisoned=plan.resolved.modules.filter(m=>m.qualified_selectors.some(s=>!['Interface'].includes(graph.nodes.find(n=>n.selector===s).kind)));
 for(const m of poisoned)fs.writeFileSync(path.join(output,m.relative_path.replace(/\\.ts$/,'.js')),'throw new Error("UNDECLARED_MODULE_LOADED");\\n');
 const module=id=>plan.resolved.modules.find(m=>m.qualified_selectors.includes('alpha:'+id)&&m.exports.some(e=>e.name==='publicContracts')),filename=id=>path.join(output,module(id).relative_path.replace(/\\.ts$/,'.js'));
 const client=path.resolve('interface-client.mjs');
 const program=['import assert from "node:assert/strict";','import * as api from '+JSON.stringify(filename('api'))+';','import * as zero from '+JSON.stringify(filename('zero'))+';',
 'const input={id:"record-1",count:"18446744073709551615"};const value=api.publicContracts.response.normalize(input);assert.deepEqual(value,{count:18446744073709551615n,id:"record-1",memo:null});',
 'assert.ok(Object.isFrozen(value));assert.equal("extend" in value,false);assert.equal("find" in api,false);assert.equal("Interface" in api,false);input.id="changed";assert.equal(value.id,"record-1");',
 'assert.notEqual(api.publicContracts.response.key(value),api.publicContracts.shadow.key(value));assert.notEqual(api.publicContracts.response.key(value),zero.publicContracts.response.key(value));',
 'assert.deepEqual(api.endpointValues.find.request.normalize({id:"x"}),{id:"x"});assert.equal(api.endpointValues.find.result.normalize(null),null);assert.deepEqual(api.endpointValues.find.result.normalize(value),value);',
 'assert.deepEqual(api.publicContracts.empty.normalize({}),{});assert.throws(()=>api.publicContracts.empty.normalize(null),/INTERFACE_VALUE/);assert.throws(()=>api.publicContracts.response.normalize({id:"x",count:9007199254740992}),/INTERFACE_VALUE/);',
 'assert.equal(api.acceptsVersion("1.2.3"),true);assert.equal(api.acceptsVersion("1.2.4"),false);assert.equal(api.acceptsVersion("2.0.0"),false);assert.equal(zero.acceptsVersion("0.1.0"),true);console.log("interface-isolation-pass");'].join(String.fromCharCode(10));fs.writeFileSync(client,program);
 const baseline=execFileSync(process.execPath,[client],{encoding:'utf8',timeout:60000}).trim();
 const provider=filename('api'),dependency=path.join(output,poisoned.find(m=>m.qualified_selectors.includes('alpha:computed')).relative_path.replace(/\\.ts$/,'.js'));let specifier=path.relative(path.dirname(provider),dependency).split(path.sep).join('/');if(!specifier.startsWith('.'))specifier='./'+specifier;
 fs.appendFileSync(provider,'\\nimport '+JSON.stringify(specifier)+';\\n');const negative=spawnSync(process.execPath,[client],{encoding:'utf8',timeout:60000});assert.notEqual(negative.status,0);assert.match(negative.stderr,/UNDECLARED_MODULE_LOADED/);
 console.log(JSON.stringify({baseline,poisoned:poisoned.length,negative:true}));`);
 assert.equal(result.baseline,'interface-isolation-pass');assert.ok(result.poisoned>0);assert.equal(result.negative,true);
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
 try{execFileSync('docker',[...docker,'tsc','--ignoreConfig','--strict','--skipLibCheck','--declaration','--types','node','--typeRoots',path.join(deps,'@types'),'--target','ES2022','--module','NodeNext','--rootDir',src,'--outDir',dist,path.join(src,'index.ts')],{encoding:'utf8'});}catch(e:any){throw new Error([e.message,e.stdout,e.stderr].filter(Boolean).join('\n'),{cause:e});}
 const options={typescript_root:'/opt/node-toolchain/node_modules/typescript',node_type_root:path.join(deps,'@types'),lean_executable:path.join(leanRoot,'bin','lean')};
 const run=(body:string)=>{const file=path.join(f.temp,'client.mjs');fs.writeFileSync(file,body);try{return JSON.parse(execFileSync('docker',[...docker,'node',file],{encoding:'utf8',timeout:180000,maxBuffer:32*1024*1024}));}catch(e:any){throw new Error([e.message,e.stdout,e.stderr].filter(Boolean).join('\n'),{cause:e});}};
 return {run,options};
}

import {nativeToolchainImage, NATIVE_TEST_IMAGE_ID} from '../helpers/native-toolchain-image.ts';
