/** Capture an explicitly bound local snapshot using source-selected encodings and native gates. */
export async function captureLocalSnapshot({port,call,protocol,requestRef,read,schemaRoot,permitRetention=false,capturedAt}){
 protocol=Object.assign({},...Object.values(protocol));
 const requestMetadata=await port.request({operation:'view-bytes',ref:requestRef}),request=requestMetadata.value,observed=new Map();
 const privacy=await call(protocol.privacy,{marker:true});
 async function validate(selector,value){
  const selected=await call(selector,{marker:true});
  const result=await port.request({operation:'validate-json',root:schemaRoot,value,schema_binding:{...selected.binding,bytes:Number(selected.binding.bytes)},schema_selector:selected.selector});
  if(!result.valid)throw Error('snapshot-structural-contract-invalid');
 }
 async function project(selector,documents,args={marker:true}){return (await port.request({operation:'construct-value',documents,batches:[await call(selector,args)]})).value;}
 async function encoded(value){return port.request({operation:'encode-ref',value});}
 async function binding(path,metadata){return project(protocol.binding_plan,{observed:metadata},{path});}
 const original=await port.request({operation:'byte-metadata',ref:requestRef});
 await call(protocol.statistics_gate,{value:{count:'0',request_bytes:String(original.bytes),parts:[]}});
 await validate(protocol.request_schema,request);
 const declared=await port.request({operation:'collect-json',value:request,schema:protocol.binding_schema,skip_fields:protocol.fields,unique:true});
 for(const item of declared.values){
  await call(protocol.path_gate,{path:item.path});
  let selected=observed.get(item.path);
  if(!selected){selected=await read(item.path,privacy.maximum_file_bytes);observed.set(item.path,selected);}
  const raw=await project(protocol.row_binding_plan,{item,observed:selected.binding}),plan=await call(protocol.facts_codec,{marker:true});
  const facts=(await port.request({operation:'represent-json',value:raw,plan})).value;
  await call(protocol.binding_gate,facts);
  await call(privacy.verify,{value:await port.request({operation:'probe-bytes',ref:selected.ref,markers:privacy.markers,keys:privacy.keys})});
 }
 const sourceRows=Array.from(observed).sort(([a],[b])=>a<b?-1:a>b?1:0),sizes=sourceRows.map(([,row])=>String(row.bytes));
 const parts=[];for(let offset=0;offset<sizes.length;offset+=100)parts.push(sizes.slice(offset,offset+100));
 // The caller supplies the byte observation of the exact request, separately from its decoded value.
 await call(protocol.statistics_gate,{value:{count:String(sourceRows.length),request_bytes:String(original.bytes),parts}});
 const entries=[];for(const [,row]of sourceRows)entries.push(await project(protocol.catalog_entry,{binding:row.binding}));
 const catalog=await project(protocol.catalog_plan,{entries});await validate(protocol.catalog_schema,catalog);
 const catalogMeta=await encoded(catalog),catalogBinding=await binding(protocol.catalog_path,catalogMeta);
 const encoding=await project(protocol.encoding_plan,{}),encodingMeta=await encoded(encoding),encodingBinding=await binding(protocol.encoding_path,encodingMeta);
 const evidence=(await port.request({operation:'select-value',value:request,selector:protocol.evidence_selector})).value,evidenceDigests=[];
 for(const value of evidence)evidenceDigests.push((await port.request({operation:'select-value',value,selector:''})).canonical_value_sha256);
 const evidenceParts=[];for(let offset=0;offset<evidenceDigests.length;offset+=100)evidenceParts.push(evidenceDigests.slice(offset,offset+100));
 const rows=[];
 for(const [,row]of sourceRows){
  const bindingDigest=(await port.request({operation:'select-value',value:row.binding,selector:''})).canonical_value_sha256;
  const external=await call(protocol.evidence,{value:{binding_digest:bindingDigest,parts:evidenceParts}});
  rows.push(await project(protocol.row_plan,{binding:row.binding,request,catalog:catalogBinding,encoding:encodingBinding},{value:{evidence:external,permit_retention:permitRetention}}));
 }
 const args={marker:true};
 const capture=(await port.request({operation:'construct-value',documents:{request,catalog:catalogBinding,rows,clock:{value:capturedAt}},batches:[await call(protocol.header_a,args),await call(protocol.header_b,args)]})).value;
 await validate(protocol.capture_schema,capture);
 const captureMeta=await encoded(capture),members=new Map(sourceRows);
 members.set(protocol.catalog_path,{...catalogMeta,binding:catalogBinding});
 if(rows.length)members.set(protocol.encoding_path,{...encodingMeta,binding:encodingBinding});
 return {capture,capture_metadata:captureMeta,members,request,request_metadata:original};
}