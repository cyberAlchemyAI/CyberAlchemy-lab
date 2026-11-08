import {disposeCommerceWorkflowFreshLocalSuccessorV1,type CommerceWorkflowFreshLocalSuccessorV1} from '../commerce/commerce-workflow-fresh-local-successor-v1.js';
/** Repeatedly interpret the checked Workflow under one qualified worker.
 * Every transition begins with a fresh generated snapshot Query. The cycle
 * stops on suspension, a contested effect, or the source transition bound.
 * Open Questions: docs/GENERIC-APPLICATIONS.md#open-questions. */
import {assertCommerceWorkflowCoordinationBindingV1,type CommerceWorkflowCoordinationBindingV1}
 from '../commerce/commerce-workflow-coordination-binding-v1.js';
import {assertCoreCommerceClaimedWorkerSession,type CoreCommerceClaimedWorkerSession}
 from './core-commerce-worker-claim-executor.js';
import type {CoreCommerceWorkerSnapshotQuery,CoreCommerceWorkerSnapshotResult}
 from './core-commerce-worker-snapshot-query.js';
import type {CoreCommerceWorkerContinuation,CoreCommerceWorkerContinuationResult}
 from './core-commerce-worker-continuation.js';
import type {CoreCommerceWorkerStepRunner,CoreCommerceWorkerStepResult}
 from './core-commerce-worker-step-runner.js';
import type {CoreCommerceWorkerLocalObservationRunner,CoreCommerceLocalObservationResult}
 from './core-commerce-worker-local-observation-runner.js';
import type {CommerceAuthActorV1} from '../commerce/commerce-entry-context-v1.js';

type SnapshotFailure=Exclude<CoreCommerceWorkerSnapshotResult,{kind:'snapshot'}>;
type ContinuationFailure=Exclude<CoreCommerceWorkerContinuationResult,{kind:'prepared-step'|'local-observation-needed'}>;
type LocalFailure=Exclude<CoreCommerceLocalObservationResult,{kind:'observed'}>;
// The step runner is being extended with a receipt-bound terminal result.
// A terminal result must take a fresh snapshot before the source terminal
// guard is evaluated; the pre-effect snapshot cannot prove the final state.
const terminalReady=(result:CoreCommerceWorkerStepResult):boolean=>{
 const view=result as {kind:string;authority_effect?:unknown;commits?:unknown;qualification?:unknown};
 if(view.kind!=='terminal-ready')return false;
 if(view.authority_effect==='committed'&&typeof view.commits==='number'&&
  Number.isSafeInteger(view.commits)&&view.commits>0&&
  view.qualification==='original-generated-same-service-commit;fresh-terminal-snapshot-required')return true;
 return view.authority_effect==='none'&&view.commits===0&&
  view.qualification==='original-protected-query-inspected-existing-commit;fresh-terminal-snapshot-required';
};

export type CoreCommerceWorkerCycleResult=
 Readonly<{kind:'finished';terminal:string;order_id:string;transitions:number;
  qualification:'checked-terminal-guard-on-current-original-owned-rows';authority_effect:'none'}>|
 Readonly<{kind:'suspended';result:SnapshotFailure|ContinuationFailure|LocalFailure|CoreCommerceWorkerStepResult;
  transitions:number}>|
 Readonly<{kind:'transition-limit';transitions:number;additional_effect:'none'}>;

export interface CoreCommerceWorkerCycle {
 inspect():Readonly<{workflow:string;source_capture_sha256:string;max_transitions:number;
  qualification:'source-bounded-repeated-worker-transitions-and-checked-terminal;recovery-pending'}>;
 run(session:CoreCommerceClaimedWorkerSession):Promise<CoreCommerceWorkerCycleResult>;
 bindActor(actor:CommerceAuthActorV1):readonly string[];
 assertCurrent():void;
 close():void;
}

export function createCoreCommerceWorkerCycle(input:Readonly<{
 binding:CommerceWorkflowCoordinationBindingV1;
 snapshots:CoreCommerceWorkerSnapshotQuery;
 continuation:CoreCommerceWorkerContinuation;
 remote:CoreCommerceWorkerStepRunner;
 local:CoreCommerceWorkerLocalObservationRunner;
}>):CoreCommerceWorkerCycle {
 const {binding,snapshots,continuation,remote,local}=input;
 assertCommerceWorkflowCoordinationBindingV1(binding);
 const source=binding.inspect(),limit=source.workflow.defaults.max_transitions_per_resume;
 if(!Number.isSafeInteger(limit)||limit<1||limit>1024||
  snapshots.inspect().workflow!==source.workflow.name||
  continuation.inspect().workflow!==source.workflow.name||
  remote.inspect().workflow!==source.workflow.name||local.inspect().workflow!==source.workflow.name||
  snapshots.inspect().source_capture_sha256!==source.source_capture_sha256||
  continuation.inspect().source_capture_sha256!==source.source_capture_sha256||
  remote.inspect().source_capture_sha256!==source.source_capture_sha256||
  local.inspect().source_capture_sha256!==source.source_capture_sha256)
  throw new Error('worker cycle components must share one checked Workflow and source bound');
 let closed=false;
 const current=()=>{
  if(closed)throw new Error('worker cycle closed');
  binding.assertCurrent();snapshots.assertCurrent();continuation.assertCurrent();
  remote.assertCurrent();local.assertCurrent();
 };
 const owner:CoreCommerceWorkerCycle=Object.freeze({
  inspect(){current();return Object.freeze({workflow:source.workflow.name,
   source_capture_sha256:source.source_capture_sha256,max_transitions:limit,
   qualification:'source-bounded-repeated-worker-transitions-and-checked-terminal;recovery-pending' as const});},
  bindActor(actor:CommerceAuthActorV1){
   if(closed)throw new Error('worker cycle closed');
   // The three public component binds each check source/Auth before assignment.
   const assigned=new Set<string>();
   for(const component of [snapshots,remote,local])
    for(const entry of component.bindActor(actor))assigned.add(entry);
   return Object.freeze([...assigned].sort());
  },
  async run(session:CoreCommerceClaimedWorkerSession):Promise<CoreCommerceWorkerCycleResult>{
   current();assertCoreCommerceClaimedWorkerSession(session);
   let pending:CommerceWorkflowFreshLocalSuccessorV1|undefined;
   try{for(let transitions=0;transitions<limit;transitions++){
    const snapshot=await snapshots.run(session);
    if(snapshot.kind!=='snapshot')return Object.freeze({kind:'suspended' as const,result:snapshot,transitions});
    const successor=pending;pending=undefined;
    try{
     const next=await continuation.prepareNext(session,snapshot,successor);
     if(next.kind==='finished')return Object.freeze({kind:'finished' as const,
      terminal:next.terminal,order_id:next.order_id,transitions,
      qualification:next.qualification,authority_effect:'none' as const});
     if(next.kind==='local-observation-needed'){
      const result=await local.run(session,snapshot);
      if(result.kind==='observed'){pending=result.successor;continue;}
      return Object.freeze({kind:'suspended' as const,result,transitions});
     }
     if(next.kind!=='prepared-step')return Object.freeze({kind:'suspended' as const,result:next,transitions});
     try{
      const result=await remote.run(session,snapshot,next);
      if(result.kind==='observed'||terminalReady(result))continue;
      return Object.freeze({kind:'suspended' as const,result,transitions});
     }finally{next.dispose();}
    }finally{try{snapshot.dispose();}finally{if(successor)disposeCommerceWorkflowFreshLocalSuccessorV1(successor);}}
   }
   return Object.freeze({kind:'transition-limit' as const,transitions:limit,additional_effect:'none' as const});
   }finally{if(pending)disposeCommerceWorkflowFreshLocalSuccessorV1(pending);}
  },
  assertCurrent:current,close(){closed=true;},
 });
 current();return owner;
}
