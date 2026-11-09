/** Resolve selected frozen JSON observations; identity/standing rules are compiled inputs. */
import {observeValueFields} from './observe-value-fields.mjs';
import {observeEmbeddedReference} from './embedded-reference.mjs';
export async function resolveArtifactReference({port,call,protocol,reference,body,bodyRef,rows,members}){
 const select=async(value,selector)=>(await port.request({operation:'select-value',value,selector})).value;
 const kind=await select(reference,protocol.reference_kind);
 const embedded=await call(protocol.classify,{kind});
 if(embedded){
  const embedded=await call(protocol.embedded_protocol,{marker:true});
  const observed=await observeEmbeddedReference({port,call,protocol:embedded,reference,body,bodyRef});
  return {...observed,embedded,standing:await call(protocol.local_standing,{marker:true})};
 }
 const key=await select(reference,protocol.reference_key),found=await port.request({operation:'lookup-records',rows,selector:protocol.row_key,key});
 await call(protocol.source_gate,{count:found.count});
 const row=found.values[0],binding=await select(row,protocol.row_binding),metadata=members.get(binding.path);
 if(!metadata)throw Error('captured-byte-reference-unavailable');
 const selected=await port.request({operation:'view-bytes',ref:metadata.ref,selector:await select(reference,protocol.reference_selector)});
 const identity=await port.request({operation:'first-field',value:selected.value,keys:protocol.identity_keys}),revision=await port.request({operation:'first-field',value:selected.value,keys:protocol.revision_keys});
 await call(protocol.field_gate,{present:identity.present});await call(protocol.field_gate,{present:revision.present});
 const steps=await call(protocol.external_facts,{marker:true});
 const documents={reference,row,identity,revision,entry_metadata:selected};Object.assign(documents,await observeValueFields({port,call,selector:protocol.digest_fields,documents}));
 const facts=(await port.request({operation:'construct-value',documents,batches:[steps]})).value;
 await call(protocol.external_gate,facts);
 return {entry:selected.value,metadata:selected,embedded,standing:await select(row,protocol.row_standing),row};
}