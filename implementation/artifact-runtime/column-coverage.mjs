/** Execute native bounded column-coverage continuations; observations contain no set decisions. */
export async function verifyNativeCoverage({port,call,protocol,ref}){
 const required=await port.request({operation:'describe-column',ref,collection:protocol.required_collection,selector:protocol.key});
 const handled=await port.request({operation:'describe-column',ref,collection:protocol.handled_collection,selector:protocol.key});
 let state=await call(protocol.begin,{value:{source_digest:ref,required_count:required.count,handled_count:handled.count,required_distinct:required.distinct_count,handled_distinct:handled.distinct_count}});
 const tokens=[];for(let offset=0;offset<Number(handled.count);offset+=100){const observed=await port.request({operation:'column-observations',ref,collection:protocol.handled_collection,selector:protocol.key,offset:String(offset),count:'100'});tokens.push(observed.ids);}
 for(let iteration=0;iteration<5;iteration++){
  const effect=await call(protocol.poll,{state});
  if(effect.tag==='Done')return call(protocol.finish,{state});
  if(effect.tag!=='Observe')throw Error('unsupported-native-column-effect');
  const observed=await port.request({operation:'column-observations',ref,collection:protocol.required_collection,selector:protocol.key,...effect.fields});
  state=await call(protocol.accept,{state,value:{...observed,handled:tokens}});
 }
 throw Error('native-column-continuation-bound');
}