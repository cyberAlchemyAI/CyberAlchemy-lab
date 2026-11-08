import {assertCompiledProjectSnapshot,type CompiledProjectGraph} from '../input/project-model.js';
import {assertCompiledCompositionBoundary,type CompiledCompositionBoundary} from '../input/composition-boundary.js';
import {createCompiledProjectCertificate} from '../compilation/certificate.js';
import {canonicalJson,sha256} from '../input/source-manifest.js';
import {PROFILED_SOURCE_DIGESTS} from './profiled-project.js';
import {renderConfiguredEvent,type EventSource} from './configured-event-source.js';
import type {PlannedArtifact} from './contracts.js';
import {eventReferenceIdentity} from './event-reference-identity.js';

export const CONFIGURED_EVENT_VERSION='domainspec.configured-events-selection/v1-candidate';
export const EVENT_VALUE_PROFILE='domainspec.event-values/v1-candidate';
export const EVENT_CONTRACT_SHA256='fd9e1a0af836f99e066e340eb0d3fdc184dfa8c832abf23d22fd05fc6394eb1b';
export interface ConfiguredEventSelection {
  readonly schema_version:typeof CONFIGURED_EVENT_VERSION;
  readonly language:'typescript';
  readonly value_profile:typeof EVENT_VALUE_PROFILE;
  readonly boundary_sha256:string;
  readonly module_root:string;
  readonly roots:readonly string[];
}
export interface EventConfigurationSources {readonly configuration:string;readonly base:string;readonly typescript:string;readonly event_contract:string;}
const fail=(message:string):never=>{throw Error('DS_CONFIGURED_EVENT:'+message);};
const freeze=<T>(v:T):T=>{if(v&&typeof v==='object'&&!Object.isFrozen(v)){Object.values(v).forEach(freeze);Object.freeze(v);}return v;};
const reserved=new Set(('as async await break case catch class const continue crate debugger def default del do else enum except export extends false finally fn for from function global if impl import in interface is lambda let loop match mod move mut new nonlocal null package pass private protected pub public raise ref return self static struct super switch this throw trait true try type typeof unsafe use var void while with yield con prn aux nul '+Array.from({length:9},(_,i)=>'com'+(i+1)+' lpt'+(i+1)).join(' ')).split(' '));
const portable=(s:string)=>/^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$/.test(s)&&!reserved.has(s);
function keys(v:unknown,expected:readonly string[]):void{
  if(!v||typeof v!=='object'||Array.isArray(v)||![Object.prototype,null].includes(Object.getPrototypeOf(v)))fail('plain data object required');
  const d=Object.getOwnPropertyDescriptors(v);
  if(Reflect.ownKeys(d).length!==expected.length||Reflect.ownKeys(d).some(k=>typeof k!=='string'||!expected.includes(k))||Object.values(d).some(p=>!Object.hasOwn(p,'value')||!p.enumerable))fail('closed data object required');
}
function frozenLiteral(v:unknown):string{
  if(Array.isArray(v))return 'Object.freeze(['+v.map(frozenLiteral).join(',')+'])';
  if(v&&typeof v==='object')return 'Object.freeze({'+Object.entries(v).map(([k,x])=>'['+JSON.stringify(k)+']:'+frozenLiteral(x)).join(',')+'})';
  return JSON.stringify(v);
}

/** Compile Event data construction, not occurrence registration or publication.
 * The checked graph owns source and reference identities; no data factory is
 * fabricated for Event, and referenced nodes are not recursively embedded.
 */
export function planConfiguredEvents(graph:CompiledProjectGraph,boundary:CompiledCompositionBoundary,selection:ConfiguredEventSelection,sources:EventConfigurationSources){
  assertCompiledProjectSnapshot(graph);assertCompiledCompositionBoundary(boundary);
  keys(selection,['schema_version','language','value_profile','boundary_sha256','module_root','roots']);
  keys(sources,['configuration','base','typescript','event_contract']);
  if(selection.schema_version!==CONFIGURED_EVENT_VERSION||selection.language!=='typescript'||selection.value_profile!==EVENT_VALUE_PROFILE)fail('unsupported selection');
  const certificate=createCompiledProjectCertificate(graph);
  if(selection.boundary_sha256!==boundary.boundary_sha256||boundary.certificate.graph_sha256!==certificate.graph_sha256)fail('stale or cross-graph boundary');
  if(typeof selection.module_root!=='string'||!selection.module_root.split('/').every(portable))fail('unsafe module root');
  const expected={configuration:'9ac018e42080483f373219049b466d8a515cb3e7748181ea8e635b1162af8317',...PROFILED_SOURCE_DIGESTS,event_contract:EVENT_CONTRACT_SHA256};
  for(const key of Object.keys(expected) as (keyof typeof expected)[])if(typeof sources[key]!=='string'||sha256(sources[key])!==expected[key])fail('source drift:'+key);
  if(!Array.isArray(selection.roots)||Object.getPrototypeOf(selection.roots)!==Array.prototype)fail('plain roots required');
  const d:Record<string,PropertyDescriptor>=Object.getOwnPropertyDescriptors(selection.roots),length=d.length!.value;
  if(!Number.isSafeInteger(length)||length<1||Reflect.ownKeys(d).length!==length+1)fail('nonempty dense roots required');
  const roots:string[]=[];
  for(let i=0;i<length;i++){const p=d[String(i)];if(!p||!Object.hasOwn(p,'value')||!p.enumerable||typeof p.value!=='string')return fail('inert roots required');roots.push(p.value);}
  if(new Set(roots).size!==roots.length)fail('duplicate roots');roots.sort();
  const config=JSON.parse(sources.configuration),cell=config.types.find((t:{kind:string})=>t.kind==='Event');
  if(cell?.role!=='domain/events'||canonicalJson(cell.blocked_by)!=='["DSR-009"]')fail('unexpected Event configuration');
  const profile=JSON.parse(sources.typescript),overlay=profile.representation_overlays.find((p:{contract_id:string})=>p.contract_id==='event.profile-representation');
  const protocol=overlay?.candidate_protocols.find((p:{protocol_id:string})=>p.protocol_id==='typescript.bound-event/v1');
  if(protocol?.form_id!=='typescript.bound-event-readonly-record')fail('missing Event protocol');
  const artifacts:PlannedArtifact[]=[];
  const add=(relative_path:string,content:string)=>{
    if(artifacts.some(a=>a.relative_path===relative_path))fail('artifact collision');
    const a={relative_path,content,size_bytes:Buffer.byteLength(content),sha256:sha256(content)};artifacts.push(a);return a;
  };
  const modules=roots.map(selector=>{
    if(selector.split(':').length!==2||!selector.split(':').every(portable))fail('unsafe selector');
    const node=graph.nodes.find(n=>n.selector===selector),bound=boundary.domain_graph.nodes.find(n=>n.selector===selector);
    if(node?.kind!=='Event'||bound?.kind!=='Event')return fail('checked Event required:'+selector);
    const source=structuredClone(node.body) as unknown as EventSource;
    const [feature,id]=selector.split(':') as [string,string],callable='event'+id.split('-').map(s=>s[0]!.toUpperCase()+s.slice(1)).join('');
    const relative_path=selection.module_root+'/features/'+feature+'/src/'+cell.role+'/'+id+'.ts',provider_path=relative_path.replace(/\.ts$/,'.provider.ts');
    const referenceIdentities=new Map([...new Set([source.occurrence_id,...source.payload].flatMap(f=>f.type_ref.kind==='reference'?[f.type_ref.selector]:[]))].map(reference=>[reference,eventReferenceIdentity(graph,reference,fail)]));
    const implementation=add(provider_path,renderConfiguredEvent(source,referenceIdentities)),provider_import='./'+id+'.provider.js';
    const references=[...new Set([source.occurrence_id,...source.payload].flatMap(f=>f.type_ref.kind==='reference'?[f.type_ref.selector]:[]))].sort().map(selector=>{
      const target=graph.nodes.find(n=>n.selector===selector),evidence=boundary.domain_graph.nodes.find(n=>n.selector===selector);
      if(!target||!evidence||!['Entity','Value Object','Enum','Event'].includes(target.kind))return fail('unbound reference');
      return {selector,kind:target.kind,source:evidence.source,body_sha256:sha256(canonicalJson(target.body)),semantics:'reference-not-embedding' as const};
    });
    const descriptorBody={schema_version:'domainspec.generated-event-descriptor/v1-candidate',protocol_id:'typescript.bound-event/v1',selector,
      source:bound.source,contract_sha256:sha256(canonicalJson(source)),event_type:source.event_type,version:source.version,
      occurrence_id:source.occurrence_id,occurred_at_policy:source.occurred_at_policy,payload:source.payload,references,
      value_profile:selection.value_profile,return_semantics:'immutable-occurrence-data',effect_contract:source.occurred_at_policy==='generated'?'explicit-clock-only':'none',
      publication:false,occurrence_registration:false,distributed_exactly_once_claim:false,primary_callable_count:1,provider:{sha256:implementation.sha256},authority_effect:'none'};
    const descriptor={...descriptorBody,descriptor_sha256:sha256(canonicalJson(descriptorBody))};
    add(relative_path,'import {make} from '+JSON.stringify(provider_import)+';\nexport type {EventInput,EventValue} from '+JSON.stringify(provider_import)+';\nexport const '+callable+'=Object.freeze(Object.assign(make,{descriptor:'+frozenLiteral(descriptor)+'}));\n');
    return {selector,relative_path,provider_path,provider_import,callable,descriptor};
  });
  artifacts.sort((a,b)=>a.relative_path<b.relative_path?-1:1);
  const body={schema_version:'domainspec.configured-events-plan/v1-candidate' as const,selection:{...selection,roots},certificate,boundary_sha256:boundary.boundary_sha256,
    source_digests:expected,modules,artifacts,authority_effect:'none' as const};
  return freeze({...body,plan_sha256:sha256(canonicalJson(body))});
}
