import {closeSync,constants,fstatSync,lstatSync,openSync,readSync} from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {assertCompiledProjectSnapshot,selectCompiledProjectNode,type CompiledProjectGraph} from '../input/project-model.js';
import {createCompiledProjectCertificate} from '../compilation/certificate.js';
import {compileSelectedProjectFields,assertCompiledProjectFields,EXACT_PROJECT_FIELD_SELECTION_VERSION,EXACT_FIELD_CONTRACT_SHA256,type CompiledProjectFields} from '../input/compiled-field-model.js';
import {getReconciledSource} from '../generation/reconciled-sources.js';
import {decodeTypedRecordContract,type TypedType} from '../typed-operation/contracts.js';
import type {TypedRuleClosureV1} from '../typed-operation/closure.js';
import {createTypedValueChecker} from '../typed-operation/value-bindings.js';
import {decodeNamedInterface,checkInterfacePublicClosure,type NamedInterfaceContract} from '../typed-backend/interface.js';
import {decodePublicMapping,checkPublicMapping} from '../typed-backend/mapping-public.js';
import {checkCoreDirectBusinessRecipeV2,type CoreDirectRecipeDataV2} from '../profile-engine/business-authoring-recipes.js';
import {captureJson,dataDigest,reject,sha256} from '../profile-engine/contracts.js';
import type {U0TypedClosureOriginV2,U0CheckedBusinessGraphV2,DirectConditionBindingV2} from '../profile-engine/business-authoring-stages-v2.js';

/** Actual direct-source graph/typing owners; no FormalClaim substitution.
 * Open Questions: U04/G01 actual accepted input, generated/native/installed joins. */
export interface DirectPureOperationPlanV2 {
 readonly kind:'checked-direct-pure-operation-plan-v2';readonly operation_ref:string;
 readonly input:Readonly<{name:string;type:TypedType}>;readonly output:TypedType;
 readonly guard:Readonly<{selector:string;parameter:string;value:Readonly<{op:'path';root:string;properties:readonly []}>}>;
 readonly result:Readonly<{op:'path';root:string;properties:readonly []}>;
 readonly rejection_code:string;readonly effects:readonly [];readonly authority_effect:'none';readonly plan_sha256:string;
}
export interface CheckedDirectBusinessSourceGraphV2 {
 readonly kind:'checked-direct-business-source-graph-v2';readonly checked:CoreDirectRecipeDataV2;
 readonly graph:CompiledProjectGraph;readonly fields:CompiledProjectFields;readonly rule:TypedRuleClosureV1;
 readonly api:NamedInterfaceContract;readonly operation:DirectPureOperationPlanV2;
 readonly closures:readonly U0TypedClosureOriginV2[];readonly graph_sha256:string;
 readonly check_sha256:string;readonly authority_effect:'none';
}
interface PhysicalFile {readonly path:string;readonly sha256:string;readonly bytes:number;readonly fingerprint:string}
function fail(code:string,at:string,message:string):never{return reject('BUSINESS_DIRECT_CONDITION_'+code,at,message);}
function equal(actual:unknown,expected:unknown,at:string):void{if(dataDigest(actual)!==dataDigest(expected))fail('CORRESPONDENCE',at,'exact independently checked business/source/typed role required');}
function physicalFile(file:string):PhysicalFile {
 if(!path.isAbsolute(file)||path.normalize(file)!==file||/[\\\u0000-\u001f\u007f]/.test(file))fail('FILE',file,'normalized absolute source required');
 const parents=()=>{
  let at=path.parse(file).root;const rows:string[]=[];
  for(const part of ['',...path.dirname(file).slice(at.length).split(path.sep).filter(Boolean)]){
   if(part)at=path.join(at,part);const stat=lstatSync(at,{bigint:true});if(!stat.isDirectory()||stat.isSymbolicLink())fail('FILE',file,'original nonsymlink parents required');rows.push(at+':'+stat.dev+':'+stat.ino);
  }return rows;
 };
 const chain=parents(),before=lstatSync(file,{bigint:true});if(!before.isFile()||before.isSymbolicLink()||before.size<1n||before.size>16777216n)fail('FILE',file,'bounded regular original source required');
 const identity=(stat:typeof before)=>[stat.dev,stat.ino,stat.mode,stat.size,stat.mtimeNs,stat.ctimeNs].map(String);
 const fd=openSync(file,constants.O_RDONLY|constants.O_NOFOLLOW|constants.O_NONBLOCK);let size=0;const chunks:Buffer[]=[];
 try{
  equal(identity(fstatSync(fd,{bigint:true})),identity(before),file);
  for(;;){const buffer=Buffer.alloc(65536),n=readSync(fd,buffer,0,buffer.length,null);if(!n)break;size+=n;if(size>16777216)fail('FILE',file,'source byte bound exceeded');chunks.push(buffer.subarray(0,n));}
  equal(identity(fstatSync(fd,{bigint:true})),identity(before),file);
 }finally{closeSync(fd);}
 equal(identity(lstatSync(file,{bigint:true})),identity(before),file);equal(parents(),chain,file);if(size!==Number(before.size))fail('FILE_STALE',file,'source byte count changed');
 const hash=sha256(Buffer.concat(chunks));return {path:file,sha256:hash,bytes:size,fingerprint:dataDigest({file,chain,physical:identity(before),hash})};
}
const extension=path.extname(fileURLToPath(import.meta.url));
const implementationPaths=[import.meta.url,...[
 '../input/project-model','../input/compiled-field-model','../typed-operation/contracts',
 '../typed-operation/closure','../typed-operation/value-bindings','../typed-backend/interface',
 '../typed-backend/mapping-public','../generation/reconciled-sources','../generation/reconciled-sources.generated',
].map(relative=>new URL(relative+extension,import.meta.url).href)];
const implementation=()=>dataDigest(implementationPaths.map(url=>physicalFile(fileURLToPath(url)).fingerprint));
const executingImplementation=implementation();
const sourceGraphs=new WeakMap<object,{graph:CompiledProjectGraph;files:readonly PhysicalFile[];fingerprint:string}>();
export function assertDirectBusinessSourceGraphV2Current(value:CheckedDirectBusinessSourceGraphV2):void {
 const state=value&&typeof value==='object'?sourceGraphs.get(value):undefined;if(!state)fail('HANDLE','/source-graph','original registered direct source graph required');
 if(implementation()!==executingImplementation)fail('IMPLEMENTATION_STALE','/source-graph','reload changed owning typed/source implementations');
 assertCompiledProjectSnapshot(state.graph);assertCompiledProjectFields(value.fields);
 if(value.graph!==state.graph||dataDigest(value)!==state.fingerprint)fail('STALE','/source-graph','original checked source graph changed');
 for(const file of state.files)if(physicalFile(file.path).fingerprint!==file.fingerprint)fail('FILE_STALE',file.path,'original compiled project bytes/physical identity changed');
}
/** Component semantic owner over real compiled project/field/Rule/Interface/Mapping
 * checks. This source-only handle is deliberately not U0CheckedBusinessGraphV2. */
export function checkDirectBusinessSourceGraphV2(graph:CompiledProjectGraph,transfer:unknown):CheckedDirectBusinessSourceGraphV2 {
 assertCompiledProjectSnapshot(graph);if(implementation()!==executingImplementation)fail('IMPLEMENTATION_STALE','/','reload changed typed/source implementations');
 const checked=checkCoreDirectBusinessRecipeV2(transfer),spec=checked.transfer.spec,roles=checked.roles,selectors=roles.selectors;
 if(graph.project_id!==roles.feature||graph.nodes.length!==6||graph.relationships.length!==5||graph.source_manifest.sources.length!==13||(graph.compositions?.length??0))fail('GRAPH_SCOPE','/graph','exact six-role/five-edge direct source graph required');
 const expectedRoles=[['Entity',selectors.entity],['Rule',selectors.rule],['Operation',selectors.operation],['Interface',selectors.entry],['Mapping',selectors.input_mapping],['Mapping',selectors.output_mapping]] as const;
 if(new Set(expectedRoles.map(row=>row[1])).size!==6)fail('GRAPH_SCOPE','/graph','derived role identities collide');
 for(const [kind,selector]of expectedRoles)if(!graph.nodes.some(node=>node.kind===kind&&node.selector===selector))fail('GRAPH_SCOPE',selector,'exact selected role required');
 for(const node of graph.nodes)if(node.authored_forbidden_projection_attributes.length)fail('GRAPH_SCOPE',node.selector,'generated relationship metadata cannot be authored');
 const expectedEdges=[[selectors.entity,'performs',selectors.operation],[selectors.rule,'enforces',selectors.operation],[selectors.entry,'exposes',selectors.operation],[selectors.input_mapping,'maps',selectors.entity],[selectors.output_mapping,'maps',selectors.entry]].map(row=>row.join('|')).sort();
 equal(graph.relationships.map(row=>[row.source.feature_id+':'+row.source.node_id,row.relationship,row.target.feature_id+':'+row.target.node_id].join('|')).sort(),expectedEdges,'/relationships');
 const files=graph.source_manifest.sources.map(source=>{
  const file=physicalFile(path.join(graph.project_root,source.relative_path));if(file.sha256!==source.sha256||file.bytes!==source.size_bytes)fail('FILE_STALE',file.path,'actual project bytes differ from original graph manifest');return file;
 });
 const certificate=createCompiledProjectCertificate(graph),body=(selector:string)=>graph.nodes.find(node=>node.selector===selector)!.body;
 const entity=spec.entities[0]!,rule=spec.rules[0]!,op=spec.operations[0]!,entry=spec.entries[0]!;
 const ontology=(selector:string)=>'BUSINESS-'+roles.feature.toUpperCase()+'-'+selector.split(':')[1]!.toUpperCase();
 const entityOntology=ontology(selectors.entity),publicOntology=ontology(selectors.entry)+'-PAYLOAD';
 const expectedEntity={schema_version:'domainspec.typed-record/v1',ontology_node:entityOntology,properties:entity.fields.map(field=>({name:field.name,type:{kind:'scalar',name:field.type},ontology_property:entityOntology+'#'+field.name,identity:field.name===entity.identity,cardinality:'one',meaning:field.meaning}))};
 equal(body(selectors.entity).typed_contract,expectedEntity,'/entity/typed_contract');equal(body(selectors.entity).fields,entity.fields.map(field=>field.name),'/entity/fields');equal(body(selectors.entity).description,entity.meaning,'/entity/meaning');
 const record=decodeTypedRecordContract(body(selectors.entity).typed_contract);
 const fields=compileSelectedProjectFields(graph,{schema_version:EXACT_PROJECT_FIELD_SELECTION_VERSION,contract_sha256:EXACT_FIELD_CONTRACT_SHA256,graph_sha256:certificate.graph_sha256,roots:[selectors.entity],bindings:[]},getReconciledSource('field'));
 assertCompiledProjectFields(fields);
 const selectedRule=selectCompiledProjectNode(graph,selectors.rule),closure=selectedRule.typed_closure;
 if(!closure||closure.schema_version!=='domainspec.typed-rule-closure/v1'||closure.root_selector!==selectors.rule)fail('RULE','/rule','actual selected typed Rule closure required');
 equal(closure.rule,roles.typed_rule,'/rule/typed_contract');equal(body(selectors.rule).description,rule.meaning,'/rule/meaning');equal(body(selectors.rule).predicate,'structured:domainspec.typed-rule/v1','/rule/predicate');
 const property=record.properties.find(p=>p.ontology_property===roles.typed_rule.expression.left.properties[0]);
 if(!property||property.name!==rule.condition.value.path[0]||property.type.kind!=='scalar'||property.type.name!=='Bool')fail('PROPERTY','/rule','actual declared Bool property required');
 const expectedInterface={schema_version:'domainspec.typed-interface/v1',ontology_interface:ontology(selectors.entry),boundary_kind:'external',version_policy:{schema_version:'domainspec.interface-version-policy/v1',mode:'exact',direction:'consumer-to-provider',provider_version:'1.0.0'},contracts:[{contract_id:'payload',ontology_contract:publicOntology,fields:entity.fields.map(field=>({name:field.name,ontology_field:publicOntology+'#'+field.name,meaning:field.meaning,type:{kind:'scalar',name:field.type}}))}],operations:[{operation_id:entry.public_name,operation_ref:selectors.operation,request:{kind:'contract',contract_id:'payload'},result:{kind:'contract',contract_id:'payload'}}]};
 equal(body(selectors.entry).typed_contract,expectedInterface,'/interface');
 equal(body(selectors.entry).description,'Logical entry '+entry.id+'; '+op.meaning,'/interface/meaning');
 const api=decodeNamedInterface(body(selectors.entry).typed_contract);checkInterfacePublicClosure(api,fields.model.declarations);
 const mappingChecks=([['input',selectors.input_mapping],['result',selectors.output_mapping]] as const).map(([side,selector])=>{
  const input=side==='input',publicType={kind:'contract',interface_selector:selectors.entry,contract_id:'payload'},namedType={kind:'named',selector:selectors.entity};
  const member={interface_selector:selectors.entry,operation_id:entry.public_name,side:input?'request':'result'};
  const expected={schema_version:'domainspec.typed-mapping/v3',ontology_mapping:ontology(selector),inputs:[{name:input?'payload':'value',type:input?publicType:namedType,use:input?member:null}],target:input?namedType:publicType,target_use:input?null:member,fields:entity.fields.map(field=>({target:field.name,value:{op:'path',root:input?'payload':'value',properties:[(input?publicOntology:entityOntology)+'#'+field.name]},default:null})),total:true};
  equal(body(selector).typed_contract,expected,'/mapping/'+side);equal(body(selector).target,input?selectors.entity:selectors.entry,'/mapping/'+side+'/target');
  equal(body(selector).description,'Recipe-derived candidate whole-'+(input?'input':'result')+' mapping for '+entry.id,'/mapping/'+side+'/meaning');
  const mapping=decodePublicMapping(body(selector).typed_contract),result=checkPublicMapping(mapping,fields.model.declarations,[{selector:selectors.entry,contract:api}]);
  return {selector,contract:mapping,checked:result};
 });
 const operation=body(selectors.operation);
 for(const name of ['reads','writes','effects'])equal(operation[name],[],'/operation/'+name);
 equal(operation.guard,selectors.rule,'/operation/guard');equal(operation.failure_continuation,op.on_rejection,'/operation/rejection');equal(operation.description,op.meaning,'/operation/meaning');
 if(operation.typed_contract!==undefined)fail('OPERATION','/operation','pure successor checks must not select legacy settlement/typed operation contracts');
 const checker=createTypedValueChecker(fields.model.declarations,message=>fail('TYPE','/operation',message));
 const inputType:TypedType={kind:'named',selector:selectors.entity},whole={op:'path' as const,root:op.input.name,properties:[] as const};
 checker.checkType(inputType);const inferred=checker.infer(whole,new Map([[op.input.name,inputType]]));
 equal(inferred,inputType,'/operation/result-type');equal(inferred,closure.rule.parameters[0]!.type,'/operation/guard-argument-type');
 const planBody={kind:'checked-direct-pure-operation-plan-v2',operation_ref:selectors.operation,input:{name:op.input.name,type:inputType},output:inputType,guard:{selector:selectors.rule,parameter:rule.input.name,value:whole},result:whole,rejection_code:op.on_rejection,effects:[],authority_effect:'none'};
 const pure=captureJson({...planBody,plan_sha256:dataDigest(planBody)}) as unknown as DirectPureOperationPlanV2;
 const origins=(kind:string,id:string,prefix?:string)=>{
  const spans=spec.source_spans,start=spans.findIndex(span=>span.column===1&&span.text===kind+' '+id+':'),end=spans.findIndex((span,i)=>i>start&&span.column===1);
  if(start<0)fail('ORIGIN','/source','original containing declaration required');
  const rows=spans.slice(start,end<0?undefined:end).filter(span=>!prefix||span.text.trimStart().startsWith(prefix+' '));
  if(!rows.length)fail('ORIGIN','/source','original executable clause required');return rows.map(span=>({source:span.source,selector:span.selector,sha256:span.source_sha256}));
 };
 const proofs=[fields.compilation_sha256,closure.closure_sha256,pure.plan_sha256,dataDigest({graph:certificate.graph_sha256,contract:api,fields:fields.compilation_sha256}),...mappingChecks.map(mapping=>dataDigest({graph:certificate.graph_sha256,fields:fields.compilation_sha256,interface:api,...mapping}))];
 const roleOrigins=[origins('entity',entity.id),origins('rule',rule.id,'condition'),origins('operation',op.id),origins('entry',entry.id),[...origins('entry',entry.id),...origins('entity',entity.id),...origins('operation',op.id,'input')],[...origins('entry',entry.id),...origins('entity',entity.id),...origins('operation',op.id,'returns')]];
 const closures=captureJson(expectedRoles.map(([role,selector],i)=>({role,selector,typed_closure_sha256:proofs[i]!,origins:roleOrigins[i]!}))) as unknown as readonly U0TypedClosureOriginV2[];
 const data={kind:'checked-direct-business-source-graph-v2' as const,checked,graph,fields,rule:closure,api,operation:pure,closures,graph_sha256:certificate.graph_sha256,authority_effect:'none' as const};
 const value:CheckedDirectBusinessSourceGraphV2=Object.freeze({...data,check_sha256:dataDigest(data)});
 sourceGraphs.set(value,{graph,files,fingerprint:dataDigest(value)});assertDirectBusinessSourceGraphV2Current(value);return value;
}

export interface DirectConditionGraphOwnerV2 {
 assertCurrent(graph:U0CheckedBusinessGraphV2):void;
 source(graph:U0CheckedBusinessGraphV2):CheckedDirectBusinessSourceGraphV2;
}
export function createDirectConditionBindingOwnerV2(owner:DirectConditionGraphOwnerV2){
 const assert=owner.assertCurrent,source=owner.source;
 const owned=new WeakMap<object,{graph:U0CheckedBusinessGraphV2;source:CheckedDirectBusinessSourceGraphV2;fingerprint:string}>();
 const assertCurrent=(condition:DirectConditionBindingV2):void=>{
  const state=condition&&typeof condition==='object'?owned.get(condition):undefined;if(!state)fail('HANDLE','/condition','original direct condition owner handle required');
  if(owner.assertCurrent!==assert||owner.source!==source)fail('OWNER_STALE','/condition','exact original graph owner changed');
  owner.assertCurrent(state.graph);assertDirectBusinessSourceGraphV2Current(state.source);
  if(condition.graph!==state.graph||owner.source(state.graph)!==state.source||dataDigest(condition)!==state.fingerprint)fail('STALE','/condition','original condition/graph/source correspondence changed');
 };
 return Object.freeze({bind(graph:U0CheckedBusinessGraphV2):DirectConditionBindingV2{
  if(owner.assertCurrent!==assert||owner.source!==source)fail('OWNER_STALE','/condition','exact original graph owner changed');
  owner.assertCurrent(graph);const checked=owner.source(graph);assertDirectBusinessSourceGraphV2Current(checked);
  const spec=checked.checked.transfer.spec,rule=spec.rules[0]!,selectors=checked.checked.roles.selectors;
  if(graph.input.spec.identity.namespace!==spec.identity.namespace||graph.input.capture.source.sha256!==checked.checked.transfer.source.sha256||graph.input.selection.models[0]!.executable_sha256!==checked.checked.executable_sha256)fail('CORRESPONDENCE','/condition','original accepted graph and exact source required');
  const body={kind:'direct-condition-binding-v2' as const,graph,rule_ref:selectors.rule,parameter:rule.input.name,entity_ref:selectors.entity,field_name:rule.condition.value.path[0],property_selector:checked.checked.roles.typed_rule.expression.left.properties[0],authority_effect:'none' as const};
  const condition:DirectConditionBindingV2=Object.freeze({...body,condition_sha256:dataDigest(body)});
  owned.set(condition,{graph,source:checked,fingerprint:dataDigest(condition)});assertCurrent(condition);return condition;
 },assertCurrent});
}
