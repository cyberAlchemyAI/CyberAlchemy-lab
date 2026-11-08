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
import {planConfiguredPolicies,CONFIGURED_POLICY_VERSION} from '../../src/generation/configured-policies.ts';
import {STRUCTURED_RULE_VERSION} from '../../src/generation/configured-rules.ts';
import {decodeTypedRulePolicyContract} from '../../src/typed-backend/policy-rules.ts';
import {migrateTypedPolicyV1} from '../../src/typed-backend/policy-compatibility.ts';
import {planCompiledProjectBuild} from '../../src/generation/project-build.ts';
import {renderImplementation} from '../../src/generation/generators.ts';
import {FROZEN_META_TYPE_CATALOG} from '../../src/meta-types/catalog.ts';
import {EXACT_UINT64_PROFILE} from '../../src/generation/exact-uint64.ts';
import {canonicalJson,sha256} from '../../src/input/source-manifest.ts';
const project=path.resolve(import.meta.dirname,'../../../..'),base='development/reconciliation-v1/profile-compiler-reconciliation/';
const bytes=(p:string)=>fs.readFileSync(path.join(project,p),'utf8'),read=(p:string)=>JSON.parse(fs.readFileSync(p,'utf8'));
const sources={policy_contract:bytes(base+'policy-generation-contract.json'),rules:{
 configuration:bytes(base+'configuration.json'),base:bytes('development/implementation-conformance/ontology-experiment/profiles/base-domain.profile.json'),typescript:bytes('development/implementation-conformance/ontology-experiment/profiles/typescript-strict.profile.json'),
 rule_contract:bytes(base+'string-order-rule-contract.json'),collection_contract:bytes(base+'rule-collection-value-contract.json'),predicate_contract:bytes(base+'rule-collection-predicate-contract.json'),numeric_contract:bytes(base+'rule-numeric-contract.json'),
 exact_contract:bytes(base+'rule-exact-contract.json'),literal_contract:bytes(base+'rule-exact-literal-contract.json'),structured_contract:bytes(base+'rule-structured-value-contract.json'),field_contract:bytes('development/reconciliation-v1/contracts/exact-field-and-reference-model.json')
}};
const boundarySource=bytes('development/reconciliation-v1/contracts/composition-boundary.json');
const scalar=(name='String'):any=>({kind:'scalar',name}),named=(id:string):any=>({kind:'named',selector:'commerce:'+id}),wrap=(kind:string,element:any):any=>({kind,element});
const at=(root:string,...properties:string[]):any=>({op:'path',root,properties}),lit=(type:string,value:any):any=>({op:'literal',type,value}),eq=(left:any,right:any):any=>({op:'eq',left,right});
const property=(name:string,type:any,identity=false):any=>({name,type,identity,cardinality:type.kind==='optional'?'optional':type.kind==='list'?'many':type.kind==='set'?'many-unique':'one',meaning:name,ontology_property:'FIXTURE-ORDER#'+name});
const choice={kind:'sum',variants:[{name:'None',ontology_variant:'FIXTURE-CHOICE#None',payload:null},{name:'Amount',ontology_variant:'FIXTURE-CHOICE#Amount',payload:scalar('UInt64')}]};
const arg=(parameter:string,value:any)=>({parameter,value}),ref=(selector:string,args:any[])=>({selector:'commerce:'+selector,arguments:args});
const policyInputs=[{name:'order',type:named('order')},{name:'total',type:scalar('UInt64')},{name:'active',type:scalar('Bool')},{name:'note',type:wrap('optional',scalar())},{name:'amounts',type:wrap('list',scalar('UInt64'))},{name:'tags',type:wrap('set',scalar())},{name:'choice',type:choice},{name:'status',type:named('status')}];
function fixture(t:any){
 const temp=fs.mkdtempSync(path.join(os.tmpdir(),'ds-policies-'));t.after(()=>fs.rmSync(temp,{recursive:true,force:true}));
 const source=path.join(temp,'source'),nodes:string[]=[],edges:string[]=[];
 const write=(p:string,v:any)=>{const f=path.join(source,p);fs.mkdirSync(path.dirname(f),{recursive:true});fs.writeFileSync(f,JSON.stringify(v));};
 const node=(id:string,kind:string,body:any)=>{nodes.push(id);write('specs/commerce/nodes/'+id+'.json',{schema_version:'domainspec.node/v1',feature_id:'commerce',node_id:id,kind,body:{description:id,...body}});};
 const edge=(id:string,relationship:string,from:string,to:string)=>{edges.push(id);write('specs/commerce/edges/'+id+'.json',{schema_version:'domainspec.edge/v1',feature_id:'commerce',edge_id:id,relationship,source_node_id:from,target_node_id:to,scope:'feature'});};
 node('order','Entity',{fields:['id','enabled'],typed_contract:{schema_version:'domainspec.typed-record/v1',ontology_node:'FIXTURE-ORDER',properties:[property('id',scalar(),true),property('enabled',scalar('Bool'))]}});
 node('status','Enum',{values:['Ready','Draft'],typed_contract:{schema_version:'domainspec.typed-sum/v1',ontology_node:'FIXTURE-STATUS',variants:['Ready','Draft'].map(name=>({name,ontology_variant:'FIXTURE-STATUS#'+name,payload:null}))}});
 for(const id of ['accept','reject'])node(id,'Operation',{reads:[],writes:[],effects:[],guard:'external',failure_continuation:'fail'});
 node('review','Calculation',{inputs:['total'],typed_contract:{schema_version:'domainspec.typed-calculation/v1',ontology_calculation:'FIXTURE-REVIEW',inputs:[{name:'total',type:scalar('UInt64')}],result:scalar('UInt64'),division_rounding:'reject',expression:{op:'input',name:'total'}}});
 edge('review-calculates-accept','calculates','review','accept');
 const rule=(id:string,parameters:any[],expression:any)=>node(id,'Rule',{predicate:'structured:domainspec.typed-rule/v2',typed_contract:{schema_version:'domainspec.typed-rule/v2',ontology_rule:'FIXTURE-'+id.toUpperCase(),parameters,expression}});
 rule('high',[{name:'amount',type:scalar('UInt64')}],{op:'lt',left:lit('UInt64','100'),right:at('amount')});
 rule('forward',[{name:'amount',type:scalar('UInt64')}],{op:'rule_ref',...ref('high',[arg('amount',at('amount'))])});
 const eligibleParams=[policyInputs[0],policyInputs[2],policyInputs[3],{name:'numbers',type:wrap('set',scalar('UInt64'))},policyInputs[5],policyInputs[6],policyInputs[7]];
 rule('eligible',eligibleParams,{op:'all',terms:[eq(at('active'),lit('Bool',true)),eq(at('order','FIXTURE-ORDER#enabled'),lit('Bool',true)),eq(at('status'),{op:'variant',selector:'FIXTURE-STATUS#Ready'}),{op:'contains',left:at('numbers'),right:lit('UInt64','2')},eq(at('note'),at('note')),eq(at('tags'),at('tags')),eq(at('choice'),at('choice'))]});
 const full:any={schema_version:'domainspec.typed-policy/v2',ontology_policy:'FIXTURE-CHOOSE',inputs:policyInputs,cases:[{target:'commerce:review',rule:ref('forward',[arg('amount',at('total'))])},{target:'commerce:accept',rule:ref('eligible',eligibleParams.map((p:any)=>arg(p.name,p.name==='numbers'?{op:'to_set',value:at('amounts')}:at(p.name))))}],default_target:'commerce:reject'};
 const scalarPolicy:any={...full,ontology_policy:'FIXTURE-SCALAR',inputs:[{name:'total',type:scalar('UInt64')}],cases:[{target:'commerce:accept',rule:ref('high',[arg('amount',at('total'))])}]};
 const repeated:any={...full,ontology_policy:'FIXTURE-REPEATED',cases:[full.cases[0],{...full.cases[1],target:'commerce:review'}]};
 const policies:any={choose:full,scalar:scalarPolicy,repeated};
 for(const [id,c]of Object.entries(policies) as [string,any][]){
  node(id,'Policy',{typed_contract:c});
  for(const target of new Set([...c.cases.map((x:any)=>x.target),c.default_target]) as Set<string>)edge(id+'-applies-'+target.split(':')[1],'applies',id,target.split(':')[1]!);
 }
 const saveIndex=()=>{write('project.json',{schema_version:'domainspec.project/v1',project_id:'policy-rules',features:['commerce'],cross_feature_edges:[]});write('specs/commerce/feature.json',{schema_version:'domainspec.feature/v1',feature_id:'commerce',nodes,edges});};saveIndex();
 const compile=()=>{
  const graph=loadCompiledProjectGraph(source),certificate=createCompiledProjectCertificate(graph),boundary=compileCompositionBoundary(graph,{schema_version:COMPOSITION_BOUNDARY_VERSION,contract_sha256:COMPOSITION_BOUNDARY_CONTRACT_SHA256,graph_sha256:certificate.graph_sha256},boundarySource);
  const fields=compileSelectedProjectFields(graph,{schema_version:EXACT_PROJECT_FIELD_SELECTION_VERSION,contract_sha256:EXACT_FIELD_CONTRACT_SHA256,graph_sha256:certificate.graph_sha256,roots:['commerce:order','commerce:status'],bindings:[]},sources.rules.field_contract);
  const selection:any={schema_version:CONFIGURED_POLICY_VERSION,language:'typescript',value_profile:EXACT_UINT64_PROFILE,rule_selection:STRUCTURED_RULE_VERSION,boundary_sha256:boundary.boundary_sha256,field_compilation_sha256:fields.compilation_sha256,module_root:'application',roots:['commerce:choose','commerce:scalar','commerce:repeated']};
  return {graph,boundary,fields,selection,plan:()=>planConfiguredPolicies(graph,boundary,fields,selection,sources)};
 };
 return {temp,source,write,node,edge,saveIndex,policies,compile,...compile()};
}
const args=(total:any=2):any=>({order:{id:'order',enabled:true},total,active:true,note:null,amounts:[2,2,1],tags:['b','a'],choice:{variant:'Amount',payload:'18446744073709551615'},status:{variant:'Ready'}});
const frozen=(v:any):void=>{if(v&&typeof v==='object'){assert.ok(Object.isFrozen(v));Object.values(v).forEach(frozen);}};
function native(root:string,plan:ReturnType<typeof planConfiguredPolicies>){
 for(const a of plan.artifacts){const f=path.join(root,a.relative_path);fs.mkdirSync(path.dirname(f),{recursive:true});fs.writeFileSync(f,a.content);}
 const chain=read(path.resolve(project,'../../toolchains/node-typescript/toolchain.json')),image=nativeToolchainImage(chain.container_image);
 const docker=['run','--rm','--pull','never','--network','none','--read-only','--cap-drop','ALL','--security-opt','no-new-privileges','--user',process.getuid!()+':'+process.getgid!(),'--mount','type=bind,source='+root+',target='+root,'--workdir',root,image];
 const compile=()=>execFileSync('docker',[...docker,'tsc','--ignoreConfig','--strict','--skipLibCheck','--declaration','--target','ES2022','--module','commonjs','--rootDir',root,'--outDir',path.join(root,'js'),...plan.artifacts.map(a=>path.join(root,a.relative_path))],{encoding:'utf8'});compile();
 const module=(id:string)=>plan.modules.find(m=>m.selector==='commerce:'+id)!,js=(id:string)=>path.join(root,'js',module(id).relative_path.replace(/\.ts$/,'.js')),load=(id:string)=>createRequire(import.meta.url)(js(id))[module(id).callable];
 const fresh=(id:string,input:any)=>execFileSync(process.execPath,['-e','process.stdout.write(require('+JSON.stringify(js(id))+')['+JSON.stringify(module(id).callable)+']('+JSON.stringify(input)+'));'],{encoding:'utf8'});
 return {root,plan,compile,module,js,load,fresh,docker,image};
}
test('explicit named v1 migration preserves typed legacy comparison behavior without automatic graph writes',t=>{
 const f=fixture(t),cases:any[]=[],legacyArtifacts:any[]=[];
 const inputs=[{name:'amount',type:scalar('UInt64')},{name:'other',type:scalar('UInt64')},{name:'text',type:scalar()},{name:'other_text',type:scalar()},{name:'enabled',type:scalar('Bool')},{name:'other_enabled',type:scalar('Bool')}];
 const parameter=(name:string)=>({kind:'parameter',name}),operand=(name:string)=>parameter(name);
 const expressions:any[]=[];
 for(const [left,right]of [['amount','other'],['text','other_text'],['enabled','other_enabled']])for(const op of left==='enabled'?['eq']:['eq','lt','lte','gt','gte'])expressions.push({op,left:operand(left!),right:operand(right!)});
 expressions.push({op:'all',terms:[{op:'eq',left:parameter('enabled'),right:{kind:'literal',type:'Bool',value:true}},{op:'gte',left:parameter('amount'),right:{kind:'literal',type:'UInt64',value:2}}]});
 expressions.push({op:'any',terms:[{op:'eq',left:parameter('text'),right:{kind:'literal',type:'String',value:'same'}},{op:'not',term:{op:'eq',left:parameter('enabled'),right:parameter('other_enabled')}}]});
 for(const [index,when]of expressions.entries()){
  const id='migrate-'+index,legacy={schema_version:'domainspec.typed-policy/v1',ontology_policy:'FIXTURE-MIGRATE-'+index,inputs,cases:[{target:'commerce:accept',when}],default_target:'commerce:reject'};
  const converted=migrateTypedPolicyV1(legacy,[{selector:'commerce:extracted-'+index,ontology_rule:'FIXTURE-EXTRACTED-'+index}]);
  assert.equal(converted.graph_effect,'none');assert.equal(converted.authority_effect,'none');frozen(converted);
  f.node(id,'Policy',{typed_contract:converted.policy});
  for(const rule of converted.rules)f.node(rule.selector.split(':')[1]!,'Rule',{predicate:'structured:domainspec.typed-rule/v2',typed_contract:rule.typed_contract});
  f.edge(id+'-applies-accept','applies',id,'accept');f.edge(id+'-applies-reject','applies',id,'reject');
  const realization=FROZEN_META_TYPE_CATALOG.realization_rows.find(r=>r.meta_type_label==='Policy'&&r.language==='typescript')!;
  const old=renderImplementation({project_id:'policy-rules',feature_id:'commerce',node_id:id,kind:'Policy',meta_type_id:realization.meta_type_id,realization,body:{description:id,strategies:['accept','reject'],typed_contract:legacy} as any,relationships:[],typed_closure:null});
  const relative_path='legacy/'+id+'.ts';legacyArtifacts.push({relative_path,content:old.content,size_bytes:Buffer.byteLength(old.content),sha256:sha256(old.content)});
  cases.push({id,legacy,oldPath:relative_path,oldSymbol:old.content.match(/export function ([A-Za-z0-9_]+)\(parameters/)![1]});
 }
 f.saveIndex();const fresh=f.compile(),plan=planConfiguredPolicies(fresh.graph,fresh.boundary,null,{...fresh.selection,field_compilation_sha256:null,roots:cases.map(c=>'commerce:'+c.id)},sources);
 const n=native(path.join(f.temp,'migrated'),{...plan,artifacts:[...plan.artifacts,...legacyArtifacts]});
 for(const c of cases){
  const old=createRequire(import.meta.url)(path.join(n.root,'js',c.oldPath.replace(/\.ts$/,'.js')))[c.oldSymbol];
  for(const amount of [0,2,3,Number.MAX_SAFE_INTEGER])for(const enabled of [false,true])for(const text of ['same','é','e\u0301']){
   const input={amount,other:2,text,other_text:'same',enabled,other_enabled:true};assert.equal(n.load(c.id)(input),old(input),c.id);
  }
 }
 const source=cases[0].legacy;
 assert.throws(()=>migrateTypedPolicyV1(source,[]),/named Rule/);
 assert.throws(()=>migrateTypedPolicyV1({...source,cases:[{target:'commerce:accept',when:{op:'eq',left:parameter('amount'),right:parameter('text')}}]},[{selector:'commerce:named',ontology_rule:'FIXTURE-NAMED'}]),/mismatched/);
 assert.throws(()=>migrateTypedPolicyV1({...source,cases:[{target:'commerce:accept',when:{op:'lt',left:parameter('enabled'),right:parameter('other_enabled')}}]},[{selector:'commerce:named',ontology_rule:'FIXTURE-NAMED'}]),/ordered Boolean/);
 let reads=0;assert.throws(()=>migrateTypedPolicyV1({...source,get inputs(){reads++;return inputs;}},[{selector:'commerce:named',ontology_rule:'FIXTURE-NAMED'}]));assert.equal(reads,0);
});
function observe(n:ReturnType<typeof native>,f:ReturnType<typeof fixture>){
 const prefix='application/features/commerce/src/',expected:any[]=[];
 const names=['choose','repeated','scalar'],eligible='condition0({["active"]:p2,["choice"]:p6,["note"]:p3,["numbers"]:ruleToSet(p4,ruleUInt64),["order"]:p0,["status"]:p7,["tags"]:p5})';
 for(const id of names){
  const c=f.policies[id],full=id!=='scalar',callable='policy'+id[0]!.toUpperCase()+id.slice(1),p=prefix+'domain/policies/'+id;
  const imports=full?[{path:'../rules/eligible.js',symbol:'ruleEligible',local:'condition0'},{path:'../rules/forward.js',symbol:'ruleForward',local:'condition1'}]:[{path:'../rules/high.js',symbol:'ruleHigh',local:'condition0'}];
  const targets=[...new Set([...c.cases.map((x:any)=>x.target),c.default_target])].sort() as string[];
  expected.push({path:p+'.provider.ts',kind:'policy',callable:'select',imports,inputs:c.inputs.map((p:any)=>p.name),targets,cases:full?[{expression:'condition1({["amount"]:p1})',target:'commerce:review'},{expression:eligible,target:id==='repeated'?'commerce:review':'commerce:accept'}]:[{expression:'condition0({["amount"]:p0})',target:'commerce:accept'}],default_target:'commerce:reject'});
  const catalogue=targets.map(selector=>{
   const file=path.join(f.source,'specs/commerce/nodes/'+selector.split(':')[1]+'.json'),raw=fs.readFileSync(file,'utf8'),node=JSON.parse(raw);
   return {selector,kind:node.kind,sha256:sha256(raw),body_sha256:sha256(canonicalJson(node.body))};
  });
  expected.push({path:p+'.ts',kind:'binding',callable,imports:[{path:'./'+id+'.provider.js',symbol:'select',local:'select'}],catalogue,contract_sha256:sha256(canonicalJson(c))});
 }
 expected.push({path:prefix+'domain/rules/high.ts',kind:'rule',callable:'ruleHigh',imports:[],inputs:['amount'],return_expression:'(100n < p0)'});
 expected.push({path:prefix+'domain/rules/forward.ts',kind:'rule',callable:'ruleForward',imports:[{path:'./high.js',symbol:'ruleHigh',local:'dependency0'}],inputs:['amount'],return_expression:'dependency0({["amount"]:p0})'});
 expected.push({path:prefix+'domain/rules/eligible.ts',kind:'rule',callable:'ruleEligible',imports:[],inputs:['order','active','note','numbers','tags','choice','status']});
 fs.writeFileSync(path.join(n.root,'tsconfig.json'),JSON.stringify({compilerOptions:{target:'ES2022',module:'NodeNext',strict:true,noEmit:true},files:expected.map(e=>e.path)}));
 fs.writeFileSync(path.join(n.root,'expected.json'),JSON.stringify(expected));
 const observer=path.join(project,'impl/cli/tools/observe-configured-policies.mjs');
 const supportObserver=path.join(project,'impl/cli/tools/structured-rule-support-observer.mjs');
 try{return JSON.parse(execFileSync('docker',[...n.docker.slice(0,-1),'--mount','type=bind,source='+observer+',target=/observer.mjs,readonly','--mount','type=bind,source='+supportObserver+',target=/structured-rule-support-observer.mjs,readonly',n.image,'node','/observer.mjs',path.join(n.root,'tsconfig.json'),path.join(n.root,'expected.json')],{encoding:'utf8'}));}
 catch(e){const error=e as any;if(error.status===1&&error.stdout)return JSON.parse(error.stdout);throw e;}
}
test('independent native Policy observation rejects compiling changed selection, effects and detached bindings',t=>{
 const f=fixture(t),p=f.plan(),n=native(path.join(f.temp,'observed'),p),baseline=observe(n,f);assert.equal(baseline.result,'pass',JSON.stringify(baseline));
 const m=n.module('choose'),a=p.artifacts.find(a=>a.relative_path===m.provider_path)!;
 const mutants=[
  a.content.replace('["amount"]:p1','["amount"]:p1 + 1n'),
  a.content.replace('if(condition1(','if(!condition1('),
  a.content.replace('return "commerce:reject";','return "commerce:accept";'),
  a.content.replace('  return "commerce:reject";','  Date.now();\n  return "commerce:reject";'),
  a.content.replace('  return "commerce:reject";','  (globalThis as any).selected=true;\n  return "commerce:reject";'),
  a.content.replace('  return "commerce:reject";','  queueMicrotask(()=>{});\n  return "commerce:reject";'),
  a.content+'const extra=Object.defineProperty(Object.prototype,"selected",{value:true});\n',
  a.content+'const R999Value=Object.freeze(Object.prototype);\n',
  a.content.replace('const d=ruleData(input,["enabled","id"]);','(input as Record<string,unknown>)["enabled"]=false; const d=ruleData(input,["enabled","id"]);')
 ];
 for(const mutant of mutants){assert.notEqual(mutant,a.content);fs.writeFileSync(path.join(n.root,a.relative_path),mutant);n.compile();assert.equal(observe(n,f).result,'fail');}
 fs.writeFileSync(path.join(n.root,a.relative_path),a.content);
 const binding=p.artifacts.find(a=>a.relative_path===m.relative_path)!;
 for(const mutant of [binding.content.replace('Object.assign(select,','Object.assign((_:unknown)=>"commerce:accept",'),binding.content.replace(m.descriptor.provider.sha256,'0'.repeat(64)),binding.content.replace(m.descriptor.strategy_set_sha256,'0'.repeat(64))]){
  assert.notEqual(mutant,binding.content);fs.writeFileSync(path.join(n.root,binding.relative_path),mutant);n.compile();assert.equal(observe(n,f).result,'fail');
 }
 fs.writeFileSync(path.join(n.root,binding.relative_path),binding.content);
 const rule=p.artifacts.find(a=>a.relative_path.endsWith('/high.ts'))!;
 fs.writeFileSync(path.join(n.root,rule.relative_path),rule.content.replace('(100n < p0)','(0n < p0)'));n.compile();assert.equal(observe(n,f).result,'fail');
});
test('independent runtime witnesses distinguish first-match order, input substitution and ignored Rule results',t=>{
 const f=fixture(t),p=f.plan(),n=native(path.join(f.temp,'behavior-controls'),p),m=n.module('choose'),a=p.artifacts.find(a=>a.relative_path===m.provider_path)!;
 const input=args(101),expected=n.fresh('choose',input);assert.equal(expected,'commerce:review');
 const lines=a.content.split('\n'),first=lines.findIndex(l=>l.includes('if(condition1(')),second=lines.findIndex(l=>l.includes('if(condition0('));
 const swapped=[...lines];[swapped[first],swapped[second]]=[swapped[second]!,swapped[first]!];
 for(const mutant of [swapped.join('\n'),a.content.replace('["amount"]:p1','["amount"]:0n'),a.content.replace('if(condition1(','if(!condition1(')]){
  assert.notEqual(mutant,a.content);fs.writeFileSync(path.join(n.root,a.relative_path),mutant);n.compile();assert.notEqual(n.fresh('choose',input),expected);
 }
});
test('Policy profile rejects structurally input-insensitive selections without inventing unreachable strategy proofs',t=>{
 const f=fixture(t),file='specs/commerce/nodes/scalar.json',original=read(path.join(f.source,file));
 const constant=structuredClone(original);constant.body.typed_contract.inputs=[];constant.body.typed_contract.cases[0].rule.arguments[0].value=lit('UInt64','101');f.write(file,constant);
 let fresh=f.compile();assert.throws(()=>planConfiguredPolicies(fresh.graph,fresh.boundary,null,{...fresh.selection,field_compilation_sha256:null,roots:['commerce:scalar']},sources),/requires explicit inputs/);
 const singleton=structuredClone(original);singleton.body.typed_contract.default_target='commerce:accept';f.write(file,singleton);
 const feature=read(path.join(f.source,'specs/commerce/feature.json'));feature.edges=feature.edges.filter((e:string)=>e!=='scalar-applies-reject');f.write('specs/commerce/feature.json',feature);
 fs.unlinkSync(path.join(f.source,'specs/commerce/edges/scalar-applies-reject.json'));
 fresh=f.compile();assert.throws(()=>planConfiguredPolicies(fresh.graph,fresh.boundary,null,{...fresh.selection,field_compilation_sha256:null,roots:['commerce:scalar']},sources),/distinct selectable strategies/);
});
test('Policy planner binds declared Rule closures and current strategy content without target imports',t=>{
 const f=fixture(t),p=f.plan();assert.equal(p.modules.length,3);assert.equal(p.rule_plan.modules.length,3);assert.equal(p.artifacts.length,9);assert.deepEqual(p,f.plan());frozen(p);
 assert.deepEqual(planConfiguredPolicies(f.graph,f.boundary,f.fields,{...f.selection,roots:[...f.selection.roots].reverse()},sources),p);
 const {plan_sha256,...body}=p;assert.equal(plan_sha256,sha256(canonicalJson(body)));
 for(const m of p.modules){const {descriptor_sha256,...d}=m.descriptor;assert.equal(descriptor_sha256,sha256(canonicalJson(d)));assert.equal(d.strategy_set_sha256,sha256(canonicalJson(d.catalogue)));assert.ok(m.imports.every(i=>i.path.includes('/rules/')));assert.ok(Object.isFrozen(m.descriptor));}
 assert.ok(p.artifacts.every(a=>!a.relative_path.includes('/operations/')&&!a.relative_path.includes('/calculations/')));
 const moved=planConfiguredPolicies(f.graph,f.boundary,f.fields,{...f.selection,module_root:'alternate/nested'},sources);assert.deepEqual(moved.artifacts.map(a=>a.content.includes('export const select')?a.content:null),p.artifacts.map(a=>a.content.includes('export const select')?a.content:null));
 const scalar=planConfiguredPolicies(f.graph,f.boundary,null,{...f.selection,field_compilation_sha256:null,roots:['commerce:scalar']},sources);assert.equal(scalar.field_compilation_sha256,null);assert.equal(scalar.rule_plan.field_model_sha256,null);
 for(const language of ['typescript','python','rust'] as const)assert.throws(()=>planCompiledProjectBuild(f.graph,language),/MTCLI_POLICY_PROFILE_REQUIRED/);
 fs.renameSync(f.source,path.join(f.temp,'moved-source'));assert.deepEqual(p,f.plan());
});
test('Policy checks exact Rule bindings and canonical edges without accepting inline predicates',t=>{
 const f=fixture(t),original=read(path.join(f.source,'specs/commerce/nodes/choose.json'));
 for(const mutate of [
  (n:any)=>n.body.strategies=['a'],(n:any)=>n.body.typed_contract.cases[0].when={op:'all',terms:[]},
  (n:any)=>n.body.typed_contract.cases[0].rule.selector='commerce:accept',(n:any)=>n.body.typed_contract.cases[0].rule.arguments=[],
  (n:any)=>n.body.typed_contract.cases[0].rule.arguments[0].value=at('active'),(n:any)=>n.body.typed_contract.inputs[0].type=named('missing'),
  (n:any)=>n.body.typed_contract.cases[0].target='commerce:order',(n:any)=>n.body.typed_contract.default_target='commerce:absent',
  (n:any)=>n.body.typed_contract.cases[0].rule.arguments[0].value={op:'call',selector:'commerce:review'}
 ]){const n=structuredClone(original);mutate(n);f.write('specs/commerce/nodes/choose.json',n);assert.throws(()=>loadCompiledProjectGraph(f.source));}
 f.write('specs/commerce/nodes/choose.json',original);
 const edge=read(path.join(f.source,'specs/commerce/edges/choose-applies-review.json'));f.write('specs/commerce/edges/choose-applies-review.json',{...edge,target_node_id:'eligible'});assert.throws(()=>loadCompiledProjectGraph(f.source),/applies rejects Policy->Rule/);
 for(const mutate of [(c:any)=>c.inputs.push(c.inputs[0]),(c:any)=>delete c.cases[0],(c:any)=>c.cases[0].rule.arguments.push(c.cases[0].rule.arguments[0]),(c:any)=>c.cases[0].rule.arguments[0].value=lit('UInt64','01')]){const c=structuredClone(f.policies.choose);mutate(c);assert.throws(()=>decodeTypedRulePolicyContract(c));}
 let gets=0;const c=structuredClone(f.policies.choose);Object.defineProperty(c.cases,'0',{get(){gets++;return {};},enumerable:true});assert.throws(()=>decodeTypedRulePolicyContract(c));assert.equal(gets,0);
});
test('Policy selection rejects fabricated/stale snapshots, unsafe paths, malformed roots and source drift',t=>{
 const f=fixture(t);
 for(const change of [{schema_version:'future'},{language:'rust'},{rule_selection:'old'},{value_profile:'number'},{boundary_sha256:'stale'},{field_compilation_sha256:null},{module_root:'../outside'},{module_root:'con'},{roots:[]},{roots:['commerce:choose','commerce:choose']},{roots:['commerce:high']},{extra:true}])assert.throws(()=>planConfiguredPolicies(f.graph,f.boundary,f.fields,{...f.selection,...change},sources));
 assert.throws(()=>planConfiguredPolicies(structuredClone(f.graph),f.boundary,f.fields,f.selection,sources));assert.throws(()=>planConfiguredPolicies(f.graph,structuredClone(f.boundary),f.fields,f.selection,sources));
 assert.throws(()=>planConfiguredPolicies(f.graph,f.boundary,structuredClone(f.fields),f.selection,sources));
 assert.throws(()=>planConfiguredPolicies(f.graph,f.boundary,f.fields,f.selection,{...sources,policy_contract:sources.policy_contract+' '}),/source drift/);
 for(const key of Object.keys(sources.rules))assert.throws(()=>planConfiguredPolicies(f.graph,f.boundary,f.fields,f.selection,{...sources,rules:{...sources.rules,[key]:(sources.rules as any)[key]+' '}}),/source drift/);
 let gets=0;assert.throws(()=>planConfiguredPolicies(f.graph,f.boundary,f.fields,{...f.selection,get roots(){gets++;return [];}},sources));assert.equal(gets,0);
});
test('native Policy preserves priority, explicit Rule reuse, exact inputs and identity-only results',t=>{
 const f=fixture(t),n=native(path.join(f.temp,'native'),f.plan()),select=n.load('choose'),a=args(),before=structuredClone(a);
 assert.equal(select(a),'commerce:accept');assert.equal(select(args('18446744073709551615')),'commerce:review');assert.equal(select({...a,active:false}),'commerce:reject');
 assert.equal(select({...a,status:{variant:'Draft'}}),'commerce:reject');assert.equal(select({...a,amounts:[1]}),'commerce:reject');
 assert.equal(n.load('repeated')(a),'commerce:review');assert.equal(n.load('scalar')({total:101}),'commerce:accept');assert.equal(n.load('scalar')({total:100}),'commerce:reject');
 assert.deepEqual(a,before);assert.equal(Object.isFrozen(a.order),false);assert.equal(typeof select(a),'string');frozen(select.descriptor);
 assert.equal(n.fresh('choose',args()),n.fresh('choose',args()));assert.ok(fs.existsSync(n.js('choose').replace(/\.js$/,'.d.ts')));
 const p=planConfiguredPolicies(f.graph,f.boundary,null,{...f.selection,field_compilation_sha256:null,roots:['commerce:scalar']},sources),scalar=native(path.join(f.temp,'no-data-roots'),p);assert.equal(scalar.load('scalar')({total:'18446744073709551615'}),'commerce:accept');
});
test('native Policy rejects hostile complete input facts without getters, coercion or caller writes',t=>{
 const f=fixture(t),n=native(path.join(f.temp,'hostile'),f.plan()),select=n.load('choose');let gets=0;
 for(const mutate of [(a:any)=>delete a.total,(a:any)=>a.total='01',(a:any)=>a.total='18446744073709551616',(a:any)=>a.total=9007199254740992,(a:any)=>a.total={valueOf(){gets++;return 1;}},(a:any)=>a.tags=['a','a'],(a:any)=>a.amounts=[,1],(a:any)=>a.choice={variant:'Amount'},(a:any)=>a.order={enabled:true},(a:any)=>a.extra=1]){
  const a=args();mutate(a);assert.throws(()=>select(a),/POLICY_INPUT/);
 }
 const a=args();Object.defineProperty(a,'total',{get(){gets++;return 1;},enumerable:true});assert.throws(()=>select(a),/POLICY_INPUT/);assert.equal(gets,0);
 let writes=0;const b=args();b.order=new Proxy(b.order,{set(){writes++;return false;},defineProperty(){writes++;return false;},deleteProperty(){writes++;return false;}});select(b);assert.equal(writes,0);
});
test('changed declared Rule and strategy bytes change the bound plan without conflating selection and execution',t=>{
 const f=fixture(t),p=f.plan(),first=native(path.join(f.temp,'before'),p);assert.equal(first.load('choose')(args(2)),'commerce:accept');
 const rule=read(path.join(f.source,'specs/commerce/nodes/high.json'));rule.body.typed_contract.expression.left.value='0';f.write('specs/commerce/nodes/high.json',rule);
 const fresh=f.compile(),changed=fresh.plan();assert.notEqual(changed.plan_sha256,p.plan_sha256);assert.notEqual(changed.rule_plan.plan_sha256,p.rule_plan.plan_sha256);
 assert.throws(()=>planConfiguredPolicies(fresh.graph,f.boundary,f.fields,f.selection,sources),/cross-graph/);
 assert.equal(native(path.join(f.temp,'after'),changed).load('choose')(args(2)),'commerce:review');
 const old=changed.modules.find(m=>m.selector==='commerce:choose')!.descriptor.strategy_set_sha256;
 const target=read(path.join(f.source,'specs/commerce/nodes/review.json'));target.body.description='changed existing strategy content';f.write('specs/commerce/nodes/review.json',target);
 const next=f.compile().plan();assert.notEqual(next.modules.find(m=>m.selector==='commerce:choose')!.descriptor.strategy_set_sha256,old);assert.equal(next.artifacts.some(a=>a.relative_path.includes('/calculations/')),false);
});

import {nativeToolchainImage} from '../helpers/native-toolchain-image.ts';
