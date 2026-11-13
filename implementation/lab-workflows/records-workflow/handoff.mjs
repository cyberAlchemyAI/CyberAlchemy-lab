import {readFileSync} from 'node:fs';
import path from 'node:path';
import {evaluate as defineEvaluate,selectors} from '../../../workspaces/products/define/implementation/cli/alchlang/preparation/native.mjs';
import {document,documentMap} from '../../../workspaces/products/define/implementation/cli/alchlang/preparation/journal.mjs';
import {membersFromBinding} from '../../../workspaces/products/define/implementation/cli/alchlang/preparation/validation.mjs';
import {load,canonical} from '../../../workspaces/products/define/implementation/cli/alchlang/runtime/runtime.mjs';
import {inspectPackage} from '../../../workspaces/products/define/implementation/cli/alchlang/runtime/package.mjs';
import {digest} from '../../lab-runtime/alchlang/shared-records/verified-projection.mjs';
import {enforce} from './kernel.mjs';
export async function inspectHandoff({work,package:directory,handoff_ref,consumer,intended_use}){
 const session=await load(work);
 const events=session.events.filter(e=>e.preparation?.command==='handoff'&&e.preparation.output.handoff_ref===handoff_ref);
 if(events.length!==1)throw Error('recorded-define-handoff-required');
 const event=events[0],record=event.preparation,handoff=record.output,documents=documentMap(record.documents),memoryMembers=directory?null:membersFromBinding(record.input.package_members,documents),inspection=await inspectPackage(directory,{observe:true,deriveReadiness:true,memoryMembers});
 const packageBytes=directory?readFileSync(path.join(directory,inspection.observation.package_binding.path)):documents.get(handoff.package_binding.path),requestBytes=directory?readFileSync(path.join(directory,inspection.observation.request_binding.path)):documents.get(handoff.request_binding.path);
 const consumerRaw=documents.get(handoff.consumer.path);
 const facts={schema_valid:handoff.schema_version==='cal.define.prepared-handoff/v1'&&handoff.authority_effect==='none',package_bound:handoff.package_binding.sha256===digest(packageBytes)&&Number(handoff.package_binding.bytes)===packageBytes.length,session_bound:handoff.session_ref===session.current.session_id&&String(handoff.session_revision)===String(event.command.expected_revision),source_bound:handoff.source_cut===event.model&&handoff.request_binding.sha256===digest(requestBytes),use_bound:handoff.intended_use===intended_use,consumer_bound:!!consumerRaw&&digest(consumerRaw)===handoff.consumer.sha256&&consumerRaw.toString()===consumer,readiness_verified:record.input.actual_native_use?.outcome==='ready',owner_decision_verified:false};
 if(Object.entries(facts).some(([key,value])=>key!=='owner_decision_verified'&&!value))throw Error('verified-handoff-not-ready-or-context-mismatch');
 return {handoff,bytes:Buffer.from(canonical(handoff)),facts,event_digest:event.event_sha256,inspection};
}
export async function responseToHandoff(verified,{responder,message}){
 if(!responder||!message)throw Error('handoff-response-subject-required');
 return defineEvaluate(selectors.response,{handoff:verified.handoff,handoff_binding:document(verified.bytes).binding,responder,message:document(Buffer.from(message)).binding});
}
