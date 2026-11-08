// H01 installed adaptation of craft/projects/domainspec-v2/impl/cli/test/u0-direct-condition.test.ts.
// All positive producers are actual packaged dist modules; negative-only custody stubs retain component scope.
// Open Questions: ../README.md and H01 CONTEXT. No original task file changed.
import test,{type TestContext} from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync,mkdirSync,mkdtempSync,writeFileSync,rmSync,renameSync,symlinkSync} from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import {pathToFileURL} from 'node:url';
const installedCore=path.join(process.env.U0_INSTALLED_CONSUMER!,'node_modules/@domainspec-v2/cli');
const {compileProject}=await import(pathToFileURL(path.join(installedCore,'dist','compilation/certificate.js')).href);
const {assertCompiledProjectFields}=await import(pathToFileURL(path.join(installedCore,'dist','input/compiled-field-model.js')).href);
const {checkDirectBusinessSourceGraphV2,assertDirectBusinessSourceGraphV2Current}=await import(pathToFileURL(path.join(installedCore,'dist','formalization/direct-condition-binding.js')).href);
const {compileFormalConditionBindings}=await import(pathToFileURL(path.join(installedCore,'dist','formalization/condition-binding.js')).href);
const {createAuthoringBusinessInputOwnerV2}=await import(pathToFileURL(path.join(installedCore,'dist','profile-engine/business-authoring-input.js')).href);
const {createBusinessDirectApplicationOwnerV2}=await import(pathToFileURL(path.join(installedCore,'dist','profile-engine/business-authoring-application.js')).href);
const {createBusinessCoreRecipeOwnerV2}=await import(pathToFileURL(path.join(installedCore,'dist','profile-engine/business-authoring-recipes.js')).href);
const {createBusinessReviewOwnerV2}=await import(pathToFileURL(path.join(installedCore,'dist','profile-engine/business-decision.js')).href);
const {createBusinessRequestStagesOwnerV2}=await import(pathToFileURL(path.join(installedCore,'dist','profile-engine/business-authoring-request.js')).href);
// Actual project/type-checker component evidence; no selected/native basis, accepted
// input or final graph/condition is fabricated. U04/G01 qualify those real joins.
// Open Questions: J01 SDK graph capture, U04 accepted input, G01 generated witness.
const root=process.env.U0_INSTALLED_CONSUMER!,alch=path.join(root,'node_modules/@cyberalchemy/alchlang/dist');
const original=readFileSync(new URL('../business.alch',import.meta.url),'utf8');
const clone=<T>(value:T):T=>JSON.parse(JSON.stringify(value));
async function fixture(t:TestContext){
 const resolver=await import(pathToFileURL(path.join(alch,'business-authoring-resolve.js')).href),parser=await import(pathToFileURL(path.join(alch,'business-authoring-parser.js')).href),carrier=await import(pathToFileURL(path.join(alch,'business-authoring-carriers.js')).href),lower=await import(pathToFileURL(path.join(alch,'application-domain-lowering.js')).href);
 const business=resolver.resolveBusinessSpecV2(parser.parseBusinessSourceV2(original)),lowered=carrier.lowerDirectBusinessV2(business),formation=lower.lowerDirectApplicationDomainV2(lowered);
 const directory=mkdtempSync(path.join(os.tmpdir(),'craft-l02-'));t.after(()=>rmSync(directory,{recursive:true,force:true}));
 for(const [relative,text]of Object.entries(formation.projectFiles)){const file=path.join(directory,relative);mkdirSync(path.dirname(file),{recursive:true});writeFileSync(file,text as string);}
 const transfer={source:business.source,spec:business.data,executable:lowered.executable,assurance:lowered.assurance};
 const node=(id:string)=>path.join(directory,'specs/dispatching/nodes/'+id+'.json');
 const mutate=(id:string,change:(node:any)=>void)=>{const file=node(id),value=JSON.parse(readFileSync(file,'utf8'));change(value);writeFileSync(file,JSON.stringify(value,null,2)+'\n');};
 const check=()=>checkDirectBusinessSourceGraphV2(compileProject(directory).graph,transfer);
 return {directory,formation,transfer,node,mutate,check};
}
test('L02 genuine six-role source graph uses real field/Rule/Interface/Mapping checkers with zero claims',async t=>{
 const f=await fixture(t),checked=f.check();assertDirectBusinessSourceGraphV2Current(checked);
 assert.equal(checked.kind,'checked-direct-business-source-graph-v2');assert.equal(Object.hasOwn(checked,'input'),false);assert.equal(Object.hasOwn(checked,'accepted'),false);assert.equal(checked.checked.transfer.spec.claims.length,0);
 assert.equal(checked.graph.nodes.length,6);assert.equal(checked.graph.relationships.length,5);assertCompiledProjectFields(checked.fields);
 assert.equal(checked.fields.model.value_profile,'exact-uint64/v1-candidate');assert.equal(checked.rule.root_selector,'dispatching:can-process');
 assert.equal(checked.rule.rule.expression.op,'eq');const property=checked.rule.properties.find((property:{ontology_property:string;type:{kind:string;name?:string}})=>property.ontology_property==='BUSINESS-DISPATCHING-SUBMISSION#verified');assert.ok(property&&property.type.kind==='scalar');assert.equal(property.type.name,'Bool');
 assert.deepEqual(checked.closures.map((row:{role:string;selector:string})=>[row.role,row.selector]),[['Entity','dispatching:submission'],['Rule','dispatching:can-process'],['Operation','dispatching:process'],['Interface','dispatching:process-http'],['Mapping','dispatching:craftrequest-process-http-input'],['Mapping','dispatching:craftrequest-process-http-output']]);
 const rule=checked.closures.find((c:{role:string})=>c.role==='Rule')!;assert.equal(rule.typed_closure_sha256,checked.rule.closure_sha256);assert.equal(checked.closures[0]!.typed_closure_sha256,checked.fields.compilation_sha256);
 assert.ok(rule.origins.some((o:{selector:string;sha256:string})=>o.selector==='line:32'&&o.sha256===f.transfer.source.sha256));
 assert.equal(checked.api.contracts[0]!.contract_id,'payload');assert.equal(checked.api.operations[0]!.operation_ref,'dispatching:process');
 assert.ok(Object.isFrozen(checked));
});
test('L02 pure typed Operation has actual guard arguments and identity result, with no settlement contract',async t=>{
 const f=await fixture(t),checked=f.check(),operation=checked.operation;
 assert.equal(operation.operation_ref,'dispatching:process');assert.deepEqual(clone(operation.input),{name:'request',type:{kind:'named',selector:'dispatching:submission'}});
 assert.deepEqual(clone(operation.guard),{selector:'dispatching:can-process',parameter:'item',value:{op:'path',root:'request',properties:[]}});
 assert.deepEqual(clone(operation.result),{op:'path',root:'request',properties:[]});assert.equal(operation.rejection_code,'delivery-verification-required');assert.equal(operation.effects.length,0);
 for(const key of ['atomicity','continuation','store','transaction','claim_ref','formal','dependency_overrides'])assert.equal(Object.hasOwn(operation,key),false,key);
});
test('L02 semantically wrong but well-typed true/false predicate substitution rejects',async t=>{
 const f=await fixture(t);f.mutate('can-process',node=>{node.body.typed_contract.expression.right.value=false;});
 assert.throws(f.check,/BUSINESS_DIRECT_CONDITION_CORRESPONDENCE/);
});
test('L02 actual selected Rule checker rejects wrong property type rather than trusting structural compile',async t=>{
 const f=await fixture(t);f.mutate('can-process',node=>{node.body.typed_contract.expression.left.properties=['BUSINESS-DISPATCHING-SUBMISSION#id'];});
 assert.throws(f.check,error=>(error as {code?:string}).code==='MTCLI_TYPED_RULE_TYPE');
});
test('L02 actual Rule source metadata and parameter names must retain exact authored meaning',async t=>{
 const f=await fixture(t);f.mutate('can-process',node=>{node.body.description='Different explanation.';});assert.throws(f.check,/BUSINESS_DIRECT_CONDITION_CORRESPONDENCE/);
});
test('L02 Entity metadata and field meaning cannot be replaced under the same source capture',async t=>{
 const f=await fixture(t);f.mutate('submission',node=>{node.body.typed_contract.properties[0].meaning='Different identity meaning.';});assert.throws(f.check,/BUSINESS_DIRECT_CONDITION_CORRESPONDENCE/);
});
test('L02 public Interface provider version and owned payload shape are checked',async t=>{
 const f=await fixture(t);f.mutate('process-http',node=>{node.body.typed_contract.version_policy.provider_version='2.0.0';});assert.throws(f.check,/BUSINESS_DIRECT_CONDITION_CORRESPONDENCE/);
});
test('L02 Mapping inputs and member use are source checked despite matching value types',async t=>{
 const f=await fixture(t);f.mutate('craftrequest-process-http-input',node=>{node.body.typed_contract.inputs[0].name='other';for(const field of node.body.typed_contract.fields)field.value.root='other';});assert.throws(f.check,/BUSINESS_DIRECT_CONDITION_CORRESPONDENCE/);
});
test('L02 result Mapping must retain totality and exact output members',async t=>{
 const f=await fixture(t);f.mutate('craftrequest-process-http-output',node=>{node.body.typed_contract.total=false;});assert.throws(f.check,/BUSINESS_DIRECT_CONDITION_CORRESPONDENCE/);
});
test('L02 Operation rejection and effects remain explicit rather than inferred from metadata',async t=>{
 const f=await fixture(t);f.mutate('process',node=>{node.body.failure_continuation='other-code';});assert.throws(f.check,/BUSINESS_DIRECT_CONDITION_CORRESPONDENCE/);
});
test('L02 source/DTO predicate substitution cannot hide in a plausible graph',async t=>{
 const f=await fixture(t),value=clone(f.transfer);value.spec.rules[0].condition.value.path=['id'];
 assert.throws(()=>checkDirectBusinessSourceGraphV2(compileProject(f.directory).graph,value),/BUSINESS_DIRECT_SOURCE/);
});
test('L02 extra semantically valid nodes are not an accepted prefix of the selected direct cell',async t=>{
 const f=await fixture(t),featureFile=path.join(f.directory,'specs/dispatching/feature.json'),feature=JSON.parse(readFileSync(featureFile,'utf8')),entity=JSON.parse(readFileSync(f.node('submission'),'utf8'));
 entity.node_id='other';entity.body.typed_contract.ontology_node='BUSINESS-DISPATCHING-OTHER';for(const p of entity.body.typed_contract.properties)p.ontology_property='BUSINESS-DISPATCHING-OTHER#'+p.name;
 writeFileSync(f.node('other'),JSON.stringify(entity));feature.nodes.push('other');writeFileSync(featureFile,JSON.stringify(feature));assert.throws(f.check,/BUSINESS_DIRECT_CONDITION_GRAPH_SCOPE/);
});
test('L02 graph and source-graph clones/proxies cannot replace real compiler or private registry custody',async t=>{
 const f=await fixture(t),checked=f.check();
 for(const graph of [clone(checked.graph),{...checked.graph},new Proxy(checked.graph,{})])assert.throws(()=>checkDirectBusinessSourceGraphV2(graph,f.transfer),error=>(error as {code?:string}).code==='MTCLI_COMPILED_SNAPSHOT');
 for(const value of [clone(checked),{...checked},new Proxy(checked,{})])assert.throws(()=>assertDirectBusinessSourceGraphV2Current(value),/BUSINESS_DIRECT_CONDITION_HANDLE/);
 assert.throws(()=>assertCompiledProjectFields(clone(checked.fields)));
});
test('L02 project rewrite and inode replacement retire an original checked source graph',async t=>{
 const f=await fixture(t),checked=f.check(),file=f.node('can-process'),old=readFileSync(file);
 renameSync(file,file+'.before');writeFileSync(file,old);assert.throws(()=>assertDirectBusinessSourceGraphV2Current(checked),/FILE_STALE/);
});
test('L02 symlink replacement cannot supply current project bytes',async t=>{
 const f=await fixture(t),checked=f.check(),file=f.node('can-process');renameSync(file,file+'.before');symlinkSync(file+'.before',file);assert.throws(()=>assertDirectBusinessSourceGraphV2Current(checked),/BUSINESS_DIRECT_CONDITION_FILE/);
});
test('L02 legacy formal condition API still requires a real claim for a selected Rule',async t=>{
 const f=await fixture(t),checked=f.check();assert.throws(()=>compileFormalConditionBindings(checked.graph,{schema_version:'domainspec.formal-condition-bindings/v1-candidate',rules:['dispatching:can-process'],bindings:[],authority_effect:'none'},new Map()),/CONDITION_MISSING/);
});
function owners(){
 let graphReads=0,nativeReads=0;
 const recipes=createBusinessCoreRecipeOwnerV2({assertCurrent(){nativeReads++;throw Error('ACTUAL_NATIVE_BASIS_REQUIRED');},capture(){throw Error('no native fixture');}}),reviews=createBusinessReviewOwnerV2(recipes);
 const generation={generate(){throw Error('actual required');},async importGenerated(){throw Error('actual required');},assertCurrent(){throw Error('actual required');}};
 const native={assertCurrent(){throw Error('actual required');},assertSelectionBasis(){throw Error('actual required');},assets(){throw Error('actual required');}};
 const requests=createBusinessRequestStagesOwnerV2(recipes,generation,native),inputs=createAuthoringBusinessInputOwnerV2(recipes,reviews,requests),application=createBusinessDirectApplicationOwnerV2(inputs,{capture(){graphReads++;throw Error('ORIGINAL_INPUT_REQUIRED');},assertCurrent(){graphReads++;throw Error('ORIGINAL_INPUT_REQUIRED');}});
 return {inputs,application,graphReads:()=>graphReads,nativeReads:()=>nativeReads};
}
test('L02 raw acceptance/early/input/application/condition data cannot mint successor handles',()=>{
 const {inputs,application,graphReads,nativeReads}=owners();let getters=0;
 for(const fake of [{kind:'accepted-business-review-v2'},{kind:'authoring-business-input-v2'},{accepted:true},{get selection(){getters++;throw Error('do not read');}}]){
  assert.throws(()=>inputs.assertCurrent(fake as any),/UNREGISTERED/);assert.throws(()=>inputs.form(fake as any,'dispatching',{} as any,{} as any),/UNREGISTERED/);assert.throws(()=>application.check(fake as any),/UNREGISTERED/);assert.throws(()=>application.assertCurrent(fake as any),/UNREGISTERED/);assert.throws(()=>application.assertConditionCurrent(fake as any),/HANDLE/);
 }
 assert.equal(graphReads(),0);assert.equal(nativeReads(),0);assert.equal(getters,0);
});
