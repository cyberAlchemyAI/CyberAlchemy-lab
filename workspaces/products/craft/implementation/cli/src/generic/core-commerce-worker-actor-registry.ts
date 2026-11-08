/** Source-selected worker actor lookup. Registration supplies native identities;
 * each protected Entry still makes its own fresh Auth decision at invocation.
 * Open Questions: docs/GENERIC-APPLICATIONS.md#open-questions. */
import {assertCommerceApplicationAssemblyV1,type CommerceApplicationAssemblyV1} from '../commerce/commerce-application-assembly-v1.js';
import {assertCommerceEntryContextOwnerV1,type CommerceAuthActorV1,
 type CommerceEntryContextOwnerV1} from '../commerce/commerce-entry-context-v1.js';
import type {CoreCommerceWorkerActorRequirement} from './core-commerce-worker-actor-selection.js';

export interface CoreCommerceWorkerActorRegistry {
 inspect():Readonly<{workflow:string;requirements:readonly CoreCommerceWorkerActorRequirement[];
  assigned_entries:readonly string[];missing_entries:readonly string[];
  qualification:'native-service-actor-selection-only;fresh-entry-auth-required'}>;
 bind(actor:CommerceAuthActorV1):readonly string[];
 actorFor(usage:CoreCommerceWorkerActorRequirement['usage'],step?:string|null):CommerceAuthActorV1;
 assertCurrent():void;
}
const owners=new WeakSet<object>();
export function assertCoreCommerceWorkerActorRegistry(owner:CoreCommerceWorkerActorRegistry):void {
 if(!owner||typeof owner!=='object'||!owners.has(owner))throw new Error('checked worker actor registry required');
 owner.assertCurrent();
}

/** A native service identity may cover several source-required Entries. This
 * mapping is never an authorization grant: beginWorker/Read/Observation/Step
 * must obtain READY for the exact Entry immediately before its own effect. */
export function createCoreCommerceWorkerActorRegistry(
 assembly:CommerceApplicationAssemblyV1,auth:CommerceEntryContextOwnerV1,workflowId:string,
):CoreCommerceWorkerActorRegistry {
 assertCommerceApplicationAssemblyV1(assembly);
 assertCommerceEntryContextOwnerV1(auth);
 if(typeof workflowId!=='string'||!workflowId)throw new Error('checked Workflow selector required');
 const source=assembly.inspect();
 const authSource=auth.inspect().source_sha256;
 if(authSource!==source.source_capture_sha256)throw new Error('worker Auth and Workflow require the same original source');
 const requirements=assembly.inspectWorkerActorRequirements(workflowId);
 if(!requirements.length||requirements.length>128)throw new Error('bounded checked Workflow actor requirements required');
 const keys=new Set<string>();
 for(const requirement of requirements){
  const key=requirement.usage+'\0'+(requirement.step??'')+'\0'+requirement.entry;
  if(keys.has(key))throw new Error('duplicate checked Workflow Entry requirement');
  keys.add(key);
  const entry=auth.bindEntry(requirement.entry);
  try{
   const checked=auth.inspectEntry(entry);
   if(checked.interaction!=='request-response'||checked.access.principal_kind!=='service'||
    checked.access.caller!==requirement.caller_service||checked.service!==requirement.target_service||
    checked.invokes.module+'.'+checked.invokes.name!==requirement.target||
    checked.access.permission!==requirement.permission||checked.access.auth_route_id!==requirement.auth_route_id||
    checked.access.auth_permission.resource!==requirement.auth_permission.resource||
    checked.access.auth_permission.action!==requirement.auth_permission.action||
    checked.access.auth_permission.scope!==requirement.auth_permission.scope)
    throw new Error('worker requirement differs from the exact selected Entry/Auth contract');
  }finally{auth.disposeEntry(entry);}
 }
 const actors=new Map<string,CommerceAuthActorV1>();
 const current=()=>{
  assembly.assertCurrent();
  if(auth.inspect().source_sha256!==source.source_capture_sha256)throw new Error('worker Auth source changed');
 };
 const rowFor=(usage:CoreCommerceWorkerActorRequirement['usage'],step:string|null)=>{
  const matches=requirements.filter(row=>row.usage===usage&&row.step===step);
  if(matches.length!==1)throw new Error('one checked Workflow actor requirement required for usage and step');
  return matches[0]!;
 };
 const inspection=()=>{
  const assigned=requirements.filter(row=>actors.has(row.entry)).map(row=>row.entry);
  const missing=requirements.filter(row=>!actors.has(row.entry)).map(row=>row.entry);
  return Object.freeze({workflow:workflowId,requirements,
   assigned_entries:Object.freeze([...new Set(assigned)].sort()),
   missing_entries:Object.freeze([...new Set(missing)].sort()),
   qualification:'native-service-actor-selection-only;fresh-entry-auth-required' as const});
 };
 const owner:CoreCommerceWorkerActorRegistry=Object.freeze({
  inspect(){current();return inspection();},
  bind(actor:CommerceAuthActorV1){
   current();auth.assertActor(actor);
   const assignment=auth.inspectActor(actor);
   if(assignment.principal_kind!=='service'||!assignment.service_id)
    throw new Error('native Workflow service actor required');
   const matches=requirements.filter(row=>row.caller_service===assignment.service_id&&
    row.auth_permission.scope===assignment.scope);
   if(!matches.length)throw new Error('native actor matches no selected Workflow Entry caller and scope');
   for(const row of matches){const prior=actors.get(row.entry);
    if(prior&&prior!==actor)throw new Error('selected Workflow Entry actor cannot be replaced');}
   for(const row of matches)actors.set(row.entry,actor);
   return Object.freeze([...new Set(matches.map(row=>row.entry))].sort());
  },
  actorFor(usage:CoreCommerceWorkerActorRequirement['usage'],step:string|null=null){
   current();const row=rowFor(usage,step),actor=actors.get(row.entry);
   if(!actor)throw new Error('native actor for selected Workflow Entry is missing');
   auth.assertActor(actor);
   const assignment=auth.inspectActor(actor);
   if(assignment.principal_kind!=='service'||assignment.service_id!==row.caller_service||
    assignment.scope!==row.auth_permission.scope)
    throw new Error('native Workflow actor assignment changed');
   return actor;
  },
  assertCurrent:current,
 });
 owners.add(owner);current();return owner;
}
