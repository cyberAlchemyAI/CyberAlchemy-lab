/** Emit executable Commerce application wiring from the checked application
 * selection. These modules never manufacture storage, Auth, workflow claims,
 * Event proofs, or publication decisions: the original source-bound owners
 * retain those responsibilities.
 * Open Questions: docs/GENERIC-APPLICATIONS.md#open-questions. */
import {createHash} from 'node:crypto';

export type CoreCommerceRuntimeSelection=Readonly<{
 application:string;
 source_capture_sha256:string;
 family_sha256:string;
 services:readonly string[];
 workflows:readonly string[];
 event_entries:readonly string[];
}>;
export type CoreCommerceRuntimeModule=Readonly<{path:string;content:string;sha256:string}>;

const sha=(value:string)=>createHash('sha256').update(value).digest('hex');
const unique=(values:readonly string[],label:string)=>{
 if(!Array.isArray(values)||values.length>128||new Set(values).size!==values.length||
  values.some(value=>typeof value!=='string'||!value||value.length>512))
  throw new Error('bounded, distinct source-selected '+label+' required');
 return [...values].sort();
};
const module=(name:string,content:string):CoreCommerceRuntimeModule=>
 Object.freeze({path:name,content,sha256:sha(content)});

/** The selection is derived by the artifact owner from the captured AlchLang
 * topology and original profile. No caller-provided route implementation is
 * embedded in generated code. */
export function emitCoreCommerceApplicationRuntime(selection:CoreCommerceRuntimeSelection):
 readonly CoreCommerceRuntimeModule[]{
 if(!selection||typeof selection.application!=='string'||!selection.application||
  !/^[a-f0-9]{64}$/.test(selection.source_capture_sha256)||
  !/^[a-f0-9]{64}$/.test(selection.family_sha256))
  throw new Error('checked Commerce application and source/profile identities required');
 const services=unique(selection.services,'services');
 const workflows=unique(selection.workflows,'workflows');
 const events=unique(selection.event_entries,'Event entries');
 if(!services.length)throw new Error('source-selected Commerce services required');
 const identity=`const expected=Object.freeze({application:${JSON.stringify(selection.application)},source_capture_sha256:${JSON.stringify(selection.source_capture_sha256)},family_sha256:${JSON.stringify(selection.family_sha256)},services:Object.freeze(${JSON.stringify(services)})});\n`;
 const check=`function checked(owner){if(!owner||typeof owner.inspect!=='function'||typeof owner.assertCurrent!=='function')throw Error('GENERATED_COMMERCE_OWNER_REQUIRED');const manifest=owner.inspect();if(manifest?.application!==expected.application||manifest?.source_capture_sha256!==expected.source_capture_sha256||manifest?.family_sha256!==expected.family_sha256||!Array.isArray(manifest?.services)||JSON.stringify(manifest.services.map(row=>row.id).sort())!==JSON.stringify(expected.services))throw Error('GENERATED_COMMERCE_SOURCE_MISMATCH');return manifest;}\n`;
 const worker=`${identity}${check}export const workflowIds=Object.freeze(${JSON.stringify(workflows)});\n`+
 `export function createGeneratedCommerceWorkflowWorkers(owner){checked(owner);const selected=new Set(workflowIds);const passes=new Map(),relays=new Map();let closed=false;const current=()=>{if(closed)throw Error('GENERATED_COMMERCE_WORKERS_CLOSED');checked(owner);};const selectedId=id=>{current();if(!selected.has(id))throw Error('GENERATED_COMMERCE_WORKFLOW_NOT_SELECTED');};const passFor=id=>{selectedId(id);let pass=passes.get(id);if(!pass){pass=owner.openWorkflowPass(id);if(pass.inspect().workflow!==id||pass.inspect().source_capture_sha256!==expected.source_capture_sha256)throw Error('GENERATED_COMMERCE_WORKFLOW_SOURCE_MISMATCH');passes.set(id,pass);}pass.assertCurrent();return pass;};const relayFor=id=>{selectedId(id);let relay=relays.get(id);if(!relay){relay=owner.openOutboxRelay(id);if(relay.inspect().workflow!==id||relay.inspect().source_capture_sha256!==expected.source_capture_sha256)throw Error('GENERATED_COMMERCE_WORKFLOW_SOURCE_MISMATCH');relays.set(id,relay);}relay.assertCurrent();return relay;};return Object.freeze({workflowIds,inspectActorRequirements(id){selectedId(id);return owner.inspectWorkerActorRequirements(id);},bindActor(id,actor){return passFor(id).bindActor(actor);},relayPage(id,cursor,limit){return relayFor(id).relayPage(cursor,limit);},runVacant(id,occurrenceId){if(typeof occurrenceId!=='string'||!occurrenceId)throw Error('GENERATED_COMMERCE_OCCURRENCE_REQUIRED');return passFor(id).runVacant(occurrenceId);},runRecovered(id,occurrenceId){if(typeof occurrenceId!=='string'||!occurrenceId)throw Error('GENERATED_COMMERCE_OCCURRENCE_REQUIRED');const pass=passFor(id);if(typeof pass.runQuiescent!=='function')throw Error('GENERATED_COMMERCE_RECOVERY_NOT_AVAILABLE');return pass.runQuiescent(occurrenceId);},assertCurrent:current,close(){if(closed)return;closed=true;for(const pass of passes.values())pass.close();}});}\n`;
 const relay=`${identity}${check}export const eventEntryIds=Object.freeze(${JSON.stringify(events)});\n`+
 `export function createGeneratedCommerceEventRelays(owner){checked(owner);const selected=new Set(eventEntryIds);const passes=new Map();let closed=false;const current=()=>{if(closed)throw Error('GENERATED_COMMERCE_RELAYS_CLOSED');checked(owner);};const passFor=id=>{current();if(!selected.has(id))throw Error('GENERATED_COMMERCE_EVENT_NOT_SELECTED');let pass=passes.get(id);if(!pass){pass=owner.openSelectedEventPass(id);const inspected=pass.inspect();if(inspected.entry!==id||inspected.source_capture_sha256!==expected.source_capture_sha256)throw Error('GENERATED_COMMERCE_EVENT_SOURCE_MISMATCH');passes.set(id,pass);}pass.assertCurrent();return pass;};return Object.freeze({eventEntryIds,inspectActorRequirement(id){return passFor(id).inspectActorRequirement();},scanReadyPage(id,cursor,limit){const pass=passFor(id);if(typeof pass.scanReady!=='function')throw Error('GENERATED_COMMERCE_EVENT_DISCOVERY_NOT_AVAILABLE');return pass.scanReady(cursor,limit);},runReady(id,occurrenceId,actor,signal){if(typeof occurrenceId!=='string'||!occurrenceId)throw Error('GENERATED_COMMERCE_OCCURRENCE_REQUIRED');return passFor(id).runReady(occurrenceId,actor,signal);},assertCurrent:current,close(){closed=true;}});}\n`;
 const application=`import {createGeneratedCommerceWorkflowWorkers,workflowIds} from './workflow-worker.mjs';\nimport {createGeneratedCommerceEventRelays,eventEntryIds} from './event-relay.mjs';\nexport {workflowIds,eventEntryIds};\n${identity}${check}`+
 `export const applicationId=expected.application;export const serviceIds=expected.services;\n`+
 `export async function createGeneratedCommerceApplication(owner,native){checked(owner);if(!native||typeof native!=='object')throw Error('GENERATED_COMMERCE_AUTH_NATIVE_REQUIRED');const http=await owner.openSelectedHttpRuntime(native);let workers,events;try{workers=createGeneratedCommerceWorkflowWorkers(owner);events=createGeneratedCommerceEventRelays(owner);}catch(error){http.close();throw error;}let closed=false;const current=()=>{if(closed)throw Error('GENERATED_COMMERCE_APPLICATION_CLOSED');checked(owner);http.assertCurrent();workers.assertCurrent();events.assertCurrent();};return Object.freeze({applicationId,serviceIds,workflowIds,eventEntryIds,auth:http.auth,serviceActorRequirements:http.service_actor_requirements,bindServiceActor(actor){current();return http.bindServiceActor(actor);},handle(request,actor){current();return http.handle(request,actor);},inspectWorkerActorRequirements(id){current();return workers.inspectActorRequirements(id);},bindWorkerActor(id,actor){current();return workers.bindActor(id,actor);},relayWorkflowPage(id,cursor,limit){current();return workers.relayPage(id,cursor,limit);},runWorkflow(id,occurrenceId){current();return workers.runVacant(id,occurrenceId);},recoverWorkflow(id,occurrenceId){current();return workers.runRecovered(id,occurrenceId);},inspectEventActorRequirement(id){current();return events.inspectActorRequirement(id);},scanReadyEventPage(id,cursor,limit){current();return events.scanReadyPage(id,cursor,limit);},runEvent(id,occurrenceId,actor,signal){current();return events.runReady(id,occurrenceId,actor,signal);},assertCurrent:current,close(){if(closed)return;closed=true;events.close();workers.close();http.close();}});}\n`;
 return Object.freeze([
  module('application.mjs',application),
  module('workflow-worker.mjs',worker),
  module('event-relay.mjs',relay),
 ]);
}
