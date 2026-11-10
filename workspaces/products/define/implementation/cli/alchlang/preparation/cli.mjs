/** CLI orchestration over native contracts and the existing canonical writer. */
import path from 'node:path';
import {decodeOriginalJson} from '../runtime/wire.mjs';
import {inspectPackage,materializePackage} from '../runtime/package.mjs';
import {readFileSync,realpathSync} from 'node:fs';
import {randomUUID} from 'node:crypto';
import {evaluate,selectors,facts,authorValue} from './native.mjs';
import {prepareRecord,noteCommand,document,documentMap,binding} from './journal.mjs';
import {build} from '../runtime/build.mjs';
import {load,commit,canonical,transition,variant} from '../runtime/runtime.mjs';
export const commands=['context','lookup','revise','fields','inspect-fields','contribute','candidate','assessment','assess','handoff','ack','next','notes','replay','bind','discover'];
export async function run(command,args){
 const required=k=>{if(typeof args[k]!=='string')throw Error('required-option-'+k);return args[k];};
 if(command==='bind')return document(readFileSync(required('--file')));
 const work=required('--work'),loaded=await load(work,{commandId:args['--id']??null}),current=loaded.before??loaded.current;if(!current)throw Error('session-missing');
 if(command==='replay')return {outcome:'verified',head:loaded.head,revision:current.revision,events:loaded.events.length,preparation_notes:loaded.events.filter(e=>e.preparation).length,authority_effect:'none'};
 if(command==='notes')return {head:loaded.head,notes:loaded.events.filter(e=>e.preparation).map(e=>({head:e.event_sha256,note:e.preparation.note,result:e.preparation.output})),authority_effect:'none'};
 if(command==='next'){const last=loaded.events.at(-1),field=['fields','inspect-fields'].includes(last?.preparation?.command)?last.preparation:null;return {revision:current.revision,head:loaded.head,action:await evaluate(selectors.next,{facts:await facts(current),selected_candidates:await authorValue('Define.Work.SelectedCandidateCount',current),report:field?.output??null,report_revision:field?String(BigInt(field.note.expected_revision)+1n):'0',current_revision:current.revision}),authority_effect:'none'};}
 if(command==='discover')return discover(args,current,loaded,required);
 const raw=readFileSync(required('--file'));if(raw.length>12*1024*1024)throw Error('preparation-input-byte-bound');
 const spec=decodeOriginalJson(raw);if(Object.keys(spec).sort().join(',')!=='documents,input')throw Error('preparation-file-requires-input-and-documents');
 const documents=[...spec.documents];documentMap(documents);
 const snapshot=document(Buffer.from(canonical(current)));if(!documents.some(d=>d.binding.path===snapshot.binding.path))documents.push(snapshot);
 const input=spec.input,cut=build().source;
 const observed={session_ref:current.session_id,revision:current.revision,source_cut:cut,closed:current.closed};
 if(command==='lookup')input.observed=observed;
 if(command==='assess'){
  input.observed_snapshot=snapshot.binding;input.observed_facts=await facts(current);input.selected_candidates=await authorValue('Define.Work.SelectedCandidateCount',current);input.applications=await authorValue('Define.Work.ParameterApplicationCount',current);input.materialization_verified=false;input.package_members=null;
  if(args['--package']){const captured=new Map(),{observation}=await inspectPackage(required('--package'),{observe:true,capture:captured});await confirmObservation(current,observation,required('--actor'));await materializePackage(required('--package'),null,{verifyOnly:true});input.package_members=attachMembers(captured,documents);input.materialization_verified=true;}
 }

 if(command==='revise'&&args['--start']){const {observation,body_binding}=await inspectPackage(required('--package'),{observe:true});await confirmObservation(current,observation,required('--actor'));const d=document(readObserved(required('--package'),body_binding));if(!documents.some(x=>x.binding.path===d.binding.path))documents.push(d);input.observed_predecessor=d.binding;}
 if(command==='handoff'){
  const captured=new Map(),{observation}=await inspectPackage(required('--package'),{observe:true,capture:captured});input.package_members=attachMembers(captured,documents);
  await transition(current,{command_id:'handoff-observe',session_id:current.session_id,project:current.scope.project,work:current.scope.work,actor:required('--actor'),expected_revision:current.revision,payload:variant('Confirm',{package_sha256:observation.package_binding.sha256,request_sha256:observation.request_binding.sha256,actor:args['--actor']})},observation);
  const packageDoc=document(readObserved(required('--package'),observation.package_binding)),requestDoc=document(readObserved(required('--package'),observation.request_binding));
  for(const d of [packageDoc,requestDoc])if(!documents.some(x=>x.binding.path===d.binding.path))documents.push(d);
  const addRaw=raw=>{const d=document(Buffer.from(raw));if(!documents.some(x=>x.binding.path===d.binding.path))documents.push(d);return d.binding;};
  input.value.session={...input.value.session,session_ref:current.session_id,revision:current.revision,source_cut:cut,snapshot:snapshot.binding,goal:addRaw(current.scope.goal),intent:addRaw(current.scope.originating_intent),consumer:addRaw(current.scope.consumer),intended_use:current.scope.intended_use,...await facts(current)};
  input.value.package_binding=packageDoc.binding;input.value.request_binding=requestDoc.binding;input.value.exported_request=requestDoc.binding;input.value.observed_request=requestDoc.binding;
 }

 const record=await prepareRecord(current,cut,{command,selector:selectors[command],input,documents,actor:required('--actor'),id:args['--id']??randomUUID()});
 const result=await commit(work,noteCommand(current,record),{preparation:record});
 if(command==='revise'&&args['--start'])return applyRevision(args,current,record,result,required);
 return {outcome:result.outcome,revision:result.revision,head:result.head,note:record.note,result:record.output,authority_effect:'none'};
}
function readObserved(directory,b){const root=realpathSync(directory),file=realpathSync(path.resolve(root,b.path));if(!file.startsWith(root+path.sep))throw Error('observed-file-outside-package');const raw=readFileSync(file),actual=binding(raw);if(actual.sha256!==b.sha256||actual.bytes!==String(b.bytes))throw Error('observed-file-changed');return raw;}
async function discover(args,current,loaded,required){
 const catalog=document(readFileSync(required('--catalog'))),source=decodeOriginalJson(Buffer.from(catalog.bytes_base64,'base64')),query=required('--query');
 if(!Array.isArray(source.entries))throw Error('catalog-requires-entries');const pages=[];
 for(let offset=0;offset<source.entries.length;offset+=25){const entries=source.entries.slice(offset,offset+25).map(e=>({definition_id:e.definition_id,version:e.version,term:e.term,path:e.path,sha256:e.sha256}));pages.push(await evaluate(selectors.search,{query,catalog:catalog.binding,entries}));}
 const documents=[catalog],add=value=>{const d=document(Buffer.from(canonical(value)));if(!documents.some(x=>x.binding.path===d.binding.path))documents.push(d);return d.binding;};
 const queryDocument=add({query,comparison:'exact identifier or term; all selected catalog versions'}),matches=add({pages}),scope=add({catalog:catalog.binding,inspected:source.entries.length,comparison:'exact identifier or term',standing:'reported-source-observation'}),cut=build().source;
 const request={session_ref:current.session_id,session_revision:current.revision,source_cut:cut,concept_ref:query,query_document:queryDocument,selected_sources:catalog.binding,intended_use:current.scope.intended_use};const requestBinding=add(request);
 const input={request,observation:{request:requestBinding,catalog_observation:catalog.binding,candidates:matches,searched_scope:scope,source_cut:cut,posture:'reported-source-observation'},actual_request:requestBinding,observed:{session_ref:current.session_id,revision:current.revision,source_cut:cut,closed:current.closed}};
 const record=await prepareRecord(current,cut,{command:'lookup',selector:selectors.lookup,input,documents,actor:required('--actor'),id:args['--id']??randomUUID()});const result=await commit(required('--work'),noteCommand(current,record),{preparation:record});
 return {outcome:result.outcome,revision:result.revision,head:result.head,results:pages,authority_effect:'none'};
}

async function confirmObservation(current,observation,actor){return transition(current,{command_id:'revision-observe',session_id:current.session_id,project:current.scope.project,work:current.scope.work,actor,expected_revision:current.revision,payload:variant('Confirm',{package_sha256:observation.package_binding.sha256,request_sha256:observation.request_binding.sha256,actor})},observation);}
async function applyRevision(args,original,record,recorded,required){
 const start=decodeOriginalJson(readFileSync(required('--start'))),plan=record.input.plan;
 if(start.request_revision!==plan.next_revision)throw Error('successor-does-not-match-reviewed-revision');
 const concepts=original.required_concepts.map((c,i)=>{const index=original.handling.findIndex(h=>h.fields.value.concept_id===c.concept_id);return {concept_key:binding(Buffer.from(c.concept_id)).sha256,required_index:String(i),handling_index:index<0?null:String(index),handling_kind:index<0?'Absent':original.handling[index].tag};});
 const carry=await evaluate(selectors.carry,{plan,concepts,observed_revision:original.request_revision,unchanged_scope:canonical(start.scope)===canonical(original.scope)});
 const actor=required('--actor'),prefix=record.note.command_ref+':revision:',payloads=[variant('ReviseRequest',{...start,request_lineage:{...start.request_lineage,predecessor_package_binding:record.input.observed_predecessor}})];
 const evaluation=carry.preserve_context?original.context_evaluation:decodeOriginalJson(readFileSync(required('--evaluation')));
 if(evaluation!==null)payloads.push(variant('SetContext',evaluation));
 for(const value of original.source_bindings)payloads.push(variant('BindSource',value));
 for(const value of [...original.evidence_bindings,record.note.body])payloads.push(variant('BindEvidence',value));
 for(const index of carry.required)payloads.push(variant('RequireConcept',original.required_concepts[Number(index)]));
 for(const index of carry.handling)payloads.push(variant('HandleMeaning',original.handling[Number(index)]));
 const sequence=payloads.map((payload,i)=>({command_id:prefix+i,session_id:original.session_id,project:original.scope.project,work:original.scope.work,actor,expected_revision:String(BigInt(record.note.expected_revision)+1n+BigInt(i)),payload}));if(sequence.some(c=>Buffer.byteLength(c.command_id)>256))throw Error('revision-command-id-bound');
 let preview=await transition(original,noteCommand(original,record));for(const next of sequence)preview=await transition(preview,next);
 let result=recorded;for(const next of sequence)result=await commit(required('--work'),next);
 return {outcome:result.outcome,revision:result.revision,head:result.head,selection:carry,request_revision:plan.next_revision,cleared:['applications','assessments','materialization_selection','confirmation'],authority_effect:'none'};
}

function attachMembers(members,documents){const rows=[];for(const [name,raw]of members){const d=document(raw);if(!documents.some(x=>x.binding.path===d.binding.path))documents.push(d);rows.push({path:name,binding:d.binding});}const manifest=document(Buffer.from(canonical(rows)));if(!documents.some(x=>x.binding.path===manifest.binding.path))documents.push(manifest);return manifest.binding;}
