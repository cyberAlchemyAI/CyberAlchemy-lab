import path from 'node:path';
import {assertCompiledProjectSnapshot,type CompiledProjectGraph} from '../input/project-model.js';
import {assertCompiledCompositionBoundary,type CompiledCompositionBoundary} from '../input/composition-boundary.js';
import {assertCompiledProjectFields,EXACT_PROJECT_FIELD_SELECTION_VERSION,type CompiledProjectFields} from '../input/compiled-field-model.js';
import {createCompiledProjectCertificate} from '../compilation/certificate.js';
import {decodeTypedRulePolicyContract,checkTypedRulePolicy,TYPED_POLICY_RULES_VERSION,type TypedRulePolicyContract} from '../typed-backend/policy-rules.js';
import type {TypedRuleContract} from '../typed-operation/contracts.js';
import {canonicalJson,sha256} from '../input/source-manifest.js';
import {EXACT_UINT64_PROFILE} from './exact-uint64.js';
import {planConfiguredRules,STRUCTURED_RULE_VERSION,type RuleConfigurationSources} from './configured-rules.js';
import {renderConfiguredPolicy} from './configured-policy-source.js';
import type {PlannedArtifact} from './contracts.js';
export const CONFIGURED_POLICY_VERSION='domainspec.configured-policies-selection/v1-candidate';
export const POLICY_CONTRACT_SHA256='7fe86c60c892471a91bce1795c7f5a960616aa2b3ec57c4467c38055cf239b2d';
export interface ConfiguredPolicySelection {
 readonly schema_version:typeof CONFIGURED_POLICY_VERSION;
 readonly language:'typescript';
 readonly value_profile:typeof EXACT_UINT64_PROFILE;
 readonly rule_selection:typeof STRUCTURED_RULE_VERSION;
 readonly boundary_sha256:string;
 readonly field_compilation_sha256:string|null;
 readonly module_root:string;
 readonly roots:readonly string[];
}
export interface PolicyConfigurationSources {readonly policy_contract:string;readonly rules:RuleConfigurationSources;}
const fail=(m:string):never=>{throw Error('DS_CONFIGURED_POLICY:'+m);};
const freeze=<T>(v:T):T=>{if(v&&typeof v==='object'&&!Object.isFrozen(v)){Object.values(v).forEach(freeze);Object.freeze(v);}return v;};
const reserved=new Set(('as async await break case catch class const continue crate debugger def default del do else enum except export extends false finally fn for from function global if impl import in interface is lambda let loop match mod move mut new nonlocal null package pass private protected pub public raise ref return self static struct super switch this throw trait true try type typeof unsafe use var void while with yield con prn aux nul '+Array.from({length:9},(_,i)=>'com'+(i+1)+' lpt'+(i+1)).join(' ')).split(' '));
const portable=(s:string)=>/^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$/.test(s)&&!reserved.has(s);
function keys(v:unknown,expected:readonly string[]):void{
 if(!v||typeof v!=='object'||Array.isArray(v)||![Object.prototype,null].includes(Object.getPrototypeOf(v)))fail('plain object required');
 const d=Object.getOwnPropertyDescriptors(v);
 if(Reflect.ownKeys(d).length!==expected.length||Reflect.ownKeys(d).some(k=>typeof k!=='string'||!expected.includes(k))||Object.values(d).some(p=>!Object.hasOwn(p,'value')||!p.enumerable))fail('closed data object required');
}
function frozenLiteral(v:unknown):string{
 if(Array.isArray(v))return 'Object.freeze(['+v.map(frozenLiteral).join(',')+'])';
 if(v&&typeof v==='object')return 'Object.freeze({'+Object.entries(v).map(([k,x])=>'['+JSON.stringify(k)+']:'+frozenLiteral(x)).join(',')+'})';
 return JSON.stringify(v);
}
/** One checked graph, explicit Rule version and immutable strategy catalogue.
 * Scalar-only Policies need no fabricated data root: fields is explicitly null.
 */
export function planConfiguredPolicies(graph:CompiledProjectGraph,boundary:CompiledCompositionBoundary,fields:CompiledProjectFields|null,selection:ConfiguredPolicySelection,sources:PolicyConfigurationSources){
 assertCompiledProjectSnapshot(graph);assertCompiledCompositionBoundary(boundary);if(fields!==null)assertCompiledProjectFields(fields);
 keys(selection,['schema_version','language','value_profile','rule_selection','boundary_sha256','field_compilation_sha256','module_root','roots']);
 keys(sources,['policy_contract','rules']);
 keys(sources.rules,['configuration','base','typescript','rule_contract','collection_contract','predicate_contract','numeric_contract','exact_contract','literal_contract','structured_contract','field_contract']);
 if(selection.schema_version!==CONFIGURED_POLICY_VERSION||selection.language!=='typescript'||selection.value_profile!==EXACT_UINT64_PROFILE||selection.rule_selection!==STRUCTURED_RULE_VERSION)fail('unsupported selection');
 const certificate=createCompiledProjectCertificate(graph);
 if(selection.boundary_sha256!==boundary.boundary_sha256||boundary.certificate.graph_sha256!==certificate.graph_sha256||selection.field_compilation_sha256!==(fields?.compilation_sha256??null)||fields&&fields.certificate.graph_sha256!==certificate.graph_sha256)fail('stale or cross-graph selection');
 if(fields&&fields.selection.schema_version!==EXACT_PROJECT_FIELD_SELECTION_VERSION)fail('exact checked fields required');
 if(typeof selection.module_root!=='string'||!selection.module_root.split('/').every(portable))fail('unsafe module root');
 if(typeof sources.policy_contract!=='string'||sha256(sources.policy_contract)!==POLICY_CONTRACT_SHA256)fail('source drift:policy_contract');
 if(!Array.isArray(selection.roots)||Object.getPrototypeOf(selection.roots)!==Array.prototype)fail('plain roots required');
 const d:Record<string,PropertyDescriptor>=Object.getOwnPropertyDescriptors(selection.roots),length=d.length!.value;
 if(!Number.isSafeInteger(length)||length<1||Reflect.ownKeys(d).length!==length+1)fail('nonempty dense roots required');
 const roots:string[]=[];for(let i=0;i<length;i++){const p=d[String(i)];if(!p||!Object.hasOwn(p,'value')||!p.enumerable||typeof p.value!=='string')return fail('inert roots required');roots.push(p.value);}
 if(new Set(roots).size!==roots.length)fail('duplicate roots');roots.sort();
 const contracts=new Map<string,TypedRulePolicyContract>();
 for(const selector of roots){
  if(selector.split(':').length!==2||!selector.split(':').every(portable))fail('unsafe selector');
  const n=graph.nodes.find(n=>n.selector===selector);
  if(n?.kind!=='Policy'||(n.body.typed_contract as {schema_version?:string})?.schema_version!==TYPED_POLICY_RULES_VERSION)fail('typed Policy v2 required; explicitly extract legacy predicates into named Rules:'+selector);
  const contract=decodeTypedRulePolicyContract(n!.body.typed_contract);
  if(!contract.inputs.length||new Set([...contract.cases.map(c=>c.target),contract.default_target]).size<2)fail('Policy profile requires explicit inputs and distinct selectable strategies; input sensitivity needs behavioral witnesses');
  contracts.set(selector,contract);
 }
 const ruleRoots=[...new Set([...contracts.values()].flatMap(c=>c.cases.map(x=>x.rule.selector)))].sort();
 const rulePlan=planConfiguredRules(graph,{schema_version:selection.rule_selection,language:'typescript',module_root:selection.module_root,value_profile:selection.value_profile,roots:ruleRoots},sources.rules);
 const config=JSON.parse(sources.rules.configuration),cell=config.types.find((t:{kind:string})=>t.kind==='Policy');
 if(cell?.role!=='domain/policies'||canonicalJson(cell.blocked_by)!=='["DSR-011","DSR-015"]')fail('unexpected Policy configuration');
 const profile=JSON.parse(sources.rules.typescript),overlay=profile.representation_overlays.find((p:{contract_id:string})=>p.contract_id==='policy.profile-representation'),protocol=overlay?.candidate_protocols.find((p:{protocol_id:string})=>p.protocol_id==='typescript.bound-policy/v1');
 if(protocol?.form_id!=='typescript.policy-selector-arrow-function')fail('missing Policy protocol');
 const ruleContracts=graph.nodes.filter(n=>n.kind==='Rule'&&n.body.typed_contract).map(n=>({selector:n.selector,contract:n.body.typed_contract as TypedRuleContract}));
 const artifacts:PlannedArtifact[]=[...rulePlan.artifacts];
 const add=(relative_path:string,content:string)=>{if(artifacts.some(a=>a.relative_path===relative_path))fail('artifact collision');const a={relative_path,content,size_bytes:Buffer.byteLength(content),sha256:sha256(content)};artifacts.push(a);return a;};
 const modules=roots.map(selector=>{
  const contract=contracts.get(selector)!;checkTypedRulePolicy(contract,fields?.model.declarations??[],ruleContracts);
  const [feature,node]=selector.split(':') as [string,string],relative_path=selection.module_root+'/features/'+feature+'/src/'+cell.role+'/'+node+'.ts',provider_path=relative_path.replace(/\.ts$/,'.provider.ts');
  const imports=[...new Set(contract.cases.map(c=>c.rule.selector))].sort().map((selector,i)=>{
   const m=rulePlan.modules.find(m=>m.selector===selector)??fail('missing Rule module');
   const p=path.posix.relative(path.posix.dirname(provider_path),m.relative_path).replace(/\.ts$/,'.js');
   return {selector,path:p.startsWith('.')?p:'./'+p,symbol:m.callable,local:'condition'+i};
  });
  const catalogue=[...new Set([...contract.cases.map(c=>c.target),contract.default_target])].sort().map(selector=>{
   const node=graph.nodes.find(n=>n.selector===selector)??fail('unknown strategy'),bound=boundary.domain_graph.nodes.find(n=>n.selector===selector)??fail('unbound strategy');
   if(!['Operation','Calculation'].includes(node.kind))fail('invalid strategy kind');
   return {selector,kind:node.kind,source:bound.source,body_sha256:sha256(canonicalJson(node.body))};
  });
  const evidence=boundary.value_bindings.core_contracts.find(c=>c.owner.selector===selector&&c.kind==='Policy')??fail('unbound Policy');
  const provider=add(provider_path,renderConfiguredPolicy(contract,fields?.model??null,imports)),callable='policy'+node.split('-').map(x=>x[0]!.toUpperCase()+x.slice(1)).join('');
  const descriptorBody={schema_version:'domainspec.generated-policy-descriptor/v1-candidate',protocol_id:'typescript.bound-policy/v1',selector,ontology_policy:contract.ontology_policy,source:evidence.source,contract_sha256:sha256(canonicalJson(contract)),
   inputs:contract.inputs,cases:contract.cases,default_target:contract.default_target,catalogue,strategy_set_sha256:sha256(canonicalJson(catalogue)),
   rule_plan_sha256:rulePlan.plan_sha256,rule_dependencies:imports.map(i=>{const m=rulePlan.modules.find(m=>m.selector===i.selector)!;return {selector:i.selector,closure_sha256:m.closure_sha256,path:m.relative_path,sha256:rulePlan.artifacts.find(a=>a.relative_path===m.relative_path)!.sha256};}),
   field_model_sha256:fields?.model.model_sha256??null,value_profile:selection.value_profile,return_semantics:'strategy',effect_contract:'none',dependency_contract:'explicit-inputs-only',result_consumption:'complete',primary_callable_count:1,evaluation:'ordered-first-true-otherwise-default',failures:['POLICY_INPUT','RULE_INPUT'],provider:{sha256:provider.sha256},authority_effect:'none'};
  const descriptor={...descriptorBody,descriptor_sha256:sha256(canonicalJson(descriptorBody))};
  add(relative_path,'import {select} from '+JSON.stringify('./'+node+'.provider.js')+';\nexport const '+callable+'=Object.freeze(Object.assign(select,{descriptor:'+frozenLiteral(descriptor)+'}));\n');
  return {selector,relative_path,provider_path,callable,imports,descriptor};
 });
 artifacts.sort((a,b)=>a.relative_path<b.relative_path?-1:1);
 const body={schema_version:'domainspec.configured-policies-plan/v1-candidate' as const,selection:{...selection,roots},certificate,boundary_sha256:boundary.boundary_sha256,field_compilation_sha256:fields?.compilation_sha256??null,
  source_digests:{policy_contract:POLICY_CONTRACT_SHA256,rules:rulePlan.profile_digests,configuration:rulePlan.configuration_source_sha256},rule_plan:rulePlan,modules,artifacts,authority_effect:'none' as const};
 return freeze({...body,plan_sha256:sha256(canonicalJson(body))});
}
