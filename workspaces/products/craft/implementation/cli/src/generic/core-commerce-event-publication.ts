/** Checked publication proposal for the finite Core EventInboxOutbox family.
 * It cannot publish: a native receiver-commit witness and source-owned producer
 * CAS are required before Ready may become Published.
 * eventId, Ready, and Published are checked against the authored source here;
 * they are not universal GenericEventBindingV1 conventions.
 * Open Questions: docs/GENERIC-APPLICATIONS.md#open-questions. */
import {isDeepStrictEqual} from 'node:util';
import {coreFreeze} from '../commerce/commerce-core-syntax.js';
import {createCoreValueTypes,sameCoreValueType} from '../commerce/commerce-core-types.js';
import {assertCoreCommerceSemanticOwner,type CoreCommerceSemanticOwner,type CoreCommerceSemanticCapture}
 from '../commerce/commerce-core-semantic-owner.js';
import {assertTechnicalModelOwnerV5,type CommerceTechnicalModelOwnerV5}
 from '../profile-engine/technical-model-v5.js';
import {assertFamilyOwnerV5,type CommerceFamilyOwnerV5} from '../profile-engine/family-v5.js';
import {assertCommerceBindingAssemblyOwnerV1,type CommerceBindingAssemblyOwnerV1}
 from '../commerce/commerce-binding-assembly-v1.js';
import type {CommerceBindingAssemblyHandle,CommerceTechnicalModelHandle} from '../commerce/commerce-stages-v1.js';
import {assertCoreCommerceSourceOwner,type CoreCommerceSourceOwner,type CoreCommerceSourceCapture}
 from '../commerce/commerce-core-source-owner.js';
import {assertCommerceServiceStorageOwnerV1,type CommerceServiceStorageOwnerV1}
 from '../commerce/commerce-service-storage-v1.js';
import {assertCoreCommerceCrossServiceEventRelay,type CoreCommerceCrossServiceEventRelay,
 type CoreCommerceCrossServiceOccurrence} from './core-commerce-cross-service-event-relay.js';

export interface CoreCommerceEventPublicationCandidate {
 readonly kind:'original-event-publication-candidate/v1-candidate';
}
export interface CoreCommerceEventPublication {
 inspect():Readonly<{entry:string;producer_operation:string;producer_service:string;receiver_service:string;
  native_family:'EventInboxOutbox';outbox_identity_field:'eventId';
  outbox_entity:string;consumer_inbox_entity:string;event_type:string;state_type:string;
  ready_state:'Ready';published_state:'Published';
  publication_machine:string;publication_signal:string;
  producer_store_id:string;receiver_store_id:string;source_capture_sha256:string;
  family_sha256:string;
  qualification:'source-selected-outbox-transition;native-receiver-witness-and-producer-CAS-pending';
  authority_effect:'none'}>;
 prepare(occurrence:CoreCommerceCrossServiceOccurrence):CoreCommerceEventPublicationCandidate;
 inspectCandidate(candidate:CoreCommerceEventPublicationCandidate):Readonly<{
  entry:string;occurrence_id:string;outbox_entity:string;expected_state:'Ready';
  expected_version:bigint;next_state:'Published';next_version:bigint;
  qualification:'original-ready-outbox-proposal-only;no-publication-authority';
  authority_effect:'none'}>;
 assertCurrent():void;close():void;
}
const owners=new WeakSet<object>();
export function assertCoreCommerceEventPublication(owner:CoreCommerceEventPublication):void {
 if(!owner||typeof owner!=='object'||!owners.has(owner))
  throw new Error('original Event publication owner required');
 owner.assertCurrent();
}

/** The relay provides the exact checked Event route and occurrence. The
 * original source supplies the outbox state type and allowed transition.
 * Neither a caller receipt nor a transport response is accepted here. */
export function createCoreCommerceEventPublication(input:Readonly<{
 sources:CoreCommerceSourceOwner;capture:CoreCommerceSourceCapture;
 semantics:CoreCommerceSemanticOwner;semantic:CoreCommerceSemanticCapture;
 models:CommerceTechnicalModelOwnerV5;model:CommerceTechnicalModelHandle;
 families:CommerceFamilyOwnerV5;assemblyOwner:CommerceBindingAssemblyOwnerV1;
 assembly:CommerceBindingAssemblyHandle;
 producer:CommerceServiceStorageOwnerV1;receiver:CommerceServiceStorageOwnerV1;
 relay:CoreCommerceCrossServiceEventRelay;
}>):CoreCommerceEventPublication {
 const {sources,capture,semantics,semantic,models,model,families,assemblyOwner,assembly,
  producer,receiver,relay}=input;
 assertCoreCommerceSourceOwner(sources);assertCommerceServiceStorageOwnerV1(producer);
 assertCommerceServiceStorageOwnerV1(receiver);assertCoreCommerceCrossServiceEventRelay(relay);
 assertCoreCommerceSemanticOwner(semantics);semantics.assertSource(semantic,capture);
 assertTechnicalModelOwnerV5(models);assertFamilyOwnerV5(families);
 assertCommerceBindingAssemblyOwnerV1(assemblyOwner);assemblyOwner.assertCurrent(assembly);
 const source=sources.inspect(capture),selection=relay.inspect(),route=selection.route,
  producerStore=producer.inspect(),receiverStore=receiver.inspect(),
  selected=assemblyOwner.inspect(assembly),family=families.inspect(assemblyOwner.family(assembly)),
  technical=models.inspect(model),checked=semantics.inspect(semantic);
 if(source.capture_sha256!==route.source_capture_sha256||
  selected.selection.source_capture_sha256!==route.source_capture_sha256||
  selected.selected_family_sha256!==family.family_sha256||
  family.family_sha256!==producerStore.family_sha256||
  family.family_sha256!==receiverStore.family_sha256||
  technical.source_capture_sha256!==route.source_capture_sha256||
  checked.source_capture_sha256!==route.source_capture_sha256||
  !selected.selection.native_requirements.some(row=>row.primitive_id==='event-inbox-outbox')||
  producerStore.store_id!==selection.producer_store_id||
  receiverStore.store_id!==selection.receiver_store_id||
  producerStore.source_capture_sha256!==route.source_capture_sha256||
  receiverStore.source_capture_sha256!==route.source_capture_sha256||
  producerStore.family_sha256!==receiverStore.family_sha256||
  producerStore.service!==route.producer_service||
  receiverStore.service!==route.receiver_service||
  producerStore.store_id===receiverStore.store_id)
  throw new Error('one original Event route and distinct selected service stores required');
 const profile=(technical.family_contract.families as Record<string,unknown>|undefined)?.EventInboxOutbox as
  {primitive?:unknown;publication?:{machine?:unknown;signal?:unknown}}|undefined;
 const publication=profile?.publication;
 if(profile?.primitive!=='event-inbox-outbox'||!publication||
  typeof publication.machine!=='string'||typeof publication.signal!=='string')
  throw new Error('selected EventInboxOutbox publication StateMachine required');
 const declarations=source.reconstruction.modules.flatMap(module=>module.declarations),
  outboxes=declarations.filter(row=>row.id===route.outbox_entity&&row.surface==='Entity');
 if(outboxes.length!==1)throw new Error('one original producer Event outbox required');
 const outbox=outboxes[0]!,types=createCoreValueTypes(source.reconstruction),
  stateField=outbox.fields.find(field=>field.name==='state'),
  versionField=outbox.fields.find(field=>field.name==='version'),
  eventField=outbox.fields.find(field=>field.name==='event');
 if(!stateField||!versionField||!eventField||
  !isDeepStrictEqual(outbox.identity,['eventId'])||
  source.reconstruction.ownership.find(row=>row.declaration===outbox.id)?.service!==route.producer_service||
  !sameCoreValueType(types.type(outbox.module,versionField.type,versionField.span),{kind:'UInt64'}))
  throw new Error('EventInboxOutbox requires source-owned eventId identity and UInt64 version');
 const stateType=types.type(outbox.module,stateField.type,stateField.span),
  eventType=types.type(outbox.module,eventField.type,eventField.span);
 if(stateType.kind!=='enum'||eventType.kind!=='record'||eventType.name!==route.event_type)
  throw new Error('selected Event outbox state and payload types required');
 const states=declarations.filter(row=>row.id===stateType.name&&row.surface==='Enum');
 if(states.length!==1||!['Ready','Published'].every(name=>
  states[0]!.variants.some(variant=>variant.name===name&&variant.fields.length===0)))
  throw new Error('EventInboxOutbox requires authored Ready and Published states');
 const machines=checked.pure.declarations.filter(row=>row.name===publication.machine&&row.kind==='StateMachine');
 if(machines.length!==1)throw new Error('one checked Event publication StateMachine required');
 const machine=machines[0]!,body=machine.body,
  enumValue=(value:unknown,type:string,variant:string)=>!!value&&typeof value==='object'&&
   (value as {op?:unknown}).op==='enum_value'&&
   (value as {type_name?:unknown}).type_name===type&&
   (value as {variant?:unknown}).variant===variant&&
   Object.keys((value as {fields?:Record<string,unknown>}).fields??{}).length===0,
  eq=(value:unknown,name:string,type:string,variant:string)=>!!value&&typeof value==='object'&&
   (value as {op?:unknown;operator?:unknown}).op==='binary'&&
   (value as {operator?:unknown}).operator==='eq'&&
   (value as {left?:{op?:unknown;name?:unknown}}).left?.op==='var'&&
   (value as {left?:{name?:unknown}}).left?.name===name&&
   enumValue((value as {right?:unknown}).right,type,variant);
 if(machine.parameters.length!==2||machine.parameters[0]?.type.kind!=='enum'||
  machine.parameters[0].type.name!==stateType.name||
  machine.parameters[1]?.type.kind!=='enum'||
  body.op!=='state_machine'||machine.result.kind!=='outcome'||
  !sameCoreValueType(machine.result.state,stateType)||
  machine.result.intent.kind!=='Bool'||machine.result.maximum!==0||
  body.max_intents!==0||body.otherwise!=='reject'||
  !enumValue(body.initial,stateType.name,'Ready')||
  body.terminal.length!==1||!enumValue(body.terminal[0],stateType.name,'Published')||
  body.transitions.length!==1||body.transitions[0]!.intents.length!==0||
  !enumValue(body.transitions[0]!.next,stateType.name,'Published')||
  body.transitions[0]!.guard.op!=='binary'||
  body.transitions[0]!.guard.operator!=='and'||
  !eq(body.transitions[0]!.guard.left,'state',stateType.name,'Ready')||
  !eq(body.transitions[0]!.guard.right,'event',machine.parameters[1].type.name,publication.signal))
  throw new Error('checked Event publication must propose only Ready plus committed consumer to Published');
 const inspected=coreFreeze({entry:route.entry,producer_operation:route.producer_operation,
  producer_service:route.producer_service,
  receiver_service:route.receiver_service,native_family:'EventInboxOutbox' as const,
  outbox_identity_field:'eventId' as const,outbox_entity:outbox.id,
  consumer_inbox_entity:route.consumer_inbox_entity,event_type:route.event_type,
  state_type:stateType.name,
  ready_state:'Ready' as const,published_state:'Published' as const,
  publication_machine:publication.machine,publication_signal:publication.signal,
  producer_store_id:producerStore.store_id,receiver_store_id:receiverStore.store_id,
  source_capture_sha256:route.source_capture_sha256,family_sha256:family.family_sha256,
  qualification:'source-selected-outbox-transition;native-receiver-witness-and-producer-CAS-pending' as const,
  authority_effect:'none' as const});
 const issued=new WeakMap<object,{occurrence:CoreCommerceCrossServiceOccurrence;id:string;
  outbox:unknown;version:bigint}>();let closed=false;
 const current=()=>{
  if(closed)throw new Error('Event publication owner closed');
  sources.assertCurrent(capture);producer.assertCurrent();receiver.assertCurrent();relay.assertCurrent();
  semantics.assertCurrent(semantic);models.assertCurrent(model);assemblyOwner.assertCurrent(assembly);
  if(producer.inspect().store_id!==producerStore.store_id||
   receiver.inspect().store_id!==receiverStore.store_id||
   relay.inspect().route.source_capture_sha256!==inspected.source_capture_sha256)
   throw new Error('Event publication source or service store changed');
 };
 const owner:CoreCommerceEventPublication=Object.freeze({
  inspect(){current();return inspected;},
  prepare(occurrence:CoreCommerceCrossServiceOccurrence){
   current();const view=relay.inspectOccurrence(occurrence);
   if(view.route.entry!==inspected.entry||view.route.outbox_entity!==inspected.outbox_entity||
    view.route.source_capture_sha256!==inspected.source_capture_sha256||
    !view.outbox||typeof view.outbox!=='object'||Array.isArray(view.outbox)||
    (view.outbox as {state?:unknown}).state!=='Ready'||
    typeof (view.outbox as {version?:unknown}).version!=='bigint')
    throw new Error('one original Ready Event occurrence required');
   const version=(view.outbox as {version:bigint}).version;
   if(version<1n||version>=(1n<<64n)-1n)
    throw new Error('outbox version cannot advance within UInt64');
   const candidate:CoreCommerceEventPublicationCandidate=Object.freeze({
    kind:'original-event-publication-candidate/v1-candidate'});
   issued.set(candidate,{occurrence,id:view.occurrence_id,outbox:view.outbox,version});
   return candidate;
  },
  inspectCandidate(candidate:CoreCommerceEventPublicationCandidate){
   current();const saved=candidate&&typeof candidate==='object'?issued.get(candidate):undefined;
   if(!saved)throw new Error('original Event publication candidate required');
   const fresh=relay.inspectOccurrence(saved.occurrence);
   if(fresh.occurrence_id!==saved.id||!isDeepStrictEqual(fresh.outbox,saved.outbox))
    throw new Error('Event outbox changed before publication');
   return coreFreeze({entry:inspected.entry,occurrence_id:saved.id,
    outbox_entity:inspected.outbox_entity,expected_state:'Ready' as const,
    expected_version:saved.version,next_state:'Published' as const,
    next_version:saved.version+1n,
    qualification:'original-ready-outbox-proposal-only;no-publication-authority' as const,
    authority_effect:'none' as const});
  },
  assertCurrent:current,close(){closed=true;},
 });
 owners.add(owner);current();return owner;
}
