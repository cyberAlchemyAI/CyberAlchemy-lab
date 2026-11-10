import {observeValueFields} from './observe-value-fields.mjs';
/** Derive source-selected artifact projections with native fidelity and lineage gates. */
export async function deriveArtifacts({port,call,snapshot,protocol,resources,schemaRoot,destination,publish=true,finalize=async value=>value,assertSource=async()=>{}}){
 protocol=Object.assign({},...Object.values(protocol));
 const body=snapshot.documents[snapshot.protocol.body_alias];
 const select=async(value,selector)=>(await port.request({operation:'select-value',value,selector})).value;
 const view=async(ref,selector='')=>port.request({operation:'view-bytes',ref,selector});
 const project=async(selector,documents,args={marker:true})=>snapshot.project(selector,documents,args);
 const selections=await select(body,protocol.selection_collection);
 await call(protocol.count_gate,{count:String(selections.length)});
 const output=[],rows=[];
 for(let ordinal=0;ordinal<selections.length;ordinal++){
  const selection=selections[ordinal],kind=await select(selection,protocol.kind_selector),intention=await select(selection,protocol.intention_selector),parent=await select(selection,protocol.parent_selector);
  const successor=await call(protocol.selection_gate,{value:{identity_intention:intention,entry_kind:kind,parent_present:parent!==null}});
  const meaning=(await view(snapshot.body_metadata.ref,await select(selection,protocol.meaning_selector))).value;
  const definitionMeta=await snapshot.readBound(await select(selection,protocol.definition_selector),protocol.namespace),definition=(await view(definitionMeta.ref)).value;
  const checked=await port.request({operation:'validate-json',root:schemaRoot,value:definition,schema_binding:resources.schema,schema_selector:''});
  if(!checked.valid)throw Error('derived-artifact-structural-contract-invalid');
  const lineageMeta=await snapshot.readBound(await select(selection,protocol.lineage_selector),protocol.namespace),lineage=(await view(lineageMeta.ref)).value;
  const structural=await port.request({operation:'validate-value',schema:await call(protocol.lineage_schema,{marker:true}),value:lineage});
  if(!structural.valid)throw Error('lineage-structural-contract-invalid');
  const notation=[];
  for(const parameter of await select(meaning,protocol.parameters_selector))notation.push(await project(protocol.notation_plan,{parameter}));
  const documents={selection,meaning,definition,notation,schema:resources.schema,provider:resources.provider,owner_metadata:await port.request({operation:'json-shape',value:await select(selection,protocol.owner_selector)})};
  Object.assign(documents,await observeValueFields({port,call,selector:protocol.digest_fields,documents}));
  Object.assign(documents,await observeValueFields({port,call,selector:protocol.parent_digest_fields,documents,args:{successor}}));
  const facts=(await port.request({operation:'construct-value',documents,batches:[await call(protocol.facts_a,{marker:true}),await call(protocol.facts_b,{successor})]})).value;
  await call(protocol.fidelity_gate,facts);
  await call(protocol.applicability_gate,await project(protocol.applicability_plan,documents));
  const expected=(await port.request({operation:'value-leaves',value:definition})).selectors.sort();
  const witnesses=await select(lineage,protocol.lineage_collection),indexed=[];
  for(const witness of witnesses)indexed.push({witness,key:await select(witness,protocol.target_selector)});
  indexed.sort((a,b)=>a.key<b.key?-1:a.key>b.key?1:0);
  await call(protocol.statistics_gate,{value:{leaves:String(expected.length),witnesses:String(indexed.length),distinct_count:String(new Set(indexed.map(row=>row.key)).size)}});
  for(let offset=0;offset<expected.length;offset+=100){
   const observations=[];
   for(const {witness,key}of indexed.slice(offset,offset+100)){
    const metadata=await snapshot.readBound(await select(witness,protocol.witness_binding_selector),protocol.namespace);
    const source=await view(metadata.ref,await select(witness,protocol.witness_selector)),target=await view(definitionMeta.ref,key);
    observations.push(await project(protocol.observation_plan,{witness,source,target}));
   }
   await call(protocol.lineage_gate,await project(protocol.batch_plan,{expected:expected.slice(offset,offset+100),observations}));
  }
  const rendered=await port.request({operation:'render-provider',root:schemaRoot,binding:resources.provider,export:protocol.provider_export,value:definition});
  const paths=await project(protocol.paths_plan,{}, {ordinal:String(ordinal)});
  output.push({path:paths.body,ref:definitionMeta.ref},{path:paths.projection,ref:rendered.ref},{path:paths.lineage,ref:lineageMeta.ref});
  rows.push(await project(protocol.report_row,{definition},{value:{ordinal:String(ordinal),body_sha256:definitionMeta.sha256}}));
 }
 const report=await project(protocol.report_header,{resources,rows});
 const encoded=await port.request({operation:'encode-ref',value:report});output.push({path:protocol.report_path,ref:encoded.ref});
 const response=await finalize(report);await assertSource();
 if(publish)await port.request({operation:'publish-refs',destination,members:output});return response;
}