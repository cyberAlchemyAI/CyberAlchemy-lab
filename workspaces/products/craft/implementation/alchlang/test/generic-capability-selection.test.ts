/** Focused source/CLI formation checks. Open Questions: ../examples/generic-capabilities/README.md. */
import assert from 'node:assert/strict';
import {spawnSync} from 'node:child_process';
import {cpSync,existsSync,mkdtempSync,readFileSync,readdirSync,rmSync,writeFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {tmpdir} from 'node:os';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import test from 'node:test';
import {parseGenericBusinessSource,lowerGenericCapabilitySelectors} from '../src/generic-business-source.js';
import {parseCommerceModuleSource} from '../src/commerce-source-parser.js';
import {dataDigest} from '../../../../../../../craft/projects/domainspec-v2/impl/cli/src/profile-engine/contracts.js';

const frontend=fileURLToPath(new URL('..',import.meta.url));
const repository=path.resolve(frontend,'../../../../../..');
const example=path.join(frontend,'examples/generic-capabilities');
const cli=path.join(frontend,'src/generic-composition-cli.ts');
const core=path.join(repository,'craft/projects/domainspec-v2/impl/cli');
const sha=(bytes:string|Buffer)=>createHash('sha256').update(bytes).digest('hex');
const text=readFileSync(path.join(example,'business.alch'),'utf8');
const selection=()=>JSON.parse(readFileSync(path.join(example,'selection.json'),'utf8'));
const parsed=()=>parseGenericBusinessSource(text,'business.alch',true,true);
function run(args:string[]){
 return spawnSync(process.execPath,['--import','tsx',cli,...args],{cwd:frontend,env:{...process.env,ALCHLANG_DOMAINSPEC_PACKAGE_ROOT:core},encoding:'utf8',timeout:120000,maxBuffer:8*1024*1024});
}
function workingFixture(){const root=mkdtempSync(path.join(tmpdir(),'alch-capability-'));cpSync(example,root,{recursive:true});return root;}
const flags=(root:string)=>['--source',path.join(root,'business.alch'),'--profile',path.join(root,'profile.json'),'--capability-selection',path.join(root,'selection.json')];

test('C01 preliminary binding ceiling agrees with the canonical data contract',()=>{
 const maximum=JSON.parse(readFileSync(path.join(core,'contracts/generic-capability-v1.schema.json'),'utf8')).$defs.GenericCapabilitySelection.properties.bindings.maxItems;
 const modules=Array.from({length:maximum+1},(_,i)=>parseGenericBusinessSource(text.replace('module Example version',`module Example${i} version`),`example${i}.alch`,true,true));
 const s=selection(),binding=s.bindings[0];
 s.bindings=modules.slice(0,maximum).map((m,i)=>({...binding,id:`Example${i}.Selection`,interface:m.module+'.Model',contract:{...binding.contract,input_type:m.module+'.Request',result_type:m.module+'.Reply'}}));
 assert.equal(lowerGenericCapabilitySelectors(modules,s,'selection.json').length,maximum);
 s.bindings.push({...binding,id:'BeyondLimit'});
 assert.throws(()=>lowerGenericCapabilitySelectors(modules,s,'selection.json'),/bounded capability-selection/);
});

test('C01 existing bounded-schema syntax lowers neutral selectors with source spans',()=>{
 const lowered=lowerGenericCapabilitySelectors([parsed()],selection(),'selection.json');
 assert.equal(lowered.length,1);assert.equal(lowered[0]!.interface,'Example.Model');
 assert.equal(lowered[0]!.input_type,'Example.Request');assert.equal(lowered[0]!.result_type,'Example.Reply');
 assert.equal(lowered[0]!.realization_ref,'Example.Native');assert.deepEqual(lowered[0]!.tools,[]);
 assert.equal(text.slice(lowered[0]!.source_span.start,lowered[0]!.source_span.start+9),'interface');
 assert.ok(Object.isFrozen(lowered));assert.equal(parsed().declarations.some(d=>d.kind==='FormalClaim'),false);
});

test('C01 neutral inference, document, search and optional agent selectors reuse the same Interface',()=>{
 for(const [kind,operation] of [['inference/v1','text.structured'],['document/v1','document.parse'],['search/v1','search.query'],['agent-run/v1','agent.run']]){
  const s=selection();s.bindings[0].contract={...s.bindings[0].contract,kind,operation,...(kind==='agent-run/v1'?{tools:[],loop_owner:'selected-harness',checkpoint_version:'1'}:{})};
  const normalized=lowerGenericCapabilitySelectors([parsed()],s,'selection.json');
  assert.equal(normalized[0]!.contract,kind);assert.equal(normalized[0]!.operation,operation);assert.deepEqual(normalized[0]!.tools,[]);
 }
});

test('C01 optional tool selectors transport existing scalar/Optional codecs without a second type compiler',()=>{
 const http=readFileSync(path.join(frontend,'examples/generic-http/business.alch'),'utf8')+'\ninterface Model:\n  kind bounded-schema\n  exposes Request, Decision\n';
 const module=parseCommerceModuleSource(http,'business.alch'),s=selection();
 const tool={name:'Read',entry:'ReviewDesk.ReadStoredRequestEntry',query:'ReviewDesk.ReadStoredRequest',argument_codec:{kind:'scalar',name:'UInt64'},result_codec:{kind:'optional',element:{kind:'record',name:'ReviewDesk.StoredRequest'}},effect:'read-only'};
 s.bindings[0].interface='ReviewDesk.Model';s.bindings[0].contract={kind:'agent-run/v1',operation:'agent.run',input_type:'ReviewDesk.Request',result_type:'ReviewDesk.Decision',required_capabilities:['readonly-tools'],loop_owner:'selected-harness',tools:[tool],checkpoint_version:'1'};
 const normalized=lowerGenericCapabilitySelectors([module],s,'selection.json');
 assert.deepEqual(normalized[0]!.tools[0]!.argument_codec,tool.argument_codec);assert.deepEqual(normalized[0]!.tools[0]!.result_codec,tool.result_codec);
 const bad=structuredClone(s);bad.bindings[0].contract.tools[0].query='ReviewDesk.CommitRequestApproval';
 assert.throws(()=>lowerGenericCapabilitySelectors([module],bad,'selection.json'),/existing Entry and Query selectors/);
 const absent=structuredClone(s);absent.bindings[0].contract.tools[0].query='ReviewDesk.Missing';
 assert.throws(()=>lowerGenericCapabilitySelectors([module],absent,'selection.json'),/missing capability selector ReviewDesk.Missing/);
});

test('C01 missing, ambiguous and mismatched selectors retain actionable source diagnostics',async t=>{
 for(const [name,mutate,pattern] of [
  ['missing Interface',(s:any)=>s.bindings[0].interface='Example.Missing',/missing capability selector Example.Missing/],
  ['unqualified Interface',(s:any)=>s.bindings[0].interface='Model',/fully qualified/],
  ['duplicate binding',(s:any)=>s.bindings.push(structuredClone(s.bindings[0])),/ambiguous capability bindings/],
  ['missing value',(s:any)=>s.bindings[0].contract.input_type='Example.Absent',/missing capability selector Example.Absent/],
  ['non-value reference',(s:any)=>s.bindings[0].contract.result_type='Example.Answer',/fully qualified exposed business value/],
 ] as const)await t.test(name,()=>{
  const s=selection();mutate(s);
  assert.throws(()=>lowerGenericCapabilitySelectors([parsed()],s,'selection.json'),(error:any)=>{assert.match(error.message,pattern);assert.equal(error.diagnostics.length,1);assert.ok(['business.alch','selection.json'].includes(error.diagnostics[0].path));return true;});
 });
 await t.test('ambiguous module-local Interface',()=>{
  const other=parseCommerceModuleSource(text.replace('module Example version','module Other version'),'other.alch');
  const s=selection();s.bindings[0].interface='Model';
  assert.throws(()=>lowerGenericCapabilitySelectors([parsed(),other],s,'selection.json'),/ambiguous capability selector Model/);
 });
 await t.test('value exists but Interface does not expose it',()=>{
  const module=parseGenericBusinessSource(text.replace('exposes Request, Reply','exposes Request'),'business.alch',true,true);
  assert.throws(()=>lowerGenericCapabilitySelectors([module],selection(),'selection.json'),/fully qualified exposed business value/);
 });
});

test('C01 real CLI inspection and generation preserve checked formation and executable lineage',async()=>{
 const root=workingFixture();try{
  const inspected=run(['inspect',...flags(root)]);assert.equal(inspected.status,0,inspected.stderr);
  const inspection=JSON.parse(inspected.stdout),checked=inspection.capability_bindings;
  assert.equal(checked.schema_version,'craft.checked-capability-bindings/v1');assert.match(checked.qualification,/formation-only/);
  assert.equal(checked.selection_sha256,sha(readFileSync(path.join(root,'selection.json'))));
  assert.equal(checked.source_sha256,sha(text));assert.equal(checked.bindings[0].interface,'Example.Model');
  assert.equal(checked.bindings[0].realization.implementation.package,'@craft/fixture');
  assert.equal(checked.selection.bindings.some((b:any)=>b.contract.kind==='agent-run/v1'),false);
  const output=path.join(root,'generated'),result=run(['generate',...flags(root),'--operation','Example.Answer','--out',output,'--accept-local-review','local-c01']);
  assert.equal(result.status,0,result.stderr);
  const manifest=JSON.parse(result.stdout),formation=JSON.parse(readFileSync(path.join(output,'capability-bindings.json'),'utf8'));
  assert.equal(formation.selection_sha256,checked.selection_sha256);assert.equal(formation.source_sha256,checked.source_sha256);
  assert.equal(manifest.capability_bindings.selection_sha256,checked.selection_sha256);
  const system=JSON.parse(readFileSync(path.join(output,'system-graph.json'),'utf8')),bridge=JSON.parse(readFileSync(path.join(output,'business-system-bridge.json'),'utf8'));
  const capabilityNode=system.nodes.find((n:any)=>n.id==='capability:Example.Selection');
  assert.equal(capabilityNode.realization_sha256,formation.bindings[0].realization_sha256);
  const lineage={integration_binding_ref:'Example.Binding',provider_realization_ref:'Example.Resource',provider_profile_ref:'Example.Provider',resource_ref:'Example.RuntimeResource',adapter_ref:'Example.Native'};
  assert.deepEqual(formation.bindings[0].provider_lineage,lineage);assert.deepEqual(capabilityNode.provider_lineage,lineage);
  const capabilityLink=bridge.links.find((l:any)=>l.business==='Example.Model');
  assert.equal(capabilityLink.source_capture_sha256,formation.source_capture_sha256);assert.equal(capabilityLink.profile,formation.profile_sha256);
  assert.equal(capabilityLink.selection_sha256,formation.selection_sha256);assert.equal(capabilityLink.kernel_sha256,formation.kernel_sha256);
  assert.deepEqual(capabilityLink.provider_lineage,lineage);assert.equal(capabilityLink.contract_sha256,formation.bindings[0].contract_sha256);
  for(const file of readdirSync(output).filter(f=>f.endsWith('.mjs')))assert.doesNotMatch(readFileSync(path.join(output,file),'utf8'),/agent-reasoning|@.*are\//);
  const generated=await import(pathToFileURL(path.join(output,'operation.mjs')).href);
  const evaluated=await generated.evaluate(new TextEncoder().encode(JSON.stringify({request:{verified:true}})));
  assert.equal(evaluated.ok,true,JSON.stringify(evaluated));
  assert.deepEqual(JSON.parse(new TextDecoder().decode(evaluated.wire)),{tag:'Returned',fields:{value:{accepted:true}}});
 }finally{rmSync(root,{recursive:true,force:true});}
});

test('C01 real CLI rejects mismatched original source, realization and unresolved native calls',async t=>{
 for(const [name,mutate,pattern] of [
  ['wrong source digest',(root:string,s:any)=>s.source_sha256='0'.repeat(64),/StaleOwner|exact primary source/],
  ['wrong profile digest',(root:string,s:any)=>s.profile_sha256='0'.repeat(64),/StaleOwner|selected profile/],
  ['wrong realization reference',(root:string,s:any)=>s.bindings[0].realization_ref='Example.Absent',/CAPABILITY_REFERENCE|realization/],
  ['missing Interface selector',(root:string,s:any)=>s.bindings[0].interface='Example.Missing',/missing capability selector/],
  ['unresolved native call',(root:string,s:any)=>{const altered=text.replace('return Echo(request)','return MissingNative(request)');writeFileSync(path.join(root,'business.alch'),altered);s.source_sha256=sha(altered);},/UnknownReference|MissingNative|unknown|absent/],
 ] as const)await t.test(name,()=>{
  const root=workingFixture();try{const s=selection();mutate(root,s);writeFileSync(path.join(root,'selection.json'),JSON.stringify(s)+'\n');const result=run(['inspect',...flags(root)]);assert.notEqual(result.status,0,result.stdout);assert.match(result.stderr,pattern);assert.equal(readdirSync(root).includes('generated'),false);}finally{rmSync(root,{recursive:true,force:true});}
 });
});

test('C01 existing protected HTTP example generates with no selection or agent dependency',()=>{
 const root=mkdtempSync(path.join(tmpdir(),'alch-http-regression-'));try{
  const source=path.join(frontend,'examples/generic-http/business.alch'),profile=path.join(frontend,'examples/generic-http/contracts/http-profile.json');
  const output=path.join(root,'generated'),result=run(['generate','--source',source,'--profile',profile,'--entry','ReviewDesk.CommitRequestApprovalEntry','--out',output,'--accept-local-review','local-c01-regression']);
  assert.equal(result.status,0,result.stderr);const manifest=JSON.parse(result.stdout);
  assert.equal(manifest.capability_bindings,undefined);assert.equal(readdirSync(output).includes('capability-bindings.json'),false);
  assert.match(readFileSync(path.join(output,'business-system-bridge.json'),'utf8'),/ReviewDesk.CommitRequestApprovalEntry/);
  assert.doesNotMatch(readFileSync(path.join(output,'application.mjs'),'utf8'),/agent-reasoning|@.*are\//);
 }finally{rmSync(root,{recursive:true,force:true});}
});

test('C01 capability handoff preserves protected HTTP permissions and checks the selected strict model boundary',()=>{
 const root=mkdtempSync(path.join(tmpdir(),'alch-http-capability-'));try{
  cpSync(path.join(frontend,'examples/generic-http'),root,{recursive:true});
  const source=path.join(root,'business.alch'),profile=path.join(root,'contracts/selected-profile.json');
  const business=readFileSync(source,'utf8')+'\nvalue-object NativeRequest:\n  requestId UInt64\n  verified Bool\n\nvalue-object NativeReply:\n  requestId UInt64\n  accepted Bool\n\ninterface Model:\n  kind bounded-schema\n  exposes Request, Decision, NativeRequest, NativeReply\n';writeFileSync(source,business);
  const s=selection(),kernel=JSON.parse(readFileSync(path.join(example,'kernel.json'),'utf8'));
  s.source_sha256=sha(business);s.profile_sha256=sha(readFileSync(profile));
  s.bindings[0].interface='ReviewDesk.Model';s.bindings[0].contract.input_type='ReviewDesk.Request';s.bindings[0].contract.result_type='ReviewDesk.Decision';
  kernel.integration_bindings[0].logical_boundary_ref='ReviewDesk.Model';s.kernel.sha256=dataDigest(kernel);
  writeFileSync(path.join(root,'kernel.json'),JSON.stringify(kernel)+'\n');writeFileSync(path.join(root,'selection.json'),JSON.stringify(s)+'\n');
  const output=path.join(root,'generated'),args=['generate','--source',source,'--profile',path.join(root,'contracts/http-profile.json'),'--capability-selection',path.join(root,'selection.json'),'--entry','ReviewDesk.CommitRequestApprovalEntry','--out',output,'--accept-local-review','local-c01-http'];
  // C01 admitted the rich shape for formation; C03 must refuse it for strict
  // native schema emission rather than discard the application's invariants.
  const unsupportedOutput=path.join(root,'unsupported-generated'),unsupportedArgs=[...args];unsupportedArgs[unsupportedArgs.indexOf('--out')+1]=unsupportedOutput;
  const unsupported=run(unsupportedArgs);assert.notEqual(unsupported.status,0);assert.match(unsupported.stderr,/UnsupportedCapability.*invariants/);assert.equal(existsSync(unsupportedOutput),false);
  s.bindings[0].contract.input_type='ReviewDesk.NativeRequest';s.bindings[0].contract.result_type='ReviewDesk.NativeReply';
  writeFileSync(path.join(root,'selection.json'),JSON.stringify(s)+'\n');
  const result=run(args);assert.equal(result.status,0,result.stderr);
  const manifest=JSON.parse(result.stdout),formed=JSON.parse(readFileSync(path.join(output,'capability-bindings.json'),'utf8'));
  assert.equal(formed.source_sha256,s.source_sha256);assert.equal(formed.profile_sha256,s.profile_sha256);
  assert.equal(manifest.capability_bindings.selection_sha256,formed.selection_sha256);
  assert.match(readFileSync(path.join(output,'business-system-bridge.json'),'utf8'),/ReviewDesk.Model/);
  const graph=JSON.parse(readFileSync(path.join(output,'system-graph.json'),'utf8'));
  assert.ok(graph.nodes.some((n:any)=>n.kind==='auth-foundation-ready'));
  assert.equal(formed.bindings[0].contract.kind,'inference/v1');
  assert.match(formed.qualification,/native-adapter-and-provider-execution-unrun/);
 }finally{rmSync(root,{recursive:true,force:true});}
});
