/** Actual Core technical model,source Mapping and family components.
 * Open Questions: docs/COMMERCE-PROFILE-FAMILY-V5.md#open-questions. */
import test,{before,after} from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync,mkdtempSync,cpSync,rmSync,renameSync} from 'node:fs';
import path from 'node:path';
import {tmpdir} from 'node:os';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
import {createCommerceTechnicalModelOwnerV5} from '../../src/profile-engine/technical-model-v5.js';
import {createCommerceFamilyOwnerV5} from '../../src/profile-engine/family-v5.js';
import {createDerivedProfileCheckerV5} from '../../src/profile-engine/loader-v5.js';
import {nativeRequirementV5,resolvedNativeAssetDataV5,resolvedDependencyDataV5,validateProfilePackageV5,familyLoweringPolicyV5,exactVersionV5} from '../../src/profile-engine/contracts-v5.js';
const root=fileURLToPath(new URL('../../../../../../../examples/ecommerce-target-candidate/',import.meta.url)).replace(/\/$/,''),policy=JSON.parse(readFileSync(new URL('../../profiles/commerce-local-v1-candidate/technical-contract.json',import.meta.url),'utf8')),params={tablePrefix:'shop_',requestBytes:4096,responseBytes:131072,bodyTimeoutMs:2000} as const,scope={kind:'pure-pricing',targets:[{module:'Orders',role:'Calculation',name:'PayableTotal'}],omitted_capabilities:'unsupported-not-silently-executed'} as const;
let models:ReturnType<typeof createCommerceTechnicalModelOwnerV5>,families:ReturnType<typeof createCommerceFamilyOwnerV5>,model:any,base:any,variant:any,directory:string;
before(async()=>{directory=mkdtempSync(path.join(tmpdir(),'commerce-profile-family-'));models=createCommerceTechnicalModelOwnerV5();families=createCommerceFamilyOwnerV5(models);model=await families.checkTechnicalSource(root,'profiles/implementation.alch');base=families.derive(model,params,scope);variant=families.derive(model,{...params,tablePrefix:'sample_'},scope);});
after(()=>{if(directory)rmSync(directory,{recursive:true,force:true});});
const clone=<T>(v:T):T=>JSON.parse(JSON.stringify(v));
function descriptor(){const d=families.inspect(base).descriptor;return {...d,resolved_dependencies:d.obligations.map((o,i)=>({dependency_id:'source-primitive-'+i,origin:'produced-artifact' as const,version_comparison:'exact' as const,version_operand:'1.0.0',actual_version:'1.0.0',semantic_abi:o.abi,artifact:{path:'native/primitive-'+i+'.js',sha256:'a'.repeat(64),bytes:123},closure_sha256:'b'.repeat(64),exports:o.required_exports,platform:'linux',architecture:'x64'}))};}
test('actual typed technical graph retains original meta-types,source spans and imported definitions',()=>{
 const m=models.inspect(model);assert.equal(m.source.module,'Shop.Implementation');assert.equal(m.mapping,'Shop.Implementation.SelectShopImplementation');assert.equal(m.graph.technical_nodes.length,14);assert.ok(m.graph.nodes.some(n=>n.id==='Shop.Implementation.TablePrefix'&&n.selector.role==='ValueObject'));assert.ok(m.graph.nodes.some(n=>n.id==='Shop.Implementation.ProfileFamilyLowering'&&n.selector.role==='Interface'));assert.ok(m.graph.imports.includes('Shop.Values.Identifier'));for(const n of m.graph.nodes){assert.equal(typeof n.meta_type_id,'string');assert.equal(n.span.path,n.source.artifact.path);assert.ok(Object.isFrozen(n.definition));}assert.match(m.qualification,/not-selected/);
});
test('real compiled source Mapping determines family selection and parameter propagation',()=>{
 const m=models.inspect(model),out=models.evaluateSelection(model,params);assert.equal(out.values,'BoundedValues');assert.equal(out.computation,'PureComputation');assert.equal(out.tablePrefix,'shop_');assert.equal(out.requestBytes,'4096');assert.match(m.compiled_mapping.source,/export function evaluate/);assert.doesNotMatch(m.compiled_mapping.source,/evaluateComputation\(/);
});
test('pure scope derives only its two required primitive families',()=>{
 const f=families.inspect(base);assert.deepEqual(f.descriptor.families,['BoundedValues','PureComputation']);assert.deepEqual(f.native_requirements.map(r=>r.primitive_id),['bounded-values','pure-computation']);assert.ok(f.native_requirements.every(r=>!Object.hasOwn(r,'sha256')&&!Object.hasOwn(r,'version')));assert.equal(Object.hasOwn(f.descriptor,'resolved_dependencies'),false);
});
test('same model/compiler accepts declared profile parameter variant with distinct derived identity',()=>{
 const a=families.inspect(base),b=families.inspect(variant);assert.equal(a.graph_sha256,b.graph_sha256);assert.equal(a.source_capture_sha256,b.source_capture_sha256);assert.notEqual(a.family_sha256,b.family_sha256);assert.equal(b.mapping_result.tablePrefix,'sample_');assert.deepEqual(a.descriptor.families,b.descriptor.families);
});
test('invalid bounds and identifier data fail before family derivation',()=>{
 for(const p of [{...params,tablePrefix:'bad-name'},{...params,tablePrefix:'x'.repeat(17)},{...params,requestBytes:4097},{...params,bodyTimeoutMs:'2000'},{...params,callback:'run'}])assert.throws(()=>families.derive(model,p as any,scope));
});
test('scope rejects unknown or effectful pure targets and duplicate selectors',()=>{
 for(const s of [{...scope,targets:[{module:'Orders',role:'Calculation',name:'Missing'}]},{...scope,targets:[{module:'Orders',role:'Operation',name:'PlaceOrder'}]},{...scope,targets:[...scope.targets,...scope.targets]},{...scope,kind:'arbitrary-http'}])assert.throws(()=>families.derive(model,params,s as any));
});
test('full application selection keeps unbuilt native obligations as requirements',()=>{
 const f=families.derive(model,params,{...scope,kind:'application'}),v=families.inspect(f);assert.equal(v.descriptor.families.length,10);assert.equal(v.native_requirements.length,10);assert.ok(v.native_requirements.some(r=>r.primitive_id==='service-sqlite'));assert.ok(v.native_requirements.some(r=>r.primitive_id==='identity-context'));assert.match(v.qualification,/requirements-only/);assert.throws(()=>validateProfilePackageV5(v.descriptor));
});
test('each effectful scope retains its closed selected slots and identity requirement',()=>{
 const expected={
  'local-effects':['bounded-values','pure-computation','service-sqlite','identity-context'],
  'protected-entry':['bounded-values','pure-computation','injected-http-entry','auth-ready-bridge','identity-context'],
  'remote-effects':['bounded-values','pure-computation','demo-pay-v1','identity-context'],
  coordination:['bounded-values','pure-computation','service-sqlite','event-inbox-outbox','durable-workflow','identity-context'],
 } as const;
 for(const [kind,primitives]of Object.entries(expected)){const f=families.derive(model,params,{...scope,kind} as any);assert.deepEqual(families.inspect(f).native_requirements.map(r=>r.primitive_id),primitives);}
});
test('custom scope policy cannot smuggle an effectful native requirement into pure scope',async()=>{
 const altered=clone(policy);altered.scope_rules.find((r:any)=>r.kind==='pure-pricing').additional_primitives=['service-sqlite'];const file=path.join(directory,'effectful-pure-policy.json');writeFileSync(file,JSON.stringify(altered));const m=createCommerceTechnicalModelOwnerV5(file),f=createCommerceFamilyOwnerV5(m),h=await f.checkTechnicalSource(root,'profiles/implementation.alch');assert.throws(()=>f.derive(h,params,scope),/pure realization scope/);m.dispose(h);
});
test('source-derived handles cannot be cloned,mixed or supplied as graph JSON',()=>{
 for(const fake of [{...model},{graph:models.inspect(model).graph},new Proxy(model,{})])assert.throws(()=>families.derive(fake as any,params,scope));assert.throws(()=>createCommerceFamilyOwnerV5({...models}));const other=createCommerceFamilyOwnerV5(models);assert.throws(()=>other.inspect(base));assert.throws(()=>families.inspect({...base}));
});
test('requirement data never accepts invented resolved artifact or version fields',()=>{
 const req=families.inspect(base).native_requirements[0]!;assert.equal(nativeRequirementV5(req).kind,'native-requirement');for(const x of [{...req,sha256:'a'.repeat(64)},{...req,version:'1.0.0'},{...req,primitive_id:'unimplemented-custom-transport'}])assert.throws(()=>nativeRequirementV5(x));
});
test('closed resolved-asset descriptor requires exact ABI,exports,version and concrete data',()=>{
 const req=families.inspect(base).native_requirements[0]!,dep=descriptor().resolved_dependencies[0]!,data={kind:'resolved-native-asset',requirement:req,dependency:dep,authority_effect:'none'};assert.equal(resolvedNativeAssetDataV5(data).kind,'resolved-native-asset');
 for(const d of [{...dep,version_operand:'^1.0.0'},{...dep,actual_version:'1.0.1'},{...dep,semantic_abi:'invented'},{...dep,exports:[]},{...dep,artifact:{...dep.artifact,sha256:'0'.repeat(64)}}])assert.throws(()=>resolvedNativeAssetDataV5({...data,dependency:d}));
});
test('exact versions reject aliases,ranges,flags and noncanonical numeric prereleases',()=>{
 for(const v of ['1.0.0','1.0.0-candidate.0','0.0.0','26.8.1+build.01'])exactVersionV5(v);for(const v of ['latest','locked','^1.0.0','1.x','01.0.0','1.0.0-01','1.0.0 || 2.0.0','>=1.0.0'])assert.throws(()=>exactVersionV5(v));
});
test('derived descriptor checking is exact data correspondence and grants no native availability',()=>{
 const checker=createDerivedProfileCheckerV5(families),d=descriptor(),h=checker.checkDescriptorData(base,d),v=checker.inspect(h);assert.equal(v.native_resolution_verified,false);assert.match(v.qualification,/descriptor-data-only/);assert.equal(validateProfilePackageV5(d).schema_version,'craft.profile-package/v5-candidate');assert.throws(()=>checker.inspect({...h}));assert.throws(()=>checker.checkDescriptorData(variant,d));assert.throws(()=>checker.checkDescriptorData(base,{...d,resolved_dependencies:[]}));
});
test('v4 relabels,extra hooks,unresolved and incompatible descriptor dependencies reject',()=>{
 const d=descriptor();for(const x of [{...d,schema_version:'craft.profile-package/v4-candidate'},{...d,callback:'code'},{...d,resolved_dependencies:[]},{...d,resolved_dependencies:[d.resolved_dependencies[0]]},{...d,resolved_dependencies:d.resolved_dependencies.map(r=>({...r,version_comparison:'compatible'}))}])assert.throws(()=>validateProfilePackageV5(x));
});
test('family policy is closed data and rejects unknown native primitives or callbacks',()=>{
 assert.equal(familyLoweringPolicyV5(policy).slots.length,10);const wrong=clone(policy);wrong.slots[0].primitive='custom-sql-eval';assert.throws(()=>familyLoweringPolicyV5(wrong));assert.throws(()=>familyLoweringPolicyV5({...policy,hook:'sql'}));let touched=0;const p=Object.defineProperty({...params},'tablePrefix',{get(){touched++;return 'shop_';},enumerable:true});assert.throws(()=>families.derive(model,p,scope));assert.equal(touched,0);
});
test('physically captured descriptor data detects same-byte replacement',()=>{
 const checker=createDerivedProfileCheckerV5(families),file=path.join(directory,'profile.json');writeFileSync(file,JSON.stringify(descriptor()));const h=checker.readDescriptorData(base,file);writeFileSync(file+'.new',readFileSync(file));renameSync(file+'.new',file);assert.throws(()=>checker.assertCurrent(h));
});
test('descriptor file duplicates and forged source-policy fields cannot pass closed parsing',()=>{
 const checker=createDerivedProfileCheckerV5(families),file=path.join(directory,'duplicate.json');writeFileSync(file,JSON.stringify(descriptor()).replace('{','{"version":"invented",'));assert.throws(()=>checker.readDescriptorData(base,file));const badPolicy=path.join(directory,'policy.json');writeFileSync(badPolicy,JSON.stringify(policy).replace('{','{"authority_effect":"invented",'));assert.throws(()=>createCommerceTechnicalModelOwnerV5(badPolicy));
});
test('isolated source-model family alias changes emitted family without compiler edits',async()=>{
 const fixture=path.join(directory,'source-variant');cpSync(root,fixture,{recursive:true});const file=path.join(fixture,'profiles/implementation.alch');writeFileSync(file,readFileSync(file,'utf8').replace('  value PureComputation\n','  value PureComputation\n  value FastComputation\n').replace('field computation <- SelectedFamily.PureComputation','field computation <- SelectedFamily.FastComputation'));
 const familyFile=path.join(fixture,'profiles/family-contract.json'),doc=JSON.parse(readFileSync(familyFile,'utf8'));doc.families.FastComputation=doc.families.PureComputation;writeFileSync(familyFile,JSON.stringify(doc,null,2)+'\n');const identityFile=path.join(fixture,'contracts/contract-identities.json'),identity=JSON.parse(readFileSync(identityFile,'utf8'));for(const row of identity.modules){const b=readFileSync(path.join(fixture,row.artifact.path));row.artifact.sha256=createHash('sha256').update(b).digest('hex');row.artifact.bytes=b.length;}for(const row of identity.contract_assets){const b=readFileSync(path.join(fixture,row.path));row.sha256=createHash('sha256').update(b).digest('hex');row.bytes=b.length;}writeFileSync(identityFile,JSON.stringify(identity,null,2)+'\n');
 const altered=await families.checkTechnicalSource(fixture,'profiles/implementation.alch'),derived=families.derive(altered,params,scope),v=families.inspect(derived);assert.deepEqual(v.descriptor.families,['BoundedValues','FastComputation']);assert.deepEqual(v.native_requirements.map(r=>r.primitive_id),['bounded-values','pure-computation']);assert.notEqual(v.graph_sha256,families.inspect(base).graph_sha256);
 writeFileSync(file+'.new',readFileSync(file));renameSync(file+'.new',file);assert.throws(()=>families.assertCurrent(derived));
});
test('disposing the original technical graph invalidates its derived families',()=>{models.dispose(model);assert.throws(()=>families.assertCurrent(base));assert.throws(()=>families.assertCurrent(variant));});
