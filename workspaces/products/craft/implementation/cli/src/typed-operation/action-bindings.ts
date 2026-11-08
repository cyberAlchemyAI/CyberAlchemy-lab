import {MINIMAL_VALUE_CONTEXT_SHA256} from '../generation/reconciled-sources.js';
import {assertCompiledProjectSnapshot,type CompiledProjectGraph} from '../input/project-model.js';
import {assertCompiledCompositionBoundary,type CompiledCompositionBoundary} from '../input/composition-boundary.js';
import {assertCompiledProjectFields,EXACT_PROJECT_FIELD_SELECTION_VERSION,type CompiledProjectFields} from '../input/compiled-field-model.js';
import {createCompiledProjectCertificate} from '../compilation/certificate.js';
import {canonicalJson,sha256} from '../input/source-manifest.js';
import {decodeTypedType,decodeValueExpression,type TypedParameter,type TypedType,type ValueExpression,type TypedRuleContract} from './contracts.js';
import {createTypedValueChecker} from './value-bindings.js';
import type {EventSource} from '../generation/configured-event-source.js';
import {assertTypedOperationValueComposition,type TypedOperationValueComposition} from './value-composition-types.js';

export const OPERATION_ACTION_BINDINGS_VERSION='domainspec.operation-action-bindings/v1-candidate';
export const OPERATION_ACTION_CONTRACT_SHA256='a28978131d9bd677293bc2a13cbdb2f09182cbe30201abd64b27670969c440b8';
export interface OperationActionBindings {
  readonly schema_version:typeof OPERATION_ACTION_BINDINGS_VERSION;
  readonly selector:string;
  readonly inputs:readonly TypedParameter[];
  readonly reads:readonly Readonly<{slot:string;target:string;parameter:string;key:ValueExpression}>[];
  readonly guards:readonly Readonly<{selector:string;arguments:readonly Readonly<{parameter:string;value:ValueExpression}>[]}>[];
  readonly writes:readonly Readonly<{slot:string;target:string;mode:'create'|'replace'|'delete';value:ValueExpression}>[];
  readonly events:readonly Readonly<{slot:string;target:string;parameter:string}>[];
  readonly result:Readonly<{type:TypedType;value:ValueExpression}>;
  readonly atomicity:'state-and-outbox';
  readonly continuation:'awaited-settlement';
}
export class OperationActionError extends Error {
  constructor(readonly code:string,readonly pointer:string){super(code+':'+pointer);this.name='OperationActionError';}
}
const fail=(code:string,pointer:string):never=>{throw new OperationActionError('OPERATION_ACTION_'+code,pointer);};
const selectorPattern=/^[a-z][a-z0-9]*(?:-[a-z0-9]+)*:[a-z][a-z0-9]*(?:-[a-z0-9]+)*$/;
const parameterPattern=/^[a-z][a-z0-9]*(?:_[a-z0-9]+)*$/;
const freeze=<T>(v:T):T=>{if(v&&typeof v==='object'&&!Object.isFrozen(v)){Object.values(v).forEach(freeze);Object.freeze(v);}return v;};

// A bounded inert-data preflight precedes existing decoders. Getter/proxy
// isolation in an arbitrary realm is not claimed; ordinary getters are not read.
function assertData(root:unknown):void {
  let count=0;
  const visit=(value:unknown,depth:number):void=>{
    if(++count>20000||depth>64)fail('LIMIT','/');
    if(value===null||typeof value==='string'||typeof value==='boolean'||typeof value==='number'&&Number.isFinite(value))return;
    if(!value||typeof value!=='object')fail('DATA','/');
    const array=Array.isArray(value),proto=Object.getPrototypeOf(value);
    if(array?proto!==Array.prototype:proto!==Object.prototype&&proto!==null)fail('DATA','/');
    const d=Object.getOwnPropertyDescriptors(value),keys=Reflect.ownKeys(d);
    if(keys.length>2048)fail('LIMIT','/');
    if(array){const length=d.length!.value;if(length>1024||keys.length!==length+1)fail('DATA','/array');for(let i=0;i<length;i++)if(!Object.hasOwn(d,String(i)))fail('DATA','/array');}
    for(const key of keys){if(array&&key==='length')continue;const p=d[key as string];if(typeof key!=='string'||!p||!Object.hasOwn(p,'value')||!p.enumerable)fail('DATA','/');visit(p!.value,depth+1);}
  };
  visit(root,0);
}
function object(v:unknown,keys:readonly string[],pointer:string):Record<string,unknown>{
  if(!v||typeof v!=='object'||Array.isArray(v)||canonicalJson(Object.keys(v).sort())!==canonicalJson([...keys].sort()))fail('SCHEMA',pointer);
  return v as Record<string,unknown>;
}
function text(v:unknown,pointer:string,pattern?:RegExp):string{
  if(typeof v!=='string'||!v.length||v.length>256||pattern&&pattern.exec(v)?.[0]!==v)return fail('IDENTIFIER',pointer);
  return v;
}
function list(v:unknown,pointer:string,min=0):readonly unknown[]{
  if(!Array.isArray(v)||v.length<min||v.length>128)fail('ARRAY',pointer);
  return v as readonly unknown[];
}
function unique(values:readonly string[],pointer:string):void{if(new Set(values).size!==values.length)fail('DUPLICATE',pointer);}

export function decodeOperationActionBindings(value:unknown):OperationActionBindings {
  assertData(value);
  const c=object(value,['schema_version','selector','inputs','reads','guards','writes','events','result','atomicity','continuation'],'/');
  if(c.schema_version!==OPERATION_ACTION_BINDINGS_VERSION||c.atomicity!=='state-and-outbox'||c.continuation!=='awaited-settlement')fail('VERSION','/');
  const inputs=list(c.inputs,'/inputs').map((v,i)=>{const p=object(v,['name','type'],'/inputs/'+i);return {name:text(p.name,'/inputs/'+i,parameterPattern),type:decodeTypedType(p.type)};});
  const reads=list(c.reads,'/reads').map((v,i)=>{const p=object(v,['slot','target','parameter','key'],'/reads/'+i);return {slot:text(p.slot,'/reads/'+i),target:text(p.target,'/reads/'+i,selectorPattern),parameter:text(p.parameter,'/reads/'+i,parameterPattern),key:decodeValueExpression(p.key,'/reads/'+i+'/key',true)};});
  const guards=list(c.guards,'/guards',1).map((v,i)=>{
    const p=object(v,['selector','arguments'],'/guards/'+i);
    const args=list(p.arguments,'/guards/'+i+'/arguments').map((v,j)=>{const a=object(v,['parameter','value'],'/guards/'+i+'/arguments/'+j);return {parameter:text(a.parameter,'/guards/'+i,parameterPattern),value:decodeValueExpression(a.value,'/guards/'+i+'/arguments/'+j,true)};});
    unique(args.map(a=>a.parameter),'/guards/'+i+'/arguments');
    return {selector:text(p.selector,'/guards/'+i,selectorPattern),arguments:args};
  });
  const writes=list(c.writes,'/writes').map((v,i)=>{
    const p=object(v,['slot','target','mode','value'],'/writes/'+i);
    if(p.mode!=='create'&&p.mode!=='replace'&&p.mode!=='delete')fail('WRITE_MODE','/writes/'+i);
    return {slot:text(p.slot,'/writes/'+i),target:text(p.target,'/writes/'+i,selectorPattern),mode:p.mode as 'create'|'replace'|'delete',value:decodeValueExpression(p.value,'/writes/'+i+'/value',true)};
  });
  const events=list(c.events,'/events').map((v,i)=>{const p=object(v,['slot','target','parameter'],'/events/'+i);return {slot:text(p.slot,'/events/'+i),target:text(p.target,'/events/'+i,selectorPattern),parameter:text(p.parameter,'/events/'+i,parameterPattern)};});
  const result=object(c.result,['type','value'],'/result');
  unique([...inputs.map(p=>p.name),...reads.map(p=>p.parameter),...events.map(p=>p.parameter)],'/parameters');
  for(const [name,rows] of [['reads',reads],['writes',writes],['events',events]] as const)unique(rows.map(r=>r.slot),'/'+name+'/slots');
  unique(guards.map(g=>g.selector),'/guards');
  return freeze({schema_version:OPERATION_ACTION_BINDINGS_VERSION,selector:text(c.selector,'/selector',selectorPattern),inputs,reads,guards,writes,events,
    result:{type:decodeTypedType(result.type),value:decodeValueExpression(result.value,'/result/value',true)},atomicity:'state-and-outbox',continuation:'awaited-settlement'});
}

const checked=new WeakSet<object>();
export type CheckedOperationAction=ReturnType<typeof compileOperationActionBindings>;
export function assertCheckedOperationAction(value:unknown):asserts value is CheckedOperationAction{
  if(!value||typeof value!=='object'||!checked.has(value))fail('UNVALIDATED','/');
}

/** Check explicit action meaning before any generator or transaction executes.
 * Binding slots are not canonical graph edges, and graph metadata is not an
 * implementation of an atomic provider. Legacy typed Operation v1 is separate.
 */
export function compileOperationActionBindings(graph:CompiledProjectGraph,boundary:CompiledCompositionBoundary,fields:CompiledProjectFields|null,value:unknown,contractSource:string){
  const result=compileOperationActionCore(graph,boundary,fields,value,contractSource,null);
  checked.add(result);return result;
}

const composedChecked=new WeakSet<object>();
export type CheckedComposedOperationAction=ReturnType<typeof compileComposedOperationActionBindings>;
export function assertCheckedComposedOperationAction(value:unknown):asserts value is CheckedComposedOperationAction{
  if(!value||typeof value!=='object'||!composedChecked.has(value))fail('UNVALIDATED_COMPOSITION','/');
}

/** Complete action checking over computed values. Old generators must reject
 * this separate custody rather than silently drop Query/Mapping preparation.
 */
export function compileComposedOperationActionBindings(graph:CompiledProjectGraph,boundary:CompiledCompositionBoundary,fields:CompiledProjectFields,composition:TypedOperationValueComposition,contractSource:string){
  assertTypedOperationValueComposition(composition);
  const base=compileOperationActionCore(graph,boundary,fields,composition.references.action,contractSource,composition);
  const {action_sha256:_,schema_version:__,...action}=base;
  const body={...action,schema_version:'domainspec.checked-composed-operation-action/v1-candidate' as const,value_composition:composition,
    execution_obligations:[...action.execution_obligations,'transaction-scoped-query-sources','named-value-calls-before-guards','preserve-query-cardinality-and-projection','explicit-absence-outcome-binding'] as const};
  const result=freeze({...body,action_sha256:sha256(canonicalJson(body))});composedChecked.add(result);return result;
}

function compileOperationActionCore(graph:CompiledProjectGraph,boundary:CompiledCompositionBoundary,fields:CompiledProjectFields|null,value:unknown,contractSource:string,composition:TypedOperationValueComposition|null){
  assertCompiledProjectSnapshot(graph);assertCompiledCompositionBoundary(boundary);if(fields!==null)assertCompiledProjectFields(fields);
  if(typeof contractSource!=='string'||sha256(contractSource)!==OPERATION_ACTION_CONTRACT_SHA256)fail('CONTRACT_DRIFT','/contract');
  const certificate=createCompiledProjectCertificate(graph);
  if(boundary.certificate.graph_sha256!==certificate.graph_sha256||(fields!==null&&fields.certificate.graph_sha256!==certificate.graph_sha256))fail('CROSS_GRAPH','/');
  if(fields!==null&&fields.selection.schema_version!==EXACT_PROJECT_FIELD_SELECTION_VERSION)fail('VALUE_PROFILE','/fields');
  const bindings=decodeOperationActionBindings(value),node=graph.nodes.find(n=>n.selector===bindings.selector);
  if(composition!==null){
    assertTypedOperationValueComposition(composition);
    const refs=composition.references;
    if(refs.certificate.graph_sha256!==certificate.graph_sha256||refs.boundary_sha256!==boundary.boundary_sha256||refs.field_compilation_sha256!==(fields?.compilation_sha256??null))fail('CROSS_GRAPH','/composition');
    if(canonicalJson(refs.action)!==canonicalJson(bindings))fail('COMPOSITION_ACTION_DRIFT','/composition');
  }
  if(node?.kind!=='Operation')return fail('ROOT','/selector');
  if(node.body.typed_contract!==undefined)fail('LEGACY_TYPED_SOURCE','/selector');
  const evidence=(selector:string)=>{
    const node=graph.nodes.find(n=>n.selector===selector),source=boundary.domain_graph.nodes.find(n=>n.selector===selector);
    if(!node||!source)fail('MISSING_NODE',selector);
    return {selector,kind:node!.kind,source:source!.source,body_sha256:sha256(canonicalJson(node!.body))};
  };
  const sameSet=(left:readonly string[],right:readonly string[],pointer:string)=>{
    if(canonicalJson([...new Set(left)].sort())!==canonicalJson([...new Set(right)].sort()))fail('COVERAGE',pointer);
  };
  const slots=(name:'reads'|'writes'|'effects',rows:readonly {slot:string}[])=>{
    const declared=node.body[name] as readonly string[];
    if(!Array.isArray(declared)||new Set(declared).size!==declared.length)fail('SOURCE_SLOTS','/'+name);
    sameSet(declared,rows.map(r=>r.slot),'/'+name);
  };
  const readCoverage=composition?.references.source_slots??bindings.reads;
  slots('reads',readCoverage);slots('writes',bindings.writes);slots('effects',bindings.events);
  const incoming=(relation:string)=>graph.relationships.filter(r=>r.relationship===relation&&r.target.feature_id+':'+r.target.node_id===bindings.selector).map(r=>r.source.feature_id+':'+r.source.node_id);
  const outgoing=(relation:string)=>graph.relationships.filter(r=>r.relationship===relation&&r.source.feature_id+':'+r.source.node_id===bindings.selector).map(r=>r.target.feature_id+':'+r.target.node_id);
  sameSet(outgoing('reads'),readCoverage.map(r=>r.target),'/relationships/reads');
  sameSet(outgoing('creates'),bindings.writes.filter(w=>w.mode==='create').map(w=>w.target),'/relationships/creates');
  sameSet(outgoing('produces'),bindings.events.map(e=>e.target),'/relationships/produces');
  sameSet(incoming('enforces'),bindings.guards.map(g=>g.selector),'/relationships/enforces');
  const primary=node.body.guard as string;
  if(!bindings.guards.some(g=>g.selector===primary||g.selector===node.feature_id+':'+primary))fail('PRIMARY_GUARD','/guards');
  const checker=createTypedValueChecker(fields?.model.declarations??[],message=>fail('TYPE',message));
  const entity=(selector:string)=>{
    const d=checker.get(selector);if(d.kind!=='Entity')return fail('ENTITY_TARGET',selector);
    const identity=d.contract.properties.filter(p=>p.identity);
    if(identity.length!==1)fail('IDENTITY',selector);
    return {declaration:d,identity:identity[0]!};
  };
  const initial=new Map(bindings.inputs.map(p=>[p.name,p.type]));bindings.inputs.forEach(p=>checker.checkType(p.type));
  const scope=new Map(initial);
  const reads=bindings.reads.map(r=>{
    const {identity}=entity(r.target),keyType=checker.infer(r.key,initial);
    if(canonicalJson(keyType)!==canonicalJson(identity.type))fail('READ_KEY_TYPE','/reads/'+r.slot);
    scope.set(r.parameter,{kind:'named',selector:r.target});
    return {...r,identity:{property:identity.ontology_property,name:identity.name,type:identity.type},source:evidence(r.target)};
  });
  const inferConsumer=(value:ValueExpression)=>{
    if(composition===null)return checker.infer(value,scope);
    const entry=composition.consumers.find(c=>canonicalJson(c.value)===canonicalJson(value));
    return entry?.type??fail('COMPOSITION_CONSUMER','/composition');
  };
  const guards=bindings.guards.map(g=>{
    const target=graph.nodes.find(n=>n.selector===g.selector),rule=target?.body.typed_contract as TypedRuleContract|undefined;
    if(target?.kind!=='Rule'||!rule||!['domainspec.typed-rule/v1','domainspec.typed-rule/v2'].includes(rule.schema_version))return fail('TYPED_GUARD','/guards/'+g.selector);
    const args=new Map(g.arguments.map(a=>[a.parameter,a.value]));
    if(args.size!==rule.parameters.length||rule.parameters.some(p=>!args.has(p.name)))fail('GUARD_ARGUMENTS','/guards/'+g.selector);
    for(const p of rule.parameters)if(canonicalJson(inferConsumer(args.get(p.name)!))!==canonicalJson(p.type))fail('GUARD_ARGUMENT_TYPE','/guards/'+g.selector+'/'+p.name);
    return {...g,contract:rule,source:evidence(g.selector)};
  });
  const writes=bindings.writes.map(w=>{
    const {identity}=entity(w.target);
    if(canonicalJson(inferConsumer(w.value))!==canonicalJson({kind:'named',selector:w.target}))fail('WRITE_VALUE_TYPE','/writes/'+w.slot);
    return {...w,identity:{property:identity.ontology_property,name:identity.name,type:identity.type},source:evidence(w.target)};
  });
  const events=bindings.events.map(e=>{
    const target=graph.nodes.find(n=>n.selector===e.target);if(target?.kind!=='Event')return fail('EVENT_TARGET','/events/'+e.slot);
    return {...e,contract:structuredClone(target.body) as unknown as EventSource,source:evidence(e.target)};
  });
  checker.checkType(bindings.result.type);
  if(canonicalJson(inferConsumer(bindings.result.value))!==canonicalJson(bindings.result.type))fail('RESULT_TYPE','/result');
  const body={schema_version:'domainspec.checked-operation-action/v1-candidate' as const,bindings,bindings_sha256:sha256(canonicalJson(bindings)),contract_sha256:OPERATION_ACTION_CONTRACT_SHA256,
    certificate,boundary_sha256:boundary.boundary_sha256,field_compilation_sha256:fields?.compilation_sha256??null,...(fields===null?{minimal_context_sha256:MINIMAL_VALUE_CONTEXT_SHA256}:{}),source:evidence(bindings.selector),reads,guards,writes,events,
    failure_continuation:node.body.failure_continuation as string,
    execution_obligations:['transactional-read-identity-check','guard-before-mutation','owned-value-validation-before-writes','single-preparation','state-and-outbox-atomicity','explicit-commit-outcome','no-automatic-retry-on-uncertainty','no-event-publication'] as const,
    execution:'not-performed' as const,authority_effect:'none' as const};
  return freeze({...body,action_sha256:sha256(canonicalJson(body))});
}
