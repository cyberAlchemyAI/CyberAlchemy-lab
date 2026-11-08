import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtempSync,mkdirSync,copyFileSync,cpSync,readFileSync,writeFileSync,rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createTechnicalProfileSourceOwner} from '../../src/profile-engine/technical-profile-source.ts';
import {resolveTechnicalApplicationInputRoles} from '../../src/profile-engine/technical-profile-application-inputs.ts';
const examples=fileURLToPath(new URL('../../examples/technical-profile-source/',import.meta.url));
const crm=fileURLToPath(new URL('../../../../../../../implementation/craft-ai-reference-apps/crm/',import.meta.url));
function fixture(t:any){
 const root=mkdtempSync(path.join(tmpdir(),'application-input-source-'));t.after(()=>rmSync(root,{recursive:true,force:true}));cpSync(examples,root,{recursive:true});
 const business=path.join(root,'business');mkdirSync(business);for(const file of ['journey.alch','preferences.alch','entries.alch'])copyFileSync(path.join(crm,file),path.join(business,file));
 const owner=createTechnicalProfileSourceOwner(),handle=owner.prepare({sourceRoot:root,manifestPath:path.join(root,'crm-application.profile.json')});t.after(()=>owner.dispose(handle));
 const args=(module='CrmOperations')=>({sourceOwner:owner,sourceHandle:handle,businessSourcePath:path.join(business,'journey.alch'),components:{sameModule:[path.join(business,'preferences.alch')],entryAccess:[path.join(business,'entries.alch')],presentation:[]},roles:{decision:module+'Access.PrepareContactUpdateEntry',preference:module+'.ReadContactPreferenceEntry'}});
 return {root,business,owner,handle,args};
}
test('application source derives checked inputs and round-trips captured source with genuine ownership',t=>{
 const f=fixture(t),inspection=f.owner.inspect(f.handle);assert.equal(inspection.target_consumer,'craft.application-inputs/v1');assert.equal(inspection.topology.layout,'ServiceAssembly');assert.equal(inspection.topology.projections.review.contactAllowed.from,'sources.preferences.json.record.allowed');assert.equal(inspection.topology.sources.find((x:any)=>x.role==='Approval').minimumOrdinal,'1');
 const out=path.join(f.root,'compiled');f.owner.publishSelection(f.handle,out);const reopened=createTechnicalProfileSourceOwner(),h=reopened.prepareCompiled(path.join(out,'selection.json'));try{assert.deepEqual(reopened.inspect(h).topology,inspection.topology);assert.throws(()=>reopened.inspect(f.handle));assert.throws(()=>f.owner.inspect({kind:'original-checked-technical-profile-source/v1'} as any));}finally{reopened.dispose(h);}
});
test('application role bindings resolve target module separately from Entry module and preserve currentness',t=>{
 const f=fixture(t),roles=resolveTechnicalApplicationInputRoles(f.args());assert.equal(roles.module,'CrmOperations');assert.equal(roles.entry,'CrmOperationsAccess.PrepareContactUpdateEntry');assert.equal(roles.operation,'PrepareContactUpdate');assert.equal(roles.preferenceEntry,'CrmOperations.ReadContactPreferenceEntry');roles.assertCurrent();
 writeFileSync(path.join(f.business,'journey.alch'),readFileSync(path.join(f.business,'journey.alch'),'utf8')+'\n');assert.throws(()=>roles.assertCurrent(),/business source changed/);
});
test('renamed business module and unrelated extra Query reuse the same source profile',t=>{
 const f=fixture(t);for(const file of ['journey.alch','preferences.alch','entries.alch']){const p=path.join(f.business,file);writeFileSync(p,readFileSync(p,'utf8').replaceAll('CrmOperations','Pipeline'));}
 const p=path.join(f.business,'preferences.alch');writeFileSync(p,readFileSync(p,'utf8')+'\nquery ReadUnrelatedPreference:\n  input contactId UInt64\n  source stored StoredContactPreference\n  output optional<ContactPreferenceSnapshot>\n  where stored.contactId == contactId\n  project stored.value\n  on-missing return none\n  on-unavailable fail preference-unavailable\n');
 const roles=resolveTechnicalApplicationInputRoles(f.args('Pipeline'));assert.equal(roles.module,'Pipeline');assert.equal(roles.entry,'PipelineAccess.PrepareContactUpdateEntry');assert.equal(f.owner.inspect(f.handle).topology.providerProfile,'crm-provider');
});
test('same-shaped nominal alias, missing selector and component misclassification reject',t=>{
 const f=fixture(t),p=path.join(f.business,'journey.alch'),original=readFileSync(p,'utf8');
 const block=/value-object ReviewRequest:\n([\s\S]*?)(?=\n(?:rule|mapping|calculation|policy|operation|value-object|enum|interface|entity) )/.exec(original);assert.ok(block,'actual ReviewRequest block');
 writeFileSync(p,original.replace('operation PrepareContactUpdate:\n  input request ReviewRequest','operation PrepareContactUpdate:\n  input request AliasedReview')+'\nvalue-object AliasedReview:\n'+block[1]+'\n');assert.throws(()=>resolveTechnicalApplicationInputRoles(f.args()),/nominal decision input\/output family mismatch/);writeFileSync(p,original);
 assert.throws(()=>resolveTechnicalApplicationInputRoles({...f.args(),roles:{decision:'CrmOperationsAccess.Missing',preference:'CrmOperations.ReadContactPreferenceEntry'}}),/selected business Entry required/);
 const args=f.args();assert.throws(()=>resolveTechnicalApplicationInputRoles({...args,components:{sameModule:[path.join(f.business,'entries.alch')],entryAccess:[path.join(f.business,'preferences.alch')],presentation:[]}}),/same-module domain additions required/);
});

test('existing layout choices are selected by profile data without changing its Alch source',t=>{
 const f=fixture(t),source=readFileSync(path.join(f.root,'crm-application.alch'),'utf8'),manifestPath=path.join(f.root,'crm-application.profile.json'),envelope=JSON.parse(readFileSync(manifestPath,'utf8'));
 envelope.selection.arguments.options.layout='EntryModules';writeFileSync(manifestPath,JSON.stringify(envelope));
 const owner=createTechnicalProfileSourceOwner(),handle=owner.prepare({sourceRoot:f.root,manifestPath});try{assert.equal(owner.inspect(handle).topology.layout,'EntryModules');assert.equal(readFileSync(path.join(f.root,'crm-application.alch'),'utf8'),source);}finally{owner.dispose(handle);}
 envelope.selection.arguments.options.layout='UnknownLayout';writeFileSync(manifestPath,JSON.stringify(envelope));assert.throws(()=>owner.prepare({sourceRoot:f.root,manifestPath}),/EVALUATION|enum|variant|Invalid/i);
});

test('duplicate business Entry declarations cannot ambiguously satisfy an exact role selector',t=>{
 const f=fixture(t),file=path.join(f.business,'entries.alch'),source=readFileSync(file,'utf8'),start=source.indexOf('\nentry ');assert.ok(start>=0,'actual authored access Entry');
 writeFileSync(file,source+'\n'+source.slice(start+1));
 assert.throws(()=>resolveTechnicalApplicationInputRoles(f.args()),(error:any)=>error.diagnostics?.some((d:any)=>d.code==='DuplicateSymbol'&&d.message==='duplicate source identity'));
});
