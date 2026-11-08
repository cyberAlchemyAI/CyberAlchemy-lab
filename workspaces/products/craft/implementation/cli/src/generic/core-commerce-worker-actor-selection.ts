/** Worker service-actor requirements come from the checked Workflow calls and
 * inline Entry permissions. Native principal provisioning remains external.
 * Open Questions: docs/GENERIC-APPLICATIONS.md#open-questions. */
import type {CoreWorkflowSource,CoreWorkflowInvocation} from '../commerce/commerce-core-flow-workflow.js';
import type {EntryContractV1} from '../commerce/commerce-data-v1.js';

export type CoreCommerceWorkerActorRequirement=Readonly<{
 usage:'claim'|'snapshot'|'observation'|'remote';
 step:string|null;
 caller_service:string;
 entry:string;
 target:string;
 target_service:string;
 permission:string;
 auth_route_id:string;
 auth_permission:EntryContractV1['access']['auth_permission'];
}>;

export function selectCoreCommerceWorkerActorRequirements(
 workflow:CoreWorkflowSource,entries:readonly EntryContractV1[],
):readonly CoreCommerceWorkerActorRequirement[]{
 const byId=new Map<string,EntryContractV1>();
 for(const entry of entries){
  if(byId.has(entry.id))throw new Error('duplicate checked Entry contract');
  byId.set(entry.id,entry);
 }
 const rows:CoreCommerceWorkerActorRequirement[]=[];
 const requireCall=(usage:CoreCommerceWorkerActorRequirement['usage'],step:string|null,call:CoreWorkflowInvocation)=>{
  const entry=byId.get(call.entry);
  if(!entry||entry.interaction!=='request-response'||entry.access.principal_kind!=='service'||
   entry.access.caller!==workflow.owner||entry.invokes.role!==call.role||
   entry.invokes.module+'.'+entry.invokes.name!==call.target||!entry.service||
   !entry.access.permission||!entry.access.auth_route_id)
   throw new Error('Workflow call must select exact checked service Entry and inline permission');
  rows.push(Object.freeze({usage,step,caller_service:workflow.owner,entry:entry.id,target:call.target,
   target_service:entry.service,permission:entry.access.permission,auth_route_id:entry.access.auth_route_id,
   auth_permission:Object.freeze({...entry.access.auth_permission})}));
 };
 for(const driver of workflow.drivers)requireCall(driver.kind,null,driver.call);
 for(const step of workflow.steps)if(step.kind==='remote')requireCall('remote',step.name,step.call);
 return Object.freeze(rows);
}
