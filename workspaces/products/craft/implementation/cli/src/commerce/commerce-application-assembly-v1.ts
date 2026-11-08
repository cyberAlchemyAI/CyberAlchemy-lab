/** Source-selected Commerce application composition for local service effects.
 * This joins original source, technical profile, computation and service storage;
 * entry/command custody and the complete native package remain separate.
 * Open Questions: docs/COMMERCE-PROFILE-FAMILY-V5.md#open-questions. */
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {existsSync,lstatSync,mkdirSync,realpathSync} from 'node:fs';
import {pinCoreImplementation} from './commerce-core-physical.js';
import {coreFreeze,coreSourceFail as fail} from './commerce-core-syntax.js';
import {createCoreCommerceSourceOwner,parseCoreCommerceJson} from './commerce-core-source-owner.js';
import {createCoreCommerceSemanticOwner} from './commerce-core-semantic-owner.js';
import {createCoreCommerceStageSourceOwner} from './commerce-core-stage-owner.js';
import {createCoreCommerceComputationContract} from './commerce-core-pure-contract.js';
import {createCommerceComputationDomainOwner} from './commerce-computation-domain.js';
import {createCommerceLocalPlanOwnerV1,type CommerceLocalReadHandleV1} from './commerce-local-plan-owner-v1.js';
import {createCommerceTechnicalModelOwnerV5} from '../profile-engine/technical-model-v5.js';
import {createCommerceFamilyOwnerV5} from '../profile-engine/family-v5.js';
import {createCommerceBindingAssemblyOwnerV1} from './commerce-binding-assembly-v1.js';
import {createCommerceServiceStorageOwnerV1,type CommerceServiceStorageOwnerV1,
 type CommerceEventPublicationAttemptV1,type CommerceEventPublicationResultV1} from './commerce-service-storage-v1.js';
import {createCommerceEntryContextOwnerV1,type CommerceEntryContextOwnerV1} from './commerce-entry-context-v1.js';
import {createCommerceSelectedEntryAuthOwnerV1,type CommerceSelectedEntryAuthOwnerV1} from './commerce-selected-entry-auth-v1.js';
import {createCommerceSourceQueryOutputCodecV1,type CommerceSourceQueryOutputCodecV1} from './commerce-source-query-output-codec-v1.js';
import {createCommerceSourceQueryRuntimeV1,type CommerceSourceQueryRuntimeV1} from './commerce-source-query-runtime-v1.js';
import {createCommerceGeneratedOperationRuntimeV1,type CommerceGeneratedOperationRuntimeV1} from './commerce-generated-operation-runtime-v1.js';
import {createCommerceDemoPaySourceSiteOwnerV1,type CommerceDemoPaySourceSiteOwnerV1} from './commerce-demopay-source-site-v1.js';
import {createCommerceDemoPayDispatchOwnerV1,type CommerceDemoPayDispatchOwnerV1} from './commerce-demopay-dispatch-v1.js';
import type {DemoPayCommerceRawBytePortV1} from './commerce-demopay-wire-v1.js';
import type {CommerceAuthNativeOwnerV1} from './commerce-auth-ready-bridge-v1.js';
import type {CommerceAuthActorV1} from './commerce-entry-context-v1.js';
import type {CommerceOperationInvocationHandle} from './commerce-stages-v1.js';
import {createCoreCommerceSelectedQueryAdapter,type CoreCommerceSelectedQueryAdapter} from '../generic/core-commerce-selected-query-adapter.js';
import {selectCoreCommerceExternalQueries,type CoreCommerceExternalQueryBinding} from '../generic/core-commerce-external-query-selection.js';
import {createCoreCommerceWorkflowIngress,type CoreCommerceWorkflowIngress} from '../generic/core-commerce-workflow-ingress.js';
import {createCoreCommerceOutboxRelay,type CoreCommerceOutboxRelay} from '../generic/core-commerce-outbox-relay.js';
import {createCoreCommerceWorkerClaimExecutor,type CoreCommerceWorkerClaimExecutor} from '../generic/core-commerce-worker-claim-executor.js';
import {createCoreCommerceWorkerSnapshotQuery,type CoreCommerceWorkerSnapshotQuery} from '../generic/core-commerce-worker-snapshot-query.js';
import {createCoreCommerceWorkerContinuation,type CoreCommerceWorkerContinuation} from '../generic/core-commerce-worker-continuation.js';
import {createCoreCommerceWorkerStepRunner,type CoreCommerceWorkerStepRunner} from '../generic/core-commerce-worker-step-runner.js';
import {createCoreCommerceWorkerLocalObservationSelector,type CoreCommerceWorkerLocalObservationSelector}
 from '../generic/core-commerce-worker-local-observation.js';
import {createCoreCommerceWorkerLocalObservationRunner,type CoreCommerceWorkerLocalObservationRunner}
 from '../generic/core-commerce-worker-local-observation-runner.js';
import {createCoreCommerceWorkerCycle,type CoreCommerceWorkerCycle}
 from '../generic/core-commerce-worker-cycle.js';
import {createCoreCommerceWorkflowPass,type CoreCommerceWorkflowPass}
 from '../generic/core-commerce-workflow-pass.js';
import {createCoreCommerceCrossServiceEventRelay,type CoreCommerceCrossServiceEventRelay}
 from '../generic/core-commerce-cross-service-event-relay.js';
import {createCoreCommerceEventIngressAdmission,type CoreCommerceEventIngressAdmission}
 from '../generic/core-commerce-event-ingress-admission.js';
import {createCoreCommerceEventPublication,type CoreCommerceEventPublication}
 from '../generic/core-commerce-event-publication.js';
import {createCoreCommerceEventProducerSource,type CoreCommerceEventProducerSource}
 from '../generic/core-commerce-event-producer-source.js';
import {createCoreCommerceEventProducerProvenance,type CoreCommerceEventProducerProvenance,
 type CoreCommerceEventProducerProof} from '../generic/core-commerce-event-producer-provenance.js';
import type {CoreCommerceEventPublicationCandidate} from '../generic/core-commerce-event-publication.js';
import {createCoreCommerceEventDelivery,type CoreCommerceEventDelivery,type CoreCommerceEventReceiverAcknowledgement}
 from '../generic/core-commerce-event-delivery.js';
import {createCoreCommerceEventAckSelection,type CoreCommerceEventAckSelection}
 from '../generic/core-commerce-event-ack-selection.js';
import {createCoreCommerceEventReceiverCommitOwner,type CoreCommerceEventReceiverCommitOwner}
 from '../generic/core-commerce-event-receiver-commit.js';
import {selectCoreCommerceWorkerActorRequirements,type CoreCommerceWorkerActorRequirement} from '../generic/core-commerce-worker-actor-selection.js';
import {createCommerceWorkflowCoordinationBindingV1,type CommerceWorkflowCoordinationBindingV1} from './commerce-workflow-coordination-binding-v1.js';
import {exportCoreCommerceFormalStructureV1,type CoreCommerceFormalStructureV1} from './commerce-core-formal-structure-v1.js';
import {exportCoreCommercePureUint64SmtV1,type CoreCommercePureUint64SmtV1} from './commerce-core-formal-uint64-v1.js';
import {exportCoreCommerceFormalTemporalV1,type CoreCommerceFormalTemporalV1} from './commerce-core-formal-temporal-v1.js';
import {CoreCommerceFormalArtifactErrorV1,createCoreCommerceFormalArtifactsV1,publishCoreCommerceFormalArtifactsV1,
 type CoreCommerceFormalArtifactsV1,type CoreCommerceFormalLanguageV1} from './commerce-core-formal-artifacts-v1.js';

const ext=path.extname(fileURLToPath(import.meta.url));
const pin=pinCoreImplementation(import.meta.url,['commerce-binding-assembly-v1'+ext,'commerce-service-storage-v1'+ext,'commerce-local-plan-owner-v1'+ext,'commerce-entry-context-v1'+ext,'commerce-selected-entry-auth-v1'+ext,'commerce-source-query-output-codec-v1'+ext,'commerce-source-query-runtime-v1'+ext,'commerce-workflow-snapshot-v1'+ext,'commerce-workflow-resume-v1'+ext,'commerce-workflow-step-identity-v1'+ext,'commerce-identity-call-owner'+ext,'commerce-generated-operation-runtime-v1'+ext,'commerce-demopay-source-site-v1'+ext,'commerce-demopay-dispatch-v1'+ext,'../generic/core-commerce-selected-query-adapter'+ext,'../generic/core-commerce-external-query-selection'+ext,'../generic/core-commerce-workflow-ingress'+ext,'../generic/core-commerce-outbox-relay'+ext,'../generic/core-commerce-cross-service-event-relay'+ext,'../generic/core-commerce-event-ingress-admission'+ext,'../generic/core-commerce-event-publication'+ext,'../generic/core-commerce-event-producer-source'+ext,'../generic/core-commerce-event-producer-provenance'+ext,'../generic/core-commerce-event-ack-selection'+ext,'../generic/core-commerce-event-ack-source'+ext,'../generic/core-commerce-event-receiver-commit'+ext,'../generic/core-commerce-worker-claim-executor'+ext,'../generic/core-commerce-worker-claim-input'+ext,'../generic/core-commerce-worker-snapshot-query'+ext,'../generic/core-commerce-worker-snapshot-input'+ext,'../generic/core-commerce-worker-continuation'+ext,'../generic/core-commerce-worker-step-runner'+ext,'../generic/core-commerce-worker-local-observation'+ext,'../generic/core-commerce-worker-local-observation-runner'+ext,'../generic/core-commerce-worker-cycle'+ext,'../generic/core-commerce-workflow-pass'+ext,'../generic/core-commerce-worker-actor-registry'+ext,'../generic/core-commerce-worker-actor-selection'+ext,'commerce-workflow-coordination-binding-v1'+ext,'commerce-core-formal-structure-v1'+ext,'commerce-core-formal-artifacts-v1'+ext,'commerce-core-formal-uint64-v1'+ext,'commerce-core-formal-temporal-v1'+ext]);
const where={path:'application.alch',start:0,end:0};

export interface CommerceApplicationAssemblyV1 {
 inspect():Readonly<{kind:'original-commerce-application-assembly/v1-candidate';application:string;services:readonly string[];
  source_capture_sha256:string;family_sha256:string;native_basis_qualified:false;bound_application_qualified:false;
  qualification:'original-source-selected-application-and-local-storage;entry-command-and-full-native-binding-pending';authority_effect:'none'}>;
 openServiceStorage(service:string):Promise<CommerceServiceStorageOwnerV1>;
 openRecoveredServiceStorage(service:string,existingDirectory:string):Promise<CommerceServiceStorageOwnerV1>;
 openSelectedEntryAuth(native:CommerceAuthNativeOwnerV1):Promise<Readonly<{auth:CommerceEntryContextOwnerV1;entries:CommerceSelectedEntryAuthOwnerV1}>>;
 inspectExternalQueryActorRequirements():readonly CoreCommerceExternalQueryBinding[];
 inspectWorkerActorRequirements(workflowId:string):readonly CoreCommerceWorkerActorRequirement[];
 bindServiceActor(actor:CommerceAuthActorV1):readonly string[];
 openDemoPayDispatch(port:DemoPayCommerceRawBytePortV1):CommerceDemoPayDispatchOwnerV1;
 openGeneratedOperation(invocation:CommerceOperationInvocationHandle):Promise<CommerceGeneratedOperationRuntimeV1>;
 releaseGeneratedOperation(invocation:CommerceOperationInvocationHandle):void;
 openGeneratedQuery(invocation:CommerceOperationInvocationHandle):Promise<CoreCommerceSelectedQueryAdapter>;
 openWorkflowIngress(workflowId:string):CoreCommerceWorkflowIngress;
 openOutboxRelay(workflowId:string):CoreCommerceOutboxRelay;
 openWorkflowClaimExecutor(workflowId:string):CoreCommerceWorkerClaimExecutor;
 openWorkflowSnapshotQuery(workflowId:string):CoreCommerceWorkerSnapshotQuery;
 openWorkflowContinuation(workflowId:string):CoreCommerceWorkerContinuation;
 openWorkflowStepRunner(workflowId:string):CoreCommerceWorkerStepRunner;
 openWorkflowLocalObservation(workflowId:string):CoreCommerceWorkerLocalObservationSelector;
 openWorkflowLocalObservationRunner(workflowId:string):ReturnType<typeof createCoreCommerceWorkerLocalObservationRunner>;
 openWorkflowCycle(workflowId:string):CoreCommerceWorkerCycle;
 openWorkflowPass(workflowId:string):CoreCommerceWorkflowPass;
 openCrossServiceEvent(entryId:string):Readonly<{relay:CoreCommerceCrossServiceEventRelay;
  admission:CoreCommerceEventIngressAdmission;publication:CoreCommerceEventPublication;
  producerSource:CoreCommerceEventProducerSource;
  provenance:CoreCommerceEventProducerProvenance;
  acknowledgement:CoreCommerceEventAckSelection;receiverCommit:CoreCommerceEventReceiverCommitOwner;
  openDelivery():CoreCommerceEventDelivery;
  publish(input:Readonly<{candidate:CoreCommerceEventPublicationCandidate;
   proof:CoreCommerceEventProducerProof;delivery:CoreCommerceEventDelivery;
   acknowledgement:CoreCommerceEventReceiverAcknowledgement}>):Promise<CommerceEventPublicationResultV1>;
  reconcile(attempt:CommerceEventPublicationAttemptV1):CommerceEventPublicationResultV1;
  reconcilePublished(occurrenceId:string):Promise<CommerceEventPublicationResultV1>}>;
 exportFormalStructure(workflowId:string,language?:CoreCommerceFormalLanguageV1):CoreCommerceFormalStructureV1;
 exportFormalArtifacts(workflowId:string,language?:CoreCommerceFormalLanguageV1):CoreCommerceFormalArtifactsV1;
 publishFormalStructure(workflowId:string,targetRoot:string,language?:CoreCommerceFormalLanguageV1):CoreCommerceFormalArtifactsV1;
 exportPureUint64Formal(selector:string):CoreCommercePureUint64SmtV1;
 exportFormalTemporal(workflowId:string):CoreCommerceFormalTemporalV1;
 assertCurrent():void;
 close():void;
}
const owners=new WeakSet<object>();
export function assertCommerceApplicationAssemblyV1(owner:CommerceApplicationAssemblyV1):void {
 if(!owner||typeof owner!=='object'||!owners.has(owner))fail('ForeignOwner',where,'original application assembly required');
 owner.assertCurrent();
}

/** The source and profile are read from one captured project. The caller can
 * select only the project root and a fresh output root, never a native hook,
 * technical family DTO, service topology, or computation contract. */
export async function createCommerceApplicationAssemblyV1(sourceRoot:string,outputRoot:string):Promise<CommerceApplicationAssemblyV1> {
 pin.assertCurrent();
 for(const value of [sourceRoot,outputRoot])if(typeof value!=='string'||!path.isAbsolute(value)||path.normalize(value)!==value)
  fail('InvalidContract',where,'normalized absolute source and fresh output roots required');
 const withinSource=path.relative(sourceRoot,outputRoot);
 if(withinSource===''||withinSource!=='..'&&!withinSource.startsWith('..'+path.sep)&&!path.isAbsolute(withinSource))
  fail('InvalidContract',where,'generated output must be outside the captured source root');
 if(existsSync(outputRoot))fail('InvalidContract',where,'fresh application output root required');
 const sources=createCoreCommerceSourceOwner();
 let capture:ReturnType<typeof sources.prepare>|undefined;
 let semantics:ReturnType<typeof createCoreCommerceSemanticOwner>|undefined;
 let semantic:ReturnType<NonNullable<typeof semantics>['check']>|undefined;
 let stage:ReturnType<typeof createCoreCommerceStageSourceOwner>|undefined;
 let source:Awaited<ReturnType<NonNullable<typeof stage>['prepare']>>|undefined;
 let domain:ReturnType<typeof createCommerceComputationDomainOwner>|undefined;
 let baseline:ReturnType<NonNullable<typeof domain>['check']>|undefined;
 let plans:ReturnType<typeof createCommerceLocalPlanOwnerV1>|undefined;
 let models:ReturnType<typeof createCommerceTechnicalModelOwnerV5>|undefined;
 let model:Awaited<ReturnType<NonNullable<typeof models>['checkTechnicalSource']>>|undefined;
 let families:ReturnType<typeof createCommerceFamilyOwnerV5>|undefined;
 let assemblyOwner:ReturnType<typeof createCommerceBindingAssemblyOwnerV1>|undefined;
 const stores=new Map<string,CommerceServiceStorageOwnerV1>();
 const operationRuntimes=new Set<CommerceGeneratedOperationRuntimeV1>();
 const openedOperations=new WeakMap<object,CommerceGeneratedOperationRuntimeV1>();
 const operationResources=new WeakMap<object,readonly {read:CommerceLocalReadHandleV1;codec:CommerceSourceQueryOutputCodecV1;query:CommerceSourceQueryRuntimeV1}[]>();
 const queryAdapters=new Set<CoreCommerceSelectedQueryAdapter>();
 const openedQueries=new WeakMap<object,CoreCommerceSelectedQueryAdapter>();
 const externalQueries=new Set<{read:CommerceLocalReadHandleV1;codec:CommerceSourceQueryOutputCodecV1;query:CommerceSourceQueryRuntimeV1}>();
 const workerSnapshotQueries=new Set<CoreCommerceWorkerSnapshotQuery>();
 const workerContinuations=new Set<CoreCommerceWorkerContinuation>();
 const workerStepRunners=new Set<CoreCommerceWorkerStepRunner>();
 const workerLocalObservations=new Set<CoreCommerceWorkerLocalObservationSelector>();
 const workerLocalObservationRunners=new Set<CoreCommerceWorkerLocalObservationRunner>();
 const workerCycles=new Set<CoreCommerceWorkerCycle>();
 const workflowPasses=new Set<CoreCommerceWorkflowPass>();
 const crossServiceEventRelays=new Set<CoreCommerceCrossServiceEventRelay>();
 const eventIngressAdmissions=new Set<CoreCommerceEventIngressAdmission>();
 const eventPublications=new Set<CoreCommerceEventPublication>();
 const eventProducerSources=new Set<CoreCommerceEventProducerSource>();
 const eventProvenances=new Set<CoreCommerceEventProducerProvenance>();
 const eventAcknowledgements=new Set<CoreCommerceEventAckSelection>();
 const eventReceiverCommits=new Set<CoreCommerceEventReceiverCommitOwner>();
 const eventDeliveries=new Set<CoreCommerceEventDelivery>();
 const eventRuntimeBindings=new Map<string,Readonly<{relay:CoreCommerceCrossServiceEventRelay;
  selection:CoreCommerceEventAckSelection;receiverCommit:CoreCommerceEventReceiverCommitOwner}>>();
 const workflowBindings=new Map<string,CommerceWorkflowCoordinationBindingV1>();
 const registeredServiceActors=new Map<string,CommerceAuthActorV1>();
 let operationRuntimeNumber=0;
 let workflowContinuationNumber=0;
 let entryContext:CommerceEntryContextOwnerV1|undefined;
 let selectedEntries:CommerceSelectedEntryAuthOwnerV1|undefined;
 let demoPaySites:CommerceDemoPaySourceSiteOwnerV1|undefined;
 let demoPayDispatch:CommerceDemoPayDispatchOwnerV1|undefined;
 let handedOff=false,closed=false;
 const cleanup=()=>{
  if(closed)return;closed=true;
  for(const runtime of operationRuntimes)try{runtime.dispose();}catch{}
  for(const query of queryAdapters)try{query.dispose();}catch{}
  for(const pass of workflowPasses)try{pass.close();}catch{}
  for(const delivery of eventDeliveries)try{delivery.close();}catch{}
  for(const receiverCommit of eventReceiverCommits)try{receiverCommit.close();}catch{}
  for(const acknowledgement of eventAcknowledgements)try{acknowledgement.close();}catch{}
  for(const provenance of eventProvenances)try{provenance.close();}catch{}
  for(const producerSource of eventProducerSources)try{producerSource.close();}catch{}
  for(const publication of eventPublications)try{publication.close();}catch{}
  for(const admission of eventIngressAdmissions)try{admission.close();}catch{}
  for(const relay of crossServiceEventRelays)try{relay.close();}catch{}
  for(const cycle of workerCycles)try{cycle.close();}catch{}
  for(const runner of workerLocalObservationRunners)try{runner.close();}catch{}
  for(const query of workerSnapshotQueries)try{query.close();}catch{}
  for(const continuation of workerContinuations)try{continuation.close();}catch{}
  for(const runner of workerStepRunners)try{runner.close();}catch{}
  for(const selector of workerLocalObservations)try{selector.close();}catch{}
  for(const resource of externalQueries){
   try{resource.query.dispose();}catch{}
   try{resource.codec.dispose();}catch{}
   try{plans?.disposeRead(resource.read);}catch{}
  }
  try{demoPayDispatch?.dispose();}catch{}
  try{demoPaySites?.dispose();}catch{}
  try{selectedEntries?.dispose();}catch{}
  try{entryContext?.dispose();}catch{}
  for(const store of stores.values())try{store.close();}catch{}
  try{assemblyOwner?.dispose();}catch{}
  try{plans?.dispose();}catch{}
  if(domain&&baseline)try{domain.dispose(baseline);}catch{}
  if(stage&&source)try{stage.dispose(source);}catch{}
  if(models&&model)try{models.dispose(model);}catch{}
  if(semantics&&semantic)try{semantics.dispose(semantic);}catch{}
  if(capture)try{sources.dispose(capture);}catch{}
 };
 try{
  capture=sources.prepare(sourceRoot,'application.alch');
  semantics=createCoreCommerceSemanticOwner(sources);semantic=semantics.check(capture);
  stage=createCoreCommerceStageSourceOwner(sources,semantics);source=await stage.prepare(sourceRoot,'application.alch');
  const captured=sources.inspect(capture),staged=stage.inspect(source);
  if(captured.capture_sha256!==staged.source_sha256)fail('ForeignOwner',where,'original stage must retain the same complete source capture');
  const textPaths=new Set(captured.reconstruction.modules.map(m=>m.path));
  const texts=captured.files.filter(f=>textPaths.has(f.path));
  const calculation=stage.moduleContracts(source).flatMap(m=>m.declarations).filter(d=>d.selector.role==='Calculation')
   .map(d=>d.selector.module+'.'+d.selector.name).sort()[0];
  if(!calculation)fail('MissingMapping',where,'selected application requires one actual pure Calculation source');
  const boundsFile=captured.files.find(f=>f.path==='contracts/compute-bounds.json');
  if(!boundsFile)fail('MissingMapping',where,'original computation bounds asset required');
  const bounds=parseCoreCommerceJson(boundsFile.text,boundsFile.path) as {computation?:{limits?:Parameters<typeof createCoreCommerceComputationContract>[2]}};
  if(!bounds.computation?.limits)fail('MissingMapping',where,'original computation limits required');
  domain=createCommerceComputationDomainOwner(stage,source);
  baseline=domain.check(createCoreCommerceComputationContract(texts,calculation,bounds.computation.limits));
  plans=createCommerceLocalPlanOwnerV1(sources,capture,semantics,semantic,stage,source,domain,baseline);
  models=createCommerceTechnicalModelOwnerV5();model=await models.checkTechnicalSource(sourceRoot,'profiles/implementation.alch');
  families=createCommerceFamilyOwnerV5(models);
  assemblyOwner=createCommerceBindingAssemblyOwnerV1(sources,capture,semantics,semantic,models,model,families);
  const assembly=assemblyOwner.assembly(),selected=assemblyOwner.inspect(assembly).selection;
  const sourceEntries=stage.moduleContracts(source).flatMap(module=>module.entries);
  const selectedServiceIds=selected.services.map(service=>service.id);
  const current=()=>{
   if(closed)fail('DisposedOwner',where,'application assembly closed');pin.assertCurrent();
   // The plan owner checks both captured source/semantic identity and the
   // separately staged domain handle. Repeating those four parent checks here
   // makes every nested worker action traverse the same physical files again.
   plans!.assertCurrent();models!.assertCurrent(model!);assemblyOwner!.assertCurrent(assembly);
   entryContext?.assertCurrent();selectedEntries?.assertCurrent();
   demoPayDispatch?.assertCurrent();
   for(const store of stores.values())store.assertCurrent();
  };
  const externalForOperation=(operation:string):readonly CoreCommerceExternalQueryBinding[]=>{
   const handle=plans!.bindOperation(operation);
   try{return selectCoreCommerceExternalQueries(plans!.inspectOperation(handle).plan,sourceEntries,selectedServiceIds);}
   finally{plans!.disposeOperation(handle);}
  };
  const externalActorRequirements=():readonly CoreCommerceExternalQueryBinding[]=>{
   current();const operations=new Set(sourceEntries.filter(entry=>entry.invokes.role==='Operation'&&
    selectedServiceIds.includes(entry.service)).map(entry=>entry.invokes.module+'.'+entry.invokes.name));
   const found=new Map<string,CoreCommerceExternalQueryBinding>();
   for(const operation of [...operations].sort())for(const binding of externalForOperation(operation)){
    const prior=found.get(binding.entry);
    if(prior&&(prior.query!==binding.query||prior.caller_service!==binding.caller_service||
      prior.target_service!==binding.target_service))fail('MissingMapping',where,'inconsistent source service Query Entry');
    found.set(binding.entry,binding);
   }
   return Object.freeze([...found.values()].sort((a,b)=>a.entry.localeCompare(b.entry)));
  };
  const inspection=coreFreeze({kind:'original-commerce-application-assembly/v1-candidate' as const,
   application:selected.application,services:selected.services.map(s=>s.id),source_capture_sha256:selected.source_capture_sha256,
   family_sha256:selected.family_sha256,native_basis_qualified:false as const,bound_application_qualified:false as const,
   qualification:'original-source-selected-application-and-local-storage;entry-command-and-full-native-binding-pending' as const,
   authority_effect:'none' as const});
  const workflowBinding=(workflowId:string)=>{
   current();
   let binding=workflowBindings.get(workflowId);
   if(!binding){binding=createCommerceWorkflowCoordinationBindingV1(sources,capture!,stage!,source!,workflowId);
    workflowBindings.set(workflowId,binding);}
   binding.assertCurrent();
   return binding;
  };
  mkdirSync(outputRoot,{mode:0o700});
  const owner:CommerceApplicationAssemblyV1=Object.freeze({
   inspect(){current();return inspection;},
   async openServiceStorage(service:string){
    current();if(!selected.services.some(s=>s.id===service))fail('ForeignOwner',where,'service absent from original application selection');
    if(stores.has(service))fail('InvalidContract',where,'service storage already opened by this assembly');
    if(!/^[A-Za-z][A-Za-z0-9_-]*$/.test(service))fail('InvalidContract',where,'selected service must have a safe output directory name');
    const store=await createCommerceServiceStorageOwnerV1(sources,capture!,semantics!,semantic!,stage!,source!,domain!,baseline!,plans!,families!,assemblyOwner!,assembly,service,path.join(outputRoot,service));
    stores.set(service,store);current();return store;
   },
   async openRecoveredServiceStorage(service:string,existingDirectory:string){
    current();if(!selected.services.some(s=>s.id===service))
     fail('ForeignOwner',where,'recovered service absent from original application selection');
    if(stores.has(service))fail('InvalidContract',where,'service storage already opened by this assembly');
    if(!/^[A-Za-z][A-Za-z0-9_-]*$/.test(service))
     fail('InvalidContract',where,'selected service must have a safe recovered directory name');
    if(typeof existingDirectory!=='string'||!path.isAbsolute(existingDirectory)||
      path.normalize(existingDirectory)!==existingDirectory||!existsSync(existingDirectory)||
      !lstatSync(existingDirectory).isDirectory()||realpathSync(existingDirectory)!==existingDirectory)
     fail('InvalidContract',where,'exact existing recovered service directory required');
    const withinSource=path.relative(sourceRoot,existingDirectory);
    if(withinSource===''||withinSource!=='..'&&!withinSource.startsWith('..'+path.sep)&&
      !path.isAbsolute(withinSource))
     fail('InvalidContract',where,'recovered service directory must be outside original source');
    const store=await createCommerceServiceStorageOwnerV1(sources,capture!,semantics!,semantic!,
     stage!,source!,domain!,baseline!,plans!,families!,assemblyOwner!,assembly,
     service,existingDirectory,'reopen');
    stores.set(service,store);current();return store;
   },
   async openSelectedEntryAuth(native:CommerceAuthNativeOwnerV1){
    current();if(entryContext||selectedEntries)fail('InvalidContract',where,'selected Entry/Auth already opened by this assembly');
    const auth=await createCommerceEntryContextOwnerV1(sources,capture!,stage!,source!,domain!,baseline!,native,path.join(outputRoot,'entry-auth'));
    try{
     const entries=await createCommerceSelectedEntryAuthOwnerV1(sources,capture!,semantics!,semantic!,stage!,source!,domain!,baseline!,plans!,assemblyOwner!,assembly,auth,path.join(outputRoot,'entry-invocations'));
     entryContext=auth;selectedEntries=entries;current();return Object.freeze({auth,entries});
    }catch(error){auth.dispose();throw error;}
   },
   inspectExternalQueryActorRequirements(){return externalActorRequirements();},
   inspectWorkerActorRequirements(workflowId:string){
    current();
    const binding=workflowBinding(workflowId);
    const rows=selectCoreCommerceWorkerActorRequirements(binding.inspect().workflow,semantics!.inspect(semantic!).entries);
    current();return rows;
   },
   bindServiceActor(actor:CommerceAuthActorV1){
    current();if(!entryContext||!selectedEntries)fail('InvalidContract',where,'selected Entry/Auth required for native service actor');
    entryContext.assertActor(actor);
    const assignment=entryContext.inspectActor(actor);
    if(assignment.principal_kind!=='service'||!assignment.service_id)
     fail('ForeignOwner',where,'native service actor assignment required');
    const matches=externalActorRequirements().filter(binding=>binding.caller_service===assignment.service_id&&
     binding.scope===assignment.scope);
    if(!matches.length)fail('ForeignOwner',where,'native actor matches no checked external Query Entry');
    for(const binding of matches){const previous=registeredServiceActors.get(binding.entry);
     if(previous&&previous!==actor)fail('ForeignOwner',where,'checked service Query Entry already has a native actor');}
    for(const binding of matches){selectedEntries.registerServiceActor(binding.entry,actor);
     registeredServiceActors.set(binding.entry,actor);}
    return Object.freeze(matches.map(binding=>binding.entry));
   },
   openDemoPayDispatch(port:DemoPayCommerceRawBytePortV1){
    current();if(demoPayDispatch||demoPaySites)fail('InvalidContract',where,'DemoPay dispatch already opened by this assembly');
    const storage=stores.get('payments');
    if(!storage)fail('InvalidContract',where,'selected payments storage must be open before DemoPay dispatch');
    const sites=createCommerceDemoPaySourceSiteOwnerV1(sources,capture!,semantics!,semantic!,stage!,source!,plans!,assemblyOwner!,assembly);
    let dispatch:CommerceDemoPayDispatchOwnerV1|undefined;
    try{
     const select=(operation:string,method:'Capture'|'InspectCapture')=>{
      const parent=plans!.bindOperation(operation);
      const matches=sites.paths(parent).map(sourcePath=>sites.bind(parent,sourcePath)).filter(site=>sites.inspect(site).method===method);
      if(matches.length!==1)fail('MissingMapping',where,'one original DemoPay '+method+' source site required');
      return matches[0]!;
     };
     const captureSite=select('Payments.DispatchOriginalCapture','Capture');
     const inspectSite=select('Payments.ReconcilePayment','InspectCapture');
     dispatch=createCommerceDemoPayDispatchOwnerV1(sources,capture!,plans!,sites,captureSite,inspectSite,storage,port);
     dispatch.assertCurrent();current();demoPaySites=sites;demoPayDispatch=dispatch;return dispatch;
    }catch(error){dispatch?.dispose();sites.dispose();throw error;}
   },
   async openGeneratedOperation(invocation:CommerceOperationInvocationHandle){
    current();if(!selectedEntries)fail('InvalidContract',where,'selected Entry/Auth must be open');
    const view=selectedEntries.inspectInvocation(invocation);
    if(view.depth!==0||view.parent_call_path!==null)fail('ForeignOwner',where,'selected root invocation required');
    const storage=stores.get(view.service);
    if(!storage)fail('InvalidContract',where,'selected service storage must be open');
    if(openedOperations.has(invocation))fail('InvalidContract',where,'generated Operation already opened for invocation');
    const eventEntry=sourceEntries.find(entry=>entry.id===view.entry&&entry.interaction==='event');
    const eventAck=eventEntry?eventRuntimeBindings.get(view.entry):undefined;
    if(eventEntry&&!eventAck)fail('MissingMapping',where,'original cross-service Event delivery must be open');
    const plan=plans!.inspectOperation(selectedEntries.operation(invocation)).plan;
    const dependencies=selectCoreCommerceExternalQueries(plan,sourceEntries,selectedServiceIds);
    const opened:{read:CommerceLocalReadHandleV1;codec:CommerceSourceQueryOutputCodecV1;query:CommerceSourceQueryRuntimeV1}[]=[];
    try{
     for(const dependency of dependencies){
      const targetStore=stores.get(dependency.target_service);
      if(!targetStore)fail('InvalidContract',where,'checked external Query service storage must be open');
      const read=plans!.bindRead(dependency.query);
      let codec:CommerceSourceQueryOutputCodecV1;
      try{codec=await createCommerceSourceQueryOutputCodecV1(stage!,source!,domain!,baseline!,plans!,read);}
      catch(error){plans!.disposeRead(read);throw error;}
      let query:CommerceSourceQueryRuntimeV1;
      try{query=createCommerceSourceQueryRuntimeV1(stage!,source!,plans!,read,domain!,baseline!,targetStore,codec);}
      catch(error){codec.dispose();plans!.disposeRead(read);throw error;}
      opened.push({read,codec,query});
     }
     const options={...view.service==='payments'&&demoPayDispatch?{demoPayDispatch}:{},
      ...opened.length?{externalQueries:opened.map(resource=>resource.query)}:{},
      ...eventAck?{eventAck}:{}};
     const runtime=await createCommerceGeneratedOperationRuntimeV1(sources,capture!,stage!,source!,domain!,baseline!,plans!,selectedEntries,storage,invocation,path.join(outputRoot,'operation-'+(++operationRuntimeNumber)),
      Object.keys(options).length?options:undefined);
     for(const resource of opened)externalQueries.add(resource);
     operationRuntimes.add(runtime);openedOperations.set(invocation,runtime);
     operationResources.set(invocation,opened);current();return runtime;
    }catch(error){
     for(const resource of opened){try{resource.query.dispose();}catch{}try{resource.codec.dispose();}catch{}
      try{plans!.disposeRead(resource.read);}catch{}}
     throw error;
    }
   },
   releaseGeneratedOperation(invocation:CommerceOperationInvocationHandle){
    current();const runtime=openedOperations.get(invocation);
    if(!runtime)fail('ForeignOwner',where,'opened selected generated Operation required');
    openedOperations.delete(invocation);operationRuntimes.delete(runtime);
    const resources=operationResources.get(invocation)??[];
    operationResources.delete(invocation);
    try{runtime.dispose();}
    finally{for(const resource of resources){
     externalQueries.delete(resource);
     try{resource.query.dispose();}finally{try{resource.codec.dispose();}finally{plans!.disposeRead(resource.read);}}
    }}
   },
   async openGeneratedQuery(invocation:CommerceOperationInvocationHandle){
    current();if(!selectedEntries)fail('InvalidContract',where,'selected Entry/Auth must be open');
    const view=selectedEntries.inspectInvocation(invocation);
    if(view.depth!==0||view.parent_call_path!==null||view.role!=='Query')
     fail('ForeignOwner',where,'selected root Query invocation required');
    const storage=stores.get(view.service);
    if(!storage)fail('InvalidContract',where,'selected service storage must be open');
    if(openedQueries.has(invocation))fail('InvalidContract',where,'generated Query already opened for invocation');
    const adapter=await createCoreCommerceSelectedQueryAdapter({stage:stage!,source:source!,domain:domain!,baseline:baseline!,
     plans:plans!,selected:selectedEntries,storage,invocation});
    queryAdapters.add(adapter);openedQueries.set(invocation,adapter);current();return adapter;
   },
   openWorkflowIngress(workflowId:string){
    current();
    const binding=workflowBinding(workflowId);
    const store=stores.get(binding.inspect().owner_service);
    if(!store)fail('MissingMapping',where,'selected Workflow producer service storage must be open');
    const ingress=createCoreCommerceWorkflowIngress(binding,store);
    current();return ingress;
   },
   openOutboxRelay(workflowId:string){
    current();return createCoreCommerceOutboxRelay(owner.openWorkflowIngress(workflowId));
   },
   openWorkflowClaimExecutor(workflowId:string){
    current();if(!entryContext||!selectedEntries)
     fail('InvalidContract',where,'selected Entry/Auth required for generated Workflow claim');
    const binding=workflowBinding(workflowId);
    const store=stores.get(binding.inspect().owner_service);
    if(!store)fail('MissingMapping',where,'selected Workflow producer storage must be open');
    const executor=createCoreCommerceWorkerClaimExecutor(owner,binding,store,entryContext,selectedEntries);
    current();return executor;
   },
   openWorkflowSnapshotQuery(workflowId:string){
    current();if(!entryContext||!selectedEntries)
     fail('InvalidContract',where,'selected Entry/Auth required for generated Workflow snapshot');
    const binding=workflowBinding(workflowId);
    const store=stores.get(binding.inspect().owner_service);
    if(!store)fail('MissingMapping',where,'selected Workflow producer storage must be open');
    const query=createCoreCommerceWorkerSnapshotQuery({assembly:owner,binding,storage:store,
     auth:entryContext,selected:selectedEntries,stage:stage!,source:source!,domain:domain!,baseline:baseline!,plans:plans!});
    workerSnapshotQueries.add(query);current();return query;
   },
   openWorkflowContinuation(workflowId:string){
    current();const binding=workflowBinding(workflowId),store=stores.get(binding.inspect().owner_service);
    if(!store)fail('MissingMapping',where,'selected Workflow producer storage must be open');
    const continuation=createCoreCommerceWorkerContinuation({assembly:owner,binding,storage:store,
     sources,capture:capture!,semantics:semantics!,semantic:semantic!,stage:stage!,source:source!,
     domain:domain!,baseline:baseline!,
     directoryRoot:path.join(outputRoot,'workflow-continuation-'+(++workflowContinuationNumber))});
    workerContinuations.add(continuation);current();return continuation;
   },
   openWorkflowStepRunner(workflowId:string){
    current();if(!entryContext||!selectedEntries)
     fail('InvalidContract',where,'selected Entry/Auth required for generated Workflow step');
    const binding=workflowBinding(workflowId),producerStorage=stores.get(binding.inspect().owner_service);
    if(!producerStorage)fail('MissingMapping',where,'selected Workflow producer storage must be open');
    const runner=createCoreCommerceWorkerStepRunner({assembly:owner,binding,producerStorage,
     serviceStores:stores,auth:entryContext,selected:selectedEntries,
     sources,capture:capture!,semantics:semantics!,semantic:semantic!,stage:stage!,source:source!,
      domain:domain!,baseline:baseline!,plans:plans!,
      ...(demoPayDispatch?{demoPayDispatch}:{}),
     directoryRoot:path.join(outputRoot,'workflow-step-runner-'+(++workflowContinuationNumber))});
    workerStepRunners.add(runner);current();return runner;
   },
   openWorkflowLocalObservation(workflowId:string){
    current();const binding=workflowBinding(workflowId),storage=stores.get(binding.inspect().owner_service);
    if(!storage)fail('MissingMapping',where,'selected Workflow producer storage must be open');
    const selector=createCoreCommerceWorkerLocalObservationSelector({assembly:owner,binding,storage,
     semantics:semantics!,semantic:semantic!,domain:domain!,baseline:baseline!});
    workerLocalObservations.add(selector);current();return selector;
   },
   openWorkflowLocalObservationRunner(workflowId:string){
    current();if(!entryContext||!selectedEntries)
     fail('InvalidContract',where,'selected Entry/Auth required for generated local observation');
    const binding=workflowBinding(workflowId),storage=stores.get(binding.inspect().owner_service);
    if(!storage)fail('MissingMapping',where,'selected Workflow producer storage must be open');
    const snapshots=owner.openWorkflowSnapshotQuery(workflowId),selector=owner.openWorkflowLocalObservation(workflowId);
    const runner=createCoreCommerceWorkerLocalObservationRunner({assembly:owner,binding,storage,
     auth:entryContext,selected:selectedEntries,semantics:semantics!,semantic:semantic!,
     domain:domain!,baseline:baseline!,selector,snapshotQuery:snapshots});
    const wrapped:ReturnType<typeof createCoreCommerceWorkerLocalObservationRunner>=Object.freeze({
     inspect:()=>runner.inspect(),assertCurrent:()=>runner.assertCurrent(),
     run:(session:Parameters<CoreCommerceWorkerLocalObservationRunner['run']>[0],snapshot:Parameters<CoreCommerceWorkerLocalObservationRunner['run']>[1])=>runner.run(session,snapshot),
     bindActor(actor:CommerceAuthActorV1){const assigned=new Set([...snapshots.bindActor(actor),...runner.bindActor(actor)]);return Object.freeze([...assigned].sort());},
     close(){try{runner.close();}finally{try{snapshots.close();}finally{selector.close();}}},
    });
    workerLocalObservationRunners.add(wrapped);current();return wrapped;
   },
   openWorkflowCycle(workflowId:string){
    current();if(!entryContext||!selectedEntries)
     fail('InvalidContract',where,'selected Entry/Auth required for generated Workflow cycle');
    const binding=workflowBinding(workflowId),storage=stores.get(binding.inspect().owner_service);
    if(!storage)fail('MissingMapping',where,'selected Workflow producer storage must be open');
    const snapshots=owner.openWorkflowSnapshotQuery(workflowId),
     continuation=owner.openWorkflowContinuation(workflowId),
     remote=owner.openWorkflowStepRunner(workflowId),
     selector=owner.openWorkflowLocalObservation(workflowId);
    const local=createCoreCommerceWorkerLocalObservationRunner({assembly:owner,binding,storage,
     auth:entryContext,selected:selectedEntries,semantics:semantics!,semantic:semantic!,
     domain:domain!,baseline:baseline!,selector,snapshotQuery:snapshots});
    workerLocalObservationRunners.add(local);
    const cycle=createCoreCommerceWorkerCycle({binding,snapshots,continuation,remote,local});
    workerCycles.add(cycle);current();return cycle;
   },
   openWorkflowPass(workflowId:string){
    current();const pass=createCoreCommerceWorkflowPass(owner,workflowId);
    workflowPasses.add(pass);current();return pass;
   },
   openCrossServiceEvent(entryId:string){
    current();
    if(eventRuntimeBindings.has(entryId))fail('InvalidContract',where,'one open receiver Event route per Entry required');
    const entries=sourceEntries.filter(entry=>entry.id===entryId&&entry.interaction==='event');
    if(entries.length!==1)fail('MissingMapping',where,'one original Event Entry required');
    const entry=entries[0]!;
    if(!entry.access.producer)fail('MissingMapping',where,'original Event producer service required');
    const producer=stores.get(entry.access.producer),receiver=stores.get(entry.service);
    if(!producer||!receiver)fail('MissingMapping',where,'both selected Event service stores must be open');
    const relay=createCoreCommerceCrossServiceEventRelay({sources,capture:capture!,semantics:semantics!,
     semantic:semantic!,producer,receiver,entryId});
    let admission:CoreCommerceEventIngressAdmission|undefined;
    let publication:CoreCommerceEventPublication|undefined;
    let producerSource:CoreCommerceEventProducerSource|undefined;
    let provenance:CoreCommerceEventProducerProvenance|undefined;
    let acknowledgement:CoreCommerceEventAckSelection|undefined;
    let receiverCommit:CoreCommerceEventReceiverCommitOwner|undefined;
    try{
     admission=createCoreCommerceEventIngressAdmission({relay,semantics:semantics!,semantic:semantic!});
     publication=createCoreCommerceEventPublication({sources,capture:capture!,
      semantics:semantics!,semantic:semantic!,models:models!,model:model!,families:families!,
      assemblyOwner:assemblyOwner!,assembly,producer,receiver,relay});
     producerSource=createCoreCommerceEventProducerSource({semantics:semantics!,
      semantic:semantic!,plans:plans!,relay});
     provenance=createCoreCommerceEventProducerProvenance({relay,source:producerSource,producer});
     acknowledgement=createCoreCommerceEventAckSelection({sources,capture:capture!,
      semantics:semantics!,semantic:semantic!,plans:plans!,relay});
     receiverCommit=createCoreCommerceEventReceiverCommitOwner({relay,acknowledgement,receiver});
    }catch(error){receiverCommit?.close();acknowledgement?.close();provenance?.close();
     producerSource?.close();publication?.close();admission?.close();relay.close();throw error;}
    crossServiceEventRelays.add(relay);eventIngressAdmissions.add(admission);
    eventPublications.add(publication);eventAcknowledgements.add(acknowledgement);
    eventProducerSources.add(producerSource);eventProvenances.add(provenance);
    eventReceiverCommits.add(receiverCommit);
    eventRuntimeBindings.set(entryId,Object.freeze({relay,selection:acknowledgement,receiverCommit}));
    current();return Object.freeze({relay,admission,publication,producerSource,provenance,
     acknowledgement,receiverCommit,
     openDelivery(){
      current();if(!entryContext||!selectedEntries)
       fail('InvalidContract',where,'selected Entry/Auth required for generated Event delivery');
      const delivery=createCoreCommerceEventDelivery({assembly:owner,auth:entryContext,
       selected:selectedEntries,producer,receiver,relay,admission,
       acknowledgement,receiverCommit});
      eventDeliveries.add(delivery);current();return delivery;
     },
     publish(input:Readonly<{candidate:CoreCommerceEventPublicationCandidate;
      proof:CoreCommerceEventProducerProof;delivery:CoreCommerceEventDelivery;
      acknowledgement:CoreCommerceEventReceiverAcknowledgement}>){
      current();return producer.publishSelectedEvent({publication,provenance,
       candidate:input.candidate,proof:input.proof,delivery:input.delivery,
       acknowledgement:input.acknowledgement});
     },
     reconcile(attempt:CommerceEventPublicationAttemptV1){current();return producer.reconcileEventPublication(attempt);},
     reconcilePublished(occurrenceId:string){current();return producer.reconcilePublishedEvent({
      publication,producerSource,receiver,occurrence_id:occurrenceId});},
    });
   },
  exportFormalStructure(workflowId:string,language:CoreCommerceFormalLanguageV1='alloy'){
   current();
   if(language!=='alloy')throw new CoreCommerceFormalArtifactErrorV1('UnsupportedLanguage');
   const binding=workflowBinding(workflowId);
   const model=exportCoreCommerceFormalStructureV1(sources,capture!,semantics!,semantic!,binding,owner);
   current();return model;
  },
  exportFormalArtifacts(workflowId:string,language:CoreCommerceFormalLanguageV1='alloy'){
   current();
   const binding=workflowBinding(workflowId);
   const artifacts=createCoreCommerceFormalArtifactsV1(sources,capture!,semantics!,semantic!,binding,owner,language);
   current();return artifacts;
  },
  publishFormalStructure(workflowId:string,targetRoot:string,language:CoreCommerceFormalLanguageV1='alloy'){
   current();
   const binding=workflowBinding(workflowId);
   return publishCoreCommerceFormalArtifactsV1(sources,capture!,semantics!,semantic!,binding,owner,targetRoot,language);
  },
  exportPureUint64Formal(selector:string){
   current();
   const model=exportCoreCommercePureUint64SmtV1(sources,capture!,semantics!,semantic!,owner,selector);
   current();return model;
  },
  exportFormalTemporal(workflowId:string){
   current();
   const binding=workflowBinding(workflowId);
   const model=exportCoreCommerceFormalTemporalV1(sources,capture!,semantics!,semantic!,binding,owner);
   current();return model;
  },
   assertCurrent:current,
   close:cleanup,
  });
  owners.add(owner);current();handedOff=true;return owner;
 }finally{if(!handedOff)cleanup();}
}
