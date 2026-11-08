/** Optional finite Alloy projection of an original emitted service inventory.
 * It models only selected emitted structural relationships, not application
 * behavior or a proof of completeness.
 * Open Questions: docs/GENERIC-APPLICATIONS.md#open-questions.
 */
import {createHash} from 'node:crypto';
import {dataDigest} from '../profile-engine/contracts.js';
import {
  assertGenericServiceArtifactOwner,
  type GenericServiceArtifactHandle,
  type GenericServiceArtifactManifest,
  createGenericServiceArtifactOwner,
} from './service-artifact-owner.js';

type Owner = ReturnType<typeof createGenericServiceArtifactOwner>;
type Artifact = Readonly<{atom:string;path:string;sha256:string}>;
type Entry = Readonly<{atom:string;id:string;service:string;interaction:'request-response'|'event';executable:string;manifest:string}>;
type Event = Readonly<{atom:string;id:string;services:readonly string[];descriptors:readonly string[]}>;
type Workflow = Readonly<{atom:string;id:string;service:string;worker:string}>;
type Service = Readonly<{atom:string;id:string;entries:readonly string[];events:readonly string[];workflow:string|null;module:string;runtime:string;graph:string;bridge:string;wiring:string}>;

export interface GenericStructuralAlloyModelV1 {
  readonly schema_version:'craft.generic-structural-alloy/v1-candidate';
  readonly language:'alloy';
  readonly scope:'selected-emitted-service-entry-event-workflow-artifacts';
  readonly qualification:'finite-exact-structural-snapshot-only';
  readonly application_contract_sha256:string;
  readonly source_capture_sha256:string;
  readonly profile_sha256:string;
  readonly executable_semantics_sha256:string;
  readonly inventory_sha256:string;
  readonly services:readonly Service[];
  readonly entries:readonly Entry[];
  readonly events:readonly Event[];
  readonly workflows:readonly Workflow[];
  readonly artifacts:readonly Artifact[];
  readonly missing_complete_application_classes:readonly string[];
  readonly source_manifest_complete_application:boolean;
  readonly alloy:string;
  readonly alloy_sha256:string;
  readonly authority_effect:'none';
  readonly claim_ceiling:'selected-emitted-structure-only-no-runtime-or-complete-application-or-solver-proof';
}

export class GenericStructuralAlloyUnsupportedError extends Error {
  constructor(readonly code:'InvalidInventory'|'InputSpaceBound') {
    super(code);
    this.name='GenericStructuralAlloyUnsupportedError';
  }
}

const hex=/^[0-9a-f]{64}$/;
const sha=(text:string)=>createHash('sha256').update(text).digest('hex');
const reject=(code:GenericStructuralAlloyUnsupportedError['code']):never=>{throw new GenericStructuralAlloyUnsupportedError(code);};
const ordered=(values:Iterable<string>)=>[...values].sort((a,b)=>a<b?-1:a>b?1:0);
const setExpr=(atoms:readonly string[])=>atoms.length?atoms.join(' + '):'none';

function checkedInventory(manifest:GenericServiceArtifactManifest) {
  if(manifest?.schema_version!=='craft.generic-service-artifacts/v1-candidate'||
    !hex.test(manifest.application_contract_sha256)||!hex.test(manifest.source_capture_sha256)||
    !hex.test(manifest.profile_sha256)||!hex.test(manifest.executable_semantics_sha256)||
    !hex.test(manifest.inventory_sha256)||!Array.isArray(manifest.services)||
    !Array.isArray(manifest.files)||!Array.isArray(manifest.missing_complete_application_classes)||
    typeof manifest.complete_application!=='boolean'||manifest.authority_effect!=='none'||
    dataDigest(manifest.files)!==manifest.inventory_sha256)reject('InvalidInventory');
  if(manifest.services.length<1||manifest.services.length>32||manifest.files.length>1024)reject('InputSpaceBound');
  const files=new Map<string,{sha256:string;bytes:number}>();
  for(const file of manifest.files){
    if(!file||typeof file.path!=='string'||!file.path||files.has(file.path)||
      !hex.test(file.sha256)||!Number.isSafeInteger(file.bytes)||file.bytes<0)reject('InvalidInventory');
    files.set(file.path,file);
  }
  const selected=new Map<string,{path:string;sha256:string}>();
  const requireFile=(path:string,expected?:string):string=>{
    const file=files.get(path);
    if(!file)throw new GenericStructuralAlloyUnsupportedError('InvalidInventory');
    if(expected&&file.sha256!==expected)reject('InvalidInventory');
    selected.set(path,{path,sha256:file.sha256});
    return path;
  };
  const rawServices=[...manifest.services].sort((a,b)=>a.service<b.service?-1:a.service>b.service?1:0);
  const serviceIds=new Set<string>(),entryIds=new Set<string>(),workflowIds=new Set<string>();
  const rawEntries:{id:string;service:string;interaction:'request-response'|'event';executable:string;manifest:string}[]=[];
  const eventServices=new Map<string,Set<string>>();
  const rawWorkflows:{id:string;service:string;worker:string}[]=[];
  const rawServiceRows:{id:string;entries:string[];events:string[];workflow:string|null;module:string;runtime:string;graph:string;bridge:string;wiring:string}[]=[];
  for(const row of rawServices){
    if(!row||typeof row.service!=='string'||!row.service||serviceIds.has(row.service)||
      !Array.isArray(row.entries)||!row.entries.length||!Array.isArray(row.event_bindings)||
      !row.directory||!row.directory.startsWith('services/')||
      !hex.test(row.module_sha256)||!hex.test(row.runtime_module_sha256)||
      !hex.test(row.system_graph_sha256)||!hex.test(row.bridge_sha256)||!hex.test(row.wiring_sha256))reject('InvalidInventory');
    serviceIds.add(row.service);
    const module=requireFile(row.directory+'/service.mjs',row.module_sha256);
    const runtime=requireFile(row.directory+'/runtime.mjs',row.runtime_module_sha256);
    const graph=requireFile(row.directory+'/service-system-graph.json',row.system_graph_sha256);
    const bridge=requireFile(row.directory+'/service-business-system-bridge.json',row.bridge_sha256);
    const wiring=requireFile(row.directory+'/service-wiring.json',row.wiring_sha256);
    const entries:string[]=[];
    for(const entry of row.entries){
      if(!entry||entry.service!==row.service||typeof entry.entry!=='string'||!entry.entry||entryIds.has(entry.entry)||
        !['request-response','event'].includes(entry.interaction)||!entry.directory.startsWith(row.directory+'/entries/')||
        !hex.test(entry.manifest_sha256))reject('InvalidInventory');
      entryIds.add(entry.entry);entries.push(entry.entry);
      rawEntries.push({id:entry.entry,service:row.service,interaction:entry.interaction,
        executable:requireFile(entry.directory+'/application.mjs'),
        manifest:requireFile(entry.directory+'/manifest.json',entry.manifest_sha256)});
    }
    const events=ordered(row.event_bindings);
    if(events.length!==new Set(events).size||events.some(id=>!id))reject('InvalidInventory');
    for(const id of events){let owners=eventServices.get(id);if(!owners){owners=new Set();eventServices.set(id,owners);}owners.add(row.service);}
    let workflow:string|null=null;
    if(row.workflow!==null){
      const workerSha=row.worker_module_sha256;
      if(typeof row.workflow!=='string'||!row.workflow||workflowIds.has(row.workflow)||!workerSha||!hex.test(workerSha))
        throw new GenericStructuralAlloyUnsupportedError('InvalidInventory');
      workflowIds.add(row.workflow);workflow=row.workflow;
      rawWorkflows.push({id:workflow,service:row.service,worker:requireFile(row.directory+'/worker.mjs',workerSha)});
    }else if(row.worker_module_sha256!==null)reject('InvalidInventory');
    rawServiceRows.push({id:row.service,entries:ordered(entries),events,workflow,module,runtime,graph,bridge,wiring});
  }
  if(rawEntries.length>128||eventServices.size>128||rawWorkflows.length>32||selected.size>512)reject('InputSpaceBound');
  const artifacts=ordered(selected.keys()).map((path,index)=>Object.freeze({atom:`A${index}`,path,sha256:selected.get(path)!.sha256}));
  const atomByPath=new Map(artifacts.map(item=>[item.path,item.atom]));
  const entries=rawEntries.sort((a,b)=>a.id<b.id?-1:a.id>b.id?1:0).map((row,index)=>Object.freeze({atom:`E${index}`,id:row.id,service:row.service,interaction:row.interaction,executable:atomByPath.get(row.executable)!,manifest:atomByPath.get(row.manifest)!}));
  const wiringByService=new Map(rawServiceRows.map(row=>[row.id,row.wiring]));
  const events=ordered(eventServices.keys()).map((id,index)=>{
    const services=ordered(eventServices.get(id)!);
    const descriptors=services.map(service=>atomByPath.get(wiringByService.get(service)!)!);
    return Object.freeze({atom:`B${index}`,id,services:Object.freeze(services),descriptors:Object.freeze(descriptors)});
  });
  const workflows=rawWorkflows.sort((a,b)=>a.id<b.id?-1:a.id>b.id?1:0).map((row,index)=>Object.freeze({atom:`W${index}`,id:row.id,service:row.service,worker:atomByPath.get(row.worker)!}));
  const services=rawServiceRows.map((row,index)=>Object.freeze({atom:`S${index}`,id:row.id,
    entries:Object.freeze(row.entries.map(id=>entries.find(entry=>entry.id===id)!.atom)),
    events:Object.freeze(row.events.map(id=>events.find(event=>event.id===id)!.atom)),
    workflow:row.workflow?workflows.find(item=>item.id===row.workflow)!.atom:null,
    module:atomByPath.get(row.module)!,runtime:atomByPath.get(row.runtime)!,graph:atomByPath.get(row.graph)!,
    bridge:atomByPath.get(row.bridge)!,wiring:atomByPath.get(row.wiring)!}));
  return {services,entries,events,workflows,artifacts};
}

export function exportGenericStructuralAlloyModel(owner:Owner,handle:GenericServiceArtifactHandle):GenericStructuralAlloyModelV1 {
  assertGenericServiceArtifactOwner(owner);
  const manifest=owner.inspect(handle),snapshot=checkedInventory(manifest);
  const scope=Math.max(1,snapshot.services.length,snapshot.entries.length,snapshot.events.length,snapshot.workflows.length,snapshot.artifacts.length);
  const lines=[
    '// Finite projection of one original checked emitted service inventory.',
    `// application_contract_sha256 ${manifest.application_contract_sha256}`,
    `// source_capture_sha256 ${manifest.source_capture_sha256}`,
    `// profile_sha256 ${manifest.profile_sha256}`,
    `// executable_semantics_sha256 ${manifest.executable_semantics_sha256}`,
    `// inventory_sha256 ${manifest.inventory_sha256}`,
    ...snapshot.services.map(item=>`// ${item.atom} service_id_sha256 ${sha(item.id)}`),
    ...snapshot.entries.map(item=>`// ${item.atom} entry_id_sha256 ${sha(item.id)}`),
    ...snapshot.events.map(item=>`// ${item.atom} event_binding_id_sha256 ${sha(item.id)}`),
    ...snapshot.workflows.map(item=>`// ${item.atom} workflow_id_sha256 ${sha(item.id)}`),
    ...snapshot.artifacts.map(item=>`// ${item.atom} artifact_path_sha256 ${sha(item.path)} artifact_content_sha256 ${item.sha256}`),
    'abstract sig Service { entries: set Entry, eventBindings: set EventBinding, workflow: lone Workflow, serviceModule: one Artifact, runtimeModule: one Artifact, systemGraph: one Artifact, bridge: one Artifact, wiring: one Artifact }',
    'abstract sig Entry { executable: one Artifact, sourceManifest: one Artifact }',
    'abstract sig EventBinding { descriptors: set Artifact }',
    'abstract sig Workflow { worker: one Artifact }',
    'abstract sig Artifact {}',
    ...snapshot.services.map(item=>`one sig ${item.atom} extends Service {}`),
    ...snapshot.entries.map(item=>`one sig ${item.atom} extends Entry {}`),
    ...snapshot.events.map(item=>`one sig ${item.atom} extends EventBinding {}`),
    ...snapshot.workflows.map(item=>`one sig ${item.atom} extends Workflow {}`),
    ...snapshot.artifacts.map(item=>`one sig ${item.atom} extends Artifact {}`),
    'fact ExactEmittedStructure {',
    ...snapshot.services.flatMap(item=>[
      `  ${item.atom}.entries = ${setExpr(item.entries)}`,
      `  ${item.atom}.eventBindings = ${setExpr(item.events)}`,
      `  ${item.atom}.workflow = ${item.workflow??'none'}`,
      `  ${item.atom}.serviceModule = ${item.module}`,
      `  ${item.atom}.runtimeModule = ${item.runtime}`,
      `  ${item.atom}.systemGraph = ${item.graph}`,
      `  ${item.atom}.bridge = ${item.bridge}`,
      `  ${item.atom}.wiring = ${item.wiring}`,
    ]),
    ...snapshot.entries.flatMap(item=>[
      `  ${item.atom}.executable = ${item.executable}`,
      `  ${item.atom}.sourceManifest = ${item.manifest}`,
    ]),
    ...snapshot.events.map(item=>`  ${item.atom}.descriptors = ${setExpr(item.descriptors)}`),
    ...snapshot.workflows.map(item=>`  ${item.atom}.worker = ${item.worker}`),
    '}',
    'assert EachEntryHasOneService { all e: Entry | one s: Service | e in s.entries }',
    'assert EachBindingHasService { all b: EventBinding | some s: Service | b in s.eventBindings }',
    'assert EachBindingHasDescriptor { all b: EventBinding | some b.descriptors }',
    'assert BindingDescriptorsMatchServices { all b: EventBinding, s: Service | (b in s.eventBindings) iff (s.wiring in b.descriptors) }',
    'assert EachWorkflowHasOneService { all w: Workflow | one s: Service | w in s.workflow }',
    `run {} for ${scope}`,
    `check EachEntryHasOneService for ${scope}`,
    `check EachBindingHasService for ${scope}`,
    `check EachBindingHasDescriptor for ${scope}`,
    `check BindingDescriptorsMatchServices for ${scope}`,
    `check EachWorkflowHasOneService for ${scope}`,
    '',
  ];
  const alloy=lines.join('\n');
  owner.inspect(handle);
  return Object.freeze({schema_version:'craft.generic-structural-alloy/v1-candidate',language:'alloy',
    scope:'selected-emitted-service-entry-event-workflow-artifacts',qualification:'finite-exact-structural-snapshot-only',
    application_contract_sha256:manifest.application_contract_sha256,source_capture_sha256:manifest.source_capture_sha256,
    profile_sha256:manifest.profile_sha256,executable_semantics_sha256:manifest.executable_semantics_sha256,
    inventory_sha256:manifest.inventory_sha256,
    services:Object.freeze(snapshot.services),entries:Object.freeze(snapshot.entries),events:Object.freeze(snapshot.events),
    workflows:Object.freeze(snapshot.workflows),artifacts:Object.freeze(snapshot.artifacts),
    missing_complete_application_classes:Object.freeze([...manifest.missing_complete_application_classes]),
    source_manifest_complete_application:manifest.complete_application,alloy,alloy_sha256:sha(alloy),authority_effect:'none',
    claim_ceiling:'selected-emitted-structure-only-no-runtime-or-complete-application-or-solver-proof'});
}

export function assertGenericStructuralAlloyCurrent(owner:Owner,handle:GenericServiceArtifactHandle,model:GenericStructuralAlloyModelV1):void {
  if(!model||typeof model!=='object'||typeof model.alloy!=='string'||!hex.test(model.alloy_sha256)||sha(model.alloy)!==model.alloy_sha256||
    dataDigest(exportGenericStructuralAlloyModel(owner,handle))!==dataDigest(model))reject('InvalidInventory');
}
