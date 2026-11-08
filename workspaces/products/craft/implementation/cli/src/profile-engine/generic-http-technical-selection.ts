/** Finite technical Alch Mapping selection for the existing injected HTTP slot.
 * This is a profile-input producer. The public HTTP owner still checks the
 * derived physical profile and remains the sole emitted adapter owner.
 * Open Questions: docs/GENERIC-APPLICATIONS.md#open-questions.
 */
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {canonicalJson,captureJson,dataDigest} from './contracts.js';
import {coreFreeze,coreSourceFail as fail} from '../commerce/commerce-core-syntax.js';
import {parseCoreCommerceJson,createCoreCommerceSourceOwner} from '../commerce/commerce-core-source-owner.js';
import {pinCoreImplementation,readCorePhysicalFile,writeCoreExclusiveFile} from '../commerce/commerce-core-physical.js';
import {createGenericSemanticOwner} from '../generic/semantic-reconstruction.js';
import {createGenericComputationDomainOwner,type GenericComputationDomainInspection} from '../generic/computation-domain.js';
import {createGenericSourceComputation} from '../generic/pure-source-stage.js';
import {evaluateGenericComputation} from '../commerce/commerce-computation-evaluate.js';
import {resolveGenericHttpProfile} from '../generic/http-profile.js';
import {createGenericHttpCompositionOwner,requireGenericCompositionRuntime} from '../generic/public-sdk.js';

const at={path:'generic-http-technical-selection',start:0,end:0};
const ext=path.extname(fileURLToPath(import.meta.url));
const pin=pinCoreImplementation(import.meta.url,['../generic/http-profile'+ext]);
const slots=Object.freeze({ApiV1:'/api',ApiV2:'/api/v2'} as const);
type RouteFamily=keyof typeof slots;
type Request=Readonly<{technicalRoot:string;selectionPath:string;baseHttpProfilePath:string;outputHttpProfilePath:string}>;
const closed=(value:unknown,names:readonly string[]):value is Record<string,unknown>=>!!value&&typeof value==='object'&&!Array.isArray(value)&&Object.keys(value).sort().join(',')===[...names].sort().join(',');
const physical=(value:unknown):string=>{
  if(typeof value!=='string'||!path.isAbsolute(value)||path.normalize(value)!==value||value.endsWith(path.sep))fail('InvalidContract',at,'normalized absolute physical path required');
  return value;
};

export interface GenericHttpTechnicalSelectionV1 {
  readonly schema_version:'craft.generic-http-technical-derivation/v1-candidate';
  readonly mapping:'Craft.HttpTechnical.SelectHttp';
  readonly route_family:RouteFamily;
  readonly route_prefix:'/api'|'/api/v2';
  readonly technical_source_capture_sha256:string;
  readonly technical_mapping_contract_sha256:string;
  readonly technical_executable_semantics_sha256:string;
  readonly technical_mapping_source:GenericComputationDomainInspection['source'];
  readonly adapter_code_epoch_sha256:string;
  readonly selection_file:Readonly<{path:string;sha256:string;bytes:number}>;
  readonly base_http_profile_file:Readonly<{path:string;sha256:string;bytes:number}>;
  readonly derived_http_profile_file:Readonly<{path:string;sha256:string;bytes:number}>;
  readonly derived_http_profile_semantics_sha256:string;
  readonly authority_effect:'none';
  readonly qualification:'checked-technical-mapping-to-existing-http-profile-input-only';
}

export function createGenericHttpTechnicalSelectionOwner(){
  pin.assertCurrent();
  const sources=createCoreCommerceSourceOwner(),semantics=createGenericSemanticOwner(sources);
  type Row={capture:ReturnType<typeof sources.prepare>;semantic:ReturnType<typeof semantics.check>;domain:ReturnType<typeof createGenericComputationDomainOwner>;domainHandle:ReturnType<ReturnType<typeof createGenericComputationDomainOwner>['check']>;selection:ReturnType<typeof readCorePhysicalFile>;base:ReturnType<typeof readCorePhysicalFile>;derived:ReturnType<typeof readCorePhysicalFile>;inspection:GenericHttpTechnicalSelectionV1;disposed:boolean};
  const rows=new WeakMap<object,Row>();
  const current=(handle:object)=>{
    pin.assertCurrent();
    const row=rows.get(handle);if(!row)fail('ForeignOwner',at,'original technical selection handle required');
    if(row.disposed)fail('DisposedOwner',at,'technical selection disposed');
    sources.assertCurrent(row.capture);semantics.assertSource(row.semantic,row.capture);row.domain.assertCurrent(row.domainHandle);
    for(const file of [row.selection,row.base,row.derived])if(readCorePhysicalFile(file.file.path).fingerprint!==file.fingerprint)fail('StaleOwner',at,'technical selection or derived HTTP profile changed');
    return row;
  };
  return Object.freeze({
    prepare(request:Request){
      pin.assertCurrent();
      const input=captureJson(request) as unknown;
      if(!closed(input,['technicalRoot','selectionPath','baseHttpProfilePath','outputHttpProfilePath']))fail('InvalidContract',at,'closed technical selection paths required');
      const technicalRoot=physical(input.technicalRoot),selectionPath=physical(input.selectionPath),basePath=physical(input.baseHttpProfilePath),outputPath=physical(input.outputHttpProfilePath);
      if(path.basename(outputPath)!=='http-profile.json'||path.basename(path.dirname(outputPath))!=='contracts'||outputPath===basePath)fail('InvalidContract',at,'new derived contracts/http-profile.json path required');
      const selection=readCorePhysicalFile(selectionPath),selected=parseCoreCommerceJson(selection.text,selection.file.path) as unknown;
      if(!closed(selected,['schema_version','mapping','parameters','slot'])||selected.schema_version!=='craft.generic-http-technical-selection/v1-candidate'||selected.mapping!=='Craft.HttpTechnical.SelectHttp'||selected.slot!=='injected-request-response/v1-candidate'||
        !closed(selected.parameters,['options'])||!closed(selected.parameters.options,['routeFamily'])||!Object.hasOwn(slots,selected.parameters.options.routeFamily as string))fail('UnsupportedCapability',at,'exact finite selected technical Mapping and HTTP slot required');
      const option=selected.parameters.options.routeFamily as RouteFamily;
      const capture=sources.prepare(technicalRoot,'application.alch'),semantic=semantics.check(capture),source=sources.inspect(capture),modulePaths=new Set(source.reconstruction.modules.map(module=>module.path)),texts=source.files.filter(file=>modulePaths.has(file.path));
      const bounds=readCorePhysicalFile(path.join(technicalRoot,'contracts/bounds.json')),
        parsedBounds=parseCoreCommerceJson(bounds.text,bounds.file.path) as {computation?:{limits?:Parameters<typeof createGenericSourceComputation>[2]}};
      if(!parsedBounds.computation?.limits)fail('MissingMapping',at,'original technical Mapping bounds required');
      const domain=createGenericComputationDomainOwner(sources,capture,semantics,semantic),proposal=createGenericSourceComputation(texts,'Craft.HttpTechnical.SelectHttp',parsedBounds.computation.limits),domainHandle=domain.check(proposal.contract),checked=domain.inspect(domainHandle);
      if(checked.contract.source_node!==selected.mapping||checked.contract.result.kind!=='record'||checked.contract.result.name!=='Craft.HttpTechnical.HttpSelection'||checked.contract.inputs.length!==1||checked.contract.inputs[0]?.name!=='options')fail('UnsupportedCapability',at,'selected Mapping must return the finite HTTP selection record');
      const executable=checked.derivation.executable_semantics_sha256;
      if(typeof executable!=='string'||!/^[0-9a-f]{64}$/.test(executable))fail('InvalidContract',at,'checked technical executable identity required');
      const evaluated=evaluateGenericComputation(domain,domainHandle,Buffer.from(canonicalJson({options:{routeFamily:option}})));
      if(!evaluated.ok)fail('UnsupportedCapability',at,'selected technical Mapping evaluation failed');
      const value=parseCoreCommerceJson(Buffer.from(evaluated.wire).toString('utf8'),selectionPath+':evaluated');
      if(!closed(value,['routeFamily'])||!Object.hasOwn(slots,value.routeFamily as string))fail('UnsupportedCapability',at,'technical Mapping returned an unknown native route slot');
      const routeFamily=value.routeFamily as RouteFamily,base=readCorePhysicalFile(basePath),http=resolveGenericHttpProfile(base.text,base.file.path),derivedText=JSON.stringify({...http,route_prefix:slots[routeFamily]},null,2)+'\n';
      resolveGenericHttpProfile(derivedText,outputPath);
      domain.assertCurrent(domainHandle);
      if(readCorePhysicalFile(selectionPath).fingerprint!==selection.fingerprint||readCorePhysicalFile(basePath).fingerprint!==base.fingerprint)fail('StaleOwner',at,'technical selection input changed before profile publication');
      const derived=writeCoreExclusiveFile(outputPath,derivedText);
      const inspection:GenericHttpTechnicalSelectionV1=coreFreeze({schema_version:'craft.generic-http-technical-derivation/v1-candidate',mapping:'Craft.HttpTechnical.SelectHttp',route_family:routeFamily,route_prefix:slots[routeFamily],technical_source_capture_sha256:source.capture_sha256,technical_mapping_contract_sha256:checked.contract_sha256,technical_executable_semantics_sha256:executable,technical_mapping_source:checked.source,adapter_code_epoch_sha256:pin.sha256,selection_file:selection.file,base_http_profile_file:base.file,derived_http_profile_file:derived.file,derived_http_profile_semantics_sha256:dataDigest(resolveGenericHttpProfile(derivedText,outputPath)),authority_effect:'none',qualification:'checked-technical-mapping-to-existing-http-profile-input-only'});
      const handle=Object.freeze({kind:'original-generic-http-technical-selection/v1-candidate'});
      rows.set(handle,{capture,semantic,domain,domainHandle,selection,base,derived,inspection,disposed:false});current(handle);return handle;
    },
    inspect(handle:object){return current(handle).inspection;},
    assertCurrent(handle:object){current(handle);},
    generateJoined(handle:object,httpOwner:ReturnType<typeof createGenericHttpCompositionOwner>,httpHandle:Parameters<ReturnType<typeof createGenericHttpCompositionOwner>['inspect']>[0],selection:{entry:string;outputDirectory:string}){
      const row=current(handle),binding=requireGenericCompositionRuntime(httpOwner,httpHandle),input=captureJson(selection) as unknown;
      if(!closed(input,['entry','outputDirectory'])||typeof input.entry!=='string'||!input.entry||typeof input.outputDirectory!=='string')fail('InvalidContract',at,'exact Entry and new output directory required');
      const output=physical(input.outputDirectory),inspection=httpOwner.inspect(httpHandle);
      if(!inspection.http_profile||inspection.http_profile.sha256!==row.derived.file.sha256||inspection.http_profile.path!=='contracts/http-profile.json'||!inspection.http_contract||inspection.http_contract.profile.route_prefix!==row.inspection.route_prefix||typeof inspection.transport_semantics_sha256!=='string')fail('InvalidContract',at,'original HTTP owner must consume this derived technical profile');
      binding.assertCurrent();
      const manifest=httpOwner.generate(httpHandle,{entry:input.entry,outputDirectory:output});
      current(handle);binding.assertCurrent();
      if(manifest.http_profile?.sha256!==row.derived.file.sha256||manifest.transport_semantics_sha256!==inspection.transport_semantics_sha256)fail('InvalidContract',at,'generated manifest must retain the selected technical HTTP profile');
      const generated=['http-plan.json','system-graph.json','business-system-bridge.json'].map(name=>{
        const captured=readCorePhysicalFile(path.join(output,name)),listed=manifest.files.find(file=>file.path===name);
        if(!listed||listed.sha256!==captured.file.sha256||listed.bytes!==captured.file.bytes)fail('InvalidContract',at,'generated artifact differs from original HTTP owner manifest');
        return {name,file:captured.file,value:parseCoreCommerceJson(captured.text,captured.file.path) as any};
      });
      const [plan,system,bridge]=generated;
      if(!plan||!system||!bridge||plan.value?.contract?.profile?.route_prefix!==row.inspection.route_prefix||plan.value.transport_semantics_sha256!==inspection.transport_semantics_sha256||dataDigest(plan.value.contract)!==dataDigest(inspection.http_contract))fail('InvalidContract',at,'generated HTTP plan differs from checked selected profile');
      const profileSha=row.derived.file.sha256,transportSha=inspection.transport_semantics_sha256;
      const httpNodes=system.value?.nodes?.filter((node:any)=>node.kind==='injected-http-handler');
      const httpLinks=bridge.value?.links?.filter((link:any)=>link.transport_semantics_sha256===transportSha);
      if(!Array.isArray(httpNodes)||!Array.isArray(httpLinks)||httpNodes.length!==inspection.http_contract.entries.length||httpLinks.length!==inspection.http_contract.entries.length||httpNodes.some((node:any)=>node.profile_source?.sha256!==profileSha||node.transport_semantics_sha256!==transportSha)||httpLinks.some((link:any)=>link.profile_source?.sha256!==profileSha))fail('InvalidContract',at,'generated graph and bridge must trace to the selected technical HTTP profile');
      const routes=inspection.http_contract.entries.map((entry:any)=>entry.route.id).sort();
      if(dataDigest(httpNodes.map((node:any)=>node.route.id).sort())!==dataDigest(routes)||dataDigest(httpLinks.map((link:any)=>link.system).sort())!==dataDigest(routes.map((id:string)=>'http:'+id).sort()))fail('InvalidContract',at,'generated graph and bridge route identities differ');
      return coreFreeze({schema_version:'craft.generic-http-technical-lineage/v1-candidate',mapping:row.inspection.mapping,mapping_source:row.inspection.technical_mapping_source,mapping_contract_sha256:row.inspection.technical_mapping_contract_sha256,selection_file:row.selection.file,derived_http_profile_file:row.derived.file,route_family:row.inspection.route_family,route_prefix:row.inspection.route_prefix,entry:input.entry,transport_semantics_sha256:transportSha,generated_files:generated.map(({name,file})=>({name,...file})),authority_effect:'none',qualification:'original-mapping-to-derived-profile-to-original-http-owner-generated-artifacts'});
    },
    dispose(handle:object){const row=current(handle);row.disposed=true;row.domain.dispose(row.domainHandle);semantics.dispose(row.semantic);sources.dispose(row.capture);},
  });
}
