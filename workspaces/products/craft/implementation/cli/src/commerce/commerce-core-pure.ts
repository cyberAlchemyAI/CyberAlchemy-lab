/** Independent Core pure source semantics. Existing ExprV1 is the executable
 * pure AST; source type constraints remain explicit alongside it. No evaluator,
 * selected profile, native basis or application owner is manufactured here.
 * Open Questions: docs/COMMERCE-CONTRACTS.md#open-questions. */
import {dataDigest} from '../profile-engine/contracts.js';
import type {GenericExprV1} from '../generic/computation-data-v1.js';
import type {ExprV1,ValueTypeV1} from './commerce-data-v1.js';
import {coreFreeze,coreSourceFail as fail,coreSourceChild as child,coreSourceChildren as children,coreSourceTokens as tokens,coreSourceText as text,type CoreSourceRange,type CoreSourceNode} from './commerce-core-syntax.js';
import {reconstructCoreCommerceSources,type CoreCommerceDeclaration,type CoreCommerceReconstruction} from './commerce-core-reconstruction.js';
import {parseCoreExpression,parseCoreExpressionValue,parseCoreTypeTokens,type CoreExpression,type CoreLambda} from './commerce-core-expression.js';
import {createCoreValueTypes,assertCoreGenericValueTypes,assertCoreGenericValueType,assertCoreGenericNullaryControl,coreGenericAdmissionMode,type CoreGenericAdmissionMode,CORE_UINT64,CORE_BOOL,acceptsCoreValueType,sameCoreValueType,coreStringDomain,matchesCoreRefinementPattern,type CoreValueType,type CoreValueTypes} from './commerce-core-types.js';
export interface CoreTypedExpression {readonly type:CoreValueType;readonly expression:ExprV1}
export interface CorePureDeclaration {readonly name:string;readonly kind:'Rule'|'Calculation'|'Mapping'|'Policy'|'StateMachine';readonly parameters:readonly {readonly name:string;readonly type:CoreValueType}[];readonly result:CoreValueType;readonly body:ExprV1;readonly preconditions:readonly ExprV1[];readonly rounding:'floor'|'ceil'|'reject';readonly on_evaluation_error:Readonly<{kind:'reject'|'fail';code:string}>|null;readonly initial:ExprV1|null;readonly terminal:readonly ExprV1[];readonly otherwise_reason:string|null}
export interface CoreValueDeclaration {readonly name:string;readonly role:'Entity'|'ValueObject'|'Event'|'Enum';readonly fields:readonly {readonly name:string;readonly type:CoreValueType}[];readonly variants:readonly {readonly name:string;readonly wire:string;readonly fields:readonly {readonly name:string;readonly type:CoreValueType}[]}[];readonly identity:readonly string[];readonly unique:readonly (readonly string[])[];readonly immutable:readonly string[]|'all';readonly event_version:1|null}
export interface CorePureSemantics {readonly schema_version:'craft.commerce-core-pure-semantics/v1-candidate';readonly qualification:'independent-pure-component-data-only';readonly declarations:readonly CorePureDeclaration[];readonly value_declarations:readonly CoreValueDeclaration[];readonly collection_predicates:readonly {readonly type:CoreValueType;readonly rule:string}[];readonly record_invariants:readonly {readonly record:string;readonly invariants:readonly ExprV1[]}[];readonly source_refinements:readonly import('./commerce-core-types.js').CoreRefinement[];readonly pure_subject_sha256:string;readonly authority_effect:'none'}
/** A source component union is data only; it grants no execution custody. */
export type GenericExpressionData<T> = T extends ExprV1 ? GenericExprV1 : T extends readonly (infer V)[] ? readonly GenericExpressionData<V>[] : T extends object ? {readonly [K in keyof T]:GenericExpressionData<T[K]>} : T;
export type CoreGenericTypedExpression=GenericExpressionData<CoreTypedExpression>;
export type CoreGenericPureDeclaration=GenericExpressionData<CorePureDeclaration>;
export type CoreGenericPureSemantics=Omit<GenericExpressionData<CorePureSemantics>,'schema_version'>&{readonly schema_version:'craft.generic-core-pure-semantics/v1-candidate'};
/** Legacy exports never return the successor algebra, even through an untyped caller. */
export function requireLegacyExpressionData<T>(value:unknown):T {
 const pending:unknown[]=[value];let count=0;
 while(pending.length){const v=pending.pop();if(!v||typeof v!=='object')continue;if(++count>1000000)fail('ResourceLimit',{path:'legacy-expression',start:0,end:0},'legacy data work bound');if('op'in v&&v.op==='append'||'schema_version'in v&&typeof v.schema_version==='string'&&v.schema_version.startsWith('craft.generic-'))fail('UnsupportedCapability',{path:'legacy-expression',start:0,end:0},'generic contract requires its original generic producer');pending.push(...Object.values(v));}
 return value as T;
}
const isPure=(d:CoreCommerceDeclaration):d is CoreCommerceDeclaration&{surface:CorePureDeclaration['kind']}=>['Rule','Calculation','Mapping','Policy','StateMachine'].includes(d.surface);
const words=(n:CoreSourceNode)=>tokens(n).filter(t=>!t.layout).map(t=>t.token);
const range=(n:CoreSourceRange):CoreSourceRange=>({path:n.path,start:n.start,end:n.end});
/** Boundary representation only; literal/minimum constraints are deliberately
 * retained in CoreValueType/source_refinements, never claimed erased/implemented. */
export function coreValueAstType(t:CoreValueType):ValueTypeV1 {
 switch(t.kind){case'UInt64':case'Bool':return {kind:'scalar',name:t.kind};case'String':return {kind:'string',max_bytes:t.max_bytes,max_scalars:t.max_scalars};case'literal':return {kind:'literal',value:t.value};case'record':case'enum':case'refinement':return {kind:t.kind,name:t.name};case'variant':return {kind:'variant',enum_name:t.name,variant:t.variant};case'optional':return {kind:'optional',element:coreValueAstType(t.value)};case'List':return {kind:'list',element:coreValueAstType(t.value),min_items:0,max_items:t.maximum};case'outcome':return {kind:'outcome',state:coreValueAstType(t.state),intent:coreValueAstType(t.intent),max_intents:t.maximum};}
}
export interface CorePureExpressionContext {readonly module:string;readonly env:ReadonlyMap<string,CoreValueType>;readonly calls:Set<string>;readonly narrowed?:ReadonlySet<string>}
type Context=CorePureExpressionContext;
/** Internal source component interface only; creates no registered owner. */
function createPureExpressionChecker(types:CoreValueTypes,generic:boolean,mode:CoreGenericAdmissionMode='bounded-values'){
 let synthetic=0,nodes=0;const fresh=(env:ReadonlyMap<string,CoreValueType>)=>{let name:string;do{name='core_internal_'+(++synthetic);}while(env.has(name));return name;};
 const requireType=(expected:CoreValueType,actual:CoreValueType,where:CoreSourceRange)=>{if(!acceptsCoreValueType(expected,actual))fail('TypeMismatch',where,'expected '+JSON.stringify(expected)+' but received '+JSON.stringify(actual));};
 const wrap=(type:CoreValueType,expression:GenericExprV1):CoreGenericTypedExpression=>{if(generic)assertCoreGenericValueType(types,type,{path:'generic-expression',start:0,end:0},mode);return {type,expression};};
 const envAdd=(ctx:Context,bindings:readonly {name:string;type:CoreValueType}[],where:CoreSourceRange):Context=>{const env=new Map(ctx.env);for(const b of bindings){if(env.has(b.name))fail('DuplicateSymbol',where,'binder shadows or duplicates '+b.name);env.set(b.name,b.type);}return {...ctx,env};};
 const binder=(b:CoreLambda,ctx:Context):{name:string;type:CoreValueType}=>{const type=types.type(ctx.module,b.type,b.span);wrap(type,{op:'var',name:b.name});return {name:b.name,type};};
 const bindAst=(b:{name:string;type:CoreValueType})=>({name:b.name,type:coreValueAstType(b.type)});
 const sourceName=(n:CoreExpression):string|null=>n.kind==='name'?n.name:n.kind==='field'?(sourceName(n.value)?sourceName(n.value)+'.'+n.field:null):null;
 const lookup=(name:string,ctx:Context,where:CoreSourceRange):CoreGenericTypedExpression=>{
  const parts=name.split('.'),root=parts[0]!,variable=ctx.env.get(root);
  if(variable){let result=wrap(variable,{op:'var',name:root}),prefix=root;if(ctx.narrowed?.has(prefix)&&result.type.kind==='optional')result=wrap(result.type.value,{op:'require_some',value:result.expression});for(const part of parts.slice(1)){prefix+='.'+part;result=field(result,part,where);if(ctx.narrowed?.has(prefix)&&result.type.kind==='optional')result=wrap(result.type.value,{op:'require_some',value:result.expression});}return result;}
  if(parts.length>1){const tag=parts.at(-1)!,owner=types.resolve(ctx.module,parts.slice(0,-1).join('.'),where);if(owner.surface!=='Enum')fail('TypeMismatch',where,'qualified constant must select declared enum');const variant=owner.variants.find(v=>v.name===tag);if(!variant)fail('UnknownReference',where,'enum variant absent '+tag);if(variant.fields.length)fail('MissingMapping',where,'payload variant requires its constructor arguments');return wrap({kind:'enum',name:owner.id},{op:'enum_value',type_name:owner.id,variant:tag,fields:{}});}
  return fail('UnknownReference',where,'unbound pure value '+name);
 };
 const field=(value:CoreGenericTypedExpression,name:string,where:CoreSourceRange):CoreGenericTypedExpression=>{const f=types.fields(value.type,where).find(f=>f.name===name);if(!f)fail('UnknownReference',where,'record field absent '+name);return wrap(f.type,{op:'field',value:value.expression,field:name});};
 const withoutFact=(ctx:Context,key:string|null):Context=>{const narrowed=new Set(ctx.narrowed);if(key)narrowed.delete(key);return {...ctx,narrowed};};
 const truth=(ctx:Context,n:CoreExpression,yes:boolean):Context=>{
  if(n.kind==='not')return truth(ctx,n.value,!yes);
  if(n.kind==='binary'&&(n.operator==='and'&&yes||n.operator==='or'&&!yes))return truth(truth(ctx,n.left,yes),n.right,yes);
  if(n.kind==='invoke'&&['present','absent'].includes(n.name)&&n.args.length===1){const key=sourceName(n.args[0]!.value);if(key){const value=lookup(key,withoutFact(ctx,key),n);if(value.type.kind==='optional'){const narrowed=new Set(ctx.narrowed);if(n.name==='present'&&yes||n.name==='absent'&&!yes)narrowed.add(key);else narrowed.delete(key);return {...ctx,narrowed};}}}
  return ctx;
 };
 const scalarLiteral=(node:CoreExpression&{kind:'number'|'string'|'Bool';value:string},expected:CoreValueType|undefined):CoreGenericTypedExpression=>{
  if(node.kind==='number'){if(!/^(0|[1-9][0-9]*)$/.test(node.value)||BigInt(node.value)>18446744073709551615n)fail('TypeMismatch',node,'literal outside exact UInt64');if(expected)requireType(expected,CORE_UINT64,node);return wrap(CORE_UINT64,{op:'literal',type:coreValueAstType(CORE_UINT64),value:node.value});}
  if(node.kind==='Bool'){if(expected)requireType(expected,CORE_BOOL,node);return wrap(CORE_BOOL,{op:'literal',type:coreValueAstType(CORE_BOOL),value:node.value==='true'});}
  const type=expected??{kind:'literal' as const,value:node.value},domain=coreStringDomain(type,types);if(!domain)fail('TypeMismatch',node,'string literal requires a bounded string/refinement/literal expected type');
  const bytes=Buffer.byteLength(node.value),scalars=[...node.value].length;if((type.kind==='literal'&&node.value!==type.value)||bytes<domain.min_bytes||bytes>domain.max_bytes||scalars<domain.min_scalars||scalars>domain.max_scalars||domain.pattern!==null&&!matchesCoreRefinementPattern(domain.pattern,node.value,node))fail('TypeMismatch',node,'string literal violates its declared exact/bounded domain');return wrap(type,{op:'literal',type:coreValueAstType(type),value:node.value});
 };
 const call=(n:CoreExpression&{kind:'invoke'},ctx:Context,expected:CoreValueType|undefined):CoreGenericTypedExpression=>{
  if(generic&&n.name==='append'){
   if(n.args.length!==2||n.args.some(a=>a.name!==null))fail('MissingMapping',n,'append requires exactly two positional arguments');
   const source=compile(n.args[0]!.value,ctx,expected?.kind==='List'?expected:undefined);if(source.type.kind!=='List')fail('TypeMismatch',n,'append source requires bounded List');
   const item=compile(n.args[1]!.value,ctx,source.type.value);const list_type=coreValueAstType(source.type);if(list_type.kind!=='list')fail('TypeMismatch',n,'append source list type required');return wrap(source.type,{op:'append',source:source.expression,item:item.expression,list_type});
  }
  const unary=['some','present','absent','require-some','tag','all-unique-exact','length','length-utf8','length-scalars','require-variant'];
  const binary:Readonly<Record<string,'add'|'subtract'|'multiply'|'divide'>>={'checked-add':'add','checked-subtract':'subtract','checked-multiply':'multiply','checked-divide':'divide'};
  if(unary.includes(n.name)||Object.hasOwn(binary,n.name)){
   if(n.args.some(a=>a.name!==null))fail('InvalidContract',n,'intrinsics require positional arguments');const arity=n.name==='require-variant'||Object.hasOwn(binary,n.name)?2:1;if(n.args.length!==arity)fail('MissingMapping',n,'intrinsic arity differs');
   if(Object.hasOwn(binary,n.name)){const left=compile(n.args[0]!.value,ctx,CORE_UINT64),right=compile(n.args[1]!.value,ctx,CORE_UINT64);return wrap(CORE_UINT64,{op:'binary',operator:binary[n.name]!,left:left.expression,right:right.expression});}
   const argContext=['present','absent','require-some'].includes(n.name)?withoutFact(ctx,sourceName(n.args[0]!.value)):ctx;
   const arg=compile(n.args[0]!.value,argContext,n.name==='some'&&expected?.kind==='optional'?expected.value:undefined);
   if(n.name==='some')return wrap({kind:'optional',value:arg.type},{op:'some',value:arg.expression});
   if(n.name==='present'||n.name==='absent'||n.name==='require-some'){if(arg.type.kind!=='optional')fail('TypeMismatch',n,'optional intrinsic needs optional value');return wrap(n.name==='require-some'?arg.type.value:CORE_BOOL,{op:n.name==='require-some'?'require_some':n.name,value:arg.expression});}
   if(n.name==='all-unique-exact'){if(arg.type.kind!=='List')fail('TypeMismatch',n,'uniqueness requires bounded List');return wrap(CORE_BOOL,{op:'all_unique_exact',value:arg.expression});}
   if(n.name==='tag'){if(arg.type.kind!=='enum'&&arg.type.kind!=='variant'&&arg.type.kind!=='outcome')fail('TypeMismatch',n,'tag requires enum/variant/outcome');return wrap({kind:'String',max_bytes:256,max_scalars:256},{op:'tag',value:arg.expression});}
   if(n.name==='require-variant'){
    const v=n.args[1]!.value;if(v.kind!=='name')fail('TypeMismatch',v,'variant selector must be a declared enum variant');const p=v.name.lastIndexOf('.');if(p<0)fail('UnknownReference',v,'qualified variant required');const d=types.resolve(ctx.module,v.name.slice(0,p),v),variant=v.name.slice(p+1);if(d.surface!=='Enum'||!d.variants.some(v=>v.name===variant)||(arg.type.kind!=='enum'&&arg.type.kind!=='variant')||arg.type.name!==d.id)fail('TypeMismatch',v,'variant does not belong to actual enum');return wrap({kind:'variant',name:d.id,variant},{op:'require_variant',value:arg.expression,enum_name:d.id,variant});
   }
   if(n.name==='length'){if(arg.type.kind!=='List')fail('TypeMismatch',n,'length accepts List; text requires explicit unit');return wrap(CORE_UINT64,{op:'length',value:arg.expression,unit:'items'});}
   if(!coreStringDomain(arg.type,types))fail('TypeMismatch',n,'text length requires bounded string carrier');return wrap(CORE_UINT64,{op:'length',value:arg.expression,unit:n.name==='length-utf8'?'utf8-bytes':'unicode-scalars'});
  }
  const propose=n.name.endsWith('.propose'),name=propose?n.name.slice(0,-8):n.name;
  let d:CoreCommerceDeclaration|undefined,variant:string|undefined;
  const dot=name.lastIndexOf('.');
  // A payload variant constructor resolves its owner against this module/imports,
  // never against a globally unique tag name.
  if(dot>=0){try{const owner=types.resolve(ctx.module,name.slice(0,dot),n);if(owner.surface==='Enum'){d=owner;variant=name.slice(dot+1);}}catch(error){if((error as {diagnostics?:readonly {code:string}[]}).diagnostics?.[0]?.code!=='UnknownReference')throw error;}}
  d??=types.resolve(ctx.module,name,n);
  if(propose&&d.surface!=='StateMachine')fail('TypeMismatch',n,'propose must select a declared StateMachine');
  if(d.refinement){if(n.args.length!==1||n.args[0]!.name!==null)fail('MissingMapping',n,'refinement constructor needs one positional scalar');const result:CoreValueType={kind:'refinement',name:d.id},arg=n.args[0]!.value;if(arg.kind==='string')return scalarLiteral(arg,result);const checked=compile(arg,ctx);if(sameCoreValueType(checked.type,result))return checked;if(!coreStringDomain(checked.type,types))fail('TypeMismatch',arg,'explicit refinement construction requires bounded scalar text');return wrap(result,{op:'validate_refinement',refinement:d.id,value:checked.expression,on_invalid:'InputType'});}
  let parameters:readonly {name:string;type:CoreValueType}[],result:CoreValueType;
  if(variant!==undefined){const v=d.variants.find(v=>v.name===variant);if(!v)fail('UnknownReference',n,'unknown variant constructor');parameters=v.fields.map(f=>({name:f.name,type:types.type(d.module,f.type,f.span)}));result={kind:'enum',name:d.id};}
  else if(['Entity','ValueObject','Event'].includes(d.surface)&&!d.refinement){parameters=types.fields({kind:'record',name:d.id},n);result={kind:'record',name:d.id};}
  else if(isPure(d)){if(d.surface==='StateMachine'&&!propose)fail('TypeMismatch',n,'StateMachine calls require explicit .propose');parameters=d.parameters.map(p=>({name:p.name,type:types.type(d.module,p.type,p.span)}));result=types.type(d.module,d.result!,d.syntax);ctx.calls.add(d.id);}
  else return fail('UnsupportedCapability',n,'pure expressions cannot invoke an effect, context, interface or unregistered primitive');
  const named=n.args.some(a=>a.name!==null);if(named&&n.args.some(a=>a.name===null)||n.args.length!==parameters.length||new Set(n.args.flatMap(a=>a.name?[a.name]:[])).size!==n.args.filter(a=>a.name!==null).length)fail('MissingMapping',n,'constructor/call requires exact unique named or positional arguments');
  if(named&&n.args.some(a=>!parameters.some(p=>p.name===a.name)))fail('UnknownReference',n,'unknown named argument');
  const args=parameters.map((p,i)=>{const a=named?n.args.find(a=>a.name===p.name):n.args[i];if(!a)fail('MissingMapping',n,'missing argument '+p.name);return compile(a.value,ctx,p.type).expression;});
  const construct=(values:readonly GenericExprV1[]):GenericExprV1=>variant!==undefined?{op:'enum_value',type_name:d.id,variant,fields:Object.fromEntries(parameters.map((p,i)=>[p.name,values[i]!] as const).sort((a,b)=>generic?(a[0]<b[0]?-1:a[0]>b[0]?1:0):0))}:!isPure(d)&&result.kind==='record'?{op:'record',type_name:d.id,fields:Object.fromEntries(parameters.map((p,i)=>[p.name,values[i]!] as const).sort((a,b)=>generic?(a[0]<b[0]?-1:a[0]>b[0]?1:0):0))}:{op:'call',declaration:d.id,arguments:values};
  let expression=construct(args);
  if(named||generic&&!isPure(d)){
   const names=n.args.map(()=>fresh(ctx.env));expression=construct(parameters.map((p,i)=>({op:'var',name:names[named?n.args.findIndex(a=>a.name===p.name):i]!})));
   for(let i=n.args.length-1;i>=0;i--){const index=named?parameters.findIndex(p=>p.name===n.args[i]!.name):i;expression={op:'let',binding:{name:names[i]!,type:coreValueAstType(parameters[index]!.type)},value:args[index]!,body:expression};}
  }
  return wrap(result,expression);
 };
 const compile=(n:CoreExpression,ctx:Context,expected?:CoreValueType,depth=0):CoreGenericTypedExpression=>{
  if(depth>32||++nodes>100000)fail('ResourceLimit',n,'pure semantic depth/work limit');
  let result:CoreGenericTypedExpression;
  switch(n.kind){
   case'number':case'string':case'Bool':result=scalarLiteral(n,expected);break;
   case'none':if(expected?.kind!=='optional')fail('MissingMapping',n,'none needs bounded optional expected type');result=wrap(expected,{op:'none',element_type:coreValueAstType(expected.value)});break;
   case'name':{
    if(!n.name.includes('.')&&!ctx.env.has(n.name)&&expected?.kind==='enum'){const d=types.declarations.get(expected.name)!;if(d.variants.some(v=>v.name===n.name&&!v.fields.length)){result=wrap(expected,{op:'enum_value',type_name:d.id,variant:n.name,fields:{}});break;}}
    result=lookup(n.name,ctx,n);break;
   }
   case'field':{const name=sourceName(n);result=name&&ctx.env.has(name.split('.')[0]!)?lookup(name,ctx,n):field(compile(n.value,ctx,undefined,depth+1),n.field,n);break;}
   case'invoke':result=call(n,ctx,expected);break;
   case'not':result=wrap(CORE_BOOL,{op:'unary',operator:'not',value:compile(n.value,ctx,CORE_BOOL,depth+1).expression});break;
   case'list':{
    if(expected&&expected.kind!=='List')fail('TypeMismatch',n,'list expected type differs');let element=expected?.kind==='List'?expected.value:undefined;
    if(!element&&!n.items.length)fail('MissingMapping',n,'empty list needs explicit expected element type');
    if(!element&&n.items.every((e):e is CoreExpression&{kind:'string';value:string}=>e.kind==='string'))element={kind:'String',max_bytes:Math.max(...n.items.map(e=>Buffer.byteLength(e.value))),max_scalars:Math.max(...n.items.map(e=>[...e.value].length))};
    const items=n.items.map(item=>{const t=compile(item,ctx,element,depth+1);element??=t.type;return t.expression;});const max=expected?.kind==='List'?expected.maximum:n.items.length;if(n.items.length>max||max>100)fail('ResourceLimit',n,'list literal exceeds bounded type');result=wrap({kind:'List',value:element!,maximum:max},{op:'list',element_type:coreValueAstType(element!),items});break;
   }
   case'binary':{
    const arithmetic=['+','-','*','/'].includes(n.operator),bool=['and','or','implies'].includes(n.operator),eq=['==','!='].includes(n.operator);
    if(n.operator==='in'){
     const left=compile(n.left,ctx,undefined,depth+1),right=compile(n.right,ctx,{kind:'List',value:left.type,maximum:100},depth+1);if(right.type.kind!=='List')fail('TypeMismatch',n,'membership requires bounded List');
     const temp=fresh(ctx.env),state=fresh(ctx.env),item=fresh(ctx.env);result=wrap(CORE_BOOL,{op:'let',binding:{name:temp,type:coreValueAstType(left.type)},value:left.expression,body:{op:'fold',source:right.expression,initial:{op:'literal',type:coreValueAstType(CORE_BOOL),value:false},state:{name:state,type:coreValueAstType(CORE_BOOL)},item:{name:item,type:coreValueAstType(left.type)},body:{op:'binary',operator:'or',left:{op:'var',name:state},right:{op:'binary',operator:'eq',left:{op:'var',name:temp},right:{op:'var',name:item}}}}});break;
    }
    if(generic&&mode==='event-handoff-entry'&&n.operator==='+'&&(expected&&coreStringDomain(expected,types)||n.left.kind==='string'||n.right.kind==='string')){
     const right=n.left.kind==='string'?compile(n.right,ctx,expected,depth+1):null;
     const left=compile(n.left,ctx,expected??right?.type,depth+1);
     const other=right??compile(n.right,ctx,expected??left.type,depth+1);
     const resultType=expected??(left.type.kind==='String'?left.type:other.type);
     if(resultType.kind!=='String'||!coreStringDomain(left.type,types)||!coreStringDomain(other.type,types))fail('TypeMismatch',n,'V4 string concatenation requires a bounded String result and bounded operands');
     result=wrap(resultType,{op:'concat',left:left.expression,right:other.expression,result_type:coreValueAstType(resultType)});break;
    }
    const wanted=arithmetic?CORE_UINT64:bool?CORE_BOOL:undefined;
    // Infer a literal's domain from its nonliteral peer, retaining source order
    // in the resulting AST even when the typing pass visits the peer first.
    const literal=(e:CoreExpression)=>['number','string','Bool','none','list'].includes(e.kind);
    let left:CoreGenericTypedExpression,right:CoreGenericTypedExpression;
    if(n.left.kind==='string'&&n.right.kind==='string'){
     const common:CoreValueType={kind:'String',max_bytes:Math.max(Buffer.byteLength(n.left.value),Buffer.byteLength(n.right.value)),max_scalars:Math.max([...n.left.value].length,[...n.right.value].length)};left=compile(n.left,ctx,common,depth+1);right=compile(n.right,ctx,common,depth+1);
    }else if(!wanted&&literal(n.left)&&!literal(n.right)){right=compile(n.right,ctx,undefined,depth+1);left=compile(n.left,ctx,right.type,depth+1);}else{left=compile(n.left,ctx,wanted,depth+1);const rightContext=n.operator==='and'||n.operator==='implies'?truth(ctx,n.left,true):n.operator==='or'?truth(ctx,n.left,false):ctx;right=compile(n.right,rightContext,wanted??left.type,depth+1);}
    if(!wanted&&!acceptsCoreValueType(left.type,right.type)&&!acceptsCoreValueType(right.type,left.type))fail('TypeMismatch',n,'comparison operands have incompatible types');
    if(!arithmetic&&!bool&&!eq&&left.type.kind!=='UInt64')fail('TypeMismatch',n,'ordered comparisons require UInt64');
    const operators:Readonly<Record<string,'eq'|'lt'|'lte'|'gt'|'gte'|'add'|'subtract'|'multiply'|'divide'|'and'|'or'>>={'==':'eq','!=':'eq','<':'lt','<=':'lte','>':'gt','>=':'gte','+':'add','-':'subtract','*':'multiply','/':'divide',and:'and',or:'or',implies:'or'};
    const ast:GenericExprV1={op:'binary',operator:operators[n.operator]!,left:n.operator==='implies'?{op:'unary',operator:'not',value:left.expression}:left.expression,right:right.expression};result=wrap(arithmetic?CORE_UINT64:CORE_BOOL,n.operator==='!='?{op:'unary',operator:'not',value:ast}:ast);break;
   }
   case'map':case'filter':{
    const source=compile(n.source,ctx,undefined,depth+1);if(source.type.kind!=='List')fail('TypeMismatch',n,'map/filter source requires bounded List');const item=binder(n.item,ctx);requireType(item.type,source.type.value,n.item.span);const body=compile(n.body,envAdd(ctx,[item],n),n.kind==='filter'?CORE_BOOL:expected?.kind==='List'?expected.value:undefined,depth+1);
    result=n.kind==='map'?wrap({kind:'List',value:body.type,maximum:source.type.maximum},{op:'map',source:source.expression,item:bindAst(item),body:body.expression}):wrap(source.type,{op:'filter',source:source.expression,item:bindAst(item),predicate:body.expression});break;
   }
   case'fold':case'indexed-fold':{
    const source=compile(n.source,ctx,undefined,depth+1);if(source.type.kind!=='List')fail('TypeMismatch',n,'fold source requires bounded List');const state=binder(n.state,ctx),item=binder(n.item,ctx);requireType(item.type,source.type.value,n.item.span);const index=n.index?binder(n.index,ctx):null;if(index)requireType(CORE_UINT64,index.type,n.index!.span);const initial=compile(n.initial,ctx,state.type,depth+1),body=compile(n.body,envAdd(ctx,[state,item,...index?[index]:[]],n),state.type,depth+1);
    result=wrap(state.type,index?{op:'indexed_fold',source:source.expression,initial:initial.expression,state:bindAst(state),item:bindAst(item),index:bindAst(index),body:body.expression}:{op:'fold',source:source.expression,initial:initial.expression,state:bindAst(state),item:bindAst(item),body:body.expression});break;
   }
   case'repeat':case'while-bounded':case'until-bounded':{
    const state=binder(n.state,ctx),initial=compile(n.initial,ctx,state.type,depth+1);if(n.kind==='repeat'){const index=binder(n.index,ctx);requireType(CORE_UINT64,index.type,n.index.span);const count=compile(n.count,ctx,CORE_UINT64,depth+1),body=compile(n.body,envAdd(ctx,[state,index],n),state.type,depth+1);result=wrap(state.type,{op:'repeat',count:count.expression,max_iterations:n.maximum,initial:initial.expression,state:bindAst(state),index:bindAst(index),body:body.expression});}
    else{const inner=envAdd(ctx,[state],n),guard=compile(n.guard,inner,CORE_BOOL,depth+1),body=compile(n.body,inner,state.type,depth+1);result=wrap(state.type,{op:n.kind==='while-bounded'?'while_bounded':'until_bounded',max_iterations:n.maximum,initial:initial.expression,state:bindAst(state),guard:guard.expression,body:body.expression});}break;
   }
   case'range':{const first=compile(n.first,ctx,CORE_UINT64,depth+1),last=compile(n.last,ctx,CORE_UINT64,depth+1),step=compile(n.step,ctx,CORE_UINT64,depth+1);result=wrap({kind:'List',value:CORE_UINT64,maximum:n.maximum},{op:'range',start:first.expression,end:last.expression,step:step.expression,max_iterations:n.maximum});break;}
   case'sort':{
    const source=compile(n.source,ctx,undefined,depth+1);if(source.type.kind!=='List')fail('TypeMismatch',n,'sort source requires bounded List');const item=n.item?binder(n.item,ctx):{name:fresh(ctx.env),type:source.type.value};requireType(item.type,source.type.value,n);const inner=envAdd(ctx,[item],n);
    const keys=n.keys.map(key=>{const value=typeof key.value==='string'?field(wrap(item.type,{op:'var',name:item.name}),key.value,n):compile(key.value,inner,undefined,depth+1);if(key.mode==='numeric')requireType(CORE_UINT64,value.type,n);else if(!coreStringDomain(value.type,types))fail('TypeMismatch',n,'lexical/natural sort needs bounded string carrier');return {value:value.expression,direction:key.direction,mode:key.mode};});result=wrap(source.type,{op:'sort',source:source.expression,item:bindAst(item),keys});break;
   }
   case'match':result=match(n,ctx,expected,depth);break;
  }
  if(expected)requireType(expected,result.type,n);return result;
 };
 const match=(n:CoreExpression&{kind:'match'},ctx:Context,expected:CoreValueType|undefined,depth:number):CoreGenericTypedExpression=>{
  const source=compile(n.value,ctx,undefined,depth+1),seen=new Set<string>();let resultType=expected;
  if(source.type.kind==='optional'){
   if(n.cases.length!==1||n.cases[0]!.patterns.length!==1||n.cases[0]!.patterns[0]!.name!=='some'||!n.cases[0]!.patterns[0]!.binding||!n.otherwise)fail('NonExhaustive',n,'optional match requires one some binder and an else');
   const user={name:n.cases[0]!.patterns[0]!.binding!,type:source.type.value},name=fresh(ctx.env),yes=compile(n.cases[0]!.body,envAdd(ctx,[user],n),expected,depth+1),no=compile(n.otherwise,ctx,expected??yes.type,depth+1);requireType(yes.type,no.type,n);
   return wrap(expected??yes.type,{op:'let',binding:{name,type:coreValueAstType(source.type)},value:source.expression,body:{op:'if',condition:{op:'present',value:{op:'var',name}},then:{op:'let',binding:bindAst(user),value:{op:'require_some',value:{op:'var',name}},body:yes.expression},else:no.expression}});
  }
  if(source.type.kind==='Bool'){
   let yes:GenericExprV1|undefined,no:GenericExprV1|undefined;for(const c of n.cases)for(const p of c.patterns){if(p.binding||!['true','false'].includes(p.name)||seen.has(p.name))fail('InvalidContract',p.span,'Boolean patterns must be unique true/false');seen.add(p.name);const b=compile(c.body,truth(ctx,n.value,p.name==='true'),resultType,depth+1);resultType??=b.type;if(p.name==='true')yes=b.expression;else no=b.expression;}
   if(n.otherwise){const otherwiseCtx=yes&&!no?truth(ctx,n.value,false):no&&!yes?truth(ctx,n.value,true):ctx,other=compile(n.otherwise,otherwiseCtx,resultType,depth+1);resultType??=other.type;yes??=other.expression;no??=other.expression;}if(!yes||!no)fail('NonExhaustive',n,'Bool match missing alternative');return wrap(resultType!,{op:'if',condition:source.expression,then:yes,else:no});
  }
  if(source.type.kind!=='enum'&&source.type.kind!=='variant')fail('TypeMismatch',n,'match requires checked optional, Bool or enum');const d=types.declarations.get(source.type.name)!;
  const cases:{variant:string;binding:string|null;then:GenericExprV1}[]=[];
  for(const c of n.cases)for(const p of c.patterns){const dot=p.name.lastIndexOf('.'),tag=dot<0?p.name:p.name.slice(dot+1);if(dot>=0&&types.resolve(ctx.module,p.name.slice(0,dot),p.span).id!==d.id)fail('TypeMismatch',p.span,'pattern belongs to another enum');const v=d.variants.find(v=>v.name===tag);if(!v)fail('UnknownReference',p.span,'variant absent from actual subject enum');if(seen.has(tag))fail('DuplicateSymbol',p.span,'repeated pure match pattern');seen.add(tag);let inner=ctx;
   if(p.binding){if(!v.fields.length)fail('TypeMismatch',p.span,'nullary enum cannot bind a payload');const type=v.fields.length===1?types.type(d.module,v.fields[0]!.type,v.fields[0]!.span):{kind:'variant' as const,name:d.id,variant:tag};inner=envAdd(ctx,[{name:p.binding,type}],p.span);}
   // Every grouped branch is checked independently under its actual payload.
   const body=compile(c.body,inner,resultType,depth+1);resultType??=body.type;cases.push({variant:tag,binding:p.binding,then:body.expression});
  }
  const other=n.otherwise?compile(n.otherwise,ctx,resultType,depth+1):null;resultType??=other?.type;if(!other&&d.variants.some(v=>!seen.has(v.name)))fail('NonExhaustive',n,'match omits a declared variant');if(!resultType)fail('NonExhaustive',n,'empty match');return wrap(resultType,{op:'match_variant',value:source.expression,cases,otherwise:other?.expression??null});
 };
 const finish=(expression:GenericExprV1,where:CoreSourceRange)=>{let count=0;const stack:{value:unknown;depth:number}[]=[{value:expression,depth:0}];while(stack.length){const {value,depth}=stack.pop()!;if(!value||typeof value!=='object')continue;const ast='op'in value;if(ast&&(++count>4096||depth>32))fail('ResourceLimit',where,'normalized pure AST size/depth limit');for(const child of Object.values(value))stack.push({value:child,depth:depth+(ast?1:0)});}};
 return {compile,envAdd,bindAst,requireType,finish,reset(){synthetic=0;nodes=0;}};
}
export function createCorePureExpressionChecker(types:CoreValueTypes){
 const e=createPureExpressionChecker(types,false);return {...e,compile:(...args:Parameters<typeof e.compile>):CoreTypedExpression=>requireLegacyExpressionData<CoreTypedExpression>(e.compile(...args))};
}
export function createCoreGenericPureExpressionChecker(types:CoreValueTypes,mode:CoreGenericAdmissionMode='bounded-values'){
 coreGenericAdmissionMode(mode);
 assertCoreGenericValueTypes(types,mode);for(const d of types.declarations.values())if(d.name==='append'&&['ValueObject','Entity','Event','Enum','Rule','Calculation','Mapping','Policy','Operation','StateMachine'].includes(d.surface))fail('DuplicateSymbol',d.syntax,'append is a reserved generic intrinsic');for(const m of types.modules.values())for(const i of m.imports)if(i.alias==='append')fail('DuplicateSymbol',i.span,'append is a reserved generic intrinsic alias');
 return createPureExpressionChecker(types,true,mode);
}
export function checkCoreGenericPureSources(sources:readonly {readonly path:string;readonly text:string}[],mode:CoreGenericAdmissionMode='bounded-values'):CoreGenericPureSemantics {
 coreGenericAdmissionMode(mode);
 return reconstructPure(reconstructCoreCommerceSources(sources,(mode==='keyed-query-entry'||(mode==='atomic-state-entry'||mode==='external-read-entry'||(mode==='external-write-entry'||mode==='event-handoff-entry')))?mode:'legacy'),true,mode) as CoreGenericPureSemantics;
}
export function checkCoreCommercePureSources(sources:readonly {readonly path:string;readonly text:string}[]):CorePureSemantics {
 return requireLegacyExpressionData<CorePureSemantics>(reconstructPure(reconstructCoreCommerceSources(sources),false));
}
/** Transfer is inert data only. Core reconstructs every field from source and
 * compares the whole candidate; retaining its hash or role labels is not enough.
 * JSON correspondence does not restore source/review/native/application custody. */
export function checkCoreCommercePureProposal(sources:readonly {readonly path:string;readonly text:string}[],proposal:unknown):CorePureSemantics {
 const actual=checkCoreCommercePureSources(sources);let candidate:string;
 try{candidate=dataDigest(proposal);}catch{return fail('InvalidContract',{path:sources[0]?.path??'application.alch',start:0,end:0},'inert closed bounded pure proposal data required');}
 if(candidate!==dataDigest(actual))fail('InvalidContract',{path:sources[0]?.path??'application.alch',start:0,end:0},'pure proposal differs from independently reconstructed source semantics');return actual;
}
function reconstructPure(reconstruction:CoreCommerceReconstruction,generic:boolean,mode:CoreGenericAdmissionMode='bounded-values') {
 const types=createCoreValueTypes(reconstruction),engine=createPureExpressionChecker(types,generic,mode),declarations:CoreGenericPureDeclaration[]=[],edges=new Map<string,Set<string>>();
 if(generic){assertCoreGenericValueTypes(types,mode);for(const m of reconstruction.modules)for(const i of m.imports)if(i.alias==='append')fail('DuplicateSymbol',i.span,'append is a reserved generic intrinsic alias');}
 if(generic)for(const d of types.declarations.values())if(d.name==='append'&&['ValueObject','Entity','Event','Enum','Rule','Calculation','Mapping','Policy','Operation','StateMachine'].includes(d.surface))fail('DuplicateSymbol',d.syntax,'append is a reserved generic intrinsic');
 const valueDeclarations:CoreValueDeclaration[]=[];
 for(const d of types.declarations.values())if(['Entity','ValueObject','Event','Enum'].includes(d.surface)&&!d.refinement){
  valueDeclarations.push({name:d.id,role:d.surface as CoreValueDeclaration['role'],fields:d.fields.map(f=>({name:f.name,type:types.type(d.module,f.type,f.span)})),variants:d.variants.map(v=>({name:v.name,wire:v.wire,fields:v.fields.map(f=>({name:f.name,type:types.type(d.module,f.type,f.span)}))})),identity:d.identity,unique:d.unique,immutable:d.immutable,event_version:d.surface==='Event'?1:null});
 }
 const predicates:CorePureSemantics['collection_predicates'][number][]= [];
 for(const d of types.declarations.values())if(d.interface_kind==='bounded-schema')for(const c of children(d.syntax,'interface-clause').flatMap(c=>children(c,'value-domain-clause'))){
  const ts=words(c);if(ts[0]!=='validates')continue;const sourceType=children(c,'type')[0]!;
  const declared=types.type(d.module,parseCoreTypeTokens(tokens(sourceType),sourceType),sourceType);
  const using=ts[ts.indexOf('using')+1]!;
  if(using==='declared-refinement'){if(declared.kind!=='refinement')fail('TypeMismatch',c,'association requires declared refinement');continue;}
  if(using==='closed-enum'){if(declared.kind!=='enum')fail('TypeMismatch',c,'association requires closed enum');continue;}
  if(using==='closed-fields-and-invariants'){if(declared.kind!=='record')fail('TypeMismatch',c,'association requires closed record');continue;}
  const target=types.resolve(d.module,children(c,'qualified-name').map(text).at(-1)??using,c);
  if(target.surface!=='Rule'||target.parameters.length!==1||!sameCoreValueType(types.type(target.module,target.parameters[0]!.type,target.parameters[0]!.span),declared))fail('TypeMismatch',c,'collection validation must select exact unary Bool Rule');
  if(predicates.some(p=>sameCoreValueType(p.type,declared)))fail('DuplicateSymbol',c,'duplicate collection predicate association');predicates.push({type:declared,rule:target.id});
 }
 for(const d of types.declarations.values())if(isPure(d)){
  engine.reset();
  const parameters=d.parameters.map(p=>({name:p.name,type:types.type(d.module,p.type,p.span)})),result=types.type(d.module,d.result!,d.syntax),calls=new Set<string>(),ctx:Context={module:d.module,env:new Map(parameters.map(p=>[p.name,p.type])),calls};edges.set(d.id,calls);
  const n=d.syntax,preconditions:GenericExprV1[]=[],terminal:GenericExprV1[]=[];let body:GenericExprV1,rounding:'floor'|'ceil'|'reject'='reject',onError:CorePureDeclaration['on_evaluation_error']=null,initial:GenericExprV1|null=null,reason:string|null=null;
  if(d.surface==='Rule'||d.surface==='Calculation'){
   body=engine.compile(parseCoreExpressionValue(child(n,'expression-value')),ctx,result).expression;
   const direct=n.children.flatMap(c=>'token'in c&&!c.layout?[c.token]:[]),r=direct.indexOf('rounding');if(r>=0)rounding=direct[r+1] as typeof rounding;const on=children(n,'failure-action')[0];if(on)onError={kind:words(on)[0] as 'reject'|'fail',code:words(on)[1]!};
  }else if(d.surface==='Mapping'){
   for(const e of children(n,'expression'))preconditions.push(engine.compile(parseCoreExpression(e),ctx,CORE_BOOL).expression);
   const m=child(n,'mapping-body'),expr=children(m,'expression-value')[0],cases=children(m,'ordered-case');
   if(expr)body=engine.compile(parseCoreExpressionValue(expr),ctx,result).expression;
   else if(cases.length){
    const names=cases.map(c=>words(c)[0]!);if(new Set(names).size!==names.length)fail('DuplicateSymbol',m,'ordered case label repeated');let otherwise:GenericExprV1|null=null;
    for(let i=cases.length-1;i>=0;i--){const c=cases[i]!,es=children(c,'expression');if(words(c)[1]==='otherwise'){if(i!==cases.length-1||otherwise)fail('NonExhaustive',c,'otherwise must be unique and last');otherwise=engine.compile(parseCoreExpression(es[0]!),ctx,result).expression;}else{if(!otherwise)fail('NonExhaustive',c,'total ordered mapping needs last otherwise');otherwise={op:'if',condition:engine.compile(parseCoreExpression(es[0]!),ctx,CORE_BOOL).expression,then:engine.compile(parseCoreExpression(es[1]!),ctx,result).expression,else:otherwise};}}
    if(!otherwise)fail('NonExhaustive',m,'mapping has no case result');body=otherwise;
   }else{
    if(result.kind!=='record')fail('TypeMismatch',m,'field Mapping requires declared record target');const fields=types.fields(result,m),assigned:Record<string,GenericExprV1>=Object.create(null),preserved=children(m,'name-list').flatMap(list=>children(list,'qualified-name').map(text));
    for(const f of children(m,'field-binding')){const name=words(f)[1]!,target=fields.find(f=>f.name===name);if(!target)fail('UnknownReference',f,'Mapping target field absent');if(Object.hasOwn(assigned,name))fail('DuplicateSymbol',f,'Mapping assigns field twice');assigned[name]=engine.compile(parseCoreExpression(child(f,'expression')),ctx,target.type).expression;}
    if(new Set(preserved).size!==preserved.length)fail('DuplicateSymbol',m,'preserve repeats a field');if(preserved.length){const candidates=parameters.filter(p=>sameCoreValueType(p.type,result));if(candidates.length!==1)fail('InvalidContract',m,'preserve needs exactly one target-record input');for(const name of preserved){if(!fields.some(f=>f.name===name)||Object.hasOwn(assigned,name))fail('InvalidContract',m,'preserved/assigned fields must be declared and disjoint');assigned[name]={op:'field',value:{op:'var',name:candidates[0]!.name},field:name};}}
    if(fields.some(f=>!Object.hasOwn(assigned,f.name)))fail('MissingMapping',m,'Mapping must cover every target field');body={op:'record',type_name:result.name,fields:Object.fromEntries(fields.map(f=>[f.name,assigned[f.name]!]))};
   }
  }else if(d.surface==='Policy'){
   const cases=children(n,'policy-case'),labels=new Set<string>(),actions:{condition:GenericExprV1;action:{calculation:string;expression:GenericExprV1}}[]=[];
   const action=(invocation:CoreSourceNode)=>{const ast=parseCoreExpression(invocation);if(ast.kind!=='invoke')fail('TypeMismatch',invocation,'Policy selects an explicit Calculation');const target=types.resolve(d.module,ast.name,invocation);if(target.surface!=='Calculation')fail('TypeMismatch',invocation,'Policy may select only Calculation');const checked=engine.compile(ast,ctx,result);return {calculation:target.id,expression:checked.expression};};
   for(const c of cases){const label=words(c)[0]!;if(labels.has(label))fail('DuplicateSymbol',c,'Policy case label repeated');labels.add(label);actions.push({condition:engine.compile(parseCoreExpression(child(c,'expression')),ctx,CORE_BOOL).expression,action:action(child(c,'invocation'))});}
   const otherwise=action(children(n,'invocation')[0]??fail('NonExhaustive',n,'Policy missing otherwise'));body={op:'policy',declaration:d.id,cases:actions,otherwise};
  }else{
   if(result.kind!=='outcome'||result.state.kind!=='enum')fail('TypeMismatch',n,'StateMachine state must be declared enum');const event=parameters[1]!.type;if(event.kind!=='enum')fail('TypeMismatch',n,'StateMachine input must be declared enum');
   if(generic){assertCoreGenericNullaryControl(types,result.state,n);assertCoreGenericNullaryControl(types,event,n);}
   const names=children(n,'qualified-name'),value=(name:CoreSourceNode,type:CoreValueType)=>engine.compile({...range(name),kind:'name',name:text(name)},ctx,type).expression;
   initial=value(names[0]!,result.state);for(const list of children(n,'name-list'))for(const name of children(list,'qualified-name'))terminal.push(value(name,result.state));
   const transitions=children(n,'machine-transition').map(t=>{const q=children(t,'qualified-name'),state=value(q[0]!,result.state),input=value(q[1]!,event),next=value(q[2]!,result.state),guard:GenericExprV1={op:'binary',operator:'and',left:{op:'binary',operator:'eq',left:{op:'var',name:'state'},right:state},right:{op:'binary',operator:'eq',left:{op:'var',name:'event'},right:input}},extra=children(t,'expression')[0];if(generic&&terminal.some(v=>dataDigest(v)===dataDigest(state))&&dataDigest(state)!==dataDigest(next))fail('InvalidContract',t,'terminal StateMachine state cannot transition to a different state');return {guard:extra?{op:'binary' as const,operator:'and' as const,left:guard,right:engine.compile(parseCoreExpression(extra),ctx,CORE_BOOL).expression}:guard,next,intents:[]};});
   const ts=words(n),otherwise=ts.lastIndexOf('otherwise'),mode=ts[otherwise+1];if(mode!=='stay'&&mode!=='reject')fail('InvalidContract',n,'StateMachine requires explicit fallback');reason=mode==='reject'?ts[otherwise+2]!:null;
   body={op:'state_machine',declaration:d.id,state:{op:'var',name:'state'},event:{op:'var',name:'event'},state_binding:engine.bindAst(parameters[0]!),event_binding:engine.bindAst(parameters[1]!),initial,terminal,transitions,otherwise:mode,otherwise_reason:reason,intent_type:coreValueAstType(CORE_BOOL),max_intents:0};
  }
  for(let i=preconditions.length-1;i>=0;i--)body={op:'require_some',value:{op:'if',condition:preconditions[i]!,then:{op:'some',value:body},else:{op:'none',element_type:coreValueAstType(result)}}};
  engine.finish(body,n);declarations.push(coreFreeze({name:d.id,kind:d.surface,parameters,result,body,preconditions,rounding,on_evaluation_error:onError,initial,terminal,otherwise_reason:reason}));
 }
 const recordInvariants:CoreGenericPureSemantics['record_invariants'][number][]=[];
 for(const d of types.declarations.values())if(['Entity','ValueObject','Event'].includes(d.surface)&&!d.refinement){engine.reset();const calls=new Set<string>(),ctx:Context={module:d.module,env:new Map(types.fields({kind:'record',name:d.id},d.syntax).map(f=>[f.name,f.type])),calls};const invariants=children(d.syntax,'record-clause').flatMap(c=>words(c)[0]==='invariant'?children(c,'expression').map(e=>engine.compile(parseCoreExpression(e),ctx,CORE_BOOL).expression):[]);for(const e of invariants)engine.finish(e,d.syntax);recordInvariants.push({record:d.id,invariants});}
 const done=new Set<string>(),active=new Set<string>();const visit=(name:string,depth:number)=>{if(active.has(name))fail('InvalidContract',types.declarations.get(name)!.syntax,'recursive pure call dependency');if(done.has(name))return;if(depth>32)fail('ResourceLimit',types.declarations.get(name)!.syntax,'pure call depth');active.add(name);for(const to of edges.get(name)??[])visit(to,depth+1);active.delete(name);done.add(name);};for(const name of edges.keys())visit(name,0);
 const subject={declarations:[...declarations].sort((a,b)=>a.name<b.name?-1:a.name>b.name?1:0),value_declarations:valueDeclarations.sort((a,b)=>a.name<b.name?-1:a.name>b.name?1:0),collection_predicates:predicates.sort((a,b)=>a.rule<b.rule?-1:a.rule>b.rule?1:0),record_invariants:recordInvariants.sort((a,b)=>a.record<b.record?-1:a.record>b.record?1:0),source_refinements:[...types.refinements.values()].sort((a,b)=>a.name<b.name?-1:a.name>b.name?1:0)};
 return coreFreeze({schema_version:generic?'craft.generic-core-pure-semantics/v1-candidate' as const:'craft.commerce-core-pure-semantics/v1-candidate' as const,qualification:'independent-pure-component-data-only',...subject,pure_subject_sha256:dataDigest(subject),authority_effect:'none'});
}
