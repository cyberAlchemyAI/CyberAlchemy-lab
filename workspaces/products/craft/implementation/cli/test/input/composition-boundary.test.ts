import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import test from 'node:test';
import {fileURLToPath} from 'node:url';
import {loadCompiledProjectGraph} from '../../src/input/project-model.ts';
import {createCompiledProjectCertificate} from '../../src/compilation/certificate.ts';
import {compileCompositionBoundary,assertCompiledCompositionBoundary,COMPOSITION_BOUNDARY_VERSION,COMPOSITION_BOUNDARY_CONTRACT_SHA256} from '../../src/input/composition-boundary.ts';
import {compileDeclarativeFunction} from '../../src/typed-backend/declarative-function.ts';
import {normalizeCompositionOntology} from '../../src/input/composition-ontology.ts';
import {canonicalJson,sha256} from '../../src/input/source-manifest.ts';

const project=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../../../..');
const descriptor=fs.readFileSync(path.join(project,'development/reconciliation-v1/contracts/composition-boundary.json'),'utf8');
const scalar={kind:'scalar',name:'UInt64'};
const priceRecord={schema_version:'domainspec.typed-record/v1',ontology_node:'FIXTURE-PRICE-INPUT',
  properties:[{ontology_property:'FIXTURE-PRICE-INPUT#amount',name:'amount',type:scalar,cardinality:'one',identity:true,meaning:'Amount'}]};
const calculation={schema_version:'domainspec.typed-calculation/v1',ontology_calculation:'FIXTURE-TOTAL',inputs:[{name:'amount',type:scalar}],result:scalar,division_rounding:'reject',expression:{op:'multiply',left:{op:'input',name:'amount'},right:{op:'literal',value:2}}};
const expr=(name:string,...args:any[])=>({op:'call',name,args});
const param=(...parts:string[])=>({op:'path',path:parts});
function composition(id='copy'){
  const c:any={schema_version:'domainspec.declarative-function/v1',records:{Input:{value:'String'},Output:{value:'String'},PriceInput:{amount:'UInt64'}},
    roots:{input:'Input'},calculations:{Total:['amount']},nodes:[{id:'Emit',kind:'Mapping',ontology:'TEST-EMIT',meaning:'Format the supplied computed value.',
      input:{name:'computed',type:'UInt64'},target:'Output',fields:{value:expr('text',param('computed'))}}],
    assertions:[],results:[{condition:{op:'literal',value:true},value:expr('Emit',expr('Total',expr('uint64',param('input','value'))))}],output:'Output'};
  const model:any={schemas:{Input:{value:{type:'string'}},Output:{value:{type:'string'}}},integrations:{},flows:{},
    endpoint:{id:'Endpoint',result:'Result',target:'node-http',runtime:'node>=26.8.1',method:'POST',path:'/copy',input:'Input',output:'Output',authEnv:'TOKEN',maxBytes:1024,timeout:1000,statuses:{ok:200},errors:{},errorStatus:422}};
  const source_text=JSON.stringify(c,null,2)+'\n',source={path:'contract.json',sha256:sha256(source_text)},location={...source,line:1};
  const nodeId=(name:string)=>name==='PriceInput'?'FIXTURE-PRICE-INPUT':name==='Total'?'FIXTURE-TOTAL':'TEST-'+name.toUpperCase();
  const nodes=['Input','Output','PriceInput','Total','Emit','Endpoint','Result'].map(name=>({name,id:nodeId(name),source:location,
    meaning:{text:name==='Emit'?c.nodes[0].meaning:name},
    ...(name==='Input'||name==='Output'?{record_type:c.records[name],constraints:model.schemas[name]}:{}),
    ...(name==='PriceInput'?{record_type:c.records[name],typed_contract:priceRecord,properties:[{name:'amount',ontology:'FIXTURE-PRICE-INPUT#amount',meaning:'Amount'}]}:{}),
    ...(name==='Total'?{typed_contract:calculation,inputs:['amount'],result:'UInt64'}:{}),
    ...(name==='Emit'?{typed_contract:c.nodes[0]}:{}),...(name==='Endpoint'?{binding:model.endpoint}:{}),
    ...(name==='Result'?{assertions:[],cases:c.results}:{})}));
  const references=[['Emit','Output','maps-to'],['Endpoint','Result','exposes'],['Endpoint','Input','input'],['Endpoint','Output','output'],['Result','Output','returns'],
    ['Result','Emit','calls'],['Result','Total','calls'],['Result','Input','depends-on'],['Total','PriceInput','input-type-context']].map(([from,to,role])=>({source:nodeId(from!),target:nodeId(to!),role,evidence:location}));
  const ontology={schema_version:'domainspec.composition-ontology/v1',source_format:'domainspec-json',source,nodes,references,composition_trace:compileDeclarativeFunction(c).trace,status:'generated-scaffold',authority_effect:'none',ontology_admitted:false};
  return {schema_version:'domainspec.project-composition/v1',id,source_text,contract:c,core_bindings:{PriceInput:{selector:'alpha:price-input',fields:{amount:'amount'}},Total:{selector:'alpha:total',fields:{amount:'amount'}}},model,bindings:[],ontology};
}
function fixture(t:any,id='copy'){
  const temp=fs.mkdtempSync(path.join(os.tmpdir(),'ds-boundary-'));t.after(()=>fs.rmSync(temp,{recursive:true,force:true}));
  const source=path.join(temp,'source');fs.cpSync(path.join(project,'impl/cli/fixtures/input-roots/canonical-project'),source,{recursive:true});
  const json=(p:string)=>JSON.parse(fs.readFileSync(path.join(source,p),'utf8'));
  const write=(p:string,v:any)=>{const f=path.join(source,p);fs.mkdirSync(path.dirname(f),{recursive:true});fs.writeFileSync(f,JSON.stringify(v,null,2)+'\n');};
  const feature=json('specs/alpha/feature.json');feature.nodes.push('price-input','total','positive','can-price');feature.edges.push('total-calculates-settle');write('specs/alpha/feature.json',feature);
  const node=(node_id:string,kind:string,body:any)=>write('specs/alpha/nodes/'+node_id+'.json',{schema_version:'domainspec.node/v1',feature_id:'alpha',node_id,kind,body:{description:node_id,...body}});
  node('price-input','Entity',{fields:['amount'],typed_contract:priceRecord});
  node('total','Calculation',{inputs:['amount'],typed_contract:calculation});
  for(const id of ['positive','can-price'])node(id,'Rule',{predicate:'structured:domainspec.typed-rule/v1',typed_contract:{schema_version:'domainspec.typed-rule/v1',ontology_rule:'FIXTURE-'+id.toUpperCase(),
    parameters:[{name:'amount',type:scalar}],expression:id==='positive'?{op:'lt',left:{op:'literal',type:'UInt64',value:0},right:{op:'path',root:'amount',properties:[]}}:
      {op:'rule_ref',selector:'alpha:positive',arguments:[{parameter:'amount',value:{op:'path',root:'amount',properties:[]}}]}}});
  write('specs/alpha/edges/total-calculates-settle.json',{schema_version:'domainspec.edge/v1',edge_id:'total-calculates-settle',feature_id:'alpha',relationship:'calculates',source_node_id:'total',target_node_id:'settle',scope:'feature'});
  const manifest=json('project.json');write('project.json',{...manifest,schema_version:'domainspec.project/v2',compositions:[id]});
  write('compositions/'+id+'.json',composition(id));
  const graph=loadCompiledProjectGraph(source);
  const selection={schema_version:COMPOSITION_BOUNDARY_VERSION,contract_sha256:COMPOSITION_BOUNDARY_CONTRACT_SHA256,graph_sha256:createCompiledProjectCertificate(graph).graph_sha256} as const;
  return {temp,source,json,write,graph,selection,run:()=>compileCompositionBoundary(graph,selection,descriptor)};
}

test('DSR-011 projects checked domain references and value contracts without cross-plane promotion',t=>{
  const f=fixture(t),b=f.run();
  assert.equal(b.coverage.domain_nodes,f.graph.nodes.length);assert.equal(b.coverage.domain_relationships,f.graph.relationships.length);
  assert.equal(b.coverage.compositions,1);assert.equal(b.coverage.composition_nodes,7);assert.equal(b.coverage.composition_references,9);
  assert.equal(b.coverage.bridges,2);assert.equal(b.coverage.core_typed_contracts+b.coverage.untyped_domain_nodes,b.coverage.domain_nodes);
  assert.deepEqual(b.domain_graph.relationships.map(({source_evidence,...edge})=>edge).sort((a,b)=>canonicalJson(a).localeCompare(canonicalJson(b))),[...f.graph.relationships].sort((a,b)=>canonicalJson(a).localeCompare(canonicalJson(b))));
  assert.ok(b.composition_graphs[0]!.references.some(r=>r.role==='maps-to'));
  assert.ok(b.composition_graphs[0]!.references.some(r=>r.role==='calls'));
  assert.ok(b.domain_graph.relationships.some(r=>r.relationship==='calculates'));
  assert.ok(b.domain_graph.relationships.every(r=>!['calls','maps-to','maps-from','depends-on'].includes(r.relationship)));
  const rules=b.value_bindings.core_contracts.find(r=>r.owner.selector==='alpha:can-price')!;
  assert.equal((rules.contract as any).expression.op,'rule_ref');
  assert.equal((rules.contract as any).expression.arguments[0].parameter,'amount');
  assert.equal(b.domain_graph.relationships.some(r=>r.source.node_id==='can-price'),false,'Rule value binding does not invent a domain edge');
  const c=b.value_bindings.composition_contracts[0]!.contract;
  assert.deepEqual(c.nodes[0].fields,{value:expr('text',param('computed'))},'mapper uses its argument, not a hidden Calculation');
  assert.deepEqual(c.results[0].value,expr('Emit',expr('Total',expr('uint64',param('input','value')))));
  assert.equal(b.authority_effect,'none');assert.equal(b.validation_ceiling,'checked-source-projection-not-execution-or-new-type-proof');
  const {boundary_sha256,...body}=b;assert.equal(boundary_sha256,sha256(canonicalJson(body)));
  assert.doesNotThrow(()=>assertCompiledCompositionBoundary(b));
  assert.throws(()=>assertCompiledCompositionBoundary(structuredClone(b)),/unvalidated boundary/);
});

test('DSR-011 identities are source scoped and bridges require explicit core bindings',t=>{
  const f=fixture(t),g=fixture(t,'other'),b=f.run(),a=b.composition_graphs[0]!,other=g.run().composition_graphs[0]!;
  assert.equal(a.nodes[0]!.identity.local_id,other.nodes[0]!.identity.local_id);
  assert.notDeepEqual(a.nodes[0]!.identity,other.nodes[0]!.identity);
  assert.equal(b.coverage.bridges,2);assert.equal(b.bridges.filter(r=>r.target.selector==='alpha:total').length,1);
  assert.notDeepEqual(b.bridges[0]!.source,g.run().bridges[0]!.source);
  assert.ok(b.bridges.every(r=>r.evidence.pointer.startsWith('/core_bindings/')));
  assert.equal(b.bridges.some(r=>r.source.name==='Emit'),false);
  for(const e of b.domain_graph.relationships)assert.equal(e.source_evidence.sha256,f.graph.source_manifest.sources.find(s=>s.relative_path===e.source_evidence.relative_path)!.sha256);
  assert.ok(Object.isFrozen(b.value_bindings.composition_contracts[0]!.contract.nodes[0].fields));
  assert.throws(()=>{(b.bridges[0]!.fields as any).amount='changed';},TypeError);
});

test('DSR-011 deterministic checked snapshots survive source removal and retain distinct source provenance',t=>{
  const f=fixture(t),b=f.run();assert.deepEqual(f.run(),b);
  const moved=path.join(f.temp,'moved');fs.renameSync(f.source,moved);
  assert.deepEqual(f.run(),b);
  const relocated=loadCompiledProjectGraph(moved);assert.deepEqual(compileCompositionBoundary(relocated,f.selection,descriptor),b);
  assert.throws(()=>compileCompositionBoundary(structuredClone(f.graph),f.selection,descriptor),/unvalidated|changed/);
  const source=f.graph.compositions![0]!.source;
  assert.equal(source.ontology.schema_version,'domainspec.composition-ontology/v1');
  assert.deepEqual(normalizeCompositionOntology(source.ontology),source.ontology);
});

test('DSR-011 selection is closed, inert and bound to exact sources',t=>{
  const f=fixture(t);let calls=0;
  const accessor=Object.defineProperty({...f.selection},'graph_sha256',{enumerable:true,get(){calls++;return f.selection.graph_sha256;}});
  for(const selection of [accessor,{...f.selection,extra:true},{...f.selection,graph_sha256:'0'.repeat(64)},{...f.selection,schema_version:'future'},Object.assign(Object.create(f.selection),{})]){
    assert.throws(()=>compileCompositionBoundary(f.graph,selection as any,descriptor),/DS_COMPOSITION_BOUNDARY/);
  }
  assert.equal(calls,0);assert.throws(()=>compileCompositionBoundary(f.graph,f.selection,descriptor+' '),/contract drift/);
  assert.throws(()=>compileCompositionBoundary(f.graph,{...f.selection,contract_sha256:'0'.repeat(64)} as any,descriptor),/contract drift/);
});

test('DSR-011 removing a lawful Calculation edge is not repaired by a composition call',t=>{
  const f=fixture(t),feature=f.json('specs/alpha/feature.json');
  feature.edges=feature.edges.filter((id:string)=>id!=='total-calculates-settle');f.write('specs/alpha/feature.json',feature);
  fs.unlinkSync(path.join(f.source,'specs/alpha/edges/total-calculates-settle.json'));
  assert.throws(()=>loadCompiledProjectGraph(f.source),/Calculation requires|calculates/);
});

test('DSR-011 forged roles and core bridges fail in the existing compiler before projection',t=>{
  for(const mutate of [
    (s:any)=>s.ontology.references.find((r:any)=>r.role==='calls').role='calculates',
    (s:any)=>s.core_bindings.Total.selector='alpha:settle',
    (s:any)=>delete s.core_bindings.Total,
    (s:any)=>s.ontology.ontology_admitted=true,
    (s:any)=>s.ontology.references.push(structuredClone(s.ontology.references[0])),
  ]){
    const f=fixture(t),s=f.json('compositions/copy.json');mutate(s);f.write('compositions/copy.json',s);
    assert.throws(()=>loadCompiledProjectGraph(f.source),/DS_PROJECT_COMPOSITION/);
  }
});

test('DSR-011 projection does not change compiled behavior or imply evaluation counts',async t=>{
  const f=fixture(t),before=canonicalJson(f.graph.compositions),b=f.run();
  assert.equal(canonicalJson(f.graph.compositions),before);
  const compiled=f.graph.compositions![0]!,api=await import('data:text/javascript;base64,'+Buffer.from(compiled.artifacts['behavior.mjs']!).toString('base64'));
  let evaluations=0;
  const result=api.execute({input:{value:'7'}},{evaluateCalculation:(name:string,args:any)=>{evaluations++;assert.equal(name,'Total');return BigInt(args.amount)*2n;}});
  assert.deepEqual(result,{value:'14'});assert.equal(evaluations,1);
  assert.equal(b.composition_graphs[0]!.references.filter(r=>r.role==='calls').length,2,'two different call references are not two Calculation evaluations');
});

test('DSR-011 legacy projects have explicit empty composition planes without inventing types',()=>{
  const graph=loadCompiledProjectGraph(path.join(project,'impl/cli/fixtures/input-roots/canonical-project'));
  const b=compileCompositionBoundary(graph,{schema_version:COMPOSITION_BOUNDARY_VERSION,contract_sha256:COMPOSITION_BOUNDARY_CONTRACT_SHA256,graph_sha256:createCompiledProjectCertificate(graph).graph_sha256},descriptor);
  assert.deepEqual(b.composition_graphs,[]);assert.deepEqual(b.bridges,[]);
  assert.equal(b.coverage.domain_nodes,graph.nodes.length);
  assert.equal(b.coverage.core_typed_contracts+b.coverage.untyped_domain_nodes,graph.nodes.length);
});
