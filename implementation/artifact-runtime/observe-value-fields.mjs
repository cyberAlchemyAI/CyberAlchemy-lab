/** Observe source-selected JSON values without moving those values into a native argument frame. */
export async function observeValueFields({port,call,selector,documents,args={marker:true}}){
 const fields=await call(selector,args),observed=Object.create(null);
 if(!Array.isArray(fields)||fields.length>100)throw Error('field-observation-bound');
 for(const field of fields){
  if(Object.hasOwn(documents,field.alias)||Object.hasOwn(observed,field.alias)||!Object.hasOwn(documents,field.document))throw Error('field-observation-alias-invalid');
  observed[field.alias]=await port.request({operation:'select-value',value:documents[field.document],selector:field.selector,metadata_only:true});
 }
 return observed;
}