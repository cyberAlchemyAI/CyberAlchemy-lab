import path from 'node:path';
import {assertCompiledProjectSnapshot,type CompiledProjectGraph} from '../input/project-model.js';
import {assertCompiledProjectFields,compileSelectedProjectFields,EXACT_PROJECT_FIELD_SELECTION_VERSION,EXACT_FIELD_CONTRACT_SHA256,type CompiledProjectFields} from '../input/compiled-field-model.js';
import {createCompiledProjectCertificate} from '../compilation/certificate.js';
import {canonicalJson,sha256} from '../input/source-manifest.js';
import {planConfiguredFactories,STRUCTURED_FACTORY_VERSION,STRUCTURED_FACTORY_CONTRACT_SHA256,type FactoryBinding} from './configured-factories.js';
import {planConfiguredEnums,EXACT_CONFIGURED_ENUM_VERSION,ENUM_PROVIDER_SHA256} from './configured-enums.js';
import {annotateEnumDefinition,renderEnumComponent} from './configured-enum-component-source.js';
import {composeValueShape,renderConfiguredSum,valueDependencies,type ConfiguredSumModule} from './configured-sum-source.js';
import * as rules from './configured-rules.js';
import {PROFILED_SOURCE_DIGESTS} from './profiled-project.js';
import {EXACT_UINT64_PROFILE} from './exact-uint64.js';
import type {PlannedArtifact} from './contracts.js';

export const ALGEBRAIC_ENUM_VERSION='domainspec.configured-algebraic-enums-selection/v1-candidate';
export const STANDALONE_SUM_CONTRACT_SHA256='58968ae73145d4663ff8a4cf78e1d2836131ba7ae0d51fb2e53ddf748d22e1cb';
export interface AlgebraicEnumSelection {
 readonly schema_version:typeof ALGEBRAIC_ENUM_VERSION;readonly language:'typescript';readonly module_root:string;
 readonly field_compilation_sha256:string;readonly factories:readonly FactoryBinding[];
}
export interface AlgebraicEnumSources {
 readonly standalone_contract:string;readonly factories:Parameters<typeof planConfiguredFactories>[3];
}
const fail=(reason:string):never=>{throw new Error('DS_ALGEBRAIC_ENUM:'+reason);};
function inert(value:unknown,depth=0):void {
 if(depth>64)fail('data depth');
 if(value===null||typeof value==='string'||typeof value==='boolean'||typeof value==='number'&&Number.isFinite(value))return;
 if(!value||typeof value!=='object')fail('inert data');
 const array=Array.isArray(value),proto=Object.getPrototypeOf(value),descriptors=Object.getOwnPropertyDescriptors(value);
 if(array?proto!==Array.prototype:proto!==Object.prototype&&proto!==null)fail('plain data');
 if(array){const length=descriptors.length!.value;if(length>1024||Reflect.ownKeys(descriptors).length!==length+1)fail('bounded dense array');for(let i=0;i<length;i++)if(!Object.hasOwn(descriptors,String(i)))fail('dense array');}
 for(const key of Reflect.ownKeys(descriptors)){if(array&&key==='length')continue;const d=descriptors[key as string];if(typeof key!=='string'||!d||!Object.hasOwn(d,'value')||!d.enumerable)fail('inert fields');inert(d!.value,depth+1);}
}
function keys(value:object,expected:readonly string[]){if(!value||Array.isArray(value)||canonicalJson(Object.keys(value).sort())!==canonicalJson([...expected].sort()))fail('closed fields');}
const freeze=<T>(value:T):T=>{if(value&&typeof value==='object'&&!Object.isFrozen(value)){Object.values(value).forEach(freeze);Object.freeze(value);}return value;};
const reserved=new Set(('as async await break case catch class const continue crate debugger def default del do else enum except export extends false finally fn for from function global if impl import in interface is lambda let loop match mod move mut new nonlocal null package pass private protected pub public raise ref return self static struct super switch this throw trait true try type typeof unsafe use var void while with yield con prn aux nul '+Array.from({length:9},(_,i)=>`com${i+1} lpt${i+1}`).join(' ')).split(' '));
const portable=(value:string)=>typeof value==='string'&&/^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$/.exec(value)?.[0]===value&&!reserved.has(value);

/** Enum-root closure over the existing owned sum and record component protocols.
 * No artificial record or Rule is introduced for an Enum-only closure.
 */
export function planConfiguredAlgebraicEnums(graph:CompiledProjectGraph,fields:CompiledProjectFields,selection:AlgebraicEnumSelection,sources:AlgebraicEnumSources){
 assertCompiledProjectSnapshot(graph);assertCompiledProjectFields(fields);inert(selection);inert(sources);
 keys(selection,['schema_version','language','module_root','field_compilation_sha256','factories']);keys(sources,['standalone_contract','factories']);
 if(selection.schema_version!==ALGEBRAIC_ENUM_VERSION||selection.language!=='typescript'||typeof selection.module_root!=='string'||!selection.module_root.split('/').every(portable)||!Array.isArray(selection.factories))fail('selection');
 if(fields.selection.schema_version!==EXACT_PROJECT_FIELD_SELECTION_VERSION||selection.field_compilation_sha256!==fields.compilation_sha256||canonicalJson(fields.certificate)!==canonicalJson(createCompiledProjectCertificate(graph)))fail('exact current fields required');
 const expected={configuration:rules.RULE_CONFIGURATION_SHA256,...PROFILED_SOURCE_DIGESTS,factory_contract:STRUCTURED_FACTORY_CONTRACT_SHA256,enum_provider:ENUM_PROVIDER_SHA256,field_contract:EXACT_FIELD_CONTRACT_SHA256,
  rule_contract:rules.STRING_ORDER_RULE_CONTRACT_SHA256,collection_contract:rules.COLLECTION_VALUE_RULE_CONTRACT_SHA256,predicate_contract:rules.COLLECTION_PREDICATE_RULE_CONTRACT_SHA256,numeric_contract:rules.NUMERIC_RULE_CONTRACT_SHA256,exact_contract:rules.EXACT_RULE_CONTRACT_SHA256,literal_contract:rules.EXACT_LITERAL_RULE_CONTRACT_SHA256,structured_contract:rules.STRUCTURED_RULE_CONTRACT_SHA256};
 keys(sources.factories,Object.keys(expected));
 if(sha256(sources.standalone_contract)!==STANDALONE_SUM_CONTRACT_SHA256)fail('definition drift');
 for(const key of Object.keys(expected) as (keyof typeof expected)[]){const value=sources.factories[key];if(typeof value!=='string'||sha256(value)!==expected[key])fail('source drift:'+key);}
 const declarations=new Map(fields.model.declarations.map(d=>[d.selector,d]));
 if(!fields.selection.roots.every(s=>declarations.get(s)?.kind==='Enum'))fail('Enum roots required');
 for(const d of declarations.values())if(!d.selector.split(':').every(portable))fail('portable selector');
 const records=fields.model.declarations.filter(d=>d.kind!=='Enum');
 let artifacts:readonly PlannedArtifact[],sumModules:readonly ConfiguredSumModule[],components:readonly {selector:string;relative_path:string;name:string}[],dependencyPlan:string|null=null;
 if(records.length){
  const plan=planConfiguredFactories(graph,fields,{schema_version:STRUCTURED_FACTORY_VERSION,language:'typescript',module_root:selection.module_root,field_compilation_sha256:fields.compilation_sha256,factories:selection.factories,rule_selection:{schema_version:rules.STRUCTURED_RULE_VERSION,value_profile:EXACT_UINT64_PROFILE}},sources.factories);
  artifacts=plan.artifacts;sumModules=plan.sum_modules??[];components=[...plan.modules,...(plan.enum_components??[])];dependencyPlan=plan.plan_sha256;
 }else{
  if(selection.factories.length)fail('no record dependencies to bind');
  const plain=fields.model.declarations.filter(d=>d.kind==='Enum'&&d.contract.variants.every(v=>v.payload===null));
  const sums=fields.model.declarations.filter(d=>d.kind==='Enum'&&d.contract.variants.some(v=>v.payload!==null));
  const sumIds=new Set(sums.map(d=>d.selector));
  const enumFields=plain.length?compileSelectedProjectFields(graph,{schema_version:EXACT_PROJECT_FIELD_SELECTION_VERSION,contract_sha256:EXACT_FIELD_CONTRACT_SHA256,graph_sha256:fields.certificate.graph_sha256,roots:plain.map(d=>d.selector),bindings:[]},sources.factories.field_contract!):null;
  const enumPlan=enumFields?planConfiguredEnums(enumFields,{schema_version:EXACT_CONFIGURED_ENUM_VERSION,language:'typescript',module_root:selection.module_root,field_compilation_sha256:enumFields.compilation_sha256},{configuration:sources.factories.configuration,base:sources.factories.base,typescript:sources.factories.typescript,provider:sources.factories.enum_provider!}):null;
  const artifact=(relative_path:string,content:string):PlannedArtifact=>({relative_path,content,size_bytes:Buffer.byteLength(content),sha256:sha256(content)});
  const enumArtifacts=enumPlan?.artifacts.map(a=>{const module=enumPlan.modules.find(m=>m.relative_path===a.relative_path);return module?artifact(a.relative_path,annotateEnumDefinition(module,a.content)):a;})??[];
  const enumComponents=enumPlan?.modules.map(m=>({selector:m.selector,name:m.symbol,members:m.members,relative_path:m.relative_path.replace(/\.ts$/,'.component.ts'),definition_path:m.relative_path,definition_sha256:enumArtifacts.find(a=>a.relative_path===m.relative_path)!.sha256,unannotated_definition_sha256:enumPlan.artifacts.find(a=>a.relative_path===m.relative_path)!.sha256,definition_import:'./'+path.posix.basename(m.relative_path).replace(/\.ts$/,'.js'),contract_sha256:STRUCTURED_FACTORY_CONTRACT_SHA256}))??[];
  sumModules=sums.map(d=>{
   if(d.kind!=='Enum')return fail('sum declaration');
   const [feature,node]=d.selector.split(':') as [string,string],relative_path=`${selection.module_root}/features/${feature}/src/domain/enums/${node}.sum.ts`;
   const shape=composeValueShape({kind:'sum',variants:d.contract.variants},'payload',(selector,local)=>{
    if(declarations.get(selector)?.kind!=='Enum')return fail('unresolved payload');
    const [f,n]=selector.split(':') as [string,string],kind=sumIds.has(selector)?'Sum':'Enum',symbol=n.split('-').map(w=>w[0]!.toUpperCase()+w.slice(1)).join('');
    const target=`${selection.module_root}/features/${f}/src/domain/enums/${n}.${kind==='Sum'?'sum':'component'}.ts`,relative=path.posix.relative(path.posix.dirname(relative_path),target).replace(/\.ts$/,'.js');
    return {kind,component:{selector,path:relative.startsWith('.')?relative:'./'+relative,symbol:symbol+'ValueComponent',local,type_symbol:symbol+'Case',type_local:local+'Type'}};
   },true);
   return {selector:d.selector,relative_path,name:node.split('-').map(w=>w[0]!.toUpperCase()+w.slice(1)).join(''),shape,contract_sha256:STRUCTURED_FACTORY_CONTRACT_SHA256,uint64_fields:true,entity_fields:true,exact_uint64:true};
  });
  artifacts=[...enumArtifacts,...enumComponents.map(m=>artifact(m.relative_path,renderEnumComponent(m))),...sumModules.map(m=>artifact(m.relative_path,renderConfiguredSum(m)))];components=enumComponents;
 }
 const paths=new Set<string>();for(const a of artifacts){if(paths.has(a.relative_path))fail('artifact collision');paths.add(a.relative_path);}
 const bindings=sumModules.flatMap(m=>valueDependencies(m.shape).map(d=>{const target=[...sumModules,...components].find(c=>c.selector===d.component.selector)??fail('missing dependency');return {owner:m.selector,value_path:d.value_path,target:target.selector,path:target.relative_path,sha256:artifacts.find(a=>a.relative_path===target.relative_path)!.sha256};}));
 const body={schema_version:'domainspec.configured-algebraic-enums-plan/v1-candidate',selection:structuredClone(selection),roots:fields.selection.roots,certificate:fields.certificate,field_compilation_sha256:fields.compilation_sha256,source_digests:{standalone_contract:STANDALONE_SUM_CONTRACT_SHA256,factories:expected},sum_modules:sumModules,components,dependency_plan_sha256:dependencyPlan,component_bindings:bindings,artifacts:[...artifacts].sort((a,b)=>a.relative_path<b.relative_path?-1:1),authority_effect:'none' as const};
 return freeze({...body,plan_sha256:sha256(canonicalJson(body))});
}
