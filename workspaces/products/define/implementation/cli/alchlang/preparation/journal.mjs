/** Canonical journal attachment transport: original bytes, exact bindings, authored validation. */
import {decodeOriginalJson} from '../runtime/wire.mjs';
import {createHash} from 'node:crypto';
import {assessmentInput,observePackage,membersFromBinding,typedHandoffInput,typedAcknowledgementInput,checkedFields} from './validation.mjs';
import {transition,variant} from '../runtime/runtime.mjs';
import {evaluate,selectors,model,facts,authorValue} from './native.mjs';
const canonical=value=>JSON.stringify(value&&typeof value==='object'?(Array.isArray(value)?value.map(item=>JSON.parse(canonical(item))):Object.fromEntries(Object.keys(value).sort().map(key=>[key,JSON.parse(canonical(value[key]))]))):value);
const sha=raw=>createHash('sha256').update(raw).digest('hex');
const verifiedRecords=new Map();
const verificationKey=(current,sourceCut,command,record,history)=>sha(canonical({current,sourceCut,command,record,history_head:history.at(-1)?.event_sha256??null}));
function remember(key){if(verifiedRecords.size>=10000)verifiedRecords.delete(verifiedRecords.keys().next().value);verifiedRecords.set(key,true);}
export const binding=raw=>({path:'doc_'+sha(raw),sha256:sha(raw),bytes:String(raw.length),digest_kind:'original-file-sha256'});
export function document(raw){raw=Buffer.from(raw);return {binding:binding(raw),bytes_base64:raw.toString('base64')};}
export function documentMap(documents){
 if(!Array.isArray(documents)||documents.length>100)throw Error('preparation-document-count');const map=new Map();let bytes=0;
 for(const d of documents){if(Object.keys(d).sort().join(',')!=='binding,bytes_base64')throw Error('invalid-preparation-document');const raw=Buffer.from(d.bytes_base64,'base64');if(raw.toString('base64')!==d.bytes_base64||canonical(binding(raw))!==canonical(d.binding)||raw.length>16777216)throw Error('preparation-document-binding-mismatch');bytes+=raw.length;if(bytes>8*1024*1024)throw Error('preparation-document-byte-bound');if(map.has(d.binding.path))throw Error('duplicate-preparation-document');map.set(d.binding.path,raw);}return map;
}
export function verifyBindings(value,documents){const map=documents instanceof Map?documents:documentMap(documents);function walk(v){if(!v||typeof v!=='object')return;if(v.digest_kind==='original-file-sha256'){const raw=map.get(v.path);if(!raw||canonical(binding(raw))!==canonical(v))throw Error('missing-or-mismatched-preparation-document:'+v.path);return;}for(const x of Object.values(v))walk(x);}walk(value);return map;}
export async function prepareRecord(current,sourceCut,{command,selector,input,documents,actor,id,history=[]}){
 input=structuredClone(input);documents=structuredClone(documents);
 if(!Object.hasOwn(selectors,command)||selectors[command]!==selector||['kind','next','note','search','view','carry','scopedContext'].includes(command))throw Error('unsupported-preparation-record');
 const observed={session_ref:current.session_id,revision:current.revision,source_cut:sourceCut,closed:current.closed};
 if(command==='lookup'&&canonical(input.observed)!==canonical(observed))throw Error('lookup-observation-not-current');
 if(command==='handoff')await evaluate(selectors.view,{value:input.value.session,observed,facts:await facts(current),snapshot:binding(Buffer.from(canonical(current))),goal:binding(Buffer.from(current.scope.goal)),intent:binding(Buffer.from(current.scope.originating_intent)),consumer:binding(Buffer.from(current.scope.consumer)),intended_use:current.scope.intended_use,project:current.scope.project,work:current.scope.work});
 if(command==='context')await evaluate(selectors.scopedContext,{value:input.value,project:current.scope.project,work:current.scope.work});
 const bytes=verifyBindings(input,documents);
 if(command==='assess'){
  const proof=input.package_members,observation=proof?await observePackage(current,actor,input.value.requested_use,{memoryMembers:membersFromBinding(proof,bytes)}):null;
  input={...await assessmentInput(current,input.value,documents,observation),package_members:proof??null};
 }
 if(command==='handoff'){
  input=await typedHandoffInput(current,sourceCut,input,documents,actor);

 }
 if(command==='ack')input=await typedAcknowledgementInput(current,sourceCut,input,documents,history);
 if(['contribute','inspect-fields'].includes(command))input=await checkedFields(command,input,bytes);
 const output=await evaluate(selector,input);verifyBindings(input,documents);const body=document(Buffer.from(canonical({selector,input,output,documents})));const all=documents;
 const request={command_ref:id,session_ref:current.session_id,expected_revision:current.revision,source_cut:sourceCut,kind:await evaluate(selectors.kind,{command}),body:body.binding,declared_actor:actor};
 const note=await evaluate(selectors.note,{observed:{session_ref:current.session_id,revision:current.revision,source_cut:sourceCut,closed:current.closed},request});
 const record={schema_version:'cal.define.preparation-note/v1',model:model(),command,selector,input,output,note,documents:all};remember(verificationKey(current,sourceCut,noteCommand(current,record),record,history));return record;
}
export async function verifyRecord(current,sourceCut,command,record,{history=[]}={}){
 if(!current||record?.schema_version!=='cal.define.preparation-note/v1'||Object.keys(record).sort().join(',')!=='command,documents,input,model,note,output,schema_version,selector'||record.model!==model())throw Error('unsupported-preparation-record');
 const cacheKey=verificationKey(current,sourceCut,command,record,history);if(verifiedRecords.has(cacheKey))return;
 const actual=await prepareRecord(current,sourceCut,{command:record.command,selector:record.selector,input:record.input,documents:record.documents,actor:command.actor,id:command.command_id,history});
 if(canonical(actual)!==canonical(record))throw Error('preparation-replay-mismatch');
 const expected={command_id:record.note.command_ref,session_id:record.note.session_ref,project:current.scope.project,work:current.scope.work,actor:record.note.declared_actor,expected_revision:record.note.expected_revision,payload:{tag:'BindEvidence',fields:{value:record.note.body}}};
 if(canonical(command)!==canonical(expected))throw Error('preparation-command-mismatch');remember(cacheKey);
}
export const noteCommand=(current,record)=>({command_id:record.note.command_ref,session_id:record.note.session_ref,project:current.scope.project,work:current.scope.work,actor:record.note.declared_actor,expected_revision:record.note.expected_revision,payload:{tag:'BindEvidence',fields:{value:record.note.body}}});
export function evidenceBytes(record){return Buffer.from(canonical({selector:record.selector,input:record.input,output:record.output,documents:record.documents}));}

export function evidenceMembers(events){const members=new Map();for(const event of events){if(!event.preparation)continue;for(const [name,raw]of documentMap(event.preparation.documents))members.set(name,raw);members.set(event.preparation.note.body.path,evidenceBytes(event.preparation));}return members;}
