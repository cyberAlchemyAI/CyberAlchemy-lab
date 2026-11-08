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
import {planConfiguredMappings,CONFIGURED_MAPPING_VERSION} from '../../src/generation/configured-mappings.ts';
import {decodeTypedInputMappingContract} from '../../src/typed-backend/mapping-inputs.ts';
import {EXACT_UINT64_PROFILE} from '../../src/generation/exact-uint64.ts';
import {planCompiledProjectBuild} from '../../src/generation/project-build.ts';
import {sha256,canonicalJson} from '../../src/input/source-manifest.ts';
const project=path.resolve(import.meta.dirname,'../../../..'),pkg=path.join(project,'development/reconciliation-v1/profile-compiler-reconciliation');
const bytes=(f:string)=>fs.readFileSync(f,'utf8'),read=(f:string)=>JSON.parse(bytes(f));
const sources={configuration:bytes(path.join(pkg,'configuration.json')),base:bytes(path.join(project,'development/implementation-conformance/ontology-experiment/profiles/base-domain.profile.json')),typescript:bytes(path.join(project,'development/implementation-conformance/ontology-experiment/profiles/typescript-strict.profile.json')),mapping_contract:bytes(path.join(pkg,'mapping-generation-contract.json'))};
const boundaryContract=bytes(path.join(project,'development/reconciliation-v1/contracts/composition-boundary.json')),fieldContract=bytes(path.join(project,'development/reconciliation-v1/contracts/exact-field-and-reference-model.json'));
const scalar=(name='String'):any=>({kind:'scalar',name}),named=(id:string):any=>({kind:'named',selector:'alpha:'+id}),wrap=(kind:string,element:any):any=>({kind,element});
const prop=(owner:string,name:string,type:any,identity=false):any=>({ontology_property:'FIXTURE-'+owner+'#'+name,name,type,identity,cardinality:type.kind==='optional'?'optional':type.kind==='list'?'many':type.kind==='set'?'many-unique':'one',meaning:name});
const value=(root:string,...properties:string[]):any=>({op:'path',root,properties}),lit=(type:string,value:string|boolean):any=>({op:'literal',type,value});
const field=(target:string,value:any,fallback:any=null):any=>({target,value,default:fallback});
const choice={kind:'sum',variants:[{name:'None',ontology_variant:'FIXTURE-CHOICE#None',payload:null},{name:'Amount',ontology_variant:'FIXTURE-CHOICE#Amount',payload:scalar('UInt64')},{name:'Money',ontology_variant:'FIXTURE-CHOICE#Money',payload:named('money')}]};
const orderFields=[prop('ORDER','id',scalar(),true),prop('ORDER','amount',scalar('UInt64')),prop('ORDER','enabled',scalar('Bool')),prop('ORDER','memo',wrap('optional',scalar())),prop('ORDER','money',named('money')),prop('ORDER','customer',named('mapping-customer')),prop('ORDER','lines',wrap('list',named('money'))),prop('ORDER','tags',wrap('set',scalar())),prop('ORDER','choice',choice),prop('ORDER','status',named('status'))];
const summaryFields=[...orderFields.map(p=>({...p,ontology_property:'FIXTURE-SUMMARY#'+p.name})),prop('SUMMARY','repeated',scalar('UInt64')),prop('SUMMARY','amounts',wrap('list',scalar('UInt64'))),prop('SUMMARY','unique_amounts',wrap('set',scalar('UInt64'))),prop('SUMMARY','line_amounts',wrap('list',scalar('UInt64'))),prop('SUMMARY','unique_line_amounts',wrap('set',scalar('UInt64')))];
const v2=()=>({schema_version:'domainspec.typed-mapping/v2',ontology_mapping:'FIXTURE-MAPPING',inputs:[{name:'order',type:named('order')},{name:'order_total',type:scalar('UInt64')},{name:'memo',type:wrap('optional',scalar())},{name:'fallback',type:scalar()},{name:'amount_list',type:wrap('list',scalar('UInt64'))}],target:'alpha:summary',fields:[
 ...orderFields.map(p=>field(p.name,p.name==='amount'?value('order_total'):p.name==='memo'?value('memo'):p.name==='status'?{op:'variant',selector:'FIXTURE-STATUS#Ready'}:value('order',p.ontology_property),p.name==='memo'?value('fallback'):null)),
 field('repeated',value('order_total')),field('amounts',value('amount_list')),field('unique_amounts',{op:'to_set',value:value('amount_list')}),field('line_amounts',value('order','FIXTURE-ORDER#lines','FIXTURE-MONEY#amount')),field('unique_line_amounts',{op:'to_set',value:value('order','FIXTURE-ORDER#lines','FIXTURE-MONEY#amount')})
],total:true});
function fixture(t:any){
 const temp=fs.mkdtempSync(path.join(os.tmpdir(),'ds-configured-mapping-'));t.after(()=>fs.rmSync(temp,{recursive:true,force:true}));
 const source=path.join(temp,'source');fs.cpSync(path.join(project,'impl/cli/fixtures/input-roots/canonical-project'),source,{recursive:true});
 const write=(name:string,v:any)=>{const f=path.join(source,name);fs.mkdirSync(path.dirname(f),{recursive:true});fs.writeFileSync(f,JSON.stringify(v));};
 const feature=read(path.join(source,'specs/alpha/feature.json'));
 const node=(id:string,kind:string,body:any)=>{feature.nodes.push(id);write('specs/alpha/nodes/'+id+'.json',{schema_version:'domainspec.node/v1',feature_id:'alpha',node_id:id,kind,body:{description:id,...(kind==='Entity'||kind==='Value Object'?{fields:body.typed_contract.properties.map((p:any)=>p.name)}:kind==='Enum'?{values:body.typed_contract.variants.map((v:any)=>v.name)}:kind==='Rule'?{predicate:'structured:domainspec.typed-rule/v1'}:{}),...body}});};
 const record=(id:string,kind:string,properties:any[])=>node(id,kind,{...(kind==='Value Object'?{invariant_refs:['alpha:valid-mapping-value']}:{}),typed_contract:{schema_version:'domainspec.typed-record/v1',ontology_node:'FIXTURE-'+id.toUpperCase(),properties}});
 node('valid-mapping-value','Rule',{typed_contract:{schema_version:'domainspec.typed-rule/v1',ontology_rule:'FIXTURE-VALID-MAPPING',parameters:[{name:'amount',type:scalar('UInt64')}],expression:{op:'eq',left:{op:'literal',type:'Bool',value:false},right:{op:'literal',type:'Bool',value:true}}}});
 record('money','Value Object',[prop('MONEY','amount',scalar('UInt64')),prop('MONEY','currency',scalar())]);
 record('mapping-customer','Entity',[prop('CUSTOMER','id',scalar(),true),prop('CUSTOMER','label',scalar())]);
 node('status','Enum',{typed_contract:{schema_version:'domainspec.typed-sum/v1',ontology_node:'FIXTURE-STATUS',variants:[{name:'Ready',ontology_variant:'FIXTURE-STATUS#Ready',payload:null},{name:'Draft',ontology_variant:'FIXTURE-STATUS#Draft',payload:null}]}});
 record('order','Entity',orderFields);record('summary','Entity',summaryFields);
 const full=v2(),partial={...v2(),ontology_mapping:'FIXTURE-PARTIAL',fields:[field('memo',value('memo'))],total:false};
 const zero={...v2(),ontology_mapping:'FIXTURE-CONSTANT',inputs:[],fields:[field('id',lit('String','constant')),field('amount',lit('UInt64','18446744073709551615'))],total:false};
 const legacy={schema_version:'domainspec.typed-mapping/v1',ontology_mapping:'FIXTURE-LEGACY',source:'alpha:order',target:'alpha:summary',fields:[{target:'id',source:'id',default:null},{target:'amount',source:'amount',default:null},{target:'memo',source:'memo',default:{type:'String',value:'absent-only'}}],total:false};
 const legacyPartial={...legacy,ontology_mapping:'FIXTURE-LEGACY-PARTIAL',fields:[{target:'memo',source:'memo',default:null}]};
 const contracts:any={full,partial,zero,legacy,'legacy-partial':legacyPartial};
 for(const [id,c]of Object.entries(contracts) as [string,any][]){
  node('map-'+id,'Mapping',{target:c.target,...(c.schema_version.endsWith('/v1')?{source:c.source}:{}),typed_contract:c});
  const edge_id='map-'+id+'-maps-summary';feature.edges.push(edge_id);write('specs/alpha/edges/'+edge_id+'.json',{schema_version:'domainspec.edge/v1',feature_id:'alpha',edge_id,relationship:'maps',source_node_id:'map-'+id,target_node_id:'summary',scope:'feature'});
 }
 write('specs/alpha/feature.json',feature);
 const compile=()=>{
  const graph=loadCompiledProjectGraph(source),graph_sha256=createCompiledProjectCertificate(graph).graph_sha256;
  const boundary=compileCompositionBoundary(graph,{schema_version:COMPOSITION_BOUNDARY_VERSION,contract_sha256:COMPOSITION_BOUNDARY_CONTRACT_SHA256,graph_sha256},boundaryContract);
  const fields=compileSelectedProjectFields(graph,{schema_version:EXACT_PROJECT_FIELD_SELECTION_VERSION,contract_sha256:EXACT_FIELD_CONTRACT_SHA256,graph_sha256,roots:['alpha:order','alpha:summary'],bindings:[]},fieldContract);
  const selection:any={schema_version:CONFIGURED_MAPPING_VERSION,language:'typescript',value_profile:EXACT_UINT64_PROFILE,boundary_sha256:boundary.boundary_sha256,field_compilation_sha256:fields.compilation_sha256,module_root:'commerce',roots:Object.keys(contracts).map(id=>'alpha:map-'+id)};
  return {graph,boundary,fields,selection,plan:()=>planConfiguredMappings(boundary,fields,selection,sources)};
 };
 return {temp,source,write,contracts,compile,...compile()};
}
const money=(amount:any=4)=>({amount,currency:'GBP'});
const order=():any=>({id:'order-1',amount:9,enabled:true,money:money(),customer:{id:'customer',label:'first'},lines:[money(2),money(2),money(1)],tags:['z','a'],choice:{variant:'Money',payload:money('18446744073709551615')},status:{variant:'Draft'}});
const args=():any=>({order:order(),order_total:'18446744073709551615',memo:null,fallback:'fallback',amount_list:['9007199254740993',2,2]});
const frozen=(v:any):void=>{if(v&&typeof v==='object'){assert.ok(Object.isFrozen(v));Object.values(v).forEach(frozen);}};
function native(root:string,plan:ReturnType<typeof planConfiguredMappings>){
 for(const a of plan.artifacts){const f=path.join(root,a.relative_path);fs.mkdirSync(path.dirname(f),{recursive:true});fs.writeFileSync(f,a.content);}
 const toolchain=read(path.resolve(project,'../../toolchains/node-typescript/toolchain.json')),image=nativeToolchainImage(toolchain.container_image);
 const docker=['run','--rm','--pull','never','--network','none','--read-only','--cap-drop','ALL','--security-opt','no-new-privileges','--user',process.getuid!()+':'+process.getgid!(),'--mount','type=bind,source='+root+',target='+root,'--workdir',root,image];
 assert.equal(execFileSync('docker',[...docker,'tsc','--version'],{encoding:'utf8'}).trim(),'Version '+toolchain.typescript);
 const compile=()=>execFileSync('docker',[...docker,'tsc','--ignoreConfig','--strict','--skipLibCheck','--declaration','--target','ES2022','--module','commonjs','--rootDir',path.join(root,plan.selection.module_root,'features'),'--outDir',path.join(root,'js'),...plan.artifacts.map(a=>path.join(root,a.relative_path))],{encoding:'utf8'});compile();
 const module=(id:string)=>plan.modules.find(m=>m.selector==='alpha:map-'+id)!,js=(id:string)=>path.join(root,'js/alpha/src/application/mappings/map-'+id+'.js'),load=(id:string)=>createRequire(import.meta.url)(js(id))[module(id).callable];
 const observe=()=>{
  // Independent expectations describe the authored fixture, not the generated descriptor.
  const fullFields=orderFields.map(p=>({name:p.name,...(p.name==='status'?{pattern:'^R[0-9]+Value\\.normalize\\(\\{variant:"Ready"\\}\\)$'}:{expression:p.name==='amount'?'p1':p.name==='memo'?'(p2 ?? p3)':'p0['+JSON.stringify(p.name)+']'})}));
  const expected=plan.modules.map(m=>{
   const id=m.selector.replace('alpha:map-',''),path=m.provider_path;
   if(id==='zero')return {path,inputs:[],protocols:[],fields:[{name:'id',expression:'"constant"'},{name:'amount',expression:'18446744073709551615n'}]};
   if(id.startsWith('legacy'))return {path,inputs:['source'],protocols:['R[0-9]+Value'],source_fields:orderFields.map(p=>p.name),fields:id==='legacy'?[{name:'id',expression:'p0["id"]'},{name:'amount',expression:'p0["amount"]'},{name:'memo',expression:'(Object.hasOwn(s,"memo")?p0["memo"]:"absent-only")'}]:[{name:'memo',expression:'p0["memo"]',present:'Object.hasOwn(s,"memo")'}]};
   return {path,inputs:['order','order_total','memo','fallback','amount_list'],protocols:['R[0-9]+Value','ruleUInt64','R[0-9]+Value','ruleString','R[0-9]+Value'],fields:id==='partial'?[{name:'memo',expression:'p2'}]:[...fullFields,{name:'repeated',expression:'p1'},{name:'amounts',expression:'p4'},{name:'unique_amounts',expression:'ruleToSet(p4,ruleUInt64)'},{name:'line_amounts',expression:'Object.freeze(p0["lines"].map(q0=>q0["amount"]))'},{name:'unique_line_amounts',expression:'ruleToSet(Object.freeze(p0["lines"].map(q1=>q1["amount"])),ruleUInt64)'}]};
  });
  fs.writeFileSync(path.join(root,'tsconfig.json'),JSON.stringify({compilerOptions:{target:'ES2022',module:'NodeNext',strict:true,noEmit:true},files:expected.map(e=>e.path)}));
  fs.writeFileSync(path.join(root,'expected.json'),JSON.stringify(expected));
  const observer=path.join(project,'impl/cli/tools/observe-configured-mappings.mjs');
  const supportObserver=path.join(project,'impl/cli/tools/structured-rule-support-observer.mjs');
  try{return JSON.parse(execFileSync('docker',[...docker.slice(0,-1),'--mount','type=bind,source='+observer+',target=/observer.mjs,readonly','--mount','type=bind,source='+supportObserver+',target=/structured-rule-support-observer.mjs,readonly',image,'node','/observer.mjs',path.join(root,'tsconfig.json'),path.join(root,'expected.json')],{encoding:'utf8'}));}
  catch(e){const error=e as any;if(error.status===1&&error.stdout)return JSON.parse(error.stdout);throw e;}
 };
 return {compile,module,load,js,root,docker,image,observe};
}
test('total legacy Mapping guards absence and Value Object projection does not construct or enforce invariants',t=>{
 const f=fixture(t);
 const legacy=read(path.join(f.source,'specs/alpha/nodes/map-legacy.json'));
 legacy.body.target='alpha:order';legacy.body.typed_contract.target='alpha:order';
 legacy.body.typed_contract.fields=orderFields.map(p=>({target:p.name,source:p.name,default:null}));legacy.body.typed_contract.total=true;
 f.write('specs/alpha/nodes/map-legacy.json',legacy);
 const edge=read(path.join(f.source,'specs/alpha/edges/map-legacy-maps-summary.json'));
 f.write('specs/alpha/edges/map-legacy-maps-summary.json',{...edge,target_node_id:'order'});
 const originalZero=read(path.join(f.source,'specs/alpha/nodes/map-zero.json')),zero=structuredClone(originalZero);
 zero.body.target='alpha:money';zero.body.typed_contract.target='alpha:money';zero.body.typed_contract.total=true;
 zero.body.typed_contract.fields=[field('amount',lit('UInt64','18446744073709551615')),field('currency',lit('String','GBP'))];
 f.write('specs/alpha/nodes/map-zero.json',zero);
 const zeroEdge=read(path.join(f.source,'specs/alpha/edges/map-zero-maps-summary.json'));
 f.write('specs/alpha/edges/map-zero-maps-summary.json',{...zeroEdge,target_node_id:'money'});
 const projected=f.compile();
 const vo=native(path.join(f.temp,'value-object'),projected.plan());
 assert.deepEqual(vo.load('zero')({}),{amount:18446744073709551615n,currency:'GBP'});
 assert.equal(vo.module('zero').descriptor.target.kind,'Value Object');
 assert.equal(vo.module('zero').descriptor.return_semantics,'field-projection-not-construction');
 // valid-mapping-value is deliberately false: a Mapping must not execute it.
 f.write('specs/alpha/nodes/map-zero.json',originalZero);
 f.write('specs/alpha/edges/map-zero-maps-summary.json',zeroEdge);
 const fresh=f.compile();
 assert.throws(()=>planConfiguredMappings(f.boundary,fresh.fields,{...fresh.selection,boundary_sha256:f.boundary.boundary_sha256},sources),/cross-graph/);
 const n=native(path.join(f.temp,'total'),fresh.plan());
 assert.throws(()=>n.load('legacy')({source:order()}),/MAPPING_REQUIRED_VALUE/);
 assert.equal(n.load('legacy')({source:{...order(),memo:null}}).memo,null);
 assert.deepEqual(n.load('zero')({}),{id:'constant',amount:18446744073709551615n});
 assert.equal(n.module('zero').descriptor.target.kind,'Entity');
 assert.equal(n.module('zero').descriptor.return_semantics,'field-projection-not-construction');
});
test('Mapping planner preserves deterministic selection, exact source binding and legacy rejection boundaries',t=>{
 const f=fixture(t),p=f.plan();assert.equal(p.modules.length,5);assert.equal(p.artifacts.length,10);assert.deepEqual(p,f.plan());
 assert.deepEqual(planConfiguredMappings(f.boundary,f.fields,{...f.selection,roots:[...f.selection.roots].reverse()},sources),p);
 const relocated=planConfiguredMappings(f.boundary,f.fields,{...f.selection,module_root:'another'},sources);assert.deepEqual(relocated.artifacts.map(a=>a.content),p.artifacts.map(a=>a.content));
 const subset=planConfiguredMappings(f.boundary,f.fields,{...f.selection,roots:['alpha:map-full']},sources);assert.deepEqual(subset.artifacts,p.artifacts.filter(a=>a.relative_path.includes('/map-full.')));
 const {plan_sha256,...body}=p;assert.equal(plan_sha256,sha256(canonicalJson(body)));frozen(p);
 for(const m of p.modules){const {descriptor_sha256,...d}=m.descriptor;assert.equal(descriptor_sha256,sha256(canonicalJson(d)));assert.equal(d.provider.sha256,p.artifacts.find(a=>a.relative_path===m.provider_path)!.sha256);assert.equal(d.return_semantics,'field-projection-not-construction');}
 for(const language of ['typescript','python','rust'] as const)assert.throws(()=>planCompiledProjectBuild(f.graph,language),/MTCLI_MAPPING_PROFILE_REQUIRED/);
 assert.throws(()=>planCompiledProjectBuild(f.graph,'typescript',EXACT_UINT64_PROFILE),/MTCLI_EXACT_CONTRACT/);
 fs.renameSync(f.source,path.join(f.temp,'relocated'));assert.deepEqual(p,f.plan());
});
test('Mapping v2 graph checks reject bad field types, paths, defaults, target coverage and invented relationships',t=>{
 const f=fixture(t),original=read(path.join(f.source,'specs/alpha/nodes/map-full.json'));
 for(const mutate of [
  (n:any)=>n.body.source='alpha:order',
  (n:any)=>n.body.target='alpha:order',
  (n:any)=>n.body.typed_contract.fields.pop(),
  (n:any)=>n.body.typed_contract.fields[0].value=value('order','FIXTURE-MISSING#id'),
  (n:any)=>n.body.typed_contract.fields[0].value=value('absent'),
  (n:any)=>n.body.typed_contract.fields[0].value=value('order_total'),
  (n:any)=>n.body.typed_contract.fields[1].default=lit('UInt64','0'),
  (n:any)=>n.body.typed_contract.fields[3].default=lit('Bool',false),
  (n:any)=>n.body.typed_contract.inputs[0].type=named('missing'),
  (n:any)=>n.body.typed_contract.fields[8].value=value('order','FIXTURE-ORDER#customer'),
  (n:any)=>n.body.typed_contract.fields[9].value={op:'variant',selector:'FIXTURE-MISSING#Ready'},
  (n:any)=>n.body.typed_contract.fields[12].value={op:'to_set',value:value('order_total')}
 ]){const n=structuredClone(original);mutate(n);f.write('specs/alpha/nodes/map-full.json',n);assert.throws(()=>loadCompiledProjectGraph(f.source));}
 f.write('specs/alpha/nodes/map-full.json',original);
 const edge=read(path.join(f.source,'specs/alpha/edges/map-full-maps-summary.json'));f.write('specs/alpha/edges/map-full-maps-summary.json',{...edge,relationship:'calculates'});assert.throws(()=>loadCompiledProjectGraph(f.source));f.write('specs/alpha/edges/map-full-maps-summary.json',edge);
 for(const mutate of [(c:any)=>c.inputs.push(c.inputs[0]),(c:any)=>delete c.inputs[0],(c:any)=>c.fields[0].extra=true,(c:any)=>c.fields[0].value=lit('UInt64','018'),(c:any)=>c.fields[0].value={op:'call',name:'Price',args:[]}]){
  const c=v2();mutate(c);assert.throws(()=>decodeTypedInputMappingContract(c));
 }
 let gets=0;const c=v2();Object.defineProperty(c.inputs,'0',{get(){gets++;return {};},enumerable:true});assert.throws(()=>decodeTypedInputMappingContract(c));assert.equal(gets,0);
});
test('Mapping selection rejects forged/stale models, unsafe outputs, source drift and malformed roots',t=>{
 const f=fixture(t);
 for(const patch of [{schema_version:'future'},{language:'rust'},{value_profile:'number'},{boundary_sha256:'stale'},{field_compilation_sha256:'stale'},{module_root:'../escape'},{module_root:'con'},{roots:[]},{roots:['alpha:map-full','alpha:map-full']},{roots:['alpha:order']},{extra:true}])assert.throws(()=>planConfiguredMappings(f.boundary,f.fields,{...f.selection,...patch},sources));
 assert.throws(()=>planConfiguredMappings(structuredClone(f.boundary),f.fields,f.selection,sources));assert.throws(()=>planConfiguredMappings(f.boundary,structuredClone(f.fields),f.selection,sources));
 for(const key of Object.keys(sources))assert.throws(()=>planConfiguredMappings(f.boundary,f.fields,f.selection,{...sources,[key]:(sources as any)[key]+' '}),/source drift/);
 let gets=0;assert.throws(()=>planConfiguredMappings(f.boundary,f.fields,{...f.selection,get roots(){gets++;return [];}},sources));assert.equal(gets,0);
});
test('native Mapping composes explicit exact inputs with nested Entity, Value Object, Enum, sum, list and set values',t=>{
 const f=fixture(t),p=f.plan(),n=native(path.join(f.temp,'native'),p),input=args(),before=structuredClone(input),result=n.load('full')(input);
 assert.equal(result.amount,18446744073709551615n);assert.equal(result.repeated,result.amount);assert.equal(result.memo,'fallback');assert.equal(result.money.amount,4n);assert.equal(result.customer.id,'customer');
 assert.deepEqual(result.status,{variant:'Ready'});assert.equal(result.choice.payload.amount,18446744073709551615n);
 assert.deepEqual(result.amounts,[9007199254740993n,2n,2n]);assert.deepEqual(result.unique_amounts.map(String).sort(),['2','9007199254740993']);assert.deepEqual(result.line_amounts,[2n,2n,1n]);assert.deepEqual(result.unique_line_amounts.map(String).sort(),['1','2']);
 assert.deepEqual(input,before);assert.equal(Object.isFrozen(input.order.money),false);frozen(result);input.order.money.amount=99;assert.equal(result.money.amount,4n);
 assert.deepEqual(Object.keys(result),summaryFields.map(p=>p.name));assert.equal('extend' in result,false,'projection is not an Entity factory product');assert.equal(result.enabled,true,'false Value Object invariant is not executed');
 assert.deepEqual(n.load('zero')({}),{id:'constant',amount:18446744073709551615n});assert.deepEqual(n.load('partial')(args()),{memo:null});
 for(const m of p.modules){const id=m.selector.replace('alpha:map-',''),fn=n.load(id);assert.ok(Object.isFrozen(fn));assert.deepEqual(fn.descriptor,m.descriptor);frozen(fn.descriptor);assert.ok(fs.existsSync(n.js(id).replace(/\.js$/,'.d.ts')));}
 const script='const f=require('+JSON.stringify(n.js('full'))+')['+JSON.stringify(n.module('full').callable)+'];process.stdout.write(JSON.stringify(f('+JSON.stringify(args())+'),(_,v)=>typeof v==="bigint"?v.toString():v));';
 assert.equal(execFileSync(process.execPath,['-e',script],{encoding:'utf8'}),execFileSync(process.execPath,['-e',script],{encoding:'utf8'}));
});
test('legacy Mapping defaults distinguish missing from null and partial output remains partial',t=>{
 const f=fixture(t),n=native(path.join(f.temp,'legacy'),f.plan()),a=order();assert.equal(n.load('legacy')({source:a}).memo,'absent-only');
 assert.equal(n.load('legacy')({source:{...a,memo:null}}).memo,null);assert.equal(n.load('legacy')({source:{...a,memo:''}}).memo,'');
 assert.deepEqual(n.load('legacy-partial')({source:a}),{});assert.deepEqual(n.load('legacy-partial')({source:{...a,memo:null}}),{memo:null});
});
test('Mapping rejects malformed runtime values without invoking getters, coercion, hidden calls or caller writes',t=>{
 const f=fixture(t),n=native(path.join(f.temp,'hostile'),f.plan()),map=n.load('full');let gets=0;
 for(const mutate of [(a:any)=>delete a.order_total,(a:any)=>a.extra=true,(a:any)=>a.order_total=9007199254740992,(a:any)=>a.order_total='18446744073709551616',(a:any)=>a.order_total={valueOf(){gets++;return 1;}},(a:any)=>a.amount_list=[,1],(a:any)=>a.order.tags=['a','a'],(a:any)=>a.order.choice={variant:'Money'},(a:any)=>a.order.customer={label:'no id'},(a:any)=>a.order.extra=true]){
  const a=args();mutate(a);assert.throws(()=>map(a),/MAPPING_INPUT/);
 }
 const a=args();Object.defineProperty(a,'order_total',{get(){gets++;return 1;},enumerable:true});assert.throws(()=>map(a),/MAPPING_INPUT/);assert.equal(gets,0);
 const b=args();Object.defineProperty(b.order,'amount',{get(){gets++;return 1;},enumerable:true});assert.throws(()=>map(b),/MAPPING_INPUT/);assert.equal(gets,0);
 let writes=0;const c=args();c.order=new Proxy(c.order,{set(){writes++;return false;},defineProperty(){writes++;return false;}});map(c);assert.equal(writes,0,'bounded instrumented input observes no write attempt');
});

test('independent native Mapping observation rejects compiling semantic and effect mutations',t=>{
 const f=fixture(t),p=f.plan(),root=path.join(f.temp,'observed'),n=native(root,p);
 assert.equal(n.observe().result,'pass',JSON.stringify(n.observe()));
 const m=n.module('full'),a=p.artifacts.find(a=>a.relative_path===m.provider_path)!;
 const mutants=[
  a.content.replace('const v1 = p1;','const v1 = p0["amount"];'),
  a.content.replace('(p2 ?? p3)','(p2 ?? "changed")'),
  a.content.replace('ruleToSet(p4,ruleUInt64)','p4'),
  a.content.replace('["amount"]:v1','["amount"]:v10 + 1n'),
  a.content.replace('  return Object.freeze({','  Date.now();\n  return Object.freeze({'),
  a.content.replace('  return Object.freeze({','  (globalThis as any).changed=true;\n  return Object.freeze({'),
  a.content.replace('  return Object.freeze({','  queueMicrotask(()=>{});\n  return Object.freeze({'),
  a.content+'const extra=Object.defineProperty(Object.prototype,"changed",{value:true});\n',
  a.content+'const R999Value=Object.freeze(Object.prototype);\n',
  a.content.replace('const d=ruleData(input,["amount","currency"]);','(input as Record<string,unknown>)["amount"]=0n; const d=ruleData(input,["amount","currency"]);')
 ];
 for(const mutant of mutants){
  assert.notEqual(mutant,a.content,'mutation must apply');fs.writeFileSync(path.join(root,m.provider_path),mutant);n.compile();
  assert.equal(n.observe().result,'fail','compiling mutation must fail observation');
 }
});
test('fresh native behavior distinguishes same-type Mapping input substitutions and fallback changes',t=>{
 const f=fixture(t),p=f.plan(),root=path.join(f.temp,'behavior-mutants'),n=native(root,p),m=n.module('full'),a=p.artifacts.find(a=>a.relative_path===m.provider_path)!;
 const run=()=>JSON.parse(execFileSync(process.execPath,['-e','const f=require('+JSON.stringify(n.js('full'))+')['+JSON.stringify(m.callable)+'];process.stdout.write(JSON.stringify(f('+JSON.stringify(args())+'),(_,v)=>typeof v==="bigint"?v.toString():v));'],{encoding:'utf8'}));
 const expected=run();
 for(const mutant of [a.content.replace('const v1 = p1;','const v1 = p0["amount"];'),a.content.replace('(p2 ?? p3)','(p2 ?? "changed")'),a.content.replace('ruleToSet(p4,ruleUInt64)','p4')]){
  assert.notEqual(mutant,a.content);fs.writeFileSync(path.join(root,m.provider_path),mutant);n.compile();assert.notDeepEqual(run(),expected);
 }
});

import {nativeToolchainImage} from '../helpers/native-toolchain-image.ts';
