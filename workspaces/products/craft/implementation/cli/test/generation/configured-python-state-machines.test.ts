import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {execFileSync} from 'node:child_process';
import test from 'node:test';
import {loadCompiledProjectGraph,selectCompiledProjectNode} from '../../src/input/project-model.ts';
import {createCompiledProjectCertificate} from '../../src/compilation/certificate.ts';
import {compileCompositionBoundary,COMPOSITION_BOUNDARY_VERSION,COMPOSITION_BOUNDARY_CONTRACT_SHA256} from '../../src/input/composition-boundary.ts';
import {compileSelectedProjectFields,EXACT_PROJECT_FIELD_SELECTION_VERSION,EXACT_FIELD_CONTRACT_SHA256} from '../../src/input/compiled-field-model.ts';
import {decodeTypedStateMachineContract,TYPED_STATE_MACHINE_VERSION} from '../../src/typed-backend/state-machine.ts';
import {planConfiguredPythonStateMachines,PYTHON_STATE_MACHINE_VERSION} from '../../src/generation/configured-python-state-machines.ts';
import * as legacy from '../../src/generation/configured-state-machines.ts';
import {canonicalJson,sha256} from '../../src/input/source-manifest.ts';
const project=path.resolve(import.meta.dirname,'../../../..'),base='development/reconciliation-v1/profile-compiler-reconciliation/';
const bytes=(p:string)=>fs.readFileSync(path.join(project,p),'utf8');
const sources={state_machine_contract:bytes(base+'state-machine-contract.json'),rules:{
 configuration:bytes(base+'configuration.json'),base:bytes('development/implementation-conformance/ontology-experiment/profiles/base-domain.profile.json'),python:bytes('development/implementation-conformance/ontology-experiment/profiles/python-strict.profile.json'),
 rule_contract:bytes(base+'string-order-rule-contract.json'),collection_contract:bytes(base+'rule-collection-value-contract.json'),predicate_contract:bytes(base+'rule-collection-predicate-contract.json'),numeric_contract:bytes(base+'rule-numeric-contract.json'),
 exact_contract:bytes(base+'rule-exact-contract.json'),literal_contract:bytes(base+'rule-exact-literal-contract.json'),structured_contract:bytes(base+'rule-structured-value-contract.json'),field_contract:bytes('development/reconciliation-v1/contracts/exact-field-and-reference-model.json')
}};
const scalar=(name='String'):any=>({kind:'scalar',name}),at=(root:string,...properties:string[]):any=>({op:'path',root,properties});
const guard=(root='amount')=>({selector:'commerce:allowed',arguments:[{parameter:'amount',value:at(root)}]});
const contract=():any=>({schema_version:TYPED_STATE_MACHINE_VERSION,ontology_state_machine:'FIXTURE-LIFECYCLE',inputs:[{name:'amount',type:scalar('UInt64')}],states:['draft','submitted','closed'],initial:'draft',transitions:[
 {transition_id:'submit',source_state:'draft',target_state:'submitted',trigger_event_ref:'commerce:requested',guard:guard(),output_intents:[{slot:'primary',event_ref:'commerce:completed'},{slot:'audit',event_ref:'commerce:completed'}]},
 {transition_id:'close',source_state:'submitted',target_state:'closed',trigger_event_ref:'commerce:completed',guard:null,output_intents:[]},
 {transition_id:'repeat',source_state:'closed',target_state:'closed',trigger_event_ref:'commerce:requested',guard:null,output_intents:[]}
]});
function fixture(t:any){
 const temp=fs.mkdtempSync(path.join(os.tmpdir(),'ds-state-machine-'));t.after(()=>fs.rmSync(temp,{recursive:true,force:true}));
 const source=path.join(temp,'source'),nodes:string[]=[],edges:string[]=[];
 const write=(p:string,v:any)=>{const file=path.join(source,p);fs.mkdirSync(path.dirname(file),{recursive:true});fs.writeFileSync(file,JSON.stringify(v));};
 const node=(id:string,kind:string,body:any)=>{if(!nodes.includes(id))nodes.push(id);write('specs/commerce/nodes/'+id+'.json',{schema_version:'domainspec.node/v1',feature_id:'commerce',node_id:id,kind,body:{description:id,...body}});};
 const edge=(id:string,from:string,to:string)=>{if(!edges.includes(id))edges.push(id);write('specs/commerce/edges/'+id+'.json',{schema_version:'domainspec.edge/v1',feature_id:'commerce',edge_id:id,relationship:'transitions',source_node_id:from,target_node_id:to,scope:'feature'});};
 const c=contract();node('lifecycle','State Machine',{typed_contract:c});
 const rule:any={schema_version:'domainspec.typed-rule/v2',ontology_rule:'FIXTURE-ALLOWED',parameters:[{name:'amount',type:scalar('UInt64')}],expression:{op:'lt',left:{op:'literal',type:'UInt64',value:'9'},right:at('amount')}};
 node('allowed','Rule',{predicate:'structured:domainspec.typed-rule/v2',typed_contract:rule});
 for(const id of ['requested','completed','unrelated'])node(id,'Event',{event_type:id,version:'1',occurrence_id:{field_id:'id',type_ref:{kind:'primitive',name:'uuid'},required:true},occurred_at_policy:'required',payload:[]});
 for(const id of ['requested','completed'])edge(id+'-advances',id,'lifecycle');
 const save=()=>{write('project.json',{schema_version:'domainspec.project/v1',project_id:'state-machines',features:['commerce'],cross_feature_edges:[]});write('specs/commerce/feature.json',{schema_version:'domainspec.feature/v1',feature_id:'commerce',nodes,edges});};save();
 const compile=(dataRoots:string[]=[])=>{
   const graph=loadCompiledProjectGraph(source),cert=createCompiledProjectCertificate(graph),boundary=compileCompositionBoundary(graph,{schema_version:COMPOSITION_BOUNDARY_VERSION,contract_sha256:COMPOSITION_BOUNDARY_CONTRACT_SHA256,graph_sha256:cert.graph_sha256},bytes('development/reconciliation-v1/contracts/composition-boundary.json'));
   const fields=dataRoots.length?compileSelectedProjectFields(graph,{schema_version:EXACT_PROJECT_FIELD_SELECTION_VERSION,contract_sha256:EXACT_FIELD_CONTRACT_SHA256,graph_sha256:cert.graph_sha256,roots:dataRoots,bindings:[]},sources.rules.field_contract):null;
   const selection:any={schema_version:PYTHON_STATE_MACHINE_VERSION,language:'python',module_root:'application',roots:['commerce:lifecycle'],boundary_sha256:boundary.boundary_sha256,field_compilation_sha256:fields?.compilation_sha256??null};
   return {graph,boundary,fields,selection,plan:()=>planConfiguredPythonStateMachines(graph,boundary,fields,selection,sources)};
 };return {temp,source,c,rule,node,edge,edges,save,write,compile,...compile()};
}

type Plan=ReturnType<typeof planConfiguredPythonStateMachines>;
function payload(root:string,p:Plan,f:ReturnType<typeof fixture>,model:any=null){
 for(const a of p.artifacts){const file=path.join(root,a.relative_path);fs.mkdirSync(path.dirname(file),{recursive:true});fs.writeFileSync(file,a.content);}
 const graph=loadCompiledProjectGraph(f.source);
 const ruleRoots=[...new Set(p.rule_plan?.modules.flatMap(m=>selectCompiledProjectNode(graph,m.selector).typed_closure!.nodes.filter(n=>['Entity','Value Object','Enum'].includes(n.kind)).map(n=>n.selector))??[])].sort();
 const ruleFields=ruleRoots.length?compileSelectedProjectFields(graph,{schema_version:EXACT_PROJECT_FIELD_SELECTION_VERSION,contract_sha256:EXACT_FIELD_CONTRACT_SHA256,graph_sha256:p.certificate.graph_sha256,roots:ruleRoots,bindings:[]},sources.rules.field_contract):null;
 return {root,module_root:p.selection.module_root.replaceAll('-','_'),model,modules:p.modules,contracts:Object.fromEntries(graph.nodes.filter(n=>n.kind==='State Machine').map(n=>[n.selector,n.body.typed_contract])),nodes:Object.fromEntries(graph.nodes.map(n=>[n.selector,{kind:n.kind,body:n.body}])),rule_model:ruleFields?.model??null,rule_model_sha256:p.rule_plan?.field_model_sha256??null,rule_modules:p.rule_plan?.modules??[],rule_artifacts:p.rule_plan?.artifacts.map(({relative_path,sha256})=>({relative_path,sha256}))??[]};
}
function run(script:string,data:unknown){return JSON.parse(execFileSync('/usr/bin/python3',['-B',path.join(import.meta.dirname,script)],{input:JSON.stringify(data),encoding:'utf8',stdio:['pipe','pipe','pipe']}));}

test('Python State Machine preserves complete state/trigger matrices, nominal enums, intent order and immutable replay',t=>{
 const f=fixture(t);
 for(const module_root of ['application','relocated/kernel']){
  const p=planConfiguredPythonStateMachines(f.graph,f.boundary,null,{...f.selection,module_root},sources),data=payload(path.join(f.temp,module_root.replaceAll('/','-')),p,f);
  assert.deepEqual(p,planConfiguredPythonStateMachines(f.graph,f.boundary,null,{...f.selection,module_root},sources));
  assert.ok(Object.isFrozen(p));assert.equal(p.modules[0].descriptor.effect_contract,'none');
  assert.equal(run('python-state-machine-runtime.py',data).cases,30);
  assert.equal(run('python-state-machine-observer.py',data).observed,1);
  assert.equal(p.artifacts.some(a=>a.relative_path.includes('/events/')),false);
 }
});

test('Python State Machine supports guardless and structured facts without inventing effects or factory validation',t=>{
 const f=fixture(t);
 f.c.inputs=[];for(const transition of f.c.transitions)transition.guard=null;
 f.node('lifecycle','State Machine',{typed_contract:f.c});
 const guardless=f.compile(),p=guardless.plan(),data=payload(path.join(f.temp,'guardless'),p,f);
 assert.equal(p.rule_plan,null);assert.equal(p.artifacts.some(a=>a.relative_path.includes('/rules/')),false);
 assert.equal(run('python-state-machine-runtime.py',data).cases,30);
 assert.equal(run('python-state-machine-observer.py',data).observed,1);
 assert.throws(()=>planConfiguredPythonStateMachines(guardless.graph,guardless.boundary,null,guardless.selection,{...sources,rules:{...sources.rules,structured_contract:sources.rules.structured_contract+' '}}),/source drift/);
 const properties=[
  {name:'id',type:scalar(),identity:true},
  {name:'balance',type:scalar('UInt64'),identity:false},
  {name:'note',type:{kind:'optional',element:scalar()},identity:false},
  {name:'history',type:{kind:'list',element:scalar('UInt64')},identity:false},
  {name:'tags',type:{kind:'set',element:scalar()},identity:false},
  {name:'choice',type:{kind:'sum',variants:[{name:'Use',ontology_variant:'FIXTURE-CHOICE#Use',payload:scalar('UInt64')},{name:'Skip',ontology_variant:'FIXTURE-CHOICE#Skip',payload:null}]},identity:false},
 ].map(p=>({...p,ontology_property:'FIXTURE-ACCOUNT#'+p.name,meaning:p.name,cardinality:p.type.kind==='optional'?'optional':p.type.kind==='list'?'many':p.type.kind==='set'?'many-unique':'one'}));
 f.node('account','Entity',{fields:properties.map(p=>p.name),typed_contract:{schema_version:'domainspec.typed-record/v1',ontology_node:'FIXTURE-ACCOUNT',properties}});
 const c=contract(),named={kind:'named',selector:'commerce:account'};
 c.inputs=[{name:'account',type:named},{name:'unused',type:scalar('Bool')}];c.transitions[0].guard={selector:'commerce:forward',arguments:[{parameter:'current',value:at('account')}]};
 f.node('allowed','Rule',{predicate:'structured:domainspec.typed-rule/v2',typed_contract:{...f.rule,parameters:[{name:'current',type:named}],expression:{op:'lt',left:{op:'literal',type:'UInt64',value:'9'},right:at('current','FIXTURE-ACCOUNT#balance')}}});
 f.node('forward','Rule',{predicate:'structured:domainspec.typed-rule/v2',typed_contract:{schema_version:'domainspec.typed-rule/v2',ontology_rule:'FIXTURE-FORWARD',parameters:[{name:'current',type:named}],expression:{op:'rule_ref',selector:'commerce:allowed',arguments:[{parameter:'current',value:at('current')}]}}});
 f.node('lifecycle','State Machine',{typed_contract:c});f.save();
 const structured=f.compile(['commerce:account']),plan=structured.plan(),structuredData=payload(path.join(f.temp,'structured'),plan,f,structured.fields!.model);
 assert.equal(plan.rule_plan!.modules.length,2);
 assert.equal(plan.artifacts.some(a=>a.relative_path.includes('/entities/')),false);
 assert.equal(run('python-state-machine-runtime.py',structuredData).cases,30);
 assert.equal(run('python-state-machine-observer.py',structuredData).observed,1);
 // Rehash the transitive dependency, so rejection must come from its semantics,
 // not from the already-covered dependency byte-integrity check.
 for(const [name,change,invisible] of [
  ['comparison',(s:string)=>s.replace('return (9 < ', 'return (9 > '),false],
  ['hidden-write',(s:string)=>s.replace('def rule_allowed(', '_counter = 0\ndef rule_allowed(').replace('    return (9 < ', '    global _counter\n    _counter += 1\n    return (9 < '),true],
 ] as const){
  const copy=structuredClone(plan),rule=copy.artifacts.find(a=>a.relative_path.endsWith('/rules/allowed.py'))!,changed=change(rule.content);
  assert.notEqual(changed,rule.content,name);rule.content=changed;rule.sha256=sha256(changed);rule.size_bytes=Buffer.byteLength(changed);
  Object.assign(copy.rule_plan!.artifacts.find(a=>a.relative_path===rule.relative_path)!,rule);
  execFileSync('/usr/bin/python3',['-c','import ast,sys; compile(ast.parse(sys.stdin.read()), "<guard-mutant>", "exec")'],{input:changed});
  const mutated=payload(path.join(f.temp,'transitive-'+name),copy,f,structured.fields!.model);
  if(invisible)assert.equal(run('python-state-machine-runtime.py',mutated).cases,30);else assert.throws(()=>run('python-state-machine-runtime.py',mutated));
  assert.throws(()=>run('python-state-machine-observer.py',mutated),(e:any)=>/Rule semantics\/effects/.test(e.stderr),name);
 }
 const extraInit=payload(path.join(f.temp,'initializer'),plan,f,structured.fields!.model);
 fs.appendFileSync(path.join(extraInit.root,'application/__init__.py'),'def unused_effect():\n    print("undeclared")\n');
 assert.throws(()=>run('python-state-machine-observer.py',extraInit),(e:any)=>/empty package initialization/.test(e.stderr));
});

test('Python State Machine rejects stale/hostile selection and keeps legacy TypeScript output unchanged',t=>{
 const f=fixture(t),build=(selection:any=f.selection,s:any=sources)=>planConfiguredPythonStateMachines(f.graph,f.boundary,null,selection,s);
 for(const delta of [{language:'typescript'},{roots:[]},{roots:['commerce:lifecycle','commerce:lifecycle']},{boundary_sha256:'0'.repeat(64)},{field_compilation_sha256:'0'.repeat(64)},{module_root:'../escape'},{module_root:'enum'},{module_root:'class'}])assert.throws(()=>build({...f.selection,...delta}));
 assert.throws(()=>build(f.selection,{...sources,state_machine_contract:sources.state_machine_contract+' '}),/source drift/);
 let reads=0;const hostile={...f.selection,get roots(){reads++;return ['commerce:lifecycle'];}};assert.throws(()=>build(hostile),/data properties/);assert.equal(reads,0);
 const tsRules:any={...sources.rules,typescript:bytes('development/implementation-conformance/ontology-experiment/profiles/typescript-strict.profile.json')};delete tsRules.python;
 const selection:any={...f.selection,language:'typescript',schema_version:legacy.CONFIGURED_STATE_MACHINE_VERSION},tsSources={state_machine_contract:sources.state_machine_contract,rules:tsRules};
 const before=legacy.planConfiguredStateMachines(f.graph,f.boundary,null,selection,tsSources);build();
 assert.deepEqual(legacy.planConfiguredStateMachines(f.graph,f.boundary,null,selection,tsSources),before);
});

test('Native and whole-source State Machine controls kill compiling transition, intent, guard and hidden-effect mutations',t=>{
 const f=fixture(t),p=f.plan(),m=p.modules[0];
 const mutations=[
  ['wrong-target',(s:string)=>s.replace('_Transition0("transitioned", State.SUBMITTED','_Transition0("transitioned", State.CLOSED'),false],
  ['skip-guard',(s:string)=>s.replace('if not _condition0(', 'if False and not _condition0('),false],
  ['wrong-trigger',(s:string)=>s.replace('if state is State.DRAFT and trigger is Trigger.COMMERCE__REQUESTED','if state is State.DRAFT and trigger is Trigger.COMMERCE__COMPLETED'),false],
  ['collapsed-intents',(s:string)=>s.replace(/, _MappingProxyType\(\{"slot": "audit", "event_ref": "commerce:completed"\}\)/,''),false],
  ['mutable-result',(s:string)=>s.replace('@_dataclass(frozen=True, slots=True)\nclass _Transition0','@_dataclass(slots=True)\nclass _Transition0'),false],
  ['wrong-type',(s:string)=>s.replace('state: _Literal[State.SUBMITTED]','state: _Literal[State.CLOSED]'),false],
  ['global-write',(s:string)=>s.replace('def reduce(', '_counter = 0\ndef reduce(').replace('    try:\n        _check_data(parameters)','    global _counter\n    _counter += 1\n    try:\n        _check_data(parameters)'),true],
  ['write-restore',(s:string)=>s.replace('def reduce(', '_counter = 0\ndef reduce(').replace('    try:\n        _check_data(parameters)','    global _counter\n    prior = _counter\n    _counter += 1\n    _counter = prior\n    try:\n        _check_data(parameters)'),true],
 ] as const;
 for(const [name,change,invisible]of mutations){
  const copy=structuredClone(p),provider=copy.artifacts.find(a=>a.relative_path===m.provider_path)!,changed=change(provider.content);assert.notEqual(changed,provider.content,name);provider.content=changed;provider.sha256=sha256(changed);provider.size_bytes=Buffer.byteLength(changed);copy.modules[0].descriptor.provider.sha256=provider.sha256;
  const descriptor=copy.modules[0].descriptor,{descriptor_sha256,...body}=descriptor;descriptor.descriptor_sha256=sha256(canonicalJson(body));
  const wrapper=copy.artifacts.find(a=>a.relative_path===m.relative_path)!;wrapper.content=wrapper.content.replaceAll(m.descriptor.provider.sha256,provider.sha256).replaceAll(descriptor_sha256,descriptor.descriptor_sha256);wrapper.sha256=sha256(wrapper.content);wrapper.size_bytes=Buffer.byteLength(wrapper.content);
  execFileSync('/usr/bin/python3',['-c','import ast,sys; compile(ast.parse(sys.stdin.read()), "<mutant>", "exec")'],{input:changed});
  const data=payload(path.join(f.temp,'mutant-'+name),copy,f);
  if(invisible)assert.equal(run('python-state-machine-runtime.py',data).cases,30);else assert.throws(()=>run('python-state-machine-runtime.py',data),undefined,name);
  assert.throws(()=>run('python-state-machine-observer.py',data),(e:any)=>/State Machine semantics\/types\/effects/.test(e.stderr),name);
 }
});
