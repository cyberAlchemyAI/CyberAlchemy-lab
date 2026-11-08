import type {TypedQueryContract,BackendPredicate,BackendValue} from '../typed-backend/contracts.js';
import {queryReturnsOptional} from '../typed-backend/contracts.js';
import type {TypedType} from '../typed-operation/contracts.js';
import type {FieldReferenceModel} from '../input/field-reference-model.js';
import {canonicalJson} from '../input/source-manifest.js';
import {createStructuredValueRenderer} from './configured-value-types.js';

const fail=(message:string):never=>{throw new Error('DS_CONFIGURED_QUERY:'+message);};
const q=JSON.stringify;
/** Static specialization over exact checked source fields. It never opens a
 * repository, executes an invariant, or interprets a query AST at runtime.
 */
export function renderConfiguredQuery(contract:TypedQueryContract,model:FieldReferenceModel){
  const values=createStructuredValueRenderer(model,fail),source=values.get(contract.source);
  if(source.kind!=='Entity')return fail('Query read target must be an Entity');
  const fields=source.contract.properties,field=(name:string)=>fields.find(f=>f.name===name)??fail('unknown source field:'+name);
  const parameters=contract.inputs.map(p=>values.ensure(p.type));
  const rowsType=values.ensure({kind:'list',element:{kind:'named',selector:contract.source}});
  const resultFields=contract.projection.map(name=>({name,type:field(name).type}));
  const optional=queryReturnsOptional(contract);
  const projectionType='Readonly<{'+resultFields.map(f=>'readonly '+q(f.name)+':'+values.ensure(f.type).native).join(';')+'}>';
  const resultType=optional?projectionType+' | null':'ReadonlyArray<'+projectionType+'>';
  const value=(v:BackendValue):{type:TypedType;code:string}=>{
    if(v.kind==='literal')return {type:{kind:'scalar',name:v.type},code:v.type==='UInt64'?String(v.value)+'n':q(v.value)};
    if(v.kind==='field')return {type:field(v.name).type,code:'row['+q(v.name)+']'};
    const index=contract.inputs.findIndex(p=>p.name===v.name);if(index<0)return fail('unknown parameter:'+v.name);
    return {type:contract.inputs[index]!.type,code:'p'+index};
  };
  const predicate=(e:BackendPredicate):string=>{
    if(e.op==='all'||e.op==='any')return e.terms.length?'('+e.terms.map(predicate).join(e.op==='all'?' && ':' || ')+')':e.op==='all'?'true':'false';
    if(e.op==='not')return '!('+predicate(e.term)+')';
    if(!('left' in e))return fail('unknown predicate');
    const left=value(e.left),right=value(e.right);
    if(canonicalJson(left.type)!==canonicalJson(right.type))return fail('comparison type mismatch');
    if(e.op==='eq')return '('+values.ensure(left.type).protocol+'.key('+left.code+') === '+values.ensure(right.type).protocol+'.key('+right.code+'))';
    if(left.type.kind!=='scalar')return fail('ordering requires a required scalar');
    const l=left.type.name==='Bool'?'Number('+left.code+')':left.code,r=left.type.name==='Bool'?'Number('+right.code+')':right.code;
    return '('+l+' '+({lt:'<',lte:'<=',gt:'>',gte:'>='} as const)[e.op]+' '+r+')';
  };
  const filter=contract.filter?predicate(contract.filter):'true';
  let ordering='';
  if(contract.order_by){
    const f=field(contract.order_by.field);if(f.type.kind!=='scalar')return fail('ordering requires a required scalar');
    const value=(owner:string)=>f.type.kind==='scalar'&&f.type.name==='Bool'?'Number('+owner+'['+q(f.name)+'])':owner+'['+q(f.name)+']';
    const a=value('a'),b=value('b'),less=contract.order_by.direction==='asc'?'-1':'1',more=contract.order_by.direction==='asc'?'1':'-1';
    ordering='  selected.sort((a,b)=>'+a+' < '+b+' ? '+less+' : '+a+' > '+b+' ? '+more+' : 0);\n';
  }
  const filterBinding=contract.filter?'row':'_row';
  const body='// Checked Query program follows.\nexport const query = (rows:'+rowsType.input+',parameters:Readonly<{'+contract.inputs.map((p,i)=>'readonly '+q(p.name)+':'+parameters[i]!.input).join(';')+'}>):'+resultType+' => {\n'+
    '  const d=ruleData(parameters,'+q(contract.inputs.map(p=>p.name))+');\n'+
    '  if(Object.keys(d).length!=='+contract.inputs.length+')throw new TypeError(\'QUERY_INPUT\');\n'+
    contract.inputs.map((p,i)=>'  const p'+i+'='+parameters[i]!.protocol+'.normalize(d['+q(p.name)+']!.value);\n').join('')+
    '  const snapshots='+rowsType.protocol+'.normalize(rows);\n'+
    '  let selected=snapshots.filter('+filterBinding+'=>'+filter+');\n'+ordering+
    (contract.limit===null?'':'  selected=selected.slice(0,'+contract.limit+');\n')+
    (optional?'  if(selected.length>1)throw new TypeError(\'QUERY_CARDINALITY\');\n  if(selected.length===0)return null;\n  const row=selected[0]!;\n  return Object.freeze({'+contract.projection.map(f=>'['+q(f)+']:row['+q(f)+']').join(',')+'});\n':
    '  return Object.freeze(selected.map(row=>Object.freeze({'+contract.projection.map(f=>'['+q(f)+']:row['+q(f)+']').join(',')+'})));\n')+'};\n';
  return {content:values.source().replaceAll("'RULE_INPUT'","'QUERY_INPUT'")+body,result_fields:resultFields,read_fields:fields.map(f=>f.name).sort()};
}
