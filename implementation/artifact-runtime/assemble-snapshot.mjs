/** Assemble a source-selected artifact pipeline from exact snapshot observations and native decisions. */
import {constructNativeData} from './construct-native-data.mjs';
import {observeValueFields} from './observe-value-fields.mjs';
import {resolveArtifactReference} from './resolve-artifact-reference.mjs';
import {verifyNativeCoverage} from './column-coverage.mjs';
export async function assembleSnapshotArtifact({port,call,protocol,captured,requestRef,schemaRoot}){
 const request=captured.request,capture=captured.capture;
 const select=async(value,selector)=>(await port.request({operation:'select-value',value,selector})).value;
 const meta=async(value,selector='')=>port.request({operation:'select-value',value,selector,metadata_only:true});
 const project=async(selector,documents,args={marker:true})=>(await port.request({operation:'construct-value',documents,batches:[await call(selector,args)]})).value;
 const group=values=>Array.from({length:Math.ceil(values.length/100)},(_,index)=>values.slice(index*100,index*100+100));
 const hashes=async values=>{const output=[];for(const value of values)output.push((await meta(value)).canonical_value_sha256);return output;};
 const column=async(rows,selector)=>(await port.request({operation:'column-values',value:rows,collection:'',selector})).parts.flat();
 async function unique(rows,selector){return call(protocol.uniqueness_gate,{value:await port.request({operation:'describe-column',value:rows,collection:'',selector})});}
 async function schema(role,value,suffix=''){
  const selected=await call(role,{marker:true}),result=await port.request({operation:'validate-json',root:schemaRoot,value,schema_binding:{...selected.binding,bytes:Number(selected.binding.bytes)},schema_selector:selected.selector+suffix});
  if(!result.valid)throw Error('assembled-artifact-structural-contract-invalid');
 }
 const handling=await select(request,protocol.handling_selector),applications=await select(request,protocol.applications_selector),assessments=await select(request,protocol.assessments_selector),selections=await select(request,protocol.selections_selector),rows=await select(capture,protocol.capture_rows);
 const meanings=[],contracts=[],checks=[],fullyBound=[],parameterCache=new Map(),appResolution=new Map(),handlingFlags=[];
 const gapGroups={capture:await select(capture,protocol.capture_gaps),retention:[],open:[],reuse:[],final:[]};
 const predecessor=await port.request({operation:'observe-field',value:request,key:protocol.predecessor_key});
 const request_binding=await project(protocol.control_binding_plan,{observed:captured.request_metadata},{path:protocol.request_path}),capture_binding=await project(protocol.control_binding_plan,{observed:captured.capture_metadata},{path:protocol.capture_path});
 const referenceProtocol=await constructNativeData({port,call,selector:protocol.reference_protocol});
 const allowedSchema=await call(protocol.allowed_schema,{marker:true});
 let body,bodyRef,readiness={},gaps=[],report;
 async function packValue(){const batches=[];for(const role of protocol.pack_parts)batches.push(await call(role,{marker:true}));return (await port.request({operation:'construct-value',documents:{request,capture_binding,request_binding,predecessor,meanings,contracts,gaps,readiness},batches})).value;}
 async function parameters(entry){
  const digest=(await meta(entry)).canonical_value_sha256;if(parameterCache.has(digest))return parameterCache.get(digest);
  const observed=await port.request({operation:'observe-field',value:entry,key:protocol.parameters_key}),shape=await port.request({operation:'json-shape',value:observed.value});
  await call(protocol.parameter_collection_gate,{value:{present:observed.present,kind:shape.kind,size:shape.size}});
  const selected=observed.value;await unique(selected,protocol.parameter_name);
  for(const parameter of selected){
   const declaration=await call(protocol.parameter_schema_resource,{marker:true});
   const valid=await port.request({operation:'validate-json',root:schemaRoot,value:parameter,schema_binding:{...declaration.binding,bytes:Number(declaration.binding.bytes)},schema_selector:declaration.selector+protocol.parameter_schema_suffix});
   await call(protocol.parameter_declaration_gate,{valid:valid.valid});
   const value=await select(parameter,protocol.parameter_schema),allowed=await port.request({operation:'validate-value',schema:allowedSchema,value}),structural=await port.request({operation:'schema-validity',value});
   await call(protocol.parameter_schema_gate,{value:{allowed:allowed.valid,structural:structural.valid}});
  }
  parameterCache.set(digest,selected);return selected;
 }
 const resolve=reference=>resolveArtifactReference({port,call,protocol:referenceProtocol,reference,body,bodyRef,rows,members:captured.members});
 const stages={
  async scope(){
   const permission=await port.request({operation:'json-shape',value:await select(capture,protocol.permission_selector)}),liveObservation=await port.request({operation:'observe-field',value:capture,key:protocol.live_key}),live=await port.request({operation:'json-shape',value:liveObservation.value});
   const documents={request,capture,permission,live};Object.assign(documents,await observeValueFields({port,call,selector:protocol.preparation_scope_fields,documents}));
   await call(protocol.preparation_scope_gate,await project(protocol.preparation_scope_facts,documents));
   for(const row of rows)if(await call(protocol.retention_gap_gate,{posture:await select(row,protocol.source_retention)}))gapGroups.retention.push(await project(protocol.retention_gap_plan,{row}));
  },
  async coverage(){
   const {ref}=await port.request({operation:'put-value',value:request});await verifyNativeCoverage({port,call,protocol:await call(protocol.coverage_protocol,{marker:true}),ref});
  },
  async meanings(){
   for(const item of handling){
    const payload=await select(item,protocol.handling_payload),mode=await port.request({operation:'observe-field',value:payload,key:protocol.handling_mode_key});
    const flags=await call(protocol.handling_flags,{value:{disposition:await select(item,protocol.handling_disposition),mode:mode.value}});handlingFlags.push(flags);
    if(flags.collect_meaning)meanings.push(await select(item,protocol.handling_meaning));
    if(flags.open_gap)gapGroups.open.push(await project(protocol.open_gap_plan,{handling:item}));
   }
   await unique(meanings,protocol.meaning_id);
   for(let ordinal=0;ordinal<meanings.length;ordinal++){
    const meaning=meanings[ordinal];await parameters(meaning);
    const reference=await project(protocol.local_reference_plan,{meaning,request},{value:{ordinal:String(ordinal),entry_digest:(await meta(meaning)).canonical_value_sha256}});
    contracts.push(await project(protocol.local_contract_plan,{meaning,reference}));
   }
   await unique(contracts,protocol.contract_id);body=await packValue();bodyRef=(await port.request({operation:'encode-ref',value:body})).ref;
  },
  async handling(){
   for(let index=0;index<handling.length;index++){
    const item=handling[index],flags=handlingFlags[index];
    if(flags.reuse){const resolved=await resolve(await select(item,protocol.handling_reference));await call(protocol.reuse_standing_gate,{standing:resolved.standing});gapGroups.reuse.push(await project(protocol.reuse_gap_plan,{handling:item}));}
    if(flags.specialization){
     const parent=await select(item,protocol.handling_parent);await resolve(parent);
     if(flags.specialization_application){
      const lookup=await port.request({operation:'lookup-records',rows:applications,selector:protocol.application_id,key:await select(item,protocol.handling_application)}),actual=await port.request({operation:'observe-index',values:lookup.values,index:'0',selector:protocol.application_reference}),selected=await meta(parent);
      await call(protocol.specialization_gate,await project(protocol.specialization_facts,{lookup,actual,selected}));
     }
    }
   }
   await unique(applications,protocol.application_id);await unique(assessments,protocol.assessment_id);
  },
  async 'external-contracts'(){
   for(let index=0;index<applications.length;index++){
    const application=applications[index],reference=await select(application,protocol.application_reference),resolved=await resolve(reference);appResolution.set(index,resolved);
    if(!resolved.embedded){
     await parameters(resolved.entry);
     const contract=await project(protocol.external_contract_plan,{reference,meaning:resolved.entry,source_binding:await select(resolved.row,protocol.source_binding)});
     const lookup=await port.request({operation:'lookup-records',rows:contracts,selector:protocol.contract_id,key:await select(contract,protocol.contract_id)}),actual=await port.request({operation:'observe-index',values:lookup.values,index:'0'}),selected=await meta(contract);
     if(await call(protocol.contract_reuse_gate,await project(protocol.contract_reuse_facts,{lookup,actual,selected})))contracts.push(contract);
    }
   }
   await unique(contracts,protocol.contract_id);
  },
  async applications(){
   for(let index=0;index<applications.length;index++){
    const application=applications[index],resolved=appResolution.get(index),documents={request,application};Object.assign(documents,await observeValueFields({port,call,selector:protocol.scope_fields,documents}));await call(protocol.scope_gate,await project(protocol.scope_facts,documents));
    await parameters(resolved.entry);
    const lookup=await port.request({operation:'lookup-records',rows:contracts,selector:protocol.contract_id,key:await select(application,protocol.application_contract)});await call(protocol.one_contract_gate,{count:lookup.count});
    const contract=lookup.values[0],contractDocuments={application,contract,lookup,selected_reference:await meta(await select(application,protocol.application_reference)),actual_reference:await meta(await select(contract,protocol.contract_reference))};Object.assign(contractDocuments,await observeValueFields({port,call,selector:protocol.contract_fields,documents:contractDocuments}));await call(protocol.contract_gate,await project(protocol.contract_facts,contractDocuments));
    const params=await select(contract,protocol.contract_parameters),values=await select(application,protocol.application_values),origins=await select(application,protocol.application_provenance),bindingGaps=await select(application,protocol.application_gaps),states=[];
    for(const parameter of params){const gapValue=await project(protocol.parameter_gap_plan,{parameter}),gap=await meta(gapValue),parameter_name=await meta(await select(parameter,protocol.parameter_name));states.push(await project(protocol.parameter_state_plan,{parameter,gap,parameter_name}));}
    const names=(await port.request({operation:'object-keys',value:values})).keys,bound_names=await hashes(names),provenance_names=await hashes(await column(origins,protocol.provenance_parameter)),gap_ids=await hashes(await column(bindingGaps,protocol.gap_id));
    const bound=await call(protocol.bindings_gate,await project(protocol.bindings_facts,{application,parameters:states,bound_names,provenance_names,gap_ids,metadata:{gap_count:String(bindingGaps.length)}}));fullyBound.push(bound);
    for(const name of names){
     const declaration=await port.request({operation:'lookup-records',rows:params,selector:protocol.parameter_name,key:name});await call(protocol.one_contract_gate,{count:declaration.count});
     const selectedValue=(await port.request({operation:'observe-field',value:values,key:name})).value,validation=await port.request({operation:'validate-value',schema:JSON.stringify(await select(declaration.values[0],protocol.parameter_schema)),value:selectedValue});
     const originLookup=await port.request({operation:'lookup-records',rows:origins,selector:protocol.provenance_parameter,key:name});await call(protocol.one_value_source_gate,{count:originLookup.count});const provenance=originLookup.values[0];
     const sourceLookup=await port.request({operation:'lookup-records',rows,selector:protocol.source_id,key:await select(provenance,protocol.provenance_input)});await call(protocol.one_value_source_gate,{count:sourceLookup.count});
     const binding=await select(sourceLookup.values[0],protocol.source_binding),source=captured.members.get(binding.path);if(!source)throw Error('captured-byte-reference-unavailable');
     const actual=await port.request({operation:'view-bytes',ref:source.ref,selector:await select(provenance,protocol.provenance_selector),metadata_only:true});
     await call(protocol.value_gate,await project(protocol.value_facts,{validation,selected:await meta(selectedValue),actual,provenance}));
    }
    checks.push(await project(protocol.application_check_plan,{application},{fully_bound:bound,standing:resolved.standing}));
   }
  },
  async assessments(){
   const kinds=await call(referenceProtocol.embedded_protocol,{marker:true});
   for(const assessment of assessments){
    const reference=await select(assessment,protocol.assessment_reference);await call(protocol.reference_subject_gate,{value:{expected:protocol.assessment_subject,actual:reference[kinds.kind_field]}});await resolve(reference);
    for(const reference of await select(assessment,protocol.assessment_methods))await resolve(reference);
    const reason_metadata=await port.request({operation:'json-shape',value:await select(assessment,protocol.reason_selector)}),args=await project(protocol.assessment_codes,{assessment,reason_metadata});
    await call(protocol.assessment_gate,await project(protocol.assessment_facts,{assessment},args));
   }
  },
  async selections(){
   const kinds=await call(referenceProtocol.embedded_protocol,{marker:true});
   for(const selection of selections){const reference=await select(selection,protocol.selection_reference);await call(protocol.reference_subject_gate,{value:{expected:protocol.selection_subject,actual:reference[kinds.kind_field]}});await resolve(reference);const parent=await select(selection,protocol.selection_parent);if(parent!==null)await resolve(parent);}
  },
  async successor(){
   let previous=null;if(predecessor.present){const original=captured.members.get(predecessor.value.path);if(!original)throw Error('captured-byte-reference-unavailable');previous=(await port.request({operation:'view-bytes',ref:original.ref})).value;await schema(protocol.pack_schema,previous);}
   const documents={request,predecessor:previous};Object.assign(documents,await observeValueFields({port,call,selector:protocol.successor_fields,documents,args:{present:predecessor.present}}));await call(protocol.successor_gate,await project(protocol.successor_facts,documents,{present:predecessor.present}));
  },
  async gaps(){
   for(let ordinal=0;ordinal<protocol.final_gap_plans.length;ordinal++)if(await call(protocol.static_gap_gate,{ordinal:String(ordinal),assessments:String(assessments.length)}))gapGroups.final.push(await project(protocol.final_gap_plans[ordinal],{}));
   gaps=protocol.gap_stage_order.flatMap(key=>{if(!Object.hasOwn(gapGroups,key))throw Error('unknown-native-gap-stage');return gapGroups[key];});
  },
  async readiness(){
   const useTarget=await call(protocol.blocking_target,{marker:true}),wanted=(await meta(useTarget)).canonical_value_sha256,effects=await hashes(await column(gaps,protocol.gap_use));
   const blocking=await project(protocol.blocking_use,{}, {value:{wanted,parts:group(effects)}}),counts={application_count:String(applications.length),fully_bound_application_count:await call(protocol.fully_bound_count,{parts:group(fullyBound)}),assessment_count:String(assessments.length),materialization_count:String(selections.length)};
   const fragments=[];
   for(const use of protocol.named_uses){
    const status=await call(protocol.readiness_gate,await project(protocol.readiness_facts,{use,blocking,counts})),filter=await project(protocol.gap_filter,{}, {use});
    const selected=await port.request({operation:'collect-json',value:gaps,schema:JSON.stringify(filter),order:protocol.collection_order}),obligations=await column(selected.values,protocol.gap_id),row=await project(protocol.readiness_record_plan,{obligations},{status});
    fragments.push((await port.request({operation:'construct-value',documents:{row},batches:[await call(protocol.readiness_layout,{marker:true}),await call(protocol.readiness_entry,{use})]})).value);
   }
   readiness=(await port.request({operation:'merge-objects',values:fragments})).value;
  },
  async finalize(){body=await packValue();await schema(protocol.pack_schema,body);report=await project(protocol.report_plan,{capture,checks,readiness});await schema(protocol.report_schema,report);}
 };
 for(const phase of protocol.stage_order){if(!Object.hasOwn(stages,phase))throw Error('unsupported-native-assembly-stage');try{await stages[phase]();}catch(error){throw Error('artifact-stage-'+phase+': '+error.message,{cause:error});}}
 if(!body||!report)throw Error('native-assembly-incomplete');return {body,report};
}