import type {TypedType,ValueExpression} from '../typed-operation/contracts.js';
import type {FieldReferenceModel} from '../input/field-reference-model.js';
import {createStructuredValueRenderer} from './configured-value-types.js';
export type BoundValue=Readonly<{type:TypedType;code:string}>;
const q=JSON.stringify;
/** Shared static lowering; preserves ontology paths and collection occurrence semantics. */
export function createStructuredValueExpressionRenderer(values:ReturnType<typeof createStructuredValueRenderer>,model:FieldReferenceModel|null,fresh:()=>string,fail:(message:string)=>never){
  const {ensure,get,use}=values,declarations=new Map(model?.declarations.map(d=>[d.selector,d])??[]);
  const value=(node:ValueExpression,scope:ReadonlyMap<string,BoundValue>):BoundValue=>{
    if(node.op==='literal')return {type:{kind:'scalar',name:node.type},code:node.type==='UInt64'?String(node.value)+'n':q(node.value)};
    if(node.op==='variant'){
      for(const d of declarations.values())if(d.kind==='Enum'){
        const variant=d.contract.variants.find(v=>v.ontology_variant===node.selector);
        if(variant&&variant.payload===null){const type:TypedType={kind:'named',selector:d.selector};return {type,code:ensure(type).protocol+'.normalize({variant:'+q(variant.name)+'})'};}
      }return fail('unknown payload-free variant:'+node.selector);
    }
    if(node.op==='to_set'){
      const source=value(node.value,scope);if(source.type.kind!=='list')return fail('to_set requires a list');
      use('to-set');
      return {type:{kind:'set',element:source.type.element},code:'ruleToSet('+source.code+','+ensure(source.type.element).protocol+')'};
    }
    let current=scope.get(node.root)??fail('unknown Rule scope:'+node.root);
    for(const property of node.properties){
      const collection=current.type.kind==='list'||current.type.kind==='set',ownerType=(current.type.kind==='list'||current.type.kind==='set')?current.type.element:current.type;
      if(ownerType.kind==='reference'){
        const d=get(ownerType.selector);if(d.kind!=='Entity')return fail('reference target must be an Entity');
        const field=d.contract.properties.find(f=>f.name===ownerType.projection[0]&&f.identity)??fail('invalid reference identity projection');
        if(field.ontology_property!==property)return fail('reference exposes only its identity projection');
        current={type:collection?{kind:current.type.kind as 'list'|'set',element:field.type}:field.type,code:current.code};
        continue;
      }
      if(ownerType.kind!=='named')return fail('property requires a named value');const d=get(ownerType.selector);
      if(d.kind==='Enum')return fail('Enum has no record properties');
      const field=d.contract.properties.find(f=>f.ontology_property===property)??fail('unknown ontology property:'+property);
      if(collection){
        const item=fresh(),mapped=current.code+'.map('+item+'=>'+item+'['+q(field.name)+'])';
        if(current.type.kind==='set')use('to-set');
        current={type:{kind:current.type.kind as 'list'|'set',element:field.type},code:current.type.kind==='set'?'ruleToSet('+mapped+','+ensure(field.type).protocol+')':'Object.freeze('+mapped+')'};
      }else current={type:field.type,code:current.code+'['+q(field.name)+']'};
    }return current;
  };
  return value;
}
