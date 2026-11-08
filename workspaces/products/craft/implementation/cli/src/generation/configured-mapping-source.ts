import type {FieldReferenceModel} from '../input/field-reference-model.js';
import type {TypedMappingContract} from '../typed-backend/contracts.js';
import {checkTypedInputMapping,assignableMappingType,type TypedInputMappingContract} from '../typed-backend/mapping-inputs.js';
import type {TypedType,TypedParameter} from '../typed-operation/contracts.js';
import {createStructuredValueRenderer} from './configured-value-types.js';
import {createStructuredValueExpressionRenderer} from './configured-value-expressions.js';
const q=JSON.stringify,fail=(m:string):never=>{throw new Error('DS_CONFIGURED_MAPPING:'+m);};
/** Static typed projection, never an Entity factory or runtime expression interpreter. */
export function renderConfiguredMapping(contract:TypedMappingContract|TypedInputMappingContract,model:FieldReferenceModel){
  const values=createStructuredValueRenderer(model,fail),{ensure,get}=values;
  let next=0;const value=createStructuredValueExpressionRenderer(values,model,()=> 'q'+next++,fail);
  const target=get(contract.target);if(target.kind==='Enum')return fail('Mapping target requires record fields');
  const inputs:readonly TypedParameter[]=contract.schema_version==='domainspec.typed-mapping/v2'?contract.inputs:[{name:'source',type:{kind:'named',selector:contract.source}}];
  const nativeInputs=inputs.map(p=>ensure(p.type)),scope=new Map(inputs.map((p,i)=>[p.name,{type:p.type,code:'p'+i}]));
  const lines:string[]=[],parts:string[]=[],result_fields:{name:string;type:TypedType;optional:boolean;ontology_property:string}[]=[];
  const add=(name:string,type:TypedType,ontology_property:string,code:string,optional=false,present='')=>{
    const index=result_fields.length;ensure(type);lines.push('  const v'+index+' = '+code+';');
    result_fields.push({name,type,optional,ontology_property});
    parts.push(optional?'...('+present+'?{['+q(name)+']:v'+index+'}:{})':'['+q(name)+']:v'+index);
  };
  if(contract.schema_version==='domainspec.typed-mapping/v2'){
    const checked=checkTypedInputMapping(contract,model.declarations);
    for(const binding of checked.bindings){
      const initial=value(binding.value,scope),fallback=binding.default===null?null:value(binding.default,scope);
      const expression=fallback?'('+initial.code+' ?? '+fallback.code+')':initial.code;
      add(binding.field.name,binding.field.type,binding.field.ontology_property,expression);
    }
  }else{
    const source=get(contract.source);if(source.kind==='Enum')return fail('Mapping source requires record fields');
    lines.push('  const s=ruleData(d["source"]!.value,'+q(source.contract.properties.map(p=>p.name))+');');
    for(const binding of contract.fields){
      const field=target.contract.properties.find(f=>f.name===binding.target)??fail('unknown target field:'+binding.target);
      const from=binding.source===null?null:source.contract.properties.find(f=>f.name===binding.source)??fail('unknown source field:'+binding.source);
      if(from&&!assignableMappingType(from.type,field.type))fail('source/target type mismatch:'+field.name);
      if(binding.default&&!assignableMappingType({kind:'scalar',name:binding.default.type},field.type))fail('default type mismatch:'+field.name);
      const fallback=binding.default?(binding.default.type==='UInt64'?String(binding.default.value)+'n':q(binding.default.value)):null;
      const present=from?'Object.hasOwn(s,'+q(from.name)+')':'false';
      if(from&&fallback===null&&contract.total)lines.push('  if(!'+present+')throw new TypeError("MAPPING_REQUIRED_VALUE");');
      const expression=from?(fallback===null?'p0['+q(from.name)+']':'('+present+'?p0['+q(from.name)+']:'+fallback+')'):fallback??fail('field requires source or default');
      add(field.name,field.type,field.ontology_property,expression,!!from&&fallback===null&&!contract.total&&from.type.kind==='optional',present);
    }
    if(contract.total&&contract.fields.length!==target.contract.properties.length)fail('total Mapping must cover every target field');
  }
  const shape=result_fields.map(f=>'readonly '+q(f.name)+(f.optional?'?':'')+':'+ensure(f.type).native).join(';');
  const signature=inputs.map((p,i)=>'readonly '+q(p.name)+':'+nativeInputs[i]!.input).join(';');
  const body=(
    'export const map = (parameters:Readonly<{'+signature+'}>):Readonly<{'+shape+'}> => {\n'+
    '  const d=ruleData(parameters,'+q(inputs.map(p=>p.name))+');\n'+
    '  if(Object.keys(d).length!=='+inputs.length+')throw new TypeError("MAPPING_INPUT");\n'+
    inputs.map((p,i)=>'  const p'+i+' = '+nativeInputs[i]!.protocol+'.normalize(d['+q(p.name)+']!.value);\n').join('')+
    lines.join('\n')+'\n  return Object.freeze({'+parts.join(',')+'});\n};\n');
  const content=values.source(body).replaceAll('RULE_INPUT','MAPPING_INPUT');
  return {content,inputs,result_fields,target_kind:target.kind};
}
