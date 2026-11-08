import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {loadCompiledProjectGraph} from '../../src/input/project-model.ts';
import {createCompiledProjectCertificate} from '../../src/compilation/certificate.ts';
import {compileCompositionBoundary,COMPOSITION_BOUNDARY_VERSION,COMPOSITION_BOUNDARY_CONTRACT_SHA256} from '../../src/input/composition-boundary.ts';
import {compileProjectComposition} from '../../src/input/project-composition.ts';
import {compileDeclarativeFunction} from '../../src/typed-backend/declarative-function.ts';
import {planResolvedArtifacts,RESOLVED_ARTIFACT_SELECTION_VERSION,RESOLVED_ARTIFACT_LAYOUT} from '../../src/generation/resolved-artifact-plan.ts';
import {getReconciledSource} from '../../src/generation/reconciled-sources.ts';
import {CONFIGURED_CALCULATION_VERSION} from '../../src/generation/configured-calculations.ts';
import {EXACT_UINT64_PROFILE} from '../../src/generation/exact-uint64.ts';
import {RECONCILED_COMPILATION_VERSION,RECONCILED_TYPESCRIPT_PROFILE} from '../../src/generation/reconciled-project.ts';
import {OPERATION_ACTION_BINDINGS_VERSION} from '../../src/typed-operation/action-bindings.ts';
import {sha256} from '../../src/input/source-manifest.ts';
const sources={configuration:getReconciledSource('configuration'),base:getReconciledSource('base'),typescript:getReconciledSource('typescript'),calculation_contract:getReconciledSource('calculation_v1')};
const scalar=(name:string)=>({kind:'scalar',name});
export function fixture(t:any,options:{valueObject?:boolean;collidingEdges?:boolean}={}){
 const root=fs.mkdtempSync(path.join(os.tmpdir(),'ds-composition-binding-'));
 t.after(()=>fs.rmSync(root,{recursive:true,force:true}));
 const source=path.join(root,'source');
 const write=(p:string,v:unknown)=>{const file=path.join(source,p);fs.mkdirSync(path.dirname(file),{recursive:true});fs.writeFileSync(file,JSON.stringify(v,null,2)+'\n');};
 const manifest={schema_version:'domainspec.project/v2',project_id:'composition-binding',features:['alpha','beta'],cross_feature_edges:[],compositions:[] as string[]};
 const {compositions,...baseManifest}=manifest;
 write('project.json',{...baseManifest,schema_version:'domainspec.project/v1'});
 for(const feature of ['alpha','beta']){
  const edgeId=options.collidingEdges?'compute-calculates-perform':feature+'-compute-calculates-perform';
  const node=(id:string,kind:string,body:unknown)=>write('specs/'+feature+'/nodes/'+id+'.json',{schema_version:'domainspec.node/v1',feature_id:feature,node_id:id,kind,body});
  write('specs/'+feature+'/feature.json',{schema_version:'domainspec.feature/v1',feature_id:feature,nodes:['compute','perform',...(feature==='alpha'?['values',...(options.valueObject?['valid']:[])]:[])],edges:[edgeId]});
  node('perform','Operation',{description:'An explicitly modeled operation, not executed by composition.',reads:[],writes:[],effects:[],guard:'none',failure_continuation:'return-error'});
  node('compute','Calculation',{description:feature,inputs:['left','right'],typed_contract:{schema_version:'domainspec.typed-calculation/v1',ontology_calculation:'TEST-'+feature.toUpperCase(),inputs:['left','right'].map(name=>({name,type:scalar('UInt64')})),result:scalar('UInt64'),division_rounding:'reject',expression:{op:feature==='alpha'?'subtract':'add',left:{op:'input',name:'left'},right:{op:'input',name:'right'}}}});
  if(feature==='alpha'){
   node('values',options.valueObject?'Value Object':'Entity',{description:'Declared request values.',fields:['id','left','right'],...(options.valueObject?{invariant_refs:['alpha:valid']}:{}),typed_contract:{schema_version:'domainspec.typed-record/v1',ontology_node:'TEST-VALUES',properties:['id','left','right'].map(name=>({name,type:scalar(name==='id'?'String':'UInt64'),identity:!options.valueObject&&name==='id',cardinality:'one',meaning:name,ontology_property:'TEST-VALUES#'+name}))}});
   if(options.valueObject)node('valid','Rule',{description:'Declared invariant reference.',predicate:'structured:domainspec.typed-rule/v2',typed_contract:{schema_version:'domainspec.typed-rule/v2',ontology_rule:'TEST-VALID',parameters:[{name:'value',type:scalar('UInt64')}],expression:{op:'eq',left:{op:'path',root:'value',properties:[]},right:{op:'path',root:'value',properties:[]}}}});
  }
  write('specs/'+feature+'/edges/'+edgeId+'.json',{schema_version:'domainspec.edge/v1',feature_id:feature,edge_id:edgeId,relationship:'calculates',source_node_id:'compute',target_node_id:'perform',scope:'feature'});
 }
 const bare=loadCompiledProjectGraph(source);
 const composition=authoredComposition(bare);
 write('compositions/calculate.json',composition);write('project.json',{...manifest,compositions:['calculate']});
 const graph=loadCompiledProjectGraph(source);
 const resolved=(g=graph,module_root='domain',roots=['alpha:compute','beta:compute'])=>{
  const certificate=createCompiledProjectCertificate(g),boundary=compileCompositionBoundary(g,{schema_version:COMPOSITION_BOUNDARY_VERSION,contract_sha256:COMPOSITION_BOUNDARY_CONTRACT_SHA256,graph_sha256:certificate.graph_sha256},getReconciledSource('composition'));
  return planResolvedArtifacts(g,boundary,{schema_version:RESOLVED_ARTIFACT_SELECTION_VERSION,language:'typescript',layout_version:RESOLVED_ARTIFACT_LAYOUT,module_root,graph_sha256:certificate.graph_sha256,boundary_sha256:boundary.boundary_sha256,requests:[{kind:'calculations-v1',fields:null,selection:{schema_version:CONFIGURED_CALCULATION_VERSION,language:'typescript',value_profile:EXACT_UINT64_PROFILE,module_root,boundary_sha256:boundary.boundary_sha256,roots},sources}]},getReconciledSource('resolved_artifact'));
 };
 return {root,source,write,manifest,graph,composition,resolved};
}

export function authoredComposition(graph:ReturnType<typeof loadCompiledProjectGraph>){
 const at=(...p:string[])=>({op:'path',path:p}),call=(name:string,...args:unknown[])=>({op:'call',name,args});
 const contract:any={schema_version:'domainspec.declarative-function/v1',records:{Input:{id:'String',qty:'String',rebate:'String'},Output:{net:'String',other:'String'},Values:{id:'String',qty:'UInt64',rebate:'UInt64'}},roots:{input:'Input'},calculations:{Net:['qty','rebate'],Other:['qty','rebate']},nodes:[
  {id:'Parsed',kind:'Mapping',ontology:'TEST-PARSED',meaning:'Convert declared request fields.',target:'Values',fields:{id:at('input','id'),qty:call('uint64',at('input','qty')),rebate:call('uint64',at('input','rebate'))}},
  {id:'Emit',kind:'Mapping',ontology:'TEST-EMIT',meaning:'Present distinct selected calculations.',target:'Output',fields:{net:call('text',call('Net',at('Parsed','qty'),at('Parsed','rebate'))),other:call('text',call('Other',at('Parsed','qty'),at('Parsed','rebate')))}}
 ],assertions:[],results:[{condition:{op:'literal',value:true},value:at('Emit')}],output:'Output'};
 const model:any={schemas:{Input:{id:{type:'string'},qty:{type:'string'},rebate:{type:'string'}},Output:{net:{type:'string'},other:{type:'string'}}},integrations:{},flows:{},endpoint:{id:'Endpoint',result:'Result',target:'node-http',runtime:'node>=26.8.1',method:'POST',path:'/calculate',input:'Input',output:'Output',authEnv:'TOKEN',maxBytes:1024,timeout:1000,statuses:{ok:200},errors:{},errorStatus:422}};
 const core_bindings:any={Values:{selector:'alpha:values',fields:{id:'id',qty:'left',rebate:'right'}},Net:{selector:'alpha:compute',fields:{qty:'left',rebate:'right'}},Other:{selector:'beta:compute',fields:{qty:'left',rebate:'right'}}};
 const source_text=JSON.stringify(contract,null,2)+'\n',source={path:'contract.json',sha256:sha256(source_text)},location={...source,line:1};
 const ids:any={Input:'TEST-INPUT',Output:'TEST-OUTPUT',Values:'TEST-VALUES',Net:'TEST-ALPHA',Other:'TEST-BETA',Parsed:'TEST-PARSED',Emit:'TEST-EMIT',Endpoint:'TEST-ENDPOINT',Result:'TEST-RESULT'};
 const nodes=Object.keys(ids).map(name=>{
  const binding=core_bindings[name],tc:any=binding?graph.nodes.find(n=>n.selector===binding.selector)!.body.typed_contract:undefined;
  const behavior=contract.nodes.find((n:any)=>n.id===name);
  return {name,id:ids[name],source:location,meaning:{text:behavior?.meaning??name},
   ...(tc?{typed_contract:tc}:{}),...(contract.records[name]?{record_type:contract.records[name]}:{}),
   ...(model.schemas[name]?{constraints:model.schemas[name]}:{}),
   ...(name==='Values'?{properties:Object.entries(binding.fields).map(([field,target])=>{const p=tc.properties.find((p:any)=>p.name===target);return {name:field,ontology:p.ontology_property,meaning:p.meaning};})}:{}),
   ...(contract.calculations[name]?{inputs:contract.calculations[name],result:'UInt64'}:{}),
   ...(behavior?{typed_contract:behavior}:{}),...(name==='Endpoint'?{binding:model.endpoint}:{}),...(name==='Result'?{assertions:[],cases:contract.results}:{})};
 });
 const edges=[['Parsed','Values','maps-to'],['Parsed','Input','depends-on'],['Emit','Output','maps-to'],['Emit','Parsed','depends-on'],['Emit','Net','calls'],['Emit','Other','calls'],['Net','Values','input-type-context'],['Other','Values','input-type-context'],['Endpoint','Result','exposes'],['Endpoint','Input','input'],['Endpoint','Output','output'],['Result','Output','returns'],['Result','Emit','depends-on']];
 const ontology={schema_version:'domainspec.composition-ontology/v1',source_format:'domainspec-json',source,nodes,references:edges.map(([from,to,role])=>({source:ids[from!],target:ids[to!],role,evidence:location})),composition_trace:compileDeclarativeFunction(contract).trace,status:'generated-scaffold',authority_effect:'none',ontology_admitted:false};
 const result={schema_version:'domainspec.project-composition/v1',id:'calculate',source_text,contract,core_bindings,model,bindings:[],ontology};
 compileProjectComposition(result,graph.nodes);
 return result;
}

export function publicFixture(t:any){
 const f=fixture(t,{valueObject:true,collidingEdges:true});
 for(const feature of ['alpha','beta']){
  const prefix='specs/'+feature+'/',manifest=JSON.parse(fs.readFileSync(path.join(f.source,prefix+'feature.json'),'utf8'));
  manifest.nodes.push('allowed');manifest.edges.push('allowed-enforces-perform');f.write(prefix+'feature.json',manifest);
  f.write(prefix+'nodes/allowed.json',{schema_version:'domainspec.node/v1',feature_id:feature,node_id:'allowed',kind:'Rule',body:{description:'Explicit operation guard.',predicate:'structured:domainspec.typed-rule/v2',typed_contract:{schema_version:'domainspec.typed-rule/v2',ontology_rule:'TEST-'+feature.toUpperCase()+'-ALLOWED',parameters:[{name:'value',type:scalar('UInt64')}],expression:{op:'eq',left:{op:'path',root:'value',properties:[]},right:{op:'path',root:'value',properties:[]}}}}});
  f.write(prefix+'edges/allowed-enforces-perform.json',{schema_version:'domainspec.edge/v1',feature_id:feature,edge_id:'allowed-enforces-perform',relationship:'enforces',source_node_id:'allowed',target_node_id:'perform',scope:'feature'});
  const operation=JSON.parse(fs.readFileSync(path.join(f.source,prefix+'nodes/perform.json'),'utf8'));operation.body.guard='allowed';f.write(prefix+'nodes/perform.json',operation);
 }
 return {...f,graph:loadCompiledProjectGraph(f.source)};
}

export function publicSelection(module_root='domain'):any {
 return {schema_version:RECONCILED_COMPILATION_VERSION,profile_id:RECONCILED_TYPESCRIPT_PROFILE,language:'typescript',module_root,layout_version:RESOLVED_ARTIFACT_LAYOUT,value_profile:EXACT_UINT64_PROFILE,field_bindings:[],
  factories:[{selector:'alpha:values',base_validators:[{rule:'alpha:valid',arguments:[{parameter:'value',field:'left'}]}],extensions:[]}],
  operations:['alpha','beta'].map(feature=>({schema_version:OPERATION_ACTION_BINDINGS_VERSION,selector:feature+':perform',inputs:[{name:'amount',type:scalar('UInt64')}],reads:[],writes:[],guards:[{selector:feature+':allowed',arguments:[{parameter:'value',value:{op:'path',root:'amount',properties:[]}}]}],events:[],result:{type:scalar('UInt64'),value:{op:'path',root:'amount',properties:[]}},atomicity:'state-and-outbox',continuation:'awaited-settlement'})),workflows:[]};
}
