/** Reusable verified-ingress -> original generated command/commit inspection.
 * Owns no broker, inbox, outbox, SQL transaction or second delivery journal.
 * projectInput is the selected original checked Mapping evaluator, not authored
 * host-language code. Open Questions: ../credentials/README.md. */
import {assert,canonical,freeze,text} from '../shared.mjs';
export function createGeneratedEventCommitPort({runtime,entry,projectInput,onResult}){
 text(entry,'selected inbound Entry');assert(runtime&&typeof runtime.prepareCommand==='function'&&typeof runtime.inspectTransferredCommandIdentity==='function'&&typeof runtime.inspectCommand==='function'&&typeof projectInput==='function','InvalidContract','original generated command runtime and checked input Mapping required');
 const receipts=new WeakMap(),bytes=value=>new TextEncoder().encode(canonical(value));
 async function prepare(actor,wire,messageIdentity){runtime.assertCurrent();const prepared=runtime.prepareCommand(runtime.entry(entry),wire,{client_key:messageIdentity});try{const permitted=await runtime.authorize(actor,prepared);assert(permitted.ok,'PermissionDenied','current original inbound Entry permission');const consumed=await runtime.consume(permitted.value,prepared);assert(consumed.ok,'PermissionDenied','current original command transfer');return {prepared,transfer:consumed.value};}catch(e){runtime.disposePrepared(prepared);throw e;}}
 return Object.freeze({
  async commitEvent({actor,entry:requested,messageIdentity,event,rawSha256}){
   assert(requested===entry,'ForeignOwner','selected inbound Entry');text(messageIdentity,'stable inbound identity',128);assert(/^[a-f0-9]{64}$/.test(messageIdentity)&&/^[a-f0-9]{64}$/.test(rawSha256),'InvalidContract','actual ingress identity and raw digest');runtime.assertCurrent();const wire=bytes(await projectInput(freeze({entry,event,messageIdentity,rawSha256})));assert(wire.byteLength<=65536,'ResourceLimit','bounded checked inbound Mapping output');runtime.assertCurrent();const command=await prepare(actor,wire,messageIdentity);let result;
   try{result=await runtime.executeCommand(command.transfer);}finally{runtime.disposePrepared(command.prepared);}if(onResult)onResult(result);
   assert(result.ok&&result.outcome.kind==='Returned'&&['committed','replayed'].includes(result.observation.kind),'CommitUnavailable','original generated command not confirmed');runtime.assertCurrent();const receipt=Object.freeze({kind:'original-generated-inbound-commit/v1'});receipts.set(receipt,{actor,wire,entry,messageIdentity,tuple:result.observation.command_tuple_sha256});return receipt;
  },
  async assertCommitted(receipt,{entry:requested,messageIdentity}){
   const selected=receipt&&typeof receipt==='object'?receipts.get(receipt):undefined;assert(selected&&selected.entry===requested&&selected.messageIdentity===messageIdentity,'ForeignOwner','original exact inbound receipt');const command=await prepare(selected.actor,selected.wire,messageIdentity);
   try{const identity=runtime.inspectTransferredCommandIdentity(command.transfer);assert(identity.command_tuple_sha256===selected.tuple,'ForeignOwner','original committed command identity');const observation=await runtime.inspectCommand(command.transfer);assert(observation.kind==='committed'&&observation.outcome.kind==='Returned'&&observation.command_tuple_sha256===identity.command_tuple_sha256,'CommitUnavailable','fresh original database commit inspection required');runtime.assertCurrent();receipts.delete(receipt);return freeze({kind:'committed',commandTupleSha256:observation.command_tuple_sha256,resultSha256:observation.result_sha256});}finally{runtime.disposePrepared(command.prepared);}
  },
 });
}
