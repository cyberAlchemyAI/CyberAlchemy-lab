import {run as defineCommand} from '../../../workspaces/products/define/implementation/cli/alchlang/preparation/cli.mjs';
import {document} from '../../../workspaces/products/define/implementation/cli/alchlang/preparation/journal.mjs';
import {canonical} from '../../../workspaces/products/define/implementation/cli/alchlang/runtime/runtime.mjs';
import {publishDirectoryView} from './publication.mjs';
import {sameBinding, Snapshots} from '../../lab-runtime/alchlang/shared-records/snapshots.mjs';
import {readFileSync,writeFileSync,mkdirSync,existsSync} from 'node:fs';
import path from 'node:path';
import {isDeepStrictEqual} from 'node:util';
import {digest} from '../../lab-runtime/alchlang/shared-records/verified-projection.mjs';
import {verifyPlanningEvidence} from '../../lab-runtime/alchlang/shared-records/evidence.mjs';
import {verifyCurrentDefinitionReviews} from '../../lab-runtime/alchlang/shared-records/carry-forward.mjs';
import {execute} from '../../lab-runtime/alchlang/shared-records/service.mjs';
import {publish} from '../../lab-runtime/alchlang/shared-records/runtime.mjs';
import {nativePort} from '../../lab-runtime/alchlang/shared-records/ports.mjs';
import {main} from '../../lab-runtime/alchlang/shared-records/cli.mjs';
import {placePackage} from '../definition-catalog/cli.mjs';
import {verifyRecordReviews} from './record-review.mjs';
import {inspectHandoff,responseToHandoff} from './handoff.mjs';
import {resolveHost} from './host.mjs';
import {reconcileViews} from './views.mjs';
import {enforce} from './kernel.mjs';
const raw=x=>Buffer.from(JSON.stringify(x)),put=(file,value)=>writeFileSync(file,JSON.stringify(value,null,2)+'\n');
export async function runLifecycle(request,active,trust){
 const run=path.resolve(request.run_directory);
 if(run===active.native_store||run.startsWith(active.native_store+path.sep))throw Error('lifecycle-journal-inside-native-store');
 mkdirSync(run,{recursive:true});const ledger=path.join(run,'lifecycle.json'),identity=digest(raw({handoff:request.handoff,apply:request.apply,placements:request.placements}));
 let state=existsSync(ledger)?JSON.parse(readFileSync(ledger)):{version:1,identity,steps:[],status:'running'};
 if(state.identity!==identity)throw Error('lifecycle-request-conflict');
 const verified=await inspectHandoff(request.handoff),construction=verifyPlanningEvidence(request.apply.construction,trust),value=construction.input.value;
 verifyCurrentDefinitionReviews(value,request.apply,trust,active.database);
 if(request.apply.proposal.targets.some(t=>t.category==='artifact-instance'))verifyRecordReviews(request.apply,value,trust,nativePort({action:'record-projection',store:active.native_store,require_current:true}));
 const commitmentBinding=request.handoff_commitment,stage=value.stages.find(s=>s.stage==='Definitions');
 const qualified=trust.materials?.[commitmentBinding?.ref??commitmentBinding?.path];
 if(!qualified||qualified.sha256!==commitmentBinding.sha256||!stage||!sameBinding(stage.subject,commitmentBinding)||!sameBinding(value.definition_selection_receipt,commitmentBinding))throw Error('handoff-construction-commitment-required');
 const commitmentRaw=readFileSync(qualified.path);
 if(digest(commitmentRaw)!==commitmentBinding.sha256||commitmentRaw.length!==Number(commitmentBinding.bytes))throw Error('handoff-construction-commitment-corrupt');
 const commitment=JSON.parse(commitmentRaw),handoff=verified.handoff;
 const commitmentVerified=commitment.schema_version==='lab-handoff-target-commitment/v1'&&commitment.handoff_sha256===digest(verified.bytes)&&sameBinding(commitment.package_binding,handoff.package_binding)&&commitment.source_cut===handoff.source_cut&&commitment.intended_use===handoff.intended_use&&sameBinding(commitment.consumer,handoff.consumer)&&isDeepStrictEqual(commitment.proposal,request.apply.proposal)&&isDeepStrictEqual(commitment.selected_meanings,value.selected_targets);
 const prepared=await execute(request.apply.construction,trust);
 if(prepared.result!=='GenerationEntryPlanReady')throw Error('construction-not-ready');
 const plan=await enforce('PlanLifecycle',{...verified.facts,target_commitment_verified:commitmentVerified,owner_decision_verified:true});
 // Checkpoints report progress; only re-observed owner receipts and idempotent effects decide it.
 state={version:1,identity,steps:[],status:'running'};
 for(const step of plan.steps){
  const name=typeof step==='string'?step:step.tag;
  let evidence;
  if(name==='InspectHandoff')evidence={handoff:digest(verified.bytes),event:verified.event_digest};
  else if(name==='ReviewOwner')evidence={construction:digest(Buffer.from(request.apply.construction.artifact,'base64')),targets:request.apply.proposal.targets.map(t=>t.version_ref)};
  else if(name==='ResolveHost')evidence=await resolveHost({workspace:request.apply.workspace,catalog:request.apply.catalog,project:Object.hasOwn(request.apply,'semantic_project')?request.apply.semantic_project:request.apply.project,store:active.native_store,work:request.apply.work});
  else if(name==='PlaceCandidate')evidence=await Promise.all(request.placements.map(p=>placePackage(p)));
  else if(name==='EnforceConstruction')evidence=await execute(request.apply.construction,trust);
  else if(name==='ApplyNative'){
   const file=path.join(run,'native-apply.json');put(file,request.apply);
   evidence=await main(['native-apply','--file',file,'--trust',active.trust,'--db',active.database]);
   if(evidence.outcome==='Unknown')throw Error('native-outcome-unknown-inspect-original-operation');
   const committed=nativePort({action:'committed',store:active.native_store,operation:request.apply.proposal.proposal_id});
   if(!isDeepStrictEqual(committed.proposal,request.apply.proposal))throw Error('lifecycle-original-operation-mismatch');
  }else if(name==='PublishSnapshot'){
   if(!request.publication){state.status='needs-qualified-publication';put(ledger,state);return state;}
   const publication=verifyPlanningEvidence(request.publication,trust,{historical:true}).input.value;
   if(request.publication.operation==='PublishDirectoryView'){
    const db=new Snapshots(active.database,{readOnly:true,trust});
    try{
     const source=JSON.parse(db.material(publication.bundle.sha256,'source.json').bytes);
     if(!source.record_construction)throw Error('lifecycle-record-publication-binding-required');
     const binding=source.record_construction,original=db.material(publication.bundle.sha256,binding.ref??binding.path);
     if(original.binding.sha256!==binding.sha256)throw Error('lifecycle-publication-original-mismatch');
     const constructor=JSON.parse(original.bytes);
     if(!isDeepStrictEqual(constructor.proposal,request.apply.proposal)||constructor.approval_artifact!==request.apply.approval_artifact)throw Error('lifecycle-publication-target-mismatch');
    }finally{db.close();}
    evidence=await publishDirectoryView(request.publication,trust,active);
   }else{
    if(publication.operation_ref!==request.apply.proposal.proposal_id)throw Error('lifecycle-publication-target-mismatch');
    evidence=await publish(request.publication,trust,active.database);
   }
  }else if(name==='ReconcileViews')evidence=await reconcileViews({...active,selector:state.steps.find(e=>e.step==='PublishSnapshot').evidence.selected},trust);
  else if(name==='Acknowledge'){
   const message='Shared Lab publication and canonical views verified for '+request.apply.proposal.proposal_id,response=await responseToHandoff(verified,{responder:request.responder,message}),envelope=document(verified.bytes),messageDocument=document(Buffer.from(message)),responseDocument=document(Buffer.from(canonical(response))),file=path.join(run,'define-ack.json');
   put(file,{input:{value:{handoff:envelope.binding,actual_response:responseDocument.binding,response_to:envelope.binding.sha256,declared_responder:request.responder,posture:'reported-acknowledgement'}},documents:[envelope,messageDocument,responseDocument]});
   evidence=await defineCommand('ack',{'--work':request.handoff.work,'--file':file,'--actor':request.responder,'--id':'lab-ack:'+request.apply.proposal.proposal_id});
  }
  else throw Error('unsupported-generated-lifecycle-step');
  state.steps.push({step:name,evidence});put(ledger,state);
 }
 state.status='completed';put(ledger,state);return state;
}
