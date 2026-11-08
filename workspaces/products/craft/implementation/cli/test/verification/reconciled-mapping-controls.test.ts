import assert from 'node:assert/strict';
import fs from 'node:fs';import os from 'node:os';import path from 'node:path';import test from 'node:test';
import {execFileSync} from 'node:child_process';import {createRequire} from 'node:module';
import {publicSelection} from '../helpers/composition-project.ts';
import {loadCompiledProjectGraph} from '../../src/input/project-model.ts';
import {planCompiledReconciledProject} from '../../src/generation/reconciled-project.ts';
import {createReconciledSemanticControls} from '../../src/verification/reconciled-semantic-controls.ts';
const project=path.resolve(import.meta.dirname,'../../../..');
const scalar=(name='String'):any=>({kind:'scalar',name}),named=(id:string):any=>({kind:'named',selector:'alpha:'+id}),wrap=(kind:string,element:any):any=>({kind,element});
const at=(root:string,...properties:string[]):any=>({op:'path',root,properties}),lit=(type:string,value:string|boolean):any=>({op:'literal',type,value});
const property=(owner:string,name:string,type:any,identity=false):any=>({name,type,identity,cardinality:type.kind==='optional'?'optional':type.kind==='list'?'many':type.kind==='set'?'many-unique':'one',meaning:name,ontology_property:'TEST-'+owner+'#'+name});
const ref=(contract_id='response',interface_selector='alpha:api'):any=>({kind:'contract',interface_selector,contract_id});
function fixture(t:any,moduleRoot='domain'){
 const temp=fs.mkdtempSync(path.join(os.tmpdir(),'ds-mapping-controls-')),source=path.join(temp,'source'),nodes:string[]=[],edges:string[]=[];
 t.after(()=>fs.rmSync(temp,{recursive:true,force:true}));
 const write=(p:string,v:any)=>{const f=path.join(source,p);fs.mkdirSync(path.dirname(f),{recursive:true});fs.writeFileSync(f,JSON.stringify(v)+'\n');};
 const node=(id:string,kind:string,body:any)=>{if(!nodes.includes(id))nodes.push(id);write('specs/alpha/nodes/'+id+'.json',{schema_version:'domainspec.node/v1',feature_id:'alpha',node_id:id,kind,body:{description:id,...body}});};
 const edge=(from:string,relationship:string,to:string)=>{const edge_id=from+'-'+relationship+'-'+to;if(!edges.includes(edge_id))edges.push(edge_id);write('specs/alpha/edges/'+edge_id+'.json',{schema_version:'domainspec.edge/v1',feature_id:'alpha',edge_id,relationship,source_node_id:from,target_node_id:to,scope:'feature'});};
 node('valid','Rule',{predicate:'structured:domainspec.typed-rule/v2',typed_contract:{schema_version:'domainspec.typed-rule/v2',ontology_rule:'TEST-VALID',parameters:[{name:'value',type:scalar()}],expression:{op:'eq',left:at('value'),right:at('value')}}});
 const props=[property('ORDER','id',scalar(),true),property('ORDER','amount',scalar('UInt64')),property('ORDER','memo',wrap('optional',scalar()))];
 for(const id of ['order','summary'])node(id,'Entity',{fields:props.map(p=>p.name),typed_contract:{schema_version:'domainspec.typed-record/v1',ontology_node:'TEST-'+id.toUpperCase(),properties:props.map(p=>({...p,ontology_property:'TEST-'+id.toUpperCase()+'#'+p.name}))}});
 node('find','Query',{reads:['alpha:order'],typed_contract:{schema_version:'domainspec.typed-query/v1',ontology_query:'TEST-FIND',source:'alpha:order',inputs:[],filter:null,projection:['id'],order_by:null,limit:null}});edge('find','reads','order');
 const api={schema_version:'domainspec.typed-interface/v1',ontology_interface:'TEST-API',boundary_kind:'external',version_policy:{schema_version:'domainspec.interface-version-policy/v1',mode:'backward',direction:'consumer-to-provider',provider_version:'1.0.0'},contracts:[{contract_id:'response',ontology_contract:'TEST-RESPONSE',fields:props.map(p=>({name:p.name,ontology_field:'TEST-PUBLIC#'+p.name,meaning:p.name,type:p.type}))},{contract_id:'empty',ontology_contract:'TEST-EMPTY',fields:[]}],operations:[{operation_id:'find',operation_ref:'alpha:find',request:scalar(),result:{kind:'contract',contract_id:'response'}}]};
 node('api','Interface',{typed_contract:api});edge('api','exposes','find');
 const bodies:any={};
 const mapping=(id:string,c:any)=>{bodies[id]=c;node(id,'Mapping',{target:typeof c.target==='string'?c.target:c.target.kind==='named'?c.target.selector:c.target.interface_selector,...(c.schema_version.endsWith('/v1')?{source:c.source}:{}),typed_contract:c});edge(id,'maps',typeof c.target==='string'?c.target.split(':')[1]:c.target.kind==='named'?c.target.selector.split(':')[1]:'api');};
 const legacy={schema_version:'domainspec.typed-mapping/v1',ontology_mapping:'TEST-LEGACY',source:'alpha:order',target:'alpha:summary',fields:[{target:'memo',source:'memo',default:{type:'String',value:'absent-only'}}],total:false};
 mapping('legacy',legacy);mapping('legacy-partial',{...legacy,ontology_mapping:'TEST-LEGACY-PARTIAL',fields:[{target:'memo',source:'memo',default:null}]});mapping('legacy-total',{...legacy,ontology_mapping:'TEST-LEGACY-TOTAL',fields:props.map(p=>({target:p.name,source:p.name,default:null})),total:true});
 const v2={schema_version:'domainspec.typed-mapping/v2',ontology_mapping:'TEST-FULL',inputs:[{name:'order',type:named('order')},{name:'total',type:scalar('UInt64')},{name:'memo',type:wrap('optional',scalar())},{name:'fallback',type:scalar()}],target:'alpha:summary',fields:[{target:'id',value:at('order','TEST-ORDER#id'),default:null},{target:'amount',value:at('total'),default:null},{target:'memo',value:at('memo'),default:at('fallback')}],total:true};
 mapping('full',v2);mapping('zero',{...v2,ontology_mapping:'TEST-ZERO',inputs:[],fields:[{target:'id',value:lit('String','constant'),default:null},{target:'amount',value:lit('UInt64','18446744073709551615'),default:null}],total:false});
 const v3={...v2,schema_version:'domainspec.typed-mapping/v3',ontology_mapping:'TEST-PUBLIC-MAPPING',inputs:v2.inputs.map(p=>({...p,use:null})),target:ref(),target_use:{interface_selector:'alpha:api',operation_id:'find',side:'result'}};
 mapping('outbound',v3);mapping('inbound',{...v3,ontology_mapping:'TEST-INBOUND',inputs:[{name:'request',type:ref(),use:null}],target:named('summary'),target_use:null,fields:props.map(p=>({target:p.name,value:at('request','TEST-PUBLIC#'+p.name),default:null}))});
 mapping('empty',{...v3,ontology_mapping:'TEST-PUBLIC-EMPTY',inputs:[],target:ref('empty'),target_use:null,fields:[]});
 const save=()=>{write('project.json',{schema_version:'domainspec.project/v1',project_id:'mapping-controls',features:['alpha'],cross_feature_edges:[]});write('specs/alpha/feature.json',{schema_version:'domainspec.feature/v1',feature_id:'alpha',nodes,edges});};save();
 const selection={...publicSelection(moduleRoot),factories:['order','summary'].map(id=>({selector:'alpha:'+id,base_validators:[{rule:'alpha:valid',arguments:[{parameter:'value',field:'id'}]}],extensions:[]})),operations:[]};
 const graph=loadCompiledProjectGraph(source),plan=planCompiledReconciledProject(graph,selection);
 return {temp,source,selection,graph,plan,node,edge,save,bodies,api,write,mapping};
}
test('Mapping cases preserve explicit inputs, legacy absence, public identities and whole source accounting',t=>{
 const f=fixture(t),controls=createReconciledSemanticControls(f.graph,f.plan),rows=controls.rows.filter(r=>r.kind==='Mapping') as any[];
 assert.equal(rows.length,8);for(const r of rows){assert.equal(r.state,'ready',r.selector+':'+r.reason);assert.ok(Object.isFrozen(r.cases));assert.equal(r.cases[0].mode,'mapping-descriptor');assert.ok(r.module_paths.every((p:string)=>/mappings|interfaces/.test(p)));}
 const cases=(id:string)=>rows.find(r=>r.selector==='alpha:'+id).cases;
 assert.ok(cases('legacy-total').some((c:any)=>c.expected.message==='MAPPING_REQUIRED_VALUE'));
 assert.ok(cases('legacy-partial').some((c:any)=>c.expected.kind==='value'&&c.expected.value==='[]'));
 assert.ok(cases('inbound').some((c:any)=>c.expected.message==='INTERFACE_VALUE'));
 assert.deepEqual(controls.rows.filter(r=>r.state==='not_evaluable').map(r=>r.kind).sort(),[]);
 const other=fixture(t,'other/root'),moved=createReconciledSemanticControls(other.graph,other.plan);
 for(const r of rows)assert.deepEqual(r.cases.filter((c:any)=>c.mode==='mapping'),(moved.rows.find(m=>m.selector===r.selector) as any).cases.filter((c:any)=>c.mode==='mapping'));
});
test('native Mapping controls cover all three source versions without loading domain factories or endpoints',t=>{
 const f=fixture(t),n=nativeContext(f),report=n.run(`import {loadCompiledProjectGraph,planCompiledReconciledProject,executeReconciledVerification} from './dist/index.js';
 const graph=loadCompiledProjectGraph(${JSON.stringify(f.source)}),plan=planCompiledReconciledProject(graph,${JSON.stringify(f.selection)});
 console.log(JSON.stringify(executeReconciledVerification(graph,plan,${JSON.stringify(n.options)})));`);
 const check=(id:string)=>report.checks.find((c:any)=>c.id===id),semantic=check('selected-generator-semantic-controls');
 assert.equal(semantic.executed,true,semantic.reason);assert.equal(semantic.result,'pass',semantic.reason);
 assert.equal(semantic.evidence.tested.filter((r:any)=>r.kind==='Mapping').length,8);assert.deepEqual(semantic.evidence.remaining.map((r:any)=>r.kind).sort(),[]);
 for(const phase of ['source','native']){assert.equal(check('mapping-'+phase+'-effect-audit').result,'pass',JSON.stringify(check('mapping-'+phase+'-effect-audit')));assert.equal(check('mapping-'+phase+'-effect-audit').evidence.selectors.length,8);}
 assert.equal(check('mapping-effect-audit-currentness').result,'pass');assert.equal(check('verification-workspace-cleanup').result,'pass');
});
test('compiling Mapping semantic and binding mutations, hidden effects and late drift cannot pass',t=>{
 const f=fixture(t),n=nativeContext(f),reports=n.run(`import fs from 'node:fs';import path from 'node:path';import {createHash} from 'node:crypto';import cp from 'node:child_process';import {syncBuiltinESMExports} from 'node:module';
 import {loadCompiledProjectGraph,planCompiledReconciledProject,executeReconciledVerification} from './dist/index.js';
 const source=${JSON.stringify(f.source)},selection=${JSON.stringify(f.selection)},tools=${JSON.stringify(n.options)},original=cp.spawnSync,reports=[];
 for(const mode of ['input','fallback','unused-input','field-order','omit','extra','root-freeze','primitive','alias','legacy-default','legacy-presence','legacy-total','zero-precision','binding-source','binding-target','binding-effect','binding-public','binding-freeze','binding-getter','binding-cycle','static-import','caught-import','global','prototype','object-write','bracket-write','source-global','late']){
  let nativeCalls=0;
  cp.spawnSync=(command,args,settings)=>{
   if(command===tools.lean_executable)return {status:1,stdout:'',stderr:'injected Lean failure for Mapping semantic isolation'};
   if(args.includes('--permission'))nativeCalls++;
   const config=args[args.indexOf('--project')+1];
   if(mode==='source-global'&&args.includes('--project')&&String(config).endsWith('/native/tsconfig.json'))fs.appendFileSync(path.join(path.dirname(config),'domain/features/alpha/src/application/mappings/full.provider.ts'),'\\nvoid Date.now();\\n');
   const result=original(command,args,settings);
   if(result.status===0&&args.includes('--project')&&String(config).endsWith('/semantic/compiler.json')&&!['source-global','late'].includes(mode)){
    const folder=path.join(path.dirname(config),'modules/domain/features/alpha/src/application/mappings'),id=mode==='binding-public'?'outbound':mode.startsWith('legacy-')?(mode==='legacy-presence'?'legacy-partial':mode==='legacy-total'?'legacy-total':'legacy'):mode==='zero-precision'?'zero':'full';
    const file=path.join(folder,id+(mode.startsWith('binding-')?'':'.provider')+'.js'),old=fs.readFileSync(file,'utf8'),start=old.indexOf('export const map ='),prefix=old.slice(0,start),body=old.slice(start);let changed=old;
    const edit=(a,b)=>{changed=prefix+body.replace(a,b);};
    if(mode==='input')edit('const v1 = p1;','const v1 = p0["amount"];');
    if(mode==='fallback')edit('p2 ?? p3','p2 ?? "fixed"');
    if(mode==='unused-input')edit(/const p3 = [^;]+;/,'const p3 = d["fallback"].value;');
    if(mode==='field-order')edit('["id"]: v0, ["amount"]: v1','["amount"]: v1, ["id"]: v0');
    if(mode==='omit')edit(', ["memo"]: v2','');
    if(mode==='extra')edit('["memo"]: v2','["memo"]: v2, extra: true');
    if(mode==='root-freeze')edit('return Object.freeze({','return Object({');
    if(mode==='primitive')edit('const v1 = p1;','const v1 = Number(p1);');
    if(mode==='alias')edit('return Object.freeze({ ["id"]: v0, ["amount"]: v1, ["memo"]: v2 });','return Object.freeze(parameters.order);');
    if(mode==='legacy-default')edit('Object.hasOwn(s, "memo") ? p0["memo"] : "absent-only"','p0["memo"] ?? "absent-only"');
    if(mode==='legacy-presence')edit('Object.hasOwn(s, "memo") ?','true ?');
    if(mode==='legacy-total')edit('if (!Object.hasOwn(s, "memo"))','if (false)');
    if(mode==='zero-precision')edit('18446744073709551615n','BigInt(Number("18446744073709551615"))');
    if(['binding-source','binding-target','binding-effect','binding-public'].includes(mode)){
     const cases=JSON.parse(fs.readFileSync(path.join(path.dirname(config),'cases.json'),'utf8')),d=JSON.parse(cases.rows.find(r=>r.selector==='alpha:'+id).cases.find(c=>c.mode==='mapping-descriptor').expected.value);
     if(mode==='binding-source')d.contract_sha256='0'.repeat(64);if(mode==='binding-target')d.target.selector='alpha:order';if(mode==='binding-effect')d.effect_contract='execute';if(mode==='binding-public')d.contract.target_use.side='request';
     delete d.descriptor_sha256;const canonical=v=>JSON.stringify(v,(_,x)=>x&&typeof x==='object'&&!Array.isArray(x)?Object.fromEntries(Object.entries(x).sort(([a],[b])=>a<b?-1:a>b?1:0)):x);d.descriptor_sha256=createHash('sha256').update(canonical(d)).digest('hex');
     changed='import {map} from "./'+id+'.provider.js";const freeze=v=>{if(v&&typeof v==="object"){Object.values(v).forEach(freeze);Object.freeze(v);}return v;};export const mapping'+id[0].toUpperCase()+id.slice(1)+'=Object.freeze(Object.assign(map,{descriptor:freeze('+JSON.stringify(d)+')}));';
    }
    if(mode==='binding-freeze')changed=old.replace('Object.freeze(Object.assign(map,','Object(Object.assign(map,');
    if(mode==='binding-getter')changed='import {map} from "./full.provider.js";export const mappingFull=Object.freeze(Object.defineProperty(map,"descriptor",{enumerable:true,get(){throw new Error("GETTER_EXECUTED");}}));';
    if(mode==='binding-cycle')changed='import {map} from "./full.provider.js";const d={};d.self=d;Object.freeze(d);export const mappingFull=Object.freeze(Object.assign(map,{descriptor:d}));';
    if(mode==='static-import')changed=old+'\\nimport "./zero.js";\\n';
    if(mode==='caught-import')changed=old+'\\nimport("./zero.js").catch(()=>{});\\n';
    if(mode==='global')changed=old+'\\nglobalThis.mappingLeak=1;\\n';
    if(mode==='prototype')changed=old+'\\nObject.freeze(Object.prototype);\\n';
    if(mode==='object-write')changed=old+'\\nObject.defineProperty(Object.prototype,"mappingLeak",{value:1});\\n';
    if(mode==='bracket-write')changed=old+'\\nObject["defineProperty"](Object["prototype"],"mappingLeak",{value:1});\\n';
    if(changed===old)throw Error('Mapping mutant not installed:'+mode+':'+old.slice(-2000));fs.writeFileSync(file,changed);
    const syntax=original(process.execPath,['--check',file],{encoding:'utf8',timeout:60000});if(syntax.status!==0)throw Error('Mapping mutant syntax:'+mode+':'+syntax.stderr);
   }
   if(mode==='late'&&args.includes('--permission')&&result.status===0)fs.appendFileSync(path.join(settings.cwd,'modules/domain/features/alpha/src/application/mappings/full.provider.js'),' ');
   return result;
  };syncBuiltinESMExports();
  try{const graph=loadCompiledProjectGraph(source),plan=planCompiledReconciledProject(graph,selection);reports.push({mode,report:executeReconciledVerification(graph,plan,tools),nativeCalls});}finally{cp.spawnSync=original;syncBuiltinESMExports();}
 }
 console.log(JSON.stringify(reports));`);
 for(const {mode,report,nativeCalls}of reports){
  const check=(id:string)=>report.checks.find((c:any)=>c.id===id),semantic=check('selected-generator-semantic-controls');
  if(mode==='source-global'){assert.equal(check('mapping-source-effect-audit').result,'fail',mode);assert.equal(nativeCalls,0);}
  else if(mode==='late'){assert.equal(check('semantic-workspace-currentness').result,'fail');assert.equal(semantic.result,'not_evaluable');assert.equal(check('mapping-native-effect-audit').result,'not_evaluable');}
  else if(['binding-getter','caught-import','global','prototype','object-write','bracket-write'].includes(mode)){assert.equal(check('mapping-native-effect-audit').result,'fail',mode);assert.equal(nativeCalls,0);}
  else{assert.equal(semantic.result,'fail',mode+':'+semantic.reason);assert.ok(nativeCalls>0,mode);assert.match(semantic.reason,mode==='static-import'?/MAPPING_NATIVE_IMPORT_BOUNDARY/:/observation mismatch/,mode);}
  assert.equal(check('verification-workspace-cleanup').result,'pass',mode);
 }
});
test('Mapping audit evidence substitution and artifact drift cannot authorize semantic execution',t=>{
 const f=fixture(t),n=nativeContext(f),reports=n.run(`import fs from 'node:fs';import cp from 'node:child_process';import {syncBuiltinESMExports} from 'node:module';
 import {loadCompiledProjectGraph,planCompiledReconciledProject,executeReconciledVerification} from './dist/index.js';
 const source=${JSON.stringify(f.source)},selection=${JSON.stringify(f.selection)},tools=${JSON.stringify(n.options)},original=cp.spawnSync,reports=[];
 for(const mode of ['source-omit','native-phase','native-hash','source-script','native-script','late']){
  let calls=0,script='';
  cp.spawnSync=(command,args,settings)=>{
   if(command===tools.lean_executable)return {status:1,stdout:'',stderr:'isolated audit custody'};
   if(args.includes('--permission'))calls++;
   const result=original(command,args,settings),file=args.find(a=>String(a).endsWith('/mapping-effects.mjs'));
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
  if(mode==='late'){assert.ok(callsAfter>0);assert.equal(check('mapping-effect-audit-currentness').result,'fail');for(const id of ['mapping-source-effect-audit','mapping-native-effect-audit','selected-generator-semantic-controls'])assert.equal(check(id).result,'not_evaluable',id);}
  else{assert.equal(callsAfter,0,mode);assert.equal(check(mode.startsWith('source')?'mapping-source-effect-audit':'mapping-native-effect-audit').result,'fail',mode);}
  assert.equal(check('verification-workspace-cleanup').result,'pass');
 }
});
test('Mapping capacity preserves the entire source node and still audits its source effects',t=>{
 const f=fixture(t),c={...f.bodies.zero,ontology_mapping:'TEST-CAPACITY',inputs:Array.from({length:128},(_,i)=>({name:'value'+i,type:scalar('UInt64')}))};f.mapping('capacity',c);f.save();
 const n=nativeContext(f),reports=n.run(`import fs from 'node:fs';import path from 'node:path';import cp from 'node:child_process';import {syncBuiltinESMExports} from 'node:module';
 import {loadCompiledProjectGraph,planCompiledReconciledProject,executeReconciledVerification} from './dist/index.js';
 const source=${JSON.stringify(f.source)},selection=${JSON.stringify(f.selection)},tools=${JSON.stringify(n.options)},original=cp.spawnSync,reports=[];
 for(const mode of ['clean','forbidden','literal']){
  let calls=0;cp.spawnSync=(command,args,settings)=>{
   if(command===tools.lean_executable)return {status:1,stdout:'',stderr:'isolated capacity'};
   if(args.includes('--permission'))calls++;const config=args[args.indexOf('--project')+1];
   if(mode==='forbidden'&&args.includes('--project')&&String(config).endsWith('/native/tsconfig.json'))fs.appendFileSync(path.join(path.dirname(config),'domain/features/alpha/src/application/mappings/capacity.provider.ts'),'\\nvoid Date.now();\\n');
   const result=original(command,args,settings);
   if(mode==='literal'&&result.status===0&&args.includes('--project')&&String(config).endsWith('/semantic/compiler.json'))fs.appendFileSync(path.join(path.dirname(config),'modules/domain/features/alpha/src/application/mappings/full.provider.js'),'\\n// Date globalThis Promise\\nvoid "Object.defineProperty";\\n');
   return result;
  };syncBuiltinESMExports();
  try{const graph=loadCompiledProjectGraph(source),plan=planCompiledReconciledProject(graph,selection),report=executeReconciledVerification(graph,plan,tools);reports.push({mode,report,calls});}finally{cp.spawnSync=original;syncBuiltinESMExports();}
 }console.log(JSON.stringify(reports));`);
 for(const {mode,report,calls}of reports){
  const check=(id:string)=>report.checks.find((c:any)=>c.id===id),row=report.semantic_coverage.rows.find((r:any)=>r.selector==='alpha:capacity');
  assert.equal(row.adapter_status,'not_evaluable');assert.equal(Object.hasOwn(row,'case_count'),false);
  if(mode==='forbidden'){assert.equal(check('mapping-source-effect-audit').result,'fail');assert.equal(calls,0);}
  else{assert.equal(check('mapping-source-effect-audit').result,'pass');assert.ok(check('mapping-source-effect-audit').evidence.selectors.includes('alpha:capacity'));assert.ok(!check('mapping-native-effect-audit').evidence.selectors.includes('alpha:capacity'));assert.ok(calls>0);}
 }
});
test('Mapping native projections preserve nested domain and qualified public shapes without factory witnesses',t=>{
 const f=fixture(t);
 f.node('invalid-value','Rule',{predicate:'structured:domainspec.typed-rule/v2',typed_contract:{schema_version:'domainspec.typed-rule/v2',ontology_rule:'TEST-INVALID-VALUE',parameters:[{name:'value',type:scalar()}],expression:{op:'eq',left:lit('Bool',false),right:lit('Bool',true)}}});
 f.node('component','Value Object',{fields:['code','enabled'],invariant_refs:['alpha:invalid-value'],typed_contract:{schema_version:'domainspec.typed-record/v1',ontology_node:'TEST-COMPONENT',properties:[property('COMPONENT','code',scalar()),property('COMPONENT','enabled',scalar('Bool'))]}});
 f.node('status','Enum',{values:['None','Some'],typed_contract:{schema_version:'domainspec.typed-sum/v1',ontology_node:'TEST-STATUS',variants:[{name:'None',ontology_variant:'TEST-STATUS#None',payload:null},{name:'Some',ontology_variant:'TEST-STATUS#Some',payload:scalar('Bool')}]}});
 const target=(type:any)=>({fields:['id','value'],typed_contract:{schema_version:'domainspec.typed-record/v1',ontology_node:'TEST-SHAPETARGET',properties:[property('SHAPETARGET','id',scalar(),true),property('SHAPETARGET','value',type)]}});
 f.node('shapetarget','Entity',target(scalar()));
 const c={schema_version:'domainspec.typed-mapping/v3',ontology_mapping:'TEST-SHAPES',inputs:[{name:'value',type:scalar(),use:null}],target:named('shapetarget'),target_use:null,fields:[{target:'id',value:lit('String','projection'),default:null},{target:'value',value:at('value'),default:null}],total:true};
 f.mapping('shapes',c);f.save();
 f.selection.factories.push({selector:'alpha:component',base_validators:[{rule:'alpha:invalid-value',arguments:[{parameter:'value',field:'code'}]}],extensions:[]},{selector:'alpha:shapetarget',base_validators:[{rule:'alpha:valid',arguments:[{parameter:'value',field:'id'}]}],extensions:[]});
 const types=[scalar('Bool'),wrap('optional',scalar('UInt64')),wrap('list',scalar('UInt64')),wrap('set',scalar('UInt64')),{kind:'sum',variants:[{name:'None',ontology_variant:'TEST-CHOICE#None',payload:null},{name:'Amount',ontology_variant:'TEST-CHOICE#Amount',payload:scalar('UInt64')}]},named('order'),named('component'),named('status'),wrap('set',named('component')),ref(),wrap('list',ref()),{kind:'sum',variants:[{name:'None',ontology_variant:'TEST-PUBLIC-CHOICE#None',payload:null},{name:'Some',ontology_variant:'TEST-PUBLIC-CHOICE#Some',payload:ref()}]}];
 const variants=types.map(type=>({input:type,output:type,expression:at('value')})).concat([
  {input:wrap('list',named('order')),output:wrap('set',named('order')),expression:{op:'to_set',value:at('value')}},
  {input:wrap('list',named('order')),output:wrap('set',scalar('UInt64')),expression:{op:'to_set',value:at('value','TEST-ORDER#amount')}},
  {input:wrap('set',ref()),output:wrap('set',scalar()),expression:at('value','TEST-PUBLIC#id')}
 ]);
 const n=nativeContext(f),reports=n.run(`import fs from 'node:fs';import path from 'node:path';import cp from 'node:child_process';import {syncBuiltinESMExports} from 'node:module';
 import {loadCompiledProjectGraph,planCompiledReconciledProject,executeReconciledVerification} from './dist/index.js';
 const source=${JSON.stringify(f.source)},selection=${JSON.stringify(f.selection)},tools=${JSON.stringify(n.options)},variants=${JSON.stringify(variants)},reports=[],original=cp.spawnSync;
 const {isDeepStrictEqual}=await import('node:util');
 const file=id=>path.join(source,'specs/alpha/nodes/'+id+'.json'),target=JSON.parse(fs.readFileSync(file('shapetarget'),'utf8')),mapping=JSON.parse(fs.readFileSync(file('shapes'),'utf8')),api=JSON.parse(fs.readFileSync(file('api'),'utf8')),edgeFile=path.join(source,'specs/alpha/edges/shapes-maps-shapetarget.json'),edge=JSON.parse(fs.readFileSync(edgeFile,'utf8'));
 const hasPublic=t=>t.kind==='contract'||(t.kind==='sum'?t.variants.some(v=>v.payload&&hasPublic(v.payload)):t.element?hasPublic(t.element):false);
 const local=t=>t.kind==='contract'?{kind:'contract',contract_id:t.contract_id}:t.kind==='sum'?{...t,variants:t.variants.map(v=>({...v,payload:v.payload?local(v.payload):null}))}:t.element?{...t,element:local(t.element)}:t;
 for(const [index,v]of variants.entries()){
  const publicOutput=hasPublic(v.output),domainType=publicOutput?{kind:'scalar',name:'String'}:v.output;
  target.body.typed_contract.properties[1].type=domainType;target.body.typed_contract.properties[1].cardinality=domainType.kind==='optional'?'optional':domainType.kind==='list'?'many':domainType.kind==='set'?'many-unique':'one';
  api.body.typed_contract.contracts=api.body.typed_contract.contracts.filter(c=>c.contract_id!=='projection');
  if(publicOutput)api.body.typed_contract.contracts.push({contract_id:'projection',ontology_contract:'TEST-PROJECTION',fields:[{name:'id',ontology_field:'TEST-PROJECTION#id',meaning:'id',type:{kind:'scalar',name:'String'}},{name:'value',ontology_field:'TEST-PROJECTION#value',meaning:'value',type:local(v.output)}]});
  mapping.body.typed_contract.target=publicOutput?{kind:'contract',interface_selector:'alpha:api',contract_id:'projection'}:{kind:'named',selector:'alpha:shapetarget'};mapping.body.target=publicOutput?'alpha:api':'alpha:shapetarget';edge.target_node_id=publicOutput?'api':'shapetarget';fs.writeFileSync(edgeFile,JSON.stringify(edge));fs.writeFileSync(file('api'),JSON.stringify(api));
  mapping.body.typed_contract.inputs[0].type=v.input;mapping.body.typed_contract.fields[1].value=v.expression;
  fs.writeFileSync(file('shapetarget'),JSON.stringify(target));fs.writeFileSync(file('shapes'),JSON.stringify(mapping));let mismatch=null;
  cp.spawnSync=(command,args,settings)=>{if(command===tools.lean_executable)return {status:1,stdout:'',stderr:'isolated shape controls'};
   const result=original(command,args,settings);if(args.includes('--permission')&&result.status===0){
    const planned=JSON.parse(fs.readFileSync(args.find(a=>String(a).endsWith('/cases.json')),'utf8')),observed=JSON.parse(result.stdout);
    for(const row of planned.rows){const o=observed.find(o=>o.selector===row.selector);for(const c of row.cases){const actual=o?.cases.find(x=>x.id===c.id);if(!isDeepStrictEqual(c.expected,actual?.outcome)){mismatch={selector:row.selector,id:c.id,expected:c.expected,actual,recipe:c.values};break;}}if(mismatch)break;}
   }return result;};syncBuiltinESMExports();
  try{const graph=loadCompiledProjectGraph(source),plan=planCompiledReconciledProject(graph,selection),report=executeReconciledVerification(graph,plan,tools);reports.push({index,semantic:report.checks.find(c=>c.id==='selected-generator-semantic-controls'),coverage:report.semantic_coverage.rows.find(r=>r.selector==='alpha:shapes'),mismatch});}finally{cp.spawnSync=original;syncBuiltinESMExports();}
 }console.log(JSON.stringify(reports));`);
 assert.equal(reports.length,variants.length);
 for(const r of reports){assert.equal(r.mismatch,null,JSON.stringify(r));assert.equal(r.coverage.adapter_status,'ready',JSON.stringify(r));assert.equal(r.semantic.executed,true,JSON.stringify(r));assert.ok(r.semantic.evidence.tested.some((x:any)=>x.selector==='alpha:shapes'),JSON.stringify(r));assert.ok(r.semantic.evidence.remaining.some((x:any)=>x.selector==='alpha:component'));}
});
test('native Mappings run while every domain factory, Rule, Calculation and endpoint module is poisoned',t=>{
 const f=fixture(t);f.node('computed','Calculation',{inputs:['left','right'],typed_contract:{schema_version:'domainspec.typed-calculation/v2',ontology_calculation:'TEST-COMPUTED',inputs:['left','right'].map(name=>({name,type:scalar('UInt64')})),result:scalar('UInt64'),division_rounding:'reject',expression:{op:'add',left:{op:'input',name:'left'},right:{op:'input',name:'right'}}}});f.save();
 const n=nativeContext(f),result=n.run(`import assert from 'node:assert/strict';import fs from 'node:fs';import path from 'node:path';import {execFileSync,spawnSync} from 'node:child_process';
 import {loadCompiledProjectGraph,planCompiledReconciledProject} from './dist/index.js';
 const graph=loadCompiledProjectGraph(${JSON.stringify(f.source)}),plan=planCompiledReconciledProject(graph,${JSON.stringify(f.selection)}),tools=${JSON.stringify(n.options)},source=path.resolve('products'),output=path.resolve('compiled-products');fs.mkdirSync(source);fs.writeFileSync(path.join(source,'package.json'),'{"type":"module"}');
 for(const a of plan.resolved.artifacts){const file=path.join(source,a.relative_path);fs.mkdirSync(path.dirname(file),{recursive:true});fs.writeFileSync(file,a.content);}
 const config=path.join(source,'tsconfig.json');fs.writeFileSync(config,JSON.stringify({compilerOptions:{strict:true,skipLibCheck:true,target:'ES2022',module:'NodeNext',moduleResolution:'NodeNext',rootDir:source,outDir:output,types:['node'],typeRoots:[tools.node_type_root]},files:plan.resolved.modules.map(m=>path.join(source,m.relative_path))}));
 execFileSync(process.execPath,[path.join(tools.typescript_root,'bin/tsc'),'--project',config],{encoding:'utf8',timeout:60000});fs.writeFileSync(path.join(output,'package.json'),'{"type":"module"}');
 const poisoned=plan.resolved.modules.filter(m=>m.qualified_selectors.some(s=>!['Mapping','Interface'].includes(graph.nodes.find(n=>n.selector===s).kind)));
 for(const m of poisoned)fs.writeFileSync(path.join(output,m.relative_path.replace(/\\.ts$/,'.js')),'throw new Error("UNDECLARED_MODULE_LOADED");\\n');
 const module=id=>plan.resolved.modules.find(m=>m.qualified_selectors.includes('alpha:'+id)&&m.exports.some(e=>e.name==='mapping'+id[0].toUpperCase()+id.slice(1))),filename=id=>path.join(output,module(id).relative_path.replace(/\\.ts$/,'.js'));
 const client=path.resolve('mapping-client.mjs');fs.writeFileSync(client,'import assert from "node:assert/strict";\\nimport {mappingFull} from '+JSON.stringify(filename('full'))+';\\nimport {mappingOutbound} from '+JSON.stringify(filename('outbound'))+';\\nimport {mappingInbound} from '+JSON.stringify(filename('inbound'))+';\\nconst input={order:{id:"order",amount:"1"},total:"18446744073709551615",memo:null,fallback:"fallback"};const a=mappingFull(input),b=mappingOutbound(input),c=mappingInbound({request:{id:"public",amount:"9007199254740993"}});assert.equal(a.amount,18446744073709551615n);assert.equal(b.amount,a.amount);assert.equal(a.memo,"fallback");assert.equal(c.amount,9007199254740993n);assert.equal(c.memo,null);assert.ok(Object.isFrozen(c));assert.equal("extend" in c,false);input.order.id="changed";assert.equal(a.id,"order");console.log("mapping-isolation-pass");');
 const baseline=execFileSync(process.execPath,[client],{encoding:'utf8',timeout:60000}).trim();
 const provider=path.join(output,module('full').relative_path.replace(/\\.ts$/,'.provider.js')),dependency=path.join(output,poisoned.find(m=>m.qualified_selectors.includes('alpha:computed')).relative_path.replace(/\\.ts$/,'.js'));let specifier=path.relative(path.dirname(provider),dependency).split(path.sep).join('/');if(!specifier.startsWith('.'))specifier='./'+specifier;
 fs.appendFileSync(provider,'\\nimport '+JSON.stringify(specifier)+';\\n');const negative=spawnSync(process.execPath,[client],{encoding:'utf8',timeout:60000});assert.notEqual(negative.status,0);assert.match(negative.stderr,/UNDECLARED_MODULE_LOADED/);
 console.log(JSON.stringify({baseline,poisoned:poisoned.length,negative:true}));`);
 assert.equal(result.baseline,'mapping-isolation-pass');assert.ok(result.poisoned>0);assert.equal(result.negative,true);
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
