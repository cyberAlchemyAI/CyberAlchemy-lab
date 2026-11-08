/** Binds a checked Workflow to its source-declared technical records.
 * This source binding creates no event, worker, claim, journal or dispatch.
 * Open Questions: docs/COMMERCE-CONTRACTS.md#open-questions. */
import {coreFreeze,coreSourceFail as fail} from './commerce-core-syntax.js';
import {createCoreValueTypes,coreStringDomain,sameCoreValueType,type CoreValueType} from './commerce-core-types.js';
import type {CoreCommerceDeclaration} from './commerce-core-reconstruction.js';
import {createCoreContextCatalog} from './commerce-core-context.js';
import {checkCoreCommerceWorkflowSources,type CoreWorkflowSource} from './commerce-core-flow-workflow.js';
import {assertCoreCommerceSourceOwner,type CoreCommerceSourceOwner,type CoreCommerceSourceCapture} from './commerce-core-source-owner.js';
import {assertCoreCommerceStageSourceOwner,type CoreCommerceStageSourceOwner} from './commerce-core-stage-owner.js';
import type {CommerceSourceHandle} from './commerce-stages-v1.js';

const where={path:'workflow-coordination-binding',start:0,end:0};
export interface CommerceWorkflowCoordinationInspectionV1 {
 readonly workflow:CoreWorkflowSource;
 readonly owner_service:string;
 readonly source_capture_sha256:string;
 readonly input_outbox_entity:string;
 readonly inbox_entity:string;
 readonly schedule_entity:string;
 readonly journal_entity:string;
 readonly receipt_type:string;
 readonly qualification:'checked-source-workflow-and-technical-record-selectors-only';
 readonly authority_effect:'none';
}
export interface CommerceWorkflowCoordinationBindingV1 {
 inspect():CommerceWorkflowCoordinationInspectionV1;
 assertCurrent():void;
}
const owners=new WeakSet<object>();
export function assertCommerceWorkflowCoordinationBindingV1(owner:CommerceWorkflowCoordinationBindingV1):void {
 if(!owner||typeof owner!=='object'||!owners.has(owner))fail('ForeignOwner',where,'original Workflow coordination binding required');
 owner.assertCurrent();
}

export function createCommerceWorkflowCoordinationBindingV1(
 sources:CoreCommerceSourceOwner,capture:CoreCommerceSourceCapture,
 stage:CoreCommerceStageSourceOwner,source:CommerceSourceHandle,workflowId:string,
):CommerceWorkflowCoordinationBindingV1 {
 assertCoreCommerceSourceOwner(sources);assertCoreCommerceStageSourceOwner(stage);
 const captured=sources.inspect(capture),staged=stage.inspect(source);
 if(captured.capture_sha256!==staged.source_sha256)fail('ForeignOwner',where,'Workflow and stage require the same original capture');
 const paths=new Set(captured.reconstruction.modules.map(m=>m.path));
 const texts=captured.files.filter(f=>paths.has(f.path)),assets=captured.files.filter(f=>f.path.endsWith('.json'));
 const audit=checkCoreCommerceWorkflowSources(texts,assets),selected=audit.workflows.filter(w=>w.name===workflowId);
 if(selected.length!==1)fail('UnknownReference',where,'one checked original Workflow required');
 const workflow=selected[0]!;
 const types=createCoreValueTypes(captured.reconstruction),catalog=createCoreContextCatalog(types,assets);
 if(workflow.parameters.length!==1||workflow.parameters[0]!.type.kind!=='record')
  fail('UnsupportedCapability',where,'selected Workflow ingress requires one original Event input');
 const outboxes=[...types.declarations.values()].filter(d=>d.surface==='Entity'&&
  captured.reconstruction.ownership.some(o=>o.declaration===d.id&&o.service===workflow.input_producer)&&
  d.identity.length===1&&d.identity[0]==='eventId'&&
  d.fields.some(f=>f.name==='event'&&sameCoreValueType(types.type(d.module,f.type,f.span),workflow.parameters[0]!.type))&&
  d.fields.some(f=>f.name==='eventId')&&d.fields.some(f=>f.name==='state')&&d.fields.some(f=>f.name==='version'));
 if(outboxes.length!==1)fail('MissingMapping',where,'one original producer outbox for the Workflow Event is required');
 const application=[...types.declarations.values()].filter(d=>d.interface_kind==='application-composition');
 if(application.length!==1)fail('InvalidContract',where,'one original application composition required');
 const value=catalog.asset(application[0]!,['coordination-contract'])?.value;
 if(!value||typeof value!=='object'||Array.isArray(value))fail('MissingMapping',where,'source coordination contract required');
 const coordination=(value as Record<string,unknown>).coordination;
 if(!coordination||typeof coordination!=='object'||Array.isArray(coordination))fail('MissingMapping',where,'source coordination declaration required');
 const c=coordination as Record<string,unknown>,selectors=c.schema_selectors;
 if(c.owner_service!==workflow.owner||!selectors||typeof selectors!=='object'||Array.isArray(selectors))
  fail('InvalidContract',where,'Workflow owner and selected coordination service must match');
 const s=selectors as Record<string,unknown>;
 const inbox=s.inbox,schedule=s.schedule,journal=s.journal,receipt=s.receipt;
 for(const [name,id,kind] of [['inbox',inbox,'Entity'],['schedule',schedule,'Entity'],['journal',journal,'Entity'],['receipt',receipt,'ValueObject']] as const){
  if(typeof id!=='string'||!id.length)fail('MissingMapping',where,'source coordination '+name+' selector required');
  const declaration=types.declarations.get(id);
  if(!declaration||declaration.surface!==kind)fail('TypeMismatch',where,'source coordination '+name+' requires '+kind);
  const owned=captured.reconstruction.ownership.find(o=>o.declaration===id);
  if(owned?.category!=='coordination')fail('InvalidContract',where,'technical selector must be an application coordination declaration');
 }
 // The selected native family writes these exact records. A selector naming an
 // Entity is insufficient if its keys or field types no longer match those
 // writes; check the source ABI before any ingress or worker claim is issued.
 const selectedRecord=(id:unknown)=>types.declarations.get(id as string)!;
 const recordFields=(declaration:CoreCommerceDeclaration)=>new Map(declaration.fields.map(field=>[
  field.name,types.type(declaration.module,field.type,field.span),
 ] as const));
 const expectRecord=(declaration:CoreCommerceDeclaration,identity:readonly string[],immutable:readonly string[],expected:Readonly<Record<string,CoreValueType>>)=>{
  const actual=recordFields(declaration),names=Object.keys(expected);
  if(declaration.identity.join('\0')!==identity.join('\0')||declaration.immutable==='all'||
   declaration.immutable.join('\0')!==immutable.join('\0')||actual.size!==names.length||
   names.some(name=>!actual.has(name)||!sameCoreValueType(actual.get(name)!,expected[name]!)))
   fail('InvalidContract',where,'selected coordination record schema differs from its native ABI: '+declaration.id);
 };
 const receiptDecl=selectedRecord(receipt),inboxDecl=selectedRecord(inbox),scheduleDecl=selectedRecord(schedule),journalDecl=selectedRecord(journal);
 const receiptFields=recordFields(receiptDecl),inboxFields=recordFields(inboxDecl),scheduleFields=recordFields(scheduleDecl),journalFields=recordFields(journalDecl);
 const key=receiptFields.get('consumerEntryId'),occurrence=receiptFields.get('occurrenceId'),orderId=receiptFields.get('orderId'),fingerprint=inboxFields.get('eventFingerprint');
 const scheduleState=scheduleFields.get('state'),journalPhase=journalFields.get('phase');
 const observation=workflow.drivers.find(driver=>driver.kind==='observation')?.call.arguments.find(argument=>argument.parameter==='observation')?.value.type;
 if(!key||!occurrence||!orderId||!fingerprint||!scheduleState||!journalPhase||!observation||
  !coreStringDomain(key,types)||!coreStringDomain(occurrence,types)||!coreStringDomain(orderId,types)||!coreStringDomain(fingerprint,types)||
  !sameCoreValueType(orderId,workflow.correlation.type)||scheduleState.kind!=='enum'||journalPhase.kind!=='enum')
  fail('InvalidContract',where,'source Workflow coordination scalar and Enum types required');
 const variants=(type:CoreValueType,required:readonly string[])=>{
  if(type.kind!=='enum')fail('InvalidContract',where,'technical state must be an Enum');
  const declaration=types.declarations.get(type.name),actual=new Set(declaration?.variants.map(value=>value.name));
  if(required.some(name=>!actual.has(name)))fail('InvalidContract',where,'technical state Enum lacks a native phase');
 };
 variants(scheduleState,['Ready','Claimed','Suspended','Finished']);
 variants(journalPhase,['Prepared','Dispatched','Observed','Indeterminate']);
 const version:CoreValueType={kind:'UInt64'},optionalKey:CoreValueType={kind:'optional',value:key},optionalObservation:CoreValueType={kind:'optional',value:observation};
 expectRecord(receiptDecl,[],[],{consumerEntryId:key,occurrenceId:occurrence,orderId});
 expectRecord(inboxDecl,['consumerEntryId','occurrenceId'],['consumerEntryId','occurrenceId','eventFingerprint','orderId','receipt'],
  {consumerEntryId:key,occurrenceId:occurrence,eventFingerprint:fingerprint,orderId,receipt:{kind:'record',name:receiptDecl.id},version});
 expectRecord(scheduleDecl,['consumerEntryId','occurrenceId'],['consumerEntryId','occurrenceId','orderId'],
  {consumerEntryId:key,occurrenceId:occurrence,orderId,state:scheduleState,workerOwner:optionalKey,workerEpoch:version,version});
 expectRecord(journalDecl,['consumerEntryId','occurrenceId','stepName','commandId'],
  ['consumerEntryId','occurrenceId','orderId','stepName','commandId','targetEntryId','requestFingerprint'],
  {consumerEntryId:key,occurrenceId:occurrence,orderId,stepName:key,commandId:key,targetEntryId:key,
   requestFingerprint:fingerprint,phase:journalPhase,workerOwner:key,workerEpoch:version,observation:optionalObservation,version});
 const inspection:CommerceWorkflowCoordinationInspectionV1=coreFreeze({workflow,owner_service:workflow.owner,
  source_capture_sha256:captured.capture_sha256,input_outbox_entity:outboxes[0]!.id,inbox_entity:inbox as string,schedule_entity:schedule as string,
  journal_entity:journal as string,receipt_type:receipt as string,
  qualification:'checked-source-workflow-and-technical-record-selectors-only',authority_effect:'none'});
 const current=()=>{
  // inspect validates each distinct original capture; preliminary assertCurrent
  // calls repeated the same physical source walk without adding custody.
  if(stage.inspect(source).source_sha256!==inspection.source_capture_sha256||
     sources.inspect(capture).capture_sha256!==inspection.source_capture_sha256)
   fail('StaleOwner',where,'original Workflow coordination source changed');
 };
 const owner:CommerceWorkflowCoordinationBindingV1=Object.freeze({inspect(){current();return inspection;},assertCurrent:current});
 owners.add(owner);current();return owner;
}
