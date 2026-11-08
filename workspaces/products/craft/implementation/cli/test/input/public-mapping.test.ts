import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import test from 'node:test';
import {decodePublicMapping,checkPublicMapping,PUBLIC_MAPPING_VERSION,PUBLIC_MAPPING_CONTRACT_SHA256} from '../../src/typed-backend/mapping-public.ts';
import {decodeNamedInterface} from '../../src/typed-backend/interface.ts';
import {loadCompiledProjectGraph,selectCompiledProjectNode} from '../../src/input/project-model.ts';
import {compilePublicMapping,assertCheckedPublicMapping} from '../../src/input/compiled-public-mapping.ts';
import {createCompiledProjectCertificate} from '../../src/compilation/certificate.ts';
import {compileCompositionBoundary,COMPOSITION_BOUNDARY_VERSION,COMPOSITION_BOUNDARY_CONTRACT_SHA256} from '../../src/input/composition-boundary.ts';
import {compileSelectedProjectFields,EXACT_PROJECT_FIELD_SELECTION_VERSION,EXACT_FIELD_CONTRACT_SHA256} from '../../src/input/compiled-field-model.ts';
import {planInstantiation} from '../../src/generation/plan-instantiation.ts';
import {createMetaTypeFormalizationProjection} from '../../src/formalization/projection.ts';
import {runInMemoryProject} from '../../src/runtime/in-memory.ts';
import {canonicalJson,sha256} from '../../src/input/source-manifest.ts';

const project=path.resolve(import.meta.dirname,'../../../..');
const read=(p:string)=>fs.readFileSync(path.join(project,'development/reconciliation-v1',p),'utf8');
const definition=read('profile-compiler-reconciliation/public-mapping-contract.json');
const successor=read('profile-compiler-reconciliation/public-mapping-value-object-contract.json');
const scalar=(name='String'):any=>({kind:'scalar',name}),named=(selector='commerce:order'):any=>({kind:'named',selector});
const ref=(contract_id='response',interface_selector='commerce:api'):any=>({kind:'contract',interface_selector,contract_id});
const local=(contract_id='response'):any=>({kind:'contract',contract_id});
const at=(root:string,...properties:string[]):any=>({op:'path',root,properties});
const use=(operation_id='find',side='result'):any=>({interface_selector:'commerce:api',operation_id,side});
const field=(name:string,type:any=scalar()):any=>({name,ontology_field:'TEST-PUBLIC#'+name,meaning:name,type});
function api():any{return {schema_version:'domainspec.typed-interface/v1',ontology_interface:'TEST-API',boundary_kind:'external',version_policy:{schema_version:'domainspec.interface-version-policy/v1',mode:'backward',direction:'consumer-to-provider',provider_version:'1.0.0'},contracts:[{contract_id:'response',ontology_contract:'TEST-RESPONSE',fields:[field('id'),field('total',scalar('UInt64'))]},{contract_id:'shadow',ontology_contract:'TEST-SHADOW',fields:[field('id'),field('total',scalar('UInt64'))]},{contract_id:'empty',ontology_contract:'TEST-EMPTY',fields:[]}],operations:[{operation_id:'find',operation_ref:'commerce:find',request:scalar(),result:local()},{operation_id:'again',operation_ref:'commerce:again',request:scalar(),result:local()}]};}
function entity():any{return {selector:'commerce:order',kind:'Entity',contract:{schema_version:'domainspec.typed-record/v1',ontology_node:'TEST-ORDER',properties:[{name:'id',ontology_property:'TEST-ORDER#id',type:scalar(),cardinality:'one',identity:true,meaning:'identity'}]}};}
function mapping():any{return {schema_version:PUBLIC_MAPPING_VERSION,ontology_mapping:'TEST-SUMMARY',inputs:[{name:'order',type:named(),use:null},{name:'total',type:scalar('UInt64'),use:null}],target:ref(),target_use:use(),fields:[{target:'id',value:at('order','TEST-ORDER#id'),default:null},{target:'total',value:at('total'),default:null}],total:true};}
const check=(m:any=mapping(),a:any=api(),declarations:any[]=[entity()])=>checkPublicMapping(decodePublicMapping(m),declarations,[{selector:'commerce:api',contract:decodeNamedInterface(a)}]);
function fixture(t:any,m=mapping(),a=api()){
 const folder=fs.mkdtempSync(path.join(os.tmpdir(),'ds-public-mapping-'));t.after(()=>fs.rmSync(folder,{recursive:true,force:true}));
 const nodes:string[]=[],edges:string[]=[];
 const write=(p:string,v:any)=>{const file=path.join(folder,p);fs.mkdirSync(path.dirname(file),{recursive:true});fs.writeFileSync(file,JSON.stringify(v,null,2)+'\n');};
 const node=(id:string,kind:string,body:any)=>{if(!nodes.includes(id))nodes.push(id);write('specs/commerce/nodes/'+id+'.json',{schema_version:'domainspec.node/v1',feature_id:'commerce',node_id:id,kind,body:{description:id,...body}});};
 const edge=(id:string,relationship:string,from:string,to:string)=>{if(!edges.includes(id))edges.push(id);write('specs/commerce/edges/'+id+'.json',{schema_version:'domainspec.edge/v1',feature_id:'commerce',edge_id:id,relationship,source_node_id:from,target_node_id:to,scope:'feature'});};
 node('order','Entity',{fields:['id'],typed_contract:entity().contract});
 node('api','Interface',{typed_contract:a});
 for(const id of ['find','again']){node(id,'Query',{reads:['order']});edge('api-'+id,'exposes','api',id);}
 node('summary','Mapping',{target:m.target.kind==='named'?m.target.selector:m.target.interface_selector,typed_contract:m});edge('summary-target','maps','summary',m.target.kind==='named'?'order':'api');
 const save=()=>{write('project.json',{schema_version:'domainspec.project/v1',project_id:'public-mapping',features:['commerce'],cross_feature_edges:[]});write('specs/commerce/feature.json',{schema_version:'domainspec.feature/v1',feature_id:'commerce',nodes,edges});};save();
 const compile=()=>{const graph=loadCompiledProjectGraph(folder),graph_sha256=createCompiledProjectCertificate(graph).graph_sha256;
  const boundary=compileCompositionBoundary(graph,{schema_version:COMPOSITION_BOUNDARY_VERSION,contract_sha256:COMPOSITION_BOUNDARY_CONTRACT_SHA256,graph_sha256},read('contracts/composition-boundary.json'));
  const fields=compileSelectedProjectFields(graph,{schema_version:EXACT_PROJECT_FIELD_SELECTION_VERSION,contract_sha256:EXACT_FIELD_CONTRACT_SHA256,graph_sha256,roots:['commerce:order'],bindings:[]},read('contracts/exact-field-and-reference-model.json'));
  return {graph,boundary,fields,check:(d=definition)=>compilePublicMapping(graph,boundary,fields,'commerce:summary',d)};};
 return {folder,nodes,edges,node,edge,write,save,compile};
}

test('definition-bound Mapping preserves public identity and explicitly supplied calculations without graph additions',t=>{
 assert.equal(sha256(definition),PUBLIC_MAPPING_CONTRACT_SHA256);const f=fixture(t),c=f.compile(),before=canonicalJson(c.graph),value=c.check();assertCheckedPublicMapping(value);
 assert.deepEqual(c.check(),value);assert.equal(canonicalJson(c.graph),before);assert.equal(value.bindings.effect_contract,'pure-explicit-projection');
 assert.deepEqual(value.bindings.target,ref());assert.equal(value.bindings.target_member!.operation_ref,'commerce:find');
 assert.deepEqual(value.bindings.inputs.map(i=>i.name),['order','total']);assert.equal(c.graph.relationships.length,3);
 assert.deepEqual(c.graph.relationships.map(r=>r.relationship).sort(),['exposes','exposes','maps']);
 assert.equal(value.authority_effect,'none');const {mapping_sha256,...body}=value;assert.equal(mapping_sha256,sha256(canonicalJson(body)));
 assert.ok(Object.isFrozen(value.bindings.fields));assert.throws(()=>assertCheckedPublicMapping(structuredClone(value)),/unregistered/);
 fs.renameSync(f.folder,f.folder+'-moved');t.after(()=>fs.rmSync(f.folder+'-moved',{recursive:true,force:true}));assert.deepEqual(c.check(),value);
});
test('shared contract member uses remain distinct bindings but do not change contract identity',()=>{
 const m=mapping(),first=check(m);m.target_use=use('again');const second=check(m);assert.deepEqual(first.target,second.target);assert.notDeepEqual(first.target_member,second.target_member);
 m.target=ref('shadow');assert.throws(()=>check(m),/member position/);m.target_use=null;assert.deepEqual(check(m).target,ref('shadow'));
 const a=api();a.operations[0].result={kind:'optional',element:local()};assert.throws(()=>check(mapping(),a),/member position/);
 m.target=ref();m.target_use=null;m.inputs.push({name:'maybe',type:{kind:'optional',element:ref()},use:use()});assert.doesNotThrow(()=>check(m,a));
 m.fields[0].value=at('maybe','TEST-PUBLIC#id');assert.throws(()=>check(m,a),/no implicit unwrap/);
});
test('inbound public Mapping projects an Entity without adding persistence or factory effects',t=>{
 const m=mapping();m.inputs=[{name:'request',type:ref(),use:use()}];m.target=named();m.target_use=null;m.fields=[{target:'id',value:at('request','TEST-PUBLIC#id'),default:null}];
 const c=fixture(t,m).compile().check();assert.equal(c.target_owner,'commerce:order');assert.deepEqual(c.bindings.interface_selectors,['commerce:api']);assert.equal(c.bindings.fields[0]!.target.ontology_property,'TEST-ORDER#id');
});
test('Value Object target requires the exact successor and remains pure projection',t=>{
 const m=mapping();m.inputs=[{name:'request',type:ref(),use:use()}];m.target=named();m.target_use=null;m.fields=[{target:'id',value:at('request','TEST-PUBLIC#id'),default:null}];
 const f=fixture(t,m),contract=entity().contract;contract.properties[0].identity=false;
 f.node('order','Value Object',{fields:['id'],invariant_refs:['commerce:valid'],typed_contract:contract});
 f.node('valid','Rule',{predicate:'explicit invariant'});f.save();
 const c=f.compile();
 assert.throws(()=>c.check(),/target must be Entity or Interface/);
 assert.throws(()=>c.check(successor+' '),/definition drift/);
 const mapped=c.check(successor);
 assert.equal(mapped.definition_sha256,sha256(successor));
 assert.equal(mapped.bindings.effect_contract,'pure-explicit-projection');
 assert.equal(mapped.runtime_execution,'not-performed');
 assert.deepEqual(mapped.bindings.target,named());
 assert.equal(sha256(definition),PUBLIC_MAPPING_CONTRACT_SHA256);
});
test('qualified public identity cannot collapse across Interfaces or same-shaped contracts',()=>{
 const a=api(),b=api();b.ontology_interface='TEST-OTHER';const m=mapping();m.inputs=[{name:'source',type:ref('response','commerce:other'),use:use()}];m.target=ref('empty');m.target_use=null;m.fields=[];
 assert.throws(()=>checkPublicMapping(decodePublicMapping(m),[entity()],[{selector:'commerce:api',contract:decodeNamedInterface(a)},{selector:'commerce:other',contract:decodeNamedInterface(b)}]),/member position/);
 const nested=api();nested.contracts[0].fields.push(field('child',local('empty')));m.inputs=[{name:'source',type:ref(),use:null}];m.target=ref();m.fields=[...mapping().fields,{target:'child',value:at('source','TEST-PUBLIC#child'),default:null}];m.inputs.push(...mapping().inputs);assert.equal((check(m,nested).fields[2]!.value_type as any).interface_selector,'commerce:api');
});
test('public closure rejects direct and transitive Entity leakage and unresolved or recursive contracts',()=>{
 const a=api();a.contracts[0].fields[0].type=named();assert.throws(()=>check(mapping(),a),/Entity snapshot leak/);
 a.contracts[0].fields[0].type=named('commerce:wrapper');const wrapper:any={selector:'commerce:wrapper',kind:'Value Object',contract:{properties:[{type:named()}]}};assert.throws(()=>check(mapping(),a,[entity(),wrapper]),/Entity snapshot leak/);
 assert.throws(()=>check(mapping(),a),/unresolved domain value/);a.contracts[0].fields[0].type=local();assert.throws(()=>check(mapping(),a),/cycl|recurs/i);
 a.contracts[0].fields[0].type=local('missing');assert.throws(()=>check(mapping(),a));
});
test('total coverage, typed defaults, optional lifting, collection kinds and empty contracts stay explicit',()=>{
 const m=mapping();m.fields.pop();assert.throws(()=>check(m),/total field coverage/);m.total=false;assert.doesNotThrow(()=>check(m));
 m.total=true;m.target=ref('empty');m.target_use=null;m.fields=[];assert.deepEqual(check(m).fields,[]);
 const a=api();a.contracts[0].fields[1].type={kind:'set',element:scalar('UInt64')};const c=mapping();c.inputs[1].type={kind:'list',element:scalar('UInt64')};assert.throws(()=>check(c,a),/field type mismatch/);c.fields[1].value={op:'to_set',value:at('total')};assert.equal(check(c,a).fields[1]!.value_type.kind,'set');
 const d=mapping();d.inputs[1].type={kind:'optional',element:scalar('UInt64')};d.fields[1].default={op:'literal',type:'UInt64',value:'18446744073709551615'};assert.doesNotThrow(()=>check(d));d.fields[1].default={op:'literal',type:'String',value:'wrong'};assert.throws(()=>check(d),/default type/);
});
test('closed decoder rejects accessors, sparse lists, depth, duplicates and hidden behavior without invoking it',()=>{
 for(const mutate of [(m:any)=>m.extra=true,(m:any)=>m.inputs.push(m.inputs[0]),(m:any)=>m.fields.push(m.fields[0]),(m:any)=>delete m.inputs[0],(m:any)=>m.target_use.side='event',(m:any)=>m.fields[0].value={op:'call',selector:'commerce:calculate'},(m:any)=>m.inputs[0].name+='\n',(m:any)=>{for(let i=0;i<20;i++)m.inputs[0].type={kind:'list',element:m.inputs[0].type};}]){const m=mapping();mutate(m);assert.throws(()=>decodePublicMapping(m));}
 let reads=0;const m=mapping();Object.defineProperty(m,'inputs',{enumerable:true,get(){reads++;return [];}});assert.throws(()=>decodePublicMapping(m));assert.equal(reads,0);
 const source=mapping(),before=canonicalJson(source),decoded=decodePublicMapping(source);assert.equal(canonicalJson(source),before);assert.equal(Object.isFrozen(source.inputs),false);source.inputs[0].name='changed';assert.equal(decoded.inputs[0]!.name,'order');
});
test('shared Value Objects, Enum variants, sums and collection paths keep their declared kinds',()=>{
 const a=api(),m=mapping();const money:any={selector:'commerce:money',kind:'Value Object',contract:{schema_version:'domainspec.typed-record/v1',ontology_node:'TEST-MONEY',properties:[{name:'amount',ontology_property:'TEST-MONEY#amount',type:scalar('UInt64'),cardinality:'one',identity:false,meaning:'amount'}]}};
 const status:any={selector:'commerce:status',kind:'Enum',contract:{schema_version:'domainspec.typed-sum/v1',ontology_node:'TEST-STATUS',variants:[{name:'Ready',ontology_variant:'TEST-STATUS#Ready',payload:null}]}};
 const sum={kind:'sum',variants:[{name:'None',ontology_variant:'TEST-CHOICE#None',payload:null},{name:'Some',ontology_variant:'TEST-CHOICE#Some',payload:local('empty')}]};
 a.contracts[0].fields.push(field('money',named('commerce:money')),field('status',named('commerce:status')),field('choice',sum),field('ids',{kind:'list',element:scalar()}));
 m.inputs.push({name:'source',type:ref(),use:null},{name:'rows',type:{kind:'list',element:ref()},use:null});
 m.fields.push(...['money','choice'].map(target=>({target,value:at('source','TEST-PUBLIC#'+target),default:null})),{target:'status',value:{op:'variant',selector:'TEST-STATUS#Ready'},default:null},{target:'ids',value:at('rows','TEST-PUBLIC#id'),default:null});
 const bindings=check(m,a,[entity(),money,status]);assert.equal(bindings.fields.find(f=>f.target.name==='choice')!.value_type.kind,'sum');assert.deepEqual(bindings.fields.find(f=>f.target.name==='ids')!.value_type,{kind:'list',element:scalar()});assert.deepEqual(bindings.domain_selectors,['commerce:order','commerce:status']);
 m.inputs[3].type.kind='set';assert.throws(()=>check(m,a,[entity(),money,status]),/field type mismatch:ids/);
 const empty=mapping();empty.target=ref('empty');empty.target_use=null;empty.fields=[];empty.inputs=[];const b=api();b.contracts[0].fields[0].type=named('commerce:money');assert.throws(()=>check(empty,b),/unresolved domain value/);
});
test('graph admission requires exact maps owner and exposes closure',t=>{
 const f=fixture(t);f.edge('summary-target','maps','summary','order');assert.throws(()=>f.compile(),/maps/);
 f.edge('summary-target','maps','summary','api');f.edges.splice(f.edges.indexOf('api-again'),1);f.save();assert.throws(()=>f.compile(),/exposes/);
});
test('registered graph, boundary, exact fields and definition cannot be forged or mixed',t=>{
 const f=fixture(t),c=f.compile();assert.throws(()=>c.check(definition+' '),/definition drift/);
 for(const [g,b,p] of [[structuredClone(c.graph),c.boundary,c.fields],[c.graph,structuredClone(c.boundary),c.fields],[c.graph,c.boundary,structuredClone(c.fields)]])assert.throws(()=>compilePublicMapping(g as any,b as any,p as any,'commerce:summary',definition));
 f.node('find','Query',{description:'source change',reads:['order']});const other=f.compile();assert.throws(()=>compilePublicMapping(other.graph,c.boundary,c.fields,'commerce:summary',definition),/cross-graph/);assert.notEqual(c.check().mapping_sha256,other.check().mapping_sha256);
});
test('legacy generation and formalization cannot silently accept the new public Mapping version',t=>{
 const c=fixture(t).compile(),node=selectCompiledProjectNode(c.graph,'commerce:summary');for(const language of ['typescript','python','rust'] as const)assert.throws(()=>planInstantiation(node,language));
 assert.throws(()=>createMetaTypeFormalizationProjection(c.graph));
});
test('legacy rejection belongs to Mapping itself, even without a named Interface in the graph',t=>{
 const m=mapping();m.target=named();m.target_use=null;m.fields=[m.fields[0]];const f=fixture(t,m);
 f.nodes.splice(f.nodes.indexOf('api'),1);f.edges.splice(f.edges.indexOf('api-find'),1);f.edges.splice(f.edges.indexOf('api-again'),1);f.save();
 const c=f.compile(),node=selectCompiledProjectNode(c.graph,'commerce:summary');
 for(const language of ['typescript','python','rust'] as const)assert.throws(()=>planInstantiation(node,language));
 assert.throws(()=>runInMemoryProject(f.folder,{schema_version:'domainspec.runtime-invocation/v1',invocation_id:'public-mapping',provider:'in-memory-v1',steps:[{step_id:'map',selector:'commerce:summary',input:{source:{id:'x'}}}]}),(error:any)=>error.code==='MTCLI_MAPPING_PROFILE_REQUIRED');
 assert.throws(()=>createMetaTypeFormalizationProjection(c.graph),/MAPPING.*UNSUPPORTED|Mapping.*successor/);
});
