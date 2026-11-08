/** Source-bound join of one checked Workflow, its Event handoff, and emitted
 * service artifacts. The finite Alloy graph fixes declaration and artifact
 * identities; the accompanying TLA+ projection still abstracts execution.
 * Open Questions: docs/GENERIC-APPLICATIONS.md#open-questions. */
import {createHash} from 'node:crypto';
import {dataDigest} from '../profile-engine/contracts.js';
import {requireGenericCompositionRuntime,requireGenericWorkflowRuntime,
 type GenericCompositionHandle,
 type createGenericCompositionOwner} from './public-sdk.js';
import {type GenericServiceArtifactHandle,type createGenericServiceArtifactOwner}
 from './service-artifact-owner.js';
import {exportGenericWorkflowTlaModel} from './formal-workflow-tla.js';
import {exportGenericStructuralAlloyModel} from './formal-structural-alloy.js';

type SDK=ReturnType<typeof createGenericCompositionOwner>;
type Artifacts=ReturnType<typeof createGenericServiceArtifactOwner>;
const sha=(value:string)=>createHash('sha256').update(value).digest('hex');
export class GenericWorkflowEventJoinErrorV1 extends Error {
 constructor(readonly code:'UnsupportedTranslation'|'StaleIdentity'|'InvalidModel'){
  super(code);this.name='GenericWorkflowEventJoinErrorV1';
 }
}
const fail=(code:GenericWorkflowEventJoinErrorV1['code']):never=>{
 throw new GenericWorkflowEventJoinErrorV1(code);
};

export interface GenericWorkflowEventJoinV1 {
 readonly schema_version:'craft.generic-workflow-event-formal-join/v1-candidate';
 readonly language:'alloy+tla+';
 readonly scope:'checked-workflow-event-definition-and-emitted-subgraph';
 readonly source_capture_sha256:string;
 readonly profile_sha256:string;
 readonly workflow_profile_sha256:string;
 readonly application_contract_sha256:string;
 readonly executable_semantics_sha256:string;
 readonly workflow_executable_semantics_sha256:string;
 readonly workflow_contract_sha256:string;
 readonly workflow_compatibility_sha256:string;
 readonly emitted_inventory_sha256:string;
 readonly structural_alloy_sha256:string;
 readonly workflow_tla_sha256:string;
 readonly workflow:Readonly<{id:string;service:string;worker_artifact:string}>;
 readonly steps:readonly Readonly<{
  index:0|1|2;name:string;kind:'local-command'|'provider-command'|'event-await';
  entry:string;entry_contract_sha256:string;emitted_artifact:string;
  successor:1|2|null;
 }>[];
 readonly compensation:Readonly<{source_step:0;entry:string;entry_contract_sha256:string;
  emitted_artifact:string}>;
 readonly event:Readonly<{binding:string;binding_sha256:string;selector:string;
  producer_service:string;producer_operation:string;target_service:string;
  target_entry:string;payload_schema_sha256:string}>;
 readonly provider_policy:Readonly<{on_unknown:'resume-original-command';
  on_definite_failure:'compensate';
  failure_compensation_precondition:'proven-no-provider-effect'}>;
 readonly emitted_complete_application:boolean;
 readonly missing_complete_application_classes:readonly string[];
 readonly alloy:string;
 readonly alloy_sha256:string;
 readonly tla:string;
 readonly authority_effect:'none';
 readonly unsupported_semantics:readonly ['provider-result-and-no-effect-proof-production',
  'event-delivery-and-receipt-proof-production','auth-and-permission-decisions',
  'journal-cas-and-lease-timing','native-effects-commit-rollback-and-recovery',
  'complete-application-runtime-parity','model-checker-proof'];
 readonly claim_ceiling:'exact-checked-definition-and-emitted-subgraph-with-abstract-runtime-transitions';
}

/** Neither a caller-supplied inventory nor an unbranded composition is enough:
 * both original owners are rechecked before and after the join. */
export function exportGenericWorkflowEventJoinV1(
 sdk:SDK,handle:GenericCompositionHandle,artifacts:Artifacts,
 artifact:GenericServiceArtifactHandle,
):GenericWorkflowEventJoinV1 {
 const binding=requireGenericWorkflowRuntime(sdk,handle);
 const source=binding.contract,application=binding.baseApplication;
 const composition=requireGenericCompositionRuntime(sdk,handle);
 if(composition.application.kind!=='original-generic-transaction-application/v1-candidate')
  fail('UnsupportedTranslation');
 const admitted=composition.plans.inspectSourceApplication(composition.application);
 const structural=exportGenericStructuralAlloyModel(artifacts,artifact);
 const temporal=exportGenericWorkflowTlaModel(sdk,handle);
 const manifest=artifacts.inspect(artifact);
 if(structural.source_capture_sha256!==source.source_capture_sha256||
  structural.profile_sha256!==admitted.derivation.profile_sha256||
  structural.application_contract_sha256!==source.base_application_sha256||
  structural.executable_semantics_sha256!==admitted.executable_semantics_sha256||
  admitted.contract_sha256!==source.base_application_sha256||
  admitted.source_capture_sha256!==source.source_capture_sha256||
  binding.derivation.profile_sha256!==source.profile_sha256||
  manifest.inventory_sha256!==structural.inventory_sha256||
  temporal.source_capture_sha256!==source.source_capture_sha256||
  temporal.profile_sha256!==source.profile_sha256||
  temporal.base_application_sha256!==source.base_application_sha256||
  temporal.executable_semantics_sha256!==binding.derivation.executable_semantics_sha256||
  temporal.workflow_contract_sha256!==dataDigest(source))fail('StaleIdentity');
 if(source.steps.length!==3)
  fail('UnsupportedTranslation');
 const local=source.steps[0]??fail('UnsupportedTranslation');
 const provider=source.steps[1]??fail('UnsupportedTranslation');
 const awaitEvent=source.steps[2]??fail('UnsupportedTranslation');
 if(local.kind!=='local-command'||provider.kind!=='provider-command'||
  awaitEvent.kind!=='event-await'||
  provider.on_unknown!=='resume-original-command'||
  provider.on_definite_failure!=='compensate'||
  provider.provider_failure_compensation_precondition!=='proven-no-provider-effect')
  fail('UnsupportedTranslation');
 const compensationEntryId=local.compensation_entry??fail('UnsupportedTranslation');
 const compensationContractSha=local.compensation_contract_sha256??fail('UnsupportedTranslation');
 const eventBindingId=awaitEvent.event_binding??fail('UnsupportedTranslation');
 const eventBindingSha=awaitEvent.event_binding_sha256??fail('UnsupportedTranslation');
 const events=application.event_bindings.filter(row=>row.id===eventBindingId);
 if(events.length!==1||dataDigest(events[0])!==eventBindingSha)
  fail('StaleIdentity');
 const event=events[0]!;
 const owner=structural.services.find(row=>row.id===source.service)??fail('UnsupportedTranslation');
 const workflow=structural.workflows.find(row=>row.id===source.workflow)??fail('UnsupportedTranslation');
 const selectedEvent=structural.events.find(row=>row.id===event.id)??fail('UnsupportedTranslation');
 const producer=structural.services.find(row=>row.id===event.producer_service)??fail('UnsupportedTranslation');
 const receiver=structural.services.find(row=>row.id===event.target_service)??fail('UnsupportedTranslation');
 if(owner.workflow!==workflow.atom||event.producer_service!==source.service||
  selectedEvent.services.length!==2||
  !selectedEvent.services.includes(producer.id)||
  !selectedEvent.services.includes(receiver.id)||
  event.target_entry!==awaitEvent.entry||
  application.entries.filter(row=>row.entry===event.target_entry).length!==1||
  application.entries.filter(row=>row.entry===provider.entry&&
   'target' in row&&row.target===event.producer_operation).length!==1)
  fail('UnsupportedTranslation');
 const entry=(id:string,expectedService?:string)=>{
  const matches=structural.entries.filter(row=>row.id===id);
  if(matches.length!==1||expectedService&&matches[0]!.service!==expectedService)
   fail('UnsupportedTranslation');
  return matches[0]!;
 };
 const start=entry(source.start_entry,source.service);
 const localEntry=entry(local.entry,source.service);
 const providerEntry=entry(provider.entry,source.service);
 const compensationEntry=entry(compensationEntryId,source.service);
 const receiverEntry=entry(awaitEvent.entry,event.target_service);
 const artifactPath=(atom:string)=>{
  const selected=structural.artifacts.filter(row=>row.atom===atom);
  if(selected.length!==1||!manifest.files.some(row=>row.path===selected[0]!.path&&
   row.sha256===selected[0]!.sha256))fail('StaleIdentity');
  return selected[0]!.path;
 };
 if(receiverEntry.interaction!=='event'||
  [start,localEntry,providerEntry,compensationEntry].some(row=>row.interaction!=='request-response'))
  fail('UnsupportedTranslation');
 const workerPath=artifactPath(workflow.worker);
 const steps=[
  {index:0 as const,name:local.name,kind:local.kind as 'local-command',entry:local.entry,
   entry_contract_sha256:local.entry_contract_sha256,
   emitted_artifact:artifactPath(localEntry.executable),successor:1 as const},
  {index:1 as const,name:provider.name,kind:provider.kind as 'provider-command',entry:provider.entry,
   entry_contract_sha256:provider.entry_contract_sha256,
   emitted_artifact:artifactPath(providerEntry.executable),successor:2 as const},
  {index:2 as const,name:awaitEvent.name,kind:awaitEvent.kind as 'event-await',entry:awaitEvent.entry,
   entry_contract_sha256:awaitEvent.entry_contract_sha256,
   emitted_artifact:artifactPath(receiverEntry.executable),successor:null},
 ];
 const lines=[
  '// Exact finite checked source order and selected emitted identity only.',
  `// source_capture_sha256 ${source.source_capture_sha256}`,
  `// workflow_contract_sha256 ${dataDigest(source)}`,
  `// workflow_tla_sha256 ${temporal.tla_sha256}`,
  `// structural_alloy_sha256 ${structural.alloy_sha256}`,
  `// emitted_inventory_sha256 ${manifest.inventory_sha256}`,
  `// workflow_id_sha256 ${sha(source.workflow)}`,
  `// event_binding_id_sha256 ${sha(event.id)}`,
  `// event_binding_contract_sha256 ${eventBindingSha}`,
  'abstract sig Service {}',
  'abstract sig Entry { service: one Service }',
  'abstract sig EventBinding { producer: one Service, receiver: one Service, target: one Entry }',
  'abstract sig Step { entry: one Entry, next: lone Step, awaits: lone EventBinding }',
  'abstract sig Workflow { owner: one Service, start: one Entry, first: one Step, compensation: one Entry }',
  'one sig OwnerService, ReceiverService extends Service {}',
  'one sig StartEntry, LocalEntry, ProviderEntry, CompensationEntry, ReceiverEntry extends Entry {}',
  'one sig Handoff extends EventBinding {}',
  'one sig LocalStep, ProviderStep, EventStep extends Step {}',
  'one sig SelectedWorkflow extends Workflow {}',
  'fact ExactCheckedDefinition {',
  '  StartEntry.service = OwnerService',
  '  LocalEntry.service = OwnerService',
  '  ProviderEntry.service = OwnerService',
  '  CompensationEntry.service = OwnerService',
  '  ReceiverEntry.service = ReceiverService',
  '  Handoff.producer = OwnerService',
  '  Handoff.receiver = ReceiverService',
  '  Handoff.target = ReceiverEntry',
  '  SelectedWorkflow.owner = OwnerService',
  '  SelectedWorkflow.start = StartEntry',
  '  SelectedWorkflow.first = LocalStep',
  '  SelectedWorkflow.compensation = CompensationEntry',
  '  LocalStep.entry = LocalEntry',
  '  ProviderStep.entry = ProviderEntry',
  '  EventStep.entry = ReceiverEntry',
  '  LocalStep.next = ProviderStep',
  '  ProviderStep.next = EventStep',
  '  no EventStep.next',
  '  no LocalStep.awaits',
  '  no ProviderStep.awaits',
  '  EventStep.awaits = Handoff',
  '}',
  '// Outcome, delivery, authorization, commit and recovery are unconstrained here.',
  'run {} for exactly 2 Service, exactly 5 Entry, exactly 1 EventBinding, exactly 3 Step, exactly 1 Workflow',
  '',
 ];
 const alloy=lines.join('\n');
 const result:GenericWorkflowEventJoinV1=Object.freeze({
  schema_version:'craft.generic-workflow-event-formal-join/v1-candidate' as const,
  language:'alloy+tla+' as const,
  scope:'checked-workflow-event-definition-and-emitted-subgraph' as const,
  source_capture_sha256:source.source_capture_sha256,
  profile_sha256:admitted.derivation.profile_sha256,
  workflow_profile_sha256:source.profile_sha256,
  application_contract_sha256:source.base_application_sha256,
  executable_semantics_sha256:admitted.executable_semantics_sha256,
  workflow_executable_semantics_sha256:binding.derivation.executable_semantics_sha256,
  workflow_contract_sha256:dataDigest(source),workflow_compatibility_sha256:temporal.compatibility_sha256,
  emitted_inventory_sha256:manifest.inventory_sha256,
  structural_alloy_sha256:structural.alloy_sha256,workflow_tla_sha256:temporal.tla_sha256,
  workflow:{id:source.workflow,service:source.service,worker_artifact:workerPath},
  steps,compensation:{source_step:0 as const,entry:compensationEntryId,
   entry_contract_sha256:compensationContractSha,
   emitted_artifact:artifactPath(compensationEntry.executable)},
  event:{binding:event.id,binding_sha256:eventBindingSha,
   selector:event.event_selector,producer_service:event.producer_service,
   producer_operation:event.producer_operation,target_service:event.target_service,
   target_entry:event.target_entry,payload_schema_sha256:event.payload_schema_sha256},
  provider_policy:{on_unknown:'resume-original-command' as const,
   on_definite_failure:'compensate' as const,
   failure_compensation_precondition:'proven-no-provider-effect' as const},
  emitted_complete_application:manifest.complete_application,
  missing_complete_application_classes:manifest.missing_complete_application_classes,
  alloy,alloy_sha256:sha(alloy),tla:temporal.tla,authority_effect:'none' as const,
  unsupported_semantics:['provider-result-and-no-effect-proof-production',
   'event-delivery-and-receipt-proof-production','auth-and-permission-decisions',
   'journal-cas-and-lease-timing','native-effects-commit-rollback-and-recovery',
   'complete-application-runtime-parity','model-checker-proof'] as const,
  claim_ceiling:'exact-checked-definition-and-emitted-subgraph-with-abstract-runtime-transitions' as const,
 });
 binding.assertCurrent();artifacts.inspect(artifact);
 return result;
}

export function assertGenericWorkflowEventJoinCurrentV1(
 sdk:SDK,handle:GenericCompositionHandle,artifacts:Artifacts,
 artifact:GenericServiceArtifactHandle,model:GenericWorkflowEventJoinV1,
):void {
 if(!model||typeof model!=='object'||typeof model.alloy!=='string'||
  typeof model.tla!=='string'||model.alloy_sha256!==sha(model.alloy)||
  model.workflow_tla_sha256!==sha(model.tla)||
  dataDigest(model)!==dataDigest(exportGenericWorkflowEventJoinV1(sdk,handle,artifacts,artifact)))
  fail('InvalidModel');
}
