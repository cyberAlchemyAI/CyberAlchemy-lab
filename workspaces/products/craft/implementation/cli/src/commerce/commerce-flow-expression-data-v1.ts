/** Fixed source-expression data evaluation for native transaction instructions.
 * Dispatch is constructed internally by the original source program owner;
 * this data helper issues no invocation, row, commit or native-context authority.
 * Open Questions: implementation/craft-alchlang-commerce-2026-10-16/evidence/EC17/CONTEXT.md. */
import {types as host} from 'node:util';
import type {FlowExprV1} from './commerce-data-v1.js';
export class CommerceFlowDataErrorV1 extends Error {
 readonly code:string;readonly source_path:string;
 constructor(code:string,sourcePath:string){super(code);this.name='CommerceFlowDataErrorV1';this.code=code;this.source_path=sourcePath;}
}
export interface CommerceFlowDataDispatchV1 {
 charge(path:string):void;
 pure(path:string,args:readonly unknown[]):unknown;
 native(path:string,args:readonly unknown[]):unknown;
 context(path:string):unknown;
 isNullaryEnum(name:string):boolean;
}
const MAX=18446744073709551615n;
const fail=(code:string,p:string):never=>{throw new CommerceFlowDataErrorV1(code,p);};
function dataField(v:any,name:string,p:string):any {if(!v||typeof v!=='object'||host.isProxy(v))return fail('InputType',p);const d=Object.getOwnPropertyDescriptor(v,name);if(!d||!d.enumerable||!Object.hasOwn(d,'value'))return fail('InputType',p);return d.value;}
function equal(a:any,b:any,p:string,charge:()=>void,depth=0):boolean {charge();if(depth>32)fail('ResourceLimit',p);if(a===b)return true;if(typeof a!==typeof b||!a||!b||typeof a!=='object')return false;if(host.isProxy(a)||host.isProxy(b))fail('InputType',p);if(Array.isArray(a)!==Array.isArray(b))return false;const keys=Object.keys(a),other=Object.keys(b);if(keys.length!==other.length)return false;return keys.every(k=>Object.hasOwn(b,k)&&equal(dataField(a,k,p),dataField(b,k,p),p,charge,depth+1));}
/** Evaluates only source operators admitted by this finite native cell. Unknown
 * operators fail closed at program binding, never acquire a fallback callback. */
export function evaluateCommerceFlowDataV1(e:FlowExprV1,p:string,env:Readonly<Record<string,any>>,dispatch:CommerceFlowDataDispatchV1,depth=0):any {
 dispatch.charge(p);if(depth>64)fail('ResourceLimit',p);
 const sub=(x:FlowExprV1,key:string,scope=env)=>evaluateCommerceFlowDataV1(x,p+'.'+key,scope,dispatch,depth+1);
 switch(e.op){
  case'literal':return e.type.kind==='scalar'&&e.type.name==='UInt64'?BigInt(e.value as string):e.value;
  case'var':return dataField(env,e.name,p);
  case'field':return dataField(sub(e.value,'value'),e.field,p);
  case'none':return Object.freeze({kind:'none'});
  case'some':return Object.freeze({kind:'some',value:sub(e.value,'value')});
  case'require_some':{const v=sub(e.value,'value');if(dataField(v,'kind',p)!=='some')fail('OptionalAbsent',p);return dataField(v,'value',p);}
  case'let':{const value=sub(e.value,'value'),scope=Object.assign(Object.create(null),env,{[e.binding.name]:value});return sub(e.body,'body',scope);}
  case'record':{const value=Object.create(null);for(const [name,child]of Object.entries(e.fields))value[name]=sub(child,'fields.'+name);return value;}
  case'enum_value':{if(dispatch.isNullaryEnum(e.type_name))return e.variant;const value:any={kind:e.variant};for(const [name,child]of Object.entries(e.fields))value[name]=sub(child,'fields.'+name);return value;}
  case'call':return dispatch.pure(p,e.arguments.map((a,i)=>sub(a,'arguments['+i+']')));
  case'native_observation':return dispatch.native(p,e.arguments.map((a,i)=>sub(a.value,'arguments['+i+'].value')));
  case'private_context':return dispatch.context(p);
  case'binary':{
   const left=sub(e.left,'left');if(e.operator==='and'&&left===false)return false;if(e.operator==='or'&&left===true)return true;const right=sub(e.right,'right');
   if(e.operator==='eq')return equal(left,right,p,()=>dispatch.charge(p));
   if(e.operator==='and'||e.operator==='or'){if(typeof left!=='boolean'||typeof right!=='boolean')return fail('InputType',p);return right;}
   if(typeof left!=='bigint'||typeof right!=='bigint')return fail('InputType',p);
   if(e.operator==='lt')return left<right;if(e.operator==='lte')return left<=right;if(e.operator==='gt')return left>right;if(e.operator==='gte')return left>=right;
   const value=e.operator==='add'?left+right:e.operator==='subtract'?left-right:e.operator==='multiply'?left*right:fail('UnsupportedCapability',p);if(value<0n||value>MAX)return fail('ArithmeticError',p);return value;
  }
  default:return fail('UnsupportedCapability',p);
 }
}
export const COMMERCE_TRANSACTION_DATA_OPERATORS_V1=Object.freeze(['literal','var','field','none','some','require_some','let','record','enum_value','call','native_observation','private_context','binary']);
