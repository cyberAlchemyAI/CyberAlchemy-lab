/** One source-selected pass from a committed Workflow occurrence through the
 * generated claim and bounded worker cycle. Each continuation obtains a new
 * original snapshot before any next local or remote step.
 * Open Questions: docs/GENERIC-APPLICATIONS.md#open-questions. */
import {assertCommerceApplicationAssemblyV1,type CommerceApplicationAssemblyV1}
 from '../commerce/commerce-application-assembly-v1.js';
import type {CommerceAuthActorV1} from '../commerce/commerce-entry-context-v1.js';
import type {CoreCommerceWorkerClaimExecution} from './core-commerce-worker-claim-executor.js';
import type {CoreCommerceWorkerCycleResult} from './core-commerce-worker-cycle.js';

type ClaimFailure=Exclude<CoreCommerceWorkerClaimExecution,{kind:'claimed-progress'}>;
export type CoreCommerceWorkflowPassResult=
 Readonly<{kind:'schedule-state';state:'not-ready'|'unavailable'|'indeterminate'}>|
 Readonly<{kind:'claim-result';result:ClaimFailure}>|
 Readonly<{kind:'cycle-result';result:CoreCommerceWorkerCycleResult}>;

export interface CoreCommerceWorkflowPass {
 inspect():Readonly<{workflow:string;source_capture_sha256:string;
  qualification:'source-bounded-workflow-pass;vacant-and-quiescent-recovery'}>;
 bindActor(actor:CommerceAuthActorV1):readonly string[];
 runVacant(occurrenceId:string):Promise<CoreCommerceWorkflowPassResult>;
 runQuiescent(occurrenceId:string):Promise<CoreCommerceWorkflowPassResult>;
 assertCurrent():void;
 close():void;
}

/** The only input to this pass is the original occurrence identity. The
 * assembly chooses the Workflow, service stores, Auth, and generated targets. */
export function createCoreCommerceWorkflowPass(
 assembly:CommerceApplicationAssemblyV1,workflowId:string,
):CoreCommerceWorkflowPass {
 assertCommerceApplicationAssemblyV1(assembly);
 const ingress=assembly.openWorkflowIngress(workflowId),claim=assembly.openWorkflowClaimExecutor(workflowId),
  cycle=assembly.openWorkflowCycle(workflowId);
 const source=ingress.inspect();
 if(claim.inspect().workflow!==source.workflow||cycle.inspect().workflow!==source.workflow||
  claim.inspect().source_capture_sha256!==source.source_capture_sha256||
  cycle.inspect().source_capture_sha256!==source.source_capture_sha256)
  throw new Error('Workflow pass components must share the original captured source');
 let closed=false;
 const current=()=>{
  if(closed)throw new Error('Workflow pass closed');
  // Claim and cycle both recheck the same assembly; ingress checks its store.
  ingress.assertCurrent();claim.assertCurrent();
  cycle.assertCurrent();
 };
 const runClaimed=async(scheduled:ReturnType<typeof ingress.claim>):Promise<CoreCommerceWorkflowPassResult>=>{
  if(scheduled.kind!=='claimed')return Object.freeze({kind:'schedule-state' as const,
   state:scheduled.kind});
  const claimed=await claim.run(scheduled.claim);
  if(claimed.kind!=='claimed-progress')return Object.freeze({kind:'claim-result' as const,
   result:claimed});
  const session=claimed.session;
  try{
   const result=await cycle.run(session);
   return Object.freeze({kind:'cycle-result' as const,result});
  }finally{session.dispose();}
 };
 const owner:CoreCommerceWorkflowPass=Object.freeze({
  inspect(){current();return Object.freeze({workflow:source.workflow,
   source_capture_sha256:source.source_capture_sha256,
   qualification:'source-bounded-workflow-pass;vacant-and-quiescent-recovery' as const});},
  bindActor(actor:CommerceAuthActorV1){
   if(closed)throw new Error('Workflow pass closed');
   // Both public component binds check original source/Auth before assigning;
   // retain the final pass-wide check after the synchronous batch.
   const assigned=new Set<string>();
   for(const component of [claim,cycle])
    for(const entry of component.bindActor(actor))assigned.add(entry);
   current();return Object.freeze([...assigned].sort());
  },
  async runVacant(occurrenceId:string):Promise<CoreCommerceWorkflowPassResult>{
   current();return runClaimed(ingress.claim(occurrenceId));
  },
  async runQuiescent(occurrenceId:string):Promise<CoreCommerceWorkflowPassResult>{
   current();return runClaimed(ingress.reclaimQuiescent(occurrenceId));
  },
  assertCurrent:current,
  close(){if(closed)return;closed=true;try{cycle.close();}finally{claim.close();}},
 });
 current();return owner;
}
