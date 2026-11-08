import type {TypedType,ValueExpression} from '../typed-operation/contracts.js';
import type {FieldReferenceModel} from '../input/field-reference-model.js';
import {canonicalJson} from '../input/source-manifest.js';
import {qualifyPublicType,type MappingValueType,type MappingInterfaceDeclaration} from '../typed-backend/mapping-public.js';
import {createStructuredValueRenderer} from './configured-value-types.js';
import {createStructuredValueExpressionRenderer,type BoundValue} from './configured-value-expressions.js';

type NativeValue=Readonly<{native:string;input:string;protocol:string}>;
type PublicBoundValue=Readonly<{type:MappingValueType;code:string}>;
const q=JSON.stringify;
/** Reuse domain lowering; extend public paths without synthetic domain declarations. */
export function createPublicMappingValues(model:FieldReferenceModel|null,interfaces:readonly MappingInterfaceDeclaration[],aliases:ReadonlyMap<string,string>,fail:(message:string)=>never,domain=createStructuredValueRenderer(model,fail,true)){
 const rows:string[]=[],cache=new Map<string,NativeValue>();let next=0;
 const fresh=()=> 'pmItem'+next++;
 const domainExpression=createStructuredValueExpressionRenderer(domain,model,fresh,fail);
 const hasPublic=(t:MappingValueType):boolean=>t.kind==='contract'||(t.kind==='sum'?t.variants.some(v=>v.payload!==null&&hasPublic(v.payload)):t.kind==='scalar'||t.kind==='named'||t.kind==='reference'?false:hasPublic(t.element));
 const ensure=(t:MappingValueType):NativeValue=>{
  if(!hasPublic(t))return domain.ensure(t as TypedType);
  const key=canonicalJson(t),prior=cache.get(key);if(prior)return prior;
  if(t.kind==='contract'){
   const alias=aliases.get(t.interface_selector)??fail('missing Interface import:'+t.interface_selector);
   const native=alias+'.PublicContracts['+q(t.contract_id)+']',value={native,input:native,protocol:alias+'.publicContracts['+q(t.contract_id)+']'};cache.set(key,value);return value;
  }
  const name='PM'+next++,value={native:name,input:name+'Input',protocol:name+'Value'};
  if(t.kind==='sum'){
   domain.use('sum');
   const variants=[...t.variants].sort((a,b)=>a.name<b.name?-1:1),children=variants.map(v=>v.payload?ensure(v.payload):null);
   const form=(input:boolean)=>variants.map((v,i)=>'Readonly<{variant:'+q(v.name)+(children[i]?';payload:'+(input?children[i]!.input:children[i]!.native):'')+'}>').join('|');
   rows.push('type '+name+'='+form(false)+';\ntype '+name+'Input='+form(true)+';\nconst '+value.protocol+':RuleProtocol<'+name+'>=ruleSum(Object.freeze({'+variants.map((v,i)=>'['+q(v.name)+']:'+(children[i]?.protocol??'null')).join(',')+'}));\n');
  }else if(t.kind==='optional'||t.kind==='list'||t.kind==='set'){
   domain.use(t.kind==='optional'?'optional':'sequence');
   const child=ensure(t.element),form=(x:string)=>t.kind==='optional'?'('+x+')|null':'ReadonlyArray<'+x+'>';
   rows.push('type '+name+'='+form(child.native)+';\ntype '+name+'Input='+form(child.input)+';\nconst '+value.protocol+':RuleProtocol<'+name+'>='+(t.kind==='optional'?'ruleOptional('+child.protocol+')':'ruleSequence('+child.protocol+','+(t.kind==='set')+')')+';\n');
  }else return fail('invalid public value type');
  cache.set(key,value);return value;
 };
 const properties=(t:MappingValueType)=>{
  if(t.kind==='contract'){
   const api=interfaces.find(i=>i.selector===t.interface_selector)??fail('missing Interface declaration');
   const contract=api.contract.contracts.find(c=>c.contract_id===t.contract_id)??fail('missing public declaration');
   return contract.fields.map(f=>({name:f.name,ontology_property:f.ontology_field,type:qualifyPublicType(f.type,t.interface_selector)}));
  }
  if(t.kind==='named'){const d=domain.get(t.selector);if(d.kind==='Enum')return fail('Enum has no fields');return d.contract.properties;}
  return fail('public path requires a declared value; no unwrap');
 };
 const expression=(node:ValueExpression,scope:ReadonlyMap<string,PublicBoundValue>):PublicBoundValue=>{
  if(node.op==='literal'||node.op==='variant')return domainExpression(node,new Map());
  if(node.op==='to_set'){
   domain.use('to-set');
   const source=expression(node.value,scope);if(source.type.kind!=='list')return fail('to_set requires list');
   return {type:{kind:'set',element:source.type.element},code:'ruleToSet('+source.code+','+ensure(source.type.element).protocol+')'};
  }
  let current=scope.get(node.root)??fail('undeclared input');
  if(!hasPublic(current.type))return domainExpression(node,new Map([[node.root,current as BoundValue]]));
  for(const property of node.properties){
   const kind=current.type.kind,collection=kind==='list'||kind==='set',owner=(current.type.kind==='list'||current.type.kind==='set')?current.type.element:current.type;
   const field=properties(owner).find(f=>f.ontology_property===property)??fail('unknown ontology field');
   if(collection){const item=fresh(),code=current.code+'.map('+item+'=>'+item+'['+q(field.name)+'])';if(kind==='set')domain.use('to-set');current={type:{kind:kind as 'list'|'set',element:field.type},code:kind==='set'?'ruleToSet('+code+','+ensure(field.type).protocol+')':'Object.freeze('+code+')'};}
   else current={type:field.type,code:current.code+'['+q(field.name)+']'};
  }return current;
 };
 return {ensure,expression,source:(body='')=>domain.source(rows.join('')+body)};
}
