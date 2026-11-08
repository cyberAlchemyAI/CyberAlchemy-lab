/** Focused real-source lowering cases. Final installed/runtime proof is separate.
 * Open Questions: ../../../../goals/plans/craft-crm-business-only-generation-2026-11-01/DESIGN.md.
 */
import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtempSync,cpSync,readFileSync,writeFileSync,rmSync,mkdirSync,renameSync} from 'node:fs';
import {tmpdir} from 'node:os';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {profileEngine} from '@domainspec-v2/cli';
import {deriveApplicationInputs} from './profile-inputs.mjs';
import {canonical} from '../shared.mjs';
const repo=fileURLToPath(new URL('../../../../',import.meta.url));
const examples=path.join(repo,'craft/projects/domainspec-v2/impl/cli/examples/technical-profile-source');
const crm=path.join(repo,'implementation/craft-ai-reference-apps/crm');
const envPath=path.join(repo,'goals/plans/craft-crm-business-only-generation-2026-11-01/examples/environment.identity.target.json');
function fixture(t,{renamed=false,renamedProvider=false}={}){
 const root=mkdtempSync(path.join(tmpdir(),'craft-input-lowering-')),profileRoot=path.join(root,'profiles'),business=path.join(root,'business');cpSync(examples,profileRoot,{recursive:true});mkdirSync(business);
 for(const name of ['journey.alch','preferences.alch','entries.alch']){let value=readFileSync(path.join(crm,name),'utf8');if(renamed)value=value.replaceAll('CrmOperations','OtherContacts');writeFileSync(path.join(business,name),value);}
 if(renamed){const extra='\nquery ReadPreferenceExtra:\n  input contactId UInt64\n  source stored StoredContactPreference\n  output optional<ContactPreferenceSnapshot>\n  where stored.contactId == contactId\n  project stored.value\n  on-missing return none\n  on-unavailable fail preference-unavailable\n';const p=path.join(business,'preferences.alch');writeFileSync(p,readFileSync(p,'utf8')+extra);}
 if(renamedProvider){const old=path.join(profileRoot,'crm-provider.profile.json'),custom=path.join(profileRoot,'custom-crm-provider.profile.json'),manifest=JSON.parse(readFileSync(old,'utf8'));manifest.id='Profiles.CustomCrmProvider';renameSync(old,custom);writeFileSync(custom,JSON.stringify(manifest,null,2)+'\n');const contractPath=path.join(profileRoot,'contracts/application-inputs.json'),contract=JSON.parse(readFileSync(contractPath,'utf8'));contract.assets.providerProfile='custom-crm-provider.profile.json';writeFileSync(contractPath,JSON.stringify(contract,null,2)+'\n');const compositionPath=path.join(profileRoot,'crm-application-native.profile.json'),composition=JSON.parse(readFileSync(compositionPath,'utf8'));composition.bindings.provider.profile=manifest.id;writeFileSync(compositionPath,JSON.stringify(composition,null,2)+'\n');const modelPath=path.join(profileRoot,'crm-application.alch');writeFileSync(modelPath,readFileSync(modelPath,'utf8').replace('field providerProfile <- "crm-provider"','field providerProfile <- "custom-crm-provider"'));}
 const sourceOwner=profileEngine.createTechnicalProfileSourceOwner(),sourceHandle=sourceOwner.prepare({sourceRoot:profileRoot,manifestPath:path.join(profileRoot,'crm-application.profile.json')}),module=renamed?'OtherContacts':'CrmOperations';let derived;
 const request={sourceOwner,sourceHandle,profileRoot,businessSourcePath:path.join(business,'journey.alch'),businessComponents:{sameModule:[path.join(business,'preferences.alch')],entryAccess:[path.join(business,'entries.alch')],presentation:[]},businessRoles:{decision:module+'Access.PrepareContactUpdateEntry',preference:module+'.ReadContactPreferenceEntry'},environment:JSON.parse(readFileSync(envPath,'utf8'))};
 t.after(()=>{derived?.close();sourceOwner.dispose(sourceHandle);rmSync(root,{recursive:true,force:true});});return {root,profileRoot,business,request,async derive(){derived=await deriveApplicationInputs(request);return derived;}};
}
test('CG04 real source produces original intent/projections/provider input and separate revision fields',async t=>{
 const f=fixture(t),value=await f.derive();assert.equal(value.intent.module,'CrmOperations');assert.equal(value.intent.entryAccess.entry,'CrmOperationsAccess.PrepareContactUpdateEntry');assert.equal(value.intent.operation,'PrepareContactUpdate');assert.equal(value.intent.schema,'craft.ai-application-intent/v1');assert.equal(value.intent.stages[1].capability_binding,'CrmOperations.HubspotContactSlot');assert.equal(value.sourceSelection.projections.review.contactAllowed.from,'sources.preferences.json.record.allowed');assert.equal(value.sourceSelection.projections.review.currentPreferenceVersion.from,'sources.preferences.json.record.version');assert.equal(value.sourceSelection.projections.review.expectedPreferenceVersion.from,'facts.expectedPreferenceVersion');assert.equal(value.sourceSelection.roles.find(r=>r.role==='approval').minimumOrdinal,1);assert.equal(value.sourceSelection.roles.find(r=>r.role==='preferences').adapter,'crm-preferences');assert.equal(value.provider.selection.payload.email.from,'facts.email');assert.equal(value.provider.selection.payload.industry.from,'decision.industry');assert.equal(value.provider.selection.logicalIdentity.parentCommand.from,'request.instance_sha256');assert.equal(value.provider.binding,'connector');assert.equal(value.provider.selection.account,undefined);assert.equal(value.inferenceOptions.target.model_or_harness,f.request.environment.inference.model);assert.equal(value.query.subjectInputs.inputField,'contactId');assert.equal(value.query.resultView.identityField,'contactId');assert.equal(value.query.entry,'CrmOperations.ReadContactPreferenceEntry');assert.doesNotThrow(()=>canonical(value.origins));value.assertCurrent();value.close();assert.throws(()=>value.assertCurrent(),{code:'StaleOwner'});value.close();
});
test('CG04 rejects environment changes incompatible with selected provider policy/resource contract',async t=>{
 const f=fixture(t);for(const [field,value] of [['resourceId','other-crm'],['operation','contact.delete'],['provider','other-provider']]){const environment=structuredClone(f.request.environment);environment.crm[field]=value;await assert.rejects(deriveApplicationInputs({...f.request,environment}));}
 const environment=structuredClone(f.request.environment);environment.effect.maxAttempts=2;await assert.rejects(deriveApplicationInputs({...f.request,environment}),{code:'UnsupportedCapability'});
});
test('CG04 source/profile roots and business files stay current after successful lowering',async t=>{
 const f=fixture(t),value=await f.derive(),file=path.join(f.profileRoot,'contracts/crm-application-base.json');writeFileSync(file,readFileSync(file,'utf8')+'\n');assert.throws(()=>value.assertCurrent(),{code:'TECHNICAL_PROFILE_STALE'});
});
test('CG04 original Core source custody rejects actor/profile-shaped JSON owners',async t=>{
 const f=fixture(t);await assert.rejects(deriveApplicationInputs({...f.request,sourceOwner:{inspect:()=>({target_consumer:'craft.application-inputs/v1'}),assertCurrent(){}}}));
});
test('CG04 reusable source supports renamed business module and an unrelated added Query',async t=>{
 const f=fixture(t,{renamed:true}),value=await f.derive();assert.equal(value.intent.module,'OtherContacts');assert.equal(value.intent.entryAccess.entry,'OtherContactsAccess.PrepareContactUpdateEntry');assert.equal(value.query.entry,'OtherContacts.ReadContactPreferenceEntry');assert.equal(value.origins.source_profile.id,'Profiles.CrmApplication');assert.equal(value.provider.inspection.id,'Profiles.CrmProvider');
});

test('CG04 profile author can rename a supported provider source without compiler changes',async t=>{
 const f=fixture(t,{renamedProvider:true}),value=await f.derive();assert.equal(value.provider.inspection.id,'Profiles.CustomCrmProvider');assert.equal(path.basename(value.provider.profileManifest),'custom-crm-provider.profile.json');assert.equal(value.provider.selection.operation,'contact.upsert');assert.equal(value.provider.selection.payload.industry.from,'decision.industry');value.assertCurrent();
});
