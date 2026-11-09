/** Encode exact native-selected ordered construction projections. */
export async function constructNativeData({port,call,selector,documents={},args={marker:true}}){
 const selectors=await call(selector,args);
 if(!Array.isArray(selectors)||selectors.length===0||selectors.length>41)throw Error('native-construction-selection-bound');
 const batches=[];for(const role of selectors)batches.push(await call(role,{marker:true}));
 return (await port.request({operation:'construct-value',documents,batches})).value;
}