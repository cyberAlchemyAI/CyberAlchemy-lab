import path from 'node:path';
import {assertCompiledProjectSnapshot,type CompiledProjectGraph} from '../input/project-model.js';
import {assertCompiledCompositionBoundary,type CompiledCompositionBoundary} from '../input/composition-boundary.js';
import {assertCompiledProjectFields,EXACT_PROJECT_FIELD_SELECTION_VERSION,type CompiledProjectFields} from '../input/compiled-field-model.js';
import {createCompiledProjectCertificate} from '../compilation/certificate.js';
import {canonicalJson,sha256} from '../input/source-manifest.js';
import {assertStateMachineData,checkTypedStateMachine,decodeTypedStateMachineContract,freezeStateMachine,stateMachineFail,stateMachineObject,STATE_MACHINE_CONTRACT_SHA256,type TypedStateMachineContract} from '../typed-backend/state-machine.js';
import type {TypedRuleContract} from '../typed-operation/contracts.js';
import {EXACT_UINT64_PROFILE} from './exact-uint64.js';
import {PROFILED_SOURCE_DIGESTS} from './profiled-project.js';
import {planConfiguredRules,RULE_CONFIGURATION_SHA256,STRUCTURED_RULE_VERSION,type RuleConfigurationSources} from './configured-rules.js';
import {renderConfiguredStateMachine} from './configured-state-machine-source.js';
import type {PlannedArtifact} from './contracts.js';

export const CONFIGURED_STATE_MACHINE_VERSION='domainspec.configured-state-machines-selection/v1-candidate' as const;
export interface StateMachineSelection {
  readonly schema_version:typeof CONFIGURED_STATE_MACHINE_VERSION;
  readonly language:'typescript';
  readonly module_root:string;
  readonly roots:readonly string[];
  readonly boundary_sha256:string;
  readonly field_compilation_sha256:string|null;
}
export interface StateMachineSources {readonly state_machine_contract:string;readonly rules:RuleConfigurationSources;}
const reserved=new Set(('as async await break case catch class const continue crate debugger def default del do else enum except export extends false finally fn for from function global if impl import in interface is lambda let loop match mod move mut new nonlocal null package pass private protected pub public raise ref return self static struct super switch this throw trait true try type typeof unsafe use var void while with yield con prn aux nul '+Array.from({length:9},(_,i)=>'com'+(i+1)+' lpt'+(i+1)).join(' ')).split(' '));
const portable=(s:string)=>/^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$/.exec(s)?.[0]===s&&!reserved.has(s);
const fail=stateMachineFail,q=JSON.stringify;
function frozenLiteral(v:unknown):string {
  if(Array.isArray(v))return 'Object.freeze(['+v.map(frozenLiteral).join(',')+'])';
  if(v&&typeof v==='object')return 'Object.freeze({'+Object.entries(v).map(([k,x])=>'['+q(k)+']:'+frozenLiteral(x)).join(',')+'})';
  return q(v);
}
/** Source-bound reducer planning only; no Event/Operation execution or output writes. */
export function planConfiguredStateMachines(graph:CompiledProjectGraph,boundary:CompiledCompositionBoundary,fields:CompiledProjectFields|null,selection:StateMachineSelection,sources:StateMachineSources){
  assertCompiledProjectSnapshot(graph);assertCompiledCompositionBoundary(boundary);if(fields!==null)assertCompiledProjectFields(fields);
  assertStateMachineData(selection);assertStateMachineData(sources);
  stateMachineObject(selection,['schema_version','language','module_root','roots','boundary_sha256','field_compilation_sha256']);
  stateMachineObject(sources,['state_machine_contract','rules']);
  stateMachineObject(sources.rules,['configuration','base','typescript','rule_contract','collection_contract','predicate_contract','numeric_contract','exact_contract','literal_contract','structured_contract','field_contract']);
  if(selection.schema_version!==CONFIGURED_STATE_MACHINE_VERSION||selection.language!=='typescript')fail('unsupported generator selection');
  if(typeof selection.module_root!=='string'||!selection.module_root.split('/').every(portable))fail('unsafe module root');
  if(!Array.isArray(selection.roots)||!selection.roots.length||selection.roots.length>128||new Set(selection.roots).size!==selection.roots.length||selection.roots.some(s=>typeof s!=='string'||s.split(':').length!==2||!s.split(':').every(portable)))fail('invalid roots');
  const certificate=createCompiledProjectCertificate(graph);
  if(boundary.certificate.graph_sha256!==certificate.graph_sha256||selection.boundary_sha256!==boundary.boundary_sha256||selection.field_compilation_sha256!==(fields?.compilation_sha256??null)||fields&&(fields.certificate.graph_sha256!==certificate.graph_sha256||fields.selection.schema_version!==EXACT_PROJECT_FIELD_SELECTION_VERSION))fail('stale or cross-graph selection');
  for(const [key,expected]of Object.entries({state_machine_contract:STATE_MACHINE_CONTRACT_SHA256,configuration:RULE_CONFIGURATION_SHA256,...PROFILED_SOURCE_DIGESTS})){
    const bytes=key==='state_machine_contract'?sources.state_machine_contract:sources.rules[key as keyof RuleConfigurationSources];
    if(typeof bytes!=='string'||sha256(bytes)!==expected)fail('source drift:'+key);
  }
  const config=JSON.parse(sources.rules.configuration),cell=config.types.find((t:{kind:string})=>t.kind==='State Machine');
  if(cell?.role!=='domain/state-machines'||canonicalJson(cell.blocked_by)!=='["DSR-011","DSR-016"]')fail('unexpected State Machine configuration');
  const overlay=JSON.parse(sources.rules.typescript).representation_overlays.find((p:{contract_id:string})=>p.contract_id==='state-machine.profile-representation');
  if(overlay?.candidate_protocols.find((p:{protocol_id:string})=>p.protocol_id==='typescript.bound-state-machine/v1')?.form_id!=='typescript.discriminated-union-reducer')fail('missing State Machine profile');
  const roots=[...selection.roots].sort(),contracts=new Map<string,TypedStateMachineContract>();
  const nodes=graph.nodes.map(n=>({selector:n.selector,kind:n.kind,rule:n.kind==='Rule'&&n.body.typed_contract?n.body.typed_contract as TypedRuleContract:null}));
  for(const s of roots){const n=graph.nodes.find(n=>n.selector===s);if(n?.kind!=='State Machine'||!n.body.typed_contract)fail('versioned State Machine required; migrate legacy explicitly:'+s);
    const c=decodeTypedStateMachineContract(n!.body.typed_contract);checkTypedStateMachine(c,fields?.model.declarations??[],nodes);contracts.set(s,c);
  }
  const ruleRoots=[...new Set([...contracts.values()].flatMap(c=>c.transitions.flatMap(t=>t.guard?[t.guard.selector]:[])))].sort();
  // A guardless machine is lawful; never fabricate a tautological Rule.
  const rulePlan=ruleRoots.length?planConfiguredRules(graph,{schema_version:STRUCTURED_RULE_VERSION,language:'typescript',module_root:selection.module_root,value_profile:EXACT_UINT64_PROFILE,roots:ruleRoots},sources.rules):null;
  const artifacts:PlannedArtifact[]=[...rulePlan?.artifacts??[]];
  const add=(relative_path:string,content:string)=>{if(artifacts.some(a=>a.relative_path===relative_path))fail('artifact collision');const a={relative_path,content,sha256:sha256(content),size_bytes:Buffer.byteLength(content)};artifacts.push(a);return a;};
  const evidence=(s:string)=>{const n=graph.nodes.find(n=>n.selector===s)??fail('missing node'),b=boundary.domain_graph.nodes.find(n=>n.selector===s)??fail('unbound node');return {selector:s,kind:n.kind,source:b.source,body_sha256:sha256(canonicalJson(n.body))};};
  const modules=roots.map(s=>{
    const c=contracts.get(s)!,[feature,node]=s.split(':') as [string,string],relative_path=selection.module_root+'/features/'+feature+'/src/'+cell.role+'/'+node+'.ts',provider_path=relative_path.replace(/\.ts$/,'.provider.ts');
    const imports=[...new Set(c.transitions.flatMap(t=>t.guard?[t.guard.selector]:[]))].sort().map((selector,i)=>{
      const m=rulePlan?.modules.find(m=>m.selector===selector)??fail('missing Rule module'),p=path.posix.relative(path.posix.dirname(provider_path),m.relative_path).replace(/\.ts$/,'.js');
      return {selector,path:p.startsWith('.')?p:'./'+p,symbol:m.callable,local:'condition'+i};
    });
    const provider=add(provider_path,renderConfiguredStateMachine(c,fields?.model??null,imports)),callable='transition'+node.split('-').map(w=>w[0]!.toUpperCase()+w.slice(1)).join('');
    const eventRefs=[...new Set(c.transitions.flatMap(t=>[t.trigger_event_ref,...t.output_intents.map(o=>o.event_ref)]))].sort();
    const body={schema_version:'domainspec.generated-state-machine-descriptor/v1-candidate',protocol_id:'typescript.bound-state-machine/v1',selector:s,source:evidence(s),contract:c,contract_sha256:sha256(canonicalJson(c)),definition_sha256:STATE_MACHINE_CONTRACT_SHA256,
      event_dependencies:eventRefs.map(evidence),rule_plan_sha256:rulePlan?.plan_sha256??null,rule_dependencies:imports.map(i=>{const m=rulePlan!.modules.find(m=>m.selector===i.selector)!;return {selector:i.selector,path:m.relative_path,sha256:artifacts.find(a=>a.relative_path===m.relative_path)!.sha256};}),
      field_model_sha256:fields?.model.model_sha256??null,return_semantics:'transition-or-rejection',effect_contract:'none',trigger_semantics:'explicit-event-input-symbol',output_semantics:'ordered-unexecuted-intents',provider:{sha256:provider.sha256},authority_effect:'none'};
    const descriptor={...body,descriptor_sha256:sha256(canonicalJson(body))};
    add(relative_path,'import {reduce,initialState} from '+q('./'+node+'.provider.js')+';\nexport type {State,Trigger,Parameters,Outcome} from '+q('./'+node+'.provider.js')+';\nexport {initialState};\nexport const '+callable+'=Object.freeze(Object.assign(reduce,{descriptor:'+frozenLiteral(descriptor)+'}));\n');
    return {selector:s,relative_path,provider_path,callable,imports,descriptor};
  });
  artifacts.sort((a,b)=>a.relative_path<b.relative_path?-1:1);
  const body={schema_version:'domainspec.configured-state-machines-plan/v1-candidate',selection:{...selection,roots},certificate,boundary_sha256:boundary.boundary_sha256,field_compilation_sha256:fields?.compilation_sha256??null,source_digests:{contract:STATE_MACHINE_CONTRACT_SHA256,configuration:RULE_CONFIGURATION_SHA256,...PROFILED_SOURCE_DIGESTS},rule_plan:rulePlan,modules,artifacts,authority_effect:'none'};
  return freezeStateMachine({...body,plan_sha256:sha256(canonicalJson(body))});
}
