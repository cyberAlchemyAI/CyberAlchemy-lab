/** Native-slot emission within the existing generic application composer.
 * Open Questions: docs/GENERIC-CAPABILITIES.md#open-questions. */
import {coreFreeze,coreSha256,coreSourceFail as fail} from '../commerce/commerce-core-syntax.js';
import {dataDigest} from '../profile-engine/contracts.js';
import {createCapabilityProfileCoverage} from '../profile-engine/coverage.js';
import {generateGenericCapabilityCodec,generateGenericNativeVectorCodec,type GenericCapabilityCodec} from './capability-codec.js';
import type {createGenericCapabilityFormationOwner} from './capability-owner.js';
import type {GenericValueSchemaV1} from './computation-data-v1.js';
import type {ValueTypeV1} from '../commerce/commerce-data-v1.js';
type Projection=ReturnType<ReturnType<typeof createGenericCapabilityFormationOwner>['inspect']>;
export interface CapabilityArtifact {relative_path:string;content:string}
export interface GenericGeneratedCodec {readonly schema_path:string;readonly decoder_path:string;readonly schema_sha256:string;readonly decoder_sha256:string;readonly type:ValueTypeV1|{readonly kind:'native-vector';readonly dimensions:number}}
export function generateGenericCapabilityWiring(projection:Projection,values:GenericValueSchemaV1){
 const at={path:'capability-generation',start:0,end:0},files:CapabilityArtifact[]=[],json=(v:unknown)=>JSON.stringify(v,null,2)+'\n';
 if(projection.bindings.length!==projection.selection.bindings.length)fail('InvalidContract',at,'complete selected binding denominator required');
 const nativeResources=new Set<string>();
 const codec=(base:string,type:ValueTypeV1,max_bytes:number,max_items:number):GenericGeneratedCodec=>{
  const c:GenericCapabilityCodec=generateGenericCapabilityCodec(values,type,{id:base,max_bytes,max_items});
  const schema_path=base+'.schema.json',decoder_path=base+'.codec.mjs';files.push({relative_path:schema_path,content:json(c.schema)},{relative_path:decoder_path,content:c.source});
  return {schema_path,decoder_path,schema_sha256:c.schema_sha256,decoder_sha256:c.codec_sha256,type:c.type};
 };
 const bindings=projection.bindings.map(b=>{
  if(nativeResources.has(b.provider_lineage.resource_ref))fail('InvalidContract',b.source_site,'competing selected native resource owners');nativeResources.add(b.provider_lineage.resource_ref);
  if(b.contract.kind==='agent-run/v1'){
   if(b.tools.length&&(!b.realization.capabilities.includes('readonly-tools')||b.bounds.max_tool_calls<1))fail('UnsupportedCapability',b.source_site,'selected agent tools require mediated read-only tool support and bounds');
  }
  const base='capabilities/'+coreSha256(b.id),input=codec(base+'/input',{kind:'record',name:b.contract.input_type},b.bounds.max_input_bytes,b.bounds.max_items);
  let result:GenericGeneratedCodec;
  if(b.contract.kind==='inference/v1'&&b.contract.operation==='vector.embed'){
   const c=generateGenericNativeVectorCodec(b.contract.embedding!.dimensions,{id:base+'/result',max_bytes:b.bounds.max_output_bytes});
   result={schema_path:base+'/result.schema.json',decoder_path:base+'/result.codec.mjs',schema_sha256:c.schema_sha256,decoder_sha256:c.codec_sha256,type:c.type};files.push({relative_path:result.schema_path,content:json(c.schema)},{relative_path:result.decoder_path,content:c.source});
  }else result=codec(base+'/result',{kind:'record',name:b.contract.result_type},b.bounds.max_output_bytes,b.bounds.max_items);
  const tools=b.tools.map(t=>({...t,argument:codec(base+'/tools/'+coreSha256(t.name)+'/argument',t.argument_codec,b.bounds.max_input_bytes,b.bounds.max_items),result:codec(base+'/tools/'+coreSha256(t.name)+'/result',t.result_codec,b.bounds.max_output_bytes,b.bounds.max_items)}));
  return {id:b.id,interface:b.interface,source_site:b.source_site,contract:b.contract,contract_sha256:b.contract_sha256,realization:b.realization,realization_sha256:b.realization_sha256,provider_lineage:b.provider_lineage,bounds:b.bounds,input,result,tools,tool_mediation:b.contract.kind==='agent-run/v1'?'original-c02-query-context/v1':'disabled',harness_owner:b.contract.kind==='agent-run/v1'?b.realization.target.model_or_harness:null};
 });
 const plan=coreFreeze({schema_version:'craft.generic-capability-wiring/v1' as const,artifact_contract:'new-capability-wiring/v1' as const,source_sha256:projection.source_sha256,profile_sha256:projection.profile_sha256,selection_sha256:projection.selection_sha256,kernel_sha256:projection.kernel_sha256,executable_semantics_sha256:projection.executable_semantics_sha256,bindings,files:files.map(f=>({path:f.relative_path,sha256:coreSha256(f.content),bytes:Buffer.byteLength(f.content)})),qualification:'generated-dispatch-and-business-codecs;native-package-load-and-provider-qualification-separate' as const,authority_effect:'none' as const});
 const coverage=createCapabilityProfileCoverage({...plan,bindings:bindings.map(b=>({id:b.id,interface:b.interface,source_path:b.source_site.path,artifact_refs:['capabilities.mjs',b.input.schema_path,b.input.decoder_path,b.result.schema_path,b.result.decoder_path],tools:b.tools.map(t=>({name:t.name,entry:t.entry,artifact_refs:[t.argument.decoder_path,t.result.decoder_path,'capabilities.mjs']}))}))});
 files.push({relative_path:'capability-wiring.json',content:json(plan)},{relative_path:'capability-coverage.json',content:json(coverage)},
  {relative_path:'capabilities.mjs',content:"// Generated extension of the original application owner; no provider starts on import.\nimport {createGenericGeneratedCapabilityOwner} from '@domainspec-v2/cli/generic';\nconst plan="+JSON.stringify(plan)+";\nexport function createGeneratedCapabilityOwner(composition,handle,options){return createGenericGeneratedCapabilityOwner(import.meta.url,plan,composition,handle,options);}\n"});
 if(new Set(files.map(f=>f.relative_path)).size!==files.length||files.length>2048||files.reduce((n,f)=>n+Buffer.byteLength(f.content),0)>33554432)fail('ResourceLimit',at,'bounded unique capability artifact closure required');
 return coreFreeze({plan,coverage,files,plan_sha256:dataDigest(plan)});
}
