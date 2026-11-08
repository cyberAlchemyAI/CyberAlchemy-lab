/** Executable type/call layout derived from original source-checked v2 data.
 * This projection is data, not an owner or an evaluator.
 * Open Questions: docs/COMMERCE-COMPUTATION-V2.md#open-questions. */
import {dataDigest} from '../profile-engine/contracts.js';
import {requireLegacyExpressionData} from './commerce-core-pure.js';
import type {GenericComputationContractV1,GenericExprV1} from '../generic/computation-data-v1.js';
import {coreFreeze,coreSourceFail as fail} from './commerce-core-syntax.js';
import {COMMERCE_TYPE_LIMITS_V1} from './commerce-stages-v1.js';
import type {ComputationContractV1,ExprV1,ValueTypeV1,BinderV1,PureDeclarationV1,EvaluationErrorActionV1} from './commerce-data-v1.js';
export interface CommerceExpressionSlot {readonly path:string;readonly type:ValueTypeV1;readonly owner:string;readonly op:ExprV1['op']}
export interface CommercePureCallBinding {readonly path:string;readonly owner:string;readonly declaration:string;readonly kind:PureDeclarationV1['kind'];readonly arguments:readonly BinderV1[];readonly result:ValueTypeV1;readonly rounding:PureDeclarationV1['rounding'];readonly on_evaluation_error:EvaluationErrorActionV1|null;readonly evaluation_order:'source-order-arguments;original-hygienic-lets-retained'}
export interface CommercePolicyActionBinding {readonly path:string;readonly policy:string;readonly branch:string;readonly calculation:string;readonly invocation_path:string;readonly invocation_entered:'must-be-observed-at-that-callsite;not-inferred-from-selection'}
export interface CommerceComputationEnvironment {
 readonly kind:'commerce-computation-environment/v2-candidate';readonly source_node:string;
 readonly expressions:readonly CommerceExpressionSlot[];readonly calls:readonly CommercePureCallBinding[];readonly policy_actions:readonly CommercePolicyActionBinding[];
 readonly graph:readonly {readonly declaration:string;readonly calls:readonly string[]}[];
 readonly counts:Readonly<{expressions:number;calls:number;records:number;enums:number;refinements:number;functions:number}>;
 readonly subject_sha256:string;readonly qualification:'source-checked-type-and-call-layout-only;no-evaluation-or-native-generation';readonly authority_effect:'none';
}
export interface GenericComputationEnvironment extends Omit<CommerceComputationEnvironment,'kind'|'expressions'>{readonly kind:'generic-computation-environment/v1-candidate';readonly expressions:readonly (Omit<CommerceExpressionSlot,'op'>&{readonly op:GenericExprV1['op']})[]}
const bool:ValueTypeV1={kind:'scalar',name:'Bool'},uint:ValueTypeV1={kind:'scalar',name:'UInt64'},text:ValueTypeV1={kind:'string',max_bytes:256,max_scalars:256};
const at=(path:string)=>({path,start:0,end:0});
const same=(a:ValueTypeV1,b:ValueTypeV1)=>dataDigest(a)===dataDigest(b);
function accepts(a:ValueTypeV1,b:ValueTypeV1):boolean {
 if(same(a,b))return true;
 if(a.kind==='enum'&&b.kind==='variant')return a.name===b.enum_name;
 if(a.kind==='optional'&&b.kind==='optional')return accepts(a.element,b.element);
 if(a.kind==='list'&&b.kind==='list')return a.min_items<=b.min_items&&a.max_items>=b.max_items&&accepts(a.element,b.element);
 if(a.kind==='string'&&b.kind==='string')return a.max_bytes>=b.max_bytes&&a.max_scalars>=b.max_scalars;
 if(a.kind==='string'&&b.kind==='literal')return Buffer.byteLength(b.value)<=a.max_bytes&&[...b.value].length<=a.max_scalars;
 return false;
}
function deriveEnvironment(contract:ComputationContractV1|GenericComputationContractV1) {
 const generic=contract.schema_version==='craft.generic-computation/v1-candidate';
 const c=contract,records=new Map(c.values.records.map(r=>[r.name,r])),enums=new Map(c.values.enums.map(r=>[r.name,r])),refinements=new Map(c.values.refinements.map(r=>[r.name,r])),functions=new Map(c.functions.map(f=>[f.name,f]));
 const expressions:(Omit<CommerceExpressionSlot,'op'>&{op:GenericExprV1['op']})[]=[],calls:CommercePureCallBinding[]=[],policy_actions:CommercePolicyActionBinding[]=[],edges=new Map<string,Set<string>>(),seenPaths=new Set<string>();
 const requireType=(actual:ValueTypeV1,expected:ValueTypeV1,p:string)=>{if(!accepts(expected,actual))fail('TypeMismatch',at(p),'source-derived expression type must match its declared binder/result');};
 const fields=(t:ValueTypeV1,p:string):Readonly<Record<string,ValueTypeV1>>=>{
  if(t.kind==='record')return records.get(t.name)?.fields??fail('UnknownReference',at(p),'declared record required');
  if(t.kind==='variant')return enums.get(t.enum_name)?.variants.find(v=>v.name===t.variant)?.fields??fail('UnknownReference',at(p),'declared variant fields required');
  if(t.kind==='outcome')return {tag:{kind:'string',max_bytes:10,max_scalars:10},state:t.state,intents:{kind:'list',element:t.intent,min_items:0,max_items:t.max_intents},machine:text,branch:text,reason:text};
  return fail('TypeMismatch',at(p),'field access requires an explicit checked record/variant/outcome');
 };
 const heights=new Map<string,number>();
 const typeHeight=(t:ValueTypeV1,p:string,active=new Set<string>()):number=>{
  const key=dataDigest(t),prior=heights.get(key);if(prior!==undefined)return prior;
  let height=0;
  if(t.kind==='record'||t.kind==='enum'||t.kind==='variant'){
   const name=t.kind==='variant'?t.enum_name:t.name;if(active.has(name))fail('InvalidContract',at(p),'recursive value schema');const next=new Set(active);next.add(name);let children:readonly ValueTypeV1[];
   if(t.kind==='record'){const r=records.get(name);if(!r)fail('UnknownReference',at(p),'unknown record');children=Object.values(r.fields);}
   else{const e=enums.get(name);if(!e)fail('UnknownReference',at(p),'unknown enum');children=e.variants.flatMap(v=>Object.values(v.fields));}
   for(const child of children)height=Math.max(height,1+typeHeight(child,p,next));
  }else if(t.kind==='refinement'){if(!refinements.has(t.name))fail('UnknownReference',at(p),'unknown scalar refinement');}
  else if(t.kind==='optional'||t.kind==='list'){if(generic&&t.kind==='optional'&&t.element.kind==='optional')fail('TypeMismatch',at(p),'adjacent Optional is outside generic value algebra');height=1+typeHeight(t.element,p,active);}
  else if(t.kind==='outcome')height=1+Math.max(typeHeight(t.state,p,active),typeHeight(t.intent,p,active));
  if(height>COMMERCE_TYPE_LIMITS_V1.source_schema_depth)fail('ResourceLimit',at(p),'declared value schema depth exceeded');heights.set(key,height);return height;
 };
 const bind=(env:ReadonlyMap<string,ValueTypeV1>,b:BinderV1,p:string,allowExisting=false)=>{
  if(env.has(b.name)&&!allowExisting)fail('DuplicateSymbol',at(p),'source binder cannot shadow an existing binder');
  const next=new Map(env);next.set(b.name,b.type);return next;
 };
 const join=(a:ValueTypeV1,b:ValueTypeV1,p:string):ValueTypeV1=>accepts(a,b)?a:accepts(b,a)?b:fail('TypeMismatch',at(p),'source alternatives need one compatible declared result');
 const selectedCall=(expression:GenericExprV1,path:string,calculation:string)=>{let e=expression,p=path;while(e.op==='let'){e=e.body;p+='.body';}if(e.op!=='call'||e.declaration!==calculation)fail('InvalidContract',at(p),'selected Policy calculation must have its own exact invocation callsite');return p;};
 const infer=(e:GenericExprV1,p:string,env:ReadonlyMap<string,ValueTypeV1>,owner:string,depth=1):ValueTypeV1=>{
  if(expressions.length>=c.limits.max_ast_nodes||depth>c.limits.max_ast_depth)fail('ResourceLimit',at(p),'executable AST node/depth budget exceeded');
  if(seenPaths.has(p))fail('InvalidContract',at(p),'one expression at each original path required');seenPaths.add(p);
  // Reserve this node before traversing children so budgets include ancestors.
  const index=expressions.length;expressions.push({path:p,type:bool,owner,op:e.op});
  const sub=(v:GenericExprV1,key:string,en=env)=>infer(v,p+'.'+key,en,owner,depth+1);
  let result:ValueTypeV1;
  switch(e.op){
   case'literal':result=e.type;break;
   case'validate_refinement':sub(e.value,'value');if(!refinements.has(e.refinement))fail('UnknownReference',at(p),'declared scalar refinement required');result={kind:'refinement',name:e.refinement};break;
   case'var':result=env.get(e.name)??fail('UnknownReference',at(p),'source-bound value name required');break;
   case'field':{const f=fields(sub(e.value,'value'),p);if(!Object.hasOwn(f,e.field))fail('UnknownReference',at(p),'declared source field required');result=f[e.field]!;}break;
   case'record':{result={kind:'record',name:e.type_name};const f=fields(result,p);for(const [name,value]of Object.entries(e.fields))requireType(sub(value,'fields.'+name),f[name]??fail('UnknownReference',at(p),'unknown record constructor field'),p);}break;
   case'record_update':{result=sub(e.value,'value');const f=fields(result,p);for(const [name,value]of Object.entries(e.fields))requireType(sub(value,'fields.'+name),f[name]??fail('UnknownReference',at(p),'unknown record update field'),p);}break;
   case'enum_value':{const v=enums.get(e.type_name)?.variants.find(v=>v.name===e.variant);if(!v)fail('UnknownReference',at(p),'declared enum constructor required');for(const [name,value]of Object.entries(e.fields))requireType(sub(value,'fields.'+name),v.fields[name]??fail('UnknownReference',at(p),'unknown variant payload field'),p);result={kind:'enum',name:e.type_name};}break;
   case'list':for(let i=0;i<e.items.length;i++)requireType(sub(e.items[i]!,'items['+i+']'),e.element_type,p);result={kind:'list',element:e.element_type,min_items:0,max_items:e.items.length};break;
   case'append':{if(!generic)fail('UnsupportedCapability',at(p),'append requires generic contract');const source=sub(e.source,'source');if(e.list_type.kind!=='list'||e.list_type.max_items>100)fail('TypeMismatch',at(p),'append needs source-derived bounded list type');requireType(source,e.list_type,p);requireType(sub(e.item,'item'),e.list_type.element,p);result=e.list_type;}break;
   case'none':result={kind:'optional',element:e.element_type};break;
   case'some':result={kind:'optional',element:sub(e.value,'value')};break;
   case'present':case'absent':{const t=sub(e.value,'value');if(t.kind!=='optional')fail('TypeMismatch',at(p),'explicit optional source required');result=bool;}break;
   case'require_some':{const t=sub(e.value,'value');if(t.kind!=='optional')fail('TypeMismatch',at(p),'checked optional unwrap required');result=t.element;}break;
   case'tag':sub(e.value,'value');result=text;break;
   case'all_unique_exact':sub(e.value,'value');result=bool;break;
   case'require_variant':sub(e.value,'value');result={kind:'variant',enum_name:e.enum_name,variant:e.variant};break;
   case'length':sub(e.value,'value');result=uint;break;
   case'let':{requireType(sub(e.value,'value'),e.binding.type,p);result=sub(e.body,'body',bind(env,e.binding,p));}break;
   case'if':requireType(sub(e.condition,'condition'),bool,p);result=join(sub(e.then,'then'),sub(e.else,'else'),p);break;
   case'concat':{if(!generic||e.result_type.kind!=='string')fail('TypeMismatch',at(p),'V4 concat needs checked bounded String result');const left=sub(e.left,'left'),right=sub(e.right,'right');if(!['string','literal','refinement'].includes(left.kind)||!['string','literal','refinement'].includes(right.kind))fail('TypeMismatch',at(p),'concat operands must be bounded text');result=e.result_type;}break;
   case'binary':sub(e.left,'left');sub(e.right,'right');result=['add','subtract','multiply','divide'].includes(e.operator)?uint:bool;break;
   case'unary':requireType(sub(e.value,'value'),bool,p);result=bool;break;
   case'call':{
    const f=functions.get(e.declaration);if(!f)fail('UnknownReference',at(p),'declared pure call required');if(e.arguments.length!==f.parameters.length)fail('MissingMapping',at(p),'exact call arity required');
    for(let i=0;i<e.arguments.length;i++)requireType(sub(e.arguments[i]!,'arguments['+i+']'),f.parameters[i]!.type,p);
    const list=edges.get(owner)??new Set<string>();list.add(f.name);edges.set(owner,list);calls.push({path:p,owner,declaration:f.name,kind:f.kind,arguments:f.parameters,result:f.result,rounding:f.rounding,on_evaluation_error:f.on_evaluation_error,evaluation_order:'source-order-arguments;original-hygienic-lets-retained'});result=f.result;
   }break;
   case'map':case'filter':case'fold':case'indexed_fold':case'sort':{
    const source=sub(e.source,'source');if(source.kind!=='list')fail('TypeMismatch',at(p),'bounded list source required');requireType(source.element,e.item.type,p);let en=bind(env,e.item,p);
    if(e.op==='map')result={kind:'list',element:sub(e.body,'body',en),min_items:0,max_items:source.max_items};
    else if(e.op==='filter'){requireType(sub(e.predicate,'predicate',en),bool,p);result={...source,min_items:0};}
    else if(e.op==='sort'){for(let i=0;i<e.keys.length;i++)sub(e.keys[i]!.value,'keys['+i+'].value',en);result=source;}
    else{requireType(sub(e.initial,'initial'),e.state.type,p);en=bind(en,e.state,p);if(e.op==='indexed_fold')en=bind(en,e.index,p);requireType(sub(e.body,'body',en),e.state.type,p);result=e.state.type;}
   }break;
   case'repeat':case'while_bounded':case'until_bounded':{
    if(e.max_iterations>c.limits.max_iterations)fail('ResourceLimit',at(p),'loop declaration exceeds configured iteration bound');requireType(sub(e.initial,'initial'),e.state.type,p);let en=bind(env,e.state,p);
    if(e.op==='repeat'){requireType(sub(e.count,'count'),uint,p);en=bind(en,e.index,p);}else requireType(sub(e.guard,'guard',en),bool,p);
    requireType(sub(e.body,'body',en),e.state.type,p);result=e.state.type;
   }break;
   case'range':for(const key of ['start','end','step']as const)requireType(sub(e[key],key),uint,p);if(e.max_iterations>c.limits.max_iterations||e.max_iterations>c.limits.max_items)fail('ResourceLimit',at(p),'range bound exceeds original configured limits');result={kind:'list',element:uint,min_items:0,max_items:e.max_iterations};break;
   case'policy':{
    const action=(a:typeof e.otherwise,key:string,branch:string)=>{const f=functions.get(a.calculation);if(!f||f.kind!=='Calculation')fail('TypeMismatch',at(p),'Policy selects a declared Calculation');const type=sub(a.expression,key+'.expression');policy_actions.push({path:p+'.'+key,policy:e.declaration,branch,calculation:a.calculation,invocation_path:selectedCall(a.expression,p+'.'+key+'.expression',a.calculation),invocation_entered:'must-be-observed-at-that-callsite;not-inferred-from-selection'});return type;};
    result=action(e.otherwise,'otherwise','otherwise');for(let i=0;i<e.cases.length;i++){const cs=e.cases[i]!;requireType(sub(cs.condition,'cases['+i+'].condition'),bool,p);result=join(result,action(cs.action,'cases['+i+'].action','case:'+i),p);}
   }break;
   case'match':{
    const value=sub(e.value,'value');requireType(value,e.binding.type,p);const en=bind(env,e.binding,p);result=sub(e.otherwise,'otherwise',en);for(let i=0;i<e.cases.length;i++){requireType(sub(e.cases[i]!.when,'cases['+i+'].when',en),bool,p);result=join(result,sub(e.cases[i]!.then,'cases['+i+'].then',en),p);}
   }break;
   case'match_variant':{
    const value=sub(e.value,'value');if(value.kind!=='enum'&&value.kind!=='variant')fail('TypeMismatch',at(p),'declared enum match subject required');const name='enum_name'in value?value.enum_name:value.name,enumDef=enums.get(name)!;let out:ValueTypeV1|undefined=e.otherwise?sub(e.otherwise,'otherwise'):undefined;
    for(let i=0;i<e.cases.length;i++){const cs=e.cases[i]!,v=enumDef.variants.find(v=>v.name===cs.variant)!;let en=env;if(cs.binding){const fs=Object.values(v.fields),type=fs.length===1?fs[0]!:{kind:'variant' as const,enum_name:name,variant:cs.variant};en=bind(en,{name:cs.binding,type},p);}const r=sub(cs.then,'cases['+i+'].then',en);out=out?join(out,r,p):r;}result=out??fail('NonExhaustive',at(p),'enum match needs a result');
   }break;
   case'state_machine':{
    const state=sub(e.state,'state'),event=sub(e.event,'event');requireType(state,e.state_binding.type,p);requireType(event,e.event_binding.type,p);const en=bind(bind(env,e.state_binding,p,true),e.event_binding,p,true);requireType(sub(e.initial,'initial'),state,p);for(let i=0;i<e.terminal.length;i++)requireType(sub(e.terminal[i]!,'terminal['+i+']'),state,p);
    for(let i=0;i<e.transitions.length;i++){const t=e.transitions[i]!;requireType(sub(t.guard,'transitions['+i+'].guard',en),bool,p);requireType(sub(t.next,'transitions['+i+'].next',en),state,p);for(let j=0;j<t.intents.length;j++)requireType(sub(t.intents[j]!,'transitions['+i+'].intents['+j+']',en),e.intent_type,p);}result={kind:'outcome',state,intent:e.intent_type,max_intents:e.max_intents};
   }break;
  }
  expressions[index]={path:p,type:result,owner,op:e.op};return result;
 };
 for(const r of c.values.records)typeHeight({kind:'record',name:r.name},'$.values.records');for(const e of c.values.enums)typeHeight({kind:'enum',name:e.name},'$.values.enums');
 for(let i=0;i<c.functions.length;i++){const f=c.functions[i]!,env=new Map(f.parameters.map(b=>[b.name,b.type]));requireType(infer(f.body,'$.functions['+i+'].body',env,f.name),f.result,'$.functions['+i+'].result');}
 for(let i=0;i<c.values.records.length;i++){const r=c.values.records[i]!,env=new Map(Object.entries(r.fields));for(let j=0;j<r.invariants.length;j++)requireType(infer(r.invariants[j]!,'$.values.records['+i+'].invariants['+j+']',env,'@invariant:'+r.name),bool,'$.values.records['+i+']');}
 requireType(infer(c.expression,'$.expression',new Map(c.inputs.map(b=>[b.name,b.type])),'@root:'+c.source_node),c.result,'$.result');
 const graph=[...edges].map(([declaration,callees])=>({declaration,calls:[...callees]}));
 const depths=new Map<string,number>();
 const callDepth=(name:string,path:ReadonlySet<string>):number=>{if(path.has(name))fail('InvalidContract',at(name),'recursive pure call graph');const prior=depths.get(name);if(prior!==undefined)return prior;const next=new Set(path);next.add(name);let depth=1;for(const target of edges.get(name)??[])depth=Math.max(depth,1+callDepth(target,next));if(depth>c.limits.max_call_depth)fail('ResourceLimit',at(name),'pure call graph exceeds configured active call depth');depths.set(name,depth);return depth;};
 for(const f of c.functions)callDepth(f.name,new Set());
 const subject={source_node:c.source_node,expressions,calls,policy_actions,graph};
 return coreFreeze({kind:generic?'generic-computation-environment/v1-candidate' as const:'commerce-computation-environment/v2-candidate' as const,...subject,counts:{expressions:expressions.length,calls:calls.length,records:records.size,enums:enums.size,refinements:refinements.size,functions:functions.size},subject_sha256:dataDigest(subject),qualification:'source-checked-type-and-call-layout-only;no-evaluation-or-native-generation',authority_effect:'none'});
}

export function deriveCommerceComputationEnvironment(contract:ComputationContractV1):CommerceComputationEnvironment {
 requireLegacyExpressionData(contract);if(contract.schema_version!=='domainspec.iteration-expression/v2-candidate'||contract.semantics_revision!=='ordered-metered-commerce-v2-candidate')fail('UnsupportedCapability',at('contract'),'original commerce discriminator required');
 return requireLegacyExpressionData<CommerceComputationEnvironment>(deriveEnvironment(contract));
}
export function deriveGenericComputationEnvironment(contract:GenericComputationContractV1):GenericComputationEnvironment {
 if(contract.schema_version!=='craft.generic-computation/v1-candidate'||contract.semantics_revision!=='ordered-metered-generic-v1-candidate'||contract.values.schema_version!=='craft.generic-values/v1-candidate'||contract.invariant_policy!=='reject-inexact/v1'||contract.record_layout!=='canonical-fields/v1'||contract.equality_policy!=='typed-structural-metered/v1'||contract.append_policy!=='list-item-checkpoint-capacity/v1')fail('InvalidContract',at('contract'),'exact generic computation policies required');
 return deriveEnvironment(contract) as GenericComputationEnvironment;
}
