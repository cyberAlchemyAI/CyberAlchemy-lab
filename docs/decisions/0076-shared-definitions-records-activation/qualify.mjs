import assert from 'node:assert/strict';
import {readFileSync,writeFileSync,mkdirSync} from 'node:fs';
import {spawnSync} from 'node:child_process';
import path from 'node:path';
import {main} from '../../../implementation/lab-runtime/alchlang/shared-records/cli.mjs';
import {digest} from '../../../implementation/lab-runtime/alchlang/shared-records/verified-projection.mjs';
import {bind} from '../../../implementation/lab-runtime/alchlang/shared-records/snapshots.mjs';
import {Journal} from '../../../implementation/lab-runtime/alchlang/shared-records/journal.mjs';
import {activation} from '../../../implementation/lab-runtime/alchlang/shared-records/activation.mjs';
import {node} from '../../../implementation/lab-runtime/alchlang/shared-records/build.mjs';
const here=import.meta.dirname,root=path.resolve(here,'../../..'),active=activation({required:true});
const local=path.join(root,'.local/lab-runtime/shared/qualification');
mkdirSync(local,{recursive:true});
const key=path.join(process.env.HOME,'.config/cyberalchemy-lab/shared-records/operator.pem'),issuer='principal:lab-shared-operator';
const load=f=>JSON.parse(readFileSync(f)),bytes=v=>Buffer.from(JSON.stringify(v));
const put=(f,v)=>{mkdirSync(path.dirname(f),{recursive:true});writeFileSync(f,JSON.stringify(v,null,2)+'\n');};
const trust=load(active.trust),proposal=load(path.join(here,'proposal.json'));
const cut=proposal.source_snapshot_digest,workspace=active.workspace,scope=workspace;
const observed='qualified-operator-observation';
trust.selections??={};trust.schemas??={};
const operations=['ReviewFiveDefinitions','SelectCompatibility','AssessExecutionContext','PlanCreationRoute','PlanPublication',
 'PlanJoinContinuation','PlanLifecycleImpact','AssessConstructionEntry','AssessConstructionCompletion','AssessJoinTransition','InitializeJoin'];
for(const operation of operations){
 const fields=operation==='ReviewFiveDefinitions'?['expected','reviews']:['value'];
 const schema={type:'object',required:fields,additionalProperties:false,
 properties:Object.fromEntries(fields.map(field=>[field,field==='value'?{type:'object'}:{type:'array',minItems:5,maxItems:5}]))};
 if(operation==='InitializeJoin'){
  const protocol=load(path.join(root,'implementation/lab-runtime/alchlang/shared-records/contracts/verification-ports.schema.json'));
  Object.assign(schema,protocol.$defs.InitializeJoinInput);
 }
 const schemaPath=path.join(here,'issuance',operation+'.schema.json');put(schemaPath,schema);
 trust.schemas[operation]={path:schemaPath,sha256:digest(readFileSync(schemaPath))};
 const selection={version:1,operation,scope,input_schema:operation,
 requirements:[{predicate:observed,schema:operation,mappings:fields.map(field=>({from:'/'+field,to:'/'+field}))}]};
 const selectionPath=path.join(here,'issuance',operation+'.json');put(selectionPath,selection);
 trust.selections[operation]={path:selectionPath,sha256:digest(readFileSync(selectionPath))};
 for(const predicate of [observed,'verified-planning-input']){
  if(!trust.principals[issuer].grants.some(g=>g.operation===operation&&g.predicate===predicate))
   trust.principals[issuer].grants.push({predicate,operation,scope,cut});
 }
}
put(active.trust,trust);
const commands=[];
async function issued(operation,input){
 const file=path.join(local,'original.json');put(file,input);
 const attest=path.join(local,'attest.json');put(attest,{artifact:file,schema:operation,predicate:observed,operation,scope,cut});
 const original=await main(['attest','--file',attest,'--issuer',issuer,'--key',key]);
 const request={selection_id:operation,operation,scope,cut,originals:[original]};
 const issueFile=path.join(local,'issue.json');put(issueFile,request);
 const sealed=await main(['issue','--file',issueFile,'--issuer',issuer,'--key',key]);
 return {operation,scope,cut,...sealed};
}
const run='join:shared-definitions-records-0076';
const initialization=await issued('InitializeJoin',{value:{workspace,run_ref:run,original_operation:proposal.proposal_id,source_cut:cut}});
const initFile=path.join(local,'initialize.json');put(initFile,initialization);
await main(['join-init','--file',initFile]);
const inspect=()=>{const journal=new Journal(active.journal,{readOnly:true});try{return journal.inspect(workspace,run);}finally{journal.close();}};
let row=inspect();
const fileBinding=f=>bind(path.relative(root,f),readFileSync(f));
const auth=fileBinding(path.join(here,'authorization.json'));
const proof=(subject,predicate)=>({subject,scope,cut,predicate,issuer,policy:auth,proof:auth});
const steps=[
 ['SelectContext','Unobserved','target.json'],['PrepareDraft','Unobserved','proposal.json'],
 ['RequestReview','Unobserved','receipts/native-review.json'],['ObserveSemanticAcceptance','Committed','receipts/semantic-review.json'],
 ['ObservePermission','Committed','approval.json'],['ObserveNativeCommit','Committed','receipts/native-application.json'],
 ['PreparePublication','Unobserved','publication-decision.json'],['ObservePublication','Committed','receipts/publication.json'],
 ['RequestSourceTransition','Unobserved','../../..//authority/definitions/current.json'],
 ['ObserveSourceTransition','Committed','../../..//implementation/lab-runtime/shared-workflow.json']
];
for(const [signal,outcome,source] of steps.slice(row.events.length)){
 const past=fileBinding(path.resolve(here,source));
 const value={observed_operation:row.operation,observed_run:row.run,observed_phase:row.phase,
 observed_signal:signal,observed_outcome:outcome,
 join_key:{id:String(row.id),operation_key:String(row.id),run_ref:row.run,workspace,operation:row.operation,
 evidence:proof(bind(row.run,bytes({workspace,run:row.run,operation:row.operation,id:row.id})),'stable-join-identity')},
 phase:row.phase,signal,revision:String(row.revision),observed_revision:String(row.revision),cut,past_fact:past,
 evidence:proof(past,'join-transition')};
 const request={...await issued('AssessJoinTransition',{value}),command:'activation-0076:'+row.revision};
 const f=path.join(local,'transition.json');put(f,request);
 await main(['join-transition','--file',f]);
 commands.push(request);row=inspect();
}
assert.equal(row.phase,'Completed');assert.equal(row.events.length,10);
put(path.join(here,'receipts/join.json'),{status:'PASS',reconciliation:'Historical activation facts reconciled through their original artifacts; journal events do not assert earlier wall-clock execution.',run:row});
const status=await main(['status']);assert.equal(status.versions,194);assert.equal(status.current,188);
const catalog=await main(['catalog']);assert.equal(catalog.entries.length,194);
for(const item of load(path.join(here,'authorization.json')).accepted_definitions)
 assert(catalog.entries.some(e=>e.definition_id+'@'+e.version===item.version&&e.sha256===item.source.sha256));
const defineCli=path.join(root,'workspaces/products/define/implementation/cli/alchlang/runtime/cli.mjs');
function define(args){const p=spawnSync(node,[defineCli,...args],{encoding:'utf8',maxBuffer:16*1024*1024,timeout:300000});
 assert.equal(p.status,0,p.stderr+' '+p.stdout);return JSON.parse(p.stdout);}
const session=path.join(local,'define-session');
put(path.join(local,'define-start.json'),{session_id:'session:shared-lab-activation-0076',
 scope:{project:null,work:null,goal:'Verify the five owner-admitted definitions',originating_intent:'Activate the shared Lab definitions and records workflow',
 context_description:'Canonical Registry/v2 owner activation',consumer:'lab:shared-runtime',intended_use:'review-meanings'},
 request_revision:'1',request_lineage:{predecessor_package_binding:null,language_evidence_binding:null,field_supplement_binding:null},
 validation_scope:{required_checks:[],evidence_scope:'Canonical selected snapshot discovery',claim_ceiling:'Source discovery and verified replay; admission comes from the separate owner decision.'}});
define(['start','--work',session,'--file',path.join(local,'define-start.json'),'--actor','person:<vrondelli>','--id','activation:start']);
const results=[];
for(const item of load(path.join(here,'authorization.json')).accepted_definitions){
 const id=item.version.split('@')[0];
 const result=define(['discover','--work',session,'--query',id,'--actor','person:<vrondelli>','--id','activation:discover:'+id]);
 assert(JSON.stringify(result).includes(id));results.push({target:item.version,result});
}
const replay=define(['replay','--work',session]);
assert.equal(replay.outcome,'verified');
put(path.join(here,'receipts/define-workflow.json'),{status:'PASS',source:'default active shared catalog; no explicit --catalog or --snapshot-db',results,replay});
put(path.join(here,'receipts/activation.json'),{status:'PASS',shared:status,checks:[
 'five-exact-owner-dispositions','signed-native-commit','registry-v2-contract-admitted',
 '194-version-canonical-publication','189-original-bodies-and-decisions-retained','188-current-identities',
 'ten-durable-join-transitions-to-Completed','original-receipt-attestation-issuance-projection',
 'default-shared-cli-catalog','default-Define-discovery-all-five','Define-session-replay',
 'single-shared-runtime-no-product-copies'],native_source_cut:cut,private_key_published:false});
console.log(JSON.stringify({status:'PASS',versions:194,current:188,join:row.phase,define_discoveries:results.length}));
