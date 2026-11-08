/** Bounded interpretation of expressions in one checked original Workflow.
 * This is inert data evaluation. It cannot authorize an Entry, call a service,
 * create a journal row, or supply a private context. Exact source callsites
 * must be resolved by their real producer owners before any result is used.
 * Open Questions: docs/COMMERCE-CONTRACTS.md#open-questions. */
import {types as host} from 'node:util';
import {assertCommerceWorkflowCoordinationBindingV1,type CommerceWorkflowCoordinationBindingV1} from './commerce-workflow-coordination-binding-v1.js';
import {assertCommerceComputationDomainOwner,type CommerceComputationDomainOwner,type CommerceComputationDomainHandle} from './commerce-computation-domain.js';
import {assertCoreCommerceSemanticOwner,type CoreCommerceSemanticOwner,type CoreCommerceSemanticCapture} from './commerce-core-semantic-owner.js';
import type {FlowExprV1,RoleExpressionV1,ValueTypeV1} from './commerce-data-v1.js';

export class CommerceWorkflowExpressionErrorV1 extends Error {
 readonly code:string;readonly source_path:string;
 constructor(code:string,source_path:string){super(code+' at '+source_path);this.name='CommerceWorkflowExpressionErrorV1';this.code=code;this.source_path=source_path;}
}
const bad=(code:string,path:string):never=>{throw new CommerceWorkflowExpressionErrorV1(code,path);};
const MAX_U64=18446744073709551615n;
interface DataRecord {readonly [name:string]:Data}
type Data=string|boolean|bigint|readonly Data[]|DataRecord;
type Scope=Readonly<Record<string,Data>>;
const plain=(v:unknown):v is Record<string,unknown>=>!!v&&typeof v==='object'&&!Array.isArray(v)&&!host.isProxy(v)&&
 (Object.getPrototypeOf(v)===Object.prototype||Object.getPrototypeOf(v)===null);
const field=(v:unknown,name:string,path:string):unknown=>{
 if(!plain(v))bad('InputType',path);
 const descriptor=Object.getOwnPropertyDescriptor(v,name);
 if(!descriptor?.enumerable||!Object.hasOwn(descriptor,'value'))bad('InputType',path+'.'+name);
 return descriptor!.value;
};
const utf8=(text:string)=>Buffer.byteLength(text,'utf8');
const unicode=(text:string)=>{for(let i=0;i<text.length;i++){const n=text.charCodeAt(i);if(n>=0xd800&&n<=0xdbff){const next=text.charCodeAt(++i);if(!(next>=0xdc00&&next<=0xdfff))return false;}else if(n>=0xdc00&&n<=0xdfff)return false;}return true;};
const copied=(value:unknown,path:string,maxItems:number):Data=>{
 let nodes=0;
 const visit=(v:unknown,p:string,depth:number):Data=>{
  if(++nodes>65536||depth>64)bad('ResourceLimit',p);
  if(typeof v==='boolean'||typeof v==='bigint')return v;
  if(typeof v==='string'){if(!unicode(v))bad('InvalidUnicode',p);return v;}
  if(!v||typeof v!=='object'||host.isProxy(v))bad('InputType',p);
  if(Array.isArray(v)){
   if(Object.getPrototypeOf(v)!==Array.prototype||v.length>maxItems||Reflect.ownKeys(v).length!==v.length+1)bad('InputBound',p);
   const out:Data[]=[];
   for(let i=0;i<v.length;i++){
    const descriptor=Object.getOwnPropertyDescriptor(v,String(i));
    if(!descriptor?.enumerable||!Object.hasOwn(descriptor,'value'))bad('InputType',p+'['+i+']');
    out.push(visit(descriptor!.value,p+'['+i+']',depth+1));
   }
   return Object.freeze(out);
  }
  if(!plain(v))bad('InputType',p);
  const object=v as Record<string,unknown>;
  if(Reflect.ownKeys(object).length>maxItems)bad('InputBound',p);
  const out:Record<string,Data>=Object.create(null);
  for(const name of Reflect.ownKeys(object)){
   if(typeof name!=='string')bad('InputType',p);
   if(!unicode(name as string))bad('InputType',p);
   out[name as string]=visit(field(object,name as string,p),p+'.'+String(name),depth+1);
  }
  return Object.freeze(out);
 };
 return visit(value,path,0);
};
const size=(value:Data):number=>{
 let bytes=0;
 const walk=(v:Data,depth:number):void=>{
  if(depth>64)bad('ResourceLimit','$.value');
  if(typeof v==='boolean'){bytes+=v?4:5;return;}
  if(typeof v==='bigint'){bytes+=String(v).length+2;return;}
  if(typeof v==='string'){bytes+=utf8(JSON.stringify(v));return;}
  if(Array.isArray(v)){bytes+=2+Math.max(0,v.length-1);for(const item of v)walk(item,depth+1);return;}
  bytes+=2+Math.max(0,Object.keys(v).length-1);
  for(const [name,item] of Object.entries(v)){bytes+=utf8(JSON.stringify(name))+1;walk(item,depth+1);}
 };
 walk(value,0);return bytes;
};
const scope=(env:Scope,additional:Record<string,Data>):Scope=>Object.freeze(Object.assign(Object.create(null),env,additional));
const list=(v:Data,p:string):readonly Data[]=>Array.isArray(v)?v:bad('InputType',p);
const bool=(v:Data,p:string):boolean=>typeof v==='boolean'?v:bad('InputType',p);
const uint=(v:Data,p:string):bigint=>typeof v==='bigint'&&v>=0n&&v<=MAX_U64?v:bad('InputType',p);
const optional=(v:Data,p:string):{kind:'none'|'some';value?:Data}=>{
 const kind=field(v,'kind',p);
 if(kind==='none'&&Object.keys(v as object).length===1)return {kind};
 if(kind==='some'&&Object.keys(v as object).length===2)return {kind,value:field(v,'value',p) as Data};
 return bad('InputType',p);
};
const tag=(v:Data,p:string):string=>{
 if(typeof v==='string')return v;
 if(!plain(v))bad('InputType',p);
 const object=v as DataRecord;
 const name=Object.hasOwn(object,'kind')?field(object,'kind',p):undefined;
 if(typeof name==='string')return name;
 const fallback=Object.hasOwn(object,'tag')?field(object,'tag',p):undefined;
 return typeof fallback==='string'?fallback:bad('InputType',p);
};
const lexical=(a:string,b:string):number=>{
 const left=[...a],right=[...b];
 for(let i=0;i<Math.min(left.length,right.length);i++){
  const x=left[i]!.codePointAt(0)!,y=right[i]!.codePointAt(0)!;
  if(x!==y)return x<y?-1:1;
 }
 return Math.sign(left.length-right.length);
};
const natural=(a:string,b:string):number=>{
 const left=a.match(/[0-9]+|[^0-9]+/gu)??[],right=b.match(/[0-9]+|[^0-9]+/gu)??[];
 for(let i=0;i<Math.min(left.length,right.length);i++){
  const x=left[i]!,y=right[i]!;if(x===y)continue;
  if(/^[0-9]+$/u.test(x)&&/^[0-9]+$/u.test(y)){
   const xx=x.replace(/^0+/u,'')||'0',yy=y.replace(/^0+/u,'')||'0';
   const order=Math.sign(xx.length-yy.length)||lexical(xx,yy)||Math.sign(x.length-y.length);
   if(order)return order;
  }else return lexical(x,y);
 }
 return Math.sign(left.length-right.length);
};

export interface CommerceWorkflowExpressionHandleV1 {readonly kind:'original-workflow-expression/v1-candidate'}
export interface CommerceWorkflowExpressionCallsiteV1 {
 readonly path:string;readonly kind:'pure'|'native';readonly declaration:string|null;
 readonly context:string|null;readonly source_type:string|null;readonly abi:string|null;readonly method:string|null;
 readonly argument_count:number;
}
export interface CommerceWorkflowExpressionProducersV1 {
 /** The caller must connect this exact checked source path to an original pure owner. */
 readonly pure?:(site:CommerceWorkflowExpressionCallsiteV1,args:readonly Data[])=>unknown;
 /** The caller must connect this exact checked source path to an original native owner. */
 readonly native?:(site:CommerceWorkflowExpressionCallsiteV1,args:readonly Data[])=>unknown;
}
export interface CommerceWorkflowExpressionInspectionV1 {
 readonly workflow:string;readonly source_capture_sha256:string;readonly path:string;readonly result:ValueTypeV1;
 readonly callsites:readonly CommerceWorkflowExpressionCallsiteV1[];
 readonly qualification:'checked-workflow-expression-data-only;producer-and-output-codec-required';
 readonly authority_effect:'none';
}
export interface CommerceWorkflowExpressionOwnerV1 {
 paths():readonly string[];
 bind(path:string):CommerceWorkflowExpressionHandleV1;
 inspect(handle:CommerceWorkflowExpressionHandleV1):CommerceWorkflowExpressionInspectionV1;
 evaluate(handle:CommerceWorkflowExpressionHandleV1,env:Readonly<Record<string,unknown>>,
  producers?:CommerceWorkflowExpressionProducersV1):Data;
 assertCurrent():void;dispose():void;
}
const owners=new WeakSet<object>();
export function assertCommerceWorkflowExpressionOwnerV1(owner:CommerceWorkflowExpressionOwnerV1):void {
 if(!owner||typeof owner!=='object'||!owners.has(owner))bad('ForeignOwner','$.owner');
 owner.assertCurrent();
}

/** Paths are relative to the checked WorkflowContractV1, for example
 * `$.steps[0].call.arguments[0].value`. No arbitrary AST is accepted. */
export function createCommerceWorkflowExpressionOwnerV1(
 binding:CommerceWorkflowCoordinationBindingV1,semantics:CoreCommerceSemanticOwner,
 semantic:CoreCommerceSemanticCapture,domain:CommerceComputationDomainOwner,
 baseline:CommerceComputationDomainHandle,
):CommerceWorkflowExpressionOwnerV1 {
 assertCommerceWorkflowCoordinationBindingV1(binding);assertCoreCommerceSemanticOwner(semantics);
 assertCommerceComputationDomainOwner(domain);
 const checked=binding.inspect(),semanticView=semantics.inspect(semantic),source=domain.inspect(baseline),
  workflow=semanticView.workflows.find(row=>row.workflow.module+'.'+row.workflow.name===checked.workflow.name);
 if(!workflow||semanticView.source_capture_sha256!==checked.source_capture_sha256||
  source.source_capture_sha256!==checked.source_capture_sha256||
  workflow.steps.length!==checked.workflow.steps.length||
  workflow.steps.some((step,index)=>step.name!==checked.workflow.steps[index]!.name||step.kind!==checked.workflow.steps[index]!.kind))
  bad('ForeignOwner','$.workflow');
 const limits=source.contract.limits,values=source.contract.values,
  enums=new Map(values.enums.map(row=>[row.name,row])),refinements=new Map(values.refinements.map(row=>[row.name,row]));
 const roles=new Map<string,RoleExpressionV1>(),sites=new Map<string,CommerceWorkflowExpressionCallsiteV1>();
 let nodes=0;
 const scan=(value:unknown,p:string,depth:number):void=>{
  if(++nodes>65536||depth>128)bad('ResourceLimit',p);
  if(!value||typeof value!=='object')return;
  if(Array.isArray(value)){value.forEach((child,i)=>scan(child,p+'['+i+']',depth+1));return;}
  if(!plain(value))bad('InvalidContract',p);
  if(Object.hasOwn(value,'result')&&Object.hasOwn(value,'expression')&&Object.hasOwn(value,'local_records')){
   const role=value as unknown as RoleExpressionV1;
   if(!role.expression||typeof role.expression!=='object'||typeof role.expression.op!=='string'||!Array.isArray(role.local_records))
    bad('InvalidContract',p);
   roles.set(p,role);scan(role.expression,p+'.expression',depth+1);return;
  }
  const e=value as Record<string,unknown>;
  if(e.op==='call'||e.op==='native_observation'){
   if(sites.has(p))bad('InvalidContract',p);
   const native=e.op==='native_observation';
   if(!Array.isArray(e.arguments)||e.arguments.length>limits.max_items)bad('InvalidContract',p);
   const arguments_=e.arguments as readonly unknown[];
   sites.set(p,Object.freeze({path:p,kind:native?'native':'pure',declaration:native?null:String(e.declaration),
    context:native?String(e.context):null,source_type:native?String(e.source_type):null,
    abi:native?String(e.abi):null,method:native?String(e.method):null,
    argument_count:arguments_.length}));
  }
  for(const [name,child] of Object.entries(value))scan(child,p+'.'+name,depth+1);
 };
 scan(workflow!,'$',0);
 if(roles.size===0)bad('InvalidContract','$.workflow');
 const handles=new WeakMap<object,string>();let disposed=false;
 const current=()=>{if(disposed)bad('DisposedOwner','$.owner');
  if(binding.inspect().source_capture_sha256!==checked.source_capture_sha256||
   semantics.inspect(semantic).source_capture_sha256!==checked.source_capture_sha256||
   domain.inspect(baseline).source_capture_sha256!==checked.source_capture_sha256)
   bad('StaleOwner','$.workflow');};
 const owned=(handle:CommerceWorkflowExpressionHandleV1):{path:string;role:RoleExpressionV1}=>{
  current();const path=handle&&typeof handle==='object'?handles.get(handle):undefined;
  const role=path?roles.get(path):undefined;
  if(!path||!role)bad('ForeignOwner','$.expression');return {path:path!,role:role!};
 };
 const calls=(path:string):readonly CommerceWorkflowExpressionCallsiteV1[]=>Object.freeze(
  [...sites.values()].filter(site=>site.path===path+'.expression'||site.path.startsWith(path+'.expression.')).sort((a,b)=>a.path.localeCompare(b.path)));
 const owner:CommerceWorkflowExpressionOwnerV1=Object.freeze({
  paths(){current();return Object.freeze([...roles.keys()].sort());},
  bind(path:string){current();if(typeof path!=='string'||!roles.has(path))bad('UnknownReference',String(path));
   const handle=Object.freeze({kind:'original-workflow-expression/v1-candidate' as const});handles.set(handle,path);return handle;},
  inspect(handle:CommerceWorkflowExpressionHandleV1){const {path,role}=owned(handle);return Object.freeze({workflow:checked.workflow.name,source_capture_sha256:checked.source_capture_sha256,
   path,result:role.result,callsites:calls(path),qualification:'checked-workflow-expression-data-only;producer-and-output-codec-required' as const,
   authority_effect:'none' as const});},
  evaluate(handle:CommerceWorkflowExpressionHandleV1,rawEnv:Readonly<Record<string,unknown>>,
   producers:CommerceWorkflowExpressionProducersV1={}){
   const {path,role}=owned(handle);if(!plain(rawEnv))bad('InputType',path+'.env');
   const env=copied(rawEnv,path+'.env',limits.max_items) as Scope;
   if(size(env)>limits.max_input_bytes)bad('InputBound',path+'.env');
   let fuel=0;const charge=(p:string,n=1)=>{if(!Number.isSafeInteger(n)||n<0||n>limits.fuel-fuel)bad('ResourceLimit',p);fuel+=n;};
   const check=(value:Data,p:string):Data=>{if(size(value)>limits.max_value_bytes)bad('OutputBound',p);return value;};
   const eq=(a:Data,b:Data,p:string,depth=0):boolean=>{
    charge(p);if(depth>64)bad('ResourceLimit',p);if(a===b)return true;
    if(typeof a!==typeof b||!a||!b||typeof a!=='object')return false;
    if(Array.isArray(a)!==Array.isArray(b))return false;
    const ak=Object.keys(a),bk=Object.keys(b);
    if(ak.length!==bk.length)return false;
    return ak.every(name=>Object.hasOwn(b as object,name)&&eq((a as Record<string,Data>)[name]!,
     (b as Record<string,Data>)[name]!,p,depth+1));
   };
   const evalExpr=(e:FlowExprV1,p:string,local:Scope,depth=0):Data=>{
    charge(p);if(depth>64)bad('ResourceLimit',p);
    const sub=(child:FlowExprV1,key:string,en=local)=>evalExpr(child,p+'.'+key,en,depth+1);
    let value:Data;
    switch(e.op){
     case 'literal':value=e.type.kind==='scalar'&&e.type.name==='UInt64'?BigInt(e.value as string):e.value;break;
     case 'validate_refinement':{
      const candidate=sub(e.value,'value'),ref=refinements.get(e.refinement);
      if(!ref||typeof candidate!=='string'||!unicode(candidate)||utf8(candidate)<ref.min_utf8_bytes||
       utf8(candidate)>ref.max_utf8_bytes||[...candidate].length<ref.min_unicode_scalars||
       [...candidate].length>ref.max_unicode_scalars||ref.pattern!==null&&!new RegExp(ref.pattern,'u').test(candidate))
       bad('InputType',p);
      value=candidate;break;
     }
     case 'var':value=field(local,e.name,p) as Data;break;
     case 'field':value=field(sub(e.value,'value'),e.field,p) as Data;break;
     case 'record':case 'record_update':{
      const base=e.op==='record_update'?sub(e.value,'value'):Object.freeze(Object.create(null)) as Data;
      if(!plain(base))bad('InputType',p);
      const out:Record<string,Data>=Object.assign(Object.create(null),base);
      for(const [name,child] of Object.entries(e.fields))out[name]=sub(child,'fields.'+name);
      value=Object.freeze(out);break;
     }
     case 'enum_value':{
      const definition=enums.get(e.type_name),variant=definition?.variants.find(row=>row.name===e.variant);
      if(!variant||Object.keys(e.fields).sort().join('\0')!==Object.keys(variant.fields).sort().join('\0'))bad('InvalidContract',p);
      if(definition!.variants.every(row=>Object.keys(row.fields).length===0))value=e.variant;
      else{const fields:Record<string,Data>=Object.create(null);
       for(const [name,child] of Object.entries(e.fields))fields[name]=sub(child,'fields.'+name);
       value=Object.freeze({kind:e.variant,fields:Object.freeze(fields)});}
      break;
     }
     case 'list':{if(e.items.length>limits.max_items)bad('OutputBound',p);value=Object.freeze(e.items.map((item,i)=>sub(item,'items['+i+']')));break;}
     case 'none':value=Object.freeze({kind:'none'});break;
     case 'some':value=Object.freeze({kind:'some',value:sub(e.value,'value')});break;
     case 'present':case 'absent':value=(optional(sub(e.value,'value'),p).kind==='some')===(e.op==='present');break;
     case 'require_some':{const option=optional(sub(e.value,'value'),p);if(option.kind!=='some')bad('OptionalAbsent',p);value=option.value!;break;}
     case 'tag':value=tag(sub(e.value,'value'),p);break;
     case 'all_unique_exact':{const rows=list(sub(e.value,'value'),p);let unique=true;
      outer:for(let i=0;i<rows.length;i++)for(let j=0;j<i;j++)if(eq(rows[i]!,rows[j]!,p)){unique=false;break outer;}
      value=unique;break;}
     case 'require_variant':{const candidate=sub(e.value,'value');if(tag(candidate,p)!==e.variant)bad('InputType',p);value=candidate;break;}
     case 'length':{const candidate=sub(e.value,'value');if(e.unit==='items')value=BigInt(list(candidate,p).length);
      else{if(typeof candidate!=='string')bad('InputType',p);const text=candidate as string;
       value=BigInt(e.unit==='utf8-bytes'?utf8(text):[...text].length);}break;}
     case 'let':value=sub(e.body,'body',scope(local,{[e.binding.name]:sub(e.value,'value')}));break;
     case 'if':value=bool(sub(e.condition,'condition'),p)?sub(e.then,'then'):sub(e.else,'else');break;
     case 'unary':value=!bool(sub(e.value,'value'),p);break;
     case 'binary':{
      const left=sub(e.left,'left');
      if(e.operator==='and'||e.operator==='or'){
       const first=bool(left,p);value=e.operator==='and'&&!first?false:e.operator==='or'&&first?true:bool(sub(e.right,'right'),p);break;
      }
      const right=sub(e.right,'right');
      if(e.operator==='eq'){value=eq(left,right,p);break;}
      if(['lt','lte','gt','gte'].includes(e.operator)){
       if(typeof left!==typeof right||!(typeof left==='bigint'||typeof left==='string'))bad('InputType',p);
       const order=typeof left==='string'?lexical(left,right as string):(left as bigint)<(right as bigint)?-1:(left as bigint)>(right as bigint)?1:0;
       value=e.operator==='lt'?order<0:e.operator==='lte'?order<=0:e.operator==='gt'?order>0:order>=0;break;
      }
      const a=uint(left,p),b=uint(right,p);
      if(e.operator==='divide'&&b===0n)bad('DivideByZero',p);
      if(e.operator==='divide'&&a%b!==0n)bad('InexactDivision',p);
      const number=e.operator==='add'?a+b:e.operator==='subtract'?a-b:e.operator==='multiply'?a*b:a/b;
      if(number<0n)bad('ArithmeticUnderflow',p);if(number>MAX_U64)bad('ArithmeticOverflow',p);
      value=number;break;
     }
     case 'call':case 'native_observation':{
      const site=sites.get(p),native=e.op==='native_observation';
      if(!site||site.kind!==(native?'native':'pure'))bad('ForeignCallsite',p);
      const args=native?e.arguments.map((argument,i)=>sub(argument.value,'arguments['+i+'].value')):
       e.arguments.map((argument,i)=>sub(argument,'arguments['+i+']'));
      if(args.length!==site!.argument_count)bad('InvalidContract',p);
      const producer=native?producers.native:producers.pure;
      if(typeof producer!=='function')bad('ProducerRequired',p);
      value=copied(producer!(site!,Object.freeze(args)),p,limits.max_items);break;
     }
     case 'map':case 'filter':{
      const rows=list(sub(e.source,'source'),p),out:Data[]=[];
      for(let i=0;i<rows.length;i++){charge(p);const localScope=scope(local,{[e.item.name]:rows[i]!});
       const item=e.op==='map'?sub(e.body,'body',localScope):sub(e.predicate,'predicate',localScope);
       if(e.op==='map')out.push(item);else if(bool(item,p))out.push(rows[i]!);
       if(out.length>limits.max_items)bad('OutputBound',p);check(Object.freeze([...out]),p);
      }
      value=Object.freeze(out);break;
     }
     case 'fold':case 'indexed_fold':{
      const rows=list(sub(e.source,'source'),p);let state=sub(e.initial,'initial');
      for(let i=0;i<rows.length;i++){charge(p);const bindings:Record<string,Data>={[e.state.name]:state,[e.item.name]:rows[i]!};
       if(e.op==='indexed_fold')bindings[e.index.name]=BigInt(i);
       state=sub(e.body,'body',scope(local,bindings));check(state,p);
      }
      value=state;break;
     }
     case 'repeat':{
      const count=uint(sub(e.count,'count'),p);if(count>BigInt(Math.min(e.max_iterations,limits.max_iterations)))bad('IterationBound',p);
      let state=sub(e.initial,'initial');
      for(let i=0;i<Number(count);i++){charge(p);state=sub(e.body,'body',scope(local,{[e.state.name]:state,[e.index.name]:BigInt(i)}));check(state,p);}
      value=state;break;
     }
     case 'while_bounded':case 'until_bounded':{
      let state=sub(e.initial,'initial');
      for(let i=0;;i++){
       const en=scope(local,{[e.state.name]:state}),guard=bool(sub(e.guard,'guard',en),p);
       if(e.op==='while_bounded'?!guard:guard)break;
       if(i>=Math.min(e.max_iterations,limits.max_iterations))bad('IterationLimit',p);
       charge(p);state=sub(e.body,'body',en);check(state,p);
      }
      value=state;break;
     }
     case 'range':{
      const start=uint(sub(e.start,'start'),p),end=uint(sub(e.end,'end'),p),step=uint(sub(e.step,'step'),p);
      if(step===0n)bad('IterationBound',p);
      const count=start>=end?0n:(end-start+step-1n)/step;
      if(count>BigInt(Math.min(e.max_iterations,limits.max_iterations,limits.max_items)))bad('IterationBound',p);
      const rows:Data[]=[];for(let i=0;i<Number(count);i++){charge(p);rows.push(start+BigInt(i)*step);}
      value=Object.freeze(rows);break;
     }
     case 'sort':{
      const rows=list(sub(e.source,'source'),p);
      const decorated=rows.map((item,i)=>{charge(p);const en=scope(local,{[e.item.name]:item});
       return {item,index:i,keys:e.keys.map((key,j)=>sub(key.value,'keys['+j+'].value',en))};});
      const compare=(a:typeof decorated[number],b:typeof decorated[number]):number=>{
       for(let j=0;j<e.keys.length;j++){charge(p);const key=e.keys[j]!,left=a.keys[j]!,right=b.keys[j]!;
        let order:number;
        if(key.mode==='numeric'){order=uint(left,p)<uint(right,p)?-1:left===right?0:1;}
        else{if(typeof left!=='string'||typeof right!=='string')bad('InputType',p);
         order=key.mode==='natural'?natural(left as string,right as string):lexical(left as string,right as string);}
        if(order)return key.direction==='desc'?-order:order;
       }
       return 0;
      };
      const sorted:typeof decorated=[];
      for(const item of decorated){let at=sorted.length;while(at>0&&compare(item,sorted[at-1]!)<0)at--;sorted.splice(at,0,item);}
      value=Object.freeze(sorted.map(row=>row.item));break;
     }
     case 'policy':{
      let action=e.otherwise,key='otherwise';
      for(let i=0;i<e.cases.length;i++)if(bool(sub(e.cases[i]!.condition,'cases['+i+'].condition'),p)){
       action=e.cases[i]!.action;key='cases['+i+'].action';break;
      }
      // A checked Policy selects a concrete Calculation invocation. Its
      // declaration metadata must never be divorced from the selected call.
      if(action.expression.op!=='call'||action.expression.declaration!==action.calculation)
       bad('InvalidContract',p+'.'+key+'.expression');
      value=sub(action.expression,key+'.expression');break;
     }
     case 'match':{
      const subject=sub(e.value,'value'),en=scope(local,{[e.binding.name]:subject});let selected=e.otherwise,key='otherwise';
      for(let i=0;i<e.cases.length;i++)if(bool(sub(e.cases[i]!.when,'cases['+i+'].when',en),p)){
       selected=e.cases[i]!.then;key='cases['+i+'].then';break;
      }
      value=sub(selected,key,en);break;
     }
     case 'match_variant':{
      const subject=sub(e.value,'value'),name=tag(subject,p),index=e.cases.findIndex(row=>row.variant===name);
      if(index<0){if(!e.otherwise)bad('NonExhaustiveMatch',p);value=sub(e.otherwise!,'otherwise');}
      else{const selected=e.cases[index]!,fields=typeof subject==='string'?null:field(subject,'fields',p);
       const names=plain(fields)?Object.keys(fields):[];
       const bound=selected.binding?scope(local,{[selected.binding]:names.length===1?field(fields,names[0]!,p) as Data:subject}):local;
       value=sub(selected.then,'cases['+index+'].then',bound);
      }break;
     }
     case 'state_machine':{
      const state=sub(e.state,'state'),event=sub(e.event,'event'),
       en=scope(local,{[e.state_binding.name]:state,[e.event_binding.name]:event});
      let outcome:Data=Object.freeze({tag:e.otherwise==='stay'?'stayed':'rejected',state,intents:Object.freeze([]),
       machine:e.declaration,branch:'otherwise',reason:e.otherwise_reason??(e.otherwise==='stay'?'no-match-stay':'no-match-reject')});
      for(let i=0;i<e.transitions.length;i++){
       const transition=e.transitions[i]!;
       if(!bool(sub(transition.guard,'transitions['+i+'].guard',en),p))continue;
       const next=sub(transition.next,'transitions['+i+'].next',en),intents:Data[]=[];
       for(let j=0;j<transition.intents.length;j++){intents.push(sub(transition.intents[j]!,'transitions['+i+'].intents['+j+']',en));
        if(intents.length>e.max_intents||intents.length>limits.max_items)bad('OutputBound',p);}
       outcome=Object.freeze({tag:'transition',state:next,intents:Object.freeze(intents),
        machine:e.declaration,branch:'transition:'+i,reason:'matched'});break;
      }
      value=outcome;break;
     }
     case 'private_context':bad('PrivateContextRequired',p);
     default:bad('UnsupportedCapability',p);
    }
    return check(value!,p);
   };
   const value=evalExpr(role.expression,path+'.expression',env);
   if(size(value)>limits.max_output_bytes)bad('OutputBound',path);
   current();return copied(value,path,limits.max_items);
  },
  assertCurrent:current,dispose(){current();disposed=true;},
 });
 owners.add(owner);return owner;
}
