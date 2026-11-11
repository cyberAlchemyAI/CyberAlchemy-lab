import assert from 'node:assert/strict';
import {readFileSync,writeFileSync,mkdirSync,existsSync,renameSync} from 'node:fs';
import {spawnSync} from 'node:child_process';
import path from 'node:path';
import {main} from '../../../implementation/lab-runtime/alchlang/shared-records/cli.mjs';
import {evaluate} from '../../../implementation/lab-runtime/alchlang/shared-records/kernel.mjs';
import {nativePort,registryAssessment} from '../../../implementation/lab-runtime/alchlang/shared-records/ports.mjs';
import {Snapshots,bind} from '../../../implementation/lab-runtime/alchlang/shared-records/snapshots.mjs';
import {signPacket} from '../../../implementation/lab-runtime/alchlang/shared-records/security.mjs';
import {digest} from '../../../implementation/lab-runtime/alchlang/shared-records/verified-projection.mjs';
import {readPublishedCatalog} from '../../../implementation/lab-runtime/alchlang/shared-records/catalog.mjs';
const here=import.meta.dirname,root=path.resolve(here,'../../..');
const local=path.join(root,'.local/lab-runtime/shared');
const database=path.join(local,'snapshots.sqlite');
const key=path.join(process.env.HOME,'.config/cyberalchemy-lab/shared-records/operator.pem');
const issuer='principal:lab-shared-operator',workspace='workspace:cyberalchemy-lab:lab';
const json=f=>JSON.parse(readFileSync(f));
const bytes=x=>Buffer.from(JSON.stringify(x));
const put=(f,x)=>{mkdirSync(path.dirname(f),{recursive:true});writeFileSync(f,JSON.stringify(x,null,2)+'\n');};
if(existsSync(path.join(here,'receipts/application.json'))){
 const prior=json(path.join(here,'receipts/application.json'));
 console.log(JSON.stringify({...prior,replayed:true}));process.exit(0);
}
const auth=json(path.join(here,'authorization.json'));
assert.equal(auth.authorized,true);
const proposal=json(path.join(here,'proposal.json')),approval=json(path.join(here,'approval.json'));
const cut=proposal.source_snapshot_digest,scope=workspace,operation=proposal.proposal_id;
const binding=f=>bind(path.relative(root,f),readFileSync(f));
const authorization=binding(path.join(here,'authorization.json'));
const role=binding(path.join(here,'role-assignment.json'));
const target=binding(path.join(here,'target.json'));
const shared=path.join(root,'implementation/lab-runtime/alchlang/shared-records');
const qualification=binding(path.join(shared,'QUALIFICATION.json'));
const decisions=[];
for(const item of auth.accepted_definitions){
 const original=readFileSync(path.join(root,item.source.path));
 assert.equal(digest(original),item.source.sha256);
 const body=JSON.parse(original);
 const decision={schema_version:'lab-exact-definition-owner-disposition/v1',
 decision_ref:'decision:shared-definitions-records-0076:'+body.definition_id,
 target:item.version,original:item.source,owner:'role:definition-owner',principal_ref:auth.principal_ref,
 role_assignment:role,scope:body.scope.authority_scope_ref,source_cut:cut,outcome:'Accepted',
 canonical_admission:true,authorization,consumer_realization:{implementation_manifest:binding(path.join(shared,'SOURCE-MANIFEST.json')),qualification},
 reason:'Explicit owner acceptance of this exact candidate for shared Lab definitions and records. Earlier candidate posture and residues remain historical authored text; this separate decision establishes current admission.'};
 const filename=path.join(here,'dispositions',body.definition_id+'.json');put(filename,decision);
 decisions.push({body,original,decision,filename});
}
const descriptor=readFileSync(path.join(here,'registry-descriptor.json'));
const admission={schema_version:'lab-registry-contract-admission/v1',
 decision_ref:'decision:shared-definitions-records-0076:registry-v2',
 artifact_type_ref:'cal.artifact-type.definition-registry/v2',standing:'owner-admitted-current',
 descriptor_sha256:digest(descriptor),descriptor:binding(path.join(here,'registry-descriptor.json')),
 proposed_contract:binding(path.join(root,'work/plans/shared-definitions-records/contracts/definition-registry-v2.contract.json')),
 schema:binding(path.join(shared,'contracts/definition-registry-v2.schema.json')),
 authorization,principal_ref:auth.principal_ref,owner_ref:'role:artifact-type-owner',
 scope,source_cut:cut,reason:'Explicit owner admission of the mixed-version Registry/v2 contract and internal shared Lab activation.'};
put(path.join(here,'registry-admission.json'),admission);
const trust={principals:{[issuer]:{public_key:readFileSync(key.replace('.pem','.pub'),'utf8').trim(),
 grants:['AssessConstructionEntry','PlanPublication','ReviewFiveDefinitions','InitializeJoin','AssessJoinTransition'].map(operation=>({predicate:'verified-planning-input',operation,scope,cut}))}},
 workspaces:{[workspace]:{scope}},required_readers:['lab.catalog-reader','define.catalog-reader'],
 initial_registry:{path:path.join(root,'authority/definitions/registry.json'),sha256:digest(readFileSync(path.join(root,'authority/definitions/registry.json')))}};
trust.principals[issuer].grants.push({predicate:'artifact-type-admission',operation:'PlanPublication',scope,cut});
function packet(operation,input){
 const artifact=bytes({operation,scope,cut,input});
 return {operation,scope,cut,artifact:artifact.toString('base64'),receipt:signPacket(bytes({
 version:1,predicate:'verified-planning-input',operation,scope,cut,artifact:{sha256:digest(artifact),bytes:artifact.length}}),issuer,readFileSync(key))};
}
const proof=(subject,predicate,proofBinding=authorization,proofScope=scope)=>({subject,scope:proofScope,cut,predicate,issuer,policy:authorization,proof:proofBinding});
const reviews=decisions.map(x=>({target:bind(x.decision.original.path,x.original),expected_owner:'role:definition-owner',
 scope:x.decision.scope,source_cut:cut,source_current:true,fields_receipt:qualification,consumer_bindings_current:true,
 disposition:{target:bind(x.decision.original.path,x.original),previous:null,owner:'role:definition-owner',scope:x.decision.scope,source_cut:cut,outcome:'Accepted',role_assignment:role,verification_receipt:binding(x.filename)}}));
const reviewed=await evaluate('ReviewFiveDefinitions',{expected:reviews.map(x=>x.target),reviews});
assert.deepEqual(reviewed,Array(5).fill('CandidateOnly'));
put(path.join(here,'receipts/semantic-review.json'),{status:'PASS',source_cut:cut,results:reviewed,
 note:'AlchLang preparation remains CandidateOnly; canonical admission is a separate explicit owner transaction.',reviews});
const stages=['Definitions','Artifacts','Business','Bridge','System','AlchLang','Generation'];
const stageFiles=['work/plans/shared-definitions-records-r4/DEFINITIONS.json','work/plans/shared-definitions-records-r4/CONTRACTS.json','work/plans/shared-definitions-records-r4/ONTOLOGY.json','work/plans/shared-definitions-records-r4/BRIDGE.json','work/plans/shared-definitions-records-r4/SYSTEM.json','implementation/lab-runtime/alchlang/shared-records/SOURCE-MANIFEST.json','implementation/lab-runtime/alchlang/shared-records/DECISION-VERIFICATION.json'];
const stageSubjects=stages.map((stage,i)=>({stage,subject:binding(path.join(root,stageFiles[i])),source_cut:cut}));
const handoffRecords=json(path.join(root,'work/plans/shared-definitions-records-r4/CHAIN-HANDOFFS.json')).handoffs;
assert.equal(handoffRecords.length,6);
const handoffs=stageSubjects.slice(0,-1).map((s,i)=>({source_stage:s.stage,target_stage:stageSubjects[i+1].stage,input_subject:s.subject,output_subject:stageSubjects[i+1].subject,source_cut:cut,contract:binding(path.join(root,'work/plans/shared-definitions-records-r4/CHAIN-HANDOFFS.json'))}));
const selected=reviews.map(x=>x.target);
const spec={obligation:'shared-lab:exact-authorized-admission',source:target,executor:binding(path.join(here,'validate.py')),fixture:authorization};
const construction={selected_targets:selected,admitted_targets:[],review_targets:selected,selection:target,
 selection_review:proof(target,'complete-selection',target,'construction'),specifications:[spec],source_cut:cut,
 stages:stageSubjects,handoffs,required_obligations:[spec.obligation],specified_checks:[spec.obligation],unresolved_mappings:'0',
 definitions:reviews,definition_targets:selected,definition_selection_receipt:binding(path.join(here,'receipts/semantic-review.json')),
 construction_compatibility:binding(path.join(root,'authority/definitions/candidates/0018-construction-chain/contracts/construction-compatibility.json')),
 prototype_selection:binding(path.join(root,'work/plans/shared-definitions-records-r4/GENERATION-RECEIPT.json')),
 language_selection:binding(path.join(shared,'profile.json')),native_closure:binding(path.join(root,'implementation/lab-runtime/alchlang/native-source.json')),
 resolved_capabilities_receipt:qualification,effects_requested:true,permission:binding(path.join(here,'approval.json'))};
const nativeRequest={workspace:path.join(root,'WORKSPACE.json'),catalog:path.join(root,'implementation/lab-workspaces/v2/catalog.json'),
 project:'project:cyberalchemy-v2-to-lab-migration',store:path.join(local,'native-store'),proposal,approval,
 approval_artifact:readFileSync(path.join(here,'approval.json')).toString('base64'),
 construction:packet('AssessConstructionEntry',{value:construction})};
put(path.join(here,'native-apply.json'),nativeRequest);
trust.registry_contract={artifact:descriptor.toString('base64'),admission_artifact:bytes(admission).toString('base64'),
 admission:signPacket(bytes({version:1,predicate:'artifact-type-admission',operation:'PlanPublication',scope,cut,artifact:{sha256:digest(bytes(admission)),bytes:bytes(admission).length}}),issuer,readFileSync(key))};
put(path.join(here,'trust.json'),trust);
const applied=await main(['native-apply','--file',path.join(here,'native-apply.json'),'--trust',path.join(here,'trust.json')]);
put(path.join(here,'receipts/native-application.json'),applied);
const committed=nativePort({action:'committed',store:path.join(local,'native-store'),operation});
const files={};
function file(name,raw){files[name]=Buffer.from(raw).toString('base64');return bind(name,Buffer.from(raw));}
const canon=b=>({path:b.ref,sha256:b.sha256,bytes:Number(b.bytes)});
const original=f=>file(path.relative(root,f),readFileSync(f));
const materials=new Map();
function capture(b){const k=b.ref??b.path;return Buffer.from(files[k],'base64');}
const carriers={};
for(const v of ['v1','v2']){
 const base=path.join(root,'authority/artifact-types/definition',v);
 const schema=original(path.join(base,'schema.json')),generator=original(path.join(base,'generator.py'));
 const descriptor=original(v==='v1'?path.join(base,'candidates/0002-post-foundation-01/artifact.json'):path.join(base,'artifact.json'));
 // v1's own historical admission is its qualified authority, not v2's successor admission.
 const admissionFile=v==='v1'?path.join(root,'docs/decisions/0015-definition-v1-admission/decision.json'):path.join(root,'authority/admissions/definition-complete-lab-model/v1/artifact-type-admission.json');
 carriers['cal.artifact-type.definition/'+v]={schema,generator,descriptor,admission:original(admissionFile)};
}
trust.carriers=carriers;
const previous=json(path.join(root,'authority/definitions/registry.json'));
const entries=[];


const historical=json(path.join(here,'historical-decisions.json'));
historical['CAL-DECISION-0074B-ADMISSION-TRANSACTION-DEFINITION-ADMISSION']='authority/admissions/governance-transaction-surface/v1/instances/governance/decisions/decision-0074b.json';
const renderHome=path.join(local,'projections');mkdirSync(renderHome,{recursive:true});
function project(raw,carrier,name){
 const input=path.join(renderHome,'definition.json'),output=path.join(renderHome,'DEFINITION.md');
 writeFileSync(input,raw);
 const run=spawnSync('python3',['-B',path.join(root,'authority/artifact-types/definition',carrier,'generator.py'),input,'--output',output],{encoding:'utf8'});
 assert.equal(run.status,0,run.stderr);
 return file('projections/'+name+'.md',readFileSync(output));
}
for(const [i,e] of previous.entries.entries()){
 const raw=readFileSync(path.join(root,e.path));assert.equal(digest(raw),e.sha256);
 const originalDecision=original(path.join(root,historical[e.admission_decision_ref]));
 const owner=file('dispositions/historical/'+e.admission_decision_ref+'.json',bytes({
 decision_ref:e.admission_decision_ref,original_decision:canon(originalDecision)}));
 const c=carriers['cal.artifact-type.definition/v1'];
 entries.push({definition_id:e.definition_id,version:e.version,body:canon(file(e.path,raw)),
 carrier:{ref:'cal.artifact-type.definition/v1',descriptor:canon(c.descriptor),admission:canon(c.admission)},
 schema:canon(c.schema),generator:canon(c.generator),owner_disposition:canon(owner),
 standing:previous.current_lookup[e.definition_id]===e.definition_id+'@'+e.version?'admitted-current':'admitted-retained',
 projection:canon(project(raw,'v1',String(i))),predecessor:null});
}
for(const [i,x] of decisions.entries()){
 const c=carriers['cal.artifact-type.definition/v2'];
 entries.push({definition_id:x.body.definition_id,version:x.body.version,body:canon(file(x.decision.original.path,x.original)),
 carrier:{ref:'cal.artifact-type.definition/v2',descriptor:canon(c.descriptor),admission:canon(c.admission)},
 schema:canon(c.schema),generator:canon(c.generator),owner_disposition:canon(original(x.filename)),standing:'admitted-current',
 projection:canon(project(x.original,'v2','accepted-'+i)),predecessor:null});
}
const lookup={...previous.current_lookup};
for(const x of decisions)lookup[x.body.definition_id]=x.body.definition_id+'@'+x.body.version;
const publicationDecision={schema_version:'lab-exact-publication-decision/v1',
 decision_ref:'decision:shared-definitions-records-0076:publication',authorization,
 source_cut:cut,workspace,accepted:decisions.map(x=>binding(x.filename)),
 registry_contract:binding(path.join(here,'registry-admission.json')),
 predecessor:binding(path.join(root,'authority/definitions/registry.json')),
 effects:['admit-five-exact-definitions','admit-registry-v2','activate-central-internal-workflow'],
 retained_versions:189,versions:194,current:188};
put(path.join(here,'publication-decision.json'),publicationDecision);
const owner=original(path.join(here,'publication-decision.json'));
const predecessor=bind('registry.json',readFileSync(path.join(root,'authority/definitions/registry.json')));
const registry={schema_version:'cyberalchemy-lab-definition-registry/v2',artifact_type_ref:'cal.artifact-type.definition-registry/v2',
 expected_predecessor:canon(predecessor),publication_decision:canon(owner),entries,current_lookup:lookup};
const approved=entries.slice(previous.entries.length).map(e=>({version:e.definition_id+'@'+e.version,postimage_sha256:digest(bytes(e))}));
assert.deepEqual(registryAssessment(previous,registry,capture,carriers,approved),{retained:189,versions:194,current:188});
const reg=file('registry.json',bytes(registry));
const index=file('index.json',bytes({current_lookup:lookup,definitions:entries.map(e=>({version:e.definition_id+'@'+e.version,body:e.body,projection:e.projection})).sort((a,b)=>a.version.localeCompare(b.version))}));
const source=file('source.json',bytes({reader_protocol:'snapshot-selector/v1',readers:trust.required_readers,
 native_transaction:{digest:committed.transaction,targets:committed.targets},approved_changes:approved}));
const proposalBinding=original(path.join(here,'proposal.json'));
const permission=original(path.join(here,'approval.json'));
original(path.join(here,'authorization.json'));original(path.join(here,'registry-admission.json'));
original(path.join(here,'registry-descriptor.json'));original(path.join(here,'role-assignment.json'));
const targetBodies=decisions.map(x=>bind(x.decision.original.path,x.original));
targetBodies.push(original(path.join(here,'registry-descriptor.json')));
put(path.join(here,'trust.json'),trust);
const snapshots=new Snapshots(database);
const staged=snapshots.stage(workspace,operation,cut,files);
const observed=snapshots.current(workspace);snapshots.close();
const selector=bind('selector',bytes(observed));
const typeReview={target:targetBodies.at(-1),expected_owner:'role:artifact-type-owner',scope,source_cut:cut,source_current:true,
 fields_receipt:binding(path.join(here,'receipts/native-review.json')),consumer_bindings_current:true,
 disposition:{target:targetBodies.at(-1),previous:null,owner:'role:artifact-type-owner',scope,source_cut:cut,outcome:'Accepted',role_assignment:authorization,
 verification_receipt:binding(path.join(here,'registry-admission.json'))}};
const value={workspace,source_cut:cut,expected_selector:selector,observed_selector:selector,expected_registry:predecessor,
 observed_registry:predecessor,proposed_registry:reg,expected_targets:committed.targets_digest,proposal:proposalBinding,
 operation_ref:operation,target_bodies:targetBodies,semantic_reviews:[...reviews,typeReview],registry_contract_current:true,
 registry_contract:bind('registry-contract',descriptor),permission,permission_proposal:proposalBinding,native_head:proposal.expected_head,
 native_receipt:{head:proposal.expected_head,workspace,operation_ref:operation,proposal:proposalBinding,targets:committed.targets_digest,
 source_cut:cut,outcome:'Committed',proof:committed.original_receipt},publication_receipt:null,published_postimage:null,observed_receipt:null,
 bundle:staged.binding,bundle_review:proof(staged.binding,'closed-publication-bundle',owner),
 canonical_permission:proof(staged.binding,'canonical-publication',owner),
 snapshot:{bundle:staged.binding,operation,workspace,cut,expected_head:proposal.expected_head,predecessor,expected_selector:selector,
 registry:reg,index,source,targets:committed.targets_digest,draft_only:true,
 readers:proof(source,'qualified-readers',qualification),migration:proof(reg,'registry-migration',owner)}};
const request=packet('PlanPublication',{value});
request.files=files;request.native_store=path.join(local,'native-store');
put(path.join(here,'publish.json'),request);
const published=await main(['publish','--file',path.join(here,'publish.json'),'--trust',path.join(here,'trust.json'),'--db',database]);
put(path.join(here,'receipts/publication.json'),published);
assert.equal((await main(['publish','--file',path.join(here,'publish.json'),'--trust',path.join(here,'trust.json'),'--db',database])).replayed,true);
const view=readPublishedCatalog(database,workspace);
assert.equal(view.entries.length,194);assert.equal(Object.keys(view.current_lookup).length,188);
const bundle=path.join(root,'authority/admissions/shared-definitions-records-0076');
mkdirSync(bundle,{recursive:true});
writeFileSync(path.join(bundle,'registry.json'),capture(reg));
writeFileSync(path.join(bundle,'index.json'),capture(index));
put(path.join(bundle,'snapshot-files.json'),files);
put(path.join(bundle,'bundle.json'),{schema_version:'lab-shared-records-admission-bundle/v1',decision_ref:'decision:shared-definitions-records-0076',
 authorization,publication_decision:binding(path.join(here,'publication-decision.json')),registry:binding(path.join(bundle,'registry.json')),
 snapshot_files:binding(path.join(bundle,'snapshot-files.json')),publication_receipt:binding(path.join(here,'receipts/publication.json')),
 selector:published.selected,counts:{retained:189,versions:194,current:188}});
put(path.join(here,'decision.json'),{schema_version:'cyberalchemy-lab-shared-records-admission-decision/v1',
 decision_id:'CAL-DECISION-0076-SHARED-DEFINITIONS-RECORDS-ACTIVATION',decision_ref:'decision:shared-definitions-records-0076',
 status:'owner-admitted-and-activated',decision_source:{kind:'explicit-user-authorization',verbatim:auth.verbatim_user_authorization,
 principal_ref:auth.principal_ref},authorization,bundle:binding(path.join(bundle,'bundle.json')),
 effects:{definitions_admitted:5,registry_contracts_admitted:1,shared_runtime_activations:1,product_runtime_copies:0,external_effects:0},
 claim_ceiling:'Local shared Lab workflow and canonical internal snapshot only. Existing frozen native profiles remain historical compatibility baselines.'});
put(path.join(here,'receipts/application.json'),{status:'PASS',decision:binding(path.join(here,'decision.json')),
 native_transaction:committed.transaction,source_cut:cut,publication:published.selected,versions:194,current:188,retained:189});
console.log(JSON.stringify({status:'APPLIED',versions:194,current:188,retained:189,selector:published.selected}));
