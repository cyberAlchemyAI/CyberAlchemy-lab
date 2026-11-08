/** C14 selected root Query adapter using the original assembly's plan handles.
 * The assembly must pass its private checked stage, domain and plan owners;
 * an independently recaptured Read cannot execute against its selected store.
 * Open Questions: docs/GENERIC-APPLICATIONS.md#open-questions. */
import {createCommerceSourceQueryOutputCodecV1,type CommerceSourceQueryOutputCodecV1} from '../commerce/commerce-source-query-output-codec-v1.js';
import {createCommerceSourceQueryRuntimeV1,type CommerceSourceQueryRuntimeV1,type CommerceSourceQueryResultV1} from '../commerce/commerce-source-query-runtime-v1.js';
import type {CoreCommerceStageSourceOwner} from '../commerce/commerce-core-stage-owner.js';
import type {CommerceSourceHandle,CommerceOperationInvocationHandle} from '../commerce/commerce-stages-v1.js';
import type {CommerceComputationDomainOwner,CommerceComputationDomainHandle} from '../commerce/commerce-computation-domain.js';
import type {CommerceLocalPlanOwnerV1,CommerceLocalReadHandleV1} from '../commerce/commerce-local-plan-owner-v1.js';
import type {CommerceSelectedEntryAuthOwnerV1} from '../commerce/commerce-selected-entry-auth-v1.js';
import type {CommerceServiceStorageOwnerV1} from '../commerce/commerce-service-storage-v1.js';

export interface CoreCommerceSelectedQueryAdapter {
 readonly query:string;
 run():CommerceSourceQueryResultV1;
 assertCurrent():void;
 dispose():void;
}

/** A scoped HTTP Query uses the original selected row witness and releases it
 * only after the same Entry/Auth owner rechecks its business resource scope. */
export async function createCoreCommerceSelectedQueryAdapter(input:Readonly<{
 stage:CoreCommerceStageSourceOwner;
 source:CommerceSourceHandle;
 domain:CommerceComputationDomainOwner;
 baseline:CommerceComputationDomainHandle;
 plans:CommerceLocalPlanOwnerV1;
 selected:CommerceSelectedEntryAuthOwnerV1;
 storage:CommerceServiceStorageOwnerV1;
 invocation:CommerceOperationInvocationHandle;
}>):Promise<CoreCommerceSelectedQueryAdapter>{
 const {stage,source,domain,baseline,plans,selected,storage,invocation}=input;
 selected.assertCurrent();storage.assertSelectedAssembly(selected);
 const view=selected.inspectInvocation(invocation),store=storage.inspect(),sourceSha=stage.inspect(source).source_sha256;
 if(view.depth!==0||view.parent_call_path!==null||view.role!=='Query'||view.service!==store.service||
   view.source_sha256!==sourceSha||view.source_sha256!==store.source_capture_sha256||
   selected.inspect().family_sha256!==store.family_sha256)
  throw new Error('selected root Query must belong to the original service/source/family');
 let read:CommerceLocalReadHandleV1|undefined,codec:CommerceSourceQueryOutputCodecV1|undefined,query:CommerceSourceQueryRuntimeV1|undefined;
 let disposed=false,used=false;
 const close=()=>{
  if(disposed)return;disposed=true;
  query?.dispose();codec?.dispose();
  if(read)plans.disposeRead(read);
  selected.retire(invocation);
 };
 try{
  read=plans.bindRead(view.operation);
  const checked=plans.inspectRead(read);
  if(checked.plan.kind!=='local'||checked.plan.service!==view.service||checked.source_capture_sha256!==sourceSha)
   throw new Error('original selected Query requires one matching local Read');
  codec=await createCommerceSourceQueryOutputCodecV1(stage,source,domain,baseline,plans,read);
  query=createCommerceSourceQueryRuntimeV1(stage,source,plans,read,domain,baseline,storage,codec);
  const current=()=>{
   if(disposed)throw new Error('selected Query adapter disposed');
   selected.inspectInvocation(invocation);storage.assertSelectedAssembly(selected);query!.assertCurrent();
  };
  const owner:CoreCommerceSelectedQueryAdapter=Object.freeze({query:view.operation,
   run(){
    current();if(used)throw new Error('selected Query adapter already consumed');used=true;
    try{
     const witness=query!.select(selected,invocation);
     return query!.releaseSelected(witness,selected,invocation);
    }finally{close();}
   },
   assertCurrent:current,dispose:close,
  });
  current();return owner;
 }catch(error){close();throw error;}
}
