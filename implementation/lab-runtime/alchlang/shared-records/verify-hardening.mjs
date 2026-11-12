import assert from 'node:assert/strict';
import {readFileSync,writeFileSync,mkdtempSync,mkdirSync,symlinkSync,readdirSync} from 'node:fs';
import path from 'node:path';
import {tmpdir} from 'node:os';
import {spawnSync} from 'node:child_process';
import {DatabaseSync,backup} from 'node:sqlite';
import {generateKeyPairSync} from 'node:crypto';
import {fixture as f} from './verify-publication.mjs';
import {enforceManagedContext} from './managed-context.mjs';
import {main} from './cli.mjs';
import {publish} from './runtime.mjs';
import {registryAssessment,nativePort,impactClosure,independentAssessment} from './ports.mjs';
import {Snapshots,bind} from './snapshots.mjs';
import {Journal} from './journal.mjs';
import {captureImplementation,verifyImplementation,loadTrust} from './implementation.mjs';
import {deriveCarryForward} from './carry-forward.mjs';
import {verifyOperationalReadiness} from './readiness.mjs';
import {captureRecovery,restoreRecovery} from './recovery.mjs';
import {signPacket} from './security.mjs';
import {digest} from './verified-projection.mjs';
import {node} from './build.mjs';
const home=mkdtempSync(path.join(tmpdir(),'lab-ten-findings-')),checks=[];
const plan=path.join(f.root,'work/plans/shared-definitions-records-r5');
const bytes=x=>Buffer.from(JSON.stringify(x)),load=file=>JSON.parse(readFileSync(file));
const put=(name,value)=>{const file=path.join(home,name);writeFileSync(file,JSON.stringify(value,null,2));return file;};
async function check(name,fn){await fn();checks.push(name);console.log('PASS '+name);}
function packet(operation,value,trust=f.trust,privateKey=f.privatePem,issuer='principal:publisher',scope=f.workspace,cut=f.cut){
 const artifact=bytes({operation,scope,cut,implementation:trust.implementation.digest,input:{value}});
 return {operation,scope,cut,artifact:artifact.toString('base64'),receipt:signPacket(bytes({version:1,predicate:'verified-planning-input',operation,scope,cut,artifact:{sha256:digest(artifact),bytes:artifact.length}}),issuer,privateKey)};
}
async function copied(source,name){const db=new DatabaseSync(source,{readOnly:true});try{await backup(db,path.join(home,name));}finally{db.close();}return path.join(home,name);}
function readMaterial(files,binding){const raw=Buffer.from(files[binding.ref??binding.path]??'','base64');assert.equal(digest(raw),binding.sha256);assert.equal(raw.length,Number(binding.bytes));return raw;}
function ref(files,name,value){const raw=Buffer.isBuffer(value)?value:bytes(value);files[name]=raw.toString('base64');return bind(name,raw);}
function rebindRequest(files,value,database){
 const snapshots=new Snapshots(database,{trust:f.trust});
 const staged=snapshots.stage(f.workspace,value.operation_ref,f.cut,files);snapshots.close();
 value.proposed_registry=bind('registry.json',Buffer.from(files['registry.json'],'base64'));
 value.snapshot.registry=value.proposed_registry;value.snapshot.index=bind('index.json',Buffer.from(files['index.json'],'base64'));
 value.snapshot.source=bind('source.json',Buffer.from(files['source.json'],'base64'));
 value.snapshot.migration.subject=value.proposed_registry;value.snapshot.readers.subject=value.snapshot.source;
 value.bundle=staged.binding;value.snapshot.bundle=staged.binding;value.bundle_review.subject=staged.binding;value.canonical_permission.subject=staged.binding;
 return {...f.request,...packet('PlanPublication',value),files};
}
await check('F01-central-valid-signed-apply-cannot-bypass-construction',async()=>{
 for(const prefix of [['--store',path.join(f.home,'store')],['--store='+path.join(f.home,'store')],['--repo='+f.root,'--store='+path.join(f.home,'store')]]){
  const child=spawnSync(node,[path.join(f.root,'implementation/lab-runtime/lab.mjs'),...prefix,'apply',path.join(f.home,'proposal.json'),path.join(f.home,'approval.json')],{encoding:'utf8'});
  assert.equal(child.status,2);assert(child.stderr.includes('shared-native-apply-required'));
 }
 const abbreviated=spawnSync(node,[path.join(f.root,'implementation/lab-runtime/lab.mjs'),'--st',path.join(f.home,'store'),'apply',path.join(f.home,'proposal.json'),path.join(f.home,'approval.json')],{encoding:'utf8'});
 assert.equal(abbreviated.status,2);assert(abbreviated.stderr.includes('unsupported-global-option'));
 const keygen=spawnSync(node,[path.join(f.root,'implementation/lab-runtime/lab.mjs'),'keygen','--private','apply','--public','temporary.pub'],{encoding:'utf8',cwd:home});
 assert.equal(keygen.status,0,keygen.stderr);
});
await check('F02-omitted-native-definition-refused-at-closure-guard',async()=>{
 const files=structuredClone(f.files),value=structuredClone(f.value);
 const reg=JSON.parse(Buffer.from(files['registry.json'],'base64'));reg.entries=[];reg.current_lookup={};ref(files,'registry.json',reg);
 ref(files,'index.json',{current_lookup:{},definitions:[]});
 const source=JSON.parse(Buffer.from(files['source.json'],'base64'));source.approved_changes=[];ref(files,'source.json',source);
 const database=path.join(home,'omitted.sqlite');
 await assert.rejects(()=>publish(rebindRequest(files,value,database),f.trust,database),/registry-effects-not-closed/);
});
await check('F02-extra-registry-addition-without-native-effect-is-refused',async()=>{
 const local=structuredClone(f.files),value=structuredClone(f.value);
 const extra={...structuredClone(f.definition),definition_id:f.definition.definition_id+'-extra',term:f.definition.term+' Extra'};
 extra.index_entry.entry_id=extra.definition_id+'@'+extra.version;
 const body=ref(local,'extra-definition.json',extra);
 const auth=ref(local,'extra-authorization.json',{authorized:true,scope:'isolated-regression-only',accepted_definitions:[{version:extra.definition_id+'@'+extra.version,source:f.canonical(body)}]});
 const role=ref(local,'extra-role.json',{role_ref:extra.semantic_owner_ref,principal_ref:'fixture:publisher',basis:auth});
 const owner=ref(local,'extra-decision.json',{decision_ref:'decision:fixture:extra',target:extra.definition_id+'@'+extra.version,original:f.canonical(body),outcome:'Accepted',
 owner:extra.semantic_owner_ref,principal_ref:'fixture:publisher',scope:extra.scope.authority_scope_ref,source_cut:f.cut,authorization:auth,role_assignment:role});
 const input=put('extra-definition.json',extra),output=path.join(home,'extra-DEFINITION.md');
 const rendered=spawnSync('python3',['-B',path.join(f.root,'authority/artifact-types/definition/v2/generator.py'),input,'--output',output],{encoding:'utf8'});assert.equal(rendered.status,0,rendered.stderr);
 const entry={...structuredClone(f.entry),definition_id:extra.definition_id,version:extra.version,body:f.canonical(body),owner_disposition:f.canonical(owner),projection:f.canonical(ref(local,'extra-DEFINITION.md',readFileSync(output)))};
 const registry=JSON.parse(Buffer.from(local['registry.json'],'base64'));registry.entries.push(entry);registry.current_lookup[extra.definition_id]=extra.definition_id+'@'+extra.version;ref(local,'registry.json',registry);
 ref(local,'index.json',{current_lookup:registry.current_lookup,definitions:registry.entries.map(e=>({version:e.definition_id+'@'+e.version,body:e.body,projection:e.projection})).sort((a,b)=>a.version.localeCompare(b.version))});
 const source=JSON.parse(Buffer.from(local['source.json'],'base64'));source.approved_changes.push({version:extra.definition_id+'@'+extra.version,postimage_sha256:digest(bytes(entry))});ref(local,'source.json',source);
 const database=path.join(home,'extra.sqlite');
 await assert.rejects(()=>publish(rebindRequest(local,value,database),f.trust,database),/registry-effects-not-closed/);
});
await check('F03-retained-disposition-cannot-be-replaced-by-missing-artifact',async()=>{
 const previous=JSON.parse(Buffer.from(f.files['registry.json'],'base64')),proposed=structuredClone(previous);
 proposed.entries[0].owner_disposition={path:'missing-owner.json',sha256:'0'.repeat(64),bytes:0};
 assert.throws(()=>registryAssessment(previous,proposed,b=>readMaterial(f.files,b),f.trust.carriers,[]),/material|disposition/);
});
await check('F05-edited-adapter-manifest-refuses-execution',async()=>{
 const invalid=structuredClone(f.trust.implementation);
 const name=Object.keys(invalid.manifest.files)[0];invalid.manifest.files[name]='0'.repeat(64);
 invalid.digest=digest(bytes(invalid.manifest));
 assert.throws(()=>verifyImplementation(invalid),/implementation-source-drift/);
 const database=path.join(home,'drift.sqlite');
 await assert.rejects(()=>publish(f.request,{...f.trust,implementation:invalid},database),/implementation-source-drift/);
});
await check('F05-partial-manifest-cannot-select-only-convenient-files',async()=>{
 const incomplete=structuredClone(f.trust.implementation);
 delete incomplete.manifest.files[Object.keys(incomplete.manifest.files)[0]];
 incomplete.digest=digest(bytes(incomplete.manifest));
 assert.throws(()=>verifyImplementation(incomplete),/implementation-closure-incomplete/);
});
await check('F05-managed-resources-reject-substituted-trust-even-through-alias',async()=>{
 const database=await copied(f.database,'managed-copy.sqlite');
 const alias=path.join(home,'managed-alias.sqlite');symlinkSync(database,alias);
 const configured={execution_selection:{},database,journal:path.join(home,'managed-journal.sqlite'),
 native_store:path.join(f.home,'store'),trust:put('selected-resource-trust.json',f.trust)};
 assert.throws(()=>enforceManagedContext('publish',{db:alias,trust:put('substituted-trust.json',f.trust)},f.request,configured,f.trust),/managed-resource-trust-mismatch/);
 const altered={...f.request,native_store:path.join(home,'unrelated-native-store')};
 const value=structuredClone(f.value);value.operation_ref+='-new';
 altered.artifact=Buffer.from(JSON.stringify({input:{value}})).toString('base64');
 assert.throws(()=>enforceManagedContext('publish',{db:database,trust:configured.trust},altered,configured,f.trust),/managed-publication-native-store-mismatch/);
});
await check('F06-corrupt-publication-receipt-refuses-inspection-and-replay',async()=>{
 const database=await copied(f.database,'bad-receipt.sqlite'),db=new DatabaseSync(database);
 const row=db.prepare('SELECT receipt FROM publications').get(),receipt=JSON.parse(row.receipt);receipt.selected.digest='0'.repeat(64);
 db.prepare('UPDATE publications SET receipt=?').run(JSON.stringify(receipt));db.close();
 await assert.rejects(()=>publish(f.request,f.trust,database),/evidence-corrupt|receipt-mismatch/);
 const snapshots=new Snapshots(database,{readOnly:true,trust:f.trust});
 assert.throws(()=>snapshots.inspectPublication(f.workspace,f.proposal.proposal_id),/evidence-corrupt|receipt-mismatch/);snapshots.close();
});
const activeRaw=load(path.join(f.root,'implementation/lab-runtime/shared-workflow.json'));
const currentPlan=path.dirname(path.resolve(f.root,activeRaw.trust));
const activeTrust=path.resolve(f.root,activeRaw.trust),rootTrust=loadTrust(activeTrust);
const active={...activeRaw,root:f.root,trust:activeTrust,database:path.join(f.root,activeRaw.database),journal:path.join(f.root,activeRaw.journal),native_store:path.join(f.root,activeRaw.native_store)};
await check('F07-erased-journal-authentication-evidence-refuses-completion',async()=>{
 const database=await copied(active.journal,'bad-journal.sqlite'),db=new DatabaseSync(database);db.exec("UPDATE commands SET evidence='{}'");db.close();
 const journal=new Journal(database,{readOnly:true,trust:rootTrust});
 assert.throws(()=>journal.inspect(active.workspace,'join:shared-definitions-records-0076'),/authentication-evidence/);journal.close();
});
await check('F07-forged-signature-refuses-even-with-recomputed-checksum',async()=>{
 const database=await copied(active.journal,'bad-journal-signature.sqlite'),db=new DatabaseSync(database);
 const row=db.prepare('SELECT rowid,evidence FROM commands LIMIT 1').get();const evidence=JSON.parse(row.evidence);evidence.receipt.signature='0'.repeat(128);const raw=JSON.stringify(evidence);
 db.prepare('UPDATE commands SET evidence=?,evidence_digest=? WHERE rowid=?').run(raw,digest(Buffer.from(raw)),row.rowid);db.close();
 const journal=new Journal(database,{readOnly:true,trust:rootTrust});
 await assert.rejects(()=>journal.verifyHistory(active.workspace,'join:shared-definitions-records-0076'),/signature-invalid/);journal.close();
});
const corrected=load(path.join(currentPlan,'TRANSFER-REQUEST.json'));
await check('F04-carry-forward-preserves-original-owner-cuts',async()=>{
 const value=await deriveCarryForward(corrected.carry_forward,rootTrust,active.database);
 const original=JSON.parse(Buffer.from(corrected.carry_forward.original_construction.artifact,'base64')).input.value;
 assert.deepEqual(value.original,original);assert(value.reviews.every(r=>r.original_cut===original.source_cut&&r.current_cut!==r.original_cut));
});
await check('F04-relabelled-original-owner-cut-is-refused',async()=>{
 const scope=active.workspace,cut=corrected.carry_forward.original_construction.cut;
 const {privateKey,publicKey}=generateKeyPairSync('ed25519');const trust=structuredClone(rootTrust);
 const issuer='fixture:cut-tamper';trust.principals[issuer]={public_key:publicKey.export({format:'pem',type:'spki'}),grants:[{predicate:'verified-planning-input',operation:'AssessConstructionEntry',scope,cut}]};
 const value=structuredClone(corrected.construction?JSON.parse(Buffer.from(corrected.construction.artifact,'base64')).input.value.original:JSON.parse(Buffer.from(corrected.carry_forward.original_construction.artifact,'base64')).input.value);
 value.definitions[0].disposition.source_cut=corrected.proposal.source_snapshot_digest;
 const request={...corrected.carry_forward,original_construction:packet('AssessConstructionEntry',value,trust,privateKey.export({format:'pem',type:'pkcs8'}),issuer,scope,cut)};
 await assert.rejects(()=>deriveCarryForward(request,trust,active.database),/original-review-receipt-context-mismatch/);
});
await check('F09-incomplete-consumer-universe-cannot-claim-closure',async()=>{
 const universe=load(rootTrust.consumer_universe.path);
 const file=put('incomplete-impact.json',{root:universe.subjects[0].ref,manifest:{...universe,subjects:universe.subjects.slice(0,1)}});
 await assert.rejects(()=>main(['impact','--file',file,'--trust',activeTrust]),/consumer-universe-mismatch/);
});
await check('F09-real-independent-checks-reject-changed-generation-output',async()=>{
 const assessment=load(path.join(currentPlan,'operational/assessment.json')),material=rootTrust.materials[assessment.output.ref];
 const generated=load(material.path);const registry=JSON.parse(Buffer.from(generated.registry.bytes_base64,'base64'));registry.entries.pop();generated.registry.bytes_base64=bytes(registry).toString('base64');
 const file=put('changed-output.json',generated),output=bind('candidate:changed-generation',readFileSync(file));
 const materials={...rootTrust.materials,[output.ref]:{path:file,sha256:output.sha256}};
 const result=independentAssessment(assessment.specifications,output,rootTrust.executors,materials);
 assert(result.some(r=>!r.passed));assert(result.some(r=>r.outcome==='Failed'));
});
await check('F10-missing-resources-cannot-report-ready',async()=>{
 await assert.rejects(()=>verifyOperationalReadiness({...active,database:path.join(home,'absent.sqlite')},rootTrust),/shared-resource-missing/);
});
let restored;
await check('F10-recovery-restores-verified-data-without-keys-or-runtime-copies',async()=>{
 const nativeFiles={};
 for(const [prefix,store]of [['native-store',path.resolve(f.root,activeRaw.historical_publication_store)],['current-store',active.native_store]]){
  for(const name of ['config.json','baseline.json','HEAD.json',...readdirSync(path.join(store,'transactions')).filter(n=>/^[0-9]{10}\.json$/.test(n)).map(n=>'transactions/'+n)])nativeFiles[prefix+'/'+name]=readFileSync(path.join(store,name)).toString('base64');
 }
 const archive=captureRecovery(active,nativeFiles),binding={sha256:digest(archive),bytes:archive.length,uncompressed_bytes:archive.readUInt32LE(archive.length-4)};
 restored=await restoreRecovery(archive,binding,path.join(home,'restored'),active,rootTrust);
 const ready=await verifyOperationalReadiness({...active,...restored},rootTrust);assert.equal(ready.status,'ready');
 const original=Buffer.from(nativeFiles['current-store/transactions/0000000001.json'],'base64');
 assert.equal(digest(readFileSync(path.join(restored.native_store,'transactions/0000000001.json'))),digest(original));
 await assert.rejects(()=>restoreRecovery(archive,{...binding,uncompressed_bytes:512*1024*1024+1},path.join(home,'bad-limit'),active,rootTrust),/limit-invalid/);
 await assert.rejects(()=>restoreRecovery(archive,{...binding,uncompressed_bytes:binding.uncompressed_bytes+1},path.join(home,'bad-inflated-size'),active,rootTrust),/size-mismatch/);
 const bad=Buffer.from(archive);bad[0]^=1;
 await assert.rejects(()=>restoreRecovery(bad,binding,path.join(home,'bad-restore'),active,rootTrust),/binding-mismatch/);
 await assert.rejects(()=>restoreRecovery(archive,binding,path.join(home,'restored'),active,rootTrust),/must-be-new/);
});
// A complete live successor -> unrelated publication journey follows.
const files=structuredClone(f.files),db=f.database;
function originalOwner(bodyBinding,body,decisionRef,label){
 const authorization=ref(files,label+'-authorization.json',{authorized:true,scope:'isolated-regression-only',accepted_definitions:[{version:body.definition_id+'@'+body.version,source:f.canonical(bodyBinding)}]});
 const role=ref(files,label+'-role.json',{role_ref:body.semantic_owner_ref,principal_ref:'fixture:publisher',basis:authorization});
 return ref(files,label+'-decision.json',{decision_ref:decisionRef,target:body.definition_id+'@'+body.version,original:f.canonical(bodyBinding),outcome:'Accepted',
 owner:body.semantic_owner_ref,principal_ref:'fixture:publisher',scope:body.scope.authority_scope_ref,source_cut:f.cut,authorization,role_assignment:role});
}
function prepareNative(kind,prefix,target){
 const result=spawnSync('python3',['-B',path.join(plan,'regression-native.py')],{input:JSON.stringify({home:f.home,kind,prefix,target}),encoding:'utf8',maxBuffer:8*1024*1024});
 assert.equal(result.status,0,result.stderr);return JSON.parse(result.stdout);
}
function reviewed(target,label,bodyBinding){
 const body=target.record,scope=body.scope?.authority_scope_ref??f.workspace,owner=body.semantic_owner_ref??body.owner_ref;
 const review=ref(files,label+'-review.json',{target:target.version_ref,scope,owner,source_cut:f.cut,observed_schema:'original-native-review'});
 return {target:bodyBinding,expected_owner:owner,scope,source_cut:f.cut,source_current:true,fields_receipt:review,consumer_bindings_current:true,
 disposition:{target:bodyBinding,previous:null,owner,scope,source_cut:f.cut,outcome:'Accepted',role_assignment:review,verification_receipt:review}};
}
async function guardedApply(prepared,prefix){
 const proposal=prepared.proposal,approval=prepared.approval,target=proposal.targets[0];
 const body=ref(files,prefix+'-body.json',target.record);
 let owner;
 if(target.category==='definition')owner=originalOwner(body,target.record,target.decision_ref,prefix+'-semantic');
 f.trust.materials??={};
 for(const name of [body.ref,...(owner?[owner.ref,prefix+'-semantic-authorization.json',prefix+'-semantic-role.json']:[])]){
   const raw=Buffer.from(files[name],'base64'),file=put(name,JSON.parse(raw));
   f.trust.materials[name]={path:file,sha256:digest(raw)};
   writeFileSync(file,raw);
 }
 const source=JSON.parse(Buffer.from(f.nativeRequest.construction.artifact,'base64')).input.value;
 const selection=ref(files,prefix+'-selection.json',{targets:[body]});
 const proof={...source.selection_review,subject:selection};
 const value={...source,selected_targets:[body],admitted_targets:[],review_targets:[body],selection,selection_review:proof,
 definitions:[{...reviewed(target,prefix,body),...(owner?{disposition:{...reviewed(target,prefix,body).disposition,verification_receipt:owner}}:{})}],definition_targets:[body],definition_selection_receipt:selection,
 permission:bind(prefix+'-approval.json',readFileSync(path.join(f.home,prefix+'-approval.json')))};
 const request={...f.nativeRequest,proposal,approval,approval_artifact:readFileSync(path.join(f.home,prefix+'-approval.json')).toString('base64'),construction:packet('AssessConstructionEntry',value)};
 const trustFile=put('lifecycle-trust.json',f.trust),file=put(prefix+'-apply.json',request);
 await main(['native-apply','--file',file,'--trust',trustFile]);
 return {owner,native:nativePort({action:'committed',store:path.join(f.home,'store'),operation:proposal.proposal_id}),target,body,
 proposal:ref(files,prefix+'-proposal.json',readFileSync(path.join(f.home,prefix+'-proposal.json'))),
 approval:ref(files,prefix+'-approval.json',readFileSync(path.join(f.home,prefix+'-approval.json')))};
}
function proof(subject,predicate,issuer='principal:publisher'){return {...f.proof(subject,predicate),issuer};}
async function publishNext(current,prepared,registry,prefix,lifecycle=[]){
 const snapshots=new Snapshots(db,{readOnly:true,trust:f.trust});const selected=snapshots.current(f.workspace);
 const previous=bind('registry.json',snapshots.material(selected.digest,'registry.json').bytes);snapshots.close();
 registry.expected_predecessor=f.canonical(previous);
 const owner=ref(files,prefix+'-publication.json',{scope:'isolated-regression-only',operation:prepared.native.proposal.proposal_id});
 registry.publication_decision=f.canonical(owner);
 const index={current_lookup:registry.current_lookup,definitions:registry.entries.map(e=>({version:e.definition_id+'@'+e.version,body:e.body,projection:e.projection})).sort((a,b)=>a.version.localeCompare(b.version))};
 const oldEntries=new Map(current.entries.map(e=>[e.definition_id+'@'+e.version,e]));
 const changes=registry.entries.filter(e=>!oldEntries.has(e.definition_id+'@'+e.version)||oldEntries.get(e.definition_id+'@'+e.version).standing!==e.standing)
 .map(e=>({version:e.definition_id+'@'+e.version,postimage_sha256:digest(bytes(e))}));
 ref(files,'registry.json',registry);ref(files,'index.json',index);
 ref(files,'source.json',{reader_protocol:'snapshot-selector/v1',readers:f.trust.required_readers,native_transaction:{digest:prepared.native.transaction,targets:prepared.native.targets},approved_changes:changes,lifecycle});
 const selector=bind('selector',bytes({...selected}));
 const value={...structuredClone(f.value),expected_selector:selector,observed_selector:selector,expected_registry:previous,observed_registry:previous,
 expected_targets:prepared.native.targets_digest,proposal:prepared.proposal,operation_ref:prepared.native.proposal.proposal_id,
 target_bodies:[prepared.body],semantic_reviews:[reviewed(prepared.target,prefix+'-publication',prepared.body)],permission:prepared.approval,permission_proposal:prepared.proposal,
 native_head:prepared.native.expected_head,native_receipt:{head:prepared.native.expected_head,workspace:f.workspace,
 operation_ref:prepared.native.proposal.proposal_id,proposal:prepared.proposal,targets:prepared.native.targets_digest,source_cut:f.cut,outcome:'Committed',proof:prepared.native.original_receipt}};
 value.snapshot={...value.snapshot,operation:value.operation_ref,expected_head:value.native_head,predecessor:previous,expected_selector:selector,targets:value.expected_targets};
 return publish(rebindRequest(files,value,db),f.trust,db);
}
let successorRegistry;
await check('F08-real-successor-publication-preserves-original-lineage',async()=>{
 const initial=JSON.parse(Buffer.from(f.files['registry.json'],'base64'));
 const prepared=await guardedApply(prepareNative('revise','successor',f.proposal.targets.find(t=>t.category==='definition')),'successor');
 const next={...structuredClone(f.entry),definition_id:prepared.target.record.definition_id,version:prepared.target.record.version,body:f.canonical(prepared.body),
 owner_disposition:f.canonical(prepared.owner),predecessor:f.entry.body};
 const input=put('successor-definition.json',prepared.target.record),output=path.join(home,'successor-DEFINITION.md');
 const rendered=spawnSync('python3',['-B',path.join(f.root,'authority/artifact-types/definition/v2/generator.py'),input,'--output',output],{encoding:'utf8'});
 assert.equal(rendered.status,0,rendered.stderr);next.projection=f.canonical(ref(files,'successor-DEFINITION.md',readFileSync(output)));
 const retained={...structuredClone(f.entry),standing:'admitted-retained'};
 successorRegistry={...structuredClone(initial),entries:[retained,next],current_lookup:{[next.definition_id]:next.definition_id+'@'+next.version}};
 const oldBody={ref:f.entry.body.path,sha256:f.entry.body.sha256,bytes:String(f.entry.body.bytes)};
 const registryBefore=ref(files,'observed-registry-before-successor.json',Buffer.from(f.files['registry.json'],'base64'));
 const consumers=[{ref:'old-definition',binding:oldBody,dependencies:[]},{ref:'selected-registry',binding:registryBefore,dependencies:['old-definition']}];
 for(const [reader,file]of [
  ['integration-reader',path.join(f.root,'implementation/lab-runtime/alchlang/shared-records/verify-publication.mjs')],
  ['lab.catalog-reader',path.join(f.root,'implementation/lab-runtime/alchlang/shared-records/catalog.mjs')],
  ['define.catalog-reader',path.join(f.root,'workspaces/products/define/implementation/cli/alchlang/preparation/cli.mjs')]]){
  consumers.push({ref:reader,binding:ref(files,'consumer-'+reader+'.source',readFileSync(file)),dependencies:['selected-registry']});
 }
 const cursorDb=new Snapshots(db,{readOnly:true,trust:f.trust}),selected=cursorDb.current(f.workspace);cursorDb.close();
 const universe={scope:f.workspace,source_cut:f.cut,cursor:'snapshot:'+selected.revision+':'+selected.digest,unresolved:0,subjects:consumers};
 const manifest=ref(files,'observed-consumers.json',universe);
 for(const [index,subject]of consumers.entries()){
  const raw=readMaterial(files,subject.binding),file=path.join(home,'consumer-material-'+index);writeFileSync(file,raw);
  f.trust.materials[subject.binding.ref]={path:file,sha256:subject.binding.sha256};
 }
 const universeFile=put('qualified-lifecycle-universe.json',universe);
 f.trust.consumer_universe={path:universeFile,sha256:digest(readFileSync(universeFile))};
 const closure=await main(['impact','--file',put('lifecycle-impact.json',{root:'old-definition'}),'--trust',put('lifecycle-impact-trust.json',f.trust),'--db',db]);
 assert.deepEqual(closure.affected,['define.catalog-reader','integration-reader','lab.catalog-reader','old-definition','selected-registry']);
 const closureReceipt=ref(files,'observed-impact.json',closure);
 const scope=f.workspace,expected_owner=prepared.target.record.semantic_owner_ref;
 const currentBody={ref:f.entry.body.path,sha256:f.entry.body.sha256,bytes:String(f.entry.body.bytes)};
 const value={current:currentBody,reviewed_current:currentBody,operation:prepared.native.proposal.proposal_id,reviewed_operation:prepared.native.proposal.proposal_id,
 proposal:prepared.proposal,intent:'RepresentationUpgrade',reviewed_intent:'RepresentationUpgrade',successor:prepared.body,reviewed_successor:prepared.body,
 expected_owner,scope,source_cut:f.cut,closure_cut:f.cut,closure_receipt:closureReceipt,consumer_manifest:manifest,truncated:false,unresolved_dependents:'0',
 permission:prepared.approval,transition_review:proof(prepared.proposal,'lifecycle-review',expected_owner),impact_review:proof(prepared.proposal,'impact-closure'),
 permission_review:proof(prepared.proposal,'lifecycle-permission'),owner_review:{target:currentBody,previous:null,owner:expected_owner,scope,source_cut:f.cut,outcome:'Accepted',role_assignment:closureReceipt,verification_receipt:closureReceipt}};
 f.trust.principals['principal:publisher'].grants.push({predicate:'verified-planning-input',operation:'PlanLifecycleImpact',scope:f.workspace,cut:f.cut});
 const result=await publishNext(initial,prepared,successorRegistry,'successor',[packet('PlanLifecycleImpact',value)]);
 assert.equal(result.selected.revision,2);
});
await check('F08-unrelated-publication-after-upgrade-keeps-predecessor',async()=>{
 const prepared=await guardedApply(prepareNative('work','unrelated'),'unrelated');
 const result=await publishNext(successorRegistry,prepared,structuredClone(successorRegistry),'unrelated');
 assert.equal(result.selected.revision,3);
 const snapshots=new Snapshots(db,{readOnly:true,trust:f.trust});
 const reg=JSON.parse(snapshots.material(result.selected.digest,'registry.json').bytes);
 assert.deepEqual(reg.entries[1].predecessor,f.entry.body);snapshots.close();
 const historical=await publish(f.request,f.trust,db);assert.equal(historical.selected.revision,1);assert.equal(historical.replayed,true);
});
await check('F06-replay-requires-the-authenticated-parent-history',async()=>{
 const copiedDb=await copied(db,'missing-parent.sqlite'),copy=new DatabaseSync(copiedDb);
 copy.prepare('DELETE FROM publications WHERE operation=?').run(f.proposal.proposal_id);copy.close();
 const snapshots=new Snapshots(copiedDb,{readOnly:true,trust:f.trust});
 const current=snapshots.current(f.workspace),manifest=snapshots.material(current.digest,'registry.json').manifest;
 assert.throws(()=>snapshots.inspectPublication(f.workspace,manifest.operation),/parent-receipt-missing/);snapshots.close();
});
verifyImplementation(f.trust.implementation);
writeFileSync(path.join(import.meta.dirname,'HARDENING-VERIFICATION.json'),JSON.stringify({status:'PASS',implementation:f.trust.implementation.digest,findings:['F01','F02','F03','F04','F05','F06','F07','F08','F09','F10'],checks,check_count:checks.length,
 scope:'All adversarial mutations and new semantic versions use disposable stores; source carry-forward reads original live authority without modifying it.'},null,2)+'\n');
console.log(JSON.stringify({status:'PASS',check_count:checks.length,checks}));
