import assert from 'node:assert/strict';
import { generateKeyPairSync } from 'node:crypto';
import { mkdtempSync, readFileSync, writeFileSync, chmodSync } from 'node:fs';
import { spawnSync } from 'node:child_process';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { nativeCall } from '../ports/native-fixture.mjs';
import { nativePort, registryAssessment } from './ports.mjs';
import { Snapshots, bind } from './snapshots.mjs';
import { publish } from './runtime.mjs';
import { node } from './build.mjs';
import { readPublishedCatalog } from './catalog.mjs';
import { main } from './cli.mjs';
import { signPacket } from './security.mjs';
import { digest } from './verified-projection.mjs';

const root=path.resolve(import.meta.dirname,'../../../..');
const home=mkdtempSync(path.join(tmpdir(),'lab-publication-integration-'));
chmodSync(home,0o700);
const native=nativeCall(home,'seed',{id:'82',mode:'normal'});
const proposal=JSON.parse(readFileSync(path.join(home,'proposal.json')));
const approval=JSON.parse(readFileSync(path.join(home,'approval.json')));
nativePort({action:'apply',store:path.join(home,'store'),proposal,approval});
const committed=nativePort({action:'committed',store:path.join(home,'store'),operation:proposal.proposal_id});
const workspace='workspace:publication-integration',cut=committed.source_cut;
const bytes=value=>Buffer.from(JSON.stringify(value));
const files={};
function file(name,raw){files[name]=Buffer.from(raw).toString('base64');return bind(name,Buffer.from(raw));}
function material(binding){
 const raw=Buffer.from(files[binding.ref ?? binding.path],'base64');
 assert.equal(digest(raw),binding.sha256);
 assert.equal(String(raw.length),String(binding.bytes));
 return raw;
}
const definition=proposal.targets.find(target=>target.category==='definition').record;
const record=proposal.targets.find(target=>target.category!=='definition').record;
const def=file('definition.json',readFileSync(path.join(home,'original-user-journey.json')));
const work=file('work.json',bytes(record));
const schema=file('schema.json',readFileSync(path.join(root,'authority/artifact-types/definition/v2/schema.json')));
const generator=file('generator.py',readFileSync(path.join(root,'authority/artifact-types/definition/v2/generator.py')));
const descriptor=file('descriptor.json',readFileSync(path.join(root,'authority/artifact-types/definition/v2/artifact.json')));
const admission=file('carrier-admission.json',readFileSync(path.join(root,'authority/admissions/definition-complete-lab-model/v1/artifact-type-admission.json')));
const rendering=path.join(home,'DEFINITION.md');
const rendered=spawnSync('python3',['-B',path.join(root,'authority/artifact-types/definition/v2/generator.py'),
 path.join(home,'original-user-journey.json'),'--output',rendering],{encoding:'utf8'});
assert.equal(rendered.status,0,rendered.stderr);
const projection=file('DEFINITION.md',readFileSync(rendering));
const version=definition.definition_id+'@'+definition.version;
const canonical=b=>({path:b.ref,sha256:b.sha256,bytes:Number(b.bytes)});
const owner=file('owner-decision.json',bytes({decision_ref:'decision:fixture-publication'}));
const entry={definition_id:definition.definition_id,version:definition.version,body:canonical(def),
 carrier:{ref:'cal.artifact-type.definition/v2',descriptor:canonical(descriptor),admission:canonical(admission)},schema:canonical(schema),generator:canonical(generator),
 owner_disposition:canonical(owner),
 standing:'admitted-current',projection:canonical(projection),predecessor:null};
const initial={entries:[],current_lookup:{}};
writeFileSync(path.join(home,'initial.json'),bytes(initial));
const registry={schema_version:'cyberalchemy-lab-definition-registry/v2',artifact_type_ref:'cal.artifact-type.definition-registry/v2',expected_predecessor:canonical(bind('registry.json',bytes(initial))),publication_decision:canonical(owner),entries:[entry],
 current_lookup:{[definition.definition_id]:version}};
const reg=file('registry.json',bytes(registry));
const index=file('index.json',bytes({current_lookup:registry.current_lookup,
 definitions:[{version,body:entry.body,projection:entry.projection}]}));
const source=file('source.json',bytes({reader_protocol:'snapshot-selector/v1',readers:['integration-reader','lab.catalog-reader','define.catalog-reader'],native_transaction:{digest:committed.transaction,targets:committed.targets},
 approved_changes:[{version,postimage_sha256:digest(bytes(entry))}]}));
const previous=bind('registry.json',bytes(initial));
const original=file('proposal.json',readFileSync(path.join(home,'proposal.json')));
const nativeApproval=file('approval.json',readFileSync(path.join(home,'approval.json')));
const database=path.join(home,'publication.sqlite');
const snapshots=new Snapshots(database);
const staged=snapshots.stage(workspace,proposal.proposal_id,cut,files);
snapshots.close();
const selector=bind('selector',bytes(null));
const proof=(subject,predicate)=>({subject,scope:workspace,cut,predicate,issuer:'principal:publisher',
 policy:bind('fixture:policy',bytes({})),proof:bind('fixture:proof',bytes({}))});
const targets=[def,work];
const reviews=targets.map(target=>({target,expected_owner:'role:definition-owner',scope:workspace,source_cut:cut,
 source_current:true,fields_receipt:schema,consumer_bindings_current:true,
 disposition:{target,previous:null,owner:'role:definition-owner',scope:workspace,source_cut:cut,outcome:'Accepted',
 role_assignment:bind('fixture:role',bytes({})),verification_receipt:bind('fixture:semantic-owner',bytes({}))}}));
const registryDescriptor=bytes({artifact_type_ref:'cal.artifact-type.definition-registry/v2',identity:['definition_id','version']});
const value={workspace,source_cut:cut,expected_selector:selector,observed_selector:selector,
 expected_registry:previous,observed_registry:previous,proposed_registry:reg,
 expected_targets:committed.targets_digest,proposal:original,operation_ref:proposal.proposal_id,
 target_bodies:targets,semantic_reviews:reviews,registry_contract_current:true,
 registry_contract:bind('fixture:registry-contract',registryDescriptor),permission:nativeApproval,
 permission_proposal:original,native_head:proposal.expected_head,
 native_receipt:{head:proposal.expected_head,workspace,operation_ref:proposal.proposal_id,proposal:original,
 targets:committed.targets_digest,source_cut:cut,outcome:'Committed',proof:committed.original_receipt},
 publication_receipt:null,published_postimage:null,observed_receipt:null,bundle:staged.binding,
 bundle_review:proof(staged.binding,'closed-publication-bundle'),
 canonical_permission:proof(staged.binding,'canonical-publication'),
 snapshot:{bundle:staged.binding,operation:proposal.proposal_id,workspace,cut,expected_head:proposal.expected_head,
 predecessor:previous,expected_selector:selector,registry:reg,index,source,targets:committed.targets_digest,draft_only:true,
 readers:proof(source,'qualified-readers'),migration:proof(reg,'registry-migration')}};
const {privateKey,publicKey}=generateKeyPairSync('ed25519');
const privatePem=privateKey.export({format:'pem',type:'pkcs8'});
const trust={principals:{'principal:publisher':{public_key:publicKey.export({format:'pem',type:'spki'}),
 grants:[{predicate:'verified-planning-input',operation:'PlanPublication',scope:workspace,cut}]}},
 required_readers:['integration-reader','lab.catalog-reader','define.catalog-reader'],
 carriers:{'cal.artifact-type.definition/v2':{schema,generator,descriptor,admission}},
 initial_registry:{path:path.join(home,'initial.json'),sha256:digest(bytes(initial))}};
const registryAdmission=bytes({artifact_type_ref:'cal.artifact-type.definition-registry/v2',
 standing:'owner-admitted-current',descriptor_sha256:digest(registryDescriptor)});
trust.principals['principal:publisher'].grants.push({predicate:'artifact-type-admission',operation:'PlanPublication',scope:workspace,cut});
trust.registry_contract={artifact:registryDescriptor.toString('base64'),admission_artifact:registryAdmission.toString('base64'),
 admission:signPacket(bytes({version:1,predicate:'artifact-type-admission',operation:'PlanPublication',scope:workspace,cut,
 artifact:{sha256:digest(registryAdmission),bytes:registryAdmission.length}}),'principal:publisher',privatePem)};
const artifact=bytes({operation:'PlanPublication',scope:workspace,cut,input:{value}});
const packet=signPacket(bytes({version:1,predicate:'verified-planning-input',operation:'PlanPublication',scope:workspace,cut,
 artifact:{sha256:digest(artifact),bytes:artifact.length}}),'principal:publisher',privatePem);
const request={operation:'PlanPublication',scope:workspace,cut,artifact:artifact.toString('base64'),
 receipt:packet,files,native_store:path.join(home,'store')};
const missingContract={...trust};delete missingContract.registry_contract;
await assert.rejects(()=>publish(request,missingContract,path.join(home,'missing-contract.sqlite')),/admission-required/);
const candidateAdmission=bytes({artifact_type_ref:'cal.artifact-type.definition-registry/v2',
 standing:'candidate-unadmitted',descriptor_sha256:digest(registryDescriptor)});
const unadmitted={...trust,registry_contract:{...trust.registry_contract,
 admission_artifact:candidateAdmission.toString('base64'),
 admission:signPacket(bytes({version:1,predicate:'artifact-type-admission',operation:'PlanPublication',scope:workspace,cut,
 artifact:{sha256:digest(candidateAdmission),bytes:candidateAdmission.length}}),'principal:publisher',privatePem)}};
await assert.rejects(()=>publish(request,unadmitted,path.join(home,'candidate-contract.sqlite')),/not-current/);
const receipt=await publish(request,trust,database);
assert.equal(receipt.selected.revision,1);
assert.equal((await publish(request,trust,database)).replayed,true);
const restarted=new Snapshots(database);
assert.equal(restarted.current(workspace).digest,staged.binding.sha256);
assert.equal(JSON.parse(restarted.material(receipt.selected.digest,'registry.json').bytes).entries.length,1);
restarted.close();
const unapproved={...registry,entries:[{...entry,body:{...def,sha256:'0'.repeat(64)}}]};
assert.throws(()=>registryAssessment(initial,unapproved,material,trust.carriers,[]),/unapproved-addition/);
const lost={...registry,entries:[]};
assert.throws(()=>registryAssessment(registry,lost,material,trust.carriers,[]),/retained-version-missing/);

const profile=JSON.parse(readFileSync(path.join(root,'WORKSPACE.json')));
profile.workspace_ref=workspace;
profile.revision='shared-qualification';
profile.kind='project';
profile.primary_subject={kind:'project',key:native.request.branch.project,ref:native.request.branch.project};
profile.linked_project_refs=[];
profile.goals=[];
profile.scope_ref=workspace;
profile.purpose='Isolated shared runtime qualification';
profile.home={mode:'hosted',path:home};
const catalog=JSON.parse(readFileSync(path.join(root,'implementation/lab-workspaces/v2/catalog.json')));
catalog.runtimes[profile.runtime_selection.runtime_ref].workspace_refs=[workspace];
writeFileSync(path.join(home,'WORKSPACE.json'),bytes(profile));
writeFileSync(path.join(home,'catalog.json'),bytes(catalog));
const scoped=(subject,predicate)=>({...proof(subject,predicate),scope:'construction'});
const stages=['Definitions','Artifacts','Business','Bridge','System','AlchLang','Generation'].map(stage=>({
 stage,subject:bind('fixture:stage:'+stage,bytes({stage})),source_cut:cut}));
const handoffs=stages.slice(0,-1).map((stage,i)=>({
 source_stage:stage.stage,target_stage:stages[i+1].stage,input_subject:stage.subject,output_subject:stages[i+1].subject,
 source_cut:cut,contract:bind('fixture:handoff:'+i,bytes({i}))}));
const spec={obligation:'fixture:construction-obligation',source:bind('fixture:spec',bytes({})),
 executor:bind('fixture:executor',bytes({})),fixture:bind('fixture:case',bytes({}))};
const permission=bind('approval',readFileSync(path.join(home,'approval.json')));
const selection=bind('fixture:construction-selection',bytes({targets}));
const constructionValue={
 selected_targets:targets,admitted_targets:[],review_targets:targets,selection,
 selection_review:scoped(selection,'complete-selection'),specifications:[spec],
 source_cut:cut,stages,handoffs,required_obligations:[spec.obligation],specified_checks:[spec.obligation],
 unresolved_mappings:'0',definitions:reviews,definition_targets:targets,definition_selection_receipt:selection,
 construction_compatibility:bind('fixture:compatibility',bytes({})),prototype_selection:bind('fixture:prototype',bytes({})),
 language_selection:bind('fixture:language',bytes({})),native_closure:bind('fixture:native',bytes({})),
 resolved_capabilities_receipt:bind('fixture:capabilities',bytes({})),effects_requested:true,permission
};
trust.principals['principal:publisher'].grants.push({
 predicate:'verified-planning-input',operation:'AssessConstructionEntry',scope:workspace,cut});
function constructionPacket(value) {
 const artifact=bytes({operation:'AssessConstructionEntry',scope:workspace,cut,input:{value}});
 return {operation:'AssessConstructionEntry',scope:workspace,cut,artifact:artifact.toString('base64'),
 receipt:signPacket(bytes({version:1,predicate:'verified-planning-input',operation:'AssessConstructionEntry',
 scope:workspace,cut,artifact:{sha256:digest(artifact),bytes:artifact.length}}),'principal:publisher',privatePem)};
}
const nativeSchema=bytes({type:'object',required:['proposal_digest','targets_digest','expected_head','source_cut','transaction','original_receipt']});
writeFileSync(path.join(home,'native.schema.json'),nativeSchema);
trust.schemas={native:{path:path.join(home,'native.schema.json'),sha256:digest(nativeSchema)}};
trust.principals['principal:publisher'].grants.push({predicate:'native-effect',operation:'PlanPublication',scope:workspace,cut});
writeFileSync(path.join(home,'trust.json'),bytes(trust));
const nativeRequest={workspace:path.join(home,'WORKSPACE.json'),catalog:path.join(home,'catalog.json'),
 project:native.request.branch.project,store:path.join(home,'store'),proposal,approval,approval_artifact:readFileSync(path.join(home,'approval.json')).toString('base64'),
 construction:constructionPacket(constructionValue)};
writeFileSync(path.join(home,'native-apply.json'),bytes(nativeRequest));
const replay=await main(['native-apply','--file',path.join(home,'native-apply.json'),'--trust',path.join(home,'trust.json')]);
assert.equal(replay.idempotent,true);
writeFileSync(path.join(home,'native-apply-inspect.json'),bytes({
 ...nativeRequest,construction:constructionPacket({...constructionValue,effects_requested:false})}));
await assert.rejects(()=>main(['native-apply','--file',path.join(home,'native-apply-inspect.json'),'--trust',path.join(home,'trust.json')]),/effect-binding-mismatch/);

writeFileSync(path.join(home,'publisher.pem'),privatePem,{mode:0o600});
writeFileSync(path.join(home,'observe-native.json'),bytes({store:path.join(home,'store'),original_operation:proposal.proposal_id,
 operation:'PlanPublication',scope:workspace,cut,schema:'native'}));
const observedNative=await main(['observe-native','--file',path.join(home,'observe-native.json'),
 '--trust',path.join(home,'trust.json'),'--issuer','principal:publisher','--key',path.join(home,'publisher.pem')]);
assert.equal(JSON.parse(Buffer.from(observedNative.artifact,'base64')).original_receipt.sha256,committed.original_receipt.sha256);

const conflicting=structuredClone(proposal);
conflicting.targets[0].record.name='Conflicting signed-operation request';
assert.throws(()=>nativePort({action:'apply',store:path.join(home,'store'),proposal:conflicting,approval}),/operation-conflict/);

const catalogView=readPublishedCatalog(database,workspace);
assert.throws(()=>readPublishedCatalog(database,workspace,'reader:unqualified'),/reader-unqualified/);
assert.equal(catalogView.entries[0].definition_id,definition.definition_id);
assert.equal(catalogView.entries[0].sha256,def.sha256);
const sessionDirectory=path.join(home,'define-session');
const sessionStart={session_id:'session:published-definition-reader',
 scope:{project:null,work:null,goal:'Inspect a published Definition',originating_intent:'Verify shared Lab reader integration',
 context_description:'Isolated snapshot reader qualification',consumer:'fixture:reader',intended_use:'review-meanings'},
 request_revision:'1',request_lineage:{predecessor_package_binding:null,language_evidence_binding:null,field_supplement_binding:null},
 validation_scope:{required_checks:[],evidence_scope:'Published source lookup',claim_ceiling:'Reported source observation'}};
writeFileSync(path.join(home,'define-start.json'),bytes(sessionStart));
const defineCli=path.join(root,'workspaces/products/define/implementation/cli/alchlang/runtime/cli.mjs');
function define(args){
 const run=spawnSync(node,[defineCli,...args],{encoding:'utf8',maxBuffer:16*1024*1024,timeout:300000});
 assert.equal(run.status,0,run.stderr+' '+run.stdout);
 return JSON.parse(run.stdout);
}
define(['start','--work',sessionDirectory,'--file',path.join(home,'define-start.json'),'--actor','fixture:reader','--id','fixture:start']);
const discovery=define(['discover','--work',sessionDirectory,'--snapshot-db',database,'--workspace',workspace,
 '--query',definition.definition_id,'--actor','fixture:reader','--id','fixture:discover']);
assert(JSON.stringify(discovery).includes(definition.definition_id));
const result={status:'PASS',checks:[
 'real-native-signed-local-transaction',
 'registry-contract-current-standing-derived-from-signed-admission',
 'missing-registry-contract-admission-refused',
 'signed-candidate-registry-contract-refused',
 'qualified-original-definition-schema-and-generator',
 'mixed-version-registry-validation-and-deterministic-projection',
 'signed-compiled-publication-route',
 'closed-native-target-and-snapshot-membership',
 'atomic-selector-and-publication-receipt',
 'publication-operation-replay-after-commit',
 'snapshot-reader-after-restart',
 'unapproved-registry-addition-refused',
 'retained-registry-version-removal-refused',
 'public-native-apply-validates-workspace-construction-and-permission',
 'read-only-construction-cannot-dispatch-native-effect',
 'public-native-observation-signs-exact-original-transaction',
 'changed-request-cannot-reconcile-as-an-old-native-commit',
 'published-catalog-reader-retains-current-original-binding',
 'define-cli-discovers-selected-published-definition'
],scope:'Isolated native store and snapshot publication using real signatures and original Lab Definition/v2 material. Fixture semantic decisions authorize only this temporary namespace.'};
writeFileSync(path.join(import.meta.dirname,'PUBLICATION-VERIFICATION.json'),JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify(result));
