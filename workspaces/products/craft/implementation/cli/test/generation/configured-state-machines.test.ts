import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {createRequire} from 'node:module';
import {execFileSync} from 'node:child_process';
import test from 'node:test';
import {decodeBody,loadCompiledProjectGraph,selectCompiledProjectNode} from '../../src/input/project-model.ts';
import {createCompiledProjectCertificate} from '../../src/compilation/certificate.ts';
import {compileCompositionBoundary,COMPOSITION_BOUNDARY_VERSION,COMPOSITION_BOUNDARY_CONTRACT_SHA256} from '../../src/input/composition-boundary.ts';
import {compileSelectedProjectFields,EXACT_PROJECT_FIELD_SELECTION_VERSION,EXACT_FIELD_CONTRACT_SHA256} from '../../src/input/compiled-field-model.ts';
import {decodeTypedStateMachineContract,TYPED_STATE_MACHINE_VERSION} from '../../src/typed-backend/state-machine.ts';
import {migrateLegacyStateMachine} from '../../src/typed-backend/state-machine-compatibility.ts';
import {planConfiguredStateMachines,CONFIGURED_STATE_MACHINE_VERSION} from '../../src/generation/configured-state-machines.ts';
import {renderImplementation} from '../../src/generation/generators.ts';
import {FROZEN_META_TYPE_CATALOG} from '../../src/meta-types/catalog.ts';
import {createMetaTypeFormalizationProjection} from '../../src/formalization/projection.ts';
import {createCheckedInterchange} from '../../src/assurance/checked-interchange.ts';
import {runInMemoryProject} from '../../src/runtime/in-memory.ts';
import {canonicalJson,sha256} from '../../src/input/source-manifest.ts';
const project=path.resolve(import.meta.dirname,'../../../..'),base='development/reconciliation-v1/profile-compiler-reconciliation/';
const bytes=(p:string)=>fs.readFileSync(path.join(project,p),'utf8');
const sources={state_machine_contract:bytes(base+'state-machine-contract.json'),rules:{
 configuration:bytes(base+'configuration.json'),base:bytes('development/implementation-conformance/ontology-experiment/profiles/base-domain.profile.json'),typescript:bytes('development/implementation-conformance/ontology-experiment/profiles/typescript-strict.profile.json'),
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
   const selection:any={schema_version:CONFIGURED_STATE_MACHINE_VERSION,language:'typescript',module_root:'application',roots:['commerce:lifecycle'],boundary_sha256:boundary.boundary_sha256,field_compilation_sha256:fields?.compilation_sha256??null};
   return {graph,boundary,fields,selection,plan:()=>planConfiguredStateMachines(graph,boundary,fields,selection,sources)};
 };return {temp,source,c,rule,node,edge,edges,save,write,compile,...compile()};
}
const frozen=(v:any):void=>{if(v&&typeof v==='object'){assert.ok(Object.isFrozen(v));Object.values(v).forEach(frozen);}};
function native(root:string,plan:ReturnType<typeof planConfiguredStateMachines>){
 for(const a of plan.artifacts){const file=path.join(root,a.relative_path);fs.mkdirSync(path.dirname(file),{recursive:true});fs.writeFileSync(file,a.content);}
 const chain=JSON.parse(fs.readFileSync(path.resolve(project,'../../toolchains/node-typescript/toolchain.json'),'utf8')),image=nativeToolchainImage(chain.container_image);
 const docker=['run','--rm','--pull','never','--network','none','--read-only','--cap-drop','ALL','--security-opt','no-new-privileges','--user',process.getuid!()+':'+process.getgid!(),'--mount','type=bind,source='+root+',target='+root,'--workdir',root,image];
 const compile=(extra:string[]=[])=>execFileSync('docker',[...docker,'tsc','--ignoreConfig','--strict','--skipLibCheck','--declaration','--target','ES2022','--module','commonjs','--rootDir',root,'--outDir',path.join(root,'js'),...plan.artifacts.map(a=>path.join(root,a.relative_path)),...extra],{encoding:'utf8',stdio:'pipe'});compile();
 const m=plan.modules[0]!,js=path.join(root,'js',m.relative_path.replace(/\.ts$/,'.js'));
 const load=()=>{const req=createRequire(import.meta.url);for(const key of Object.keys(req.cache))if(key.startsWith(root+path.sep))delete req.cache[key];return req(js)[m.callable];};
 return {root,plan,m,js,compile,load,docker,image};
}
test('versioned reducer emits native transitions and keeps trigger, guard, output slots and state distinct',t=>{
 const f=fixture(t),p=f.plan();frozen(p);assert.deepEqual(p,f.plan());assert.equal(p.modules[0]!.descriptor.event_dependencies.length,2);
 const n=native(path.join(f.temp,'native'),p),reduce=n.load();
 const yes=reduce('draft','commerce:requested',{amount:'18446744073709551615'});frozen(yes);
 assert.deepEqual(yes,{status:'transitioned',state:'submitted',transition_id:'submit',output_intents:[{slot:'primary',event_ref:'commerce:completed'},{slot:'audit',event_ref:'commerce:completed'}]});
 assert.deepEqual(reduce('draft','commerce:requested',{amount:9}),{status:'rejected',state:'draft',reason:'guard',output_intents:[]});
 assert.deepEqual(reduce('draft','commerce:completed',{amount:10}),{status:'rejected',state:'draft',reason:'no-transition',output_intents:[]});
 assert.equal(reduce('submitted','commerce:completed',{amount:0}).state,'closed');
 assert.equal(reduce('closed','commerce:requested',{amount:0}).transition_id,'repeat');
 for(const state of f.c.states)for(const trigger of ['commerce:requested','commerce:completed'])for(const amount of [0,9,10,Number.MAX_SAFE_INTEGER,'18446744073709551615']){
   const transition=f.c.transitions.find((r:any)=>r.source_state===state&&r.trigger_event_ref===trigger),out=reduce(state,trigger,{amount});
   const accepted=transition&&(!transition.guard||BigInt(amount)>9n);
   assert.equal(out.status,accepted?'transitioned':'rejected');assert.equal(out.state,accepted?transition.target_state:state);assert.deepEqual(out.output_intents,accepted?transition.output_intents:[]);assert.deepEqual(out,reduce(state,trigger,{amount}));
 }
 assert.throws(()=>{yes.output_intents[0].slot='changed';},TypeError);assert.equal(reduce('draft','commerce:requested',{amount:10}).output_intents[0].slot,'primary');
});
test('closed versioned source rejects ambiguity, missing bindings and hostile data before execution',()=>{
 const c=contract();frozen(decodeTypedStateMachineContract(c));
 for(const mutate of [(v:any)=>v.schema_version='future',(v:any)=>v.inputs.push(v.inputs[0]),(v:any)=>v.states.push('draft'),(v:any)=>v.initial='absent',(v:any)=>v.transitions[0].source_state='absent',(v:any)=>v.transitions[0].trigger_event_ref='commerce:requested\n',(v:any)=>delete v.transitions[0].output_intents,(v:any)=>v.transitions[0].output_intents.push(v.transitions[0].output_intents[0]),(v:any)=>v.transitions.push({...v.transitions[0],transition_id:'ambiguous'}),(v:any)=>v.transitions[0].guard.arguments.push(v.transitions[0].guard.arguments[0])]){const copy=structuredClone(c);mutate(copy);assert.throws(()=>decodeTypedStateMachineContract(copy));}
 let reads=0;const outer={description:'test',get typed_contract(){reads++;return c;}};assert.throws(()=>decodeBody('State Machine',outer));assert.equal(reads,0);
 const cycle:any={};cycle.self=cycle;assert.throws(()=>decodeTypedStateMachineContract(cycle),/limits/);
 assert.throws(()=>decodeTypedStateMachineContract({...c,inputs:Array(1000000)}));
});
test('graph requires trigger edges, exact typed Rule arguments and Event output targets',t=>{
 const f=fixture(t);
 for(const mutate of [(c:any)=>c.transitions[0].guard.arguments[0].parameter='missing',(c:any)=>c.transitions[0].guard.arguments[0].value=at('missing'),(c:any)=>c.transitions[0].guard.selector='commerce:requested',(c:any)=>c.transitions[0].output_intents[0].event_ref='commerce:allowed',(c:any)=>c.transitions[0].trigger_event_ref='commerce:unrelated']){
  const c=contract();mutate(c);f.node('lifecycle','State Machine',{typed_contract:c});assert.throws(()=>f.compile());
 }
 f.node('lifecycle','State Machine',{typed_contract:contract()});f.edge('extra-output','unrelated','lifecycle');f.save();assert.throws(()=>f.compile(),{code:'MTCLI_STATE_MACHINE_TRIGGER_RELATIONSHIP'});
 f.edges.pop();f.save();assert.doesNotThrow(()=>f.compile());
});
test('migration requires explicit triggers and argument bindings and leaves legacy source and defaults unchanged',t=>{
 const f=fixture(t),legacy:any={description:'legacy',states:['draft','submitted'],initial:'draft',transitions:[{transition_id:'submit',source_state:'draft',target_state:'submitted',guard_ref:'commerce:allowed',effect_event_ref:'commerce:completed'}]};
 const b:any={ontology_state_machine:'FIXTURE-LIFECYCLE',inputs:[{name:'amount',type:scalar('UInt64')}],transitions:[{transition_id:'submit',trigger_event_ref:'commerce:requested',guard_arguments:guard().arguments,output_slot:'submitted'}]};
 const before=JSON.stringify(legacy),m=migrateLegacyStateMachine(legacy,b);frozen(m);assert.equal(JSON.stringify(legacy),before);assert.equal(m.graph_effect,'none');
 assert.deepEqual(m.relationship_review.legacy_output_events,['commerce:completed']);assert.deepEqual(m.relationship_review.required_trigger_events,['commerce:requested']);
 for(const mutate of [(v:any)=>delete v.transitions[0].trigger_event_ref,(v:any)=>v.transitions=[],(v:any)=>v.transitions[0].guard_arguments=null,(v:any)=>v.transitions[0].output_slot=null]){const v=structuredClone(b);mutate(v);assert.throws(()=>migrateLegacyStateMachine(legacy,v));}
 f.node('lifecycle','State Machine',legacy);f.edges.splice(0,1);f.save();const old=f.compile();assert.throws(()=>old.plan(),/migrate legacy/);
 const realization=FROZEN_META_TYPE_CATALOG.realization_rows.find(r=>r.meta_type_label==='State Machine'&&r.language==='typescript')!;
 const input:any={...selectCompiledProjectNode(old.graph,'commerce:lifecycle'),realization};const oldSource=renderImplementation(input).content;
 f.node('lifecycle','State Machine',m.body);assert.throws(()=>f.compile(),{code:'MTCLI_STATE_MACHINE_TRIGGER_RELATIONSHIP'});
 f.edges.splice(0);f.edge('requested-advances','requested','lifecycle');f.save();const fresh=f.compile();assert.doesNotThrow(()=>fresh.plan());
 for(const language of ['typescript','python','rust'])assert.throws(()=>renderImplementation({...input,body:m.body,realization:FROZEN_META_TYPE_CATALOG.realization_rows.find(r=>r.meta_type_label==='State Machine'&&r.language===language)!}),/STATE_MACHINE_PROFILE_REQUIRED/);
 assert.equal(renderImplementation(input).content,oldSource);
});
test('planner rejects forged snapshots, stale evidence, unsafe roots and changed selected source bytes',t=>{
 const f=fixture(t);
 assert.throws(()=>planConfiguredStateMachines(structuredClone(f.graph),f.boundary,null,f.selection,sources));
 for(const change of [{schema_version:'future'},{language:'python'},{roots:['commerce:allowed']},{roots:['commerce:lifecycle','commerce:lifecycle']},{module_root:'../escape'},{module_root:'con'},{module_root:'app\n'},{boundary_sha256:'0'.repeat(64)},{field_compilation_sha256:'0'.repeat(64)}])assert.throws(()=>planConfiguredStateMachines(f.graph,f.boundary,null,{...f.selection,...change},sources));
 for(const key of ['configuration','base','typescript','structured_contract'])assert.throws(()=>planConfiguredStateMachines(f.graph,f.boundary,null,f.selection,{...sources,rules:{...sources.rules,[key]:sources.rules[key as keyof typeof sources.rules]+' '}}));
 assert.throws(()=>planConfiguredStateMachines(f.graph,f.boundary,null,f.selection,{...sources,state_machine_contract:sources.state_machine_contract+' '}));
 let reads=0;assert.throws(()=>planConfiguredStateMachines(f.graph,f.boundary,null,{...f.selection,get roots(){reads++;return ['commerce:lifecycle'];}},sources));assert.equal(reads,0);
 const other=fixture(t);other.c.transitions[0].target_state='closed';other.node('lifecycle','State Machine',{typed_contract:other.c});const cross=other.compile();assert.throws(()=>planConfiguredStateMachines(cross.graph,f.boundary,null,f.selection,sources));
});
test('runtime rejects getters, coercion, invalid symbols, unsafe integers and extra fields with no input mutation',t=>{
 const f=fixture(t),n=native(path.join(f.temp,'hostile'),f.plan()),reduce=n.load();let reads=0;
 for(const input of [{get amount(){reads++;return 10;}},{amount:{valueOf(){reads++;return 10;}}},{amount:10,extra:1},{amount:NaN},{amount:Number.MAX_SAFE_INTEGER+1},{amount:'18446744073709551616'},{amount:-1},{amount:'10\n'},[],null])assert.throws(()=>reduce('draft','commerce:requested',input),/STATE_MACHINE_INPUT/);
 assert.equal(reads,0);assert.throws(()=>reduce({toString(){reads++;return 'draft';}},'commerce:requested',{amount:10}));assert.equal(reads,0);
 assert.throws(()=>reduce('missing','commerce:requested',{amount:10}));assert.throws(()=>reduce('draft','commerce:unrelated',{amount:10}));
 const input=Object.freeze({amount:10});reduce('draft','commerce:requested',input);assert.deepEqual(input,{amount:10});
});
test('guardless machine compiles without fabricating Rule dependencies',t=>{
 const f=fixture(t);f.c.inputs=[];for(const row of f.c.transitions)row.guard=null;f.node('lifecycle','State Machine',{typed_contract:f.c});
 const p=f.compile().plan();assert.equal(p.rule_plan,null);assert.equal(p.artifacts.length,2);const n=native(path.join(f.temp,'guardless'),p);assert.equal(n.load()('draft','commerce:requested',{}).state,'submitted');
});

function observe(n:ReturnType<typeof native>,f:ReturnType<typeof fixture>){
 const c=f.c,events=[...new Set(c.transitions.flatMap((t:any)=>[t.trigger_event_ref,...t.output_intents.map((o:any)=>o.event_ref)]))].sort().map((selector:any)=>{
   const raw=fs.readFileSync(path.join(f.source,'specs/commerce/nodes/'+selector.split(':')[1]+'.json'),'utf8');return {selector,body_sha256:sha256(canonicalJson(JSON.parse(raw).body)),source_sha256:sha256(raw)};
 });
 const expected={contract:c,provider_path:n.m.provider_path,relative_path:n.m.relative_path,callable:n.m.callable,events,rules:[{selector:'commerce:allowed',path:'../rules/allowed.js',symbol:'ruleAllowed'}]};
 fs.writeFileSync(path.join(n.root,'expected.json'),JSON.stringify(expected));fs.writeFileSync(path.join(n.root,'tsconfig.json'),JSON.stringify({compilerOptions:{target:'ES2022',module:'NodeNext',strict:true,noEmit:true},files:n.plan.artifacts.map(a=>a.relative_path)}));
 const observer=path.join(project,'impl/cli/tools/observe-configured-state-machines.mjs');
 const supportObserver=path.join(project,'impl/cli/tools/structured-rule-support-observer.mjs');
 try{return JSON.parse(execFileSync('docker',[...n.docker.slice(0,-1),'--mount','type=bind,source='+observer+',target=/observer.mjs,readonly','--mount','type=bind,source='+supportObserver+',target=/structured-rule-support-observer.mjs,readonly',n.image,'node','/observer.mjs',path.join(n.root,'tsconfig.json'),path.join(n.root,'expected.json')],{encoding:'utf8'}));}
 catch(e){const x=e as any;if(x.status===1&&x.stdout)return JSON.parse(x.stdout);throw e;}
}
const frozenLiteral=(v:any):string=>Array.isArray(v)?'Object.freeze(['+v.map(frozenLiteral).join(',')+'])':v&&typeof v==='object'?'Object.freeze({'+Object.entries(v).map(([k,x])=>'['+JSON.stringify(k)+']:'+frozenLiteral(x)).join(',')+'})':JSON.stringify(v);
test('independent native source observer rejects compiling semantic mutations with refreshed descriptor hashes',t=>{
 const f=fixture(t),p=f.plan(),n=native(path.join(f.temp,'mutations'),p),original=p.artifacts.find(a=>a.relative_path===n.m.provider_path)!.content,wrapper=p.artifacts.find(a=>a.relative_path===n.m.relative_path)!.content;
 const baseline=observe(n,f);assert.equal(baseline.result,'pass',JSON.stringify(baseline));
 const mutations=[
   original.replace('if(!condition0({["amount"]:p0}))','if(false)'),
   original.replace('if(!condition0({["amount"]:p0}))','if(condition0({["amount"]:p0}))'),
   original.replace('&&trigger==="commerce:requested"','&&trigger==="commerce:completed"'),
   original.replace('if(state==="draft"','if(state==="closed"'),
   original.replaceAll('state:"submitted"','state:"closed"'),
   original.replaceAll('event_ref:"commerce:completed"','event_ref:"commerce:requested"'),
   original.replaceAll('slot:"audit"','slot:"primary"'),
   original.replace('checkData(parameters);',''),
   original.replace('  checkData(parameters);','  (globalThis as {leak?:unknown}).leak=parameters;\n  checkData(parameters);')
 ];
 for(const [i,content]of mutations.entries()){
   assert.notEqual(content,original,'mutation applied '+i);fs.writeFileSync(path.join(n.root,n.m.provider_path),content);
   const {descriptor_sha256,...body}=n.m.descriptor,changed={...body,provider:{sha256:sha256(content)}};const descriptor={...changed,descriptor_sha256:sha256(canonicalJson(changed))};
   fs.writeFileSync(path.join(n.root,n.m.relative_path),wrapper.replace(frozenLiteral(n.m.descriptor),frozenLiteral(descriptor)));n.compile();
   const result=observe(n,f);assert.equal(result.result,'fail','observer killed compiling mutation '+i);assert.ok(result.errors.some((s:string)=>!s.includes('hash')));
   if(i===0)assert.equal(n.load()('draft','commerce:requested',{amount:0}).status,'transitioned');
   if(i===2)assert.equal(n.load()('draft','commerce:requested',{amount:10}).status,'rejected');
   if(i===5)assert.equal(n.load()('draft','commerce:requested',{amount:10}).output_intents[0].event_ref,'commerce:requested');
 }
 fs.writeFileSync(path.join(n.root,n.m.provider_path),original);fs.writeFileSync(path.join(n.root,n.m.relative_path),wrapper);n.compile();assert.equal(observe(n,f).result,'pass');
});
test('generated declarations expose readonly closed state, trigger and transition-specific output types',t=>{
 const f=fixture(t),n=native(path.join(f.temp,'consumer'),f.plan()),file=path.join(n.root,'consumer.ts');
 fs.writeFileSync(file,`import {transitionLifecycle,initialState,type State,type Outcome} from './application/features/commerce/src/domain/state-machines/lifecycle.js';
const state:State=initialState;
const result:Outcome=transitionLifecycle(state,'commerce:requested',{amount:18446744073709551615n});
// @ts-expect-error Unknown state is outside the closed union.
transitionLifecycle('missing','commerce:requested',{amount:10});
// @ts-expect-error Event not declared as a trigger is not a trigger symbol.
transitionLifecycle(state,'commerce:unrelated',{amount:10});
// @ts-expect-error Boolean is not UInt64.
transitionLifecycle(state,'commerce:requested',{amount:true});
// @ts-expect-error Result cannot be mutated in place.
result.state='draft';
if(result.status==='rejected'){
 // @ts-expect-error Rejected results have no transition identity.
 result.transition_id;
 // @ts-expect-error Rejected results carry no output slots.
 result.output_intents[0];
}else if(result.transition_id==='submit'){
 const emitted:'commerce:completed'=result.output_intents[0].event_ref;
 // @ts-expect-error Output slots are readonly.
 result.output_intents[0].slot='other';
}
`);assert.doesNotThrow(()=>n.compile([file]));
});
test('explicit structured facts retain optional, list, set, sum, Enum and Entity distinctions',t=>{
 const f=fixture(t),named=(id:string)=>({kind:'named',selector:'commerce:'+id}),wrap=(kind:string,element:any)=>({kind,element});
 const prop=(name:string,type:any,identity=false)=>({name,type,identity,cardinality:type.kind==='optional'?'optional':type.kind==='list'?'many':type.kind==='set'?'many-unique':'one',meaning:name,ontology_property:'FIXTURE-ORDER#'+name});
 f.node('order','Entity',{fields:['id','active'],typed_contract:{schema_version:'domainspec.typed-record/v1',ontology_node:'FIXTURE-ORDER',properties:[prop('id',scalar(),true),prop('active',scalar('Bool'))]}});
 f.node('status','Enum',{values:['Ready','Draft'],typed_contract:{schema_version:'domainspec.typed-sum/v1',ontology_node:'FIXTURE-STATUS',variants:['Ready','Draft'].map(name=>({name,ontology_variant:'FIXTURE-STATUS#'+name,payload:null}))}});
 const sum={kind:'sum',variants:[{name:'None',ontology_variant:'FIXTURE-CHOICE#None',payload:null},{name:'Amount',ontology_variant:'FIXTURE-CHOICE#Amount',payload:scalar('UInt64')}]};
 const inputs=[{name:'order',type:named('order')},{name:'status',type:named('status')},{name:'amounts',type:wrap('list',scalar('UInt64'))},{name:'tags',type:wrap('set',scalar())},{name:'note',type:wrap('optional',scalar())},{name:'choice',type:sum}];
 const rule:any={schema_version:'domainspec.typed-rule/v2',ontology_rule:'FIXTURE-ALLOWED',parameters:inputs,expression:{op:'all',terms:[{op:'eq',left:at('order','FIXTURE-ORDER#active'),right:{op:'literal',type:'Bool',value:true}},{op:'eq',left:at('status'),right:{op:'variant',selector:'FIXTURE-STATUS#Ready'}},...inputs.slice(2).map(p=>({op:'eq',left:at(p.name),right:at(p.name)}))]}};
 f.node('allowed','Rule',{predicate:'structured:domainspec.typed-rule/v2',typed_contract:rule});f.c.inputs=inputs;f.c.transitions[0].guard={selector:'commerce:allowed',arguments:inputs.map(p=>({parameter:p.name,value:at(p.name)}))};f.node('lifecycle','State Machine',{typed_contract:f.c});f.save();
 const plan=f.compile(['commerce:order','commerce:status']).plan(),n=native(path.join(f.temp,'structured'),plan),reduce=n.load();
 const input:any={order:{id:'id',active:true},status:{variant:'Ready'},amounts:['18446744073709551615','18446744073709551615'],tags:['b','a'],note:null,choice:{variant:'Amount',payload:'18446744073709551615'}};
 assert.equal(reduce('draft','commerce:requested',input).status,'transitioned');assert.equal(reduce('draft','commerce:requested',{...input,order:{...input.order,active:false}}).status,'rejected');
 for(const change of [{tags:['a','a']},{choice:{variant:'None',payload:1}},{note:undefined},{amounts:['18446744073709551616']}])assert.throws(()=>reduce('draft','commerce:requested',{...input,...change}),/STATE_MACHINE_INPUT/);
 const sparse=Array(2);sparse[1]=1;assert.throws(()=>reduce('draft','commerce:requested',{...input,amounts:sparse}));assert.throws(()=>reduce('draft','commerce:requested',{...input,amounts:Array(1025).fill(0)}));
});
test('legacy runtime and proof projection reject the successor explicitly before claiming conformance',t=>{
 const f=fixture(t);
 assert.throws(()=>createMetaTypeFormalizationProjection(f.graph),{code:'MTCLI_STATE_MACHINE_FORMALIZATION_UNSUPPORTED'});
 assert.throws(()=>createCheckedInterchange(f.graph),{code:'MTCLI_STATE_MACHINE_FORMALIZATION_UNSUPPORTED'});
 assert.throws(()=>runInMemoryProject(f.source,{schema_version:'domainspec.runtime-invocation/v1',invocation_id:'state-machine-check',provider:'in-memory-v1',steps:[{step_id:'transition',selector:'commerce:lifecycle',input:{current_state:'draft',transition_id:'submit',guards:{'commerce:allowed':true}}}]}),{code:'MTCLI_STATE_MACHINE_PROFILE_REQUIRED'});
 assert.throws(()=>runInMemoryProject(f.source,{schema_version:'domainspec.runtime-invocation/v1',invocation_id:'mixed-graph-check',provider:'in-memory-v1',steps:[{step_id:'event',selector:'commerce:requested',input:{}}]}),{code:'MTCLI_STATE_MACHINE_FORMALIZATION_UNSUPPORTED'});
});

import {nativeToolchainImage} from '../helpers/native-toolchain-image.ts';
