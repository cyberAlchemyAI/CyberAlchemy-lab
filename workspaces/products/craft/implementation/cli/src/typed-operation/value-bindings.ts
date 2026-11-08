import type {TypedType,TypedRecordContract,TypedSumContract,ValueExpression} from './contracts.js';
export type TypedValueDeclaration=
 | Readonly<{selector:string;kind:'Entity'|'Value Object';contract:TypedRecordContract}>
 | Readonly<{selector:string;kind:'Enum';contract:TypedSumContract}>;
/** Static value typing shared by argument and field bindings; creates no domain nodes. */
export function createTypedValueChecker(declarations:readonly TypedValueDeclaration[],fail:(message:string)=>never){
 const map=new Map(declarations.map(d=>[d.selector,d]));
 if(map.size!==declarations.length)fail('duplicate declarations');
 const get=(selector:string)=>map.get(selector)??fail('unresolved declaration:'+selector);
 const referenceField=(t:Extract<TypedType,{kind:'reference'}>)=>{
  const d=get(t.selector);if(d.kind!=='Entity')return fail('reference target must be an Entity:'+t.selector);
  if(t.projection.length!==1)return fail('reference requires exactly one identity projection:'+t.selector);
  const field=d.contract.properties.find(f=>f.name===t.projection[0]);
  if(!field||!field.identity)return fail('reference projection must select the Entity identity:'+t.selector+'#'+t.projection[0]);
  return field;
 };
 const checkType=(t:TypedType):void=>{if(t.kind==='named')get(t.selector);else if(t.kind==='reference')checkType(referenceField(t).type);else if(t.kind==='sum')t.variants.forEach(v=>{if(v.payload)checkType(v.payload);});else if(t.kind!=='scalar')checkType(t.element);};
 const infer=(v:ValueExpression,scope:ReadonlyMap<string,TypedType>):TypedType=>{
  if(v.op==='literal')return {kind:'scalar',name:v.type};
  if(v.op==='variant'){
   const matches=declarations.filter(d=>d.kind==='Enum'&&d.contract.variants.some(x=>x.ontology_variant===v.selector&&x.payload===null));
   if(matches.length!==1)return fail('unresolved or ambiguous payload-free variant');
   return {kind:'named',selector:matches[0]!.selector};
  }
  if(v.op==='to_set'){const t=infer(v.value,scope);if(t.kind!=='list')return fail('to_set requires a list');return {kind:'set',element:t.element};}
  let current=scope.get(v.root)??fail('unresolved input:'+v.root);
  for(const property of v.properties){
   const collection=current.kind==='list'||current.kind==='set',owner=collection?(current as Extract<TypedType,{element:TypedType}>).element:current;
   if(owner.kind==='reference'){
    const field=referenceField(owner);
    if(field.ontology_property!==property)return fail('reference exposes only its declared identity projection:'+owner.selector+'#'+owner.projection[0]);
    current=collection?{kind:current.kind as 'list'|'set',element:field.type}:field.type;
    continue;
   }
   if(owner.kind!=='named')return fail('property requires named value; no implicit optional traversal');
   const d=get(owner.selector);if(d.kind==='Enum')return fail('Enum has no record properties');
   const field=d.contract.properties.find(f=>f.ontology_property===property)??fail('unknown ontology property:'+property);
   current=collection?{kind:current.kind as 'list'|'set',element:field.type}:field.type;
  }
  return current;
 };
 return {get,checkType,infer,referenceField};
}
