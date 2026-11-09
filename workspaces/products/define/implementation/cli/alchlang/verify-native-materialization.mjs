import {observeValueFields} from '../../../../../../implementation/artifact-runtime/observe-value-fields.mjs';
import assert from 'node:assert/strict';
import path from 'node:path';
import {readFileSync,writeFileSync} from 'node:fs';
import {root,fingerprint} from './materialization-build.mjs';
import {callNative as call} from './runtime/native.mjs';
import {openJsonPort} from '../../../../../../implementation/artifact-runtime/json-pipe.mjs';
const R=path.resolve(root,'../../../../../..'),base=path.join(R,'workspaces/products/define/implementation/cli/alchlang/tests/fixtures/materialization-package'),pack=JSON.parse(readFileSync(path.join(base,'pack.json'))),selection=pack.materialization_selection[0],meaning=pack.working_meanings[0],definition=JSON.parse(readFileSync(path.join(base,'inputs',selection.definition_binding.path))),checks=[];
const port=openJsonPort(path.join(R,'implementation/artifact-runtime/json-port.py'));
async function project(name,documents,args={marker:true}){return (await port.request({operation:'construct-value',documents,batches:[await call('Define.PackageConstruction.'+name,args)]})).value;}
try{
 const successor=await call('Define.PackageConstruction.VerifyMaterializationSelection',{value:{identity_intention:selection.identity_intention,entry_kind:selection.meaning_ref.entry_kind,parent_present:selection.parent_ref!==null}});
 const resources=await call('Define.PackageConstruction.SelectMaterializationResources',{marker:true});
 const notation=[];for(const parameter of meaning.parameters)notation.push(await project('NotationProjection',{parameter}));
 const docs={selection,meaning,definition,notation,schema:resources.schema,provider:resources.provider,owner_metadata:await port.request({operation:'json-shape',value:selection.owner_route})};
 Object.assign(docs,await observeValueFields({port,call,selector:'Define.PackageConstruction.MaterializationDigestFields',documents:docs}));
 Object.assign(docs,await observeValueFields({port,call,selector:'Define.PackageConstruction.MaterializationParentFields',documents:docs,args:{successor}}));
 const facts=(await port.request({operation:'construct-value',documents:docs,batches:[await call('Define.PackageConstruction.MaterializationFactsA',{marker:true}),await call('Define.PackageConstruction.MaterializationFactsB',{successor})]})).value;
 assert.equal(await call('Define.PackEngine.VerifyMaterialization',facts),true);checks.push('actual-Definition-and-working-meaning-native-comparison');
 assert.equal(await call('Define.PackageConstruction.VerifyApplicability',await project('ApplicabilityFacts',docs)),true);checks.push('actual-applicability-comparison');
 for(const patch of [{entry_kind:'application'},{parent_present:true},{identity_intention:'unknown'}]){await assert.rejects(()=>call('Define.PackageConstruction.VerifyMaterializationSelection',{value:{identity_intention:selection.identity_intention,entry_kind:selection.meaning_ref.entry_kind,parent_present:false,...patch}}));checks.push('negative-selection:'+Object.keys(patch)[0]);}
 await assert.rejects(()=>call('Define.PackageConstruction.VerifyApplicability',{value:{selected:'1'.repeat(64),observed:'2'.repeat(64)}}));checks.push('negative-applicability');
 assert.equal(await call('Define.PackageConstruction.VerifyLineageStatistics',{value:{leaves:'12',witnesses:'12',distinct_count:'12'}}),true);
 for(const patch of [{leaves:'13'},{distinct_count:'11'},{witnesses:'1025'}]){await assert.rejects(()=>call('Define.PackageConstruction.VerifyLineageStatistics',{value:{leaves:'12',witnesses:'12',distinct_count:'12',...patch}}));checks.push('negative-lineage:'+Object.keys(patch)[0]);}
 const provider={...resources.provider,bytes:Number(resources.provider.bytes)};const rendered=await port.request({operation:'render-provider',root:R,binding:provider,export:'render',value:definition});assert.ok(rendered.bytes>100);checks.push('bound-shared-artifact-provider-rendering');
 await assert.rejects(()=>port.request({operation:'render-provider',root:R,binding:{...provider,sha256:'0'.repeat(64)},export:'render',value:definition}));checks.push('changed-provider-bytes-refused');
 const receipt={schema_version:'define-native-materialization-policy-verification/v1',status:'PASS',source:fingerprint(),checks,check_count:checks.length,full_materialization_workflow:false,scope:'Actual retained Definition comparison, applicability, selection, total-lineage preconditions and exact shared provider; output workflow remains pending.'};writeFileSync(path.join(root,'.local/NATIVE-MATERIALIZATION-POLICY-VERIFICATION.json'),JSON.stringify(receipt,null,2)+'\n');console.log(JSON.stringify(receipt));
}finally{await port.close();}