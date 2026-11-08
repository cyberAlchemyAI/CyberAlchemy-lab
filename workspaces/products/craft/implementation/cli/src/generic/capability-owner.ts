/** Original source-linked capability formation. Descriptors grant no execution authority.
 * Open Questions: docs/GENERIC-CAPABILITIES.md#open-questions. */
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {coreFreeze,coreSourceFail as fail} from '../commerce/commerce-core-syntax.js';
import {readCorePhysicalFile,pinCorePhysicalCaptures,pinCoreImplementation} from '../commerce/commerce-core-physical.js';
import {assertCoreCommerceSourceOwner,parseCoreCommerceJson,type CoreCommerceSourceOwner,type CoreCommerceSourceCapture} from '../commerce/commerce-core-source-owner.js';
import {assertGenericSemanticOwner,type GenericSemanticOwner,type GenericSemanticCapture} from './semantic-reconstruction.js';
import {dataDigest} from '../profile-engine/contracts.js';
import {validateGenericCapabilitySelection} from './capability-contract.js';
import type {ValueTypeV1} from '../commerce/commerce-data-v1.js';
import type {GenericCapabilitySelectionV1} from './capability-data-v1.js';
import {GENERIC_NATIVE_VECTOR_TYPE_V1} from './capability-data-v1.js';
import type {GenericValueSchemaV1} from './computation-data-v1.js';
import {createCoreGenericComputationContract} from '../commerce/commerce-core-pure-contract.js';
const ext=path.extname(fileURLToPath(import.meta.url)),pin=pinCoreImplementation(import.meta.url,['capability-contract'+ext,'capability-data-v1'+ext,'capability-generation'+ext,'capability-codec'+ext,'capability-dispatch'+ext,'capability-resource'+ext,'../commerce/commerce-computation-kernel'+ext,'../commerce/commerce-core-pure-contract'+ext,'../profile-engine/contracts'+ext,'../profile-engine/coverage'+ext,'../system-integration/kernel-v2'+ext,'../../contracts/generic-capability-v1.schema.json']);
const at={path:'generic-capability',start:0,end:0};
export interface GenericCheckedCapabilityHandle {readonly kind:'original-checked-capabilities/v1'}
export function createGenericCapabilityFormationOwner(sources:CoreCommerceSourceOwner,source:CoreCommerceSourceCapture,semantics:GenericSemanticOwner,semantic:GenericSemanticCapture){
 const current=()=>{pin.assertCurrent();assertCoreCommerceSourceOwner(sources);assertGenericSemanticOwner(semantics);semantics.assertSource(semantic,source);};current();
 const rows=new WeakMap<object,{projection:ReturnType<typeof check>;assertCurrent:()=>void}>();
 function check(selectionPath:string,sourcePath:string,profilePath:string){
  current();for(const file of [selectionPath,sourcePath,profilePath])if(typeof file!=='string'||!path.isAbsolute(file)||path.normalize(file)!==file)fail('InvalidContract',at,'normalized absolute capability inputs required');
  const selectionFile=readCorePhysicalFile(selectionPath),primary=readCorePhysicalFile(sourcePath),profile=readCorePhysicalFile(profilePath),raw=parseCoreCommerceJson(selectionFile.text,selectionPath) as GenericCapabilitySelectionV1;
  if(!raw?.kernel?.path||path.isAbsolute(raw.kernel.path)||raw.kernel.path.split('/').includes('..'))fail('InvalidContract',at,'relative kernel path required');
  const kernelFile=readCorePhysicalFile(path.join(path.dirname(selectionPath),raw.kernel.path)),kernel=parseCoreCommerceJson(kernelFile.text,kernelFile.file.path),selection=validateGenericCapabilitySelection(raw,kernel);
  if(selection.source_sha256!==primary.file.sha256||selection.profile_sha256!==profile.file.sha256)fail('StaleOwner',at,'selection requires exact primary source and selected profile bytes');
  const capture=sources.inspect(source),checked=semantics.inspect(semantic),declarations=capture.reconstruction.modules.flatMap(m=>m.declarations),primaryModule=capture.reconstruction.modules.find(m=>capture.files.some(f=>f.path===m.path&&f.sha256===primary.file.sha256));
  if(!primaryModule||!capture.files.some(f=>f.path===primaryModule.path&&f.sha256===primary.file.sha256))fail('ForeignOwner',at,'capability selection must join the actual checked application sources');
  const resolve=(module:string,name:string)=>{const found=declarations.find(d=>d.id===(name.includes('.')?name:module+'.'+name));if(!found)fail('UnknownReference',at,'source capability reference absent: '+name);return found;};
  const modulePaths=new Set(capture.reconstruction.modules.map(m=>m.path));
  const values:GenericValueSchemaV1='transaction_contract'in checked?checked.transaction_contract.values:'keyed_contract'in checked?checked.keyed_contract.values:createCoreGenericComputationContract(capture.files.filter(f=>modulePaths.has(f.path)),checked.pure.declarations[0]!.name,checked.limits,checked.admission_mode).values;
  const projections=selection.bindings.map(binding=>{
   const iface=declarations.find(d=>d.id===binding.interface);if(!iface||iface.surface!=='Interface'||iface.interface_kind!=='bounded-schema')fail('UnsupportedCapability',at,'capability requires source bounded-schema Interface');
   const exposed=iface.exposes.map(name=>resolve(iface.module,name));
   for(const type of [binding.contract.input_type,...(binding.contract.kind==='inference/v1'&&binding.contract.operation==='vector.embed'&&binding.contract.result_type===GENERIC_NATIVE_VECTOR_TYPE_V1?[]:[binding.contract.result_type])]){const d=resolve(iface.module,type);if(d.surface!=='ValueObject'||!exposed.includes(d))fail('TypeMismatch',iface.syntax,'Interface must expose exact named input/result ValueObjects');}
   const tools=binding.contract.kind==='agent-run/v1'?binding.contract.tools.map(tool=>{
    const entry=checked.entries.find(e=>e.entry===tool.entry),query=checked.reads.find(q=>q.query===tool.query);
    if(!entry||!query||entry.target!==tool.query||entry.target_role!=='Query'||entry.service!==query.service)fail('UnsupportedCapability',iface.syntax,'tool requires exact checked read-only Query Entry');
    if(entry.parameters.length!==1||dataDigest(entry.parameters[0]!.type)!==dataDigest(tool.argument_codec)||dataDigest(entry.result)!==dataDigest(tool.result_codec))fail('TypeMismatch',iface.syntax,'tool requires exact generated argument/result codecs');
    return {...tool,argument_parameter:entry.parameters[0]!.name,entry_sha256:dataDigest(entry),query_sha256:dataDigest(query),argument_codec:entry.parameters[0]!.type,result_codec:entry.result};
   }):[];
   const search_filter_codecs:Record<string,ValueTypeV1>={};
   if(binding.contract.kind==='search/v1'){
    const search=binding.contract.search,collection=declarations.find(d=>d.id===search.collection);
    if(!collection||collection.surface!=='Entity')fail('UnsupportedCapability',iface.syntax,'search requires a checked Entity collection');
    const app='transaction_contract'in checked?checked.transaction_contract:'keyed_contract'in checked?checked.keyed_contract:null,record=app?.values.records.find(r=>r.name===search.collection);if(!record)fail('UnsupportedCapability',iface.syntax,'search requires checked collection codecs');for(const field of search.filter_fields){const codec=record.fields[field];if(!codec||!['scalar','string','literal'].includes(codec.kind))fail('UnsupportedCapability',iface.syntax,'search filter field requires finite scalar codec');search_filter_codecs[field]=codec;}
    if(new Set(search.filter_fields).size!==search.filter_fields.length||new Set(search.filter_operators).size!==search.filter_operators.length||search.filter_fields.some(f=>!collection.fields.some(field=>field.name===f)))fail('UnsupportedCapability',iface.syntax,'only declared collection fields and finite eq/in filters supported');
   }
   const realization=selection.realizations.find(r=>r.id===binding.realization_ref)!;
   const k=kernel as {integration_bindings:{binding_id:string;provider_realization_ref:string}[];provider_realizations:{realization_id:string;provider_profile_ref:string;resource_ref:string;adapter_ref:string}[]},integration=k.integration_bindings.find(v=>v.binding_id===realization.integration_binding_ref)!,resource=k.provider_realizations.find(v=>v.realization_id===integration.provider_realization_ref)!;
   const provider_lineage={integration_binding_ref:integration.binding_id,provider_realization_ref:resource.realization_id,provider_profile_ref:resource.provider_profile_ref,resource_ref:resource.resource_ref,adapter_ref:resource.adapter_ref};
   return {...binding,provider_lineage,search_filter_codecs,source_site:{path:iface.syntax.path,start:iface.syntax.start,end:iface.syntax.end},realization,tools,contract_sha256:dataDigest(binding.contract),realization_sha256:dataDigest(realization)};
  });
  const physical=pinCorePhysicalCaptures([selectionFile,kernelFile,primary,profile]);
  physical.assertCurrent();current();
  return coreFreeze({schema_version:'craft.checked-capability-bindings/v1' as const,selection,selection_sha256:selectionFile.file.sha256,kernel_sha256:selection.kernel.sha256,source_sha256:primary.file.sha256,profile_sha256:profile.file.sha256,source_capture_sha256:capture.capture_sha256,executable_semantics_sha256:checked.executable_sha256,bindings:projections,qualification:'formation-only;native-adapter-and-provider-execution-unrun' as const,authority_effect:'none' as const,physical,values,assets:[{path:'capability-source/selection.json',text:selectionFile.text},{path:'capability-source/'+selection.kernel.path,text:kernelFile.text}]});
 }
 const row=(h:GenericCheckedCapabilityHandle)=>{const r=h&&typeof h==='object'?rows.get(h):undefined;if(!r)fail('ForeignOwner',at,'exact checked capability handle required');current();r.assertCurrent();return r;};
 return Object.freeze({prepare(selectionPath:string,sourcePath:string,profilePath:string){const projection=check(selectionPath,sourcePath,profilePath),h=Object.freeze({kind:'original-checked-capabilities/v1' as const});rows.set(h,{projection,assertCurrent:()=>{current();projection.physical.assertCurrent();}});return h;},inspect(h:GenericCheckedCapabilityHandle){const {physical,values,assets,...projection}=row(h).projection;return coreFreeze(projection);},values(h:GenericCheckedCapabilityHandle){return row(h).projection.values;},assets(h:GenericCheckedCapabilityHandle){return row(h).projection.assets;},assertCurrent(h:GenericCheckedCapabilityHandle){row(h);}});
}
