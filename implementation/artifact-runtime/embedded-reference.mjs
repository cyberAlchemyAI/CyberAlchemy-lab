import {observeValueFields} from './observe-value-fields.mjs';
/** Observe one embedded reference through source-selected metadata and native gates. */
export async function observeEmbeddedReference({port,call,protocol,reference,body,bodyRef}){
 async function project(selector,documents){return (await port.request({operation:'construct-value',documents,batches:[await call(selector,{marker:true})]})).value;}
 const pointer_metadata=await port.request({operation:'pointer-metadata',selector:reference[protocol.selector_field]});
 await call(protocol.location_selector,await project(protocol.location_plan,{reference,pointer_metadata}));
 const kind=protocol.kinds.find(row=>row.tag===reference[protocol.kind_field]);
 if(!kind)throw Error('native-reference-kind-contract-incomplete');
 const observed=await port.request({operation:'view-bytes',ref:bodyRef,selector:reference[protocol.selector_field]});
 const entry_identity=(await port.request({operation:'select-value',value:observed.value,selector:'/'+kind.identity_field})).value;
 const documents={reference,pointer_metadata,body,entry:observed.value,entry_metadata:observed,entry_identity};Object.assign(documents,await observeValueFields({port,call,selector:protocol.digest_fields,documents}));
 await call(protocol.verify_selector,await project(protocol.observation_plan,documents));
 return {entry:observed.value,metadata:observed};
}
/** Observe references only in source-selected typed regions. */
export async function verifyEmbeddedReferences({port,call,protocol,body,bodyRef}){
 for(const collection of protocol.collections){
  const region=(await port.request({operation:'select-value',value:body,selector:collection})).value;
  const {values}=await port.request({operation:'collect-json',value:region,schema:protocol.schema,skip_fields:protocol.opaque_fields,unique:true});
  for(const reference of values)await observeEmbeddedReference({port,call,protocol,reference,body,bodyRef});
 }
}