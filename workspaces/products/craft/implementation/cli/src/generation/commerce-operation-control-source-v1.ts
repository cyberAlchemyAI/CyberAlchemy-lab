/** Checked source -> explicit async control flow. This is construction code;
 * the original runtime assembly and recovery producers are separate obligations.
 * Open Questions: implementation/craft-alchlang-commerce-2026-10-16/evidence/EC18/CONTEXT.md. */
import type {FlowExprV1,RoleExpressionV1,OperationActionV1,OperationCallV1,OperationControlStepV1} from '../commerce/commerce-data-v1.js';
import type {CommerceEffectSourceInputV1,CommerceEffectSourceBundleV1} from './commerce-effectful-operation-source-v1.js';
import {renderCommerceEffectfulTransactionSourcesV1,commerceTransactionOutcomeMappingV1} from './commerce-effectful-operation-source-v1.js';
import {deriveCommerceSourceRecoveryPlansV1} from './commerce-recovery-plan-v1.js';
import {commerceTransactionFailureActionsV1} from '../commerce/commerce-transaction-source-failure-v1.js';

const q=(v:unknown)=>JSON.stringify(v);
const seal=<T>(v:T):T=>{if(v&&typeof v==='object'&&!Object.isFrozen(v)){for(const x of Object.values(v))seal(x);Object.freeze(v);}return v;};
export const COMMERCE_CONTROL_KINDS_V1=Object.freeze(['preflight','guard','let','count','read','call','conditional','case','present','read-set','transaction','action','acknowledge']);
export const COMMERCE_OUTER_EXPRESSION_KINDS_V1=Object.freeze(['literal','var','field','none','some','present','absent','require_some','require_variant','record','enum_value','list','let','if','binary','call','map','fold','sort','match_variant','native_observation','private_context']);

const contract=`// Generated prospective construction obligations. Not public SDK handle identity.
import type {SourceSettlement} from './native-effect-contract.js';
export type Data=boolean|string|bigint|readonly Data[]|Readonly<{[key:string]:Data}>;
export type Observation={readonly kind:'value';readonly value:Data;readonly commits:readonly unknown[];readonly unresolved:readonly unknown[]}|{readonly kind:'rejected'|'failed';readonly code:string;readonly channel:string|null}|({readonly kind:'indeterminate';readonly ticket:unknown;readonly channel:string|null}&({readonly has_value:true;readonly value:Data}|{readonly has_value:false}));
export type ReadObservation={readonly kind:'found';readonly value:Data}|{readonly kind:'missing'|'unavailable'};
export type OperationResult={readonly kind:'returned';readonly value:Data;readonly commits:readonly unknown[]}|{readonly kind:'rejected'|'failed';readonly code:string;readonly commits:readonly unknown[]}|({readonly kind:'indeterminate';readonly tickets:readonly unknown[];readonly source_code:string|null;readonly commits:readonly unknown[];readonly do_not_ack:true}&({readonly has_value:true;readonly value:Data}|{readonly has_value:false}));
// Technical owner ports only. Future native assembly must construct them from
// original owners. The source generator accepts no feature implementation,
// expression evaluator, SQL, authorization decision or recovery callback.
export interface OperationExecution {
 assertCurrent(source:string,operation:string,path:string):void;
 parameters(value:unknown):Readonly<Record<string,Data>>;
 charge(path:string):void;
 validateRole(path:string,value:Data):Data;
 validateReturn(value:Data):Data;
 context(path:string):Data;
 enumValue(path:string,type:string,variant:string,fields:Readonly<Record<string,Data>>):Data;
 pure(path:string,args:readonly Data[]):Promise<{readonly ok:true;readonly value:Data}|{readonly ok:false;readonly code:string}>;
 native(path:string,args:readonly Data[]):Promise<Data>;
 preflight(path:string):Promise<void>;
 count(path:string):Promise<bigint>;
 read(path:string,key:Readonly<Record<string,Data>>,args:Readonly<Record<string,Data>>):Promise<ReadObservation>;
 call(path:string,args:Readonly<Record<string,Data>>):Promise<Observation>;
 assertObservation(path:string,observation:unknown):void;
 openReadSet(path:string):Promise<unknown>;
 closeReadSet(lease:unknown):Promise<void>;
 transaction(path:string,scope:Readonly<Record<string,Data>>):Promise<SourceSettlement>;
 assertTransaction(path:string,settlement:SourceSettlement):void;
 assertSourceReturn(path:string,settlement:SourceSettlement,action:unknown):void;
 assertRecovery(path:string,settlement:SourceSettlement,plan:Readonly<Record<string,unknown>>):void;
 acknowledge(path:string,originalCommits:readonly unknown[]):Promise<void>;
}
`;

/** Every expression is emitted at its original source path, in evaluation order.
 * The generated module contains no evaluator for a caller-supplied expression AST. */
export function renderCommerceOperationControlSourcesV1(input:CommerceEffectSourceInputV1):CommerceEffectSourceBundleV1 {
 if(input.effect_plan.protocol!==null)throw new TypeError('ConformanceProtocolIsNotAnInvocableOperation');
 const recoveryPlans=deriveCommerceSourceRecoveryPlansV1(input),recoveryStack=new Set<string>();
 let serial=0,nodes=0;const sites:Record<string,unknown>=Object.create(null),kinds=new Set<string>(),expressions=new Set<string>();
 const fresh=(prefix='v')=>prefix+(++serial),check=(p:string)=>{if(++nodes>65536||p.length>8192)throw new TypeError('SourceGenerationBound');};
 const expr=(e:FlowExprV1,p:string,scope:string):string=>{
  check(p);expressions.add(e.op);if(!COMMERCE_OUTER_EXPRESSION_KINDS_V1.includes(e.op))throw new TypeError('UnsupportedOuterExpression:'+e.op+':'+p);
  const sub=(x:FlowExprV1,key:string,s=scope)=>expr(x,p+'.'+key,s),fields=(v:Readonly<Record<string,FlowExprV1>>)=>`record([${Object.entries(v).map(([k,v])=>`[${q(k)},${sub(v,'fields.'+k)}]`).join(',')}])`;
  let code:string;
  switch(e.op){
   case'literal':code=e.type.kind==='scalar'&&e.type.name==='UInt64'?`BigInt(${q(e.value)})`:q(e.value);break;
   case'var':code=`field(${scope},${q(e.name)})`;break;
   case'field':code=`field(${sub(e.value,'value')},${q(e.field)})`;break;
   case'none':code=`Object.freeze({kind:'none'})`;break;
   case'some':code=`Object.freeze({kind:'some',value:${sub(e.value,'value')}})`;break;
   case'present':case'absent':code=`(optional(${sub(e.value,'value')}).kind===${q(e.op==='present'?'some':'none')})`;break;
   case'require_some':code=`someValue(${sub(e.value,'value')})`;break;
   case'require_variant':code=`variantValue(${sub(e.value,'value')},${q(e.variant)})`;break;
   case'record':code=fields(e.fields);break;
   case'enum_value':code=`runtime.enumValue(${q(p)},${q(e.type_name)},${q(e.variant)},${fields(e.fields)})`;break;
   case'list':code=`Object.freeze([${e.items.map((v,i)=>sub(v,'items['+i+']')).join(',')}])`;break;
   case'private_context':sites[p]=e;code=`runtime.context(${q(p)})`;break;
   case'native_observation':sites[p]=e;code=`await native(${q(p)},[${e.arguments.map((a,i)=>sub(a.value,'arguments['+i+'].value')).join(',')}])`;break;
   case'call':sites[p]=e;code=`await pure(${q(p)},[${e.arguments.map((a,i)=>sub(a,'arguments['+i+']')).join(',')}])`;break;
   case'binary':{
    if(!['eq','lt','lte','gt','gte','add','subtract','multiply','and','or'].includes(e.operator))throw new TypeError('UnsupportedOuterArithmetic:'+e.operator+':'+p);
    const l=sub(e.left,'left'),r=sub(e.right,'right');code=e.operator==='and'?`(bool(${l})&&bool(${r}))`:e.operator==='or'?`(bool(${l})||bool(${r}))`:`binary(${q(e.operator)},${l},${r},${q(p)})`;break;
   }
   case'if':code=`(bool(${sub(e.condition,'condition')})?${sub(e.then,'then')}:${sub(e.else,'else')})`;break;
   case'let':{const s=fresh('scope');code=`await (async()=>{const ${s}=extend(${scope},${q(e.binding.name)},${sub(e.value,'value')});return ${sub(e.body,'body',s)};})()`;break;}
   case'map':{const s=fresh('scope'),item=fresh('item'),out=fresh('items');code=`await (async()=>{const ${out}:Data[]=[];for(const ${item} of list(${sub(e.source,'source')})){runtime.charge(${q(p)});const ${s}=extend(${scope},${q(e.item.name)},${item});${out}.push(${sub(e.body,'body',s)});}return Object.freeze(${out});})()`;break;}
   case'fold':{const s=fresh('scope'),item=fresh('item'),state=fresh('state'),items=fresh('items');code=`await (async()=>{const ${items}=list(${sub(e.source,'source')});let ${state}:Data=${sub(e.initial,'initial')};for(const ${item} of ${items}){runtime.charge(${q(p)});const ${s}=extend(extend(${scope},${q(e.state.name)},${state}),${q(e.item.name)},${item});${state}=${sub(e.body,'body',s)};}return ${state};})()`;break;}
   case'match_variant':{const value=fresh('subject'),s=fresh('scope');code=`await (async()=>{const ${value}=${sub(e.value,'value')};${e.cases.map((c,i)=>`if(tag(${value})===${q(c.variant)}){const ${s}=${c.binding?`extend(${scope},${q(c.binding)},variantPayload(${value}))`:scope};return ${sub(c.then,'cases['+i+'].then',s)};}`).join('')}return ${e.otherwise?sub(e.otherwise,'otherwise'):`invalid('NonExhaustiveMatch')`};})()`;break;}
   case'sort':{if(e.keys.some(k=>k.mode==='natural'))throw new TypeError('UnsupportedOuterNaturalSort:'+p);const items=fresh('items'),item=fresh('item'),s=fresh('scope'),out=fresh('decorated');code=`await (async()=>{const ${items}=list(${sub(e.source,'source')}),${out}:{value:Data;keys:Data[];index:number}[]=[];for(let i=0;i<${items}.length;i++){runtime.charge(${q(p)});const ${item}=${items}[i],${s}=extend(${scope},${q(e.item.name)},${item});${out}.push({value:${item},keys:[${e.keys.map((k,i)=>sub(k.value,'keys['+i+'].value',s)).join(',')}],index:i});}${out}.sort((a,b)=>{runtime.charge(${q(p)});${e.keys.map((k,i)=>`{const c=compare(a.keys[${i}],b.keys[${i}],${q(k.mode)});if(c)return c*${k.direction==='asc'?1:-1};}`).join('')}return a.index-b.index;});return Object.freeze(${out}.map(v=>v.value));})()`;break;}
   default:throw new TypeError('UnsupportedOuterExpression:'+e.op);
  }
  return `(runtime.charge(${q(p)}),${code})`;
 };
 const role=(r:RoleExpressionV1,p:string,s:string)=>{sites[p]=r;return `runtime.validateRole(${q(p)},${expr(r.expression,p+'.expression',s)})`;};
 const args=(call:OperationCallV1,p:string,s:string)=>`record([${call.arguments.map((a,i)=>`[${q(a.parameter)},${role(a.value,p+'.arguments['+i+'].value',s)}]`).join(',')}])`;
 const invoke=(call:OperationCallV1,p:string,s:string)=>{sites[p]=call;return `await call(${q(p)},${args(call,p,s)})`;};
 const action=(a:OperationActionV1,p:string,s:string):string=>{
  check(p);sites[p]=a;
  if(a.kind==='return')return `return await returned(${role(a.value,p+'.value',s)});`;
  if(a.kind==='reject'||a.kind==='fail')return `return await stopped(${q(a.kind==='reject'?'rejected':'failed')},${q(a.code)});`;
  if(a.kind!=='invoke-return')throw new TypeError('UnknownSourceAction');
  const observed=fresh('returnedCall');return `${a.read_set_unwind_required?'await unwind();':''}const ${observed}=${invoke(a.call,p+'.call',s)};return await forwarded(${observed});`;
 };
 const transaction=(p:string,s:string):string=>{
  const t=input.transactions.find(t=>t.path===p);if(!t)throw new TypeError('MissingOriginalTransaction:'+p);sites[p]=t.plan;
  const result=fresh('transaction'),mapping=commerceTransactionOutcomeMappingV1(t.plan);
  const unknownAction=mapping.indeterminate.action as OperationActionV1|null,unknownHandler=t.plan.handlers.findIndex(h=>h.channel==='on-unknown-commit'),unknownDefault=t.plan.defaults.findIndex(h=>h.channel==='on-unknown-commit'),unknownPath=unknownHandler>=0?p+'.handlers['+unknownHandler+'].action':p+'.defaults['+unknownDefault+'].action';
  const unknown=unknownAction?`runtime.assertSourceReturn(${q(p)},${result},${q(unknownAction)});${action(unknownAction,unknownPath,s)}`:`return await uncertain(undefined,false,null);`;
  // Source return handlers are generated below, never evaluated by a callback.
  const mappedActions=Object.entries(mapping).filter(([,m])=>'action'in m&&m.action&&(m.action.kind==='return'||m.action.kind==='invoke-return')).map(([,m])=>{const a=('action'in m?m.action:null)! as OperationActionV1,handler=t.plan.handlers.findIndex(h=>q(h.action)===q(a)),fallback=t.plan.defaults.findIndex(h=>q(h.action)===q(a)),at=handler>=0?p+'.handlers['+handler+'].action':p+'.defaults['+fallback+'].action';return `if(${result}.kind==='source-return-required'&&${result}.source_action_path===null&&equal(${result}.source_action,${q(a)})){runtime.assertSourceReturn(${q(p)},${result},${q(a)});${action(a,at,s)}}`;});
  const failureActions=commerceTransactionFailureActionsV1(p,t.plan).filter(row=>row.action.kind==='return'||row.action.kind==='invoke-return').map(row=>
   `if(${result}.kind==='source-return-required'&&${result}.source_action_path===${q(row.action_path)}&&equal(${result}.source_action,${q(row.action)})){runtime.assertSourceReturn(${q(p)},${result},${q(row.action)});${action(row.action,row.action_path,s)}}`);
  const sourceActions=[...mappedActions,...failureActions];
  const aliases=t.plan.body.flatMap(step=>step.kind==='mutation'?[step.binding]:step.kind==='let'?[step.name]:[]);
  const recoveryBranches=recoveryPlans.filter(r=>r.transaction_path===p).map(r=>{
   const key=p+':'+r.kind;if(recoveryStack.has(key))throw new TypeError('RecursiveSourceRecovery');recoveryStack.add(key);
   const scope=fresh('recoveryScope');
   const prefix=[...r.guard_indices,...r.prefix_indices].map(index=>controls([input.effect_plan.body[index]!],'$.body',scope,index,true)).join('\n');
   recoveryStack.delete(key);
   return `if(${result}.recovery===${q(r.kind)}){if(${result}.source_path!==${q(p)})throw new TypeError('ForeignRecoverySource');runtime.assertRecovery(${q(p)},${result},JSON.parse(${q(q(r))}));current(${q(p)});const ${scope}=extend(${s});${r.retained_bindings.map(name=>`field(${scope},${q(name)});`).join('')}\n${prefix}\n${action(r.fallback.action,r.fallback.source_path,scope)}}`;
  });
  return `const ${result}=await runtime.transaction(${q(p)},Object.freeze({...${s}}));current(${q(p)});runtime.assertTransaction(${q(p)},${result});
if(${result}.kind==='committed'){const aliases=${result}.aliases;if(!aliases||typeof aliases!=='object'||Array.isArray(aliases)||Object.keys(aliases).length!==${aliases.length})throw new TypeError('InvalidCommittedSourceAliases');${aliases.map(name=>`${s}[${q(name)}]=field(aliases,${q(name)});`).join('')}commits.push(${result}.receipt);}
else {
if(${result}.kind==='indeterminate'){tickets.push(${result}.ticket);${unknown}}
if(${result}.kind==='generated-recovery-required'){${recoveryBranches.join('\n')}throw new TypeError('UnknownOriginalRecoveryTemplate:'+${q(p)});}
${sourceActions.join('\n')}
if(${result}.kind==='rejected'||${result}.kind==='failed'){return await stopped(${result}.kind,${result}.code);}
throw new TypeError('MissingOriginalSourceSettlement');}`;
 };
 const controls=(body:readonly OperationControlStepV1[],base:string,s:string,offset=0,recovery=false):string=>body.map((step,i)=>{
  const p=base+'['+(i+offset)+']';check(p);kinds.add(step.kind);sites[p]=step;const prefix=`current(${q(p)});runtime.charge(${q(p)});\n`;
  switch(step.kind){
   case'preflight':return prefix+`await runtime.preflight(${q(p)});current(${q(p)});`;
   case'guard':return prefix+`if(!bool(${role(step.condition,p+'.condition',s)})){${action(step.on_false,p+'.on_false',s)}}`;
   case'let':return prefix+`try{${s}[${q(step.name)}]=${role(step.value,p+'.value',s)};}catch(error){if(!(error instanceof ExpressionFault))throw error;${action(step.on_error,p+'.on_error',s)}}`;
   case'count':return prefix+`${s}[${q(step.name)}]=await runtime.count(${q(p)});current(${q(p)});runtime.assertObservation(${q(p)},${s}[${q(step.name)}]);`;
   case'read':{const r=fresh('read'),snapshot=fresh('readInput'),key=step.key?`record([${step.key.values.map((v,i)=>`[${q(v.field)},${role(v.value,p+'.key.values['+i+'].value',s)}]`).join(',')}])`:'record([])',argumentsValue=step.call?args(step.call,p+'.call',s):'record([])',acquire=recovery?`const ${snapshot}=readInputs.get(${q(p)});if(!${snapshot})throw new TypeError('MissingOriginalReadSnapshot');`:`const ${snapshot}=Object.freeze({key:Object.freeze(${key}),args:Object.freeze(${argumentsValue})});readInputs.set(${q(p)},${snapshot});`;return prefix+`${acquire}const ${r}=await runtime.read(${q(p)},${snapshot}.key,${snapshot}.args);current(${q(p)});runtime.assertObservation(${q(p)},${r});if(${r}.kind==='unavailable'){${action(step.on_unavailable,p+'.on_unavailable',s)}}else if(${r}.kind==='missing'){${step.on_missing?action(step.on_missing,p+'.on_missing',s):`${s}[${q(step.name)}]=Object.freeze({kind:'none'});`}}else if(${r}.kind==='found'){${s}[${q(step.name)}]=${step.type.kind==='optional'?`Object.freeze({kind:'some',value:${r}.value})`:`${r}.value`};}else{throw new TypeError('InvalidReadObservation');}`;}
   case'call':{const o=fresh('callResult');return prefix+`const ${o}=${invoke(step.call,p+'.call',s)};${step.handlers.map((h,i)=>`if(${o}.kind!=='value'&&${o}.channel===${q(h.channel)}){${o}.kind==='indeterminate'&&tickets.push(${o}.ticket);${action(h.action,p+'.handlers['+i+'].action',s)}}`).join('')}if(${o}.kind==='value'){commits.push(...${o}.commits);tickets.push(...${o}.unresolved);${s}[${q(step.name)}]=${o}.value;}else if(${o}.kind==='indeterminate'&&${o}.has_value){tickets.push(${o}.ticket);${s}[${q(step.name)}]=${o}.value;}else{return await forwarded(${o});}`;}
   case'conditional':return prefix+`if(bool(${role(step.condition,p+'.condition',s)})){const child=extend(${s});${controls(step.then,p+'.then','child')}}else{const child=extend(${s});${controls(step.otherwise,p+'.otherwise','child')}}`;
   case'case':{const subject=fresh('subject');return prefix+`{const ${subject}=${role(step.subject,p+'.subject',s)};${step.branches.map((b,i)=>`if(tag(${subject})===${q(b.variant)}){const branch=${b.binding?`extend(${s},${q(b.binding)},${subject})`:`extend(${s})`};${b.guard?`if(bool(${role(b.guard,p+'.branches['+i+'].guard','branch')})){`:''}${action(b.action,p+'.branches['+i+'].action','branch')}${b.guard?'}':''}}`).join('')}}`;}
   case'present':return prefix+`if(optional(${role(step.subject,p+'.subject',s)}).kind==='some'){${step.condition?`if(!bool(${role(step.condition,p+'.condition',s)})){${step.on_false?action(step.on_false,p+'.on_false',s):`throw new TypeError('MissingPresentFailure');`}}`:''}${step.action?action(step.action,p+'.action',s):''}${step.transaction?transaction(p+'.transaction',s):''}}`;
   case'read-set':{const items=fresh('readItems'),out=fresh('readRows'),lease=fresh('lease'),child=fresh('row');return prefix+`const ${items}=list(${role(step.source,p+'.source',s)}),${out}:Data[]=[];const ${lease}=await runtime.openReadSet(${q(p)});leases.push(${lease});current(${q(p)});try{for(const item of ${items}){runtime.charge(${q(p)});const ${child}=extend(${s},${q(step.item)},item);${controls(step.body,p+'.body',child)}${out}.push(record([${step.collected.map((c,i)=>`[${q(c.name)},${role(c.value,p+'.collected['+i+'].value',child)}]`).join(',')}]));}}finally{await close(${lease});}${s}[${q(step.name)}]=Object.freeze(${out});`;}
   case'transaction':return prefix+transaction(p+'.transaction',s);
   case'action':return prefix+action(step.action,p+'.action',s);
   case'acknowledge':return prefix+`if(tickets.length)return await uncertain(undefined,false,null);await runtime.acknowledge(${q(p)},Object.freeze([...commits]));current(${q(p)});`;
   default:throw new TypeError('UnsupportedOperationControl');
  }
 }).join('\n');
 const body=controls(input.effect_plan.body,'$.body','scope');
 const text=`// Generated explicit async source control; native assembly is not established.
import type {Data,OperationExecution,OperationResult,Observation} from './operation-execution-contract.js';
const source=${q(input.source_capture_sha256)},operation=${q(input.operation)};
class ExpressionFault extends Error {readonly code:string;constructor(code:string){super(code);this.code=code;}}
const invalid=(code:string):never=>{throw new ExpressionFault(code);};
const own=(v:unknown,key:string):unknown=>{if(v===null||typeof v!=='object')return invalid('InputType');const d=Object.getOwnPropertyDescriptor(v,key);if(!d||!d.enumerable||!Object.hasOwn(d,'value'))return invalid('InputType');return d.value;};
const field=(v:Data,key:string):Data=>own(v,key) as Data;
const record=(entries:readonly(readonly[string,Data])[]):Record<string,Data>=>Object.assign(Object.create(null),Object.fromEntries(entries));
const extend=(v:Readonly<Record<string,Data>>,key?:string,value?:Data):Record<string,Data>=>{const out:Record<string,Data>=Object.assign(Object.create(null),v);if(key!==undefined){if(value===undefined)return invalid('MissingNativeScopeValue');out[key]=value;}return out;};
const bool=(v:Data):boolean=>typeof v==='boolean'?v:invalid('InputType');
const list=(v:Data):readonly Data[]=>Array.isArray(v)?v:invalid('InputType');
const optional=(v:Data):Readonly<{kind:'some';value:Data}>|Readonly<{kind:'none'}>=>{const kind=field(v,'kind');if(kind==='some')return Object.freeze({kind,value:field(v,'value')});if(kind==='none')return Object.freeze({kind});return invalid('InputType');};
const someValue=(v:Data):Data=>{const value=optional(v);return value.kind==='some'?value.value:invalid('OptionalAbsent');};
const tag=(v:Data):string=>{const value=typeof v==='string'?v:field(v,'kind');return typeof value==='string'?value:invalid('InputType');};
const variantValue=(v:Data,variant:string):Data=>tag(v)===variant?v:invalid('UnexpectedVariant');
// A single-field variant binds its payload; a multi-field variant binds the
// complete refined value, matching Core's checked source match semantics.
const variantPayload=(v:Data):Data=>{if(!v||typeof v!=='object'||Array.isArray(v))return invalid('InputType');const keys=Object.keys(v).filter(key=>key!=='kind');return keys.length===1?field(v,keys[0]!):v;};
function binary(op:string,a:Data,b:Data,path:string):Data{if(op==='eq')return equal(a,b);if(typeof a!=='bigint'||typeof b!=='bigint')return invalid('InputType');if(op==='lt')return a<b;if(op==='lte')return a<=b;if(op==='gt')return a>b;if(op==='gte')return a>=b;const result=op==='add'?a+b:op==='subtract'?a-b:op==='multiply'?a*b:invalid('UnsupportedArithmetic:'+path);if(result<0n||result>18446744073709551615n)return invalid('ArithmeticError');return result;}
function equal(a:unknown,b:unknown,depth=0):boolean{if(depth>64)return invalid('ResourceLimit');if(a===b)return true;if(typeof a!==typeof b||a===null||b===null||typeof a!=='object'||typeof b!=='object')return false;if(Array.isArray(a)!==Array.isArray(b))return false;const keys=Object.keys(a);return keys.length===Object.keys(b).length&&keys.every(k=>Object.hasOwn(b,k)&&equal(own(a,k),own(b,k),depth+1));}
function compare(a:Data,b:Data,mode:string):number{if(mode==='numeric'){if(typeof a!=='bigint'||typeof b!=='bigint')return invalid('InputType');return a<b?-1:a>b?1:0;}if(typeof a!=='string'||typeof b!=='string')return invalid('InputType');if(mode==='natural')return invalid('NaturalSortNotInSelectedOuterCell');const aa=Array.from(a,c=>c.codePointAt(0)!),bb=Array.from(b,c=>c.codePointAt(0)!);for(let i=0;i<Math.min(aa.length,bb.length);i++)if(aa[i]!==bb[i])return aa[i]!<bb[i]!?-1:1;return aa.length-bb.length;}
export const controlSourceQualification='generated-async-control-and-source-recovery-component;original-runtime-assembly-required' as const;
export async function runOperation(parameters:unknown,runtime:OperationExecution):Promise<OperationResult>{
 const current=(path:string)=>runtime.assertCurrent(source,operation,path);current('$');
 const scope=extend(runtime.parameters(parameters)),commits:unknown[]=[],tickets:unknown[]=[],leases:unknown[]=[],readInputs=new Map<string,Readonly<{key:Readonly<Record<string,Data>>;args:Readonly<Record<string,Data>>}>>();
 const close=async(lease:unknown)=>{const index=leases.lastIndexOf(lease);if(index<0)return;if(index!==leases.length-1)throw new TypeError('ReadSetUnwindOrder');await runtime.closeReadSet(lease);leases.pop();current('$');};
 const unwind=async()=>{while(leases.length)await close(leases[leases.length-1]);};
 const uncertain=async(value:Data|undefined,has_value:boolean,source_code:string|null):Promise<OperationResult>=>{await unwind();current('$');const shared={kind:'indeterminate' as const,tickets:Object.freeze([...tickets]),source_code,commits:Object.freeze([...commits]),do_not_ack:true as const};if(has_value){if(value===undefined)throw new TypeError('MissingIndeterminateSourceValue');return Object.freeze({...shared,has_value:true,value});}return Object.freeze({...shared,has_value:false});};
 const returned=async(value:Data):Promise<OperationResult>=>{value=runtime.validateReturn(value);await unwind();current('$');return tickets.length?uncertain(value,true,null):Object.freeze({kind:'returned',value,commits:Object.freeze([...commits])});};
 const stopped=async(kind:'rejected'|'failed',code:string):Promise<OperationResult>=>{await unwind();current('$');return tickets.length?uncertain(undefined,false,code):Object.freeze({kind,code,commits:Object.freeze([...commits])});};
 const forwarded=async(o:Observation):Promise<OperationResult>=>{if(o.kind==='value'){commits.push(...o.commits);tickets.push(...o.unresolved);return returned(o.value);}if(o.kind==='indeterminate'){tickets.push(o.ticket);return uncertain(o.has_value?o.value:undefined,o.has_value,null);}return stopped(o.kind,o.code);};
 const pure=async(path:string,args:readonly Data[]):Promise<Data>=>{current(path);const value=await runtime.pure(path,args);current(path);if(!value.ok)throw new ExpressionFault(value.code);return value.value;};
 const native=async(path:string,args:readonly Data[]):Promise<Data>=>{current(path);const value=await runtime.native(path,args);current(path);return value;};
 const call=async(path:string,args:Readonly<Record<string,Data>>):Promise<Observation>=>{current(path);const value=await runtime.call(path,args);current(path);runtime.assertObservation(path,value);return value;};
 try{${body}\nthrow new TypeError('MissingSourceReturn');}finally{await unwind();}
}
`;
 const adapters=renderCommerceEffectfulTransactionSourcesV1(input);
 return seal({files:[...adapters.files,{path:'operation-execution-contract.ts',text:contract},{path:'operation-control.ts',text}],manifest:{...adapters.manifest,outer_control_generation:true,whole_operation_generation:false,generated_control_kinds:[...kinds].sort(),generated_expression_kinds:[...expressions].sort(),source_sites:sites,source_site_count:Object.keys(sites).length,recovery_generation:true,recovery_plans:recoveryPlans,original_runtime_assembly:false,qualification:'generated-async-control-recovery-and-transaction-components;not-complete-native-operation-assembly'}});
}
