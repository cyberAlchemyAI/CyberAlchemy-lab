import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync,mkdtempSync,mkdirSync,writeFileSync,rmSync} from 'node:fs';
import os from 'node:os';import path from 'node:path';import {pathToFileURL} from 'node:url';
import {parseBusinessSourceV2} from '../src/business-authoring-parser.js';
import {resolveBusinessSpecV2,prepareBusinessSpecFileV2,disposeResolvedBusinessSpecV2} from '../src/business-authoring-resolve.js';
import {lowerDirectBusinessV2,assertLoweredDirectBusinessV2Current} from '../src/business-authoring-carriers.js';
import {deriveDirectBusinessApplicationBindingsV2,assertDerivedDirectBusinessBindingsV2Current} from '../src/business-application-bindings.js';
import {assertDirectBusinessFormationV2Current} from '../src/application-domain-lowering.js';
import {assertDirectRuleSourceProjectionV2Current} from '../src/application-rule-projection.js';
import {deriveDirectBusinessApplicationActionsV2,assertDirectOperationActionsV2Current} from '../src/business-application-actions.js';
import {prepareDirectApplicationExecutableV2,compileDirectApplicationExecutableV2,validateDirectGraphCorrespondenceDataV2,type DirectBusinessCoreSurfaceV2,type DirectGraphCorrespondenceDataV2} from '../src/application-executable.js';
import {prepareVersionedBusinessAuthoringApplication} from '../src/business-authoring-prepare.js';
import {businessCanonical,businessHash} from '../src/business-authoring-model.js';
// Source/typed-role component evidence only. No fabricated accepted Core input or
// successful mock owner is used; actual original joined witness remains G01.
// Open Questions: Core reconstruction/accepted owner and native/installed joins.
const repo=path.resolve(import.meta.dirname,'../../../../../../..'),core=path.join(repo,'craft/projects/domainspec-v2/impl/cli');
const source=readFileSync(path.join(core,'test/profile-engine/fixtures/u0-v2/business.alch'),'utf8');
const resolved=(text=source)=>resolveBusinessSpecV2(parseBusinessSourceV2(text));
const derive=(text=source)=>deriveDirectBusinessApplicationBindingsV2(lowerDirectBusinessV2(resolved(text)));
const plain=<T>(value:T):T=>JSON.parse(JSON.stringify(value));
function writeFiles(root:string,files:Readonly<Record<string,string>>):void {
 for(const [relative,body] of Object.entries(files)){const file=path.join(root,relative);mkdirSync(path.dirname(file),{recursive:true});writeFileSync(file,body);}
}
test('L01 source carrier/project retains a direct nonempty Rule and original physical clauses',()=>{
 const bindings=derive();assertDerivedDirectBusinessBindingsV2Current(bindings);
 assert.deepEqual(bindings.selected_rule_refs,['dispatching:can-process']);
 assert.equal(Object.keys(bindings.formation.projectFiles).length,13);
 assert.equal(bindings.rule.property_selector,'BUSINESS-DISPATCHING-SUBMISSION#verified');
 assert.equal(bindings.rule.source.text,'  condition item.verified');
 assert.equal(bindings.rule.source.source_sha256,bindings.lowered.business.source.sha256);
 assert.deepEqual(plain(bindings.rule.typed_contract.expression),{op:'eq',left:{op:'path',root:'item',properties:['BUSINESS-DISPATCHING-SUBMISSION#verified']},right:{op:'literal',type:'Bool',value:true}});
 for(const key of ['condition','guard','result','rejection','effects','entry','permission'] as const){assert.equal(bindings.formation.origins[key].source_sha256,bindings.lowered.business.source.sha256);assert.ok(bindings.formation.origins[key].line>0);}
 assert.equal(Object.keys(bindings.formation.projectFiles).some(name=>/formal|definition|condition-bindings/.test(name)),false);
});
test('L01 pure action projection preserves parameter mapping, result and authored rejection without settlement ports',()=>{
 const actions=deriveDirectBusinessApplicationActionsV2(derive());assertDirectOperationActionsV2Current(actions);
 assert.deepEqual(plain(actions.plan),{
  operation_ref:'dispatching:process',input:{name:'request',type:{kind:'named',selector:'dispatching:submission'}},output:{kind:'named',selector:'dispatching:submission'},
  guards:[{rule_ref:'dispatching:can-process',arguments:[{parameter:'item',value:{op:'path',root:'request',properties:[]}}]}],
  result:{op:'path',root:'request',properties:[]},rejection:{kind:'authored-guard-rejection',code:'delivery-verification-required'},effects:[],
 });
 for(const forbidden of ['formal','claim_ref','store','atomicity','continuation','dependency_overrides'])assert.equal(Object.hasOwn(actions.plan,forbidden),false);
});
test('L01 Interface owns the public payload and explicit Mapping data closes both directions',()=>{
 const formation=derive().formation,files=formation.projectFiles;
 const node=(id:string)=>JSON.parse(files['specs/dispatching/nodes/'+id+'.json']!).body;
 const api=node('process-http').typed_contract;
 assert.equal(api.schema_version,'domainspec.typed-interface/v1');assert.equal(api.contracts.length,1);
 assert.deepEqual(api.contracts[0].fields.map((field:any)=>field.type),[{kind:'scalar',name:'UInt64'},{kind:'scalar',name:'Bool'}]);
 assert.deepEqual(api.operations[0].request,{kind:'contract',contract_id:'payload'});
 for(const id of ['craftrequest-process-http-input','craftrequest-process-http-output']){
  const mapping=node(id).typed_contract;assert.equal(mapping.schema_version,'domainspec.typed-mapping/v3');assert.equal(mapping.total,true);assert.equal(mapping.fields.length,2);
 }
 assert.equal(node('craftrequest-process-http-input').typed_contract.inputs[0].use.side,'request');
 assert.equal(node('craftrequest-process-http-output').typed_contract.target_use.side,'result');
});
test('L01 actual public Core source compiler accepts the formed project and selects its typed Rule',async t=>{
 const bindings=derive(),root=mkdtempSync(path.join(os.tmpdir(),'alch-l01-source-'));t.after(()=>rmSync(root,{recursive:true,force:true}));writeFiles(root,bindings.formation.projectFiles);
 const api=await import(pathToFileURL(path.join(core,'src/index.ts')).href);
 const compiled=api.compileProject(root);api.validateCompiledProjectCertificate(compiled.graph,compiled.certificate);
 assert.equal(compiled.certificate.node_count,6);assert.equal(compiled.certificate.edge_count,5);
 assert.equal(compiled.graph.nodes.some((node:any)=>node.kind==='FormalClaim'),false);
 const selected=api.loadProjectNode(root,bindings.rule.selector);
 assert.equal(selected.typed_closure.root_selector,bindings.rule.selector);
 const property=selected.typed_closure.properties.find((field:any)=>field.ontology_property===bindings.rule.property_selector);
 assert.equal(property.type.name,'Bool');
 // A real selected Rule closure exists. Other role/native support is not inferred
 // from compileProject or from JSON data correspondence.
 assert.match(selected.typed_closure.closure_sha256,/^[a-f0-9]{64}$/);
});
test('L01 actual selected Core Rule owner rejects broken property/type formation',async t=>{
 const api=await import(pathToFileURL(path.join(core,'src/index.ts')).href),bindings=derive();
 for(const mode of ['missing-property','wrong-type']){
  const root=mkdtempSync(path.join(os.tmpdir(),'alch-l01-control-'));t.after(()=>rmSync(root,{recursive:true,force:true}));writeFiles(root,bindings.formation.projectFiles);
  const file=path.join(root,'specs/dispatching/nodes/submission.json'),node=JSON.parse(readFileSync(file,'utf8'));
  if(mode==='missing-property'){
   node.body.typed_contract.properties[1].ontology_property='BUSINESS-DISPATCHING-SUBMISSION#missing';
   // Keep the independent Mapping valid so the selected Rule is the causal failure.
   const outputFile=path.join(root,'specs/dispatching/nodes/craftrequest-process-http-output.json'),output=JSON.parse(readFileSync(outputFile,'utf8'));
   output.body.typed_contract.fields[1].value.properties=['BUSINESS-DISPATCHING-SUBMISSION#missing'];writeFileSync(outputFile,JSON.stringify(output));
  }else{
   node.body.typed_contract.properties[1].type={kind:'scalar',name:'String'};
   const publicFile=path.join(root,'specs/dispatching/nodes/process-http.json'),boundary=JSON.parse(readFileSync(publicFile,'utf8'));
   boundary.body.typed_contract.contracts[0].fields[1].type={kind:'scalar',name:'String'};writeFileSync(publicFile,JSON.stringify(boundary));
  }
  writeFileSync(file,JSON.stringify(node));
  assert.throws(()=>api.loadProjectNode(root,bindings.rule.selector),e=>(e as any).code=== (mode==='missing-property'?'MTCLI_TYPED_CLOSURE_PROPERTY':'MTCLI_TYPED_RULE_TYPE'));
 }
});
test('L01 metadata correspondence checks selectors/condition/origins without granting graph custody',()=>{
 const bindings=derive(),f=bindings.formation,sourceHash=bindings.lowered.business.source.sha256;
 // Candidate metadata uses measured source-artifact digests, not future owner
 // handles. Passing this pure check cannot satisfy Core input/application custody.
 const closures=Object.entries(f.selectors).map(([name,selector])=>{
  const id=selector.split(':')[1]!,file=f.projectFiles['specs/dispatching/nodes/'+id+'.json']!;
  const role=name==='entity'?'Entity':name==='rule'?'Rule':name==='operation'?'Operation':name==='entry'?'Interface':'Mapping';
  return {role,selector,typed_closure_sha256:businessHash(file),origins:[{source:bindings.rule.source.source,selector:bindings.rule.source.selector,sha256:sourceHash}]};
 });
 const data:DirectGraphCorrespondenceDataV2={operation_ref:f.selectors.operation,plan_sha256:deriveDirectBusinessApplicationActionsV2(bindings).actions_sha256,graph:{graph_sha256:f.formation_sha256,closures:closures as DirectGraphCorrespondenceDataV2['graph']['closures']},condition:{rule_ref:bindings.rule.selector,entity_ref:bindings.rule.entity_selector,parameter:bindings.rule.parameter,field_name:bindings.rule.field_name,property_selector:bindings.rule.property_selector,condition_sha256:bindings.rule.projection_sha256}};
 assert.doesNotThrow(()=>validateDirectGraphCorrespondenceDataV2(bindings,data));
 for(const mutate of [
  (v:any)=>{v.condition.property_selector='BUSINESS-DISPATCHING-SUBMISSION#id';},
  (v:any)=>{v.condition.parameter='other';},(v:any)=>{v.operation_ref='dispatching:other';},
  (v:any)=>{v.graph.closures=v.graph.closures.filter((row:any)=>row.role!=='Rule');},
  (v:any)=>{v.graph.closures[1].origins=[];},(v:any)=>{v.graph.closures[1].selector='dispatching:other';},
 ]){const changed=plain(data);mutate(changed);assert.throws(()=>validateDirectGraphCorrespondenceDataV2(bindings,changed),/BUSINESS_DIRECT_CORE_JOIN/);}
 assert.throws(()=>compileDirectApplicationExecutableV2(data as any),/original direct executable preparation/);
});
test('L01 preparation and v2-first dispatch reject fake acceptance before any Core graph action',()=>{
 const business=resolved(),bindings=deriveDirectBusinessApplicationBindingsV2(lowerDirectBusinessV2(business)),actions=deriveDirectBusinessApplicationActionsV2(bindings);let checks=0;
 const core:DirectBusinessCoreSurfaceV2={input:{form(){throw Error('not a fixture producer');},assertCurrent(){throw Error('CORE_INPUT_ORIGINAL_REQUIRED');}},application:{check(){checks++;throw Error('must not compile a forged input');},assertCurrent(){throw Error('no fixture graph');},assertConditionCurrent(){throw Error('no fixture condition');}}};
 for(const fake of [{accepted:true},JSON.parse(JSON.stringify(business))])assert.throws(()=>prepareDirectApplicationExecutableV2(bindings,actions,fake as any,core),/CORE_INPUT_ORIGINAL_REQUIRED/);
 assert.throws(()=>prepareVersionedBusinessAuthoringApplication({source_contract:'alchlang.business-spec/v2-candidate',business,input:{accepted:true} as any,core}),/CORE_INPUT_ORIGINAL_REQUIRED/);
 assert.equal(checks,0);assert.throws(()=>prepareVersionedBusinessAuthoringApplication({source_contract:'unknown'} as any),/BUSINESS_SOURCE_VERSION/);
});
test('L01 field/guard/return/rejection/access source changes cannot be replaced by stale projection data',()=>{
 const base=derive(),changed=derive(source.replaceAll('CanProcess','MayProcess'));
 assert.notEqual(changed.bindings_sha256,base.bindings_sha256);assert.notEqual(changed.rule.projection_sha256,base.rule.projection_sha256);
 const rejected=derive(source.replace('on-rejection delivery-verification-required','on-rejection another-code'));
 assert.notEqual(deriveDirectBusinessApplicationActionsV2(base).actions_sha256,deriveDirectBusinessApplicationActionsV2(rejected).actions_sha256);
 for(const text of [source.replace('  requires CanProcess(item: request)\n',''),source.replace('returns request','returns missing'),source.replace('permission public','permission protected')])assert.throws(()=>derive(text));
 assert.notEqual(businessCanonical(changed.rule.typed_contract),businessCanonical(base.rule.typed_contract));
});
test('L01 source-derived handles reject clone/proxy data and disposed or physically changed sources',()=>{
 const bindings=derive(),actions=deriveDirectBusinessApplicationActionsV2(bindings);
 for(const [value,assertCurrent] of [[bindings.lowered,assertLoweredDirectBusinessV2Current],[bindings.formation,assertDirectBusinessFormationV2Current],[bindings.rule,assertDirectRuleSourceProjectionV2Current],[bindings,assertDerivedDirectBusinessBindingsV2Current],[actions,assertDirectOperationActionsV2Current]] as const){
  for(const forged of [plain(value),{...value},new Proxy(value,{})])assert.throws(()=>(assertCurrent as (v:any)=>void)(forged),/BUSINESS_HANDLE/);
 }
 disposeResolvedBusinessSpecV2(bindings.lowered.business);assert.throws(()=>assertDirectOperationActionsV2Current(actions),/BUSINESS_DISPOSED/);
 const root=mkdtempSync(path.join(os.tmpdir(),'alch-l01-current-'));
 try{const file=path.join(root,'business.alch');writeFileSync(file,source);const current=deriveDirectBusinessApplicationBindingsV2(lowerDirectBusinessV2(prepareBusinessSpecFileV2(root,'business.alch')));writeFileSync(file,source+'# recaptured\n');assert.throws(()=>assertDerivedDirectBusinessBindingsV2Current(current),/BUSINESS_SOURCE_DRIFT/);}finally{rmSync(root,{recursive:true,force:true});}
});
