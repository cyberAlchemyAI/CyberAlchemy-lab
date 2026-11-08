import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtempSync,cpSync,readFileSync,writeFileSync,rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createTechnicalProfileSourceOwner} from '../../src/profile-engine/technical-profile-source.ts';
import {validateTechnicalApplicationInputs,resolveTechnicalApplicationInputRoles} from '../../src/profile-engine/technical-profile-application-inputs.ts';

const examples=fileURLToPath(new URL('../../examples/technical-profile-source/',import.meta.url));
const definitions=[{stem:'knowledge-ingestion-application',family:'knowledge-ingestion/domain-v1',module:'KnowledgeIngestion',operation:'DecideActivation'},{stem:'permissioned-rag-application',family:'permissioned-rag/domain-v1',module:'PermissionedRag',operation:'ValidateAnswer'}];

test('catalog knowledge entries resolve to actual checked source profiles and publish the original descriptor',()=>{
 const catalog=JSON.parse(readFileSync(path.join(examples,'../technical-profile-sources.json'),'utf8'));
 for(const definition of definitions){
  const entries=catalog.entries.filter((entry:any)=>entry.id===definition.stem);assert.equal(entries.length,1);
  const entry=entries[0],owner=createTechnicalProfileSourceOwner(),handle=owner.prepare({sourceRoot:path.resolve(examples,'..',entry.source_root),manifestPath:path.resolve(examples,'..',entry.manifest)});
  try{const inspected=owner.inspect(handle);assert.equal(entry.consumer,inspected.target_consumer);assert.equal(inspected.topology.family,definition.family);assert.equal(entry.output_schema,'craft.technical-profile-selection/v1');assert.ok(entry.required_inputs.length);assert.ok(entry.deferred.includes('publication'));}finally{owner.dispose(handle);}
 }
});
function fixture(t:any,definition=definitions[0]!){
 const root=mkdtempSync(path.join(tmpdir(),'knowledge-profile-source-'));cpSync(examples,root,{recursive:true});t.after(()=>rmSync(root,{recursive:true,force:true}));
 const owner=createTechnicalProfileSourceOwner(),handle=owner.prepare({sourceRoot:root,manifestPath:path.join(root,definition.stem+'.profile.json')});t.after(()=>owner.dispose(handle));
 const topology=JSON.parse(JSON.stringify(owner.inspect(handle).topology)),contract=JSON.parse(readFileSync(path.join(root,'contracts',definition.stem+'-inputs.json'),'utf8'));
 const business=path.join(root,definition.stem+'-example');
 const args=()=>({sourceOwner:owner,sourceHandle:handle,businessSourcePath:path.join(business,'business.alch'),components:{sameModule:[],entryAccess:[path.join(business,'entries.alch')],presentation:[]},roles:{decision:definition.module+'Access.'+definition.operation+'Entry'}});
 return {root,owner,handle,topology,contract,business,args};
}

test('both knowledge families compile real Alch Mapping sources and publish captured no-provider selections',t=>{
 for(const definition of definitions){const f=fixture(t,definition),inspection=f.owner.inspect(f.handle);assert.equal(inspection.target_consumer,'craft.application-inputs/v1');assert.equal(inspection.topology.family,definition.family);assert.equal(inspection.topology.representation.dimensions,'1536');assert.deepEqual(Object.keys(inspection.topology).sort(),['family','decisionRole','layout','types','sources','projections','representation'].sort());assert.ok(inspection.source_files.some((s:any)=>s.path==='contracts/'+definition.stem+'-base.json'));assert.ok(!inspection.source_files.some((s:any)=>s.path.endsWith('crm-provider.profile.json')));assert.ok(!inspection.source_files.some((s:any)=>s.path.endsWith('crm-application-native.profile.json')));
  const output=path.join(f.root,'published'),next=createTechnicalProfileSourceOwner();f.owner.publishSelection(f.handle,output);const reopened=next.prepareCompiled(path.join(output,'selection.json'));try{assert.deepEqual(next.inspect(reopened).topology,inspection.topology);assert.throws(()=>next.inspect(f.handle));}finally{next.dispose(reopened);}
 }
});

test('knowledge family contracts reject fabricated protected observation paths, private prompts and unknown operands',t=>{
 for(const definition of definitions){const f=fixture(t,definition);const changed=()=>JSON.parse(JSON.stringify(f.topology));
  const prompt=changed();prompt.projections.modelInput.prompt={from:'sources.approval.json.approved'};assert.throws(()=>validateTechnicalApplicationInputs(prompt,f.contract),/original knowledge producer/);
  const literal=changed();const field=definition.stem.startsWith('knowledge-')?'parsed':'answerSupported';literal.projections.review[field]={literal:true};assert.throws(()=>validateTechnicalApplicationInputs(literal,f.contract),/closed application input record|original knowledge producer/);
  const relabel=changed();relabel.projections.review[field]={from:'facts.'+field};assert.throws(()=>validateTechnicalApplicationInputs(relabel,f.contract),/original knowledge producer/);
  const unexpected=changed();unexpected.providerProfile='crm-provider';assert.throws(()=>validateTechnicalApplicationInputs(unexpected,f.contract),/closed application input record/);
  const embedding=changed();embedding.representation.dimensions='768';assert.throws(()=>validateTechnicalApplicationInputs(embedding,f.contract),/1536-dimensional/);
  const approval=changed();approval.sources.find((s:any)=>s.role==='Approval').disclose=true;assert.throws(()=>validateTechnicalApplicationInputs(approval,f.contract),/knowledge source roles/);
  const query=changed();query.sources.find((s:any)=>s.role==='Facts').kind='ProtectedQuery';assert.throws(()=>validateTechnicalApplicationInputs(query,f.contract),/knowledge source roles/);
 }
});

test('actual knowledge role binding needs only original protected decision Entry, exact nominal DTOs and ingestion continuation',t=>{
 for(const definition of definitions){const f=fixture(t,definition),resolved=resolveTechnicalApplicationInputRoles(f.args());assert.equal(resolved.module,definition.module);assert.equal(resolved.operation,definition.operation);assert.equal(resolved.entry,definition.module+'Access.'+definition.operation+'Entry');assert.equal('preferenceEntry' in resolved,false);assert.equal(resolved.family,definition.family);assert.equal(resolved.continuationRule,definition.module==='KnowledgeIngestion'?'KnowledgeIngestion.CanActivate':undefined);resolved.assertCurrent();
  assert.throws(()=>resolveTechnicalApplicationInputRoles({...f.args(),roles:{...f.args().roles,preference:'Fake.Read'}}),/exact role assignment/);
  const source=path.join(f.business,'business.alch');writeFileSync(source,readFileSync(source,'utf8')+'\n');assert.throws(()=>resolved.assertCurrent(),/business source changed/);
 }
});

test('same-shaped decision aliases and wrong ingestion acceptance Rule cannot satisfy nominal knowledge roles',t=>{
 const f=fixture(t),file=path.join(f.business,'business.alch'),source=readFileSync(file,'utf8');
 const result=/value-object Decision:\n([\s\S]*?)(?=\n(?:rule|mapping|calculation|policy|operation|value-object|enum|interface|entity) )/.exec(source);assert.ok(result);
 writeFileSync(file,source.replace('operation DecideActivation:\n  input request ReviewRequest\n  output Decision','operation DecideActivation:\n  input request ReviewRequest\n  output AliasDecision')+'\nvalue-object AliasDecision:\n'+result[1]+'\n');assert.throws(()=>resolveTechnicalApplicationInputRoles(f.args()),/nominal decision input\/output family/);
 writeFileSync(file,source.replace('rule CanActivate:\n  input decision Decision','rule CanActivate:\n  input decision ReviewRequest'));assert.throws(()=>resolveTechnicalApplicationInputRoles(f.args()),/CanActivate Decision-to-Bool/);
});

test('knowledge architecture is selected by profile data while source Mapping and business permissions remain original',t=>{
 for(const definition of definitions){const f=fixture(t,definition),manifest=path.join(f.root,definition.stem+'.profile.json'),original=readFileSync(path.join(f.root,definition.stem+'.alch'),'utf8'),selected=JSON.parse(readFileSync(manifest,'utf8'));selected.selection.arguments.options.layout='EntryModules';writeFileSync(manifest,JSON.stringify(selected));const owner=createTechnicalProfileSourceOwner(),handle=owner.prepare({sourceRoot:f.root,manifestPath:manifest});try{assert.equal(owner.inspect(handle).topology.layout,'EntryModules');assert.equal(readFileSync(path.join(f.root,definition.stem+'.alch'),'utf8'),original);assert.match(readFileSync(path.join(f.business,'entries.alch'),'utf8'),definition.module==='KnowledgeIngestion'?/permission source\.manage/:/permission knowledge\.ask/);}finally{owner.dispose(handle);}}
});
