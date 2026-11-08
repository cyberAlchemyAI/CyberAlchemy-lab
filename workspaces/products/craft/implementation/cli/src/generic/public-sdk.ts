import {assertPolicyEnforcementProfile} from '../commerce/commerce-policy-enforcement.js';
import {projectPolicyEnforcementLineage,type PolicyEnforcementLineage} from './policy-enforcement-lineage.js';
/** Cumulative generated composition SDK. C01 grants only pure Rule custody.
 * Open Questions: docs/GENERIC-APPLICATIONS.md#open-questions. */
import {mkdirSync,mkdtempSync} from 'node:fs';
import path from 'node:path';
import {tmpdir} from 'node:os';
import {stripTypeScriptTypes} from 'node:module';
import {fileURLToPath} from 'node:url';
import {AsyncLocalStorage} from 'node:async_hooks';
import {types as nodeTypes} from 'node:util';
import {publishAtomicDirectory} from '../generation/atomic-publication.js';
import {createCoreCommerceReviewOwner,type CoreCommerceReviewCapture,type CoreCommerceAcceptedReview} from '../commerce/commerce-core-review-owner.js';
import {dataDigest,captureJson} from '../profile-engine/contracts.js';
import {coreFreeze,coreSha256,coreRelativePath,CoreCommerceSourceError,coreSourceFail as fail} from '../commerce/commerce-core-syntax.js';
import {readCorePhysicalFile,writeCoreExclusiveFile,pinCoreImplementation,pinCorePhysicalCaptures,withCorePhysicalIdentityPhase} from '../commerce/commerce-core-physical.js';
import {createCoreCommerceSourceOwner,parseCoreCommerceJson,type CoreCommerceSourceCapture} from '../commerce/commerce-core-source-owner.js';
import {createCoreCommerceSemanticOwner,type CoreCommerceSemanticCapture} from '../commerce/commerce-core-semantic-owner.js';
import {reconstructCoreCommerceModule,reconstructCoreCommerceSources} from '../commerce/commerce-core-reconstruction.js';
import {captureExternalProfile,generateExternalBusinessSources} from './external-read-profile.js';
import {createExternalApiComposition,EXTERNAL_GENERATION_PATH,EXTERNAL_COMPOSITION_PATH} from './external-read-source.js';
import {createCoreValueTypes,coreGenericAdmissionMode,type CoreGenericAdmissionMode} from '../commerce/commerce-core-types.js';
import {createCoreContextCatalog} from '../commerce/commerce-core-context.js';
import {createCoreCommerceComputationContract} from '../commerce/commerce-core-pure-contract.js';
import {createOriginalPureComputationDomainOwner,createOriginalPureOperationDomainOwner,createOriginalGenericMappingDomainOwner,type CommerceComputationDomainOwner} from '../commerce/commerce-computation-domain.js';
import {evaluateCommerceComputation,evaluateGenericComputation} from '../commerce/commerce-computation-evaluate.js';
import {compileCommerceComputationTypeScript,compileGenericComputationTypeScript} from '../commerce/commerce-computation-native.js';
import {admitGenericComposition,GENERIC_COMPOSITION_CAPABILITIES} from './composition-capabilities.js';
import {resolveGenericPureProfile,PURE_PROFILE_RECIPE,PURE_OPERATION_RECIPE,PURE_MAPPING_RECIPE,PURE_CALCULATION_RECIPE,PURE_VALUE_RECIPE,PURE_STATE_RECIPE} from './profile-resolver.js';
import {createOrderedMappingComputation} from './pure-mapping.js';
import {createPureOperationComputation,assertPureOperationPlan} from './pure-operation.js';
import {requireLegacyExpressionData} from '../commerce/commerce-core-pure.js';
import {createSourceSemanticBridge,type SemanticCapture,type ReviewCapture,type AcceptedReview} from './pure-bridge.js';
import {createGenericComputationDomainOwner,type GenericComputationDomainOwner} from './computation-domain.js';
import type {GenericSemanticCapture} from './semantic-reconstruction.js';
import {createGenericSourceComputation} from './pure-source-stage.js';
import {exportGenericFiniteBoolSmtModel} from './formal-finite-bool.js';
import {exportCheckedGenericPureExpressionFormalFromWireV1} from './formal-pure-expression-v1.js';
import {exportCheckedGenericFiniteBoolListFormalModelV1} from './formal-finite-bool-list-v1.js';
import {exportGenericStructuralAlloyModel} from './formal-structural-alloy.js';
import {exportGenericWorkflowTlaModel} from './formal-workflow-tla.js';
import type {createGenericServiceArtifactOwner,GenericServiceArtifactHandle} from './service-artifact-owner.js';
import {createGenericSemanticOwner} from './semantic-reconstruction.js';
import {createGenericSourceReviewOwner,type GenericReviewCapture,type GenericAcceptedReview} from './source-review-owner.js';
import {createGenericRepositoryPlanOwner,type GenericRepositoryPlanOwner,type GenericKeyedApplicationHandle,type GenericTransactionApplicationHandle} from './repository-plan.js';
import {KEYED_AUTH_SOURCE,KEYED_AUTH_CONTEXT} from './readonly-control.js';
import {resolveGenericKeyedProfile,KEYED_PROFILE_RECIPE} from './profile-resolver.js';
import {deriveGenericStorageDescriptor,deriveGenericTransactionStorageDescriptor,deriveGenericExternalWriteStorageDescriptor,deriveGenericEventStorageDescriptor} from './value-codec.js';
import {createGenericOperationAssembly} from './operation-assembly.js';
import {deriveGenericReachableOperationSemantics} from './identity.js';
import type {GenericRuntimeOptions,GenericApplicationRuntime,GenericTransactionApplicationRuntime} from './invocation-owner.js';
import type {ComputationLimitsV1} from '../commerce/commerce-data-v1.js';
import {resolveGenericTransactionProfile,resolveGenericEventProfile,resolveGenericTransactionBounds,TRANSACTION_PROFILE_RECIPE,EVENT_PROFILE_RECIPE} from './profile-resolver.js';
import {genericClaimReference} from './assurance-source.js';
import type {GenericTransactionAuthoredInputV1,GenericTransactionAuthoredFileV1} from './transaction-data-v1.js';
import type {GenericTransactionApplicationContractV1} from './transaction-data-v1.js';
import type {GenericExternalTransactionApplicationV1} from './external-read-data-v1.js';
import type {GenericExternalWriteTransactionApplicationV1} from './external-write-data-v1.js';
import type {GenericEventTransactionApplicationV1} from './event-data-v1.js';
import {createGenericWorkflowSourceContract,type GenericWorkflowSourceContractV1} from './workflow-source.js';
import {createGenericHttpSourceContract} from './entry-http-source.js';
import {resolveGenericHttpProfile} from './http-profile.js';
import {projectGenericHttpTransport} from './http-projection.js';
import {createGenericHttpHandler} from './http-adapter.js';
import {resolveGenericExternalWriteSelection} from './external-write-profile.js';
import {createGenericCapabilityFormationOwner,type GenericCheckedCapabilityHandle} from './capability-owner.js';
import {generateGenericCapabilityWiring} from './capability-generation.js';
export {createGenericGeneratedCapabilityOwner} from './capability-dispatch.js';
const ext=path.extname(fileURLToPath(import.meta.url));
const pin=pinCoreImplementation(import.meta.url,['policy-enforcement-lineage'+ext,'../commerce/commerce-policy-enforcement'+ext,'identity'+ext,'pure-bridge'+ext,'semantic-reconstruction'+ext,'source-review-owner'+ext,'computation-domain'+ext,'pure-source-stage'+ext,'formal-finite-bool'+ext,'formal-pure-expression-v1'+ext,'formal-finite-bool-list-v1'+ext,'formal-workflow-event-join-v1'+ext,'pure-operation'+ext,'pure-mapping'+ext,'../commerce/commerce-computation-evaluate'+ext,'composition-capabilities'+ext,'profile-resolver'+ext,'../commerce/commerce-computation-native'+ext,'../commerce/commerce-computation-domain'+ext,'../commerce/commerce-core-review-owner'+ext,'../generation/atomic-publication'+ext,'../generation/atomic-publication-native'+ext,'../generation/atomic-publication-native.generated'+ext]);
const at={path:'composition',start:0,end:0};
function generatedManifestContent(manifest:unknown){
 // Manifests repeat checked source and graph metadata. Formatting must not
 // make otherwise bounded applications impossible to reopen in the SDK.
 const content=JSON.stringify(manifest)+'\n';
 if(Buffer.byteLength(content)>1048576)fail('ResourceLimit',at,'generated manifest exceeds the original 1 MiB bundle reader bound');
 return content;
}
/** Join checked static lineage into the original artifact views, never runtime evidence. */
function addPolicyEnforcementArtifacts(artifacts:{relative_path:string;content:string}[],lineage:PolicyEnforcementLineage):void {
 if(!lineage.nodes.length)return;
 for(const artifact of artifacts){
  if(artifact.relative_path==='system-graph.json'){
   const graph=JSON.parse(artifact.content);graph.nodes.push(...lineage.nodes);graph.edges.push(...lineage.edges);artifact.content=JSON.stringify(graph,null,2)+'\n';
  }else if(artifact.relative_path==='business-system-bridge.json'){
   const bridge=JSON.parse(artifact.content);bridge.links.push(...lineage.links);artifact.content=JSON.stringify(bridge,null,2)+'\n';
  }
 }
}
const capabilityFormations=new WeakMap<object,{owner:ReturnType<typeof createGenericCapabilityFormationOwner>;handle:GenericCheckedCapabilityHandle}>();
function capabilityProjection(h:GenericCompositionHandle){const r=capabilityFormations.get(h);return r?r.owner.inspect(r.handle):null;}
const capabilityGenerations=new WeakMap<object,ReturnType<typeof generateGenericCapabilityWiring>>();
function capabilityGeneration(h:GenericCompositionHandle){const r=capabilityFormations.get(h);if(!r)fail('UnsupportedCapability',at,'selected capability source required');r.owner.assertCurrent(r.handle);let g=capabilityGenerations.get(h);if(!g){g=generateGenericCapabilityWiring(r.owner.inspect(r.handle),r.owner.values(r.handle));capabilityGenerations.set(h,g);}return g;}
type CapabilityGenerationBinding={generation:()=>ReturnType<typeof generateGenericCapabilityWiring>;assertCurrent:()=>void};
const capabilityParents=new WeakMap<object,(h:GenericCompositionHandle)=>CapabilityGenerationBinding>();
/** Internal original-parent join. Inert generated plans cannot mint this binding. */
export function requireGenericCapabilityGenerationBinding(owner:unknown,h:GenericCompositionHandle):CapabilityGenerationBinding{const get=owner&&typeof owner==='object'?capabilityParents.get(owner):undefined;if(!get)fail('ForeignOwner',at,'original application owner required');return get(h);}
/** Internal join used only after the original runtime registry validates its parent. */
export function requireGenericCapabilityProjection(h:GenericCompositionHandle){const projection=capabilityProjection(h);if(!projection)fail('UnsupportedCapability',at,'selected checked native capabilities required');return projection;}
function addCapabilityArtifacts(h:GenericCompositionHandle,artifacts:{relative_path:string;content:string}[]){
 const projection=capabilityProjection(h);if(!projection)return;
 const generated=capabilityGeneration(h),parent=capabilityFormations.get(h)!;
 const json=(value:unknown)=>JSON.stringify(value,null,2)+'\n';
 for(const artifact of artifacts){if(artifact.relative_path==='system-graph.json'){const graph=JSON.parse(artifact.content);graph.nodes.push(...projection.bindings.map(b=>({id:'capability:'+b.id,kind:'checked-native-capability-formation',interface:b.interface,contract_sha256:b.contract_sha256,realization_sha256:b.realization_sha256,provider_lineage:b.provider_lineage,scope:projection.qualification})));artifact.content=json(graph);}if(artifact.relative_path==='business-system-bridge.json'){const bridge=JSON.parse(artifact.content);bridge.links.push(...projection.bindings.map(b=>({business:b.interface,system:'capability:'+b.id,selection_sha256:projection.selection_sha256,profile:projection.profile_sha256,source_capture_sha256:projection.source_capture_sha256,kernel_sha256:projection.kernel_sha256,contract_sha256:b.contract_sha256,realization_sha256:b.realization_sha256,provider_lineage:b.provider_lineage,scope:projection.qualification})));artifact.content=json(bridge);}}
 for(const artifact of artifacts){if(artifact.relative_path==='system-graph.json'){const graph=JSON.parse(artifact.content);for(const b of generated.plan.bindings){const node=graph.nodes.find((n:{id:string})=>n.id==='capability:'+b.id);Object.assign(node,{kind:'generated-native-capability-dispatch',artifact:'capabilities.mjs',input_schema:b.input.schema_path,result_schema:b.result.schema_path,source_to_profile:{source:projection.source_sha256,profile:projection.profile_sha256},scope:generated.plan.qualification});graph.nodes.push({id:'capability-resource:'+b.id,kind:b.contract.kind==='agent-run/v1'?'selected-agent-harness':'selected-native-resource',resource:b.provider_lineage.resource_ref,package:b.realization.implementation,contract:b.contract.kind,harness_owner:b.harness_owner,tool_mediation:b.tool_mediation,authority_effect:'none'});}artifact.content=json(graph);}if(artifact.relative_path==='business-system-bridge.json'){const bridge=JSON.parse(artifact.content);for(const b of generated.plan.bindings){const link=bridge.links.find((n:{system:string})=>n.system==='capability:'+b.id);Object.assign(link,{artifact:'capabilities.mjs',result_schema_sha256:b.result.schema_sha256,result_decoder_sha256:b.result.decoder_sha256,harness_owner:b.harness_owner,tools:b.tools.map(t=>({name:t.name,entry:t.entry,query:t.query,argument_codec_sha256:t.argument.decoder_sha256,result_codec_sha256:t.result.decoder_sha256})),scope:generated.plan.qualification});}artifact.content=json(bridge);}}
 artifacts.push({relative_path:'capability-bindings.json',content:json(projection)},...generated.files,...parent.owner.assets(parent.handle).map(f=>({relative_path:'model/'+f.path,content:f.text})));
 const paths=artifacts.map(f=>f.relative_path);if(new Set(paths).size!==paths.length)fail('InvalidContract',at,'generated capability artifacts conflict with existing application artifacts');
}
function capabilityOverlay(h:GenericCompositionHandle,artifacts:{relative_path:string;content:string}[]){
 const r=capabilityFormations.get(h);if(!r)return {};
 if(artifacts.length>128||artifacts.some(f=>Buffer.byteLength(f.content)>1048576))fail('ResourceLimit',at,'capability wiring exceeds the original generated bundle bounds');
 const files=(rows:{path:string;text:string}[])=>rows.map(f=>({path:f.path,sha256:coreSha256(f.text),bytes:Buffer.byteLength(f.text)}));
 const generated=artifacts.filter(f=>f.relative_path==='capability-bindings.json'||capabilityGeneration(h).files.some(g=>g.relative_path===f.relative_path)).map(f=>({path:f.relative_path,text:f.content}));
 return {capabilities:{schema_version:'craft.generic-capability-overlay/v1',selection_path:'capability-source/selection.json',assets:files([...r.owner.assets(r.handle)]),generated:files(generated),plan_sha256:capabilityGeneration(h).plan_sha256}};
}
function checkCapabilityOverlay(raw:any,known:Map<string,{path:string;sha256:string;bytes:number}>){
 if(!raw||typeof raw!=='object'||Object.keys(raw).sort().join(',')!=='assets,generated,plan_sha256,schema_version,selection_path'||raw.schema_version!=='craft.generic-capability-overlay/v1'||raw.selection_path!=='capability-source/selection.json'||!Array.isArray(raw.assets)||raw.assets.length!==2||!Array.isArray(raw.generated)||raw.generated.length<7||raw.generated.length>120||!/^[a-f0-9]{64}$/.test(raw.plan_sha256))fail('InvalidContract',at,'closed generated capability overlay required');
 const refs=new Set<string>();for(const [prefix,rows]of [['model/',raw.assets],['',raw.generated]] as const)for(const f of rows){if(!f||typeof f!=='object'||Object.keys(f).sort().join(',')!=='bytes,path,sha256'||!coreRelativePath(f.path)||refs.has(prefix+f.path)||!Number.isSafeInteger(f.bytes)||f.bytes<0||f.bytes>1048576||!/^[a-f0-9]{64}$/.test(f.sha256))fail('InvalidContract',at,'exact bounded capability file pins required');if(prefix? !f.path.startsWith('capability-source/'):!f.path.startsWith('capabilities/')&&!['capabilities.mjs','capability-bindings.json','capability-wiring.json','capability-coverage.json'].includes(f.path))fail('InvalidContract',at,'reserved capability artifact namespace required');const actual=known.get(prefix+f.path);if(!actual||actual.sha256!==f.sha256||actual.bytes!==f.bytes)fail('InvalidContract',at,'capability overlay differs from complete bundle file inventory');refs.add(prefix+f.path);}
 if(!refs.has('model/'+raw.selection_path)||!refs.has('capabilities.mjs')||!refs.has('capability-wiring.json'))fail('InvalidContract',at,'capability selection and generated dispatch closure required');return refs;
}

function captureKeyedPackage(){const physical=readCorePhysicalFile(fileURLToPath(new URL('../../package.json',import.meta.url))),manifest=parseCoreCommerceJson(physical.text,physical.file.path) as any;if(manifest?.name!==KEYED_PROFILE_RECIPE.runtime_package||manifest?.version!==KEYED_PROFILE_RECIPE.runtime_package_version)fail('InvalidContract',at,'exact selected runtime package name/version required');return physical;}

/** Internal source-stage helper, deliberately absent from the public index.
 * Runtime/accepted-plan dispatch joins this capture only after genuine B4/B5.
 * Open Questions: docs/GENERIC-APPLICATIONS.md#open-questions. */
export function prepareGenericTransactionSources(proposal:unknown){
 const input=captureTransactionPreparation(proposal);
 const compare=(a:string,b:string)=>Buffer.compare(Buffer.from(a,'utf8'),Buffer.from(b,'utf8'));
 const root=path.dirname(input.sourcePath),primary=path.basename(input.sourcePath);
 const modulePaths=[primary,...input.additionalSourcePaths];
 const fixed=['application.alch','generated/auth-context.alch','generated/auth-context.json','contracts/selected-profile.json','contracts/bounds.json','contracts/transactions.json','contracts/workflow-profile.json',...(input.httpProfilePath?['contracts/http-profile.json']:[]),...(input.externalProfilePath?['contracts/external-profile.json','contracts/external-config.json',EXTERNAL_GENERATION_PATH,EXTERNAL_COMPOSITION_PATH]:[]),...(input.externalWriteSelectionPath?['contracts/external-write-bindings.json']:[])];
 const collides=(a:string,b:string)=>a===b||a.startsWith(b+'/')||b.startsWith(a+'/');
 if(new Set(modulePaths).size!==modulePaths.length||modulePaths.some((p,i)=>fixed.some(f=>collides(p,f))||modulePaths.slice(0,i).some(q=>collides(p,q))))fail('InvalidContract',at,'authored source paths collide with each other or exact generated/configuration files');
 type Physical=ReturnType<typeof readCorePhysicalFile>;
 type Authored={path:string;physical:Physical};
 const authored:Authored[]=modulePaths.map(p=>({path:p,physical:readCorePhysicalFile(path.join(root,p))}));
 if(input.externalProfilePath&&authored.some(f=>f.path.startsWith('generated/external-')||f.path.startsWith('contracts/external-')))fail('InvalidContract',at,'external generated paths are reserved');
 const bounds=readCorePhysicalFile(path.join(root,'contracts/bounds.json')),transactions=readCorePhysicalFile(path.join(root,'contracts/transactions.json')),profile=readCorePhysicalFile(input.profilePath),httpProfile=input.httpProfilePath?readCorePhysicalFile(input.httpProfilePath):undefined;
 const raw=parseCoreCommerceJson(bounds.text,bounds.file.path) as {schema_version?:unknown;computation?:{required_schema_version?:unknown;required_semantics_revision?:unknown;limits?:ComputationLimitsV1}};
 if(raw?.schema_version!=='craft.generic-compute-bounds/v1-candidate'||raw.computation?.required_schema_version!=='craft.generic-computation/v1-candidate'||raw.computation?.required_semantics_revision!=='ordered-metered-generic-v1-candidate'||!raw.computation.limits)fail('MissingMapping',at,'exact authored generic computation bounds required');
 const profileData=parseCoreCommerceJson(profile.text,profile.file.path) as {schema_version?:unknown};
 const eventMode=profileData?.schema_version==='craft.generic-event-profile/v1-candidate';
 const selected=eventMode?resolveGenericEventProfile(profile.text,profile.file.path,raw.computation.limits,resolveGenericTransactionBounds(transactions.text,transactions.file.path)):resolveGenericTransactionProfile(profile.text,profile.file.path,raw.computation.limits,resolveGenericTransactionBounds(transactions.text,transactions.file.path));
 if(httpProfile)resolveGenericHttpProfile(httpProfile.text,httpProfile.file.path);
 const recipe=eventMode?EVENT_PROFILE_RECIPE:TRANSACTION_PROFILE_RECIPE;
 if(input.externalWriteSelectionPath&&!input.externalProfilePath)fail('InvalidContract',at,'external write selection requires the selected external read profile');
 const writeSelection=input.externalWriteSelectionPath?readCorePhysicalFile(input.externalWriteSelectionPath):undefined;
 if(writeSelection)resolveGenericExternalWriteSelection(parseCoreCommerceJson(writeSelection.text,writeSelection.file.path));
 const external=input.externalProfilePath?captureExternalProfile(input.externalProfilePath,root):undefined,mode=eventMode?'event-handoff-entry' as const:input.externalWriteSelectionPath?'external-write-entry' as const:external?'external-read-entry' as const:'atomic-state-entry' as const;
 const modules=authored.map(f=>reconstructCoreCommerceModule(f.physical.text,f.path));
 assertPolicyEnforcementProfile(modules.flatMap(m=>m.declarations),selected.capabilities);
 const workflows=modules.flatMap(m=>m.declarations.filter(d=>d.surface==='Workflow'));
 if(workflows.length>1||workflows.some(d=>!eventMode||d.syntax.rule!=='generic-workflow-declaration'))fail('UnsupportedCapability',at,'one cumulative Event-mode generic Workflow supported');
 const workflowProfile=workflows.length?readCorePhysicalFile(path.join(root,'contracts/workflow-profile.json')):undefined;
 const claims=new Map<string,Physical>();let claimCount=0,claimBytes=0;
 for(const m of modules){
  if(m.module==='Craft.Generated.Auth'||m.module.startsWith('Craft.Generated.Auth.')||external&&(m.module==='Craft.Generated.External'||m.module.startsWith('Craft.Generated.External.'))||m.module==='CraftGenerated.Root'||m.module.startsWith('CraftGenerated.Root.'))fail('InvalidContract',m.syntax,'generated namespace is reserved');
  for(const d of m.declarations){
   if(!['Rule','ValueObject','Enum','Operation','Mapping','Calculation','Policy','StateMachine','Entity','Query','Entry','FormalClaim',...(eventMode?['Event',...(d.syntax.rule==='generic-workflow-declaration'?['Workflow']:[])]:[])].includes(d.surface)&&!(d.surface==='Interface'&&(d.interface_kind==='bounded-schema'||external&&d.interface_kind==='external')))fail('UnsupportedCapability',d.syntax,'business-only atomic declarations required');
   if(d.surface==='FormalClaim'){
    if(++claimCount>16)fail('ResourceLimit',d.syntax,'opaque claim count bound');
    const ref=genericClaimReference(d,m.path);
    if([...modulePaths,...fixed,...claims.keys()].some(p=>p!==ref.path&&collides(p,ref.path))||[...modulePaths,...fixed].includes(ref.path))fail('InvalidContract',d.syntax,'claim path collides with authored or generated files');
    if(!claims.has(ref.path)){const f=readCorePhysicalFile(path.join(root,ref.path),262144);claims.set(ref.path,f);claimBytes+=f.file.bytes;if(claimBytes>262144)fail('ResourceLimit',d.syntax,'opaque claim aggregate byte bound');}
   }
  }
 }
 const nativePaths=[...new Set(authored.flatMap(f=>[...f.physical.text.matchAll(/^\s*binding\s+([^\s]+\.json)\s*$/gm)].map(match=>match[1]!)))];
 if(nativePaths.some(p=>!coreRelativePath(p)||!p.startsWith('native/'))||nativePaths.length>(writeSelection?16:0))fail('InvalidContract',at,'bounded normalized native binding paths required for selected external write');
 const nativeFiles=nativePaths.map(p=>({path:p,physical:readCorePhysicalFile(path.join(root,p))}));
 const sortedModules=modulePaths.slice().sort(compare);
 const baseApplication='module CraftGenerated.Root version 1\ninterface Application:\n  kind application-composition\n'+sortedModules.map(p=>'  source '+p+'\n').join('')+'  source generated/auth-context.alch\n'+selected.services.map(s=>'  service '+s.id+' module '+s.module+'\n').join('')+'  computation-bounds contracts/bounds.json\n  parameters contracts/selected-profile.json\n';
 const initialSources=[...authored.map(f=>({path:f.path,text:f.physical.text})),{path:'application.alch',text:baseApplication},{path:'generated/auth-context.alch',text:KEYED_AUTH_SOURCE}];
 const generated=external?generateExternalBusinessSources(external,reconstructCoreCommerceSources(initialSources,mode),authored.map(f=>({path:f.path,text:f.physical.text})),initialSources,eventMode?'event-handoff-entry':'external-read-entry'):undefined;
 const externalFiles:{path:string;text:string}[]=[];
 if(external&&generated){
  externalFiles.push(...generated.files,{path:'contracts/external-profile.json',text:external.profile.text},{path:'contracts/external-config.json',text:external.configuration.text},{path:EXTERNAL_COMPOSITION_PATH,text:JSON.stringify(createExternalApiComposition(generated.bindings),null,2)+'\n'},{path:'contracts/external-assets/profile.json',text:external.manifest.text});
  for(const declared of external.recipes.values())externalFiles.push({path:'contracts/external-recipes/'+dataDigest(declared.data.id)+'.json',text:declared.physical.text});
  for(const f of external.templateFiles){const asset=(JSON.parse(external.manifest.text) as {assets:{path:string;sha256:string}[]}).assets.find(a=>a.sha256===f.file.sha256&&f.file.path.endsWith('/'+a.path));if(!asset)fail('InvalidContract',at,'captured external asset absent');externalFiles.push({path:'contracts/external-assets/'+asset.path,text:f.text});}
  const inventory=externalFiles.filter(f=>f.path!=='contracts/external-profile.json'&&f.path!=='contracts/external-config.json').map(f=>({path:f.path,sha256:coreSha256(f.text),bytes:Buffer.byteLength(f.text)}));
  const generation={schema_version:'craft.generic-external-generation/v1-candidate',bindings:generated.bindings,calls:generated.calls,files:inventory,recipes:[...external.recipes.values()].map(r=>({id:r.data.id,path:'contracts/external-recipes/'+dataDigest(r.data.id)+'.json'})),authored_paths:modulePaths,template_manifest:'contracts/external-assets/profile.json'};
  externalFiles.push({path:EXTERNAL_GENERATION_PATH,text:JSON.stringify(generation,null,2)+'\n'});
 }
 const applicationText=baseApplication+(generated?generated.files.map(f=>'  source '+f.path+'\n').join('')+'  external-bindings contracts/external-profile.json\n  external-config contracts/external-config.json\n':'')+(httpProfile?'  http-bindings contracts/http-profile.json\n':'');
 reconstructCoreCommerceModule(applicationText,'application.alch');
 const model=[...authored.map(f=>({path:f.path,text:f.physical.text})),...Array.from(claims,([path,physical])=>({path,text:physical.text})),...nativeFiles.map(f=>({path:f.path,text:f.physical.text})),...(writeSelection?[{path:'contracts/external-write-bindings.json',text:writeSelection.text}]:[]),...(workflowProfile?[{path:'contracts/workflow-profile.json',text:workflowProfile.text}]:[]),...(httpProfile?[{path:'contracts/http-profile.json',text:httpProfile.text}]:[]),{path:'contracts/bounds.json',text:bounds.text},{path:'contracts/transactions.json',text:transactions.text},{path:'contracts/selected-profile.json',text:profile.text},{path:'application.alch',text:applicationText},{path:'generated/auth-context.alch',text:KEYED_AUTH_SOURCE},{path:'generated/auth-context.json',text:JSON.stringify(KEYED_AUTH_CONTEXT,null,2)+'\n'},...externalFiles].sort((a,b)=>compare(a.path,b.path));
 if(new Set(model.map(f=>f.path)).size!==model.length)fail('InvalidContract',at,'authored/generated external path collision');
 if(model.length>128||model.reduce((n,f)=>n+Buffer.byteLength(f.text,'utf8'),0)>4194304)fail('ResourceLimit',at,'complete authored and generated source closure bound');
 const originals=[...authored.map(f=>f.physical),...claims.values(),...nativeFiles.map(f=>f.physical),...(writeSelection?[writeSelection]:[]),...(workflowProfile?[workflowProfile]:[]),...(httpProfile?[httpProfile]:[]),bounds,transactions,profile];
 const originalPin=pinCorePhysicalCaptures(originals);
 const assertOriginal=()=>{pin.assertCurrent();transactionSourcePin.assertCurrent();external?.assertCurrent();originalPin.assertCurrent();};
 assertOriginal();
 const writeModel=(prefix:string)=>{const directory=mkdtempSync(path.join(tmpdir(),prefix));for(const f of model){const destination=path.join(directory,f.path);mkdirSync(path.dirname(destination),{recursive:true});writeCoreExclusiveFile(destination,f.text);}return directory;};
 const sources=createCoreCommerceSourceOwner(mode),semantics=createGenericSemanticOwner(sources,mode);
 const source=sources.prepare(writeModel('craft-atomic-logical-'),'application.alch'),semantic=semantics.check(source),logical=sources.inspect(source),checked=semantics.inspect(semantic);
 const expandedSources=createCoreCommerceSourceOwner(mode),expandedSemantics=createGenericSemanticOwner(expandedSources,mode);
 const expanded=expandedSources.prepare(writeModel('craft-atomic-expanded-'),'application.alch'),expandedSemantic=expandedSemantics.check(expanded),expansion=expandedSources.inspect(expanded),actual=expandedSemantics.inspect(expandedSemantic);
 if(checked.admission_mode!==mode||actual.admission_mode!==mode)fail('InvalidContract',at,'actual atomic source semantics required');
 const inventory=(capture:typeof logical)=>capture.files.map(({path,sha256,bytes})=>({path,sha256,bytes})).sort((a,b)=>compare(a.path,b.path));
 const expected=model.map(f=>({path:f.path,sha256:coreSha256(f.text),bytes:Buffer.byteLength(f.text,'utf8')}));
 if(dataDigest(inventory(logical))!==dataDigest(expected)||dataDigest(inventory(expansion))!==dataDigest(expected))fail('InvalidContract',at,'captured closure must include every exact authored and generated file');
 const comparableWorkflows=(rows:typeof checked.workflows)=>rows.map(({source_capture_sha256:_capture,...rest})=>rest);
 if(checked.executable_sha256!==actual.executable_sha256||checked.assurance_sha256!==actual.assurance_sha256||dataDigest(checked.transaction_contract)!==dataDigest(actual.transaction_contract)||dataDigest(comparableWorkflows(checked.workflows))!==dataDigest(comparableWorkflows(actual.workflows)))fail('InvalidContract',at,'expanded atomic semantics, Workflow or assurance differ from original reconstructed source');
 const httpChecked=httpProfile?createGenericHttpSourceContract(logical):undefined,httpExpanded=httpProfile?createGenericHttpSourceContract(expansion):undefined;
 if(httpChecked&&httpExpanded&&(httpChecked.transport_semantics_sha256!==httpExpanded.transport_semantics_sha256||httpChecked.executable_sha256!==httpExpanded.executable_sha256||dataDigest(httpChecked.contract)!==dataDigest(httpExpanded.contract)))fail('InvalidContract',at,'expanded HTTP profile or checked routes differ from original source');
 const authoredPaths=new Set(modulePaths);
 const graph=(capture:typeof logical,sem:typeof checked,businessOnly:boolean,httpExecutable?:string)=>{
  const modules=capture.reconstruction.modules.filter(m=>!businessOnly||authoredPaths.has(m.path)),ids=new Set(modules.flatMap(m=>m.declarations.map(d=>d.id)));
  return {admission_mode:sem.admission_mode,capture_sha256:capture.capture_sha256,executable_semantics_sha256:httpExecutable??sem.executable_sha256,...(httpExecutable?{base_executable_semantics_sha256:sem.executable_sha256}:{}),nodes:modules.flatMap(m=>m.declarations.map(d=>({id:d.id,kind:d.surface,source:{path:m.path,sha256:m.sha256,start:d.syntax.start,end:d.syntax.end}}))),ownership:capture.reconstruction.ownership.filter(o=>!businessOnly||ids.has(o.declaration))};
 };
 const file=(relative:string):GenericTransactionAuthoredFileV1=>{const f=logical.files.find(f=>f.path===relative);if(!f)fail('UnknownReference',at,'authored file missing from actual physical closure');return {path:f.path,sha256:f.sha256,bytes:f.bytes};};
 const authoredRecords={primary_source:file(primary),additional_sources:input.additionalSourcePaths.slice().sort(compare).map(file),computation_bounds:file('contracts/bounds.json'),transaction_bounds:file('contracts/transactions.json'),claim_assets:[...claims.keys()].sort(compare).map(file),profile:file('contracts/selected-profile.json')};
 const relativeOrigin=(capture:typeof logical)=>({authored:authoredRecords,...(httpProfile?{http_profile:file('contracts/http-profile.json')}:{}),...(workflowProfile?{workflow_profile:file('contracts/workflow-profile.json')}:{}),...(external?{external_profile:file('contracts/external-profile.json'),external_config:file('contracts/external-config.json'),external_generation:file(EXTERNAL_GENERATION_PATH)}:{}),...(writeSelection?{external_write_selection:file('contracts/external-write-bindings.json'),native_files:nativeFiles.map(f=>file(f.path))}:{}),modules:capture.reconstruction.modules.filter(m=>authoredPaths.has(m.path)).slice().sort((a,b)=>compare(a.path,b.path)).map(m=>({path:m.path,sha256:m.sha256,module:m.module,declarations:m.declarations.map(d=>({id:d.id,kind:d.surface,start:d.syntax.start,end:d.syntax.end}))})),assurance:checked.assurance});
 const origin=dataDigest(relativeOrigin(logical));
 if(origin!==dataDigest(relativeOrigin(expansion)))fail('InvalidContract',at,'expanded model-relative authored origin changed');
 const authoredInput:GenericTransactionAuthoredInputV1=coreFreeze({schema_version:'craft.generic-transaction-authored-input/v1-candidate',...authoredRecords,source_origin_sha256:origin});
 const originalFiles=[...authored.map(f=>({path:f.path,role:f.path===primary?'primary-source':'additional-source',physical:f.physical})),...Array.from(claims,([path,physical])=>({path,role:'claim-asset',physical})),...nativeFiles.map(f=>({...f,role:'native-profile'})),...(writeSelection?[{path:'contracts/external-write-bindings.json',role:'external-write-selection',physical:writeSelection}]:[]),...(workflowProfile?[{path:'contracts/workflow-profile.json',role:'workflow-profile',physical:workflowProfile}]:[]),...(httpProfile?[{path:'contracts/http-profile.json',role:'http-profile',physical:httpProfile}]:[]),{path:'contracts/bounds.json',role:'computation-bounds',physical:bounds},{path:'contracts/transactions.json',role:'transaction-bounds',physical:transactions},{path:'contracts/selected-profile.json',role:'profile',physical:profile}].sort((a,b)=>compare(a.path,b.path)).map(f=>({model_path:f.path,role:f.role,original:{...f.physical.file,capture_fingerprint:f.physical.fingerprint}}));
 const reviews=createGenericSourceReviewOwner(expandedSemantics);
 const inspection=coreFreeze({schema_version:'craft.generic-composition-inspection/v1-candidate',source:{original_files:originalFiles},authored_input:authoredInput,profile:{id:selected.id,path:profile.file.path,sha256:profile.file.sha256,recipe,recipe_sha256:dataDigest(recipe)},logical:graph(logical,checked,true,httpChecked?.executable_sha256),expanded:{...graph(expansion,actual,false,httpExpanded?.executable_sha256),origins:[{declaration:'CraftGenerated.Root.Application',kind:'technical',recipe_sha256:dataDigest(recipe)},{module:'Craft.Generated.Auth',kind:'technical',recipe_sha256:dataDigest(recipe)},...modules.map(m=>({module:m.module,kind:'unchanged-business',source:file(m.path)}))]},assurance:actual.assurance,reachable_operations:[...actual.transaction_contract.pure_operations.map(plan=>({operation:plan.operation.module+'.'+plan.operation.name,semantic_sha256:dataDigest(plan)})),...actual.transaction_contract.readonly_operations.map(plan=>({operation:plan.operation,semantic_sha256:dataDigest(plan)})),...actual.transaction_contract.stateful_operations.map(plan=>({operation:plan.operation,semantic_sha256:dataDigest(plan)}))],transaction_contract:actual.transaction_contract,...(httpChecked?{http_profile:file('contracts/http-profile.json'),http_contract:httpChecked.contract,transport_semantics_sha256:httpChecked.transport_semantics_sha256}:{}),...(workflowProfile?{workflow_profile:file('contracts/workflow-profile.json'),workflow_contract:actual.workflows[0]}:{}),...(external?{external_profile:file('contracts/external-profile.json'),external_config:file('contracts/external-config.json'),external_generation:file(EXTERNAL_GENERATION_PATH),external_contract:actual.transaction_contract}:{}),...(writeSelection?{external_write_selection:file('contracts/external-write-bindings.json'),native_profiles:nativeFiles.map(f=>file(f.path))}:{}),capabilities:selected.capabilities,limits:selected.limits,qualification:httpChecked?'http-source-capture-only;runtime-pending':'atomic-source-capture-only;runtime-pending',authority_effect:'none'});
 // These are Core-owned synchronous source/semantic checks only. Reuse the
 // existing physical phase to coalesce nested pin samples and recheck them on
 // exit. No identity is retained across calls, callbacks, awaits or effects.
 const assertCurrent=()=>withCorePhysicalIdentityPhase(()=>{assertOriginal();sources.assertCurrent(source);semantics.assertSource(semantic,source);expandedSources.assertCurrent(expanded);expandedSemantics.assertSource(expandedSemantic,expanded);});
 assertCurrent();
 return Object.freeze({sources,source,semantics,semantic,expandedSources,expanded,expandedSemantics,expandedSemantic,reviews,inspection,authoredInput,assertCurrent});
}
const transactionSourcePin=pinCoreImplementation(import.meta.url,['assurance-source'+ext,'transaction-data-v1'+ext,'profile-resolver'+ext,'../commerce/commerce-core-source-owner'+ext,'semantic-reconstruction'+ext]);
function captureTransactionPreparation(proposal:unknown):{sourcePath:string;profilePath:string;additionalSourcePaths:readonly string[];externalProfilePath?:string;externalWriteSelectionPath?:string;httpProfilePath?:string;capabilitySelectionPath?:string}{
 if(!proposal||typeof proposal!=='object'||nodeTypes.isProxy(proposal)||Array.isArray(proposal))fail('InvalidContract',at,'plain preparation input required');
 const proto=Object.getPrototypeOf(proposal);
 if(proto!==Object.prototype&&proto!==null)fail('InvalidContract',at,'plain preparation input required');
 const descriptors=Object.getOwnPropertyDescriptors(proposal),keys=Reflect.ownKeys(descriptors);
 if(keys.some(k=>typeof k!=='string'||!['sourcePath','profilePath','additionalSourcePaths','externalProfilePath','externalWriteSelectionPath','httpProfilePath','capabilitySelectionPath'].includes(k))||!Object.hasOwn(descriptors,'sourcePath')||!Object.hasOwn(descriptors,'profilePath'))fail('InvalidContract',at,'closed preparation input required');
 for(const key of keys){const d=descriptors[key as string]!;if(!Object.hasOwn(d,'value')||!d.enumerable)fail('InvalidContract',at,'own enumerable data preparation fields required');}
 const absolute=(v:unknown):string=>{if(typeof v!=='string'||v.length>4096||!path.isAbsolute(v)||path.normalize(v)!==v||v.endsWith('/')||/[\\\u0000-\u001f\u007f]/.test(v))fail('InvalidContract',at,'normalized absolute physical file required');return v;};
 const sourcePath=absolute(descriptors.sourcePath!.value),profilePath=absolute(descriptors.profilePath!.value);
 if(!sourcePath.endsWith('.alch'))fail('InvalidContract',at,'primary source must be .alch');
 const result:string[]=[];
 if(Object.hasOwn(descriptors,'additionalSourcePaths')){
  const value:unknown=descriptors.additionalSourcePaths!.value;
  if(!value||typeof value!=='object'||nodeTypes.isProxy(value)||!Array.isArray(value)||Object.getPrototypeOf(value)!==Array.prototype)fail('InvalidContract',at,'ordinary dense additional source array required');
  const ds=Object.getOwnPropertyDescriptors(value),length=Object.getOwnPropertyDescriptor(value,'length');
  if(!length||!Object.hasOwn(length,'value')||!Number.isSafeInteger(length.value)||length.value<0||length.value>31)fail('ResourceLimit',at,'at most 31 additional authored sources');
  const n=length.value;
  if(Reflect.ownKeys(ds).length!==n+1)fail('InvalidContract',at,'dense additional source array without extra properties required');
  for(let i=0;i<n;i++){const d=ds[String(i)];if(!d||!d.enumerable||!Object.hasOwn(d,'value'))fail('InvalidContract',at,'own data absolute .alch path required');const full=absolute(d.value),relative=path.relative(path.dirname(sourcePath),full);if(!coreRelativePath(relative)||!full.endsWith('.alch'))fail('InvalidContract',at,'absolute .alch path beneath primary directory required');result.push(relative);}
 }
 const externalWriteSelectionPath=Object.hasOwn(descriptors,'externalWriteSelectionPath')?absolute(descriptors.externalWriteSelectionPath!.value):undefined;
 const httpProfilePath=Object.hasOwn(descriptors,'httpProfilePath')?absolute(descriptors.httpProfilePath!.value):undefined;
 if(externalWriteSelectionPath&&externalWriteSelectionPath!==path.join(path.dirname(sourcePath),'contracts/external-write-bindings.json'))fail('InvalidContract',at,'write selection must be the source-root contract');
 return Object.freeze({sourcePath,profilePath,additionalSourcePaths:Object.freeze(result),...(Object.hasOwn(descriptors,'capabilitySelectionPath')?{capabilitySelectionPath:absolute(descriptors.capabilitySelectionPath!.value)}:{}),...(Object.hasOwn(descriptors,'externalProfilePath')?{externalProfilePath:absolute(descriptors.externalProfilePath!.value)}:{}),...(externalWriteSelectionPath?{externalWriteSelectionPath}:{}),...(httpProfilePath?{httpProfilePath}:{})});
}


export interface GenericCompositionHandle {readonly kind:'original-generic-composition/v1-candidate'}
const keyedPin=pinCoreImplementation(import.meta.url,['identity'+ext,'readonly-control'+ext,'repository-plan'+ext,'value-codec'+ext,'semantic-reconstruction'+ext,'source-review-owner'+ext,'profile-resolver'+ext]);
export type GenericPureSelection={rule:string}|{operation:string}|{mapping:string}|{calculation:string}|{policy:string};
export type GenericSelection=GenericPureSelection|{entry:string};
export interface GenericKeyedCompositionRuntimeBinding {
 readonly plans:GenericRepositoryPlanOwner;
 readonly application:GenericKeyedApplicationHandle;
 readonly assertCurrent:()=>void;
 readonly assertEffectCurrent?:()=>void;
 readonly withCommandCurrentnessScope?:<T>(work:()=>Promise<T>)=>Promise<T>;
}
export interface GenericTransactionCompositionRuntimeBinding {readonly plans:GenericRepositoryPlanOwner;readonly application:GenericTransactionApplicationHandle;readonly assertCurrent:()=>void;readonly assertEffectCurrent?:()=>void;readonly withCommandCurrentnessScope?:<T>(work:()=>Promise<T>)=>Promise<T>}
export type GenericCompositionRuntimeBinding=GenericKeyedCompositionRuntimeBinding|GenericTransactionCompositionRuntimeBinding;
const compositionRegistry=new WeakMap<object,(handle:GenericCompositionHandle)=>GenericCompositionRuntimeBinding>();
export interface GenericWorkflowRuntimeBinding {
 readonly contract:GenericWorkflowSourceContractV1;
 readonly derivation:ReturnType<typeof createGenericWorkflowSourceContract>['derivation'];
 readonly baseApplication:GenericEventTransactionApplicationV1;
 readonly assertCurrent:()=>void;
}
const workflowRegistry=new WeakMap<object,(handle:GenericCompositionHandle)=>GenericWorkflowRuntimeBinding>();
/** Internal registry join. The public index deliberately does not export it. */
export function requireGenericCompositionRuntime(owner:unknown,handle:GenericCompositionHandle):GenericCompositionRuntimeBinding {
 const get=owner&&typeof owner==='object'?compositionRegistry.get(owner):undefined;
 if(!get)fail('ForeignOwner',at,'original registered composition owner required');
 const binding=get(handle);binding.assertCurrent();return binding;
}
/** Internal original-handle join for the C13 worker. Caller DTOs are never admitted. */
export function requireGenericWorkflowRuntime(owner:unknown,handle:GenericCompositionHandle):GenericWorkflowRuntimeBinding {
 const get=owner&&typeof owner==='object'?workflowRegistry.get(owner):undefined;
 if(!get)fail('ForeignOwner',at,'original registered composition owner required');
 const binding=get(handle);binding.assertCurrent();return binding;
}
export function createGenericCompositionOwner(){
 const legacy=createCompositionOwner(false),successor=createCompositionOwner(true),states=createCompositionOwner(true,'state-proposals'),keyed=createKeyedCompositionOwner(),atomic=createTransactionCompositionOwner(),httpAtomic=createTransactionCompositionOwner(true);
 const owners=new WeakMap<object,typeof legacy|typeof keyed|typeof atomic>();
 const formalExports=new WeakMap<object,{handle:GenericCompositionHandle;assertCurrent:()=>void}>();
 const current=(h:GenericCompositionHandle)=>{const o=h&&typeof h==='object'?owners.get(h):undefined;if(!o)fail('ForeignOwner',at,'original composition handle from this factory required');const cap=capabilityFormations.get(h);if(cap)cap.owner.assertCurrent(cap.handle);return o;};
 const owner=Object.freeze({
  async prepare(proposal:{sourcePath:string;profilePath:string;additionalSourcePaths?:readonly string[];externalProfilePath?:string;externalWriteSelectionPath?:string;httpProfilePath?:string;capabilitySelectionPath?:string}){
   const captured=captureTransactionPreparation(proposal),hasAdditional=Object.hasOwn(proposal,'additionalSourcePaths'),input={sourcePath:captured.sourcePath,profilePath:captured.profilePath,...(hasAdditional?{additionalSourcePaths:captured.additionalSourcePaths.map(p=>path.join(path.dirname(captured.sourcePath),p))}:{}),...(captured.externalProfilePath?{externalProfilePath:captured.externalProfilePath}:{}),...(captured.externalWriteSelectionPath?{externalWriteSelectionPath:captured.externalWriteSelectionPath}:{}),...(captured.httpProfilePath?{httpProfilePath:captured.httpProfilePath}:{})};
   if(!input||typeof input.sourcePath!=='string'||typeof input.profilePath!=='string'||!path.isAbsolute(input.sourcePath)||!path.isAbsolute(input.profilePath))fail('InvalidContract',at,'absolute business and profile paths required');
   const bounds=readCorePhysicalFile(path.join(path.dirname(input.sourcePath),'contracts/bounds.json')),profile=readCorePhysicalFile(input.profilePath),raw=parseCoreCommerceJson(bounds.text,bounds.file.path) as any;
   const candidate=parseCoreCommerceJson(profile.text,profile.file.path) as any;
   let selectedOwner:typeof legacy|typeof keyed|typeof atomic;
   if(candidate?.schema_version==='craft.generic-transaction-profile/v1-candidate'||candidate?.schema_version==='craft.generic-event-profile/v1-candidate'){
    selectedOwner=captured.httpProfilePath?httpAtomic:atomic;
   }else if(hasAdditional||captured.externalProfilePath||captured.externalWriteSelectionPath||captured.httpProfilePath){fail('UnsupportedCapability',at,'additional/external sources require the transaction profile');
   }else if(candidate?.schema_version==='craft.generic-keyed-query-profile/v1-candidate'){
    resolveGenericKeyedProfile(profile.text,input.profilePath,raw?.computation?.limits);selectedOwner=keyed;
   }else{
    const selected=resolveGenericPureProfile(profile.text,input.profilePath,raw?.computation?.limits);
    selectedOwner=selected.capabilities.includes('StateMachine')?states:selected.capabilities.includes('bounded-values')?successor:legacy;
   }
   const h=await selectedOwner.prepare(input);
   try{
    if(readCorePhysicalFile(profile.file.path).fingerprint!==profile.fingerprint||readCorePhysicalFile(bounds.file.path).fingerprint!==bounds.fingerprint)fail('StaleOwner',at,'profile or bounds changed during mode selection');
    if(captured.capabilitySelectionPath){const sourceBinding=selectedOwner.sourceBinding(h),capabilityOwner=createGenericCapabilityFormationOwner(sourceBinding.sources,sourceBinding.source,sourceBinding.semantics,sourceBinding.semantic),capability=capabilityOwner.prepare(captured.capabilitySelectionPath,input.sourcePath,input.profilePath);capabilityFormations.set(h,{owner:capabilityOwner,handle:capability});}
    owners.set(h,selectedOwner);return h;
   }catch(error){try{selectedOwner.dispose(h);}catch(cleanup){throw new AggregateError([error,cleanup],'preparation validation and acquired-owner cleanup failed',{cause:error});}throw error;}
  },
  review(h:GenericCompositionHandle,label:string){return current(h).review(h,label);},
  accept(h:GenericCompositionHandle,r:Parameters<typeof legacy.accept>[1],file:string){return current(h).accept(h,r,file);},
  inspect(h:GenericCompositionHandle){const inspection=current(h).inspect(h),capability_bindings=capabilityProjection(h);return capability_bindings?coreFreeze({...inspection,capability_bindings}):inspection;},
  inspectCapabilities(h:GenericCompositionHandle){current(h).assertCurrent(h);return capabilityProjection(h);},
  assertCurrent(h:GenericCompositionHandle){current(h).assertCurrent(h);},
  evaluateReference(h:GenericCompositionHandle,s:GenericPureSelection,input:Uint8Array){
   const selected=current(h);if('runtimeBinding'in selected)fail('UnsupportedCapability',at,'protected keyed execution requires its real runtime and current Auth');
   return selected.evaluateReference(h,s,input);
  },
  exportFiniteBoolFormal(h:GenericCompositionHandle,s:{rule:string}){
   const selected=current(h);
   if('runtimeBinding'in selected)fail('UnsupportedCapability',at,'finite pure formal output requires the bounded-values profile');
   const joined=selected.exportFiniteBoolFormal(h,s);
   formalExports.set(joined,{handle:h,assertCurrent:()=>{selected.exportFiniteBoolFormal(h,s);}});
   return joined;
  },
  exportPureWireFormal(h:GenericCompositionHandle,s:GenericPureSelection,input:Uint8Array){
   const selected=current(h);
   if('runtimeBinding'in selected)fail('UnsupportedCapability',at,'pure wire formal output requires a bounded-values profile');
   const joined=selected.exportPureWireFormal(h,s,input);
   if(coreSha256(input)!==joined.model.input_sha256)fail('StaleOwner',at,'formal input changed during selected export');
   const captured=Uint8Array.prototype.slice.call(input) as Uint8Array;
   formalExports.set(joined,{handle:h,assertCurrent:()=>{
    const again=selected.exportPureWireFormal(h,s,captured);
    if(dataDigest(again)!==dataDigest(joined))fail('StaleOwner',at,'selected pure wire formal output changed');
   }});
   return joined;
  },
  exportFiniteBoolListFormal(h:GenericCompositionHandle,s:GenericPureSelection){
   const selected=current(h);
   if('runtimeBinding'in selected)fail('UnsupportedCapability',at,'Bool-list formal output requires a bounded-values profile');
   const joined=selected.exportFiniteBoolListFormal(h,s);
   formalExports.set(joined,{handle:h,assertCurrent:()=>{
    const again=selected.exportFiniteBoolListFormal(h,s);
    if(dataDigest(again)!==dataDigest(joined))fail('StaleOwner',at,'selected Bool-list formal output changed');
   }});
   return joined;
  },
  exportWorkflowTlaFormal(h:GenericCompositionHandle){
   current(h);
   const model=exportGenericWorkflowTlaModel(owner,h);
   current(h);
   const joined=coreFreeze({schema_version:'craft.generic-workflow-tla-sdk-join/v1-candidate' as const,
    model,authority_effect:'none' as const,claim_ceiling:model.claim_ceiling});
   formalExports.set(joined,{handle:h,assertCurrent:()=>{requireGenericWorkflowRuntime(owner,h).assertCurrent();}});
   return joined;
  },
  exportStructuralAlloyFormal(h:GenericCompositionHandle,
   selection:{owner:ReturnType<typeof createGenericServiceArtifactOwner>;artifact:GenericServiceArtifactHandle}){
   const selected=current(h);
   if(!('runtimeBinding'in selected))fail('UnsupportedCapability',at,'structural Alloy requires an accepted stateful application');
   const binding=requireGenericCompositionRuntime(owner,h);
   if(binding.application.kind!=='original-generic-transaction-application/v1-candidate')
    fail('UnsupportedCapability',at,'structural Alloy requires an accepted stateful application');
   if(!selection||typeof selection!=='object'||Array.isArray(selection)||
    Object.keys(selection).sort().join(',')!=='artifact,owner')fail('InvalidContract',at,'exact original emitted service artifact selection required');
   const model=exportGenericStructuralAlloyModel(selection.owner,selection.artifact);
   const source=binding.plans.inspectSourceApplication(binding.application);
   if(model.application_contract_sha256!==source.contract_sha256||
    model.source_capture_sha256!==source.source_capture_sha256||
    model.profile_sha256!==source.derivation.profile_sha256||
    model.executable_semantics_sha256!==source.executable_semantics_sha256)
    fail('StaleOwner',at,'emitted structural model differs from the selected original application');
   binding.assertCurrent();selection.owner.inspect(selection.artifact);
   return coreFreeze({schema_version:'craft.generic-structural-alloy-sdk-join/v1-candidate' as const,
    model,authority_effect:'none' as const,claim_ceiling:model.claim_ceiling});
  },
  /** CLI bridge: issue the service-artifact handle inside this original SDK
   * owner, then join its exact emitted inventory to the selected application. */
  async exportStructuralAlloyFormalFromSource(h:GenericCompositionHandle,
   request:{outputDirectory:string;entries:readonly string[]}){
   const selected=current(h);
   if(!('runtimeBinding'in selected))fail('UnsupportedCapability',at,'structural Alloy requires an accepted stateful application');
   const binding=requireGenericCompositionRuntime(owner,h);
   if(binding.application.kind!=='original-generic-transaction-application/v1-candidate')
    fail('UnsupportedCapability',at,'structural Alloy requires an accepted stateful application');
   if(!request||typeof request!=='object'||nodeTypes.isProxy(request)||Array.isArray(request)||
    Object.keys(request).sort().join(',')!=='entries,outputDirectory'||!Array.isArray(request.entries)||nodeTypes.isProxy(request.entries)||
    typeof request.outputDirectory!=='string'||!path.isAbsolute(request.outputDirectory)||path.normalize(request.outputDirectory)!==request.outputDirectory)
    fail('InvalidContract',at,'exact formal artifact output and selected Entries required');
   const {createGenericServiceArtifactOwner}=await import('./service-artifact-owner.js');
   binding.assertCurrent();
   const artifactOwner=createGenericServiceArtifactOwner(owner,h),artifact=artifactOwner.emit({outputDirectory:request.outputDirectory,entries:request.entries});
   const joined=owner.exportStructuralAlloyFormal(h,{owner:artifactOwner,artifact});
   const artifact_manifest=artifactOwner.inspect(artifact);
   binding.assertCurrent();
   const result=coreFreeze({...joined,artifact_manifest});
   formalExports.set(result,{handle:h,assertCurrent:()=>{binding.assertCurrent();artifactOwner.inspect(artifact);}});
   return result;
  },
  async exportWorkflowEventJoinFormalFromSource(h:GenericCompositionHandle,
   request:{outputDirectory:string;entries:readonly string[]}){
   current(h);requireGenericWorkflowRuntime(owner,h);
   if(!request||typeof request!=='object'||nodeTypes.isProxy(request)||Array.isArray(request)||
    Object.keys(request).sort().join(',')!=='entries,outputDirectory'||
    !Array.isArray(request.entries)||nodeTypes.isProxy(request.entries)||
    typeof request.outputDirectory!=='string'||!path.isAbsolute(request.outputDirectory)||
    path.normalize(request.outputDirectory)!==request.outputDirectory)
    fail('InvalidContract',at,'exact Workflow/Event artifact output and selected Entries required');
   const {createGenericServiceArtifactOwner}=await import('./service-artifact-owner.js');
   const {exportGenericWorkflowEventJoinV1,assertGenericWorkflowEventJoinCurrentV1}=await import('./formal-workflow-event-join-v1.js');
   const artifactOwner=createGenericServiceArtifactOwner(owner,h);
   const artifact=artifactOwner.emit({outputDirectory:request.outputDirectory,entries:request.entries});
   const model=exportGenericWorkflowEventJoinV1(owner,h,artifactOwner,artifact);
   const joined=coreFreeze({schema_version:'craft.generic-workflow-event-sdk-join/v1-candidate' as const,
    model,authority_effect:'none' as const,claim_ceiling:model.claim_ceiling});
   const artifact_manifest=artifactOwner.inspect(artifact);
   const result=coreFreeze({...joined,artifact_manifest});
   formalExports.set(result,{handle:h,assertCurrent:()=>{
    assertGenericWorkflowEventJoinCurrentV1(owner,h,artifactOwner,artifact,model);
    artifactOwner.inspect(artifact);
   }});
   return result;
  },
  publishFormalExportDirectory(h:GenericCompositionHandle,joined:object,outputDirectory:string,
   artifacts:readonly {relative_path:string;content:string}[]){
   const registered=formalExports.get(joined);
   if(!registered||registered.handle!==h)fail('ForeignOwner',at,'original selected formal export required');
   registered.assertCurrent();
   publishAtomicDirectory(outputDirectory,artifacts,'.domainspec-formal-',registered.assertCurrent);
  },
  generate(h:GenericCompositionHandle,s:GenericSelection&{outputDirectory:string}){
   const selected=current(h);
   if('runtimeBinding'in selected)return selected.generate(h,s);
   if('entry'in s)fail('UnsupportedCapability',at,'Entry requires the keyed profile');
   return selected.generate(h,s);
  },
  async openWorkflow(h:GenericCompositionHandle,options:import('./workflow-driver.js').GenericWorkflowDriverOptions){
   const {openGenericWorkflowDriver}=await import('./workflow-driver.js');
   return openGenericWorkflowDriver(owner,h,options);
  },
  async openRuntime(h:GenericCompositionHandle,options:GenericRuntimeOptions):Promise<GenericApplicationRuntime|GenericTransactionApplicationRuntime>{
   requireGenericCompositionRuntime(owner,h);
   const {createGenericApplicationRuntime}=await import('./invocation-owner.js');
   return createGenericApplicationRuntime(owner,h,options);
  },
  bindHttp(h:GenericCompositionHandle,runtime:GenericTransactionApplicationRuntime,routeId:string){
   requireGenericCompositionRuntime(owner,h);return createGenericHttpHandler(owner,h,runtime,routeId);
  },
  dispose(h:GenericCompositionHandle){current(h).dispose(h);},
 });
 capabilityParents.set(owner,h=>{current(h).assertCurrent(h);const cap=capabilityFormations.get(h);if(!cap)fail('UnsupportedCapability',at,'selected capability source required');return {generation:()=>{current(h).assertCurrent(h);return capabilityGeneration(h);},assertCurrent:()=>{current(h).assertCurrent(h);}};});
 compositionRegistry.set(owner,h=>{const selected=current(h);if(selected===keyed)return keyed.runtimeBinding(h);if(selected===atomic||selected===httpAtomic)return selected.runtimeBinding(h);return fail('UnsupportedCapability',at,'runtime requires original keyed or atomic composition');});
 workflowRegistry.set(owner,h=>{const selected=current(h);if(selected!==atomic&&selected!==httpAtomic)fail('UnsupportedCapability',at,'Workflow requires original cumulative Event composition');return selected.workflowBinding(h);});
 return owner;
}
function createCompositionOwner(generic:boolean,mode:CoreGenericAdmissionMode='bounded-values'){
 coreGenericAdmissionMode(mode);
 const sources=createCoreCommerceSourceOwner(),semantics=createSourceSemanticBridge(sources,generic,mode),reviews=semantics.reviews,expandedSources=createCoreCommerceSourceOwner(),expandedSemantics=createSourceSemanticBridge(expandedSources,generic,mode);
 type State={source:CoreCommerceSourceCapture;semantic:SemanticCapture;expanded:CoreCommerceSourceCapture;expandedSemantic:SemanticCapture;profile:ReturnType<typeof readCorePhysicalFile>;limits:ComputationLimitsV1;inspection:any;root:string;logicalRoot:string;originals:ReturnType<typeof readCorePhysicalFile>[];review?:ReviewCapture;accepted?:AcceptedReview|undefined;operationDomain?:CommerceComputationDomainOwner|undefined;mappingDomain?:CommerceComputationDomainOwner|undefined;genericDomain?:GenericComputationDomainOwner|undefined;disposed:boolean};
 const rows=new WeakMap<object,State>();
 const current=(h:GenericCompositionHandle)=>{const r=h&&typeof h==='object'?rows.get(h):undefined;if(!r)fail('ForeignOwner',at,'original composition handle from this owner required');if(r.disposed)fail('DisposedOwner',at,'composition disposed');pin.assertCurrent();for(const f of r.originals)if(readCorePhysicalFile(f.file.path).fingerprint!==f.fingerprint)fail('StaleOwner',at,'original business source or limits changed');sources.assertCurrent(r.source);semantics.assertSource(r.semantic,r.source);expandedSources.assertCurrent(r.expanded);expandedSemantics.assertSource(r.expandedSemantic,r.expanded);if(readCorePhysicalFile(r.profile.file.path).fingerprint!==r.profile.fingerprint)fail('StaleOwner',at,'profile physical identity changed');return r;};
 const selector=(input:unknown,output=false)=>{
  const request=captureJson(input) as Record<string,unknown>,allowed=['rule','operation','mapping','calculation','policy'],keys=request&&typeof request==='object'&&!Array.isArray(request)?Object.keys(request):[];
  const selected=allowed.filter(k=>Object.hasOwn(request??{},k));
  if(selected.length!==1||keys.length!==(output?2:1)||keys.some(k=>!allowed.includes(k)&&!(output&&k==='outputDirectory'))||typeof request[selected[0]!]!=='string'||!request[selected[0]!]||output&&typeof request.outputDirectory!=='string')fail('InvalidContract',at,'exactly one explicit rule, operation, mapping, calculation or policy selector required');
  return {kind:selected[0]! as 'rule'|'operation'|'mapping'|'calculation'|'policy',name:request[selected[0]!] as string,outputDirectory:request.outputDirectory as string};
 };
 const checkedTarget=(h:GenericCompositionHandle,selection:{kind:'rule'|'operation'|'mapping'|'calculation'|'policy';name:string})=>{
  const row=current(h);if(!row.accepted)fail('MissingMapping',at,'exact accepted source review required before execution or generation');reviews.assertAcceptedCurrent(row.accepted);
  const capture=expandedSources.inspect(row.expanded),sem=expandedSemantics.inspect(row.expandedSemantic),{kind,name}=selection;
  if(kind==='operation'?!(row.operationDomain||row.genericDomain)||!sem.effects.some(p=>p.operation.module+'.'+p.operation.name===name):!sem.pure.declarations.some(d=>d.kind===(kind==='mapping'?'Mapping':kind==='calculation'?'Calculation':kind==='policy'?'Policy':'Rule')&&d.name===name)||kind==='mapping'&&!(row.mappingDomain||row.genericDomain))fail('UnknownReference',at,'exact admitted source selector required');
  const paths=new Set(capture.reconstruction.modules.map(m=>m.path)),texts=capture.files.filter(f=>paths.has(f.path));
  if(generic){const domain=row.genericDomain!,contract=createGenericSourceComputation(texts,name,row.limits,mode).contract,handle=domain.check(contract);return {row,domain,domainHandle:handle,inspect:()=>domain.inspect(handle),assertCurrent:()=>domain.assertCurrent(handle),evaluate:(input:Uint8Array)=>evaluateGenericComputation(domain,handle,input),compile:()=>compileGenericComputationTypeScript(domain,handle)};}
  const contract=kind==='operation'?createPureOperationComputation(texts,capture.files.filter(f=>f.path.endsWith('.json')),name,row.limits,!!row.mappingDomain,row.inspection.capabilities.includes('Calculation')).contract:row.mappingDomain?createOrderedMappingComputation(texts,name,row.limits,row.inspection.capabilities.includes('Calculation')).contract:createCoreCommerceComputationContract(texts,name,row.limits);
  const domain=kind==='operation'?row.operationDomain!:row.mappingDomain??createOriginalPureComputationDomainOwner(expandedSources,row.expanded,expandedSemantics.legacy!,row.expandedSemantic as CoreCommerceSemanticCapture),handle=domain.check(contract);
  return {row,inspect:()=>domain.inspect(handle),assertCurrent:()=>domain.assertCurrent(handle),evaluate:(input:Uint8Array)=>evaluateCommerceComputation(domain,handle,input),compile:()=>compileCommerceComputationTypeScript(domain,handle)};
 };
 return Object.freeze({
  async prepare({sourcePath,profilePath}:{sourcePath:string;profilePath:string}):Promise<GenericCompositionHandle>{
   pin.assertCurrent();if(!path.isAbsolute(sourcePath)||!sourcePath.endsWith('.alch')||!path.isAbsolute(profilePath))fail('InvalidContract',at,'absolute .alch source and profile paths required');
   // Capture original files before any generated copy. The original owner stays
   // live and is checked on every downstream operation, including same-byte replacement.
   const original=readCorePhysicalFile(sourcePath),authoredBounds=readCorePhysicalFile(path.join(path.dirname(sourcePath),'contracts/bounds.json'));
   const business=reconstructCoreCommerceModule(original.text,'source/business.alch');for(const d of business.declarations)if(!['Rule','ValueObject','Operation','Mapping','Calculation','Policy',...(generic?['Enum']:[]),...(mode==='state-proposals'?['StateMachine']:[])].includes(d.surface)&&!(generic&&d.surface==='Interface'&&d.interface_kind==='bounded-schema'))fail('UnsupportedCapability',d.syntax,'C01 business source admits only Rule and Bool records; supplied claims await formal parser qualification');
   const logicalRoot=mkdtempSync(path.join(tmpdir(),'craft-composition-logical-'));
   mkdirSync(path.join(logicalRoot,'contracts'));mkdirSync(path.join(logicalRoot,'source'));
   writeCoreExclusiveFile(path.join(logicalRoot,'source/business.alch'),original.text);
   writeCoreExclusiveFile(path.join(logicalRoot,'contracts/bounds.json'),authoredBounds.text);
   writeCoreExclusiveFile(path.join(logicalRoot,'application.alch'),'module CraftGenerated.Root version 1\ninterface Application:\n  kind application-composition\n  source source/business.alch\n  computation-bounds contracts/bounds.json\n');
   const source=sources.prepare(logicalRoot,'application.alch'),semantic=semantics.check(source),logical=sources.inspect(source),checked=semantics.inspect(semantic);
   if(logical.reconstruction.modules.find(m=>m.path==='source/business.alch')!.declarations.some(d=>d.surface==='Interface'&&!(generic&&d.interface_kind==='bounded-schema')))fail('UnsupportedCapability',at,'business source cannot declare technical interfaces in C01');
   const types=createCoreValueTypes(logical.reconstruction),application=[...types.declarations.values()].find(d=>d.interface_kind==='application-composition')!,bounds=createCoreContextCatalog(types,logical.files.filter(f=>f.path.endsWith('.json'))).asset(application,['computation-bounds']),raw=bounds?.value as any;
   if(!raw||raw.schema_version!==(generic?'craft.generic-compute-bounds/v1-candidate':'craft.commerce-compute-bounds/v1-candidate')||raw.computation?.required_schema_version!==(generic?'craft.generic-computation/v1-candidate':'domainspec.iteration-expression/v2-candidate')||raw.computation?.required_semantics_revision!==(generic?'ordered-metered-generic-v1-candidate':'ordered-metered-commerce-v2-candidate'))fail('MissingMapping',at,'source must declare original exact computation-bounds');
   const limits=raw.computation.limits as ComputationLimitsV1;
   const modulePaths=new Set(logical.reconstruction.modules.map(m=>m.path)),texts=logical.files.filter(f=>modulePaths.has(f.path));
   // Existing contract producer checks all nine positive finite limit fields.
   const firstRule=checked.pure.declarations[0];if(!firstRule)fail('MissingMapping',at,'this composition phase requires at least one declared Rule');
   if(generic)createGenericSourceComputation(texts,firstRule.name,limits,mode);else createCoreCommerceComputationContract(texts,firstRule.name,limits);
   const profile=readCorePhysicalFile(profilePath),selection=resolveGenericPureProfile(profile.text,profilePath,limits);
   assertPolicyEnforcementProfile(logical.reconstruction.modules.flatMap(m=>m.declarations),selection.capabilities);
   if(!generic){admitGenericComposition(logical,requireLegacyExpressionData(checked.pure),selection.capabilities);for(const plan of checked.effects)assertPureOperationPlan(requireLegacyExpressionData(plan),new Set(checked.pure.declarations.map(d=>d.name)),selection.capabilities.includes('Mapping'),selection.capabilities.includes('Calculation'));}
   if(generic&&selection.capabilities.includes('StateMachine')!==(mode==='state-proposals'))fail('InvalidContract',at,'profile and original semantic admission mode differ');
   const recipe=mode==='state-proposals'?PURE_STATE_RECIPE:generic?PURE_VALUE_RECIPE:selection.capabilities.includes('Calculation')?PURE_CALCULATION_RECIPE:selection.capabilities.includes('Mapping')?PURE_MAPPING_RECIPE:selection.capabilities.includes('Operation')?PURE_OPERATION_RECIPE:PURE_PROFILE_RECIPE,root=mkdtempSync(path.join(tmpdir(),'craft-composition-expanded-'));
   try{
    for(const f of logical.files){const destination=path.join(root,f.path);mkdirSync(path.dirname(destination),{recursive:true});writeCoreExclusiveFile(destination,f.text);}
    const expanded=expandedSources.prepare(root,'application.alch'),expandedSemantic=expandedSemantics.check(expanded),expansion=expandedSources.inspect(expanded),expandedChecked=expandedSemantics.inspect(expandedSemantic);
    if(!generic){admitGenericComposition(expansion,requireLegacyExpressionData(expandedChecked.pure),selection.capabilities);for(const plan of expandedChecked.effects)assertPureOperationPlan(requireLegacyExpressionData(plan),new Set(expandedChecked.pure.declarations.map(d=>d.name)),selection.capabilities.includes('Mapping'),selection.capabilities.includes('Calculation'));}
    if(generic&&('admission_mode'in checked&&'admission_mode'in expandedChecked)&&(checked.admission_mode!==expandedChecked.admission_mode||checked.admission_capabilities_sha256!==expandedChecked.admission_capabilities_sha256))fail('InvalidContract',at,'expanded admission differs from original semantic owner');
    if(checked.executable_sha256!==expandedChecked.executable_sha256||checked.pure.pure_subject_sha256!==expandedChecked.pure.pure_subject_sha256)fail('InvalidContract',at,'profile expansion changed business semantics');
    const mappingSemantics=generic?createGenericSourceComputation(texts,firstRule.name,limits,mode).derivation:selection.capabilities.includes('Mapping')?createOrderedMappingComputation(texts,firstRule.name,limits,selection.capabilities.includes('Calculation')).derivation:undefined;
    if(mappingSemantics){const expandedPaths=new Set(expansion.reconstruction.modules.map(m=>m.path)),actual=(generic?createGenericSourceComputation(expansion.files.filter(f=>expandedPaths.has(f.path)),firstRule.name,limits,mode):createOrderedMappingComputation(expansion.files.filter(f=>expandedPaths.has(f.path)),firstRule.name,limits,selection.capabilities.includes('Calculation'))).derivation;if(dataDigest(mappingSemantics)!==dataDigest(actual))fail('InvalidContract',at,'expanded generic Mapping semantics differ from logical source');}
    // EffectPlans here are original typed semantics. Explicitly omit source
    // capture and qualification metadata from executable identity.
    const compositionDigest=(sem:typeof checked)=>generic?sem.executable_sha256:mappingSemantics?dataDigest({revision:'craft.generic-composition-semantics/v1-candidate',mapping_semantics_sha256:mappingSemantics.mapping_semantics_sha256,operations:sem.effects.map(({schema_version,operation,service,parameters,contexts,result,body,protocol})=>({schema_version,operation,service,parameters,contexts,result,body,protocol}))}):undefined;
    if(mappingSemantics&&compositionDigest(checked)!==compositionDigest(expandedChecked))fail('InvalidContract',at,'expanded composition executable semantics differ');
    const graph=(capture:typeof logical,sem:typeof checked,businessOnly=false)=>({...('admission_mode'in sem?{admission_mode:sem.admission_mode,admission_capabilities_sha256:sem.admission_capabilities_sha256}:{}),capture_sha256:capture.capture_sha256,semantic_sha256:sem.executable_sha256,pure_sha256:sem.pure.pure_subject_sha256,...(mappingSemantics?{executable_semantics_sha256:compositionDigest(sem),projection_sha256:mappingSemantics.projection_sha256}:{}),nodes:capture.reconstruction.modules.filter(m=>!businessOnly||m.path==='source/business.alch').flatMap(m=>m.declarations.map(d=>({id:d.id,kind:d.surface,source:{path:m.path,sha256:m.sha256,start:d.syntax.start,end:d.syntax.end}}))),ownership:capture.reconstruction.ownership.filter(o=>!businessOnly||o.declaration.startsWith(business.module+'.'))});
    const reachableContract=generic?createGenericSourceComputation(texts,firstRule.name,limits,mode).contract:undefined;
    const reachableOperations=reachableContract&&'admission_mode'in checked?checked.effects.map(operation=>deriveGenericReachableOperationSemantics(operation,reachableContract.functions,reachableContract.values,limits)):[];
    const inspection=coreFreeze({schema_version:'craft.generic-composition-inspection/v1-candidate',source:{path:sourcePath,sha256:original.file.sha256,bounds:authoredBounds.file,files:logical.files.map(({path,sha256,bytes})=>({path,sha256,bytes}))},profile:{id:selection.id,path:profilePath,sha256:profile.file.sha256,recipe,recipe_sha256:dataDigest(recipe)},logical:graph(logical,checked,true),expanded:{...graph(expansion,expandedChecked),origins:[{declaration:'CraftGenerated.Root.Application',kind:'technical',recipe_sha256:dataDigest(recipe)},{module:business.module,kind:'unchanged-business',original:original.file}]},capabilities:selection.capabilities,...(mappingSemantics?{mapping_semantics:mappingSemantics}:{}),operations:expandedChecked.effects,reachable_operations:reachableOperations,compiler_sha256:pin.sha256,tools:{node:process.version,platform:process.platform,arch:process.arch,type_erasure:'node:module.stripTypeScriptTypes/strip'},limits,qualification:mode==='state-proposals'?'C06-source-cli-zero-intent-state-proposals':generic?'C05-source-cli-bounded-values-and-collections':selection.capabilities.includes('Calculation')?'C04-source-cli-scalar-calculation-policy-composition':selection.capabilities.includes('Mapping')?'C03-source-cli-ordered-mapping-composition':selection.capabilities.includes('Operation')?'C02-source-cli-generated-zero-effect-operation':'C01-source-cli-generated-pure-rule-only',authority_effect:'none'});
    const operationDomain=!generic&&selection.capabilities.includes('Operation')?await createOriginalPureOperationDomainOwner(expandedSources,expanded,expandedSemantics.legacy!,expandedSemantic as CoreCommerceSemanticCapture,selection.capabilities.includes('Mapping'),selection.capabilities.includes('Calculation')):undefined;
    const mappingDomain=!generic&&selection.capabilities.includes('Mapping')?await createOriginalGenericMappingDomainOwner(expandedSources,expanded,expandedSemantics.legacy!,expandedSemantic as CoreCommerceSemanticCapture,selection.capabilities.includes('Calculation')):undefined;
    const genericDomain=generic?createGenericComputationDomainOwner(expandedSources,expanded,expandedSemantics.successor!,expandedSemantic as GenericSemanticCapture):undefined;
    const handle=Object.freeze({kind:'original-generic-composition/v1-candidate' as const});rows.set(handle,{source,semantic,expanded,expandedSemantic,profile,limits,inspection,root,logicalRoot,originals:[original,authoredBounds],operationDomain,mappingDomain,genericDomain,disposed:false});current(handle);return handle;
   }catch(error){throw error;}
  },
  review(h:GenericCompositionHandle,owner:string){const row=current(h);row.review=reviews.prepare(row.semantic,owner);row.accepted=undefined;return reviews.inspect(row.review);},
  accept(h:GenericCompositionHandle,request:{decision_id:string;owner:string;outcome:'accepted'|'declined';reviewed_digest:string},decisionPath:string){const row=current(h);if(!row.review)fail('MissingMapping',at,'prepare an explicit source review first');row.accepted=undefined;const decision=reviews.recordDecision(row.review,request,decisionPath);row.accepted=reviews.requireAccepted(row.review,decision);return reviews.inspectDecision(decision);},
  sourceBinding(h:GenericCompositionHandle){const r=current(h);if(!expandedSemantics.successor)fail('UnsupportedCapability',at,'capabilities require checked generic value semantics');return {sources:expandedSources,source:r.expanded,semantics:expandedSemantics.successor,semantic:r.expandedSemantic as GenericSemanticCapture};},
  inspect(h:GenericCompositionHandle){return current(h).inspection;},assertCurrent(h:GenericCompositionHandle){current(h);},
  evaluateReference(h:GenericCompositionHandle,selection:{rule:string}|{operation:string}|{mapping:string}|{calculation:string}|{policy:string},input:Uint8Array){
   const target=checkedTarget(h,selector(selection)),result=target.evaluate(input);current(h);reviews.assertAcceptedCurrent(target.row.accepted!);return result;
  },
  exportFiniteBoolFormal(h:GenericCompositionHandle,selection:{rule:string}){
   if(!generic||mode!=='bounded-values')fail('UnsupportedCapability',at,'finite pure formal output requires the bounded-values profile');
   const chosen=selector(selection);
   if(chosen.kind!=='rule')fail('UnsupportedCapability',at,'finite pure formal output requires a Rule selector');
   const target=checkedTarget(h,chosen);
   if(!('domain'in target)||!target.domain||!target.domainHandle)fail('UnsupportedCapability',at,'original generic computation domain required');
   const profile=target.row.inspection.profile;
   const model=exportGenericFiniteBoolSmtModel(target.domain,target.domainHandle,{id:profile.id,path:profile.path,sha256:profile.sha256});
   current(h);target.assertCurrent();reviews.assertAcceptedCurrent(target.row.accepted!);
   return coreFreeze({schema_version:'craft.generic-finite-bool-sdk-join/v1-candidate',profile_binding:'original-selected-profile-bound',profile:{id:profile.id,path:profile.path,sha256:profile.sha256},model,authority_effect:'none',claim_ceiling:'reference-behavior-on-canonical-bool-leaves-only-no-generated-code-parity-or-application-semantics-or-solver-proof'});
  },
  exportPureWireFormal(h:GenericCompositionHandle,selection:GenericPureSelection,input:Uint8Array){
   if(!generic||mode!=='bounded-values')fail('UnsupportedCapability',at,'pure wire formal output requires the bounded-values profile');
   const chosen=selector(selection);
   if(chosen.kind==='operation')fail('UnsupportedCapability',at,'Operation effects are outside the pure wire formal model');
   const target=checkedTarget(h,chosen);
   if(!('domain'in target)||!target.domain||!target.domainHandle)
    fail('UnsupportedCapability',at,'original generic computation domain required');
   const model=exportCheckedGenericPureExpressionFormalFromWireV1(target.domain,target.domainHandle,input);
   const observed=target.evaluate(input);
   const actual=observed.ok?
    {ok:true,wire_hex:Buffer.from(observed.wire).toString('hex'),fuel_used:observed.fuel_used}:
    {ok:false,code:observed.error.code,expression_path:observed.error.expression_path,
     index_path:observed.error.index_path,call_path:observed.error.call_path,fuel_used:observed.fuel_used};
   if(dataDigest(actual)!==dataDigest(model.result))fail('InvalidContract',at,'selected pure formal/reference behavior differs');
   current(h);target.assertCurrent();reviews.assertAcceptedCurrent(target.row.accepted!);
   const profile=target.row.inspection.profile;
   return coreFreeze({schema_version:'craft.generic-pure-wire-sdk-join/v1-candidate' as const,
    profile_binding:'original-selected-profile-bound' as const,
    profile:{id:profile.id,path:profile.path,sha256:profile.sha256},model,
    reference_parity:'checked-reference-matched-for-this-wire' as const,
    authority_effect:'none' as const,claim_ceiling:model.claim_ceiling});
  },
  exportFiniteBoolListFormal(h:GenericCompositionHandle,selection:GenericPureSelection){
   if(!generic||mode!=='bounded-values')fail('UnsupportedCapability',at,'Bool-list formal output requires the bounded-values profile');
   const chosen=selector(selection);
   if(chosen.kind==='operation')fail('UnsupportedCapability',at,'Operation effects are outside the Bool-list formal model');
   const target=checkedTarget(h,chosen);
   if(!('domain'in target)||!target.domain||!target.domainHandle)
    fail('UnsupportedCapability',at,'original generic computation domain required');
   const model=exportCheckedGenericFiniteBoolListFormalModelV1(target.domain,target.domainHandle);
   current(h);target.assertCurrent();reviews.assertAcceptedCurrent(target.row.accepted!);
   const profile=target.row.inspection.profile;
   return coreFreeze({schema_version:'craft.generic-finite-bool-list-sdk-join/v1-candidate' as const,
    profile_binding:'original-selected-profile-bound' as const,
    profile:{id:profile.id,path:profile.path,sha256:profile.sha256},model,
    authority_effect:'none' as const,claim_ceiling:model.claim_ceiling});
  },
  generate(h:GenericCompositionHandle,selection:({rule:string}|{operation:string}|{mapping:string}|{calculation:string}|{policy:string})&{outputDirectory:string}){
   const chosen=selector(selection,true),{kind,name:rule,outputDirectory}=chosen,operation=kind==='operation'?rule:undefined,mapping=kind==='mapping'?rule:undefined;
   if(!path.isAbsolute(outputDirectory)||path.normalize(outputDirectory)!==outputDirectory)fail('InvalidContract',at,'normalized absolute new output directory required');
   const target=checkedTarget(h,chosen),{row}=target,compiled=target.compile(),moduleName=kind+'.mjs';
   const code=stripTypeScriptTypes(compiled.source,{mode:'strip'});current(h);target.assertCurrent();
   const native=compiled.manifest,codeSha=coreSha256(code);
   const system={schema_version:'craft.generic-system-view/v1-candidate',nodes:[{id:'generated:'+rule,kind:'node-esm-module',artifact:moduleName,sha256:codeSha}],edges:[],authority_effect:'none'};
   const bridge={schema_version:'craft.generic-business-system-bridge/v1-candidate',links:[{business:rule,system:'generated:'+rule,profile:row.inspection.profile.sha256,recipe:row.inspection.profile.recipe_sha256,source:native.source,source_capture_sha256:native.source_capture_sha256,contract_sha256:native.contract_sha256}],authority_effect:'none'};
   const artifacts=[{relative_path:moduleName,content:code},...([['business-graph.json',row.inspection.logical],['system-graph.json',system],['business-system-bridge.json',bridge]] as const).map(([relative_path,value])=>({relative_path,content:JSON.stringify(value,null,2)+'\n'}))];
   const checkedContract=target.inspect().contract;
   const checkedOperations:readonly (import('./computation-data-v1.js').GenericEffectPlanV1|import('../commerce/commerce-data-v1.js').EffectPlanV1)[]=row.inspection.operations;
   if(checkedContract.schema_version==='craft.generic-computation/v1-candidate')addPolicyEnforcementArtifacts(artifacts,projectPolicyEnforcementLineage({artifactNode:'generated:'+rule,functions:checkedContract.functions,operations:checkedOperations.filter((o):o is import('./computation-data-v1.js').GenericEffectPlanV1=>o.schema_version==='craft.generic-effects/v1-candidate').map(o=>({operation:o.operation.module+'.'+o.operation.name,body:o.body}))}));
   addCapabilityArtifacts(h,artifacts);
   const files=artifacts.map(f=>({path:f.relative_path,sha256:coreSha256(f.content),bytes:Buffer.byteLength(f.content)}));
   const manifest=coreFreeze({...row.inspection,...(capabilityProjection(h)?{capability_bindings:capabilityProjection(h),capability_wiring:capabilityGeneration(h).plan}:{}),selected_recipe:{kind:kind[0]!.toUpperCase()+kind.slice(1),module:moduleName,recipe_sha256:row.inspection.profile.recipe_sha256},...{[kind]:rule},...((target.inspect() as any).derivation?{lowering:(target.inspect() as any).derivation}:{}),native,files,output_sha256:dataDigest(files),review:reviews.inspect(row.review!)});
   artifacts.push({relative_path:'manifest.json',content:generatedManifestContent(manifest)});
   publishAtomicDirectory(outputDirectory,artifacts,'.domainspec-composition-',()=>{capabilityProjection(h);current(h);target.assertCurrent();reviews.assertAcceptedCurrent(row.accepted!);});
   return manifest;
  },
  dispose(h:GenericCompositionHandle){const row=current(h);row.disposed=true;semantics.dispose(row.semantic);sources.dispose(row.source);expandedSemantics.dispose(row.expandedSemantic);expandedSources.dispose(row.expanded);// Private snapshots are retained as diagnostics, never recursively deleted by replaceable pathname.
},
 });
}


/** Actual source/review/plan producer for the atomic branch of the same SDK. */
function createTransactionCompositionOwner(http=false){
 type Capture=ReturnType<typeof prepareGenericTransactionSources>;
 type Row={capture:Capture;runtimePackage:ReturnType<typeof readCorePhysicalFile>;review?:GenericReviewCapture|undefined;accepted?:GenericAcceptedReview|undefined;plans?:GenericRepositoryPlanOwner|undefined;application?:GenericTransactionApplicationHandle|undefined;workflowBinding?:GenericWorkflowRuntimeBinding;workflowAccepted?:GenericAcceptedReview|undefined;disposed:boolean};
 const rows=new WeakMap<object,Row>();
 const current=(h:GenericCompositionHandle)=>{
  const r=h&&typeof h==='object'?rows.get(h):undefined;
  if(!r)fail('ForeignOwner',at,'original atomic composition handle required');
  if(r.disposed)fail('DisposedOwner',at,'atomic composition disposed');
  r.capture.assertCurrent();atomicPlanPin.assertCurrent();
  if(readCorePhysicalFile(r.runtimePackage.file.path).fingerprint!==r.runtimePackage.fingerprint)fail('StaleOwner',at,'original runtime package identity changed');
  return r;
 };
 const runtimeBinding=(h:GenericCompositionHandle):GenericTransactionCompositionRuntimeBinding=>{
  const row=current(h),{plans,application,accepted}=row;
  if(!plans||!application||!accepted)fail('MissingMapping',at,'current accepted atomic source review required');
  const assertCurrent=()=>withCorePhysicalIdentityPhase(()=>{const r=current(h);if(r.plans!==plans||r.application!==application||r.accepted!==accepted)fail('StaleOwner',at,'runtime belongs to an earlier accepted atomic review');r.capture.reviews.assertAcceptedSemantic(accepted,r.capture.expandedSemantic);plans.assertCurrent(application);});
  assertCurrent();return Object.freeze({plans,application,assertCurrent});
 };
 return Object.freeze({
  async prepare(input:{sourcePath:string;profilePath:string;additionalSourcePaths?:readonly string[];externalProfilePath?:string;externalWriteSelectionPath?:string;httpProfilePath?:string}):Promise<GenericCompositionHandle>{
   if(http!==!!input.httpProfilePath)fail('InvalidContract',at,'selected HTTP owner requires exactly one original HTTP profile');
   const runtimePackage=captureKeyedPackage(),capture=prepareGenericTransactionSources(input),handle=Object.freeze({kind:'original-generic-composition/v1-candidate' as const});
   rows.set(handle,{capture,runtimePackage,disposed:false});current(handle);return handle;
  },
  review(h:GenericCompositionHandle,label:string){const r=current(h);r.accepted=undefined;r.plans=undefined;r.application=undefined;r.review=r.capture.reviews.prepare(r.capture.expandedSemantic,label);return r.capture.reviews.inspect(r.review);},
  accept(h:GenericCompositionHandle,request:{decision_id:string;owner:string;outcome:'accepted'|'declined';reviewed_digest:string},decisionPath:string){
   const r=current(h);if(!r.review)fail('MissingMapping',at,'prepare explicit atomic source review first');r.accepted=undefined;r.plans=undefined;r.application=undefined;
   const {expandedSources,expanded,expandedSemantics,expandedSemantic,reviews}=r.capture,decision=reviews.recordDecision(r.review,request,decisionPath),accepted=reviews.requireAccepted(r.review,decision);
   const checked=expandedSemantics.inspect(expandedSemantic);if(checked.admission_mode!=='atomic-state-entry'&&checked.admission_mode!=='external-read-entry'&&checked.admission_mode!=='external-write-entry'&&checked.admission_mode!=='event-handoff-entry')fail('InvalidContract',at,'actual transaction semantic admission required');
   const plans=createGenericRepositoryPlanOwner(expandedSources,expanded,expandedSemantics,expandedSemantic,reviews,accepted),application=plans.check(checked.transaction_contract as GenericTransactionApplicationContractV1|GenericExternalTransactionApplicationV1|GenericExternalWriteTransactionApplicationV1|GenericEventTransactionApplicationV1) as GenericTransactionApplicationHandle;
   r.accepted=accepted;r.plans=plans;r.application=application;runtimeBinding(h);return reviews.inspectDecision(decision);
  },
  sourceBinding(h:GenericCompositionHandle){const {capture:c}=current(h);return {sources:c.expandedSources,source:c.expanded,semantics:c.expandedSemantics,semantic:c.expandedSemantic};},
  inspect(h:GenericCompositionHandle){const r=current(h);return coreFreeze({...r.capture.inspection,source:{...r.capture.inspection.source,files:r.capture.expandedSources.inspect(r.capture.expanded).files.map(({path,sha256,bytes})=>({path,sha256,bytes}))}});},
  assertCurrent(h:GenericCompositionHandle){current(h);},
  runtimeBinding,
  workflowBinding(h:GenericCompositionHandle):GenericWorkflowRuntimeBinding{
   const row=current(h);
   // The accepted source/plan is immutable. Reuse its original checked Workflow
   // rather than rebuilding every transaction/type/step at each custody check.
   // The binding still checks physical source, implementation, current review
   // and runtime on every use; a newly accepted review gets a new binding.
   if(row.workflowBinding&&row.workflowAccepted===row.accepted){row.workflowBinding.assertCurrent();return row.workflowBinding;}
   const runtime=runtimeBinding(h),capture=row.capture.expandedSources.inspect(row.capture.expanded);
   if(!row.capture.inspection.workflow_profile)fail('UnsupportedCapability',at,'authored Workflow profile required');
   const checked=createGenericWorkflowSourceContract(capture);
   if(dataDigest(checked.contract)!==dataDigest(row.capture.inspection.workflow_contract))fail('InvalidContract',at,'checked Workflow differs from original source inspection');
   const assertCurrent=()=>withCorePhysicalIdentityPhase(()=>{runtime.assertCurrent();const r=current(h);if(r!==row||r.capture.expandedSources.inspect(r.capture.expanded).capture_sha256!==capture.capture_sha256)fail('StaleOwner',at,'original Workflow source changed');});
   assertCurrent();const binding=Object.freeze({contract:checked.contract,derivation:checked.derivation,baseApplication:checked.base_application,assertCurrent});row.workflowBinding=binding;row.workflowAccepted=row.accepted;return binding;
  },
  generate(h:GenericCompositionHandle,selection:GenericSelection&{outputDirectory:string}){
   const raw=captureJson(selection) as {entry?:unknown;outputDirectory?:unknown};
   if(!raw||typeof raw!=='object'||Array.isArray(raw)||Object.keys(raw).sort().join(',')!=='entry,outputDirectory'||typeof raw.entry!=='string'||typeof raw.outputDirectory!=='string'||!path.isAbsolute(raw.outputDirectory)||path.normalize(raw.outputDirectory)!==raw.outputDirectory)fail('InvalidContract',at,'exact entry selector and normalized new output directory required');
   const row=current(h),binding=runtimeBinding(h),{plans,application}=binding,entry=plans.inspectEntry(plans.bindEntry(application,raw.entry)),service=plans.bindService(application,entry.service),source=row.capture.expandedSources.inspect(row.capture.expanded),app=plans.inspectSourceApplication(application) as ReturnType<typeof plans.inspectSourceApplication>&{contract:GenericTransactionApplicationContractV1|GenericExternalTransactionApplicationV1|GenericExternalWriteTransactionApplicationV1|GenericEventTransactionApplicationV1};
   const transport=http?plans.inspectHttpApplication(application):undefined;
   // Internal Entries retain the complete checked public-route profile; only
   // its explicitly selected routes receive HTTP handlers.
   const httpTopology=transport?projectGenericHttpTransport(transport.contract):undefined;
   const eventContract=app.contract.admission_mode==='event-handoff-entry'?app.contract:undefined;
   const workflowProjection=row.capture.inspection.workflow_profile?plans.inspectWorkflow(plans.bindWorkflow(application,row.capture.inspection.workflow_contract!.workflow)):undefined;
   if(workflowProjection&&dataDigest(workflowProjection.contract)!==dataDigest(row.capture.inspection.workflow_contract))fail('InvalidContract',at,'generated Workflow plan differs from checked source inspection');
   const workflow=workflowProjection?.contract;
   const writeContract=app.contract.admission_mode==='external-write-entry'?app.contract:eventContract?.write_bindings.length?eventContract:undefined;
   const eventMode=!!eventContract,writeMode=!!writeContract;
   const storage=eventMode?deriveGenericEventStorageDescriptor(plans,application,service):writeMode?deriveGenericExternalWriteStorageDescriptor(plans,application,service):deriveGenericTransactionStorageDescriptor(plans,application,service),assembly=createGenericOperationAssembly(plans,application);
   const operationRows=app.contract.stateful_operations.filter(o=>eventMode||o.service===entry.service).map(o=>({service:o.service,assembly:assembly.inspectSource(assembly.bind(plans.bindStatefulOperation(application,o.operation)))}));
   const operations=operationRows.map(row=>row.assembly),localOperations=operationRows.filter(row=>row.service===entry.service).map(row=>row.assembly);
   const storageId='storage:'+entry.service,applicationId='generated:'+entry.entry,authId='auth:'+entry.entry,httpId='http:'+entry.entry;
   const routeEntries=transport?[...new Set(transport.contract.entries.map(candidate=>candidate.route.entry))].map(id=>{const selected=app.contract.entries.find(candidate=>candidate.entry===id);if(!selected)fail('InvalidContract',at,'checked HTTP Entry missing from application');return selected;}):[];
   const privateEntry=!!transport&&!routeEntries.some(candidate=>candidate.entry===entry.entry);
   const route='/entries/'+entry.entry.replaceAll('.','/');
   const commandEntry=entry.schema_version==='craft.generic-transaction-entry/v1-candidate'||entry.schema_version==='craft.generic-operator-entry/v1-candidate';
   const httpConfig={entry:entry.entry,route,kind:commandEntry?'command':'read',max_request_bytes:app.contract.limits.max_input_bytes};
   const externalBindings='external_bindings'in app.contract?app.contract.external_bindings.filter(b=>eventMode||b.service===entry.service):[];
   const externalNodes=externalBindings.flatMap(b=>[{id:'external:'+b.id,kind:'profiled-safe-get-provider',interface:b.interface_ref,operation:b.contract_operation_ref,provider_operation:b.provider_operation_ref,request_mapping:b.request_mapping.name,response_mapping:b.response_mapping.name,validation_rule:b.response_validation_rule.name,protocol:b.protocol},{id:'external-config:'+b.id,kind:'captured-provider-origin',configuration_binding:b.configuration_source.binding,origin:b.configuration_source.origin}]);
   const externalEdges=externalBindings.flatMap(b=>[...operations.filter(o=>o.control.preflight.some(s=>s.kind==='read-external'&&s.call.binding_ref===b.id)).map(o=>({from:'operation:'+o.operation,to:'external:'+b.id,kind:'source-bound-external-read'})),{from:'external:'+b.id,to:'external-config:'+b.id,kind:'selected-immutable-origin'}]);
   const writeBindings=writeContract?.write_bindings??[];
   const writeNodes=writeBindings.flatMap(b=>[{id:'external-write:'+b.id,kind:'source-selected-write-inspect-pair',interface:b.interface_ref,write_operation:b.write_operation_ref,inspect_query:b.inspect_query_ref,protocol:b.protocol_id,selection:b.selection_source,native:b.native_source,mappings:{request:b.request_mapping_ref,inspect_request:b.inspect_request_mapping_ref,response:b.response_mapping_ref,validation:b.response_validation_rule_ref},continuations:{matches:b.matches_rule_ref,unresolved:b.unresolved_rule_ref}},{id:'external-intent:'+b.id,kind:'durable-external-intent',identity_limits:writeContract?.identity_limits}]);
   const writeEdges=writeBindings.flatMap(b=>{const callers=operations.filter(o=>o.control.preflight.some(s=>s.kind==='write-external'&&s.call.binding_ref===b.id));return [...callers.map(o=>({from:'operation:'+o.operation,to:'external-write:'+b.id,kind:'source-bound-write-inspect'})),{from:'external-write:'+b.id,to:'external-intent:'+b.id,kind:'durable-before-dispatch'},...(callers.some(o=>localOperations.includes(o))?[{from:'external-intent:'+b.id,to:storageId,kind:'same-sqlite-owner'}]:[])];});
   const eventBindings=eventContract?.event_bindings??[];
   const eventNodes=eventBindings.flatMap(b=>[{id:'event:'+b.id,kind:'source-bound-event',selector:b.event_selector,version:b.event_version,payload_schema_sha256:b.payload_schema_sha256,producer_service:b.producer_service,source_site:b.event_source_site},{id:'outbox:'+b.id,kind:'durable-event-outbox',service:b.producer_service},{id:'inbox:'+b.id,kind:'durable-event-inbox',service:b.target_service},{id:'receiver:'+b.id,kind:'protected-event-receiver',entry:b.target_entry,service:b.target_service,operation:b.consumer_operation,mapping:b.consumer_mapping,permission:b.target_permission}]);
   const eventEdges=eventBindings.flatMap(b=>[{from:'operation:'+b.producer_operation,to:'event:'+b.id,kind:'source-ordered-emission'},{from:'event:'+b.id,to:'outbox:'+b.id,kind:'same-producer-command-transaction'},{from:'outbox:'+b.id,to:'inbox:'+b.id,kind:'profile-owned-at-least-once-relay'},{from:'inbox:'+b.id,to:'receiver:'+b.id,kind:'fresh-auth-before-inbox-replay-and-commit'},{from:'receiver:'+b.id,to:'operation:'+b.consumer_operation,kind:'source-bound-consumer-mapping'}]);
   const workflowId=workflow?'workflow:'+workflow.workflow:undefined;
   const workflowEntries=workflow?[{entry:workflow.start_entry,contract_sha256:workflow.start_entry_contract_sha256},...workflow.steps.map(s=>({entry:s.entry,contract_sha256:s.entry_contract_sha256})),...workflow.steps.filter(s=>s.compensation_entry).map(s=>({entry:s.compensation_entry!,contract_sha256:s.compensation_contract_sha256!}))].filter((e,i,a)=>a.findIndex(x=>x.entry===e.entry)===i):[];
   const workflowNodes=workflow?[{id:workflowId!,kind:'source-checked-workflow-plan',artifact:'workflow-plan.json',workflow:workflow.workflow,service:workflow.service,profile_sha256:workflow.profile_sha256,source_capture_sha256:workflow.source_capture_sha256,contract_sha256:dataDigest(workflow),runtime_qualification:'worker-binding-required'},...workflowEntries.map(e=>({id:'workflow-entry:'+e.entry,kind:'checked-workflow-entry',entry:e.entry,contract_sha256:e.contract_sha256})),...workflow.steps.map(s=>({id:workflowId+':step:'+s.name,kind:'workflow-step',step:s.name,step_kind:s.kind,entry:s.entry,entry_contract_sha256:s.entry_contract_sha256,source_site:s.source_site}))]:[];
   const workflowEdges=workflow?[{from:workflowId!,to:'workflow-entry:'+workflow.start_entry,kind:'source-checked-start-entry'},...workflow.steps.flatMap(s=>[{from:workflowId!,to:workflowId+':step:'+s.name,kind:'declared-order-step'},{from:workflowId+':step:'+s.name,to:'workflow-entry:'+s.entry,kind:'checked-step-entry'},...(s.compensation_entry?[{from:workflowId+':step:'+s.name,to:'workflow-entry:'+s.compensation_entry,kind:'reverse-completion-compensation'}]:[])])]:[];
   const system=coreFreeze({schema_version:'craft.generic-transaction-system-view/v1-candidate',nodes:[{id:applicationId,kind:'node-esm-application',artifact:'application.mjs',entry:entry.entry,target:entry.target},...(httpTopology?httpTopology.nodes:[{id:httpId,kind:'injected-http-entry',artifact:'entry-http.mjs',method:'POST',route,entry:entry.entry}]),{id:storageId,kind:'sqlite-atomic-command-store',artifact:'storage/schema.json',service:entry.service,storage_projection_sha256:storage.storage_projection_sha256},{id:'journal:'+entry.service,kind:'immutable-command-journal',table:storage.journal.table,mutation_policy:storage.journal.mutation_policy},...(transport?[...routeEntries,...(privateEntry?[entry]:[])].map(candidate=>({id:'auth:'+candidate.entry,kind:'auth-foundation-ready',access:candidate.access})):[{id:authId,kind:'auth-foundation-ready',access:entry.access}]),...operations.map(o=>({id:'operation:'+o.operation,kind:'stateful-operation-assembly',operation:o.operation,contract_sha256:o.stateful_contract_sha256,source_sites:o.source_sites,roles:o.roles.map(r=>({path:r.path,source_site:r.source_site})),pure_calls:o.pure_calls.map(c=>({target:c.target,contract_sha256:c.target_contract_sha256,source_callsite:c.source_callsite}))})),...externalNodes,...writeNodes,...eventNodes,...workflowNodes],edges:[...(httpTopology?[...httpTopology.edges,...routeEntries.map(candidate=>({from:'entry:'+candidate.entry,to:applicationId,kind:'selected-application-entry'}))]:[{from:httpId,to:applicationId,kind:'original-protected-entry'}]),{from:applicationId,to:storageId,kind:commandEntry?'atomic-command':'protected-read'},...(transport?[...routeEntries.map(candidate=>({from:'entry:'+candidate.entry,to:'auth:'+candidate.entry,kind:'requires-permission'})),...(privateEntry?[{from:applicationId,to:authId,kind:'requires-permission'}]:[])]:[{from:applicationId,to:authId,kind:'requires-permission'}]),{from:storageId,to:'journal:'+entry.service,kind:'same-sqlite-transaction'},...localOperations.map(o=>({from:'operation:'+o.operation,to:storageId,kind:'source-declared-transaction'})),...externalEdges,...writeEdges,...eventEdges,...workflowEdges],authority_effect:'none'});
   const workflowLinks=workflow?[{business:workflow.workflow,system:workflowId!,source_site:workflow.source_site,source_capture_sha256:workflow.source_capture_sha256,profile_sha256:workflow.profile_sha256,base_application_sha256:workflow.base_application_sha256,contract_sha256:dataDigest(workflow),artifact:'workflow-plan.json'},...workflow.steps.map(s=>({business:workflow.workflow+'.'+s.name,system:workflowId+':step:'+s.name,source_site:s.source_site,entry:s.entry,entry_contract_sha256:s.entry_contract_sha256}))]:[];
   const bridge=coreFreeze({schema_version:'craft.generic-transaction-business-system-bridge/v1-candidate',source_origin_sha256:row.capture.authoredInput.source_origin_sha256,links:[{business:entry.entry,system:applicationId,profile:row.capture.inspection.profile.sha256,recipe:row.capture.inspection.profile.recipe_sha256,source_capture_sha256:source.capture_sha256,executable_semantics_sha256:row.capture.inspection.logical.executable_semantics_sha256},...(httpTopology?httpTopology.bridge_links:[{business:entry.entry,system:httpId,transport:'http',method:'POST',route}]),...storage.tables.map(t=>({business:t.entity,system:storageId,physical_table:t.physical_name,revision_column:t.revision_column,profile:row.capture.inspection.profile.sha256})),...operations.map(o=>({business:o.operation,system:'operation:'+o.operation,source_sites:o.source_sites,contract_sha256:o.stateful_contract_sha256})),...externalBindings.map(b=>({business:b.interface_ref,system:'external:'+b.id,provider_operation:b.provider_operation_ref,request_mapping:b.request_mapping.name,response_mapping:b.response_mapping.name,validation_rule:b.response_validation_rule.name,profile:b.profile_source.sha256})),...writeBindings.map(b=>({business:b.interface_ref,system:'external-write:'+b.id,write_operation:b.write_operation_ref,inspect_query:b.inspect_query_ref,protocol:b.protocol_id,selection_sha256:b.selection_source.sha256,native_sha256:b.native_source.sha256})),...writeBindings.map(b=>({business:b.write_operation_ref,system:'external-intent:'+b.id,identity_limits:writeContract?.identity_limits})),...eventBindings.flatMap(b=>[{business:b.event_selector,system:'event:'+b.id,source_site:b.event_source_site,payload_schema_sha256:b.payload_schema_sha256},{business:b.event_selector,system:'outbox:'+b.id,producer_service:b.producer_service},{business:b.target_entry,system:'inbox:'+b.id,target_service:b.target_service},{business:b.target_entry,system:'receiver:'+b.id,consumer_mapping:b.consumer_mapping,consumer_operation:b.consumer_operation,permission:b.target_permission}]) ,...workflowLinks],authority_effect:'none'});
   const httpSource=transport?"export const routes="+JSON.stringify(transport.contract.entries.map(candidate=>candidate.route.id))+";\nexport function createGeneratedHttpHandler(owner,handle,runtime,routeId){if(!routes.includes(routeId))throw Error('UNKNOWN_CHECKED_ROUTE');return owner.bindHttp(handle,runtime,routeId);}\n": "import {createGenericEntryHttpHandler} from '@domainspec-v2/cli/generic';\nexport const config="+JSON.stringify(httpConfig)+";\nexport function createGeneratedHttpHandler(runtime){return createGenericEntryHttpHandler(runtime,config);}\n";
   const artifacts=[...source.files.map(f=>({relative_path:'model/'+f.path,content:f.text})),{relative_path:'entry-http.mjs',content:httpSource},...([['storage/schema.json',storage],['business-graph.json',row.capture.inspection.logical],['system-graph.json',system],['business-system-bridge.json',bridge],...(transport?[['http-contract.json',transport.contract] as const,['http-plan.json',{schema_version:'craft.generic-http-plan/v1-candidate',contract:transport.contract,source_capture_sha256:source.capture_sha256,transport_semantics_sha256:transport.transport_semantics_sha256,authority_effect:'none'}] as const]:[]),...(workflowProjection?[['workflow-plan.json',{schema_version:'craft.generic-workflow-plan/v1-candidate',contract:workflowProjection.contract,derivation:workflowProjection.derivation,qualification:'source-checked;worker-binding-required',authority_effect:'none'}] as const]:[])] as const).map(([relative_path,value])=>({relative_path,content:JSON.stringify(value,null,2)+'\n'}))];
   addPolicyEnforcementArtifacts(artifacts,projectPolicyEnforcementLineage({artifactNode:applicationId,functions:app.contract.functions,operations:[...app.contract.pure_operations.map(o=>({operation:o.operation.module+'.'+o.operation.name,body:o.body})),...operations.map(o=>({operation:o.operation,body:o.control.preflight}))]}));
   addCapabilityArtifacts(h,artifacts);
   const files=artifacts.map(f=>({path:f.relative_path,sha256:coreSha256(f.content),bytes:Buffer.byteLength(f.content)}));
   const bundle={schema_version:'craft.generic-transaction-bundle/v1-candidate',entry:entry.entry,executable_semantics_sha256:row.capture.inspection.logical.executable_semantics_sha256,assurance_sha256:row.capture.inspection.assurance.assurance_sha256,recipe_sha256:row.capture.inspection.profile.recipe_sha256,profile_sha256:row.capture.inspection.profile.sha256,authored_input:row.capture.authoredInput,...(transport?{http_profile:row.capture.inspection.http_profile,transport_semantics_sha256:transport.transport_semantics_sha256}:{}),...(row.capture.inspection.workflow_profile?{workflow_profile:row.capture.inspection.workflow_profile}:{}),...(row.capture.inspection.external_profile?{external_profile:row.capture.inspection.external_profile,external_config:row.capture.inspection.external_config}:{}),...(row.capture.inspection.external_write_selection?{external_write_selection:row.capture.inspection.external_write_selection,native_profiles:row.capture.inspection.native_profiles}:{}),...capabilityOverlay(h,artifacts),files};
   const code="import {createGenericBundledApplicationOwner} from '@domainspec-v2/cli/generic';\nconst bundle="+JSON.stringify(bundle)+";\nexport function createGeneratedApplicationOwner(){return createGenericBundledApplicationOwner(import.meta.url,bundle);}\n";
   artifacts.push({relative_path:'application.mjs',content:code});
   const invocation=commandEntry?{kind:'command',prepare:'prepareCommand',execute:'executeCommand',inspect:'inspectCommand',metadata:{type:'GenericCommandMetadataV1',required:['client_key'],additional_properties:false,client_key:{type:'string',min_unicode_scalars:1,max_unicode_scalars:128,max_utf8_bytes:128,normalization:'none'}}}:{kind:'read',prepare:'prepareInput',execute:'execute'};
   const runtimeContract={invocation,...(transport?{http_contract:transport.contract}:{}),http:transport?{routes:transport.contract.entries.map(candidate=>candidate.route),module:'entry-http.mjs',profile:'model/contracts/http-profile.json',transport_semantics_sha256:transport.transport_semantics_sha256,identity:'injected-original-runtime-actor'}:{method:'POST',route,module:'entry-http.mjs',identity:'injected-original-runtime-actor'},application_schema_version:app.contract.schema_version,semantics_revision:app.contract.semantics_revision,storage_schema_version:storage.schema_version,profile_schema_version:transport?'craft.generic-http-profile/v1-candidate':eventMode?'craft.generic-event-profile/v1-candidate':'craft.generic-transaction-profile/v1-candidate',transaction_bounds:app.contract.transaction_bounds};
   const allFiles=artifacts.map(f=>({path:f.relative_path,sha256:coreSha256(f.content),bytes:Buffer.byteLength(f.content)})),manifest=coreFreeze({...row.capture.inspection,...(capabilityProjection(h)?{capability_bindings:capabilityProjection(h),capability_wiring:capabilityGeneration(h).plan}:{}),source:{...row.capture.inspection.source,files:source.files.map(({path,sha256,bytes})=>({path,sha256,bytes}))},entry:entry.entry,runtime_contract:runtimeContract,selected_recipe:{kind:'Entry',module:'application.mjs',recipe_sha256:row.capture.inspection.profile.recipe_sha256},files:allFiles,output_sha256:dataDigest(allFiles),review:row.capture.reviews.inspect(row.review!),qualification:transport?'http-source-and-artifact-candidate;runtime-qualification-pending':'atomic-source-and-artifact-candidate;runtime-qualification-pending'});
   artifacts.push({relative_path:'manifest.json',content:generatedManifestContent(manifest)});
   publishAtomicDirectory(raw.outputDirectory,artifacts,'.domainspec-atomic-',()=>{capabilityProjection(h);binding.assertCurrent();});binding.assertCurrent();return manifest;
  },
  dispose(h:GenericCompositionHandle){const r=current(h);if(r.application&&r.plans)r.plans.dispose(r.application);r.capture.semantics.dispose(r.capture.semantic);r.capture.sources.dispose(r.capture.source);r.capture.expandedSemantics.dispose(r.capture.expandedSemantic);r.capture.expandedSources.dispose(r.capture.expanded);r.disposed=true;},
 });
}
const atomicPlanPin=pinCoreImplementation(import.meta.url,['repository-plan'+ext,'operation-assembly'+ext,'value-codec'+ext,'source-review-owner'+ext,'transaction-data-v1'+ext]);

/** Explicit checked HTTP overlay on the original atomic application. */
export function createGenericHttpCompositionOwner(){
 const original=createTransactionCompositionOwner(true);
 const current=(h:GenericCompositionHandle)=>{original.assertCurrent(h);capabilityProjection(h);};
 const owner=Object.freeze({
  async prepare(input:{sourcePath:string;profilePath:string;additionalSourcePaths?:readonly string[];externalProfilePath?:string;externalWriteSelectionPath?:string;httpProfilePath?:string;capabilitySelectionPath?:string}){
   const captured=captureTransactionPreparation(input),h=await original.prepare(input);
   try{if(captured.capabilitySelectionPath){const b=original.sourceBinding(h),o=createGenericCapabilityFormationOwner(b.sources,b.source,b.semantics,b.semantic);capabilityFormations.set(h,{owner:o,handle:o.prepare(captured.capabilitySelectionPath,captured.sourcePath,captured.profilePath)});}return h;}catch(e){original.dispose(h);throw e;}
  },review:original.review,accept:original.accept,
  inspect(h:GenericCompositionHandle){current(h);const v=original.inspect(h),c=capabilityProjection(h);return c?coreFreeze({...v,capability_bindings:c}):v;},inspectCapabilities(h:GenericCompositionHandle){current(h);return capabilityProjection(h);},assertCurrent:current,generate:original.generate,dispose:original.dispose,
  async openWorkflow(h:GenericCompositionHandle,options:import('./workflow-driver.js').GenericWorkflowDriverOptions){
   const {openGenericWorkflowDriver}=await import('./workflow-driver.js');
   return openGenericWorkflowDriver(owner,h,options);
  },
  async openRuntime(h:GenericCompositionHandle,options:GenericRuntimeOptions):Promise<GenericTransactionApplicationRuntime>{
   requireGenericCompositionRuntime(owner,h);const {createGenericApplicationRuntime}=await import('./invocation-owner.js');
   const runtime=await createGenericApplicationRuntime(owner,h,options);
   if(!('prepareCommand'in runtime)){runtime.close();return fail('InvalidContract',at,'original atomic HTTP runtime required');}
   return runtime;
  },
  bindHttp(h:GenericCompositionHandle,runtime:GenericTransactionApplicationRuntime,routeId:string){requireGenericCompositionRuntime(owner,h);return createGenericHttpHandler(owner,h,runtime,routeId);},
 });
 capabilityParents.set(owner,h=>{current(h);if(!capabilityProjection(h))fail('UnsupportedCapability',at,'selected capability source required');return {generation:()=>{current(h);return capabilityGeneration(h);},assertCurrent:()=>current(h)};});
 compositionRegistry.set(owner,h=>original.runtimeBinding(h));
 workflowRegistry.set(owner,h=>original.workflowBinding(h));
 return owner;
}


function createKeyedCompositionOwner(){
 const sources=createCoreCommerceSourceOwner('keyed-query-entry');
 const semantics=createGenericSemanticOwner(sources,'keyed-query-entry');
 const expandedSources=createCoreCommerceSourceOwner('keyed-query-entry');
 const expandedSemantics=createGenericSemanticOwner(expandedSources,'keyed-query-entry');
 const reviews=createGenericSourceReviewOwner(expandedSemantics);
 type Physical=ReturnType<typeof readCorePhysicalFile>;
 type Row={source:CoreCommerceSourceCapture;semantic:GenericSemanticCapture;expanded:CoreCommerceSourceCapture;expandedSemantic:GenericSemanticCapture;originals:Physical[];inspection:any;review?:GenericReviewCapture|undefined;accepted?:GenericAcceptedReview|undefined;plans?:GenericRepositoryPlanOwner|undefined;application?:GenericKeyedApplicationHandle|undefined;disposed:boolean};
 const rows=new WeakMap<object,Row>();
 const current=(handle:GenericCompositionHandle)=>{
  const row=handle&&typeof handle==='object'?rows.get(handle):undefined;
  if(!row)fail('ForeignOwner',at,'original keyed composition handle required');
  if(row.disposed)fail('DisposedOwner',at,'keyed composition disposed');
  pin.assertCurrent();keyedPin.assertCurrent();
  for(const f of row.originals)if(readCorePhysicalFile(f.file.path).fingerprint!==f.fingerprint)fail('StaleOwner',at,'original business source/profile/bounds changed');
  sources.assertCurrent(row.source);semantics.assertSource(row.semantic,row.source);
  expandedSources.assertCurrent(row.expanded);expandedSemantics.assertSource(row.expandedSemantic,row.expanded);
  return row;
 };
 const runtimeBinding=(h:GenericCompositionHandle):GenericKeyedCompositionRuntimeBinding=>{
  const row=current(h),{plans,application,accepted}=row;
  if(!plans||!application||!accepted)fail('MissingMapping',at,'current accepted keyed source review required');
  const assertCurrent=()=>{const r=current(h);if(r.plans!==plans||r.application!==application||r.accepted!==accepted)fail('StaleOwner',at,'runtime belongs to an earlier accepted review');reviews.assertAcceptedSemantic(accepted,row.expandedSemantic);plans.assertCurrent(application);};
  assertCurrent();return Object.freeze({plans,application,assertCurrent});
 };
 return Object.freeze({
  async prepare({sourcePath,profilePath}:{sourcePath:string;profilePath:string}):Promise<GenericCompositionHandle>{
   pin.assertCurrent();keyedPin.assertCurrent();
   if(!path.isAbsolute(sourcePath)||!sourcePath.endsWith('.alch')||!path.isAbsolute(profilePath))fail('InvalidContract',at,'absolute business/profile files required');
   const runtimePackage=captureKeyedPackage(),original=readCorePhysicalFile(sourcePath),bounds=readCorePhysicalFile(path.join(path.dirname(sourcePath),'contracts/bounds.json')),profile=readCorePhysicalFile(profilePath);
   const raw=parseCoreCommerceJson(bounds.text,bounds.file.path) as any;
   if(raw?.schema_version!=='craft.generic-compute-bounds/v1-candidate'||raw.computation?.required_schema_version!=='craft.generic-computation/v1-candidate'||raw.computation?.required_semantics_revision!=='ordered-metered-generic-v1-candidate')fail('MissingMapping',at,'exact generic source bounds required');
   const selected=resolveGenericKeyedProfile(profile.text,profilePath,raw.computation.limits),business=reconstructCoreCommerceModule(original.text,'source/business.alch');
   if(business.module==='Craft.Generated.Auth'||business.module.startsWith('Craft.Generated.Auth.')||business.module==='CraftGenerated.Root')fail('InvalidContract',at,'generated namespace is reserved');
   for(const d of business.declarations)if(!['Rule','ValueObject','Enum','Operation','Mapping','Calculation','Policy','StateMachine','Entity','Query','Entry'].includes(d.surface)&&!(d.surface==='Interface'&&d.interface_kind==='bounded-schema'))fail('UnsupportedCapability',d.syntax,'business-only keyed declarations required');
   const applicationText='module CraftGenerated.Root version 1\ninterface Application:\n  kind application-composition\n  source source/business.alch\n  source generated/auth-context.alch\n'+selected.services.map(s=>'  service '+s.id+' module '+s.module+'\n').join('')+'  computation-bounds contracts/bounds.json\n  parameters contracts/selected-profile.json\n';
   const logicalRoot=mkdtempSync(path.join(tmpdir(),'craft-keyed-logical-'));
   const model=[{path:'application.alch',text:applicationText},{path:'source/business.alch',text:original.text},{path:'contracts/bounds.json',text:bounds.text},{path:'contracts/selected-profile.json',text:profile.text},{path:'generated/auth-context.alch',text:KEYED_AUTH_SOURCE},{path:'generated/auth-context.json',text:JSON.stringify(KEYED_AUTH_CONTEXT,null,2)+'\n'}];
   for(const f of model){const destination=path.join(logicalRoot,f.path);mkdirSync(path.dirname(destination),{recursive:true});writeCoreExclusiveFile(destination,f.text);}
   const source=sources.prepare(logicalRoot,'application.alch'),semantic=semantics.check(source),logical=sources.inspect(source),checked=semantics.inspect(semantic);
   const expandedRoot=mkdtempSync(path.join(tmpdir(),'craft-keyed-expanded-'));
   for(const f of logical.files){const destination=path.join(expandedRoot,f.path);mkdirSync(path.dirname(destination),{recursive:true});writeCoreExclusiveFile(destination,f.text);}
   const expanded=expandedSources.prepare(expandedRoot,'application.alch'),expandedSemantic=expandedSemantics.check(expanded),expansion=expandedSources.inspect(expanded),actual=expandedSemantics.inspect(expandedSemantic);
   if(checked.admission_mode!=='keyed-query-entry'||actual.admission_mode!=='keyed-query-entry')fail('InvalidContract',at,'actual keyed semantic admission required');
   if(checked.executable_sha256!==actual.executable_sha256||dataDigest(checked.keyed_contract)!==dataDigest(actual.keyed_contract))fail('InvalidContract',at,'expanded keyed semantics differ from original reconstructed source');
   const graph=(capture:typeof logical,sem:typeof checked,businessOnly:boolean)=>({admission_mode:sem.admission_mode,capture_sha256:capture.capture_sha256,executable_semantics_sha256:sem.executable_sha256,nodes:capture.reconstruction.modules.filter(m=>!businessOnly||m.path==='source/business.alch').flatMap(m=>m.declarations.map(d=>({id:d.id,kind:d.surface,source:{path:m.path,sha256:m.sha256,start:d.syntax.start,end:d.syntax.end}}))),ownership:capture.reconstruction.ownership.filter(o=>!businessOnly||o.declaration.startsWith(business.module+'.'))});
   const inspection=coreFreeze({schema_version:'craft.generic-composition-inspection/v1-candidate',source:{path:sourcePath,sha256:original.file.sha256,bounds:bounds.file,files:logical.files.map(({path,sha256,bytes})=>({path,sha256,bytes}))},profile:{id:selected.id,path:profilePath,sha256:profile.file.sha256,recipe:KEYED_PROFILE_RECIPE,recipe_sha256:dataDigest(KEYED_PROFILE_RECIPE)},logical:graph(logical,checked,true),expanded:{...graph(expansion,actual,false),origins:[{declaration:'CraftGenerated.Root.Application',kind:'technical',recipe_sha256:dataDigest(KEYED_PROFILE_RECIPE)},{module:'Craft.Generated.Auth',kind:'technical',recipe_sha256:dataDigest(KEYED_PROFILE_RECIPE)},{module:business.module,kind:'unchanged-business',original:original.file}]},capabilities:selected.capabilities,operations:actual.effects,queries:actual.reads,entries:actual.entries,keyed_contract:actual.keyed_contract,reachable_operations:actual.keyed_contract.pure_operations.map(operation=>deriveGenericReachableOperationSemantics(operation,actual.keyed_contract.functions,actual.keyed_contract.values,actual.keyed_contract.limits)),compiler_sha256:keyedPin.sha256,limits:selected.limits,qualification:'C07-source-keyed-query-protected-read-candidate',authority_effect:'none'});
   const handle=Object.freeze({kind:'original-generic-composition/v1-candidate' as const});
   rows.set(handle,{source,semantic,expanded,expandedSemantic,originals:[original,bounds,profile,runtimePackage],inspection,disposed:false});current(handle);return handle;
  },
  review(h:GenericCompositionHandle,label:string){const row=current(h);row.accepted=undefined;row.plans=undefined;row.application=undefined;row.review=reviews.prepare(row.expandedSemantic,label);return reviews.inspect(row.review);},
  accept(h:GenericCompositionHandle,request:{decision_id:string;owner:string;outcome:'accepted'|'declined';reviewed_digest:string},decisionPath:string){
   const row=current(h);if(!row.review)fail('MissingMapping',at,'prepare explicit source review first');row.accepted=undefined;row.plans=undefined;row.application=undefined;
   const decision=reviews.recordDecision(row.review,request,decisionPath),accepted=reviews.requireAccepted(row.review,decision);
   const checked=expandedSemantics.inspect(row.expandedSemantic);if(checked.admission_mode!=='keyed-query-entry')fail('InvalidContract',at,'actual keyed semantic admission required');
   const plans=createGenericRepositoryPlanOwner(expandedSources,row.expanded,expandedSemantics,row.expandedSemantic,reviews,accepted),application=plans.check(checked.keyed_contract);
   row.accepted=accepted;row.plans=plans;row.application=application;runtimeBinding(h);return reviews.inspectDecision(decision);
  },
  sourceBinding(h:GenericCompositionHandle){const r=current(h);return {sources:expandedSources,source:r.expanded,semantics:expandedSemantics,semantic:r.expandedSemantic};},
  inspect(h:GenericCompositionHandle){return current(h).inspection;},
  assertCurrent(h:GenericCompositionHandle){current(h);},
  runtimeBinding,
  generate(h:GenericCompositionHandle,selection:GenericSelection&{outputDirectory:string}){
   const raw=captureJson(selection) as any;
   if(!raw||typeof raw!=='object'||Array.isArray(raw)||Object.keys(raw).sort().join(',')!=='entry,outputDirectory'||typeof raw.entry!=='string'||typeof raw.outputDirectory!=='string'||!path.isAbsolute(raw.outputDirectory)||path.normalize(raw.outputDirectory)!==raw.outputDirectory)fail('InvalidContract',at,'exact entry selector and normalized new output directory required');
   const row=current(h),binding=runtimeBinding(h),entry=binding.plans.inspectEntry(binding.plans.bindEntry(binding.application,raw.entry)),service=binding.plans.bindService(binding.application,entry.service);
   const storage=deriveGenericStorageDescriptor(binding.plans,binding.application,service),source=expandedSources.inspect(row.expanded);
   const system={schema_version:'craft.generic-system-view/v1-candidate',nodes:[{id:'generated:'+entry.entry,kind:'node-esm-application',artifact:'application.mjs'},{id:'storage:'+entry.service,kind:'sqlite-keyed-store',artifact:'storage/schema.json'},{id:'auth:'+entry.entry,kind:'auth-foundation-ready',permission:entry.access.permission}],edges:[{from:'generated:'+entry.entry,to:'storage:'+entry.service,kind:'protected-read'},{from:'generated:'+entry.entry,to:'auth:'+entry.entry,kind:'requires-permission'}],authority_effect:'none'};
   const bridge={schema_version:'craft.generic-business-system-bridge/v1-candidate',links:[{business:entry.entry,system:'generated:'+entry.entry,profile:row.inspection.profile.sha256,recipe:row.inspection.profile.recipe_sha256,source_capture_sha256:source.capture_sha256,executable_semantics_sha256:row.inspection.logical.executable_semantics_sha256},...storage.tables.map(t=>({business:t.entity,system:'storage:'+entry.service,physical_table:t.physical_name,profile:row.inspection.profile.sha256}))],authority_effect:'none'};
   const artifacts=[...source.files.map(f=>({relative_path:'model/'+f.path,content:f.text})),...([['storage/schema.json',storage],['business-graph.json',row.inspection.logical],['system-graph.json',system],['business-system-bridge.json',bridge]] as const).map(([relative_path,value])=>({relative_path,content:JSON.stringify(value,null,2)+'\n'}))];
   addCapabilityArtifacts(h,artifacts);
   const files=artifacts.map(f=>({path:f.relative_path,sha256:coreSha256(f.content),bytes:Buffer.byteLength(f.content)}));
   const bundle={schema_version:'craft.generic-keyed-bundle/v1-candidate',entry:entry.entry,executable_semantics_sha256:row.inspection.logical.executable_semantics_sha256,recipe_sha256:row.inspection.profile.recipe_sha256,...capabilityOverlay(h,artifacts),files};
   const code="import {createGenericBundledApplicationOwner} from '@domainspec-v2/cli/generic';\nconst bundle="+JSON.stringify(bundle)+";\nexport function createGeneratedApplicationOwner(){return createGenericBundledApplicationOwner(import.meta.url,bundle);}\n";
   artifacts.push({relative_path:'application.mjs',content:code});
   const allFiles=artifacts.map(f=>({path:f.relative_path,sha256:coreSha256(f.content),bytes:Buffer.byteLength(f.content)}));
   const manifest=coreFreeze({...row.inspection,...(capabilityProjection(h)?{capability_bindings:capabilityProjection(h),capability_wiring:capabilityGeneration(h).plan}:{}),entry:entry.entry,selected_recipe:{kind:'Entry',module:'application.mjs',recipe_sha256:row.inspection.profile.recipe_sha256},files:allFiles,output_sha256:dataDigest(allFiles),review:reviews.inspect(row.review!)});
   artifacts.push({relative_path:'manifest.json',content:generatedManifestContent(manifest)});
   publishAtomicDirectory(raw.outputDirectory,artifacts,'.domainspec-keyed-',()=>{capabilityProjection(h);binding.assertCurrent();});binding.assertCurrent();return manifest;
  },
  dispose(h:GenericCompositionHandle){const row=current(h);row.disposed=true;semantics.dispose(row.semantic);sources.dispose(row.source);expandedSemantics.dispose(row.expandedSemantic);expandedSources.dispose(row.expanded);},
 });
}

/** Fresh source recapture factory used by generated installed adapters. It carries no acceptance. */

/** Fresh atomic recapture retains the entire original envelope throughout use. */
function createGenericTransactionBundledApplicationOwner(moduleUrl:string,proposal:unknown){
 const bundle=captureJson(proposal) as any;
 const hex=(x:unknown)=>typeof x==='string'&&/^[a-f0-9]{64}$/.test(x);
 const keys=(x:unknown,expected:string)=>!!x&&typeof x==='object'&&!Array.isArray(x)&&Object.keys(x).sort().join(',')===expected;
 const externalBundle=!!bundle&&typeof bundle==='object'&&(Object.hasOwn(bundle,'external_profile')||Object.hasOwn(bundle,'external_config'));
 const writeBundle=!!bundle&&typeof bundle==='object'&&(Object.hasOwn(bundle,'external_write_selection')||Object.hasOwn(bundle,'native_profiles'));
 const workflowBundle=!!bundle&&typeof bundle==='object'&&Object.hasOwn(bundle,'workflow_profile');
 const httpBundle=!!bundle&&typeof bundle==='object'&&(Object.hasOwn(bundle,'http_profile')||Object.hasOwn(bundle,'transport_semantics_sha256'));
 const capabilityBundle=!!bundle&&typeof bundle==='object'&&Object.hasOwn(bundle,'capabilities');
 const bundleKeys=['assurance_sha256','authored_input','entry','executable_semantics_sha256','files','profile_sha256','recipe_sha256','schema_version',...(httpBundle?['http_profile','transport_semantics_sha256']:[]),...(workflowBundle?['workflow_profile']:[]),...(externalBundle?['external_config','external_profile']:[]),...(writeBundle?['external_write_selection','native_profiles']:[]),...(capabilityBundle?['capabilities']:[])].sort().join(',');
 if(!keys(bundle,bundleKeys)||writeBundle&&!externalBundle||bundle.schema_version!=='craft.generic-transaction-bundle/v1-candidate'||typeof bundle.entry!=='string'||!hex(bundle.executable_semantics_sha256)||!hex(bundle.assurance_sha256)||!hex(bundle.profile_sha256)||![dataDigest(TRANSACTION_PROFILE_RECIPE),dataDigest(EVENT_PROFILE_RECIPE)].includes(bundle.recipe_sha256)||!Array.isArray(bundle.files)||bundle.files.length<7||bundle.files.length>128)fail('InvalidContract',at,'closed generated atomic bundle required');
 const validFile=(f:any)=>keys(f,'bytes,path,sha256')&&typeof f.path==='string'&&coreRelativePath(f.path)&&hex(f.sha256)&&Number.isSafeInteger(f.bytes)&&f.bytes>=0&&f.bytes<=1048576;
 if(httpBundle&&(!validFile(bundle.http_profile)||bundle.http_profile.path!=='contracts/http-profile.json'||!hex(bundle.transport_semantics_sha256)))fail('InvalidContract',at,'exact checked request-response HTTP overlay bundle required');
 if(workflowBundle&&(!validFile(bundle.workflow_profile)||bundle.workflow_profile.path!=='contracts/workflow-profile.json'||bundle.recipe_sha256!==dataDigest(EVENT_PROFILE_RECIPE)))fail('InvalidContract',at,'exact source-selected Workflow bundle profile required');
 if(externalBundle&&(!validFile(bundle.external_profile)||bundle.external_profile.path!=='contracts/external-profile.json'||!validFile(bundle.external_config)||bundle.external_config.path!=='contracts/external-config.json'))fail('InvalidContract',at,'exact external bundle profile/config identities required');
 if(writeBundle&&(!validFile(bundle.external_write_selection)||bundle.external_write_selection.path!=='contracts/external-write-bindings.json'||!Array.isArray(bundle.native_profiles)||bundle.native_profiles.length<1||bundle.native_profiles.length>16||bundle.native_profiles.some((f:any)=>!validFile(f)||!f.path.startsWith('native/')||!f.path.endsWith('.json'))||new Set(bundle.native_profiles.map((f:any)=>f.path)).size!==bundle.native_profiles.length))fail('InvalidContract',at,'exact bounded write selection and native profile identities required');
 const a=bundle.authored_input;
 if(!keys(a,'additional_sources,claim_assets,computation_bounds,primary_source,profile,schema_version,source_origin_sha256,transaction_bounds')||a.schema_version!=='craft.generic-transaction-authored-input/v1-candidate'||!hex(a.source_origin_sha256)||!Array.isArray(a.additional_sources)||a.additional_sources.length>31||!Array.isArray(a.claim_assets)||a.claim_assets.length>16)fail('InvalidContract',at,'closed generated authored input required');
 const authored=[a.primary_source,...a.additional_sources,a.computation_bounds,a.transaction_bounds,...a.claim_assets,a.profile];
 if(authored.some(f=>!validFile(f))||new Set(authored.map(f=>f.path)).size!==authored.length||!a.primary_source.path.endsWith('.alch')||a.primary_source.path.includes('/')||a.additional_sources.some((f:any)=>!f.path.endsWith('.alch'))||a.computation_bounds.path!=='contracts/bounds.json'||a.transaction_bounds.path!=='contracts/transactions.json'||a.profile.path!=='contracts/selected-profile.json'||a.profile.sha256!==bundle.profile_sha256)fail('InvalidContract',at,'exact unique authored input paths and identities required');
 const sorted=(xs:any[])=>xs.every((f,i)=>i===0||Buffer.compare(Buffer.from(xs[i-1].path,'utf8'),Buffer.from(f.path,'utf8'))<0);
 if(!sorted(a.additional_sources)||!sorted(a.claim_assets)||a.claim_assets.reduce((n:number,f:any)=>n+f.bytes,0)>262144)fail('InvalidContract',at,'ordered bounded unique authored files required');
 const known=new Map<string,{path:string;sha256:string;bytes:number}>();
 for(const f of bundle.files){if(!validFile(f)||known.has(f.path))fail('InvalidContract',at,'bounded unique generated file pins required');known.set(f.path,f);}
 const technical=['application.alch','generated/auth-context.alch','generated/auth-context.json'];
 const expected=new Set([...authored.map(f=>'model/'+f.path),...technical.map(p=>'model/'+p),'entry-http.mjs','storage/schema.json','business-graph.json','system-graph.json','business-system-bridge.json']);
 if(httpBundle){expected.add('model/contracts/http-profile.json');expected.add('http-plan.json');expected.add('http-contract.json');}
 if(externalBundle){for(const p of ['contracts/external-profile.json','contracts/external-config.json',EXTERNAL_GENERATION_PATH,EXTERNAL_COMPOSITION_PATH,'contracts/external-assets/profile.json'])expected.add('model/'+p);for(const f of bundle.files)if(f.path.startsWith('model/generated/external-')||f.path.startsWith('model/contracts/external-assets/templates/')||f.path.startsWith('model/contracts/external-recipes/'))expected.add(f.path);}
 if(writeBundle){expected.add('model/contracts/external-write-bindings.json');for(const f of bundle.native_profiles)expected.add('model/'+f.path);}
 if(workflowBundle){expected.add('model/contracts/workflow-profile.json');expected.add('workflow-plan.json');}
 const capabilityFiles=capabilityBundle?checkCapabilityOverlay(bundle.capabilities,known):new Set<string>();for(const p of capabilityFiles)expected.add(p);
 if(expected.size!==known.size||[...expected].some(p=>!known.has(p)))fail('InvalidContract',at,'exact complete generated closure required');
 if(externalBundle&&(['external_profile','external_config'] as const).some(k=>{const f=bundle[k],actual=known.get('model/'+f.path);return !actual||actual.sha256!==f.sha256||actual.bytes!==f.bytes;}))fail('InvalidContract',at,'external profile/config file pins differ');
 if(writeBundle&&[bundle.external_write_selection,...bundle.native_profiles].some((f:any)=>{const actual=known.get('model/'+f.path);return !actual||actual.sha256!==f.sha256||actual.bytes!==f.bytes;}))fail('InvalidContract',at,'write selection/native profile file pins differ');
 if(workflowBundle){const f=bundle.workflow_profile,actual=known.get('model/'+f.path);if(!actual||actual.sha256!==f.sha256||actual.bytes!==f.bytes)fail('InvalidContract',at,'Workflow overlay profile file pin differs');}
 if(httpBundle){const f=bundle.http_profile,actual=known.get('model/'+f.path);if(!actual||actual.sha256!==f.sha256||actual.bytes!==f.bytes)fail('InvalidContract',at,'HTTP overlay profile file pin differs');}
 const modelFiles=bundle.files.filter((f:any)=>f.path.startsWith('model/')&&!capabilityFiles.has(f.path));
 if(modelFiles.length>128||modelFiles.reduce((n:number,f:any)=>n+f.bytes,0)>4194304)fail('ResourceLimit',at,'generated model closure exceeds file or aggregate byte bound');
 for(const f of authored){const actual=known.get('model/'+f.path)!;if(actual.sha256!==f.sha256||actual.bytes!==f.bytes)fail('InvalidContract',at,'authored identity must match full generated inventory');}
 const url=new URL(moduleUrl);if(url.protocol!=='file:')fail('InvalidContract',at,'physical generated module required');
 const directory=path.dirname(fileURLToPath(url)),envelope=[captureKeyedPackage(),readCorePhysicalFile(fileURLToPath(url)),readCorePhysicalFile(path.join(directory,'manifest.json')),...bundle.files.map((f:any)=>readCorePhysicalFile(path.join(directory,f.path)))];
 for(const f of bundle.files){const physical=envelope.find(row=>row.file.path===path.join(directory,f.path));if(!physical||physical.file.sha256!==f.sha256||physical.file.bytes!==f.bytes)fail('StaleOwner',at,'generated atomic source or artifact changed');}
 const physicalPin=pinCorePhysicalCaptures(envelope);
 const assertBundle=()=>{try{pin.assertCurrent();atomicPlanPin.assertCurrent();physicalPin.assertCurrent();}catch(error){if(error instanceof CoreCommerceSourceError&&error.diagnostics[0]?.code==='StaleOwner')fail('StaleOwner',at,'original generated atomic bundle unavailable or changed');throw error;}};
 assertBundle();const original=httpBundle?createGenericHttpCompositionOwner():createGenericCompositionOwner(),handles=new WeakSet<object>();
 const current=(h:GenericCompositionHandle)=>withCorePhysicalIdentityPhase(()=>{assertBundle();if(!h||typeof h!=='object'||!handles.has(h))fail('ForeignOwner',at,'original generated atomic handle required');original.assertCurrent(h);});
 const owner=Object.freeze({
  async prepare(...args:unknown[]){
   if(args.length)fail('InvalidContract',at,'generated preparation takes no caller paths');assertBundle();
   const root=mkdtempSync(path.join(tmpdir(),'craft-atomic-bundled-authored-'));
   for(const f of [...authored,...(capabilityBundle?bundle.capabilities.assets:[]),...(httpBundle?[bundle.http_profile]:[]),...(workflowBundle?[bundle.workflow_profile]:[]),...(externalBundle?[bundle.external_profile,bundle.external_config]:[]),...(writeBundle?[bundle.external_write_selection,...bundle.native_profiles]:[])]){const destination=path.join(root,f.path);mkdirSync(path.dirname(destination),{recursive:true});writeCoreExclusiveFile(destination,readCorePhysicalFile(path.join(directory,'model/'+f.path)).text);}
   assertBundle();const h=await original.prepare({sourcePath:path.join(root,a.primary_source.path),profilePath:path.join(root,a.profile.path),additionalSourcePaths:a.additional_sources.map((f:any)=>path.join(root,f.path)),...(httpBundle?{httpProfilePath:path.join(root,bundle.http_profile.path)}:{}),...(externalBundle?{externalProfilePath:path.join(root,bundle.external_profile.path)}:{}),...(writeBundle?{externalWriteSelectionPath:path.join(root,bundle.external_write_selection.path)}:{}),...(capabilityBundle?{capabilitySelectionPath:path.join(root,bundle.capabilities.selection_path)}:{})});
   try{
    const inspection=original.inspect(h);
    if(capabilityBundle&&capabilityGeneration(h).plan_sha256!==bundle.capabilities.plan_sha256)fail('InvalidContract',at,'regenerated capability wiring differs from original bundle');
    if(inspection.logical.executable_semantics_sha256!==bundle.executable_semantics_sha256||inspection.assurance.assurance_sha256!==bundle.assurance_sha256||inspection.profile.recipe_sha256!==bundle.recipe_sha256||inspection.profile.sha256!==bundle.profile_sha256||dataDigest(inspection.authored_input)!==dataDigest(a))fail('InvalidContract',at,'fresh generated atomic source identities differ');
    const order=(x:{path:string},y:{path:string})=>Buffer.compare(Buffer.from(x.path,'utf8'),Buffer.from(y.path,'utf8'));
    const regenerated=inspection.source.files.map((f:{path:string;sha256:string;bytes:number})=>({path:'model/'+f.path,sha256:f.sha256,bytes:f.bytes})).sort(order);
    if(dataDigest(regenerated)!==dataDigest([...modelFiles].sort(order)))fail('InvalidContract',at,'entire regenerated model differs from the original bundle inventory');
    if(workflowBundle){const plan=parseCoreCommerceJson(readCorePhysicalFile(path.join(directory,'workflow-plan.json')).text,'workflow-plan.json') as any,actual=inspection.workflow_contract,comparable=(value:any)=>{if(!value||typeof value!=='object')fail('InvalidContract',at,'Workflow bundle plan contract required');const {source_capture_sha256:_capture,...rest}=value;return rest;};if(plan?.schema_version!=='craft.generic-workflow-plan/v1-candidate'||!actual||plan.qualification!=='source-checked;worker-binding-required'||dataDigest(comparable(plan.contract))!==dataDigest(comparable(actual))||plan.derivation?.profile_sha256!==actual.profile_sha256)fail('InvalidContract',at,'regenerated Workflow differs from pinned generated plan');}
    if(httpBundle){const emitted=parseCoreCommerceJson(readCorePhysicalFile(path.join(directory,'http-contract.json')).text,'http-contract.json'),plan=parseCoreCommerceJson(readCorePhysicalFile(path.join(directory,'http-plan.json')).text,'http-plan.json') as any,actual=inspection.http_contract;if(plan?.schema_version!=='craft.generic-http-plan/v1-candidate'||!actual||plan.transport_semantics_sha256!==bundle.transport_semantics_sha256||inspection.transport_semantics_sha256!==bundle.transport_semantics_sha256||dataDigest(plan.contract)!==dataDigest(actual)||dataDigest(emitted)!==dataDigest(actual))fail('InvalidContract',at,'regenerated HTTP routes differ from pinned generated plan or contract');}
    assertBundle();handles.add(h);return h;
   }catch(error){try{original.dispose(h);}catch(cleanup){throw new AggregateError([error,cleanup],'bundle validation and acquired-owner cleanup failed',{cause:error});}throw error;}
  },
  review(h:GenericCompositionHandle,label:string){current(h);return original.review(h,label);},
  accept(h:GenericCompositionHandle,r:Parameters<typeof original.accept>[1],file:string){current(h);return original.accept(h,r,file);},
  inspect(h:GenericCompositionHandle){current(h);return original.inspect(h);},
  assertCurrent:current,
  async openWorkflow(h:GenericCompositionHandle,options:import('./workflow-driver.js').GenericWorkflowDriverOptions){
   const {openGenericWorkflowDriver}=await import('./workflow-driver.js');
   return openGenericWorkflowDriver(owner,h,options);
  },
  async openRuntime(h:GenericCompositionHandle,options:GenericRuntimeOptions):Promise<GenericApplicationRuntime|GenericTransactionApplicationRuntime>{requireGenericCompositionRuntime(owner,h);const {createGenericApplicationRuntime}=await import('./invocation-owner.js');return createGenericApplicationRuntime(owner,h,options);},
  bindHttp(h:GenericCompositionHandle,runtime:GenericTransactionApplicationRuntime,routeId:string){
   if(!httpBundle)fail('UnsupportedCapability',at,'generated application has no checked HTTP profile');
   requireGenericCompositionRuntime(owner,h);
   return createGenericHttpHandler(owner,h,runtime,routeId);
  },
  dispose(h:GenericCompositionHandle){current(h);original.dispose(h);},
 });
 const commandScope=new AsyncLocalStorage<GenericCompositionHandle>();
 capabilityParents.set(owner,h=>{current(h);const bound=requireGenericCapabilityGenerationBinding(original,h);return {generation:()=>{current(h);return bound.generation();},assertCurrent:()=>{current(h);bound.assertCurrent();}};});
 compositionRegistry.set(owner,h=>{current(h);const binding=requireGenericCompositionRuntime(original,h);const full=()=>withCorePhysicalIdentityPhase(()=>{current(h);binding.assertCurrent();});return Object.freeze({...binding,assertCurrent:()=>{if(commandScope.getStore()!==h)full();},assertEffectCurrent:full,withCommandCurrentnessScope:<T>(work:()=>Promise<T>)=>{full();return commandScope.run(h,work);}});});
 workflowRegistry.set(owner,h=>{current(h);if(!workflowBundle)fail('UnsupportedCapability',at,'generated bundle has no authored Workflow');const binding=requireGenericWorkflowRuntime(original,h);return Object.freeze({...binding,assertCurrent:()=>withCorePhysicalIdentityPhase(()=>{current(h);binding.assertCurrent();})});});
 return owner;
}


export function createGenericBundledApplicationOwner(moduleUrl:string,proposal:unknown){
 const bundle=captureJson(proposal) as any;
 const hasCapabilityOverlay=!!bundle&&typeof bundle==='object'&&Object.hasOwn(bundle,'capabilities');
 if(bundle?.schema_version==='craft.generic-transaction-bundle/v1-candidate')return createGenericTransactionBundledApplicationOwner(moduleUrl,bundle);
 if(!bundle||typeof bundle!=='object'||Array.isArray(bundle)||Object.keys(bundle).sort().join(',')!==(hasCapabilityOverlay?'capabilities,entry,executable_semantics_sha256,files,recipe_sha256,schema_version':'entry,executable_semantics_sha256,files,recipe_sha256,schema_version')||bundle.schema_version!=='craft.generic-keyed-bundle/v1-candidate'||typeof bundle.entry!=='string'||!Array.isArray(bundle.files)||bundle.files.length<6||bundle.files.length>128||bundle.recipe_sha256!==dataDigest(KEYED_PROFILE_RECIPE)||!/^([a-f0-9]{64})$/.test(bundle.executable_semantics_sha256))fail('InvalidContract',at,'closed generated keyed bundle required');
 const url=new URL(moduleUrl);if(url.protocol!=='file:')fail('InvalidContract',at,'physical generated module required');const directory=path.dirname(fileURLToPath(url)),seen=new Set<string>();
 for(const f of bundle.files){if(!f||typeof f!=='object'||Object.keys(f).sort().join(',')!=='bytes,path,sha256'||typeof f.path!=='string'||path.posix.normalize(f.path)!==f.path||path.isAbsolute(f.path)||f.path.split('/').some((p:string)=>!p||p==='..'||p==='.')||f.path.includes('\\')||seen.has(f.path)||!/^[a-f0-9]{64}$/.test(f.sha256)||!Number.isSafeInteger(f.bytes)||f.bytes<0||f.bytes>1048576)fail('InvalidContract',at,'bounded unique generated file pins required');seen.add(f.path);}
 for(const f of ['model/application.alch','model/source/business.alch','model/contracts/bounds.json','model/contracts/selected-profile.json','model/generated/auth-context.alch','model/generated/auth-context.json'])if(!seen.has(f))fail('InvalidContract',at,'complete generated source closure required');
 const capabilityFiles=hasCapabilityOverlay?checkCapabilityOverlay(bundle.capabilities,new Map(bundle.files.map((f:any)=>[f.path,f]))):new Set<string>();
 const envelope=[captureKeyedPackage(),readCorePhysicalFile(fileURLToPath(url)),readCorePhysicalFile(path.join(directory,'manifest.json')),...bundle.files.map((f:any)=>readCorePhysicalFile(path.join(directory,f.path)))];
 for(const f of bundle.files){const physical=envelope.find(row=>row.file.path===path.join(directory,f.path));if(!physical||physical.file.sha256!==f.sha256||physical.file.bytes!==f.bytes)fail('StaleOwner',at,'generated source/artifact changed');}
 const physicalPin=pinCorePhysicalCaptures(envelope);
 const assertBundle=()=>{pin.assertCurrent();keyedPin.assertCurrent();physicalPin.assertCurrent();};
 assertBundle();const original=createGenericCompositionOwner();
 const known=new WeakSet<object>();
 const current=(h:GenericCompositionHandle)=>{assertBundle();if(!h||typeof h!=='object'||!known.has(h))fail('ForeignOwner',at,'original generated application handle required');original.assertCurrent(h);};
 const owner=Object.freeze({
  async prepare(...args:unknown[]){if(args.length)fail('InvalidContract',at,'generated preparation takes no caller paths');assertBundle();const authored=mkdtempSync(path.join(tmpdir(),'craft-bundled-authored-'));mkdirSync(path.join(authored,'contracts'));for(const [from,to]of [['model/source/business.alch','business.alch'],['model/contracts/bounds.json','contracts/bounds.json'],['model/contracts/selected-profile.json','profile.json']] as const)writeCoreExclusiveFile(path.join(authored,to),readCorePhysicalFile(path.join(directory,from)).text);if(hasCapabilityOverlay)for(const f of bundle.capabilities.assets){const dest=path.join(authored,f.path);mkdirSync(path.dirname(dest),{recursive:true});writeCoreExclusiveFile(dest,readCorePhysicalFile(path.join(directory,'model/'+f.path)).text);}
assertBundle();const h=await original.prepare({sourcePath:path.join(authored,'business.alch'),profilePath:path.join(authored,'profile.json'),...(hasCapabilityOverlay?{capabilitySelectionPath:path.join(authored,bundle.capabilities.selection_path)}:{})});const inspection=original.inspect(h);if(hasCapabilityOverlay&&capabilityGeneration(h).plan_sha256!==bundle.capabilities.plan_sha256)fail('InvalidContract',at,'regenerated capability wiring differs from original keyed bundle');if(inspection.logical.executable_semantics_sha256!==bundle.executable_semantics_sha256||inspection.profile.recipe_sha256!==bundle.recipe_sha256)fail('InvalidContract',at,'fresh generated source semantics differ');assertBundle();known.add(h);return h;},
  review(h:GenericCompositionHandle,label:string){current(h);return original.review(h,label);},
  accept(h:GenericCompositionHandle,r:Parameters<typeof original.accept>[1],file:string){current(h);return original.accept(h,r,file);},
  inspect(h:GenericCompositionHandle){current(h);return original.inspect(h);},assertCurrent:current,
  async openWorkflow(h:GenericCompositionHandle,_options:import('./workflow-driver.js').GenericWorkflowDriverOptions):Promise<never>{
   current(h);return fail('UnsupportedCapability',at,'keyed application has no checked Workflow');
  },
  async openRuntime(h:GenericCompositionHandle,options:GenericRuntimeOptions):Promise<GenericApplicationRuntime|GenericTransactionApplicationRuntime>{requireGenericCompositionRuntime(owner,h);const {createGenericApplicationRuntime}=await import('./invocation-owner.js');return createGenericApplicationRuntime(owner,h,options);},
  dispose(h:GenericCompositionHandle){current(h);original.dispose(h);},
 });
 capabilityParents.set(owner,h=>{current(h);const bound=requireGenericCapabilityGenerationBinding(original,h);return {generation:()=>{current(h);return bound.generation();},assertCurrent:()=>{current(h);bound.assertCurrent();}};});
 compositionRegistry.set(owner,h=>{current(h);const binding=requireGenericCompositionRuntime(original,h);return Object.freeze({...binding,assertCurrent:()=>{current(h);binding.assertCurrent();}});});
 return owner;
}
