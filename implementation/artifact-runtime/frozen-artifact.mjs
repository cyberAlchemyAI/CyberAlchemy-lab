/** Frozen-artifact I/O adapter. Layout, gates, closure and output policy are compiled inputs. */
import {observeValueFields} from './observe-value-fields.mjs';
import {traverseNativeGraph} from './graph-conductor.mjs';
export async function readFrozenArtifact({port,call,read,schemaRoot,protocol,all=false}){
 protocol=Object.assign({},...Object.values(protocol));
 const privacy=await call(protocol.privacy_selector,{marker:true});
 const graph=await call(protocol.graph_selector,{marker:true});
 const frame=Object.create(null),documents=Object.create(null),document_metadata=Object.create(null),metadata=new Map();
 async function probe(ref){const value=await port.request({operation:'probe-bytes',ref,markers:privacy.markers,keys:privacy.keys});await call(privacy.verify,{value});}
 async function schema(selector,value){
  const selected=await call(selector,{marker:true});
  const bytes=Number(selected.binding.bytes);if(!Number.isSafeInteger(bytes)||bytes<0||bytes>16777216)throw Error('schema-resource-bound');
  const checked=await port.request({operation:'validate-json',root:schemaRoot,value,schema_binding:{...selected.binding,bytes},schema_selector:selected.selector});
  if(!checked.valid)throw Error('artifact-structural-contract-invalid');
 }
 async function value(ref){return (await port.request({operation:'view-bytes',ref})).value;}
 async function construct(selector,docs,args={marker:true}){
  const steps=await call(selector,args);
  return (await port.request({operation:'construct-value',documents:docs,batches:[steps]})).value;
 }
 async function facts(selector,docs,args){
  const encoded=await construct(selector,docs,args);
  const plan=await call(protocol.facts_codec,{marker:true});
  return (await port.request({operation:'represent-json',value:encoded,plan})).value;
 }
 frame.manifest_metadata=await read(protocol.manifest_path,privacy.maximum_manifest_bytes);
 await probe(frame.manifest_metadata.ref);
 frame.manifest=await value(frame.manifest_metadata.ref);
 await schema(protocol.manifest_schema,frame.manifest);
 const {ref}=await port.request({operation:'put-value',value:frame.manifest});
 const counts=await port.request({operation:'describe-column',ref,collection:protocol.path_collection,selector:protocol.path_selector});
 await call(protocol.statistics_selector,{value:counts});
 const rows=[];
 const graphCounts=await port.request({operation:'observe-graph',ref,layout:graph.layout,query:{mode:'counts'}});
 for(let index=0;index<Number(graphCounts.nodes);index++){
  const row=await port.request({operation:'observe-graph',ref,layout:graph.layout,query:{mode:'node',index:String(index),parent:null}});rows.push(row.record);
 }
 await port.request({operation:'check-member-paths',paths:[protocol.manifest_path,...rows.map(row=>row[protocol.path_field])]});
 const columns=await port.request({operation:'column-values',ref,collection:protocol.path_collection,selector:protocol.byte_selector,encoding:'uint-decimal'});
 await call(protocol.budget_selector,await construct(protocol.budget_plan,{manifest_metadata:frame.manifest_metadata,columns}));
 const state=await traverseNativeGraph({call,port,ref,protocol:graph});
 const bodyId=(await port.request({operation:'select-value',value:frame.manifest,selector:protocol.body_member_selector})).value;
 const body=await port.request({operation:'observe-graph',ref,layout:graph.layout,query:{mode:'identity',id:bodyId,index:'0',parent:null}});
 await call(protocol.header_available_selector,{found:body.observation.found});
 await call(graph.require_selected,{state,slot:body.observation.slot});
 await call(protocol.header_binding_selector,await construct(protocol.header_binding_plan,{manifest:frame.manifest,item:body.record}));
 const masks=await call(protocol.mask_selector,{state,all}),selected=graph.mask_fields.flatMap(key=>masks[key]);
 for(let index=0;index<rows.length;index++){
  if(!selected[index])continue;
  const row=rows[index],path=row[protocol.path_field],observed=await read(path,privacy.maximum_file_bytes);
  await call(protocol.binding_selector,await facts(protocol.row_binding_plan,{item:row,observed:observed.binding}));
  await probe(observed.ref);metadata.set(path,observed);
 }
 async function linked(binding,prefix){
  const path=prefix+binding.path;
  await call(protocol.member_available_selector,{found:metadata.has(path)});
  const observed=metadata.get(path);
  const args=await facts(protocol.link_binding_plan,{item:binding,observed:observed.binding},{value:{prefix,path:binding.path}});
  await call(protocol.binding_selector,args);return observed;
 }
 const bodyMeta=metadata.get(body.record[protocol.path_field]);
 document_metadata[protocol.body_alias]=bodyMeta;documents[protocol.body_alias]=await value(bodyMeta.ref);await schema(protocol.body_schema,documents[protocol.body_alias]);
 const identityDocuments={manifest:frame.manifest,body:documents[protocol.body_alias]};Object.assign(identityDocuments,await observeValueFields({port,call,selector:protocol.identity_fields,documents:identityDocuments}));
 await call(protocol.identity_selector,await construct(protocol.identity_plan,identityDocuments));
 for(const link of protocol.control_links){
  if(Object.hasOwn(documents,link.alias))throw Error('artifact-document-alias-collision');
  const binding=(await port.request({operation:'select-value',value:documents[link.source],selector:link.selector})).value;
  const observed=await linked(binding,link.prefix);document_metadata[link.alias]=observed;documents[link.alias]=await value(observed.ref);await schema(link.schema,documents[link.alias]);
 }
 for(const scan of protocol.binding_scans){
  const selected=await port.request({operation:'collect-json',value:documents[scan.source],schema:protocol.binding_schema,skip_fields:protocol.opaque_fields,unique:true});
  for(const binding of selected.values)await linked(binding,scan.prefix);
 }
 return {manifest:frame.manifest,manifest_metadata:frame.manifest_metadata,documents,document_metadata,metadata,state,graph,privacy,protocol,body_metadata:bodyMeta,readBound:linked,validateDocument:schema,project:construct,facts};
}