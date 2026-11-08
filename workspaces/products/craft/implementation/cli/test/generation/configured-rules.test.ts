import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {createRequire} from 'node:module';
import {execFileSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import test from 'node:test';
import {loadCompiledProjectGraph, loadProjectNode, selectCompiledProjectNode} from '../../src/input/project-model.ts';
import {planConfiguredRules, CONFIGURED_RULE_VERSION, STRING_ORDER_RULE_VERSION, COLLECTION_VALUE_RULE_VERSION, COLLECTION_PREDICATE_RULE_VERSION, NUMERIC_RULE_VERSION, type ConfiguredRuleSelection} from '../../src/generation/configured-rules.ts';
import {NUMERIC_RULE_VALUE_PROFILE} from '../../src/generation/configured-rule-numeric.ts';
import {EXACT_RULE_VERSION, EXACT_LITERAL_RULE_VERSION} from '../../src/generation/configured-rules.ts';
import {decodeTypedRuleContract, decodeRuleExpression, isCanonicalUInt64Decimal} from '../../src/typed-operation/contracts.ts';
import {planInstantiation} from '../../src/generation/plan-instantiation.ts';
import {renderTypedRustRule, renderTypedRustOperation} from '../../src/typed-operation/rust.ts';
import {runInMemoryProject} from '../../src/runtime/in-memory.ts';
import {EXACT_UINT64_PROFILE} from '../../src/generation/exact-uint64.ts';
import {planCompiledProjectBuild} from '../../src/generation/project-build.ts';
import {canonicalJson, sha256} from '../../src/input/source-manifest.ts';

const project = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../../../..');
const packageRoot = path.join(project, 'development/reconciliation-v1/profile-compiler-reconciliation');
const read = (p:string) => JSON.parse(fs.readFileSync(p, 'utf8'));
const sources = {configuration: fs.readFileSync(path.join(packageRoot, 'configuration.json'), 'utf8'),
  base: fs.readFileSync(path.join(project, 'development/implementation-conformance/ontology-experiment/profiles/base-domain.profile.json'), 'utf8'),
  typescript: fs.readFileSync(path.join(project, 'development/implementation-conformance/ontology-experiment/profiles/typescript-strict.profile.json'), 'utf8')};
const stringOrderSources = {...sources, rule_contract:fs.readFileSync(path.join(packageRoot,'string-order-rule-contract.json'),'utf8')};
const collectionValueSources = {...stringOrderSources, collection_contract:fs.readFileSync(path.join(packageRoot,'rule-collection-value-contract.json'),'utf8')};
const predicateSources = {...collectionValueSources, predicate_contract:fs.readFileSync(path.join(packageRoot,'rule-collection-predicate-contract.json'),'utf8')};
const numericSources = {...predicateSources, numeric_contract:fs.readFileSync(path.join(packageRoot,'rule-numeric-contract.json'),'utf8')};
const exactSources = {...numericSources, exact_contract:fs.readFileSync(path.join(packageRoot,'rule-exact-contract.json'),'utf8')};
const exactLiteralSources = {...exactSources, literal_contract:fs.readFileSync(path.join(packageRoot,'rule-exact-literal-contract.json'),'utf8')};
const selection: ConfiguredRuleSelection = {schema_version: CONFIGURED_RULE_VERSION, language: 'typescript', module_root: 'commerce', roots: ['commerce:can-submit']};
const allRuleRoots=['commerce:can-submit','commerce:has-label','commerce:is-enabled','audit:is-enabled'];
const literal = (type:string, value:unknown) => ({op:'literal', type, value});
const parameter = (root:string) => ({op:'path', root, properties:[]});
const eq = (left:unknown, right:unknown) => ({op:'eq', left, right});
const param = (name:string, scalar='Bool') => ({name, type:{kind:'scalar', name:scalar}});
const collectionParam=(name:string,kind:'list'|'set',scalar='String')=>({name,type:{kind,element:{kind:'scalar',name:scalar}}});
function fixture(t:any) {
  const temp = fs.mkdtempSync(path.join(os.tmpdir(), 'pcr06-rules-'));
  t.after(() => fs.rmSync(temp, {recursive:true, force:true}));
  const source = path.join(temp, 'source');
  const write = (relative:string, value:unknown) => {const file=path.join(source,relative);fs.mkdirSync(path.dirname(file),{recursive:true});fs.writeFileSync(file,JSON.stringify(value,null,2)+'\n');};
  write('project.json', {schema_version:'domainspec.project/v1', project_id:'configured-rules', features:['commerce','audit'], cross_feature_edges:[]});
  write('specs/commerce/feature.json',{schema_version:'domainspec.feature/v1',feature_id:'commerce',nodes:['can-submit','has-label','is-enabled'],edges:[]});
  write('specs/audit/feature.json',{schema_version:'domainspec.feature/v1',feature_id:'audit',nodes:['is-enabled'],edges:[]});
  const rules:any = {
    'commerce:is-enabled':{parameters:[param('enabled')],expression:eq(parameter('enabled'),literal('Bool',true))},
    'audit:is-enabled':{parameters:[param('allowed')],expression:{op:'not',term:eq(parameter('allowed'),literal('Bool',false))}},
    'commerce:has-label':{parameters:[param('label','String')],expression:{op:'not',term:eq(parameter('label'),literal('String',''))}},
    'commerce:can-submit':{parameters:[param('enabled'),param('allowed'),param('label','String')],expression:{op:'all',terms:[
      {op:'rule_ref',selector:'commerce:is-enabled',arguments:[{parameter:'enabled',value:parameter('enabled')}]},
      {op:'rule_ref',selector:'audit:is-enabled',arguments:[{parameter:'allowed',value:parameter('allowed')}]},
      {op:'rule_ref',selector:'commerce:has-label',arguments:[{parameter:'label',value:parameter('label')}]}]}}};
  for(const [selector,contract] of Object.entries(rules)) {
    const [feature_id,node_id]=selector.split(':');
    write(`specs/${feature_id}/nodes/${node_id}.json`,{schema_version:'domainspec.node/v1',feature_id,node_id,kind:'Rule',body:{description:selector,predicate:'structured:domainspec.typed-rule/v1',typed_contract:{schema_version:'domainspec.typed-rule/v1',ontology_rule:selector.replace(':','-').toUpperCase(),...contract as object}}});
  }
  return {temp,source,write,graph:loadCompiledProjectGraph(source)};
}
const paths = (root='commerce') => ({audit:`${root}/features/audit/src/domain/rules/is-enabled.ts`, label:`${root}/features/commerce/src/domain/rules/has-label.ts`, enabled:`${root}/features/commerce/src/domain/rules/is-enabled.ts`, submit:`${root}/features/commerce/src/domain/rules/can-submit.ts`});
function expected(root='commerce') {
  const p=paths(root);
  return [{path:p.audit,callable:'ruleIsEnabled',imports:[]},{path:p.label,callable:'ruleHasLabel',imports:[]},{path:p.enabled,callable:'ruleIsEnabled',imports:[]},
    {path:p.submit,callable:'ruleCanSubmit',imports:[
      {path:'../../../../audit/src/domain/rules/is-enabled.js',symbol:'ruleIsEnabled',local:'dependency0'},
      {path:'./has-label.js',symbol:'ruleHasLabel',local:'dependency1'},
      {path:'./is-enabled.js',symbol:'ruleIsEnabled',local:'dependency2'}]}];
}
function writeArtifacts(root:string, artifacts:readonly {relative_path:string;content:string}[]) {
  for (const a of artifacts) {const file=path.join(root,a.relative_path);fs.mkdirSync(path.dirname(file),{recursive:true});fs.writeFileSync(file,a.content,{flag:'wx'});}
}
function native(root:string, artifacts:readonly {relative_path:string;content:string}[], expectations=expected()) {
  const toolchain=read(path.resolve(project,'../../toolchains/node-typescript/toolchain.json'));
  const image=nativeToolchainImage(toolchain.container_image);
  const args=['run','--rm','--pull','never','--network','none','--read-only','--cap-drop','ALL','--security-opt','no-new-privileges','--user',`${process.getuid!()}:${process.getgid!()}`,'--mount',`type=bind,source=${root},target=${root}`,'--workdir',root,image,'tsc'];
  assert.equal(execFileSync('docker',[...args,'--version'],{encoding:'utf8'}).trim(),'Version '+toolchain.typescript);
  execFileSync('docker',[...args,'--ignoreConfig','--strict','--skipLibCheck','--target','ES2022','--module','commonjs','--outDir',path.join(root,'js'),...artifacts.map(a=>path.join(root,a.relative_path))],{encoding:'utf8'});
  fs.writeFileSync(path.join(root,'tsconfig.json'),JSON.stringify({compilerOptions:{target:'ES2022',module:'NodeNext',strict:true,noEmit:true},files:expectations.map(e=>e.path)}));
  fs.writeFileSync(path.join(root,'expected.json'),JSON.stringify(expectations));
  return {image,observe:(observerName='observe-configured-rules.mjs',observedExpectations=expectations)=>{
    fs.writeFileSync(path.join(root,'tsconfig.json'),JSON.stringify({compilerOptions:{target:'ES2022',module:'NodeNext',strict:true,noEmit:true},files:observedExpectations.map(e=>e.path)}));
    fs.writeFileSync(path.join(root,'expected.json'),JSON.stringify(observedExpectations));
    const observer=path.join(project,'impl/cli/tools',observerName);
    const command=['run','--rm','--pull','never','--network','none','--read-only','--cap-drop','ALL','--security-opt','no-new-privileges','--tmpfs','/tmp','--user',`${process.getuid!()}:${process.getgid!()}`,'--mount',`type=bind,source=${root},target=${root},readonly`,'--mount',`type=bind,source=${observer},target=/observer.mjs,readonly`,image,'node','/observer.mjs',path.join(root,'tsconfig.json'),path.join(root,'expected.json')];
    try{return JSON.parse(execFileSync('docker',command,{encoding:'utf8'}));}
    catch(error){const e=error as any;if(e.status===1&&e.stdout)return JSON.parse(e.stdout);throw error;}
  }};
}
const loadJs=(root:string,name='can-submit')=>createRequire(import.meta.url)(path.join(root,'js',`commerce/src/domain/rules/${name}.js`));

test('PCR-06 Rule slice binds PCR-05 and checked closures, with deterministic direct leaf modules',async t=>{
  const f=fixture(t),p=planConfiguredRules(f.graph,selection,sources);
  assert.equal(p.artifacts.length,4);assert.equal(p.authority_effect,'none');
  assert.deepEqual(p.artifacts.map(a=>a.relative_path).sort(),Object.values(paths()).sort());
  assert.deepEqual(planConfiguredRules(f.graph,selection,sources),p);
  assert.deepEqual(planConfiguredRules(f.graph,{...selection,roots:['commerce:is-enabled','commerce:can-submit']},sources).artifacts,p.artifacts);
  assert.deepEqual(planConfiguredRules(f.graph,{...selection,roots:['commerce:can-submit','commerce:is-enabled']},sources),planConfiguredRules(f.graph,{...selection,roots:['commerce:is-enabled','commerce:can-submit']},sources));
  const {plan_sha256,...body}=p;assert.equal(sha256(canonicalJson(body)),plan_sha256);
  const legacy=planCompiledProjectBuild(f.graph,'typescript');
  const alternate=planConfiguredRules(f.graph,{...selection,module_root:'alternate'},sources);
  assert.deepEqual(alternate.artifacts.map(a=>a.content),p.artifacts.map(a=>a.content));
  assert.deepEqual(planCompiledProjectBuild(f.graph,'typescript'),legacy);
  const config=await import(path.join(packageRoot,'configuration.mjs'));
  const loaded=config.loadConfiguration(undefined,undefined,read(path.join(packageRoot,'configuration-input-boundary-sources.json')));
  const locations=config.previewLocations(config.resolveConfiguration({schema_version:'domainspec.compilation-selection/v1-candidate',language:'typescript',module_root:'commerce'},loaded),f.graph.nodes.map(n=>({kind:n.kind,feature_id:n.feature_id,node_id:n.node_id})));
  assert.deepEqual(locations.map((l:any)=>l.source_path).sort(),p.artifacts.map(a=>a.relative_path).sort());
  fs.renameSync(f.source,path.join(f.temp,'removed-source'));
  assert.deepEqual(planConfiguredRules(f.graph,selection,sources),p,'generation never rereads source');
  assert.throws(()=>planConfiguredRules(structuredClone(f.graph),selection,sources),/compiled graph is unvalidated or changed/);
  assert.ok(Object.isFrozen(p.artifacts));
});

test('PCR-06 selection rejects stale sources, unsupported lanes and forged options',t=>{
  const f=fixture(t);
  for(const module_root of ['con','package/class','mod','com1','lpt9']) assert.throws(()=>planConfiguredRules(f.graph,{...selection,module_root},sources),/reserved module root/);
  for(const changed of [{...selection,language:'rust'},{...selection,schema_version:'future'},{...selection,module_root:'../escape'},{...selection,module_root:'/absolute'},{...selection,roots:[]},{...selection,roots:['commerce:missing']},{...selection,roots:['commerce:can-submit','commerce:can-submit']},{...selection,ignore_blockers:true}]) assert.throws(()=>planConfiguredRules(f.graph,changed as any,sources));
  for(const key of ['configuration','base','typescript'])assert.throws(()=>planConfiguredRules(f.graph,selection,{...sources,[key]:(sources as any)[key]+' '}),/source drift/);
  const rule=read(path.join(f.source,'specs/commerce/nodes/can-submit.json'));
  rule.body.typed_contract.parameters=[param('count','UInt64')];rule.body.typed_contract.expression=eq(parameter('count'),literal('UInt64',2));
  f.write('specs/commerce/nodes/can-submit.json',rule);
  assert.throws(()=>planConfiguredRules(loadCompiledProjectGraph(f.source),selection,sources),/unsupported parameter type/);
  const feature=read(path.join(f.source,'specs/commerce/feature.json'));
  feature.nodes.push('con'); f.write('specs/commerce/feature.json',feature);
  const reservedRule=read(path.join(f.source,'specs/commerce/nodes/is-enabled.json'));
  reservedRule.node_id='con'; f.write('specs/commerce/nodes/con.json',reservedRule);
  assert.throws(()=>planConfiguredRules(loadCompiledProjectGraph(f.source),{...selection,roots:['commerce:con']},sources),/unsupported portable identifier/);
});

test('PCR-06 any composes declared Rule references with native Boolean semantics',t=>{
  const f=fixture(t),rule=read(path.join(f.source,'specs/commerce/nodes/can-submit.json'));
  rule.body.typed_contract.expression.op='any'; f.write('specs/commerce/nodes/can-submit.json',rule);
  const p=planConfiguredRules(loadCompiledProjectGraph(f.source),selection,sources),target=path.join(f.temp,'any');
  writeArtifacts(target,p.artifacts);assert.equal(native(target,p.artifacts).observe().result,'pass');
  const {ruleCanSubmit}=loadJs(target);
  for(const enabled of [false,true])for(const allowed of [false,true])for(const label of ['', 'order']) assert.equal(ruleCanSubmit({enabled,allowed,label}),enabled||allowed||label!=='');
});

test('PCR-06 native compilation and independent AST checks preserve Rule truth tables and inert inputs',t=>{
  const f=fixture(t),p=planConfiguredRules(f.graph,selection,sources),target=path.join(f.temp,'target');
  writeArtifacts(target,p.artifacts);const n=native(target,p.artifacts);
  assert.equal(n.observe().result,'pass');
  const {ruleCanSubmit}=loadJs(target);
  for(const enabled of [false,true])for(const allowed of [false,true])for(const label of ['', 'order', 'class; process.exit(); "\\']) {
    const input=Object.freeze({enabled,allowed,label});assert.equal(ruleCanSubmit(input),enabled&&allowed&&label!=='');
  }
  for(const input of [null,[],{}, {enabled:'true',allowed:true,label:'ok'},{enabled:true,allowed:true,label:'ok',extra:1},Object.create({enabled:true,allowed:true,label:'ok'})])assert.throws(()=>ruleCanSubmit(input),/RULE_INPUT/);
  let reads=0;const accessor={get enabled(){reads++;return true;},allowed:true,label:'ok'};
  assert.throws(()=>ruleCanSubmit(accessor),/RULE_INPUT/);assert.equal(reads,0);
  const file=path.join(target,paths().submit),original=fs.readFileSync(file,'utf8');
  const mutants=[
    ['wrong import',original.replace('./has-label.js','./missing.js'),'import-binding:'],
    ['extra export',original+'\nexport const bypass = ():boolean => true;\n','export-set:'],
    ['ambient call',original.replace('  return (','  console.log("hidden");\n  return ('),'undeclared-call:'],
    ['nonboolean arrow',original.replace('):boolean =>','):string =>'),'boolean-arrow:'],
    ['imperative declaration',original.replace('export const ruleCanSubmit = (','export function ruleCanSubmit(').replace('):boolean => {','):boolean {'),'extra-top-level:']];
  for(const [name,mutant,reason] of mutants){assert.notEqual(mutant,original,name);fs.writeFileSync(file,mutant!);assert.ok(n.observe().errors.some((e:string)=>e.startsWith(reason!)),name);}
  fs.writeFileSync(file,original);
  assert.equal(n.observe().result,'pass');
});

test('PCR-06 semantic mutants still compile but fail independent expected outcomes',t=>{
  const f=fixture(t),p=planConfiguredRules(f.graph,selection,sources);
  for(const [id,rewrite] of [['constant',(s:string)=>s.replace(/  return .*;\n/, '  return true;\n')],['dropped-reference',(s:string)=>s.replace('dependency0({["allowed"]:p1})','true')]] as const){
    const artifacts=p.artifacts.map(a=>({...a,content:a.relative_path===paths().submit?rewrite(a.content):a.content}));
    assert.notEqual(artifacts.find(a=>a.relative_path===paths().submit)!.content,p.artifacts.find(a=>a.relative_path===paths().submit)!.content);
    const target=path.join(f.temp,id);writeArtifacts(target,artifacts);const n=native(target,artifacts);assert.equal(n.observe().result,'pass','bounded AST is not a semantic oracle');
    const {ruleCanSubmit}=loadJs(target);assert.notEqual(ruleCanSubmit({enabled:true,allowed:false,label:'ok'}),false,id);
  }
});

test('PCR-06 String ordering is opt-in digest-bound and preserves exact v1 output',t=>{
  const f=fixture(t),rule=read(path.join(f.source,'specs/commerce/nodes/can-submit.json'));
  rule.body.typed_contract.parameters=[param('left','String'),param('right','String')];
  rule.body.typed_contract.expression={op:'lt',left:parameter('left'),right:parameter('right')};
  f.write('specs/commerce/nodes/can-submit.json',rule);const graph=loadCompiledProjectGraph(f.source);
  assert.throws(()=>planConfiguredRules(graph,selection,sources),/unsupported lt/);
  const v2={...selection,schema_version:STRING_ORDER_RULE_VERSION,roots:allRuleRoots} as ConfiguredRuleSelection;
  const p=planConfiguredRules(graph,v2,stringOrderSources);
  assert.equal(p.schema_version,'domainspec.configured-rules-plan/v2-candidate');
  assert.equal(p.input_envelope,'string-order-direct-rule-refs/v2-candidate');
  assert.match(p.artifacts.find(a=>a.relative_path===paths().submit)!.content,/return \(p0 < p1\);/);
  assert.deepEqual(planConfiguredRules(graph,{...v2,roots:[...allRuleRoots].reverse()},stringOrderSources),p);
  for(const value of [undefined,'',stringOrderSources.rule_contract+' '])
    assert.throws(()=>planConfiguredRules(graph,v2,{...stringOrderSources,rule_contract:value} as any),/source drift:rule_contract/);
  const original=fixture(t),legacy=planConfiguredRules(original.graph,selection,sources);
  assert.deepEqual(planConfiguredRules(original.graph,selection,sources),legacy);
  assert.throws(()=>planConfiguredRules(original.graph,selection,stringOrderSources),/unknown or missing fields/);
});

test('PCR-06 native String ordering follows exact ECMAScript code-unit behavior without coercion or normalization',t=>{
  const f=fixture(t),rule=read(path.join(f.source,'specs/commerce/nodes/can-submit.json'));
  rule.body.typed_contract.parameters=[param('left','String'),param('right','String')];
  rule.body.typed_contract.expression={op:'all',terms:[
    {op:'lt',left:parameter('left'),right:parameter('right')},
    {op:'not',term:{op:'eq',left:parameter('left'),right:parameter('right')}}]};
  f.write('specs/commerce/nodes/can-submit.json',rule);const graph=loadCompiledProjectGraph(f.source);
  const p=planConfiguredRules(graph,{...selection,schema_version:STRING_ORDER_RULE_VERSION,roots:allRuleRoots},stringOrderSources),target=path.join(f.temp,'string-order');
  const xp=expected();xp.find(e=>e.path===paths().submit)!.imports=[];
  writeArtifacts(target,p.artifacts);const n=native(target,p.artifacts,xp);assert.equal(n.observe().result,'pass');
  const {ruleCanSubmit}=loadJs(target);
  for(const [left,right] of [['a','b'],['A','a'],['10','2'],['e\u0301','é'],['😀','😁'],['','a']])
    assert.equal(ruleCanSubmit({left,right}),left<right,`${JSON.stringify(left)} < ${JSON.stringify(right)}`);
  assert.equal(ruleCanSubmit({left:'é',right:'e\u0301'}),'é'<'e\u0301');
  for(const input of [{left:1,right:'2'},{left:'1',right:true},{left:{toString:()=>''},right:'a'}])assert.throws(()=>ruleCanSubmit(input),/RULE_INPUT/);
});

test('PCR-06 String ordering composes through declared Rule references and short-circuit Boolean operators',t=>{
  const f=fixture(t),ordered=read(path.join(f.source,'specs/commerce/nodes/has-label.json'));
  ordered.body.typed_contract.parameters=[param('left','String'),param('right','String')];
  ordered.body.typed_contract.expression={op:'lt',left:parameter('left'),right:parameter('right')};
  f.write('specs/commerce/nodes/has-label.json',ordered);
  const root=read(path.join(f.source,'specs/commerce/nodes/can-submit.json'));
  root.body.typed_contract.parameters=[param('left','String'),param('right','String')];
  root.body.typed_contract.expression={op:'any',terms:[
    {op:'rule_ref',selector:'commerce:has-label',arguments:[{parameter:'left',value:parameter('left')},{parameter:'right',value:parameter('right')}]},
    {op:'eq',left:parameter('left'),right:parameter('right')}]};
  f.write('specs/commerce/nodes/can-submit.json',root);const graph=loadCompiledProjectGraph(f.source);
  const p=planConfiguredRules(graph,{...selection,schema_version:STRING_ORDER_RULE_VERSION,roots:allRuleRoots},stringOrderSources),target=path.join(f.temp,'string-order-ref');
  const xp=expected();xp.find(e=>e.path===paths().submit)!.imports=[{path:'./has-label.js',symbol:'ruleHasLabel',local:'dependency0'}];
  writeArtifacts(target,p.artifacts);assert.equal(native(target,p.artifacts,xp).observe().result,'pass');
  const {ruleCanSubmit}=loadJs(target);for(const [a,b] of [['a','b'],['b','a'],['a','a']])assert.equal(ruleCanSubmit({left:a,right:b}),a<=b);
});

test('PCR-06 String ordering rejects Bool UInt64 property and collection operands without broadening v2',t=>{
  const cases=[
    {parameters:[param('left'),param('right')],expression:{op:'lt',left:parameter('left'),right:parameter('right')}},
    {parameters:[param('left','String')],expression:{op:'lt',left:parameter('left'),right:literal('Bool',true)}},
    {parameters:[param('left','String')],expression:{op:'lt',left:{op:'path',root:'left',properties:['MISSING#value']},right:literal('String','z')}}];
  for(const candidate of cases){const f=fixture(t),rule=read(path.join(f.source,'specs/commerce/nodes/can-submit.json'));
    rule.body.typed_contract={...rule.body.typed_contract,...candidate};f.write('specs/commerce/nodes/can-submit.json',rule);
    assert.throws(()=>{const graph=loadCompiledProjectGraph(f.source);return planConfiguredRules(graph,{...selection,schema_version:STRING_ORDER_RULE_VERSION},stringOrderSources);},JSON.stringify(candidate));}
  const f=fixture(t),rule=read(path.join(f.source,'specs/commerce/nodes/can-submit.json'));
  rule.body.typed_contract.parameters=[param('left','String'),param('right','String')];
  rule.body.typed_contract.expression={op:'contains',left:parameter('left'),right:parameter('right')};
  f.write('specs/commerce/nodes/can-submit.json',rule);assert.throws(()=>planConfiguredRules(loadCompiledProjectGraph(f.source),{...selection,schema_version:STRING_ORDER_RULE_VERSION},stringOrderSources));
});

test('PCR-06 native String ordering mutants expose direction equality and locale substitutions',t=>{
  const f=fixture(t),rule=read(path.join(f.source,'specs/commerce/nodes/can-submit.json'));
  rule.body.typed_contract.parameters=[param('left','String'),param('right','String')];rule.body.typed_contract.expression={op:'lt',left:parameter('left'),right:parameter('right')};
  f.write('specs/commerce/nodes/can-submit.json',rule);const p=planConfiguredRules(loadCompiledProjectGraph(f.source),{...selection,schema_version:STRING_ORDER_RULE_VERSION,roots:allRuleRoots},stringOrderSources);
  const original=p.artifacts.find(a=>a.relative_path===paths().submit)!.content;
  for(const [id,rewrite,input] of [
    ['direction',(s:string)=>s.replace('p0 < p1','p1 < p0'),{left:'a',right:'b'}],
    ['equality',(s:string)=>s.replace('p0 < p1','p0 <= p1'),{left:'a',right:'a'}],
    ['locale',(s:string)=>s.replace('p0 < p1','p0.localeCompare(p1) < 0'),{left:'ä',right:'z'}]] as const){
    const content=rewrite(original),artifacts=p.artifacts.map(a=>a.relative_path===paths().submit?{...a,content}:a),target=path.join(f.temp,'string-order-'+id);
    writeArtifacts(target,artifacts);const xp=expected();xp.find(e=>e.path===paths().submit)!.imports=[];native(target,artifacts,xp);
    const fn=loadJs(target).ruleCanSubmit;assert.notEqual(fn(input),input.left<input.right,id);
  }
});

function collectionRuleFixture(t:any){
  const f=fixture(t),parameters=[collectionParam('items','list'),collectionParam('flags','list','Bool'),collectionParam('tags','set'),collectionParam('states','set','Bool'),param('enabled')];
  const dependency=read(path.join(f.source,'specs/commerce/nodes/has-label.json'));
  dependency.body.typed_contract.parameters=parameters;dependency.body.typed_contract.expression=eq(parameter('enabled'),literal('Bool',true));
  f.write('specs/commerce/nodes/has-label.json',dependency);
  const root=read(path.join(f.source,'specs/commerce/nodes/can-submit.json'));root.body.typed_contract.parameters=parameters;
  root.body.typed_contract.expression={op:'rule_ref',selector:'commerce:has-label',arguments:parameters.map(p=>({parameter:p.name,value:parameter(p.name)}))};
  f.write('specs/commerce/nodes/can-submit.json',root);
  return {...f,graph:loadCompiledProjectGraph(f.source),selection:{...selection,schema_version:COLLECTION_VALUE_RULE_VERSION,roots:allRuleRoots} as ConfiguredRuleSelection};
}
const captureDependency=`export let received:Readonly<{readonly items:readonly string[];readonly flags:readonly boolean[];readonly tags:readonly string[];readonly states:readonly boolean[];readonly enabled:boolean}>|null=null;
export const ruleHasLabel=(parameters:Readonly<{readonly items:readonly string[];readonly flags:readonly boolean[];readonly tags:readonly string[];readonly states:readonly boolean[];readonly enabled:boolean}>):boolean=>{received=parameters;return parameters.enabled;};
`;
function captureArtifacts(plan:any,rootRewrite=(content:string)=>content){return plan.artifacts.map((a:any)=>a.relative_path===paths().label?{...a,content:captureDependency}:a.relative_path===paths().submit?{...a,content:rootRewrite(a.content)}:a);}

test('PCR-06 collection values are opt-in double-contract-bound and preserve v1-v2 output',t=>{
  const f=collectionRuleFixture(t);
  assert.throws(()=>planConfiguredRules(f.graph,{...f.selection,schema_version:STRING_ORDER_RULE_VERSION},stringOrderSources),/unsupported parameter type/);
  const p=planConfiguredRules(f.graph,f.selection,collectionValueSources);
  assert.equal(p.schema_version,'domainspec.configured-rules-plan/v3-candidate');assert.equal(p.input_envelope,'scalar-collection-rule-values/v3-candidate');
  const source=p.artifacts.find(a=>a.relative_path===paths().submit)!.content;
  assert.match(source,/readonly "items":readonly string\[\]/);assert.match(source,/readonly "states":readonly boolean\[\]/);
  assert.match(source,/normalizeRuleCollection<string>\(descriptors\["tags"\]!\.value,"string",true\)/);
  assert.match(source,/dependency0\(\{\["enabled"\]:p4,\["flags"\]:p1,\["items"\]:p0,\["states"\]:p3,\["tags"\]:p2\}\)/);
  assert.deepEqual(planConfiguredRules(f.graph,{...f.selection,roots:[...allRuleRoots].reverse()},collectionValueSources),p);
  for(const value of [undefined,'',collectionValueSources.collection_contract+' '])assert.throws(()=>planConfiguredRules(f.graph,f.selection,{...collectionValueSources,collection_contract:value} as any),/source drift:collection_contract/);
  const old=fixture(t),v1=planConfiguredRules(old.graph,selection,sources),v2=planConfiguredRules(old.graph,{...selection,schema_version:STRING_ORDER_RULE_VERSION},stringOrderSources);
  assert.deepEqual(planConfiguredRules(old.graph,selection,sources),v1);assert.deepEqual(planConfiguredRules(old.graph,{...selection,schema_version:STRING_ORDER_RULE_VERSION},stringOrderSources),v2);
  assert.throws(()=>planConfiguredRules(old.graph,selection,collectionValueSources),/unknown or missing fields/);
});

test('PCR-06 native collection values copy lists and canonicalize sets before rule_ref transport',t=>{
  const f=collectionRuleFixture(t),p=planConfiguredRules(f.graph,f.selection,collectionValueSources),target=path.join(f.temp,'collection-values');
  const artifacts=captureArtifacts(p);writeArtifacts(target,artifacts);native(target,artifacts);
  const root=loadJs(target),dependency=loadJs(target,'has-label'),items=['b','a','b'],flags=[true,false,true],tags=['é','b','A','a'],states=[true,false];
  assert.equal(root.ruleCanSubmit({items,flags,tags,states,enabled:true}),true);const got=dependency.received;
  assert.deepEqual(got.items,['b','a','b']);assert.deepEqual(got.flags,[true,false,true]);assert.deepEqual(got.tags,['A','a','b','é']);assert.deepEqual(got.states,[false,true]);
  for(const value of [got.items,got.flags,got.tags,got.states])assert.ok(Object.isFrozen(value));
  items[0]='changed';flags.push(false);tags.reverse();states.reverse();assert.deepEqual(got.items,['b','a','b']);assert.deepEqual(got.tags,['A','a','b','é']);
});

test('PCR-06 collection value boundary rejects holes accessors extras duplicates prototypes and wrong elements',t=>{
  const f=collectionRuleFixture(t),p=planConfiguredRules(f.graph,f.selection,collectionValueSources),target=path.join(f.temp,'collection-invalid');
  const artifacts=captureArtifacts(p);writeArtifacts(target,artifacts);native(target,artifacts);const fn=loadJs(target).ruleCanSubmit;
  const valid=()=>({items:['a'],flags:[true],tags:['a'],states:[false],enabled:true});
  const hole=new Array(1),accessor:string[]=[];Object.defineProperty(accessor,'0',{get:()=> 'a',enumerable:true});Object.defineProperty(accessor,'length',{value:1});
  const extra=['a'];(extra as any).x=true;class Derived<T> extends Array<T>{};
  for(const patch of [{items:hole},{items:accessor},{items:extra},{items:new Derived('a')},{items:['a',1]},{flags:[true,'false']},{tags:['a','a']},{states:[false,false]},{tags:new Set(['a'])},{items:null}])
    assert.throws(()=>fn({...valid(),...patch}),/RULE_INPUT/);
  let reads=0;const top={...valid()};Object.defineProperty(top,'items',{get(){reads++;return ['a'];},enumerable:true});assert.throws(()=>fn(top),/RULE_INPUT/);assert.equal(reads,0);
});

test('PCR-06 collection values reject nested named numeric and premature collection operators',t=>{
  for(const type of [{kind:'list',element:{kind:'list',element:{kind:'scalar',name:'String'}}},{kind:'set',element:{kind:'scalar',name:'UInt64'}},{kind:'list',element:{kind:'named',selector:'commerce:item'}}]){
    const f=fixture(t),rule=read(path.join(f.source,'specs/commerce/nodes/can-submit.json'));rule.body.typed_contract.parameters=[{name:'items',type},param('enabled')];rule.body.typed_contract.expression=eq(parameter('enabled'),literal('Bool',true));
    f.write('specs/commerce/nodes/can-submit.json',rule);assert.throws(()=>planConfiguredRules(loadCompiledProjectGraph(f.source),{...selection,schema_version:COLLECTION_VALUE_RULE_VERSION},collectionValueSources));
  }
  for(const expression of [{op:'eq',left:parameter('items'),right:parameter('items')},{op:'set_equal',left:parameter('tags'),right:parameter('tags')},{op:'contains',left:parameter('items'),right:literal('String','a')},
    {op:'exists',binding:'item',collection:parameter('items'),where:eq(parameter('item'),literal('String','a'))}]){
    const f=collectionRuleFixture(t),rule=read(path.join(f.source,'specs/commerce/nodes/can-submit.json'));rule.body.typed_contract.expression=expression;f.write('specs/commerce/nodes/can-submit.json',rule);
    assert.throws(()=>planConfiguredRules(loadCompiledProjectGraph(f.source),f.selection,collectionValueSources),/collection operators unsupported|unsupported operator/);
  }
});

test('PCR-06 native collection normalization mutants expose duplicate order and ownership collapse',t=>{
  const f=collectionRuleFixture(t),p=planConfiguredRules(f.graph,f.selection,collectionValueSources),original=p.artifacts.find(a=>a.relative_path===paths().submit)!.content;
  const mutants=[
    ['duplicate',(s:string)=>s.replace("if(new Set(values).size!==values.length) throw new TypeError('RULE_INPUT');",''),{items:[],flags:[],tags:['a','a'],states:[],enabled:true},(received:any)=>received!==null],
    ['order',(s:string)=>s.replace("values.sort((a,b)=>{const ka=typeof a==='string'?'S'+a:a?'B1':'B0',kb=typeof b==='string'?'S'+b:b?'B1':'B0';return ka<kb?-1:ka>kb?1:0;});",''),{items:[],flags:[],tags:['b','a'],states:[],enabled:true},(received:any)=>received.tags[0]==='b'],
    ['ownership',(s:string)=>s.replace('return Object.freeze(values);','return values;'),{items:['a'],flags:[],tags:[],states:[],enabled:true},(received:any)=>!Object.isFrozen(received.items)]] as const;
  for(const [id,rewrite,input,wrong] of mutants){const artifacts=captureArtifacts(p,rewrite),target=path.join(f.temp,'collection-mutant-'+id);assert.notEqual(artifacts.find((a:any)=>a.relative_path===paths().submit)!.content,original);
    writeArtifacts(target,artifacts);native(target,artifacts);const root=loadJs(target),dep=loadJs(target,'has-label');if(id==='duplicate')root.ruleCanSubmit(input);else assert.equal(root.ruleCanSubmit(input),true);assert.ok(wrong(dep.received),id);}
});

const binary=(op:string,left:unknown,right:unknown)=>({op,left,right});
const quantify=(op:string,collection:unknown,where:unknown,binding='item')=>({op,binding,collection,where});
const toSet=(value:unknown)=>({op:'to_set',value});
function predicateFixture(t:any,definitions:Record<string,{parameters:unknown[];expression:unknown;schema_version?:string}>,numeric=false,exact=false,exactLiterals=false){
  const f=fixture(t),feature=read(path.join(f.source,'specs/commerce/feature.json'));
  for(const [id,contract] of Object.entries(definitions)){
    feature.nodes.push(id);
    const schema_version=contract.schema_version??(exactLiterals?'domainspec.typed-rule/v2':'domainspec.typed-rule/v1');
    f.write(`specs/commerce/nodes/${id}.json`,{schema_version:'domainspec.node/v1',feature_id:'commerce',node_id:id,kind:'Rule',body:{description:id,predicate:'structured:'+schema_version,typed_contract:{schema_version,ontology_rule:'COMMERCE-'+id.toUpperCase(),...contract}}});
  }
  f.write('specs/commerce/feature.json',feature);
  const graph=loadCompiledProjectGraph(f.source),selected={...selection,schema_version:exactLiterals?EXACT_LITERAL_RULE_VERSION:exact?EXACT_RULE_VERSION:numeric?NUMERIC_RULE_VERSION:COLLECTION_PREDICATE_RULE_VERSION,...(exact||exactLiterals?{value_profile:EXACT_UINT64_PROFILE}:numeric?{value_profile:NUMERIC_RULE_VALUE_PROFILE}:{}),roots:[...allRuleRoots,...Object.keys(definitions).map(id=>'commerce:'+id)]} as ConfiguredRuleSelection;
  return {...f,graph,selected,plan:planConfiguredRules(graph,selected,exactLiterals?exactLiteralSources:exact?exactSources:numeric?numericSources:predicateSources)};
}
const nativePredicate=(f:ReturnType<typeof predicateFixture>,suffix='predicates',rewrite=(content:string)=>content)=>{
  const target=path.join(f.temp,suffix),artifacts=f.plan.artifacts.map(a=>({...a,content:rewrite(a.content)}));
  writeArtifacts(target,artifacts);native(target,artifacts);
  return (id:string)=>loadJs(target,id)['rule'+id.split('-').map(s=>s[0]!.toUpperCase()+s.slice(1)).join('')];
};

test('PCR-06 v4 scalar collection predicates bind all inherited contracts and retain earlier version outputs',t=>{
  const f=predicateFixture(t,{'membership':{parameters:[collectionParam('items','list'),param('needle','String')],expression:binary('contains',parameter('items'),parameter('needle'))}});
  assert.equal(f.plan.schema_version,'domainspec.configured-rules-plan/v4-candidate');
  assert.equal(f.plan.input_envelope,'scalar-collection-rule-predicates/v4-candidate');
  for(const key of ['rule_contract','collection_contract','predicate_contract'] as const){
    assert.throws(()=>planConfiguredRules(f.graph,f.selected,{...predicateSources,[key]:undefined} as any),/source drift/);
    assert.throws(()=>planConfiguredRules(f.graph,f.selected,{...predicateSources,[key]:predicateSources[key]+' '}),/source drift/);
  }
  assert.throws(()=>planConfiguredRules(f.graph,{...f.selected,schema_version:COLLECTION_VALUE_RULE_VERSION},collectionValueSources),/unsupported operator:contains/);
  assert.deepEqual(planConfiguredRules(f.graph,{...f.selected,roots:[...f.selected.roots].reverse()},predicateSources),f.plan);
  const moved=planConfiguredRules(f.graph,{...f.selected,module_root:'another'},predicateSources);
  assert.deepEqual(moved.artifacts.map(a=>a.content),f.plan.artifacts.map(a=>a.content));
  const old=fixture(t);
  for(const [version,selectedSources] of [[CONFIGURED_RULE_VERSION,sources],[STRING_ORDER_RULE_VERSION,stringOrderSources],[COLLECTION_VALUE_RULE_VERSION,collectionValueSources]] as const){
    const before=planConfiguredRules(old.graph,{...selection,schema_version:version},selectedSources);
    planConfiguredRules(old.graph,{...selection,schema_version:COLLECTION_PREDICATE_RULE_VERSION},predicateSources);
    assert.deepEqual(planConfiguredRules(old.graph,{...selection,schema_version:version},selectedSources),before);
    assert.throws(()=>planConfiguredRules(old.graph,{...selection,schema_version:version},predicateSources),/unknown or missing fields/);
  }
  fs.renameSync(f.source,path.join(f.temp,'source-removed'));
  assert.deepEqual(planConfiguredRules(f.graph,f.selected,predicateSources),f.plan);
});

test('PCR-06 v4 native membership and equality distinguish lists sets exact strings and Bool',t=>{
  const definitions:Record<string,any>={};
  for(const kind of ['list','set'] as const)for(const type of ['String','Bool']){
    const id=kind+'-'+type.toLowerCase();
    definitions[id+'-contains']={parameters:[collectionParam('items',kind,type),param('needle',type)],expression:binary('contains',parameter('items'),parameter('needle'))};
    definitions[id+'-equal']={parameters:[collectionParam('left',kind,type),collectionParam('right',kind,type)],expression:eq(parameter('left'),parameter('right'))};
    if(kind==='set')definitions[id+'-set-equal']={parameters:[collectionParam('left',kind,type),collectionParam('right',kind,type)],expression:binary('set_equal',parameter('left'),parameter('right'))};
  }
  const f=predicateFixture(t,definitions),fn=nativePredicate(f);
  for(const [type,values] of [['string',['','a','A','é','e\u0301','😀','__proto__','false']],['bool',[false,true]]] as const){
    for(const kind of ['list','set']){
      const contains=fn(kind+'-'+type+'-contains'),equal=fn(kind+'-'+type+'-equal');
      for(const needle of values){assert.equal(contains({items:[],needle}),false);for(const member of values)assert.equal(contains({items:[member],needle}),member===needle);}
      const a=values[0],b=values[1];
      assert.equal(equal({left:[a,b],right:[b,a]}),kind==='set');
      assert.equal(equal({left:[],right:[]}),true);assert.equal(equal({left:[a],right:[]}),false);
      if(kind==='list')assert.equal(equal({left:[a,a],right:[a]}),false);
      else {assert.equal(fn(kind+'-'+type+'-set-equal')({left:[a,b],right:[b,a]}),true);assert.throws(()=>contains({items:[a,a],needle:a}),/RULE_INPUT/);}
      assert.throws(()=>contains({items:[a],needle:type==='bool'?'false':false}),/RULE_INPUT/);
    }
  }
  let reads=0;const accessor:string[]=[];Object.defineProperty(accessor,'0',{enumerable:true,get(){reads++;return 'a';}});
  assert.throws(()=>fn('list-string-contains')({items:accessor,needle:'a'}),/RULE_INPUT/);assert.equal(reads,0);
});

test('PCR-06 v4 native quantifiers match independently counted occurrences including empty and duplicate lists',t=>{
  const definitions:Record<string,any>={};
  for(const op of ['exists','exactly_one','unique'])for(const kind of ['list','set'] as const)for(const type of ['String','Bool']){
    definitions[kind+'-'+type.toLowerCase()+'-'+op.replace('_','-')]={parameters:[collectionParam('items',kind,type),param('needle',type)],expression:quantify(op,parameter('items'),eq(parameter('item'),parameter(op==='unique'?'item':'needle')))};
  }
  const f=predicateFixture(t,definitions),fn=nativePredicate(f);
  for(const [type,alphabet] of [['string',['a','b']],['bool',[false,true]]] as const){
    const lists:any[][]=[[]];for(let length=1;length<=4;length++)for(let mask=0;mask<2**length;mask++)lists.push(Array.from({length},(_,i)=>alphabet[(mask>>i)&1]));
    for(const items of lists)for(const needle of alphabet){
      let count=0,duplicates=false;for(let i=0;i<items.length;i++){if(items[i]===needle)count++;for(let j=0;j<i;j++)if(items[i]===items[j])duplicates=true;}
      for(const kind of ['list','set']){
        if(kind==='set'&&duplicates)continue;
        const input=Object.freeze({items:Object.freeze([...items]),needle});
        assert.equal(fn(kind+'-'+type+'-exists')(input),count>0);
        assert.equal(fn(kind+'-'+type+'-exactly-one')(input),count===1);
        assert.equal(fn(kind+'-'+type+'-unique')(input),!duplicates);
      }
    }
  }
});

test('PCR-06 v4 native conversion deduplicates lists and transports canonical sets to declared Rules',t=>{
  const f=predicateFixture(t,{
    'set-check':{parameters:[collectionParam('tags','set'),param('needle','String')],expression:binary('contains',parameter('tags'),parameter('needle'))},
    'converted-member':{parameters:[collectionParam('items','list'),param('needle','String')],expression:{op:'rule_ref',selector:'commerce:set-check',arguments:[{parameter:'tags',value:toSet(parameter('items'))},{parameter:'needle',value:parameter('needle')}]}},
    'converted-equal':{parameters:[collectionParam('items','list'),collectionParam('tags','set')],expression:binary('set_equal',toSet(parameter('items')),parameter('tags'))},
    'converted-one':{parameters:[collectionParam('items','list')],expression:quantify('exactly_one',toSet(parameter('items')),eq(parameter('item'),literal('String','a')))}
  }),fn=nativePredicate(f);
  assert.equal(fn('converted-member')({items:['b','a','a'],needle:'a'}),true);
  assert.equal(fn('converted-member')({items:['b','a','a'],needle:'c'}),false);
  assert.equal(fn('converted-equal')({items:['b','a','a'],tags:['a','b']}),true);
  assert.equal(fn('converted-equal')({items:['b','a','a'],tags:['a']}),false);
  assert.equal(fn('converted-one')({items:['a','a']}),true);
  assert.throws(()=>fn('converted-equal')({items:['a'],tags:['a','a']}),/RULE_INPUT/);
});

test('PCR-06 v4 native nested lexical scopes and Rule dependencies do not collapse or leak',t=>{
  const rootParams=[collectionParam('items','list'),collectionParam('tags','list'),param('item','String')];
  const f=predicateFixture(t,{
    'scoped-ref':{parameters:[collectionParam('items','list')],expression:quantify('exists',parameter('items'),{op:'rule_ref',selector:'commerce:has-label',arguments:[{parameter:'label',value:parameter('q0')}]},'q0')},
    'shadowed':{parameters:rootParams,expression:{op:'all',terms:[quantify('exists',parameter('items'),{op:'all',terms:[eq(parameter('item'),literal('String','outer')),quantify('exists',parameter('tags'),eq(parameter('item'),literal('String','inner'))),eq(parameter('item'),literal('String','outer'))]}),eq(parameter('item'),literal('String','root'))]}},
    'cross-scope':{parameters:rootParams,expression:quantify('exists',parameter('items'),quantify('exists',parameter('tags'),eq(parameter('item'),parameter('other')),'other'))},
    'constant-key':{parameters:rootParams,expression:quantify('unique',parameter('items'),eq(parameter('item'),parameter('item')),'member')}
  }),fn=nativePredicate(f);
  assert.ok(f.plan.modules.find(m=>m.selector==='commerce:scoped-ref')!.imports.some(i=>i.selector==='commerce:has-label'));
  assert.equal(fn('scoped-ref')({items:['','ok']}),true);assert.equal(fn('scoped-ref')({items:['','']}),false);
  const input={items:['outer'],tags:['inner'],item:'root'};
  assert.equal(fn('shadowed')(input),true);assert.equal(fn('shadowed')({...input,item:'wrong'}),false);
  assert.equal(fn('shadowed')({...input,tags:['outer']}),false);
  assert.equal(fn('cross-scope')({items:['a','b'],tags:['b'],item:'unused'}),true);
  assert.equal(fn('cross-scope')({items:['a'],tags:['b'],item:'unused'}),false);
  assert.equal(fn('constant-key')({...input,items:['a','b']}),false);
  assert.equal(fn('constant-key')({...input,items:['a']}),true);
});

test('PCR-06 v4 rejects mismatched operands non-set set_equal and unsupported key/type shapes',t=>{
  for(const expression of [binary('contains',parameter('items'),literal('Bool',true)),binary('contains',literal('String','a'),literal('String','a')),
    binary('set_equal',parameter('items'),parameter('items')),binary('set_equal',literal('String','a'),literal('String','a')),
    quantify('exists',parameter('items'),eq(parameter('missing'),literal('String','a'))),
    quantify('unique',parameter('items'),eq(parameter('items'),parameter('items'))),
    binary('set_equal',toSet(parameter('tags')),parameter('tags'))]){
    assert.throws(()=>predicateFixture(t,{'invalid':{parameters:[collectionParam('items','list'),collectionParam('tags','set')],expression}}));
  }
  for(const type of [{kind:'scalar',name:'UInt64'},{kind:'list',element:{kind:'list',element:{kind:'scalar',name:'String'}}},{kind:'optional',element:{kind:'scalar',name:'String'}}])
    assert.throws(()=>predicateFixture(t,{'invalid':{parameters:[{name:'items',type}],expression:eq(literal('Bool',true),literal('Bool',true))}}),/unsupported parameter type/);
});

test('PCR-06 v4 native compiling mutants expose predicate and occurrence substitutions',t=>{
  const f=predicateFixture(t,{
    'membership':{parameters:[collectionParam('items','list'),param('needle','String')],expression:binary('contains',parameter('items'),parameter('needle'))},
    'one':{parameters:[collectionParam('items','list'),param('needle','String')],expression:quantify('exactly_one',parameter('items'),eq(parameter('item'),parameter('needle')))},
    'distinct':{parameters:[collectionParam('items','list')],expression:quantify('unique',parameter('items'),eq(parameter('item'),parameter('item')))},
    'ordered':{parameters:[collectionParam('left','list'),collectionParam('right','list')],expression:eq(parameter('left'),parameter('right'))}
  });
  const mutants=[
    ['all-for-any',(s:string)=>s.replace('.some(','.every('),'membership',{items:['a','b'],needle:'a'},true],
    ['invert-equality',(s:string)=>s.replace('q0===p1','q0!==p1'),'membership',{items:['a'],needle:'a'},true],
    ['at-least-one',(s:string)=>s.replace('.length===1)','.length>=1)'),'one',{items:['a','a'],needle:'a'},false],
    ['ignore-duplicates',(s:string)=>s.replace('new Set(p0.map(q0=>q0)).size','p0.length'),'distinct',{items:['a','a']},false],
    ['ignore-order',(s:string)=>s.replace('q2===q1[q3]','q1.includes(q2)'),'ordered',{left:['a','b'],right:['b','a']},false]
  ] as const;
  for(const [id,rewrite,rule,input,expected] of mutants){
    assert.ok(f.plan.artifacts.some(a=>rewrite(a.content)!==a.content),id);
    const fn=nativePredicate(f,'mutant-'+id,rewrite);assert.notEqual(fn(rule)(input),expected,id);
  }
});

const collectionObserver='observe-configured-rule-collections.mjs';
function collectionObservationBindings(f:ReturnType<typeof predicateFixture>){
  return f.plan.modules.map(module=>({path:module.relative_path,callable:module.callable,imports:module.imports.map(({path,symbol,local})=>({path,symbol,local})),
    ...([EXACT_RULE_VERSION,EXACT_LITERAL_RULE_VERSION].includes(f.plan.selection.schema_version)?{value_profile:EXACT_UINT64_PROFILE}:f.plan.selection.schema_version===NUMERIC_RULE_VERSION?{value_profile:NUMERIC_RULE_VALUE_PROFILE}:{}),
    parameters:(f.graph.nodes.find(node=>node.selector===module.selector)!.body.typed_contract as any).parameters.map((p:any)=>({name:p.name,type:p.type.kind==='scalar'?p.type.name:`${p.type.kind}<${p.type.element.name}>`}))}));
}
function observationFixture(t:any){return predicateFixture(t,{
  'member':{parameters:[collectionParam('items','list'),param('needle','String')],expression:binary('contains',parameter('items'),parameter('needle'))},
  'equal':{parameters:[collectionParam('left','set'),collectionParam('right','set')],expression:binary('set_equal',parameter('left'),parameter('right'))},
  'converted':{parameters:[collectionParam('items','list'),collectionParam('tags','set')],expression:binary('set_equal',toSet(parameter('items')),parameter('tags'))},
  'one':{parameters:[collectionParam('items','list','Bool')],expression:quantify('exactly_one',parameter('items'),eq(parameter('item'),literal('Bool',true)))},
  'distinct':{parameters:[collectionParam('items','list','Bool')],expression:quantify('unique',parameter('items'),eq(parameter('item'),parameter('item')))},
  'nested':{parameters:[collectionParam('items','list'),collectionParam('tags','list')],expression:quantify('exists',parameter('items'),{op:'all',terms:[{op:'rule_ref',selector:'commerce:has-label',arguments:[{parameter:'label',value:parameter('item')}]},quantify('exists',parameter('tags'),eq(parameter('item'),literal('String','yes')))]})}
});}

test('PCR-06 collection observer independently accepts v3-v4 boundaries helpers imports and pure scoped expressions',t=>{
  const f=observationFixture(t),target=path.join(f.temp,'observed'),bindings=collectionObservationBindings(f);
  writeArtifacts(target,f.plan.artifacts);const n=native(target,f.plan.artifacts);
  const result=n.observe(collectionObserver,bindings);
  assert.deepEqual(result.errors,[]);assert.equal(result.result,'pass');
  assert.equal(result.semantic_verdict,'requires-independent-execution');
  assert.equal(result.observations.length,f.plan.modules.length);
  for(const row of result.observations)assert.equal(row.helper_digests.length,2);
  const v3=collectionRuleFixture(t),p3=planConfiguredRules(v3.graph,v3.selection,collectionValueSources),oldTarget=path.join(v3.temp,'observed-v3');
  writeArtifacts(oldTarget,p3.artifacts);const oldBindings=collectionObservationBindings({...v3,plan:p3} as any);
  assert.equal(native(oldTarget,p3.artifacts).observe(collectionObserver,oldBindings).result,'pass');
});

test('PCR-06 collection observer rejects native-compiling boundary helper export effect and binding mutants',t=>{
  const f=observationFixture(t),target=path.join(f.temp,'observation-mutants'),bindings=collectionObservationBindings(f);
  writeArtifacts(target,f.plan.artifacts);const n=native(target,f.plan.artifacts),artifact=f.plan.artifacts.find(a=>a.relative_path.endsWith('/member.ts'))!,file=path.join(target,artifact.relative_path),original=artifact.content;
  assert.equal(n.observe(collectionObserver,bindings).result,'pass');
  const mutations=[
    ['mutable-support',(s:string)=>s.replace('return Object.freeze(values);','return values;'),'helper-binding:'],
    ['extra-export',(s:string)=>s+'export const bypass=():boolean=>true;\n','export-set:'],
    ['mutable-export',(s:string)=>s.replace('export const ruleMember','export let ruleMember'),'export-not-const:'],
    ['ambient-effect',(s:string)=>s.replace('  return p0.some(', '  console.log("hidden");\n  return p0.some('),'boundary-shape:'],
    ['nested-effect',(s:string)=>s.replace('q0=>q0===p1','q0=>{console.log(q0);return q0===p1;}'),'callback-form:'],
    ['hidden-call',(s:string)=>s.replace('q0===p1','q0===p1.toLowerCase()'),'undeclared-call:'],
    ['normalization-bypass',(s:string)=>s.replace('normalizeRuleCollection<string>(descriptors["items"]!.value,"string",false)','descriptors["items"]!.value as readonly string[]'),'parameter-normalization:'],
    ['wrong-kind',(s:string)=>s.replace('normalizeRuleCollection<string>(descriptors["items"]!.value,"string",false)','normalizeRuleCollection<string>(descriptors["items"]!.value,"string",true)'),'parameter-normalization:'],
    ['boundary-bypass',(s:string)=>s.replace('if (Reflect.ownKeys(parameters).length !== 2','if (false && Reflect.ownKeys(parameters).length !== 2'),'field-boundary:'],
    ['literal-space',(s:string)=>s.replace("Array.isArray(parameters)) throw new TypeError('RULE_INPUT')","Array.isArray(parameters)) throw new TypeError('RULE INPUT')"),'object-boundary:'],
    ['wrong-binding',(s:string)=>s.replace('q0===p1','q0===(parameters.needle)'),'unsupported-expression:']
  ] as const;
  for(const [id,rewrite,reason] of mutations){const changed=rewrite(original);assert.notEqual(changed,original,id);fs.writeFileSync(file,changed);
    native(target,f.plan.artifacts);const result=n.observe(collectionObserver,bindings);assert.equal(result.result,'fail',id);assert.ok(result.errors.some((e:string)=>e.startsWith(reason)),JSON.stringify({id,errors:result.errors}));
  }
  fs.writeFileSync(file,original);
  const wrong=structuredClone(bindings);wrong.find(e=>e.path===artifact.relative_path)!.parameters[0]!.type='set<String>';
  assert.ok(n.observe(collectionObserver,wrong).errors.some((e:string)=>e.startsWith('parameter-normalization:')));
  const importArtifact=f.plan.artifacts.find(a=>a.relative_path.endsWith('/nested.ts'))!,importFile=path.join(target,importArtifact.relative_path);
  fs.writeFileSync(importFile,importArtifact.content.replace('./has-label.js','./is-enabled.js'));
  assert.ok(n.observe(collectionObserver,bindings).errors.some((e:string)=>e.startsWith('import-binding:')));
  fs.writeFileSync(importFile,importArtifact.content);
  assert.equal(n.observe(collectionObserver,bindings).result,'pass');
});

test('PCR-06 collection observer does not promote valid structure into a semantic verdict',t=>{
  const f=observationFixture(t),target=path.join(f.temp,'structure-not-meaning'),bindings=collectionObservationBindings(f);
  const artifacts=f.plan.artifacts.map(a=>a.relative_path.endsWith('/member.ts')?{...a,content:a.content.replace('.some(','.every(')}:a);
  assert.notDeepEqual(artifacts,f.plan.artifacts);writeArtifacts(target,artifacts);
  const result=native(target,artifacts).observe(collectionObserver,bindings);
  assert.equal(result.result,'pass');assert.equal(result.semantic_verdict,'requires-independent-execution');
  assert.notEqual(loadJs(target,'member').ruleMember({items:['a','b'],needle:'a'}),true);
});

const numericPair=[param('left','UInt64'),param('right','UInt64')];
const numericDefinitions=()=>({
  'less':{parameters:numericPair,expression:binary('lt',parameter('left'),parameter('right'))},
  'same':{parameters:numericPair,expression:eq(parameter('left'),parameter('right'))},
  'below-ten':{parameters:[param('value','UInt64')],expression:{op:'rule_ref',selector:'commerce:less',arguments:[{parameter:'left',value:parameter('value')},{parameter:'right',value:literal('UInt64',10)}]}},
});

test('PCR-06 numeric v5 binds explicit JSON-safe selection and contracts without changing earlier versions',t=>{
  const f=predicateFixture(t,numericDefinitions(),true);
  assert.equal(f.plan.schema_version,'domainspec.configured-rules-plan/v5-candidate');
  assert.equal(f.plan.input_envelope,'json-safe-numeric-rules/v5-candidate');
  const {value_profile,...missing}=f.selected;
  assert.throws(()=>planConfiguredRules(f.graph,missing,numericSources),/unknown or missing fields/);
  for(const value_profile of ['full-width-uint64','domainspec.typescript-exact-uint64/v1',undefined])
    assert.throws(()=>planConfiguredRules(f.graph,{...f.selected,value_profile} as any,numericSources),/unsupported numeric value profile/);
  for(const key of ['rule_contract','collection_contract','predicate_contract','numeric_contract'] as const)
    assert.throws(()=>planConfiguredRules(f.graph,f.selected,{...numericSources,[key]:numericSources[key]+' '}),/source drift/);
  assert.throws(()=>planConfiguredRules(f.graph,{...missing,schema_version:COLLECTION_PREDICATE_RULE_VERSION},predicateSources),/unsupported parameter type/);
  assert.throws(()=>planConfiguredRules(f.graph,{...f.selected,schema_version:COLLECTION_PREDICATE_RULE_VERSION},predicateSources),/unknown or missing fields/);
  assert.deepEqual(planConfiguredRules(f.graph,{...f.selected,roots:[...f.selected.roots].reverse()},numericSources),f.plan);
  assert.deepEqual(planConfiguredRules(f.graph,{...f.selected,module_root:'another'},numericSources).artifacts.map(a=>a.content),f.plan.artifacts.map(a=>a.content));
  const {plan_sha256,...body}=f.plan;assert.equal(sha256(canonicalJson(body)),plan_sha256);
  const old=fixture(t);
  for(const [schema_version,bound] of [[CONFIGURED_RULE_VERSION,sources],[STRING_ORDER_RULE_VERSION,stringOrderSources],[COLLECTION_VALUE_RULE_VERSION,collectionValueSources],[COLLECTION_PREDICATE_RULE_VERSION,predicateSources]] as const){
    const prior=planConfiguredRules(old.graph,{...selection,schema_version},bound);
    planConfiguredRules(old.graph,{...selection,schema_version:NUMERIC_RULE_VERSION,value_profile},numericSources);
    assert.deepEqual(planConfiguredRules(old.graph,{...selection,schema_version},bound),prior);
    assert.throws(()=>planConfiguredRules(old.graph,{...selection,schema_version},numericSources),/unknown or missing fields/);
  }
  fs.renameSync(f.source,path.join(f.temp,'source-removed'));
  assert.deepEqual(planConfiguredRules(f.graph,f.selected,numericSources),f.plan);
});

test('PCR-06 numeric native scalar ordering range and exact Rule arguments reject coercion and accessors',t=>{
  const f=predicateFixture(t,numericDefinitions(),true),fn=nativePredicate(f),max=9007199254740991;
  const values=[0,-0,1,2,10,max-1,max];
  for(const left of values)for(const right of values){
    assert.equal(fn('less')({left,right}),left<right);
    assert.equal(fn('same')({left,right}),left===right);
  }
  assert.equal(fn('below-ten')({value:2}),true);assert.equal(fn('below-ten')({value:10}),false);
  assert.equal(fn('below-ten')({value:max}),false);
  for(const value of [-1,0.5,NaN,Infinity,-Infinity,max+1,18446744073709551615,'2','18446744073709551615',2n,true,null,undefined,new Number(2)]){
    assert.throws(()=>fn('below-ten')({value}),/RULE_INPUT/);
    assert.throws(()=>fn('less')({left:0,right:value}),/RULE_INPUT/);
  }
  for(const input of [null,[],{},Object.create({value:2}),{value:2,extra:1},Object.defineProperty({},'value',{value:2})])
    assert.throws(()=>fn('below-ten')(input),/RULE_INPUT/);
  let reads=0;assert.throws(()=>fn('below-ten')({get value(){reads++;return 2;}}),/RULE_INPUT/);assert.equal(reads,0);
  assert.equal(fn('has-label')({label:'é'}),true);assert.equal(fn('is-enabled')({enabled:false}),false);
});

function numericCollectionDefinitions(){
  const definitions:Record<string,any>={...numericDefinitions()};
  for(const kind of ['list','set'] as const){
    definitions[kind+'-contains']={parameters:[collectionParam('items',kind,'UInt64'),param('needle','UInt64')],expression:binary('contains',parameter('items'),parameter('needle'))};
    definitions[kind+'-equal']={parameters:[collectionParam('left',kind,'UInt64'),collectionParam('right',kind,'UInt64')],expression:eq(parameter('left'),parameter('right'))};
    for(const op of ['exists','exactly_one','unique'])
      definitions[kind+'-'+op.replace('_','-')]={parameters:[collectionParam('items',kind,'UInt64'),param('needle','UInt64')],expression:quantify(op,parameter('items'),eq(parameter('item'),parameter(op==='unique'?'item':'needle')))};
  }
  definitions['set-equivalent']={parameters:[collectionParam('left','set','UInt64'),collectionParam('right','set','UInt64')],expression:binary('set_equal',parameter('left'),parameter('right'))};
  definitions['converted']={parameters:[collectionParam('items','list','UInt64'),collectionParam('tags','set','UInt64')],expression:binary('set_equal',toSet(parameter('items')),parameter('tags'))};
  definitions['converted-ref']={parameters:[collectionParam('items','list','UInt64'),param('needle','UInt64')],expression:{op:'rule_ref',selector:'commerce:set-contains',arguments:[{parameter:'items',value:toSet(parameter('items'))},{parameter:'needle',value:parameter('needle')}]}};
  return definitions;
}

test('PCR-06 numeric native collection predicates agree with independent occurrence and equality oracles',t=>{
  const f=predicateFixture(t,numericCollectionDefinitions(),true),fn=nativePredicate(f),alphabet=[0,2,10,9007199254740991];
  const lists:number[][]=[[]];
  for(let length=1;length<=3;length++)for(let code=0;code<alphabet.length**length;code++)
    lists.push(Array.from({length},(_,i)=>alphabet[Math.floor(code/alphabet.length**i)%alphabet.length]!));
  for(const items of lists)for(const needle of alphabet){
    let count=0,duplicates=false;
    for(let i=0;i<items.length;i++){if(items[i]===needle)count++;for(let j=0;j<i;j++)if(items[i]===items[j])duplicates=true;}
    for(const kind of ['list','set']){
      if(kind==='set'&&duplicates)continue;
      const input=Object.freeze({items:Object.freeze([...items]),needle});
      assert.equal(fn(kind+'-contains')(input),count>0);
      assert.equal(fn(kind+'-exists')(input),count>0);
      assert.equal(fn(kind+'-exactly-one')(input),count===1);
      assert.equal(fn(kind+'-unique')(input),!duplicates);
      const right=[...items].reverse();let ordered=true;
      for(let i=0;i<items.length;i++)if(items[i]!==right[i])ordered=false;
      assert.equal(fn(kind+'-equal')({left:items,right}),kind==='set'||ordered);
    }
  }
  for(const kind of ['list','set'])assert.equal(fn(kind+'-equal')({left:[2],right:[10]}),false);
  assert.equal(fn('set-equivalent')({left:[10,2,0],right:[0,2,10]}),true);
  assert.equal(fn('converted')({items:[10,2,2,-0,0],tags:[0,2,10]}),true);
  assert.equal(fn('converted')({items:[10,2,2],tags:[2]}),false);
  assert.equal(fn('converted-ref')({items:[10,2,2,-0],needle:0}),true);
  assert.equal(fn('list-exactly-one')({items:[-0,0],needle:0}),false);
  assert.equal(fn('list-unique')({items:[-0,0],needle:0}),false);
});

test('PCR-06 numeric native collections reject malformed inputs and transport frozen normalized copies',t=>{
  const f=predicateFixture(t,{
    'capture':{parameters:[collectionParam('items','list','UInt64'),collectionParam('tags','set','UInt64'),param('value','UInt64')],expression:eq(literal('Bool',true),literal('Bool',true))},
    'transport':{parameters:[collectionParam('items','list','UInt64'),collectionParam('tags','set','UInt64'),param('value','UInt64')],expression:{op:'rule_ref',selector:'commerce:capture',arguments:['items','tags','value'].map(parameterName=>({parameter:parameterName,value:parameter(parameterName)}))}}
  },true);
  const target=path.join(f.temp,'captured'),artifacts=f.plan.artifacts.map(a=>a.relative_path.endsWith('/capture.ts')?{...a,content:'export let captured:unknown; export const ruleCapture=(parameters:Readonly<{items:readonly number[];tags:readonly number[];value:number}>):boolean=>{captured=parameters;return true;};\n'}:a);
  writeArtifacts(target,artifacts);native(target,artifacts);
  const rule=loadJs(target,'transport').ruleTransport,observed=loadJs(target,'capture');
  const input={items:[10,2,2,-0],tags:[9007199254740991,10,-0,2],value:-0};
  assert.equal(rule(input),true);const captured=observed.captured;
  assert.deepEqual(captured,{items:[10,2,2,0],tags:[0,2,10,9007199254740991],value:0});
  assert.equal(Object.is(captured.value,-0),false);assert.equal(Object.is(captured.items[3],-0),false);
  assert.notEqual(captured.items,input.items);assert.notEqual(captured.tags,input.tags);
  assert.ok(Object.isFrozen(captured.items));assert.ok(Object.isFrozen(captured.tags));
  assert.equal(Object.is(input.items[3],-0),true);assert.deepEqual(input.tags,[9007199254740991,10,-0,2]);
  let reads=0;const accessor:number[]=[];Object.defineProperty(accessor,'0',{enumerable:true,get(){reads++;return 2;}});
  const hidden=[2];Object.defineProperty(hidden,'0',{value:2,enumerable:false});
  class Derived extends Array<number>{}
  for(const items of [[-1],[0.5],[9007199254740992],[NaN],[Infinity],['2'],[2n],[true],[[2]],Array(1),accessor,hidden,Object.assign([2],{extra:1}),new Derived(2),new Set([2])])
    for(const key of ['items','tags'])assert.throws(()=>rule({...input,[key]:items}),/RULE_INPUT/);
  assert.equal(reads,0);
  for(const tags of [[2,2],[-0,0]])assert.throws(()=>rule({...input,tags}),/RULE_INPUT/);
});

test('PCR-06 numeric native scopes compose comparisons declared Rules and independent sibling scalar types',t=>{
  const f=predicateFixture(t,{
    ...numericDefinitions(),
    'nested':{parameters:[collectionParam('items','list','UInt64'),collectionParam('tags','list','UInt64'),param('item','UInt64'),param('label','String'),param('enabled','Bool')],expression:{op:'all',terms:[
      quantify('exists',parameter('items'),{op:'all',terms:[
        {op:'rule_ref',selector:'commerce:below-ten',arguments:[{parameter:'value',value:parameter('item')}]},
        quantify('exists',parameter('tags'),binary('lt',parameter('item'),parameter('other')),'other'),
        quantify('exists',parameter('tags'),eq(parameter('item'),literal('UInt64',10))),
        eq(parameter('item'),literal('UInt64',2))]}),
      eq(parameter('item'),literal('UInt64',9007199254740991)),eq(parameter('label'),literal('String','2')),eq(parameter('enabled'),literal('Bool',true))]}}
  },true),fn=nativePredicate(f),input={items:[2],tags:[10],item:9007199254740991,label:'2',enabled:true};
  assert.equal(fn('nested')(input),true);
  for(const change of [{items:[10]},{tags:[2]},{item:2},{label:'02'},{enabled:false}])assert.equal(fn('nested')({...input,...change}),false);
  const target=path.join(f.temp,'scoped-observed');writeArtifacts(target,f.plan.artifacts);
  assert.equal(native(target,f.plan.artifacts).observe(collectionObserver,collectionObservationBindings(f)).result,'pass');
});

test('PCR-06 numeric selection rejects mixed operands invalid literals and unsupported named optional nested types',t=>{
  for(const expression of [eq(parameter('value'),literal('String','2')),binary('lt',literal('Bool',true),literal('Bool',false)),
    {op:'rule_ref',selector:'commerce:is-enabled',arguments:[{parameter:'enabled',value:parameter('value')}]},
    binary('contains',parameter('items'),literal('String','2')),binary('set_equal',parameter('items'),parameter('items'))])
    assert.throws(()=>predicateFixture(t,{'invalid':{parameters:[param('value','UInt64'),collectionParam('items','list','UInt64')],expression}},true));
  for(const value of [-1,0.5,9007199254740992,'2',null])
    assert.throws(()=>predicateFixture(t,{'invalid':{parameters:[param('value','UInt64')],expression:eq(parameter('value'),literal('UInt64',value))}},true));
  for(const type of [{kind:'optional',element:{kind:'scalar',name:'UInt64'}},{kind:'list',element:{kind:'list',element:{kind:'scalar',name:'UInt64'}}},{kind:'named',selector:'commerce:missing'}])
    assert.throws(()=>predicateFixture(t,{'invalid':{parameters:[{name:'value',type}],expression:eq(literal('Bool',true),literal('Bool',true))}},true));
});

test('PCR-06 numeric independent observer and runtime controls reject native-compiling range order and normalization mutants',t=>{
  const f=predicateFixture(t,numericCollectionDefinitions(),true),target=path.join(f.temp,'numeric-observed'),bindings=collectionObservationBindings(f);
  writeArtifacts(target,f.plan.artifacts);const n=native(target,f.plan.artifacts),result=n.observe(collectionObserver,bindings);
  assert.equal(result.result,'pass');assert.deepEqual(result.errors,[]);
  assert.ok(result.observations.every((row:any)=>row.helper_digests.length===3));
  assert.equal(result.semantic_verdict,'requires-independent-execution');
  for(const id of ['less','set-contains','converted']){
    const row=bindings.find(b=>b.path.endsWith('/'+id+'.ts'))!;
    const wrong=bindings.map(b=>b===row?{...b,parameters:b.parameters.map((p:any)=>({...p,type:p.type.replace('UInt64','String')}))}:b);
    assert.equal(n.observe(collectionObserver,wrong).result,'fail');
  }
  const artifact=f.plan.artifacts.find(a=>a.relative_path.endsWith('/less.ts'))!,file=path.join(target,artifact.relative_path);
  for(const [id,rewrite,reason] of [
    ['range',(s:string)=>s.replace('!Number.isSafeInteger(input)','!Number.isInteger(input)'),'helper-binding:'],
    ['lexical-sort',(s:string)=>s.replace('return a-b','return String(a)<String(b)?-1:String(a)>String(b)?1:0'),'helper-binding:'],
    ['zero',(s:string)=>s.replace('return input===0?0:input','return input'),'helper-binding:'],
    ['scalar-bypass',(s:string)=>s.replace('normalizeRuleUInt64(descriptors["left"]!.value)','descriptors["left"]!.value as number'),'parameter-normalization:'],
  ] as const){
    const changed=rewrite(artifact.content);assert.notEqual(changed,artifact.content,id);fs.writeFileSync(file,changed);
    native(target,f.plan.artifacts);const observed=n.observe(collectionObserver,bindings);
    assert.equal(observed.result,'fail',id);assert.ok(observed.errors.some((e:string)=>e.startsWith(reason)),id);
  }
  fs.writeFileSync(file,artifact.content);
  const collection=f.plan.artifacts.find(a=>a.relative_path.endsWith('/list-contains.ts'))!,collectionFile=path.join(target,collection.relative_path);
  fs.writeFileSync(collectionFile,collection.content.replace('"number",false)','"number",true)'));
  native(target,f.plan.artifacts);assert.ok(n.observe(collectionObserver,bindings).errors.some((e:string)=>e.startsWith('parameter-normalization:')));
  fs.writeFileSync(collectionFile,collection.content);
  // An incorrect declared profile must not be inferred back from generated helper text.
  const unselected=bindings.map(({value_profile,...row})=>({...row,parameters:row.parameters.map((p:any)=>({...p,type:p.type.replace('UInt64','String')}))}));
  assert.equal(n.observe(collectionObserver,unselected).result,'fail');
  fs.writeFileSync(file,artifact.content.replace('(p0 < p1)','(p0 > p1)'));
  native(target,f.plan.artifacts);assert.equal(n.observe(collectionObserver,bindings).result,'pass','structure is not a semantic verdict');
  assert.equal(loadJs(target,'less').ruleLess({left:2,right:10}),false,'independent expected true detects direction mutation');
  const unsafe=nativePredicate(f,'unsafe-range',s=>s.replace('!Number.isSafeInteger(input)','!Number.isInteger(input)'));
  assert.doesNotThrow(()=>unsafe('less')({left:9007199254740992,right:0}),'mutant accepts a value that the original rejects');
});

const exactMaximum=18446744073709551615n;
test('PCR-06 exact Rule inputs bind the existing full-width profile and preserve v1-v5 selections',t=>{
  const f=predicateFixture(t,numericDefinitions(),true,true),p=f.plan;
  assert.equal(p.schema_version,'domainspec.configured-rules-plan/v6-candidate');assert.equal(p.input_envelope,'exact-uint64-rule-inputs/v6-candidate');assert.equal(p.selection.value_profile,EXACT_UINT64_PROFILE);
  for(const value_profile of [NUMERIC_RULE_VALUE_PROFILE,'uint64',undefined])assert.throws(()=>planConfiguredRules(f.graph,{...f.selected,value_profile} as any,exactSources),/unsupported numeric value profile/);
  for(const key of ['rule_contract','collection_contract','predicate_contract','numeric_contract','exact_contract'] as const)
    assert.throws(()=>planConfiguredRules(f.graph,f.selected,{...exactSources,[key]:exactSources[key]+' '}),/source drift/);
  const {value_profile,...missing}=f.selected;assert.throws(()=>planConfiguredRules(f.graph,missing,exactSources),/unknown or missing fields/);
  const prior=planConfiguredRules(f.graph,{...f.selected,schema_version:NUMERIC_RULE_VERSION,value_profile:NUMERIC_RULE_VALUE_PROFILE},numericSources);
  assert.deepEqual(planConfiguredRules(f.graph,{...f.selected,roots:[...f.selected.roots].reverse()},exactSources),p);
  assert.deepEqual(planConfiguredRules(f.graph,{...f.selected,module_root:'other'},exactSources).artifacts.map(a=>a.content),p.artifacts.map(a=>a.content));
  assert.deepEqual(planConfiguredRules(f.graph,{...f.selected,schema_version:NUMERIC_RULE_VERSION,value_profile:NUMERIC_RULE_VALUE_PROFILE},numericSources),prior);
  assert.throws(()=>planConfiguredRules(f.graph,{...f.selected,schema_version:NUMERIC_RULE_VERSION},numericSources),/unsupported numeric value profile/);
  const old=fixture(t);for(const [schema_version,bound] of [[CONFIGURED_RULE_VERSION,sources],[STRING_ORDER_RULE_VERSION,stringOrderSources],[COLLECTION_VALUE_RULE_VERSION,collectionValueSources],[COLLECTION_PREDICATE_RULE_VERSION,predicateSources]] as const){
    const before=planConfiguredRules(old.graph,{...selection,schema_version},bound);planConfiguredRules(old.graph,{...selection,schema_version:EXACT_RULE_VERSION,value_profile},exactSources);
    assert.deepEqual(planConfiguredRules(old.graph,{...selection,schema_version},bound),before);
  }
  fs.renameSync(f.source,path.join(f.temp,'source-removed'));assert.deepEqual(planConfiguredRules(f.graph,f.selected,exactSources),p);
  const {plan_sha256,...body}=p;assert.equal(sha256(canonicalJson(body)),plan_sha256);
});

test('PCR-06 exact Rule inputs retain full-width scalar precision across every accepted representation',t=>{
  const f=predicateFixture(t,{...numericDefinitions(),'two':{parameters:[param('value','UInt64')],expression:eq(parameter('value'),literal('UInt64',2))}},true,true),fn=nativePredicate(f);
  const values=[0n,2n,10n,9007199254740991n,9007199254740992n,exactMaximum-1n,exactMaximum];
  const representations=(value:bigint):unknown[]=>[value,String(value),...(value<=9007199254740991n?[Number(value)]:[])];
  for(const left of values)for(const right of values)for(const a of representations(left))for(const b of representations(right)){
    assert.equal(fn('less')({left:a,right:b}),left<right);assert.equal(fn('same')({left:a,right:b}),left===right);
  }
  for(const value of [2n,2,'2'])assert.equal(fn('two')({value}),true);
  assert.equal(fn('two')({value:'3'}),false);assert.equal(fn('below-ten')({value:'2'}),true);assert.equal(fn('below-ten')({value:exactMaximum}),false);
  assert.equal(fn('same')({left:-0,right:0n}),true);
  for(const value of [-1n,exactMaximum+1n,-1,0.1,NaN,Infinity,Number(exactMaximum),9007199254740992,'18446744073709551616','00','02','+2','-0',' 2','2 ','2\n','2\r','2\u2028','2\u2029','2.0','2e0','0x2','',true,null,{},new Number(2),Object(2n)])
    assert.throws(()=>fn('below-ten')({value}),/RULE_INPUT/);
  let reads=0;assert.throws(()=>fn('below-ten')({get value(){reads++;return 2n;}}),/RULE_INPUT/);assert.equal(reads,0);
  assert.throws(()=>fn('below-ten')(Object.defineProperty({},'value',{value:2n})),/RULE_INPUT/);
  assert.equal(fn('has-label')({label:'02'}),true);assert.equal(fn('is-enabled')({enabled:true}),true);
  assert.throws(()=>fn('is-enabled')({enabled:1}),/RULE_INPUT/);
});

test('PCR-06 exact Rule inputs preserve list occurrences normalized set equality and quantifier semantics',t=>{
  const f=predicateFixture(t,numericCollectionDefinitions(),true,true),fn=nativePredicate(f),alphabet=[0n,2n,10n,exactMaximum-1n,exactMaximum];
  const lists:bigint[][]=[[]];for(let length=1;length<=3;length++)for(let n=0;n<alphabet.length**length;n++)lists.push(Array.from({length},(_,i)=>alphabet[Math.floor(n/alphabet.length**i)%alphabet.length]!));
  for(const values of lists)for(const needle of alphabet){
    let count=0,duplicates=false;for(let i=0;i<values.length;i++){if(values[i]===needle)count++;for(let j=0;j<i;j++)if(values[i]===values[j])duplicates=true;}
    const items=values.map((v,i)=>i%2?String(v):v),input={items,needle:String(needle)};
    for(const kind of ['list','set']){
      if(kind==='set'&&duplicates)continue;
      assert.equal(fn(kind+'-contains')(input),count>0);assert.equal(fn(kind+'-exists')(input),count>0);
      assert.equal(fn(kind+'-exactly-one')(input),count===1);assert.equal(fn(kind+'-unique')(input),!duplicates);
      const right=[...values].reverse().map(String);let ordered=true;for(let i=0;i<values.length;i++)if(values[i]!==values[values.length-1-i])ordered=false;
      assert.equal(fn(kind+'-equal')({left:items,right}),kind==='set'||ordered);
    }
  }
  assert.equal(fn('list-exactly-one')({items:[2,2n,'2'],needle:2n}),false);
  assert.equal(fn('list-unique')({items:[2,'2'],needle:0}),false);
  assert.equal(fn('converted')({items:[exactMaximum,'2',2n,0,0n],tags:['0',2,String(exactMaximum)]}),true);
  assert.equal(fn('converted-ref')({items:[exactMaximum,String(exactMaximum)],needle:exactMaximum}),true);
  assert.equal(fn('set-equivalent')({left:[exactMaximum,2n],right:['2',String(exactMaximum)]}),true);
  assert.equal(fn('set-equivalent')({left:[exactMaximum],right:[exactMaximum-1n]}),false);
  for(const items of [[2,2n],[2n,'2'],[-0,'0'],[exactMaximum,String(exactMaximum)]])assert.throws(()=>fn('set-contains')({items,needle:2}),/RULE_INPUT/);
  let reads=0;const accessor:any[]=[];Object.defineProperty(accessor,'0',{enumerable:true,get(){reads++;return 2n;}});
  for(const items of [[exactMaximum+1n],[9007199254740992],['2\n'],[true],Array(1),accessor,Object.assign([2n],{extra:1})])assert.throws(()=>fn('list-contains')({items,needle:2n}),/RULE_INPUT/);
  assert.equal(reads,0);
});

test('PCR-06 exact Rule inputs transport frozen normalized bigint values without mutating caller arrays',t=>{
  const f=predicateFixture(t,{
    'capture':{parameters:[collectionParam('items','list','UInt64'),collectionParam('tags','set','UInt64'),param('value','UInt64')],expression:eq(literal('Bool',true),literal('Bool',true))},
    'transport':{parameters:[collectionParam('items','list','UInt64'),collectionParam('tags','set','UInt64'),param('value','UInt64')],expression:{op:'rule_ref',selector:'commerce:capture',arguments:['items','tags','value'].map(name=>({parameter:name,value:parameter(name)}))}}
  },true,true);
  const target=path.join(f.temp,'exact-capture'),artifacts=f.plan.artifacts.map(a=>a.relative_path.endsWith('/capture.ts')?{...a,content:'export let captured:unknown;export const ruleCapture=(parameters:Readonly<{items:readonly (bigint|number|string)[];tags:readonly (bigint|number|string)[];value:bigint|number|string}>):boolean=>{captured=parameters;return true;};\n'}:a);
  writeArtifacts(target,artifacts);native(target,artifacts);const input={items:[2,'2',2n,-0],tags:[String(exactMaximum),10n,'2',-0],value:String(exactMaximum)},before=structuredClone(input);
  assert.equal(loadJs(target,'transport').ruleTransport(input),true);const captured=loadJs(target,'capture').captured;
  assert.deepEqual(captured,{items:[2n,2n,2n,0n],tags:[0n,2n,10n,exactMaximum],value:exactMaximum});
  assert.deepEqual(input,before);assert.notEqual(captured.items,input.items);assert.notEqual(captured.tags,input.tags);assert.ok(Object.isFrozen(captured.items));assert.ok(Object.isFrozen(captured.tags));
});

test('PCR-06 exact Rule inputs compose nested lexical scopes and numeric literals as bigint source',t=>{
  const f=predicateFixture(t,{...numericDefinitions(),
    'nested':{parameters:[collectionParam('items','list','UInt64'),collectionParam('tags','list','UInt64'),param('item','UInt64')],expression:{op:'all',terms:[
      quantify('exists',parameter('items'),{op:'all',terms:[quantify('exists',parameter('tags'),{op:'rule_ref',selector:'commerce:less',arguments:[{parameter:'left',value:parameter('item')},{parameter:'right',value:parameter('other')}]},'other'),quantify('exists',parameter('tags'),eq(parameter('item'),literal('UInt64',2))),eq(parameter('item'),parameter('item'))]}),
      eq(parameter('item'),literal('UInt64',10))]}}
  },true,true),fn=nativePredicate(f),input={items:[String(exactMaximum-1n)],tags:[2,exactMaximum],item:'10'};
  assert.equal(fn('nested')(input),true);assert.equal(fn('nested')({...input,tags:[2,exactMaximum-1n]}),false);assert.equal(fn('nested')({...input,item:'11'}),false);
  assert.ok(f.plan.artifacts.some(a=>a.content.includes('10n')));
  const target=path.join(f.temp,'exact-scoped');writeArtifacts(target,f.plan.artifacts);const observed=native(target,f.plan.artifacts).observe(collectionObserver,collectionObservationBindings(f));
  assert.deepEqual(observed.errors,[]);assert.ok(observed.observations.every((o:any)=>o.helper_digests.length===4));
});

test('PCR-06 exact Rule inputs expose usable native input types and keep authored literal bounds explicit',t=>{
  const f=predicateFixture(t,numericDefinitions(),true,true),target=path.join(f.temp,'exact-types');
  const consumer={relative_path:'consumer.ts',content:'import {ruleLess} from "./commerce/features/commerce/src/domain/rules/less.js";\nruleLess({left:18446744073709551614n,right:"18446744073709551615"});\nruleLess({left:2,right:10n});\n'};
  writeArtifacts(target,[...f.plan.artifacts,consumer]);native(target,[...f.plan.artifacts,consumer]);
  fs.writeFileSync(path.join(target,'consumer.ts'),consumer.content+'ruleLess({left:true,right:2n});\n');assert.throws(()=>native(target,[...f.plan.artifacts,consumer]));
  for(const value of ['18446744073709551615',9007199254740992])assert.throws(()=>predicateFixture(t,{'invalid':{parameters:[param('value','UInt64')],expression:eq(parameter('value'),literal('UInt64',value))}},true,true),'existing source schema is not silently widened');
  assert.throws(()=>predicateFixture(t,{'invalid':{parameters:[param('value','UInt64')],expression:eq(parameter('value'),literal('String','2'))}},true,true));
});

test('PCR-06 exact Rule inputs independent observation and behavior detect compiling precision range and coercion mutants',t=>{
  const f=predicateFixture(t,numericCollectionDefinitions(),true,true),target=path.join(f.temp,'exact-observer'),bindings=collectionObservationBindings(f);
  writeArtifacts(target,f.plan.artifacts);const n=native(target,f.plan.artifacts);assert.deepEqual(n.observe(collectionObserver,bindings).errors,[]);
  assert.equal(n.observe(collectionObserver,bindings.map(b=>({...b,value_profile:NUMERIC_RULE_VALUE_PROFILE}))).result,'fail');
  const artifact=f.plan.artifacts.find(a=>a.relative_path.endsWith('/same.ts'))!,file=path.join(target,artifact.relative_path);
  for(const [id,rewrite] of [
    ['precision',(s:string)=>s.replace('return result;','return BigInt(Number(result));')],
    ['overflow',(s:string)=>s.replace('result>18446744073709551615n','result>18446744073709551616n')],
    ['coercion',(s:string)=>s.replace("input.length<=20&&/^(0|[1-9][0-9]*)$/.exec(input)?.[0]===input","input.trim().length>0")],
    ['mutable',(s:string)=>s.replace('return Object.freeze(values);','return values;')]
  ] as const){const changed=rewrite(artifact.content);assert.notEqual(changed,artifact.content,id);fs.writeFileSync(file,changed);native(target,f.plan.artifacts);assert.ok(n.observe(collectionObserver,bindings).errors.some((e:string)=>e.startsWith('helper-binding:')),id);}
  fs.writeFileSync(file,artifact.content);
  const precision=nativePredicate(f,'exact-rounded',s=>s.replace('return result;','return BigInt(Number(result));'));
  assert.equal(precision('same')({left:exactMaximum-1n,right:exactMaximum}),true,'rounded mutant collapses distinct integers');
  const overflow=nativePredicate(f,'exact-overflow',s=>s.replace('result>18446744073709551615n','result>18446744073709551616n'));
  assert.equal(overflow('same')({left:exactMaximum+1n,right:exactMaximum+1n}),true,'overflow mutant accepts forbidden value');
  const direction=f.plan.artifacts.map(a=>a.relative_path.endsWith('/less.ts')?{...a,content:a.content.replace('(p0 < p1)','(p0 > p1)')}:a),other=path.join(f.temp,'exact-direction');
  writeArtifacts(other,direction);assert.equal(native(other,direction).observe(collectionObserver,bindings).result,'pass');
  assert.equal(loadJs(other,'less').ruleLess({left:exactMaximum-1n,right:exactMaximum}),false,'semantic oracle detects reversed comparison');
});

const decimalLiteral=(value:string)=>literal('UInt64',value);
const exactLiteralFixture=(t:any,definitions:Parameters<typeof predicateFixture>[1])=>predicateFixture(t,definitions,true,true,true);
const exactThresholdDefinitions=()=>({
  'at-maximum':{parameters:[param('value','UInt64')],expression:eq(parameter('value'),decimalLiteral('18446744073709551615'))},
  'below-maximum':{parameters:[param('value','UInt64')],expression:binary('lt',parameter('value'),decimalLiteral('18446744073709551615'))},
  'above-safe':{parameters:[param('value','UInt64')],expression:binary('lt',decimalLiteral('9007199254740991'),parameter('value'))},
  'constant-order':{parameters:[param('enabled')],expression:binary('lt',decimalLiteral('18446744073709551614'),decimalLiteral('18446744073709551615'))},
  'numeric-order':{parameters:[param('enabled')],expression:binary('lt',decimalLiteral('10'),decimalLiteral('2'))},
  'text-order':{parameters:[param('enabled')],expression:binary('lt',literal('String','10'),literal('String','2'))},
  'zero':{parameters:[param('value','UInt64')],expression:eq(parameter('value'),decimalLiteral('0'))}
});

test('PCR-06 exact Rule literals decode explicit v2 decimal source without widening v1',()=>{
  const raw=(schema_version:string,value:unknown)=>({schema_version,ontology_rule:'COMMERCE-LIMIT',parameters:[param('value','UInt64')],expression:eq(parameter('value'),literal('UInt64',value))});
  for(const value of ['0','1','10','9007199254740991','9007199254740992','18446744073709551614','18446744073709551615']){
    const source=raw('domainspec.typed-rule/v2',value),decoded=decodeTypedRuleContract(source);
    assert.deepEqual(decoded,source);assert.ok(Object.isFrozen(decoded)&&Object.isFrozen(decoded.expression));
    assert.equal(JSON.parse(JSON.stringify(decoded)).expression.right.value,value);
    assert.throws(()=>decodeTypedRuleContract({...source,schema_version:'domainspec.typed-rule/v1'}),/literal does not match/);
    assert.throws(()=>decodeRuleExpression(source.expression),/literal does not match/,'standalone decoder remains v1');
  }
  for(const value of [0,1,9007199254740991])assert.deepEqual(decodeTypedRuleContract(raw('domainspec.typed-rule/v1',value)),raw('domainspec.typed-rule/v1',value));
  const invalid:unknown[]=[0,-0,1,9007199254740992,Infinity,NaN,0n,null,true,{},[],new String('1'),'', '00','01','-0','-1','+1',' 1','1 ','1.0','1e1','0x10','18446744073709551616','999999999999999999999'];
  for(const ending of ['\n','\r','\r\n','\u2028','\u2029','\t','\0'])invalid.push('1'+ending);
  for(const value of invalid){assert.equal(isCanonicalUInt64Decimal(value),false,String(value));assert.throws(()=>decodeTypedRuleContract(raw('domainspec.typed-rule/v2',value)),/literal does not match/);}
  for(let i=0;i<80;i++){const value=(BigInt(i)*230584300921369395n).toString();assert.equal(isCanonicalUInt64Decimal(value),BigInt(value)<=exactMaximum);}
  assert.throws(()=>decodeTypedRuleContract(raw('domainspec.typed-rule/v3','1')),/unsupported typed Rule schema/);
  const extra=raw('domainspec.typed-rule/v2','1');(extra.expression.right as any).encoding='decimal';assert.throws(()=>decodeTypedRuleContract(extra),/unknown|unexpected|fields/);
});

test('PCR-06 exact Rule literals bind v7 sources and retain exact v6 artifact bytes for v1 inputs',t=>{
  const old=predicateFixture(t,numericDefinitions(),true,true);
  const newer=planConfiguredRules(old.graph,{...old.selected,schema_version:EXACT_LITERAL_RULE_VERSION},exactLiteralSources);
  assert.deepEqual(newer.artifacts,old.plan.artifacts);assert.deepEqual(newer.modules,old.plan.modules);
  const f=exactLiteralFixture(t,exactThresholdDefinitions()),p=f.plan;
  assert.equal(p.schema_version,'domainspec.configured-rules-plan/v7-candidate');assert.equal(p.input_envelope,'exact-uint64-rule-literals/v7-candidate');
  for(const key of Object.keys(exactLiteralSources) as (keyof typeof exactLiteralSources)[])assert.throws(()=>planConfiguredRules(f.graph,f.selected,{...exactLiteralSources,[key]:exactLiteralSources[key]+' '}),/source drift/);
  const {literal_contract,...missing}=exactLiteralSources;assert.throws(()=>planConfiguredRules(f.graph,f.selected,missing),/unknown or missing fields/);
  assert.throws(()=>planConfiguredRules(f.graph,{...f.selected,value_profile:NUMERIC_RULE_VALUE_PROFILE},exactLiteralSources),/unsupported numeric value profile/);
  assert.deepEqual(planConfiguredRules(f.graph,{...f.selected,roots:[...f.selected.roots].reverse()},exactLiteralSources),p);
  assert.deepEqual(planConfiguredRules(f.graph,{...f.selected,module_root:'relocated'},exactLiteralSources).artifacts.map(a=>a.content),p.artifacts.map(a=>a.content));
  const fromSource=loadProjectNode(f.source,'commerce:at-maximum'),fromSnapshot=selectCompiledProjectNode(f.graph,'commerce:at-maximum');
  assert.deepEqual(fromSource.typed_closure,fromSnapshot.typed_closure);
  assert.equal(fromSnapshot.typed_closure?.rules.find(row=>row.domainspec_selector==='commerce:at-maximum')?.ontology_rule,'COMMERCE-AT-MAXIMUM');
  fs.renameSync(f.source,path.join(f.temp,'removed-source'));
  assert.deepEqual(planConfiguredRules(f.graph,f.selected,exactLiteralSources),p,'generation consumes checked bytes, not mutable files');
});

test('PCR-06 exact Rule literals compile full-width thresholds and keep text Bool and numeric meanings separate',t=>{
  const f=exactLiteralFixture(t,exactThresholdDefinitions()),fn=nativePredicate(f);
  for(const value of [0n,1n,10n,9007199254740991n,9007199254740992n,exactMaximum-1n,exactMaximum]){
    for(const input of [value,value.toString(),...(value<=9007199254740991n?[Number(value)]:[])]){
      assert.equal(fn('at-maximum')({value:input}),value===exactMaximum);
      assert.equal(fn('below-maximum')({value:input}),value<exactMaximum);
      assert.equal(fn('above-safe')({value:input}),value>9007199254740991n);
      assert.equal(fn('zero')({value:input}),value===0n);
    }
  }
  assert.equal(fn('constant-order')({enabled:true}),true);assert.equal(fn('numeric-order')({enabled:true}),false);assert.equal(fn('text-order')({enabled:true}),true);
  for(const input of [exactMaximum+1n,'18446744073709551616',Number(exactMaximum),true])assert.throws(()=>fn('at-maximum')({value:input}),/RULE_INPUT/);
  const target=path.join(f.temp,'literal-observer');writeArtifacts(target,f.plan.artifacts);
  assert.equal(native(target,f.plan.artifacts).observe(collectionObserver,collectionObservationBindings(f)).result,'pass');
  assert.ok(f.plan.artifacts.find(a=>a.relative_path.endsWith('/at-maximum.ts'))!.content.includes('=== 18446744073709551615n'));
});

test('PCR-06 exact Rule literals compose collections lexical scopes and mixed-version Rule calls',t=>{
  const call=(selector:string,value:unknown)=>({op:'rule_ref',selector,arguments:[{parameter:'value',value}]});
  const f=exactLiteralFixture(t,{
    'is-max':{parameters:[param('value','UInt64')],expression:eq(parameter('value'),decimalLiteral('18446744073709551615'))},
    'old-one':{schema_version:'domainspec.typed-rule/v1',parameters:[param('value','UInt64')],expression:eq(parameter('value'),literal('UInt64',1))},
    'old-caller':{schema_version:'domainspec.typed-rule/v1',parameters:[param('value','UInt64')],expression:call('commerce:is-max',parameter('value'))},
    'constant-call':{parameters:[param('enabled')],expression:call('commerce:is-max',decimalLiteral('18446744073709551615'))},
    'old-call':{parameters:[param('enabled')],expression:call('commerce:old-one',decimalLiteral('1'))},
    'contains-max':{parameters:[collectionParam('items','list','UInt64')],expression:binary('contains',parameter('items'),decimalLiteral('18446744073709551615'))},
    'set-contains-max':{parameters:[collectionParam('items','set','UInt64')],expression:binary('contains',parameter('items'),decimalLiteral('18446744073709551615'))},
    'one-max':{parameters:[collectionParam('items','list','UInt64')],expression:quantify('exactly_one',parameter('items'),call('commerce:is-max',parameter('item')))},
    'one-distinct-max':{parameters:[collectionParam('items','list','UInt64')],expression:quantify('exactly_one',toSet(parameter('items')),eq(parameter('item'),decimalLiteral('18446744073709551615')))},
    'nested':{parameters:[collectionParam('items','list','UInt64')],expression:quantify('exists',parameter('items'),{op:'all',terms:[eq(parameter('outer'),decimalLiteral('18446744073709551614')),quantify('exists',parameter('items'),{op:'all',terms:[call('commerce:is-max',parameter('inner')),binary('lt',parameter('outer'),parameter('inner'))]},'inner')]},'outer')}
  }),fn=nativePredicate(f),alphabet=[0n,exactMaximum-1n,exactMaximum];
  const lists:bigint[][]=[[]];for(let length=1;length<=3;length++)for(const prefix of lists.filter(x=>x.length===length-1))for(const value of alphabet)lists.push([...prefix,value]);
  for(const list of lists){const count=list.filter(x=>x===exactMaximum).length,items=list.map((x,i)=>i%2?x.toString():x);
    assert.equal(fn('contains-max')({items}),count>0);assert.equal(fn('one-max')({items}),count===1);assert.equal(fn('one-distinct-max')({items}),count>0);
    assert.equal(fn('nested')({items}),list.includes(exactMaximum-1n)&&count>0);
    assert.equal(fn('set-contains-max')({items:[...new Set(list)]}),count>0);
  }
  assert.equal(fn('old-caller')({value:exactMaximum}),true);assert.equal(fn('old-caller')({value:exactMaximum-1n}),false);
  assert.equal(fn('constant-call')({enabled:true}),true);assert.equal(fn('old-call')({enabled:true}),true);
  const old=selectCompiledProjectNode(f.graph,'commerce:old-caller');assert.ok(old.typed_closure?.nodes.some(n=>n.typed_contract.schema_version==='domainspec.typed-rule/v2'));
  assert.throws(()=>planConfiguredRules(f.graph,{...f.selected,schema_version:EXACT_RULE_VERSION,roots:['commerce:old-caller']},exactSources),/typed Rule v2 requires/);
});

test('PCR-06 exact Rule literals reject type scope and version mismatches before returning source',t=>{
  for(const right of [literal('String','18446744073709551615'),literal('Bool',true),parameter('missing')])assert.throws(()=>exactLiteralFixture(t,{'bad':{parameters:[param('value','UInt64')],expression:eq(parameter('value'),right)}}));
  assert.throws(()=>exactLiteralFixture(t,{'bad':{parameters:[param('value','UInt64')],expression:quantify('exists',parameter('value'),eq(parameter('item'),decimalLiteral('0')))}}));
  assert.throws(()=>exactLiteralFixture(t,{'bad':{parameters:[param('enabled')],expression:{op:'rule_ref',selector:'commerce:is-enabled',arguments:[{parameter:'enabled',value:decimalLiteral('1')}]}}}));
  const f=exactLiteralFixture(t,exactThresholdDefinitions());
  for(const [schema_version,bound] of [[CONFIGURED_RULE_VERSION,sources],[STRING_ORDER_RULE_VERSION,stringOrderSources],[COLLECTION_VALUE_RULE_VERSION,collectionValueSources],[COLLECTION_PREDICATE_RULE_VERSION,predicateSources],[NUMERIC_RULE_VERSION,numericSources],[EXACT_RULE_VERSION,exactSources]] as const){
    assert.throws(()=>planConfiguredRules(f.graph,{...selection,schema_version,roots:['commerce:at-maximum'],...(schema_version===EXACT_RULE_VERSION?{value_profile:EXACT_UINT64_PROFILE}:schema_version===NUMERIC_RULE_VERSION?{value_profile:NUMERIC_RULE_VALUE_PROFILE}:{})},bound),/typed Rule v2 requires/);
  }
});

test('PCR-06 exact Rule literals reject legacy generation and runtime for selected roots and transitive dependencies',t=>{
  const f=exactLiteralFixture(t,{
    'limit':{parameters:[param('value','UInt64')],expression:eq(parameter('value'),decimalLiteral('18446744073709551615'))},
    'old-caller':{schema_version:'domainspec.typed-rule/v1',parameters:[param('value','UInt64')],expression:{op:'rule_ref',selector:'commerce:limit',arguments:[{parameter:'value',value:parameter('value')}]}}
  });
  const invocation=(selector:string,parameters:unknown)=>({schema_version:'domainspec.runtime-invocation/v1',invocation_id:'literal-check',provider:'in-memory-v1',steps:[{step_id:'evaluate',selector,input:{parameters}}]});
  for(const selector of ['commerce:limit','commerce:old-caller']){
    const node=selectCompiledProjectNode(f.graph,selector);
    for(const language of ['typescript','python','rust'] as const)assert.throws(()=>planInstantiation(node,language),/typed Rule v2/);
    assert.throws(()=>planInstantiation(node,'typescript',null,EXACT_UINT64_PROFILE),/typed Rule v2/);
    assert.throws(()=>renderTypedRustRule(node.typed_closure as any),/typed Rule v2/);
    assert.throws(()=>runInMemoryProject(f.source,invocation(selector,{value:0})),/typed Rule v2/);
  }
  assert.ok(planInstantiation(selectCompiledProjectNode(f.graph,'commerce:is-enabled'),'typescript').artifacts.length>0);
  assert.equal(runInMemoryProject(f.source,invocation('commerce:is-enabled',{enabled:true})).outcomes[0]!.output,true,'unselected v2 nodes do not disable unrelated v1 execution');
  // Isolate the build compatibility boundary from the unrelated fixture's two
  // same-named legacy Rust callables in different features.
  f.write('project.json',{schema_version:'domainspec.project/v1',project_id:'configured-rules',features:['commerce'],cross_feature_edges:[]});
  f.write('specs/commerce/feature.json',{schema_version:'domainspec.feature/v1',feature_id:'commerce',nodes:['limit','old-caller'],edges:[]});
  const buildGraph=loadCompiledProjectGraph(f.source);
  for(const language of ['typescript','python','rust'] as const)assert.throws(()=>planCompiledProjectBuild(buildGraph,language),/typed Rule v2/);
});

test('PCR-06 exact Rule literals native compiling constant mutants fail independent outcomes',t=>{
  const f=exactLiteralFixture(t,{'at-maximum':exactThresholdDefinitions()['at-maximum']}),bindings=collectionObservationBindings(f);
  const original=f.plan.artifacts.find(a=>a.relative_path.endsWith('/at-maximum.ts'))!;
  for(const [id,replacement,structural] of [
    ['adjacent','18446744073709551614n','pass'],
    ['overflow','18446744073709551616n','pass'],
    ['rounded','BigInt(Number("18446744073709551615"))','fail']
  ]){
    const changed=original.content.replace('=== 18446744073709551615n','=== '+replacement);assert.notEqual(changed,original.content);
    const artifacts=f.plan.artifacts.map(a=>a===original?{...a,content:changed}:a),target=path.join(f.temp,'literal-mutant-'+id);writeArtifacts(target,artifacts);
    const observed=native(target,artifacts).observe(collectionObserver,bindings);assert.equal(observed.result,structural,id);
    assert.equal(loadJs(target,'at-maximum').ruleAtMaximum({value:exactMaximum}),false,'independent maximum-equality oracle rejects '+id);
  }
});

test('PCR-06 exact Rule literals preserve Operation closure dependency binding without enabling a legacy evaluator',t=>{
  const f=fixture(t),source=path.join(f.temp,'capacity');
  fs.cpSync(path.join(project,'impl/cli/test/fixtures/capacity-decision'),source,{recursive:true});
  const file=path.join(source,'specs/capacity-decision/nodes/within-capacity.json'),node=read(file);
  const original=loadProjectNode(source,'capacity-decision:decide-capacity').typed_closure!;
  node.body.typed_contract.schema_version='domainspec.typed-rule/v2';node.body.predicate='structured:domainspec.typed-rule/v2';
  const exactValues=(value:any):any=>Array.isArray(value)?value.map(exactValues):value&&typeof value==='object'?Object.fromEntries(Object.entries(value).map(([key,child])=>[key,key==='value'&&value.op==='literal'&&value.type==='UInt64'?String(child):exactValues(child)])):value;
  node.body.typed_contract.expression=exactValues(node.body.typed_contract.expression);fs.writeFileSync(file,JSON.stringify(node,null,2)+'\n');
  const changed=loadProjectNode(source,'capacity-decision:decide-capacity'),closure=changed.typed_closure!;
  assert.equal(closure.schema_version,'domainspec.typed-operation-closure/v1');assert.notEqual(closure.closure_sha256,original.closure_sha256);
  assert.deepEqual(closure.rules,original.rules);assert.deepEqual(closure.relationships,original.relationships);
  assert.ok(closure.nodes.some(n=>n.typed_contract.schema_version==='domainspec.typed-rule/v2'));
  assert.throws(()=>renderTypedRustOperation(closure as any),/typed Rule v2/);
  assert.throws(()=>planInstantiation(changed,'rust'),/typed Rule v2/);
  assert.throws(()=>runInMemoryProject(source,{schema_version:'domainspec.runtime-invocation/v1',invocation_id:'operation-literal',provider:'in-memory-v1',steps:[{step_id:'evaluate',selector:'capacity-decision:decide-capacity',input:{parameters:{}}}]}),/typed Rule v2/,'reject unsupported closure before interpreting parameters');
});

import {nativeToolchainImage} from '../helpers/native-toolchain-image.ts';
