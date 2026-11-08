/** Fixed observer executes existing public factory routes, never computes expected outcomes. */
export const FACTORY_SEMANTIC_RUNNER=String.raw`
async function observeFactory(row){
 const {root,build,constructRecord,view,fingerprint,rejects,reset,metrics}=await createOwnedValueObserver(row);
 const native=await enumImport(row.relative_path),foreignNative=await enumImport(row.relative_path,'?semantic-foreign'),results=[];
 for(const c of row.cases){
  reset();let input,previous,before=null,previousBefore=null,outcome,changed=false;const tracked=[];
  try{
   const request=JSON.parse(c.values[0]),base=native[row.callable]();let factory=base;
   tracked.push([base,fingerprint(base)]);
   for(const id of request.chain){factory=factory.extend(id);tracked.push([factory,fingerprint(factory)]);}
   input=await build(request.input);before=fingerprint(input);
   if(request.previous){previous=await build(request.previous);previousBefore=fingerprint(previous);}
   if(request.route==='extend'){
    factory.extend(input);outcome={kind:'unexpected',type:'extension-accepted'};
   }else{
    const result=request.route==='transition'?factory.transition(previous,input):factory[request.route](input);
    let snapshot=null;
    if(result.ok===true){
     const value=result.value,copyInput=await build(request.input),copyBefore=fingerprint(copyInput),copy=factory.create(copyInput);
     changed ||= copyBefore!==fingerprint(copyInput);
     let foreignFactory=foreignNative[row.callable]();for(const id of request.chain)foreignFactory=foreignFactory.extend(id);
     const foreignInput=await build(request.input),foreignBefore=fingerprint(foreignInput),foreignResult=foreignFactory.create(foreignInput);
     changed ||= foreignBefore!==fingerprint(foreignInput);
     if(!copy.ok||!foreignResult.ok)throw Error('factory copy or foreign witness rejected');
     const baseline=await constructRecord(row.baseline),equal=value[row.kind==='Entity'?'sameIdentity':'equals'];
     snapshot={view:await view(row.shape,value),key:root.key(value),hash:value.hash(),owned:root.isOwned(value),fresh:value!==copy.value,fresh_previous:request.route!=='transition'||value!==previous,equal_copy:root.equals(value,copy.value),equals_baseline:root.equals(value,baseline),
      clone_rejected:rejects(root)({...value}),foreign_rejected:rejects(root)(foreignResult.value),snapshot_copy_equal:equal(copy.value),snapshot_clone_equal:equal({...value}),snapshot_foreign_equal:equal(foreignResult.value),
      metadata:{protocol_id:root.protocol_id,concept:root.concept,contract_sha256:root.contract_sha256,frozen:Object.isFrozen(root)},
      components_frozen:Object.isFrozen(value.components),components:value.components.map(component=>({field:component.field,tag:component.tag,protocol_id:component.protocol_id,protocol_sha256:component.protocol_sha256,frozen:Object.isFrozen(component),field_value_identical:Object.is(component.value,value.fields[component.field])})),
      identity:Object.hasOwn(value,'identity')?{frozen:Object.isFrozen(value.identity),component_index:value.components.indexOf(value.identity.component)}:null};
    }else if(result.value!==null)throw Error('failed factory result contains a value');
    const observed={ok:result.ok,failure_codes:result.failure_codes,trace:{route:result.trace.route,phases:result.trace.phases,validators:result.trace.validators},
     frozen:{result:Object.isFrozen(result),failure_codes:Object.isFrozen(result.failure_codes),trace:Object.isFrozen(result.trace),phases:Object.isFrozen(result.trace.phases),validators:Object.isFrozen(result.trace.validators),validator_rows:result.trace.validators.every(Object.isFrozen)},
     factory:{frozen:Object.isFrozen(factory),extensions:factory.extensions,extensions_frozen:Object.isFrozen(factory.extensions),base_extensions:base.extensions,base_frozen:Object.isFrozen(base),base_extensions_frozen:Object.isFrozen(base.extensions),transition_present:typeof factory.transition==='function'},snapshot};
    outcome={kind:'value',value:semanticJson(observed)};
   }
  }catch(e){outcome={kind:'error',name:e?.name,message:e?.message};}
  changed ||= tracked.some(([value,before])=>before!==fingerprint(value));
  results.push({id:c.id,outcome,getter_reads:metrics().getter_reads,input_changed:changed||metrics().construction_changed||(before!==null&&before!==fingerprint(input))||(previousBefore!==null&&previousBefore!==fingerprint(previous))});
 }
 return {selector:row.selector,cases:results};
}
`;
