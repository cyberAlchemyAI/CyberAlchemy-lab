import path from 'node:path';
import {assertCompiledProjectSnapshot,type CompiledProjectGraph} from '../input/project-model.js';
import {createCompiledProjectCertificate} from '../compilation/certificate.js';
import {canonicalJson,sha256} from '../input/source-manifest.js';
import {assertInterfaceData} from '../typed-backend/interface.js';
import {assertResolvedArtifactPlan,type ResolvedArtifactPlan} from './resolved-artifact-plan.js';
import {inventoryGeneratedModule} from './generated-module-surface.js';
import type {PlannedArtifact} from './contracts.js';

export const RESOLVED_COMPOSITION_BINDINGS_DEFINITION_SHA256='c7c0cf577e372c3036e6ec567fb2e36855f16b723ff1298647739f24c171c388';
export class ResolvedCompositionBindingsError extends Error {
 readonly exitCode=22;
 readonly code='DS_RESOLVED_COMPOSITION_BINDINGS';
 constructor(readonly pointer:string,message:string){super('DS_RESOLVED_COMPOSITION_BINDINGS:'+pointer+':'+message);this.name='ResolvedCompositionBindingsError';}
}
const fail=(pointer:string,message:string):never=>{throw new ResolvedCompositionBindingsError(pointer,message);};
const compare=(a:string,b:string)=>a<b?-1:a>b?1:0;
function freeze<T>(value:T):T{if(value&&typeof value==='object'&&!Object.isFrozen(value)){Object.values(value).forEach(freeze);Object.freeze(value);}return value;}
export interface NativeTarget {readonly relative_path:string;readonly sha256:string;readonly export_name:string;}
export interface CompositionBinding {
 readonly name:string;
 readonly selector:string;
 readonly role:'calculation-call'|'structural-record';
 readonly contract_sha256:string;
 readonly arguments:readonly {readonly authored_name:string;readonly core_name:string}[];
 readonly native_target:NativeTarget|null;
}
const registered=new WeakSet<object>();
const runtime=`function argumentsFor(input:unknown,names:readonly string[]):Record<string,PropertyDescriptor>{
 if(!input||typeof input!=='object'||![Object.prototype,null].includes(Object.getPrototypeOf(input)))throw new TypeError('COMPOSITION_CALCULATION_INPUT');
 const d=Object.getOwnPropertyDescriptors(input);
 if(Reflect.ownKeys(d).length!==names.length||Reflect.ownKeys(d).some(k=>typeof k!=='string'||!names.includes(k))||Object.values(d).some(p=>!Object.hasOwn(p,'value')||!p.enumerable))throw new TypeError('COMPOSITION_CALCULATION_INPUT');
 return d;
}
`;
/** Existing behavior owns evaluation order; this adapter only renames its argument data. */
function adapter(bindings:readonly CompositionBinding[],relativePath:string):string{
 const calls=bindings.filter(b=>b.role==='calculation-call'),lines:string[]=[];
 for(const [i,b] of calls.entries()){
  const target=b.native_target!;
  let specifier=path.posix.relative(path.posix.dirname(relativePath),target.relative_path).replace(/\.ts$/,'.js');
  if(!specifier.startsWith('.'))specifier='./'+specifier;
  lines.push('import {'+target.export_name+' as calculation'+i+'} from '+JSON.stringify(specifier)+';');
 }
 lines.push(runtime,"export function evaluateCalculation(name:string,input:unknown):bigint {"," switch(name){");
 for(const [i,b] of calls.entries()){
  lines.push('  case '+JSON.stringify(b.name)+': {',
   '   const d=argumentsFor(input,'+JSON.stringify(b.arguments.map(a=>a.authored_name))+');',
   '   return calculation'+i+'({'+b.arguments.map(a=>JSON.stringify(a.core_name)+':d['+JSON.stringify(a.authored_name)+']!.value').join(',')+'});',
   '  }');
 }
 lines.push("  default: throw new TypeError('COMPOSITION_CALCULATION');"," }","}","");
 return lines.join('\n');
}
function safePath(relative:string){
 return !relative.includes('\\')&&path.posix.normalize(relative)===relative&&!relative.startsWith('/')&&relative.split('/').every(s=>
  s!=='.'&&s!=='..'&&/^[a-z0-9][a-z0-9.-]*$/.exec(s)?.[0]===s&&!/[. ]$/.test(s)&&!/^(con|prn|aux|nul|com[1-9]|lpt[1-9])(?:\.|$)/i.test(s));
}

/** Additive checked binding only. Does not publish, launch an endpoint or execute behavior. */
export function planResolvedCompositionBindings(graph:CompiledProjectGraph,resolved:ResolvedArtifactPlan,definition:string){
 assertCompiledProjectSnapshot(graph);assertResolvedArtifactPlan(resolved);
 if(typeof definition!=='string'||sha256(definition)!==RESOLVED_COMPOSITION_BINDINGS_DEFINITION_SHA256)fail('/definition','pinned definition required');
 const certificate=createCompiledProjectCertificate(graph);
 if(canonicalJson(certificate)!==canonicalJson(resolved.certificate)||canonicalJson(graph.source_manifest)!==canonicalJson(resolved.semantic_sources))fail('/graph','exact graph and resolved source identity required');
 const artifacts:PlannedArtifact[]=[];
 const add=(relative_path:string,content:string)=>{
  if(!safePath(relative_path)||typeof content!=='string')fail('/artifacts','unsafe composition artifact path');
  const a={relative_path,content,sha256:sha256(content),size_bytes:Buffer.byteLength(content)};artifacts.push(a);return a;
 };
 const compositions=[...(graph.compositions??[])].sort((a,b)=>compare(a.id,b.id)).map(c=>{
  if(c.source.model.endpoint.target!=='node-http')fail('/compositions/'+c.id,'unsupported composition target; no fallback');
  const bindings:CompositionBinding[]=Object.entries(c.source.core_bindings as Record<string,{selector:string;fields:Record<string,string>}>).sort(([a],[b])=>compare(a,b)).map(([name,b])=>{
   const node=graph.nodes.find(n=>n.selector===b.selector);
   if(!node?.body.typed_contract)fail('/bindings/'+name,'checked core declaration required');
   const contract=node!.body.typed_contract,calculation=Object.hasOwn(c.source.contract.calculations,name);
   const names:string[]=calculation?c.source.contract.calculations[name]:Object.keys(b.fields).sort(compare);
   let target:NativeTarget|null=null;
   if(calculation){
    if(node!.kind!=='Calculation'||(contract as {schema_version?:string}).schema_version!=='domainspec.typed-calculation/v1')fail('/bindings/'+name,'existing v1 Calculation binding required');
    const nodeId=b.selector.split(':')[1]!,exportName='calculate'+nodeId.split('-').map(s=>s[0]!.toUpperCase()+s.slice(1)).join('');
    const matches=resolved.modules.filter(m=>m.qualified_selectors.includes(b.selector)&&m.exports.some(e=>e.kind==='value'&&e.name===exportName)&&
     m.request_sha256s.some(id=>resolved.requests.some(r=>r.request_sha256===id&&r.kind==='calculations-v1')));
    if(matches.length!==1)fail('/bindings/'+name,'exactly one selected native Calculation required: '+b.selector);
    target={relative_path:matches[0]!.relative_path,sha256:matches[0]!.sha256,export_name:exportName};
   }
   return {name,selector:b.selector,role:calculation?'calculation-call':'structural-record',contract_sha256:sha256(canonicalJson(contract)),arguments:names.map(authored_name=>({authored_name,core_name:b.fields[authored_name]!})),native_target:target};
  });
  const prefix='compositions/'+c.id+'/',adapterPath=prefix+'core-api.ts';
  for(const [name,content] of Object.entries(c.artifacts).sort(([a],[b])=>compare(a,b)))add(prefix+name,content);
  add(adapterPath,adapter(bindings,adapterPath));
  return {id:c.id,source_sha256:sha256(canonicalJson(c.source)),validation:structuredClone(c.validation),dependency_graph:structuredClone(c.dependency_graph),bindings,adapter_path:adapterPath,behavior_path:prefix+'behavior.mjs',artifact_paths:[...Object.keys(c.artifacts).map(name=>prefix+name),adapterPath].sort(compare)};
 });
 artifacts.sort((a,b)=>compare(a.relative_path,b.relative_path));
 const all=new Map<string,PlannedArtifact>();
 for(const a of [...resolved.artifacts,...artifacts]){
  const key=a.relative_path.toLowerCase();
  if(all.has(key))fail('/artifacts','case-fold or exact artifact collision');
  all.set(key,a);
 }
 for(const key of all.keys()){
  let parent=path.posix.dirname(key);
  while(parent!=='.'){if(all.has(parent))fail('/artifacts','file-directory collision');parent=path.posix.dirname(parent);}
 }
 const modules=compositions.map(c=>{
  const file=artifacts.find(a=>a.relative_path===c.adapter_path)!,surface=inventoryGeneratedModule(file.content);
  return {relative_path:file.relative_path,sha256:file.sha256,composition_id:c.id,exports:surface.exports,imports:surface.imports.map(i=>{
   if(!i.specifier.endsWith('.js')||!i.specifier.startsWith('.'))fail('/imports','relative generated module required');
   const targetPath=path.posix.normalize(path.posix.join(path.posix.dirname(file.relative_path),i.specifier.slice(0,-3)+'.ts'));
   const target=resolved.modules.find(m=>m.relative_path===targetPath);
   if(!target||i.names.some(name=>!target.exports.some(e=>e.kind==='value'&&e.name===name)))fail('/imports','checked generated export required');
   return {...i,target_path:targetPath,target_sha256:target!.sha256,dependency:'generated-leaf' as const};
  })};
 });
 const body={schema_version:'domainspec.resolved-composition-bindings/v1-candidate' as const,definition_sha256:RESOLVED_COMPOSITION_BINDINGS_DEFINITION_SHA256,
  definition_source:{content:definition,sha256:sha256(definition),size_bytes:Buffer.byteLength(definition)},graph_sha256:certificate.graph_sha256,
  source_manifest_sha256:graph.source_manifest.manifest_sha256,resolved_plan_sha256:resolved.plan_sha256,compositions,artifacts,modules,
  verification_obligations:['composition-source-preservation','selected-calculation-bindings','strict-native-compilation','composition-behavior-controls'],
  claim_scope:'composition-binding-plan-only' as const,authority_effect:'none' as const,output_effect:'none' as const};
 const result=freeze({...body,plan_sha256:sha256(canonicalJson(body))});registered.add(result);return result;
}
export type ResolvedCompositionBindings=ReturnType<typeof planResolvedCompositionBindings>;
export function validateResolvedCompositionBindings(value:unknown,graph:CompiledProjectGraph,resolved:ResolvedArtifactPlan,definition:string){
 assertInterfaceData(value);const expected=planResolvedCompositionBindings(graph,resolved,definition);
 if(canonicalJson(value)!==canonicalJson(expected))fail('/plan','incomplete or changed binding evidence');
 return expected;
}
export function renderResolvedCompositionBindings(plan:ResolvedCompositionBindings):string{
 if(!plan||typeof plan!=='object'||!registered.has(plan))fail('/plan','registered binding plan required');
 return canonicalJson(plan)+'\n';
}
