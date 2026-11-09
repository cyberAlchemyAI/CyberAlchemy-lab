/** Pure-step continuation conductor. Graph policy belongs to compiled components. */
export async function traverseNativeGraph({call,port,ref,protocol}){
 const maximum=Number(protocol.max_steps);if(!Number.isSafeInteger(maximum)||maximum<1||maximum>131072)throw Error('continuation-step-bound');
 const counts=await port.request({operation:'observe-graph',ref,layout:protocol.layout,query:{mode:'counts'}});
 let state=await call(protocol.init,{value:counts});
 for(let index=0;index<Number(counts.nodes);index++){
  const value=await port.request({operation:'observe-graph',ref,layout:protocol.layout,query:{mode:'node',index:String(index),parent:null}});
  await call(protocol.verify_node,{observation:value.observation});
 }
 for(let step=0;step<maximum;step++){
  const next=await call(protocol.poll,{state});
  if(next.tag==='Compute')state=next.fields.state;
  else if(next.tag==='Read'){
   const value=await port.request({operation:'observe-graph',ref,layout:protocol.layout,query:next.fields.query});
   state=await call(protocol.receive,{state,observation:value.observation});
  }else if(next.tag==='Complete')return next.fields.state;
  else throw Error('unsupported-native-continuation');
 }
 throw Error('continuation-step-bound');
}