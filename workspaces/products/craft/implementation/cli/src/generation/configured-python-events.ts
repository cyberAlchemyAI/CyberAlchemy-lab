import {assertCompiledProjectSnapshot,type CompiledProjectGraph} from '../input/project-model.js';
import {assertCompiledCompositionBoundary,type CompiledCompositionBoundary} from '../input/composition-boundary.js';
import {createCompiledProjectCertificate} from '../compilation/certificate.js';
import {canonicalJson,sha256} from '../input/source-manifest.js';
import {PYTHON_ENUM_SOURCE_DIGESTS, pythonPortableIdentifier, pythonStringLiteral} from './configured-python-enums.js';
import {pythonRelativeModule, pythonSnake} from './configured-python-owned-values.js';
import {EVENT_VALUE_PROFILE, EVENT_CONTRACT_SHA256} from './configured-events.js';
import {renderPythonEvent, renderPythonEventBinding} from './configured-python-event-source.js';
import {renderPythonEventValues} from './configured-python-event-values.js';
import type {EventSource} from './configured-event-source.js';
import type {PlannedArtifact} from './contracts.js';
import {eventReferenceIdentity} from './event-reference-identity.js';

export const PYTHON_EVENT_VERSION='domainspec.configured-python-events-selection/v1-candidate';
export interface PythonEventSelection {
  readonly schema_version:typeof PYTHON_EVENT_VERSION;
  readonly language:'python';
  readonly value_profile:typeof EVENT_VALUE_PROFILE;
  readonly boundary_sha256:string;
  readonly module_root:string;
  readonly roots:readonly string[];
}
export interface PythonEventSources {readonly configuration:string;readonly base:string;readonly python:string;readonly event_contract:string;}
const fail=(message:string):never=>{throw Error('DS_PYTHON_EVENT:'+message);};
const freeze=<T>(v:T):T=>{if(v&&typeof v==='object'&&!Object.isFrozen(v)){Object.values(v).forEach(freeze);Object.freeze(v);}return v;};
function keys(v:unknown,expected:readonly string[]):void{
  if(!v||typeof v!=='object'||Array.isArray(v)||![Object.prototype,null].includes(Object.getPrototypeOf(v)))fail('plain data object required');
  const d=Object.getOwnPropertyDescriptors(v);
  if(Reflect.ownKeys(d).length!==expected.length||Reflect.ownKeys(d).some(k=>typeof k!=='string'||!expected.includes(k))||Object.values(d).some(p=>!Object.hasOwn(p,'value')||!p.enumerable))fail('closed data object required');
}
/** Compile Event data construction, not occurrence registration or publication.
 * The checked graph owns source and reference identities; no data factory is
 * fabricated for Event, and referenced nodes are not recursively embedded.
 */
export function planConfiguredPythonEvents(graph:CompiledProjectGraph,boundary:CompiledCompositionBoundary,selection:PythonEventSelection,sources:PythonEventSources){
  assertCompiledProjectSnapshot(graph);assertCompiledCompositionBoundary(boundary);
  keys(selection,['schema_version','language','value_profile','boundary_sha256','module_root','roots']);
  keys(sources,['configuration','base','python','event_contract']);
  if(selection.schema_version!==PYTHON_EVENT_VERSION||selection.language!=='python'||selection.value_profile!==EVENT_VALUE_PROFILE)fail('unsupported selection');
  const certificate=createCompiledProjectCertificate(graph);
  if(selection.boundary_sha256!==boundary.boundary_sha256||boundary.certificate.graph_sha256!==certificate.graph_sha256)fail('stale or cross-graph boundary');
  if(typeof selection.module_root!=='string')fail('unsafe module root');
  const segments=selection.module_root.split('/');segments.forEach(pythonPortableIdentifier);
  if(['enum','typing','types','builtins','dataclasses','collections','json','sys','hashlib','weakref','codecs','encodings','math','re'].includes(segments[0]!))fail('module root shadows standard library');
  const root=segments.map(pythonSnake).join('/');
  const expected={...PYTHON_ENUM_SOURCE_DIGESTS,event_contract:EVENT_CONTRACT_SHA256};
  for(const key of Object.keys(expected) as (keyof typeof expected)[])if(typeof sources[key]!=='string'||sha256(sources[key])!==expected[key])fail('source drift:'+key);
  if(!Array.isArray(selection.roots)||Object.getPrototypeOf(selection.roots)!==Array.prototype)fail('plain roots required');
  const d:Record<string,PropertyDescriptor>=Object.getOwnPropertyDescriptors(selection.roots),length=d.length!.value;
  if(!Number.isSafeInteger(length)||length<1||length>256||Reflect.ownKeys(d).length!==length+1)fail('nonempty dense roots required');
  const roots:string[]=[];
  for(let i=0;i<length;i++){const p=d[String(i)];if(!p||!Object.hasOwn(p,'value')||!p.enumerable||typeof p.value!=='string')return fail('inert roots required');roots.push(p.value);}
  if(new Set(roots).size!==roots.length)fail('duplicate roots');roots.sort();
  const config=JSON.parse(sources.configuration),cell=config.types.find((t:{kind:string})=>t.kind==='Event');
  if(cell?.role!=='domain/events'||canonicalJson(cell.blocked_by)!=='["DSR-009"]')fail('unexpected Event configuration');
  const profile=JSON.parse(sources.python),overlay=profile.representation_overlays.find((p:{contract_id:string})=>p.contract_id==='event.profile-representation');
  const protocol=overlay?.candidate_protocols.find((p:{protocol_id:string})=>p.protocol_id==='python.bound-event/v1');
  if(protocol?.form_id!=='python.bound-event-frozen-record')fail('missing Event protocol');
  const artifacts:PlannedArtifact[]=[];
  const add=(relative_path:string,content:string)=>{
    if(artifacts.some(a=>a.relative_path===relative_path))fail('artifact collision');
    const a={relative_path,content,size_bytes:Buffer.byteLength(content),sha256:sha256(content)};artifacts.push(a);
    const parts=relative_path.split('/');
    for(let i=1;i<parts.length;i++){const p=parts.slice(0,i).join('/')+'/__init__.py';if(!artifacts.some(a=>a.relative_path===p))artifacts.push({relative_path:p,content:'',size_bytes:0,sha256:sha256('')});}
    return a;
  };
  const support=add(root+'/runtime/event_values.py',renderPythonEventValues());
  const modules=roots.map(selector=>{
    if(selector.split(':').length!==2)fail('unsafe selector');selector.split(':').forEach(pythonPortableIdentifier);
    const node=graph.nodes.find(n=>n.selector===selector),bound=boundary.domain_graph.nodes.find(n=>n.selector===selector);
    if(node?.kind!=='Event'||bound?.kind!=='Event')return fail('checked Event required:'+selector);
    const source=structuredClone(node.body) as unknown as EventSource;
    const [feature,id]=selector.split(':') as [string,string],callable='event_'+pythonSnake(id);
    const relative_path=root+'/features/'+pythonSnake(feature)+'/src/'+cell.role+'/'+pythonSnake(id)+'.py',provider_path=relative_path.replace(/\/([^/]+)\.py$/,'/_providers/$1.py');
    const runtimeModule=pythonRelativeModule(provider_path,support.relative_path).replace(/\.event_values$/,'');
    const reference_imports=[...new Set([source.occurrence_id,...source.payload].flatMap(f=>f.type_ref.kind==='reference'?[f.type_ref.selector]:[]))].sort().map(selector=>{
      const [feature,node]=selector.split(':') as [string,string];
      pythonPortableIdentifier(feature);pythonPortableIdentifier(node);
      const relative_path=root+'/runtime/event_references/'+pythonSnake(feature)+'/'+pythonSnake(node)+'.py';
      const identity=eventReferenceIdentity(graph,selector,fail);
      const content='from typing import NewType as _NewType\n\nEventRef = _NewType('+pythonStringLiteral(selector)+', '+(identity.scalar==='UInt64'?'int':'str')+')\n';
      const artifact=artifacts.find(a=>a.relative_path===relative_path)??add(relative_path,content);
      if(artifact.content!==content)fail('reference artifact collision');
      return {selector,relative_path,module:pythonRelativeModule(provider_path,relative_path),sha256:artifact.sha256,identity};
    });
    const implementation=add(provider_path,renderPythonEvent(source,runtimeModule,reference_imports)),provider_import=pythonRelativeModule(relative_path,provider_path);
    const references=[...new Set([source.occurrence_id,...source.payload].flatMap(f=>f.type_ref.kind==='reference'?[f.type_ref.selector]:[]))].sort().map(selector=>{
      const target=graph.nodes.find(n=>n.selector===selector),evidence=boundary.domain_graph.nodes.find(n=>n.selector===selector);
      if(!target||!evidence||!['Entity','Value Object','Enum','Event'].includes(target.kind))return fail('unbound reference');
      return {selector,kind:target.kind,source:evidence.source,body_sha256:sha256(canonicalJson(target.body)),semantics:'reference-not-embedding' as const,type_artifact:{id:selector+'/python-event-ref/v1',sha256:reference_imports.find(r=>r.selector===selector)!.sha256}};
    });
    const descriptorBody={schema_version:'domainspec.generated-python-event-descriptor/v1-candidate',protocol_id:'python.bound-event/v1',selector,
      source:bound.source,contract_sha256:sha256(canonicalJson(source)),event_type:source.event_type,version:source.version,
      occurrence_id:source.occurrence_id,occurred_at_policy:source.occurred_at_policy,payload:source.payload,references,
      value_profile:selection.value_profile,return_semantics:'immutable-occurrence-data',effect_contract:source.occurred_at_policy==='generated'?'explicit-clock-only':'none',
      publication:false,occurrence_registration:false,distributed_exactly_once_claim:false,primary_callable_count:1,runtime:{id:'event_values.py',sha256:support.sha256},provider:{sha256:implementation.sha256},authority_effect:'none'};
    const descriptor={...descriptorBody,descriptor_sha256:sha256(canonicalJson(descriptorBody))};
    add(relative_path,renderPythonEventBinding(provider_import,callable,descriptor,source.occurred_at_policy==='generated'));
    return {selector,relative_path,provider_path,provider_import,reference_imports,import_name:relative_path.slice(0,-3).replaceAll('/','.'),callable,descriptor};
  });
  artifacts.sort((a,b)=>a.relative_path<b.relative_path?-1:1);
  const body={schema_version:'domainspec.configured-python-events-plan/v1-candidate' as const,selection:{...selection,roots},certificate,boundary_sha256:boundary.boundary_sha256,
    source_digests:expected,modules,artifacts,authority_effect:'none' as const};
  return freeze({...body,plan_sha256:sha256(canonicalJson(body))});
}
