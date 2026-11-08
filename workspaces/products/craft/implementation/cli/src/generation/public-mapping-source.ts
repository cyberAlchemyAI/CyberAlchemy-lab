import {assertCheckedPublicMapping,type CheckedPublicMapping} from '../input/compiled-public-mapping.js';
import {assertCompiledProjectFields,type CompiledProjectFields} from '../input/compiled-field-model.js';
import {createPublicMappingValues} from './public-mapping-values.js';
import {canonicalJson,sha256} from '../input/source-manifest.js';
import type {MappingValueType} from '../typed-backend/mapping-public.js';
import {assertInterfaceData} from '../typed-backend/interface.js';
const q=JSON.stringify,fail=(message:string):never=>{throw new TypeError('DS_PUBLIC_MAPPING_SOURCE:'+message);};
export interface PublicMappingImport {readonly selector:string;readonly alias:string;readonly path:string;readonly descriptor:Readonly<{selector:string;contract_sha256:string;graph_sha256:string;field_compilation_sha256:string|null}>;}
/** Pure static field projection. Imports provide values and types, never endpoint calls. */
export function renderPublicMappingSource(mapping:CheckedPublicMapping,fields:CompiledProjectFields|null,imports:readonly PublicMappingImport[]){
 assertCheckedPublicMapping(mapping);if(fields!==null)assertCompiledProjectFields(fields);
 assertInterfaceData(imports);
 if(mapping.field_compilation_sha256!==(fields?.compilation_sha256??null))fail('field mismatch');
 if(canonicalJson(imports.map(i=>i.selector).sort())!==canonicalJson(mapping.bindings.interface_selectors))fail('exact Interface import closure required');
 const aliases=new Map(imports.map(i=>[i.selector,i.alias]));if(new Set(imports.map(i=>i.alias)).size!==imports.length)fail('duplicate import alias');
 for(const i of imports){
  if(!/^Public[0-9]+$/.test(i.alias)||typeof i.path!=='string'||!i.path.endsWith('.js'))fail('invalid native import');
  const source=mapping.interfaces.find(api=>api.source.selector===i.selector)??fail('missing Interface evidence');
  if(i.descriptor.selector!==i.selector||i.descriptor.contract_sha256!==sha256(canonicalJson(source.contract))||i.descriptor.graph_sha256!==mapping.certificate.graph_sha256||i.descriptor.field_compilation_sha256!==(fields?.compilation_sha256??null))fail('Interface descriptor mismatch');
 }
 const values=createPublicMappingValues(fields?.model??null,mapping.interfaces.map(i=>({selector:i.source.selector,contract:i.contract})),aliases,fail);
 const inputs=mapping.contract.inputs.map(p=>({...p,native:values.ensure(p.type)}));
 const scope=new Map(inputs.map((p,i)=>[p.name,{type:p.type,code:'p'+i}]));
 const projections=mapping.bindings.fields.map(f=>{
  const value=values.expression(f.value,scope),fallback=f.default===null?null:values.expression(f.default,scope),target=values.ensure(f.target.type as MappingValueType);
  return {name:f.target.name,native:target.native,code:target.protocol+'.normalize('+(fallback?'('+value.code+' ?? '+fallback.code+')':value.code)+')'};
 });
 let result='Readonly<{'+projections.map(p=>'readonly '+q(p.name)+':'+p.native).join(';')+'}>';
 if(mapping.contract.target.kind==='contract'){
  const target=values.ensure(mapping.contract.target).native;
  result=mapping.contract.total?target:'Pick<'+target+','+(projections.length?projections.map(p=>q(p.name)).join('|'):'never')+'>';
 }
 const body=
  'export type Parameters=Readonly<{'+inputs.map(p=>'readonly '+q(p.name)+':'+p.native.input).join(';')+'}>;\n'+
  'export type Result='+result+';\n'+
  'export const map=(parameters:Parameters):Result=>{\n'+
  ' const d=ruleData(parameters,'+q(inputs.map(p=>p.name))+');\n'+
  ' if(Object.keys(d).length!=='+inputs.length+')throw new TypeError("MAPPING_INPUT");\n'+
  inputs.map((p,i)=>' const p'+i+'='+p.native.protocol+'.normalize(d['+q(p.name)+']!.value);\n').join('')+
  projections.map((p,i)=>' const v'+i+'='+p.code+';\n').join('')+
  ' return Object.freeze({'+projections.map((p,i)=>'['+q(p.name)+']:v'+i).join(',')+'});\n};\n';
 const code=imports.map(i=>'import * as '+i.alias+' from '+q(i.path)+';\n').join('')+
  imports.map(i=>'if('+i.alias+'.descriptor.selector!=='+q(i.descriptor.selector)+'||'+i.alias+'.descriptor.contract_sha256!=='+q(i.descriptor.contract_sha256)+'||'+i.alias+'.descriptor.graph_sha256!=='+q(i.descriptor.graph_sha256)+'||'+i.alias+'.descriptor.field_compilation_sha256!=='+q(i.descriptor.field_compilation_sha256)+')throw new TypeError("MAPPING_INTERFACE_BINDING");\n').join('')+
  values.source(body);
 // Keep authored strings/identifiers intact; only the fixed shared support error literal changes.
 return {content:code,result_fields:projections.map(p=>p.name)};
}
