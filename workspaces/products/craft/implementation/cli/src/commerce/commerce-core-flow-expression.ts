import {coreGenericAdmissionMode,type CoreGenericAdmissionMode} from './commerce-core-types.js';
/** Typed expression facet for structured roles. Native observations stay at
 * their original expression callsites; this is not an executable hoisting plan.
 * Open Questions: docs/COMMERCE-CONTRACTS.md#open-questions. */
import {coreFreeze,coreSourceFail as fail,type CoreSourceRange} from './commerce-core-syntax.js';
import type {CoreExpression,CoreLambda} from './commerce-core-expression.js';
import {createCorePureExpressionChecker,createCoreGenericPureExpressionChecker,requireLegacyExpressionData,type GenericExpressionData,type CorePureExpressionContext,type CoreTypedExpression} from './commerce-core-pure.js';
import {acceptsCoreValueType,coreStringDomain,type CoreValueType,type CoreValueTypes} from './commerce-core-types.js';
import type {CoreContextCatalog,CoreContextRequirement,CoreNativeSignature} from './commerce-core-context.js';
import {buildCoreFlowEvaluation,type CoreFlowEvaluation,type CoreFlowLocalRecord} from './commerce-core-flow-evaluation.js';
export interface CoreFlowScope {readonly module:string;readonly env:ReadonlyMap<string,CoreValueType>;readonly contexts:ReadonlyMap<string,CoreContextRequirement>;readonly narrowed?:ReadonlySet<string>}
export interface CoreNativeExpressionCall {readonly binding:string;readonly span:CoreSourceRange;readonly context:string;readonly source_type:string;readonly abi:string;readonly method:string;readonly arguments:readonly {readonly parameter:string|null;readonly value:CoreFlowExpression;readonly allowed_text:readonly string[]|null}[];readonly result:CoreValueType;readonly placement:'original-source-expression-callsite';readonly custody:'required-from-original-native-owner'}
export interface CorePrivateScalarSlot {readonly name:string;readonly context:string;readonly property:string;readonly source_type:string;readonly abi:string;readonly type:CoreValueType;readonly origin:'authenticated_subject_id'|'current_action_allowed';readonly span:CoreSourceRange}
export interface CoreFlowExpression extends CoreTypedExpression {readonly private_slots?:readonly CorePrivateScalarSlot[];readonly source:CoreExpression;readonly evaluation:CoreFlowEvaluation;readonly local_records:readonly CoreFlowLocalRecord[];readonly native_calls:readonly CoreNativeExpressionCall[];readonly context_reads:readonly {readonly binding:string;readonly source_type:string;readonly abi:string}[];readonly qualification:'typed-source-expression-only'}
export interface CoreFlowExpressionChecker {check(source:CoreExpression,scope:CoreFlowScope,expected?:CoreValueType):CoreFlowExpression;fields(type:CoreValueType,where:CoreSourceRange):readonly {readonly name:string;readonly type:CoreValueType}[];registerRecord(name:string,fields:readonly {readonly name:string;readonly type:CoreValueType}[],where:CoreSourceRange):CoreValueType}
export function createCoreFlowExpressionChecker(types:CoreValueTypes,catalog:CoreContextCatalog):CoreFlowExpressionChecker {
 const records=new Map<string,readonly {name:string;type:CoreValueType}[]>();
 const fields=(type:CoreValueType,where:CoreSourceRange)=>type.kind==='record'&&records.has(type.name)?records.get(type.name)!:types.fields(type,where);
 const augmented:CoreValueTypes={...types,fields};let depth=0;
 const check=(original:CoreExpression,scope:CoreFlowScope,expected?:CoreValueType):CoreFlowExpression=>{
  if(depth>=64)fail('ResourceLimit',original,'native expression nesting bound');const previous=depth;depth++;try{const engine=createCorePureExpressionChecker(augmented),calls:CoreNativeExpressionCall[]=[],reads=new Map<string,{binding:string;source_type:string;abi:string}>(),env=new Map(scope.env);let sequence=0;
  for(const [binding,ctx]of scope.contexts){if(records.has(ctx.projection_type)&&JSON.stringify(records.get(ctx.projection_type))!==JSON.stringify(ctx.properties))fail('InvalidContract',original,'private projection type changed');records.set(ctx.projection_type,ctx.properties);if(env.has(binding))fail('DuplicateSymbol',original,'context name collides with a data input');env.set(binding,{kind:'record',name:ctx.projection_type});}
  const occupied=new Set<string>(env.keys()),names:unknown[]=[original];while(names.length){const v=names.pop();if(v&&typeof v==='object'){if('name'in v&&typeof v.name==='string')occupied.add(v.name.split('.')[0]!);names.push(...Object.values(v));}}
  const ctx=(s:CoreFlowScope,e=env):CorePureExpressionContext=>({module:s.module,env:e,calls:new Set(),...s.narrowed?{narrowed:s.narrowed}:{}});
  const sourceName=(source:CoreExpression):string|null=>source.kind==='name'?source.name:source.kind==='field'&&sourceName(source.value)?sourceName(source.value)+'.'+source.field:null;
  const truth=(scope:CoreFlowScope,source:CoreExpression,yes:boolean):CoreFlowScope=>{
   if(source.kind==='not')return truth(scope,source.value,!yes);if(source.kind==='binary'&&(source.operator==='and'&&yes||source.operator==='or'&&!yes))return truth(truth(scope,source.left,yes),source.right,yes);
   if(source.kind==='invoke'&&['present','absent'].includes(source.name)&&source.args.length===1){const name=sourceName(source.args[0]!.value);if(name){const narrowed=new Set(scope.narrowed);if(source.name==='present'&&yes||source.name==='absent'&&!yes)narrowed.add(name);else narrowed.delete(name);return {...scope,narrowed};}}return scope;
  };
  const compileArgument=(source:CoreExpression,current:CoreFlowScope,context:CoreContextRequirement,signature:CoreNativeSignature,index:number):{value:CoreFlowExpression;allowed:readonly string[]|null}=>{
   const parameter=signature.parameters[index]!,type=catalog.annotation(parameter.annotation,context,source,signature);
   if(type.kind==='selected-event'){const value=check(source,current);if(value.type.kind!=='record')fail('TypeMismatch',source,'native event fingerprint requires a concrete selected Event');const event=types.declarations.get(value.type.name);if(!event||event.surface!=='Event'||event.module!==type.module)fail('TypeMismatch',source,'event does not belong to selected source Event module');return {value,allowed:null};}
   if(type.kind==='finite-text'){
    if(source.kind==='string'&&!type.values.includes(source.value))fail('InvalidContract',source,'native text literal outside selected finite domain');const value=source.kind==='string'?check(source,current,type.type):check(source,current);if(!coreStringDomain(value.type,types))fail('TypeMismatch',source,'closed native text parameter requires bounded scalar text');return {value,allowed:type.values};
   }
   // Transparent scalar refinements may enter a wider native scalar domain
   // only when all expected bounds are entailed. Records/enums remain nominal.
   if(type.type.kind==='refinement'){
    let value:CoreFlowExpression|undefined;try{value=check(source,current);}catch(error){if((error as {diagnostics?:readonly {code:string}[]}).diagnostics?.[0]?.code!=='MissingMapping')throw error;}
    if(value?.type.kind==='refinement'&&value.type.name!==type.type.name){const actual=coreStringDomain(value.type,types)!,expected=coreStringDomain(type.type,types)!,minScalars=Math.max(actual.min_scalars,Math.ceil(actual.min_bytes/4)),maxScalars=Math.min(actual.max_scalars,actual.max_bytes);
     if(expected.pattern===null&&actual.min_bytes>=expected.min_bytes&&actual.max_bytes<=expected.max_bytes&&minScalars>=expected.min_scalars&&maxScalars<=expected.max_scalars)return {value,allowed:null};
    }
   }
   return {value:check(source,current,type.type),allowed:null};
  };
  const rewrite=(source:CoreExpression,current:CoreFlowScope,localEnv:Map<string,CoreValueType>):CoreExpression=>{
   if(source.kind==='name'){const root=source.name.split('.')[0]!,context=scope.contexts.get(root);if(context)reads.set(root,{binding:root,source_type:context.source_type,abi:context.abi});return source;}
   if(source.kind==='invoke'){
    const dot=source.name.indexOf('.'),receiver=dot<0?'':source.name.slice(0,dot),context=scope.contexts.get(receiver);
    if(context){const method=source.name.slice(dot+1),signature=context.methods.get(method);if(!signature)fail('UnknownReference',source,'method absent from captured native context signature '+method);reads.set(receiver,{binding:receiver,source_type:context.source_type,abi:context.abi});
     const named=source.args.some(a=>a.name!==null);if(source.args.length!==signature.parameters.length||named&&source.args.some(a=>a.name===null)||new Set(source.args.flatMap(a=>a.name?[a.name]:[])).size!==source.args.filter(a=>a.name!==null).length)fail('MissingMapping',source,'native call requires exact unique positional or named argument set');
     const arguments_=source.args.map((arg,index)=>{const parameter=named?signature.parameters.findIndex(p=>p.name===arg.name):index;if(parameter<0)fail('UnknownReference',arg.value,'unknown named native parameter');const checked=compileArgument(arg.value,{...current,env:new Map([...localEnv].filter(([name])=>!current.contexts.has(name)))},context,signature,parameter);return {parameter:signature.parameters[parameter]!.name,value:checked.value,allowed_text:checked.allowed};});
     const result=catalog.annotation(signature.result,context,source,signature);if(result.kind!=='value')fail('TypeMismatch',source,'native method result must be one explicit bounded data type');let binding:string;do{binding='core_native_result_'+(++sequence);}while(localEnv.has(binding)||occupied.has(binding));occupied.add(binding);localEnv.set(binding,result.type);env.set(binding,result.type);calls.push({binding,span:{path:source.path,start:source.start,end:source.end},context:receiver,source_type:context.source_type,abi:context.abi,method,arguments:arguments_,result:result.type,placement:'original-source-expression-callsite',custody:'required-from-original-native-owner'});return {...source,kind:'name',name:binding};
    }
   }
   if(source.kind==='binary'){const left=rewrite(source.left,current,localEnv),rightScope=source.operator==='and'||source.operator==='implies'?truth(current,source.left,true):source.operator==='or'?truth(current,source.left,false):current;return {...source,left,right:rewrite(source.right,rightScope,localEnv)};}
   const loopBinders:CoreLambda[]=[];let childEnv=localEnv;
   if(source.kind==='map'||source.kind==='filter')loopBinders.push(source.item);
   if(source.kind==='fold'||source.kind==='indexed-fold')loopBinders.push(source.state,source.item,...source.index?[source.index]:[]);
   if(source.kind==='repeat')loopBinders.push(source.state,source.index);
   if(source.kind==='while-bounded'||source.kind==='until-bounded')loopBinders.push(source.state);
   if(source.kind==='sort'&&source.item)loopBinders.push(source.item);
   if(loopBinders.length){childEnv=new Map(localEnv);for(const b of loopBinders){if(childEnv.has(b.name))fail('DuplicateSymbol',b.span,'loop binder shadows source input/context');childEnv.set(b.name,types.type(current.module,b.type,b.span));}}
   // Native calls inside match payload branches need the actual payload scope.
   if(source.kind==='match'){
    const value=rewrite(source.value,current,localEnv),subject=engine.compile(value,ctx(current,localEnv)),cases=source.cases.map(c=>{
     const branches=c.patterns.map(pattern=>{const branch=new Map(localEnv),branchScope=subject.type.kind==='Bool'&&['true','false'].includes(pattern.name)?truth(current,source.value,pattern.name==='true'):current;if(pattern.binding){let type:CoreValueType;
       if(subject.type.kind==='optional'&&pattern.name==='some')type=subject.type.value;
       else if(subject.type.kind==='enum'||subject.type.kind==='variant'){const d=types.declarations.get(subject.type.name)!,name=pattern.name.split('.').at(-1)!,variant=d.variants.find(v=>v.name===name);if(!variant||!variant.fields.length)fail('TypeMismatch',pattern.span,'native payload reference requires actual variant fields');type=variant.fields.length===1?types.type(d.module,variant.fields[0]!.type,variant.fields[0]!.span):{kind:'variant',name:d.id,variant:name};}
       else return fail('TypeMismatch',pattern.span,'match payload binding requires optional or actual enum');if(branch.has(pattern.binding))fail('DuplicateSymbol',pattern.span,'match binder shadows source scope');branch.set(pattern.binding,type);}
      return {patterns:[pattern],body:rewrite(c.body,branchScope,branch)};});return branches;
    }).flat();const boolPattern=source.cases.flatMap(c=>c.patterns).find(p=>p.name==='true'||p.name==='false'),otherwiseScope=subject.type.kind==='Bool'&&boolPattern?truth(current,source.value,boolPattern.name!=='true'):current;return {...source,value,cases,otherwise:source.otherwise?rewrite(source.otherwise,otherwiseScope,localEnv):null};
   }
   const mapValue=(value:unknown,active:Map<string,CoreValueType>):unknown=>{
    if(value&&typeof value==='object'&&'kind'in value&&'path'in value&&'start'in value&&'end'in value)return rewrite(value as CoreExpression,current,active);
    if(Array.isArray(value))return value.map(v=>mapValue(v,active));if(value&&typeof value==='object'){const out:Record<string,unknown>={};for(const [k,v]of Object.entries(value))out[k]=mapValue(v,active);return out;}return value;
   };
   const out:Record<string,unknown>={};for(const [key,value]of Object.entries(source))out[key]=mapValue(value,['body','guard','keys'].includes(key)?childEnv:localEnv);return out as unknown as CoreExpression;
  };
   const rewritten=rewrite(original,scope,env),typed=engine.compile(rewritten,ctx(scope),expected);engine.finish(typed.expression,original);
   const evaluation=buildCoreFlowEvaluation(typed.expression,typed.type,calls,env,scope.contexts,records,original);
   return coreFreeze({...typed,...evaluation,source:original,native_calls:calls,context_reads:[...reads.values()],qualification:'typed-source-expression-only'});
  }finally{depth=previous;}
 };
 const registerRecord=(name:string,fs:readonly {name:string;type:CoreValueType}[],where:CoreSourceRange):CoreValueType=>{if(types.declarations.has(name)||records.has(name)||new Set(fs.map(f=>f.name)).size!==fs.length)fail('DuplicateSymbol',where,'source-local record identity/fields collide');records.set(name,coreFreeze([...fs]));return {kind:'record',name};};
 return Object.freeze({check,fields,registerRecord});
}

/** Generic C05 uses the same source expression compiler and excludes private/native values. */
export type CoreGenericFlowExpression=Omit<GenericExpressionData<CoreFlowExpression>,'evaluation'|'native_calls'|'context_reads'|'local_records'>&{readonly evaluation:import('../generic/computation-data-v1.js').GenericExprV1;readonly native_calls:readonly [];readonly context_reads:readonly [];readonly local_records:readonly []};
export function createCoreGenericFlowExpressionChecker(types:CoreValueTypes,mode:CoreGenericAdmissionMode='bounded-values'){
 coreGenericAdmissionMode(mode);
 return Object.freeze({check(source:CoreExpression,scope:CoreFlowScope,expected?:CoreValueType):CoreGenericFlowExpression{
  if(scope.contexts.size&&(mode!=='keyed-query-entry'&&(mode!=='atomic-state-entry'&&mode!=='external-read-entry'&&(mode!=='external-write-entry'&&mode!=='event-handoff-entry'))))fail('UnsupportedCapability',source,'generic pure expressions cannot acquire native/private contexts');
  const env=new Map(scope.env),slots:CorePrivateScalarSlot[]=[],occupied=new Set(scope.env.keys()),pending:unknown[]=[source];
  while(pending.length){const v=pending.pop();if(!v||typeof v!=='object')continue;if('name'in v&&typeof v.name==='string')occupied.add(v.name.split('.')[0]!);pending.push(...Object.values(v));}
  const sourceName=(v:CoreExpression):string|null=>v.kind==='name'?v.name:v.kind==='field'&&sourceName(v.value)?sourceName(v.value)+'.'+v.field:null;
  const rewrite=(v:unknown):unknown=>{
   if(Array.isArray(v))return v.map(rewrite);if(!v||typeof v!=='object')return v;
   if('kind'in v&&'path'in v&&'start'in v&&'end'in v){const node=v as CoreExpression,name=sourceName(node),parts=name?.split('.'),context=parts&&scope.contexts.get(parts[0]!);
    if(context){if(parts!.length!==2||context.source_type!=='Craft.Generated.Auth.CustomerContext'||context.abi!=='craft.generic-auth-customer-context/v1-candidate')fail('UnsupportedCapability',node,'only source-owned selected Auth scalar property access is admitted');
     const property=parts![1]!,field=context.properties.find(f=>f.name===property);if(!field||!['customerId','currentActionAllowed'].includes(property))fail('UnknownReference',node,'selected Auth property absent');
     if(property==='customerId'&&(field.type.kind!=='refinement'||field.type.name!=='Craft.Generated.Auth.ReadySubjectId')||property==='currentActionAllowed'&&field.type.kind!=='Bool')fail('InvalidContract',node,'selected Auth property type differs');
     let slot=slots.find(s=>s.context===parts![0]&&s.property===property);if(!slot){let fresh='__craft_context_'+parts![0]+'_'+property,n=0;while(occupied.has(fresh))fresh='__craft_context_'+parts![0]+'_'+property+'_'+(++n);occupied.add(fresh);slot={name:fresh,context:parts![0]!,property,source_type:context.source_type,abi:context.abi,type:field.type,origin:property==='customerId'?'authenticated_subject_id':'current_action_allowed',span:{path:node.path,start:node.start,end:node.end}};slots.push(slot);env.set(fresh,field.type);}
     return {kind:'name',name:slot.name,path:node.path,start:node.start,end:node.end};
    }
    if(node.kind==='invoke'&&scope.contexts.has(node.name.split('.')[0]!))fail('UnsupportedCapability',node,'Auth context methods cannot be invoked');
   }
   return Object.fromEntries(Object.entries(v).map(([key,value])=>[key,rewrite(value)]));
  };
  const rewritten=scope.contexts.size?rewrite(source) as CoreExpression:source,engine=createCoreGenericPureExpressionChecker(types,mode),typed=engine.compile(rewritten,{module:scope.module,env,calls:new Set(),...scope.narrowed?{narrowed:scope.narrowed}:{}},expected);engine.finish(typed.expression,source);
  return coreFreeze({...typed,source,evaluation:typed.expression,local_records:[],native_calls:[],context_reads:[],...(slots.length?{private_slots:slots}:{}),qualification:'typed-source-expression-only'});
 },fields:types.fields,registerRecord(_name:string,_fields:readonly {readonly name:string;readonly type:CoreValueType}[],where:CoreSourceRange):never{return fail('UnsupportedCapability',where,'generic C05 does not admit source-local/native records');}});
}
