/** Optional Alloy view of one checked original Core Commerce application.
 * It preserves selected source/profile identities and the Workflow's declared
 * branch topology. Guards, effects, recovery, Auth, and SQLite are outside this
 * structural model; generating it neither needs claims nor runs a solver.
 * Open Questions: docs/COMMERCE-CONTRACTS.md#open-questions. */
import {createHash} from 'node:crypto';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {dataDigest} from '../profile-engine/contracts.js';
import {coreFreeze} from './commerce-core-syntax.js';
import {pinCoreImplementation} from './commerce-core-physical.js';
import {assertCoreCommerceSourceOwner,type CoreCommerceSourceOwner,type CoreCommerceSourceCapture} from './commerce-core-source-owner.js';
import {assertCoreCommerceSemanticOwner,type CoreCommerceSemanticOwner,type CoreCommerceSemanticCapture} from './commerce-core-semantic-owner.js';
import {assertCommerceWorkflowCoordinationBindingV1,type CommerceWorkflowCoordinationBindingV1} from './commerce-workflow-coordination-binding-v1.js';
import {assertCommerceApplicationAssemblyV1,type CommerceApplicationAssemblyV1} from './commerce-application-assembly-v1.js';
import {projectCoreServiceTopologyV1} from '../generic/core-topology-bridge.js';

export class CoreCommerceFormalStructureErrorV1 extends Error {
 constructor(readonly code:'InvalidSource'|'UnsupportedStructure'|'InvalidModel') {super(code);this.name='CoreCommerceFormalStructureErrorV1';}
}
const bad=(code:CoreCommerceFormalStructureErrorV1['code']):never=>{throw new CoreCommerceFormalStructureErrorV1(code);};
const sha=(value:string)=>createHash('sha256').update(value).digest('hex');
const extension=path.extname(fileURLToPath(import.meta.url));
const codePin=pinCoreImplementation(import.meta.url,['../generic/core-topology-bridge'+extension]);
const sorted=(values:Iterable<string>)=>[...values].sort((a,b)=>a.localeCompare(b));
const union=(values:readonly string[])=>values.length?values.join(' + '):'none';
const atom=(prefix:string,index:number)=>prefix+String(index);

type Service=Readonly<{atom:string;id:string}>;
type Entry=Readonly<{atom:string;id:string;service:string;target:string;permission:string;contract_sha256:string}>;
type Event=Readonly<{atom:string;id:string}>;
type PersistedState=Readonly<{atom:string;name:string}>;
type ControlTarget=Readonly<{atom:string;name:string}>;
type Step=Readonly<{atom:string;name:string;kind:'remote'|'local-observation'|'review';entry:string|null;next:string|null}>;
type Terminal=Readonly<{atom:string;name:string}>;
type Branch=Readonly<{atom:string;from:string;channel:string;variant:string|null;action:'step'|'finish'|'suspend'|'resume'|'stop-this-worker';target:string|null;suspend_category:'control'|'persisted-state'|null;observes:boolean}>;
type Resume=Readonly<{atom:string;from_state:string;action:'step'|'finish'|'suspend'|'resume'|'stop-this-worker';target:string|null;suspend_category:'control'|'persisted-state'|null;guarded:boolean}>;

export interface CoreCommerceFormalStructureV1 {
 readonly schema_version:'craft.core-commerce-formal-structure/v1-candidate';
 readonly language:'alloy';
 readonly scope:'selected-original-application-services-entries-events-and-one-workflow-branch-topology';
 readonly qualification:'checked-source-and-selected-profile-structural-projection-only';
 readonly application:string;readonly workflow:string;
 readonly source_capture_sha256:string;readonly executable_sha256:string;readonly family_sha256:string;readonly exporter_code_sha256:string;
 readonly workflow_contract_sha256:string;readonly structure_sha256:string;
 readonly services:readonly Service[];readonly entries:readonly Entry[];readonly events:readonly Event[];
 readonly persisted_states:readonly PersistedState[];readonly control_targets:readonly ControlTarget[];
 readonly steps:readonly Step[];readonly terminals:readonly Terminal[];readonly branches:readonly Branch[];readonly resume:readonly Resume[];
 readonly alloy:string;readonly alloy_sha256:string;
 readonly unsupported_formal_languages:readonly ['tla+'];
 readonly authority_effect:'none';
 readonly claim_ceiling:'selected-checked-structure-only-no-guard-effect-auth-event-delivery-recovery-sqlite-runtime-or-solver-proof';
}

function renderAlloy(model:Pick<CoreCommerceFormalStructureV1,'services'|'entries'|'events'|'persisted_states'|'control_targets'|'steps'|'terminals'|'branches'|'resume'>,
 ownerService:string,ingress:string,drivers:Readonly<{snapshot:string;claim:string;observation:string}>,
 provenance:Readonly<{source:string;executable:string;family:string;workflow:string;exporter:string;structure:string}>):string {
 const serviceAtom=new Map(model.services.map(row=>[row.id,row.atom]));
 const entryAtom=new Map(model.entries.map(row=>[row.id,row.atom]));
 const stepAtom=new Map(model.steps.map(row=>[row.name,row.atom]));
 const terminalAtom=new Map(model.terminals.map(row=>[row.name,row.atom]));
 const stateAtom=new Map(model.persisted_states.map(row=>[row.name,row.atom]));
 const controlAtom=new Map(model.control_targets.map(row=>[row.name,row.atom]));
 const channels=sorted(new Set(model.branches.map(row=>row.channel))),
  variants=sorted(new Set(model.branches.flatMap(row=>row.variant===null?[]:[row.variant])));
 const channelAtom=new Map(channels.map((value,index)=>[value,atom('C',index)]));
 const variantAtom=new Map(variants.map((value,index)=>[value,atom('X',index)]));
 const actionAtom={step:'StepAction',finish:'FinishAction',suspend:'SuspendAction',resume:'ResumeAction','stop-this-worker':'StopAction'} as const;
 const rows=[
  'module CoreCommerceCheckedStructure',
  `// source_capture_sha256: ${provenance.source}`,
  `// executable_sha256: ${provenance.executable}`,
  `// family_sha256: ${provenance.family}`,
  `// workflow_contract_sha256: ${provenance.workflow}`,
  `// exporter_code_sha256: ${provenance.exporter}`,
  `// structure_sha256: ${provenance.structure}`,
  '// Source names and exact relations are carried by the adjacent model metadata.',
  '// This finite model contains structure only; no behavioral proof is claimed.',
  'abstract sig Service { entries: set Entry }',
  'abstract sig Entry {}',
  'abstract sig Event {}',
  'abstract sig Workflow { owner: one Service, ingress: one Entry, snapshot: one Entry, claim: one Entry, observation: one Entry, workflowSteps: set Step, resumes: set ResumeSelector }',
  'abstract sig PersistedState {}',
  'abstract sig ControlTarget {}',
  'abstract sig Step { kind: one StepKind, entry: lone Entry, nextStep: lone Step, branches: set Branch }',
  'abstract sig StepKind {}',
  'one sig RemoteStep, ObservationStep, ReviewStep extends StepKind {}',
  'abstract sig Terminal {}',
  'abstract sig Branch { channel: one OutcomeChannel, variant: lone OutcomeVariant, action: one ActionKind, toStep: lone Step, toTerminal: lone Terminal, toState: lone PersistedState, toControl: lone ControlTarget, observationRequired: one ObservationFlag }',
  'abstract sig ResumeSelector { fromState: one PersistedState, action: one ActionKind, toStep: lone Step, toTerminal: lone Terminal, toState: lone PersistedState, toControl: lone ControlTarget, guardPresent: one GuardFlag }',
  'abstract sig OutcomeChannel {}',
  'abstract sig OutcomeVariant {}',
  'abstract sig ActionKind {}',
  'one sig StepAction, FinishAction, SuspendAction, ResumeAction, StopAction extends ActionKind {}',
  'abstract sig ObservationFlag {}',
  'one sig Required, NotRequired extends ObservationFlag {}',
  'abstract sig GuardFlag {}',
  'one sig GuardPresent, GuardAbsent extends GuardFlag {}',
  ...model.services.map(row=>`one sig ${row.atom} extends Service {}`),
  ...model.entries.map(row=>`one sig ${row.atom} extends Entry {}`),
  ...model.events.map(row=>`one sig ${row.atom} extends Event {}`),
  'one sig W0 extends Workflow {}',
  ...model.persisted_states.map(row=>`one sig ${row.atom} extends PersistedState {}`),
  ...model.control_targets.map(row=>`one sig ${row.atom} extends ControlTarget {}`),
  ...model.steps.map(row=>`one sig ${row.atom} extends Step {}`),
  ...model.terminals.map(row=>`one sig ${row.atom} extends Terminal {}`),
  ...model.branches.map(row=>`one sig ${row.atom} extends Branch {}`),
  ...model.resume.map(row=>`one sig ${row.atom} extends ResumeSelector {}`),
  ...channels.map(value=>`one sig ${channelAtom.get(value)!} extends OutcomeChannel {}`),
  ...variants.map(value=>`one sig ${variantAtom.get(value)!} extends OutcomeVariant {}`),
  'fact ExactCheckedStructure {',
  `  Service = ${union(model.services.map(row=>row.atom))}`,
  `  Entry = ${union(model.entries.map(row=>row.atom))}`,
  `  Event = ${union(model.events.map(row=>row.atom))}`,
  '  Workflow = W0',
  `  PersistedState = ${union(model.persisted_states.map(row=>row.atom))}`,
  `  ControlTarget = ${union(model.control_targets.map(row=>row.atom))}`,
  `  Step = ${union(model.steps.map(row=>row.atom))}`,
  `  Terminal = ${union(model.terminals.map(row=>row.atom))}`,
  `  Branch = ${union(model.branches.map(row=>row.atom))}`,
  `  ResumeSelector = ${union(model.resume.map(row=>row.atom))}`,
  `  OutcomeChannel = ${union(channels.map(value=>channelAtom.get(value)!))}`,
  `  OutcomeVariant = ${union(variants.map(value=>variantAtom.get(value)!))}`,
  ...model.services.map(service=>`  ${service.atom}.entries = ${union(model.entries.filter(entry=>entry.service===service.id).map(entry=>entry.atom))}`),
  `  W0.owner = ${serviceAtom.get(ownerService)!}`,
  `  W0.ingress = ${entryAtom.get(ingress)!}`,
  `  W0.snapshot = ${entryAtom.get(drivers.snapshot)!}`,
  `  W0.claim = ${entryAtom.get(drivers.claim)!}`,
  `  W0.observation = ${entryAtom.get(drivers.observation)!}`,
  `  W0.workflowSteps = ${union(model.steps.map(row=>row.atom))}`,
  `  W0.resumes = ${union(model.resume.map(row=>row.atom))}`,
  ...model.steps.flatMap(step=>[
   `  ${step.atom}.kind = ${{remote:'RemoteStep','local-observation':'ObservationStep',review:'ReviewStep'}[step.kind]}`,
   `  ${step.atom}.entry = ${step.entry?entryAtom.get(step.entry)!:'none'}`,
   `  ${step.atom}.nextStep = ${step.next?stepAtom.get(step.next)!:'none'}`,
   `  ${step.atom}.branches = ${union(model.branches.filter(branch=>branch.from===step.name).map(branch=>branch.atom))}`,
  ]),
  ...model.branches.flatMap(branch=>[
   `  ${branch.atom}.channel = ${channelAtom.get(branch.channel)!}`,
   `  ${branch.atom}.variant = ${branch.variant===null?'none':variantAtom.get(branch.variant)!}`,
   `  ${branch.atom}.action = ${actionAtom[branch.action]}`,
   `  ${branch.atom}.toStep = ${branch.action==='step'?stepAtom.get(branch.target!)!:'none'}`,
   `  ${branch.atom}.toTerminal = ${branch.action==='finish'?terminalAtom.get(branch.target!)!:'none'}`,
   `  ${branch.atom}.toState = ${branch.action==='suspend'&&branch.suspend_category==='persisted-state'?stateAtom.get(branch.target!)!:'none'}`,
   `  ${branch.atom}.toControl = ${branch.action==='suspend'&&branch.suspend_category==='control'?controlAtom.get(branch.target!)!:'none'}`,
   `  ${branch.atom}.observationRequired = ${branch.observes?'Required':'NotRequired'}`,
  ]),
  ...model.resume.flatMap(row=>[
   `  ${row.atom}.fromState = ${stateAtom.get(row.from_state)!}`,
   `  ${row.atom}.action = ${actionAtom[row.action]}`,
   `  ${row.atom}.toStep = ${row.action==='step'?stepAtom.get(row.target!)!:'none'}`,
   `  ${row.atom}.toTerminal = ${row.action==='finish'?terminalAtom.get(row.target!)!:'none'}`,
   `  ${row.atom}.toState = ${row.action==='suspend'&&row.suspend_category==='persisted-state'?stateAtom.get(row.target!)!:'none'}`,
   `  ${row.atom}.toControl = ${row.action==='suspend'&&row.suspend_category==='control'?controlAtom.get(row.target!)!:'none'}`,
   `  ${row.atom}.guardPresent = ${row.guarded?'GuardPresent':'GuardAbsent'}`,
  ]),
  '}',
  'assert EveryEntryHasExactlyOneService { all e: Entry | one s: Service | e in s.entries }',
  'assert EveryBranchHasExactlyOneStep { all b: Branch | one s: Step | b in s.branches }',
  'assert BranchTargetsMatchAction { all b: Branch |',
  '  (b.action = StepAction implies (one b.toStep and no b.toTerminal and no b.toState and no b.toControl)) and',
  '  (b.action = FinishAction implies (one b.toTerminal and no b.toStep and no b.toState and no b.toControl)) and',
  '  (b.action = SuspendAction implies (((one b.toState and no b.toControl) or (one b.toControl and no b.toState)) and no b.toStep and no b.toTerminal)) and',
  '  (b.action in ResumeAction + StopAction implies (no b.toStep and no b.toTerminal and no b.toState and no b.toControl))',
  '}',
  'assert EveryResumeHasOneWorkflow { all r: ResumeSelector | one w: Workflow | r in w.resumes }',
  'assert ResumeTargetsMatchAction { all r: ResumeSelector |',
  '  (r.action = StepAction implies (one r.toStep and no r.toTerminal and no r.toState and no r.toControl)) and',
  '  (r.action = FinishAction implies (one r.toTerminal and no r.toStep and no r.toState and no r.toControl)) and',
  '  (r.action = SuspendAction implies (((one r.toState and no r.toControl) or (one r.toControl and no r.toState)) and no r.toStep and no r.toTerminal)) and',
  '  (r.action in ResumeAction + StopAction implies (no r.toStep and no r.toTerminal and no r.toState and no r.toControl))',
  '}',
  `run {} for ${Math.max(5,model.entries.length,model.steps.length,model.branches.length,model.events.length,model.terminals.length,model.persisted_states.length,model.control_targets.length,model.resume.length)}`,
  `check EveryEntryHasExactlyOneService for ${Math.max(5,model.entries.length,model.steps.length,model.branches.length,model.events.length,model.terminals.length,model.persisted_states.length,model.control_targets.length,model.resume.length)}`,
  `check EveryBranchHasExactlyOneStep for ${Math.max(5,model.entries.length,model.steps.length,model.branches.length,model.events.length,model.terminals.length,model.persisted_states.length,model.control_targets.length,model.resume.length)}`,
  `check BranchTargetsMatchAction for ${Math.max(5,model.entries.length,model.steps.length,model.branches.length,model.events.length,model.terminals.length,model.persisted_states.length,model.control_targets.length,model.resume.length)}`,
  `check EveryResumeHasOneWorkflow for ${Math.max(5,model.entries.length,model.steps.length,model.branches.length,model.events.length,model.terminals.length,model.persisted_states.length,model.control_targets.length,model.resume.length)}`,
  `check ResumeTargetsMatchAction for ${Math.max(5,model.entries.length,model.steps.length,model.branches.length,model.events.length,model.terminals.length,model.persisted_states.length,model.control_targets.length,model.resume.length)}`,
  '',
 ];
 return rows.join('\n');
}

/** All four inputs are original branded owners. A copied topology, workflow,
 * source hash, profile DTO, or optional claim is never accepted as authority. */
export function exportCoreCommerceFormalStructureV1(
 sources:CoreCommerceSourceOwner,capture:CoreCommerceSourceCapture,
 semantics:CoreCommerceSemanticOwner,semantic:CoreCommerceSemanticCapture,
 binding:CommerceWorkflowCoordinationBindingV1,
 assembly:CommerceApplicationAssemblyV1,
):CoreCommerceFormalStructureV1 {
 assertCoreCommerceSourceOwner(sources);assertCoreCommerceSemanticOwner(semantics);
 assertCommerceWorkflowCoordinationBindingV1(binding);assertCommerceApplicationAssemblyV1(assembly);
 codePin.assertCurrent();
 semantics.assertSource(semantic,capture);
 const selected=sources.inspect(capture),checked=semantics.inspect(semantic),workflow=binding.inspect(),application=assembly.inspect();
 const topology=projectCoreServiceTopologyV1(sources,capture,semantics,semantic);
 if(selected.capture_sha256!==checked.source_capture_sha256||checked.source_capture_sha256!==workflow.source_capture_sha256||
  workflow.source_capture_sha256!==application.source_capture_sha256||application.application!==topology.application||
  checked.executable_sha256!==topology.executable_sha256||
  sorted(topology.services.map(row=>row.id)).join('\0')!==sorted(application.services).join('\0'))bad('InvalidSource');
 const selectedWorkflow=topology.workflows.filter(row=>row.id===workflow.workflow.name);
 if(selectedWorkflow.length!==1||workflow.workflow.owner!==workflow.owner_service||
  !topology.services.some(row=>row.id===workflow.owner_service))bad('InvalidSource');
 const declared=checked.workflows.filter(row=>row.workflow.module+'.'+row.workflow.name===workflow.workflow.name);
 if(declared.length!==1||dataDigest(declared[0])!==selectedWorkflow[0]!.contract_sha256)bad('InvalidSource');
 const entries=topology.entries.slice().sort((a,b)=>a.id.localeCompare(b.id));
 const byEntry=new Map(entries.map(row=>[row.id,row]));
 const requireEntry=(id:string,target:string,role:'Operation'|'Query'|'Workflow')=>{
  const entry=byEntry.get(id);if(!entry||entry.target!==target||entry.target_role!==role)bad('InvalidSource');return entry;
 };
 requireEntry(workflow.workflow.input_entry,workflow.workflow.name,'Workflow');
 const drivers=workflow.workflow.drivers;
 if(drivers.length!==3||new Set(drivers.map(row=>row.kind)).size!==3)bad('UnsupportedStructure');
 const byDriver=new Map(drivers.map(row=>[row.kind,row]));
 for(const row of drivers)requireEntry(row.call.entry,row.call.target,row.call.role);
 const steps=workflow.workflow.steps;
 if(steps.length<1||steps.length>64||new Set(steps.map(row=>row.name)).size!==steps.length||
  workflow.workflow.terminals.length>16||new Set(workflow.workflow.terminals.map(row=>row.name)).size!==workflow.workflow.terminals.length)
  bad('UnsupportedStructure');
 const stepNames=new Set(steps.map(row=>row.name)),terminalNames=new Set(workflow.workflow.terminals.map(row=>row.name));
 const resume=workflow.workflow.resume;
 const stateNames=sorted(new Set([...resume.map(row=>row.state),
  ...steps.flatMap(row=>row.kind==='remote'?row.branches.filter(branch=>branch.action.kind==='suspend'&&branch.action.category==='persisted-state')
   .map(branch=>branch.action.kind==='suspend'?branch.action.target:''):[]),
  ...resume.filter(row=>row.action.kind==='suspend'&&row.action.category==='persisted-state')
   .map(row=>row.action.kind==='suspend'?row.action.target:'')]));
 const controlNames=sorted(new Set([...steps.flatMap(row=>row.kind==='remote'?row.branches.filter(branch=>branch.action.kind==='suspend'&&branch.action.category==='control')
  .map(branch=>branch.action.kind==='suspend'?branch.action.target:''):[]),
  ...resume.filter(row=>row.action.kind==='suspend'&&row.action.category==='control')
   .map(row=>row.action.kind==='suspend'?row.action.target:'')]));
 if(stateNames.length>64||controlNames.length>64||resume.length>128)bad('UnsupportedStructure');
 const checkedAction=(action:{readonly kind:'step'|'finish'|'suspend'|'resume'|'stop-this-worker';readonly target?:string;readonly category?:'control'|'persisted-state'})=>{
  if(action.kind==='step'&&!stepNames.has(action.target??'')||
   action.kind==='finish'&&!terminalNames.has(action.target??'')||
   action.kind==='suspend'&&action.category==='persisted-state'&&!stateNames.includes(action.target??'')||
   action.kind==='suspend'&&action.category==='control'&&!controlNames.includes(action.target??'')||
   action.kind==='suspend'&&!['control','persisted-state'].includes(action.category??''))bad('InvalidSource');
  return action.kind==='step'||action.kind==='finish'||action.kind==='suspend'?action.target!:null;
 };
 const serviceRows=topology.services.slice().sort((a,b)=>a.id.localeCompare(b.id)).map((row,i)=>({atom:atom('S',i),id:row.id}));
 const entryRows=entries.map((row,i)=>({atom:atom('E',i),id:row.id,service:row.service,target:row.target,
  permission:row.permission,contract_sha256:row.contract_sha256}));
 const eventRows=topology.events.slice().sort((a,b)=>a.id.localeCompare(b.id)).map((row,i)=>({atom:atom('V',i),id:row.id}));
 const stateRows:PersistedState[]=stateNames.map((name,i)=>({atom:atom('P',i),name}));
 const controlRows:ControlTarget[]=controlNames.map((name,i)=>({atom:atom('K',i),name}));
 const stepRows:Step[]=steps.map((row,i)=>{
  if(row.kind==='remote')requireEntry(row.call.entry,row.call.target,row.call.role);
  if(row.kind==='local-observation'&&!stepNames.has(row.next))bad('InvalidSource');
  return {atom:atom('T',i),name:row.name,kind:row.kind,
   entry:row.kind==='remote'?row.call.entry:null,next:row.kind==='local-observation'?row.next:null};
 });
 const terminalRows=workflow.workflow.terminals.map((row,i)=>({atom:atom('Z',i),name:row.name}));
 const branchRows:Branch[]=steps.flatMap(row=>row.kind!=='remote'?[]:row.branches.map(branch=>{
  const action=branch.action;
  return {atom:'',from:row.name,channel:branch.channel,variant:branch.variant,action:action.kind,
   target:checkedAction(action),suspend_category:action.kind==='suspend'?action.category:null,
   observes:branch.observe!==null};
 })).map((row,i)=>({...row,atom:atom('B',i)}));
 const resumeRows:Resume[]=resume.map((row,i)=>({atom:atom('R',i),from_state:row.state,
  action:row.action.kind,target:checkedAction(row.action),
  suspend_category:row.action.kind==='suspend'?row.action.category:null,guarded:row.guard!==null}));
 if(branchRows.length>256||entryRows.length>128||eventRows.length>128||serviceRows.length>64)bad('UnsupportedStructure');
 const structural={services:serviceRows,entries:entryRows,events:eventRows,persisted_states:stateRows,control_targets:controlRows,
  steps:stepRows,terminals:terminalRows,branches:branchRows,resume:resumeRows};
 const structureDigest=dataDigest(structural);
 const alloy=renderAlloy(structural,workflow.owner_service,workflow.workflow.input_entry,{
  snapshot:byDriver.get('snapshot')!.call.entry,claim:byDriver.get('claim')!.call.entry,
  observation:byDriver.get('observation')!.call.entry},{
   source:selected.capture_sha256,executable:checked.executable_sha256,family:application.family_sha256,
   workflow:selectedWorkflow[0]!.contract_sha256,exporter:codePin.sha256,structure:structureDigest});
 const result:CoreCommerceFormalStructureV1=coreFreeze({
  schema_version:'craft.core-commerce-formal-structure/v1-candidate' as const,language:'alloy' as const,
  scope:'selected-original-application-services-entries-events-and-one-workflow-branch-topology' as const,
  qualification:'checked-source-and-selected-profile-structural-projection-only' as const,
  application:application.application,workflow:workflow.workflow.name,
  source_capture_sha256:selected.capture_sha256,executable_sha256:checked.executable_sha256,
  family_sha256:application.family_sha256,exporter_code_sha256:codePin.sha256,
  workflow_contract_sha256:selectedWorkflow[0]!.contract_sha256,
  structure_sha256:structureDigest,...structural,alloy,alloy_sha256:sha(alloy),
  unsupported_formal_languages:['tla+'] as const,authority_effect:'none' as const,
  claim_ceiling:'selected-checked-structure-only-no-guard-effect-auth-event-delivery-recovery-sqlite-runtime-or-solver-proof' as const,
 });
 codePin.assertCurrent();sources.assertCurrent(capture);semantics.assertCurrent(semantic);binding.assertCurrent();assembly.assertCurrent();
 return result;
}

export function assertCoreCommerceFormalStructureCurrentV1(
 sources:CoreCommerceSourceOwner,capture:CoreCommerceSourceCapture,
 semantics:CoreCommerceSemanticOwner,semantic:CoreCommerceSemanticCapture,
 binding:CommerceWorkflowCoordinationBindingV1,assembly:CommerceApplicationAssemblyV1,
 model:CoreCommerceFormalStructureV1,
):void {
 if(!model||typeof model!=='object'||typeof model.alloy!=='string'||typeof model.alloy_sha256!=='string')bad('InvalidModel');
 const current=exportCoreCommerceFormalStructureV1(sources,capture,semantics,semantic,binding,assembly);
 if(model.alloy_sha256!==sha(model.alloy)||dataDigest(model)!==dataDigest(current))bad('InvalidModel');
}
