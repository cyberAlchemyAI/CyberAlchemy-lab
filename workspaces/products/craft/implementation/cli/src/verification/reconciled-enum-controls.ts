import type {CompiledProjectGraph} from '../input/project-model.js';
import type {ReconciledProjectPlan} from '../generation/reconciled-project.js';
import type {SemanticCase} from './reconciled-semantic-controls.js';
import {decodeTypedSumContract} from '../typed-operation/contracts.js';
import {canonicalJson,sha256} from '../input/source-manifest.js';
import {getReconciledSource} from '../generation/reconciled-sources.js';

export const SEMANTIC_ENUM_DEFINITION_SHA256='b42ff6607f4ddfdff572c226d46ab9210cd50801b56b4525815e8964d645deaf';
export interface PlainEnumControls {
 readonly selector:string;readonly kind:'Enum';readonly state:'ready';readonly adapter:'plain-enum';
 readonly contract_sha256:string;readonly relative_path:string;readonly callable:string;
 readonly names:readonly string[];readonly module_paths:readonly string[];readonly cases:readonly SemanticCase[];
 readonly component:Readonly<{relative_path:string;symbol:string;contract_sha256:string;definition_sha256:string}>;
 readonly provider_path:string;
}
const fail=(reason:string):never=>{throw new TypeError('DS_RECONCILED_ENUM_CONTROLS:'+reason);};
const part=(s:string)=>s.length+':'+s;
export function createPlainEnumControls(node:CompiledProjectGraph['nodes'][number],plan:ReconciledProjectPlan):PlainEnumControls|null {
 if(node.kind!=='Enum')fail('Enum source required');
 const contract=decodeTypedSumContract(node.body.typed_contract);
 if(contract.variants.some(v=>v.payload!==null))return null;
 const names=contract.variants.map(v=>v.name).sort(),symbol=node.selector.split(':')[1]!.split('-').map(w=>w[0]!.toUpperCase()+w.slice(1)).join('');
 const find=(name:string)=>{
  const matches=plan.resolved.modules.filter(m=>m.qualified_selectors.includes(node.selector)&&m.exports.some(e=>e.name===name&&e.kind==='value'));
  return matches.length===1?matches[0]!:fail('unique checked export required:'+node.selector+':'+name);
 };
 const definition=find(symbol),componentModule=find(symbol+'ValueComponent'),paths=new Set<string>();
 const visit=(relative:string)=>{
  if(paths.has(relative))return;paths.add(relative);
  const m=plan.resolved.modules.find(m=>m.relative_path===relative)??fail('missing native module');
  for(const i of m.imports)visit(i.target_path??fail('external pure Enum import'));
 };
 visit(definition.relative_path);visit(componentModule.relative_path);
 const providers=plan.resolved.modules.filter(m=>paths.has(m.relative_path)&&['defineEnum','composeEnum'].every(n=>m.exports.some(e=>e.name===n&&e.kind==='value')));
 if(providers.length!==1)fail('unique checked Enum provider required');
 const component={relative_path:componentModule.relative_path,symbol:symbol+'ValueComponent',contract_sha256:sha256(getReconciledSource('factory')),
  definition_sha256:plan.resolved.artifacts.find(a=>a.relative_path===definition.relative_path)?.sha256??fail('missing definition artifact')};
 const cases:SemanticCase[]=[];
 const push=(mode:string,values:string[],value:unknown)=>cases.push({id:'case-'+cases.length,mode,format:'string',values,expected:{kind:'value',value:canonicalJson(value)}});
 push('definition',[],{members:names.map(n=>[n,n]),frozen:true,owned:true,cloned_rejected:true,repeat_rejected:true});
 push('metadata',[],{protocol_id:'typescript.owned-enum-case/v1-candidate',concept:node.selector,contract_sha256:component.contract_sha256,definition_sha256:component.definition_sha256,frozen:true,values_frozen:true,members:names});
 for(const name of names)push('member',[name],{variant:name,frozen:true,owned:true,stable:true,key:part(node.selector)+part(component.contract_sha256)+part(name),self_equal:true,others:names.map(n=>n===name),definition_value_matches:true});
 for(const mode of ['unknown','null','undefined','number','boolean','boxed','object','array','symbol','coercion'])push('invalid-variant',[mode],{name:'TypeError',message:'INVALID_ENUM_VARIANT'});
 for(const mode of ['raw','clone','plain','null','undefined','getter','foreign'])push('unowned',[mode],{owned:false,key:{name:'TypeError',message:'UNOWNED_ENUM_CASE'},left_equal:false,right_equal:false});
 return {selector:node.selector,kind:'Enum',state:'ready',adapter:'plain-enum',contract_sha256:sha256(canonicalJson(contract)),relative_path:definition.relative_path,callable:symbol,names,module_paths:[...paths].sort(),cases,component,provider_path:providers[0]!.relative_path};
}

/** Fixed observation code, not generated from an Enum renderer. */
export const PLAIN_ENUM_RUNNER=String.raw`
const semanticJson=value=>{
 if(value===null||typeof value!=='object')return JSON.stringify(value);
 if(Array.isArray(value))return '['+value.map(semanticJson).join(',')+']';
 return '{'+Object.keys(value).sort().map(k=>JSON.stringify(k)+':'+semanticJson(value[k])).join(',')+'}';
};
const enumImport=async(relative,suffix='')=>import(pathToFileURL(path.join(moduleRoot,relative.replace(/\.ts$/,'.js'))).href+suffix);
const caught=action=>{try{action();return {returned:true};}catch(e){return {name:e?.name,message:e?.message};}};
async function observePlainEnum(row){
 const definition=(await enumImport(row.relative_path))[row.callable],component=(await enumImport(row.component.relative_path))[row.component.symbol],provider=await enumImport(row.provider_path);
 const foreign=(await enumImport(row.component.relative_path,'?semantic-foreign'))[row.component.symbol],result=[];
 for(const c of row.cases){
  let getter_reads=0,input=null,value;
  const first=component.fromVariant(row.names[0]),mode=c.values[0];
  if(c.mode==='definition'){
   const composed=provider.composeEnum({candidate:definition});
   value={members:Object.keys(definition).sort().map(k=>[k,definition[k]]),frozen:Object.isFrozen(definition),
    owned:Object.isFrozen(composed)&&semanticJson(composed)===semanticJson(definition),
    cloned_rejected:caught(()=>provider.composeEnum({candidate:{...definition}})).name==='EnumContractError',
    repeat_rejected:caught(()=>provider.composeEnum({first:definition,second:definition})).name==='EnumContractError'};
  }else if(c.mode==='metadata'){
   value={protocol_id:component.protocol_id,concept:component.concept,contract_sha256:component.contract_sha256,definition_sha256:component.definition_sha256,
    frozen:Object.isFrozen(component),values_frozen:Object.isFrozen(component.values),members:Object.keys(component.values).sort()};
  }else if(c.mode==='member'){
   const owned=component.fromVariant(mode);
   value={variant:owned.variant,frozen:Object.isFrozen(owned),owned:component.isOwned(owned),stable:owned===component.fromVariant(mode)&&owned===component.values[mode],
    key:component.key(owned),self_equal:component.equals(owned,owned),others:row.names.map(n=>component.equals(owned,component.fromVariant(n))),definition_value_matches:owned.variant===definition[mode]};
  }else{
   let unknown='__semantic_unknown__';while(row.names.includes(unknown))unknown+='_';
   const variants={unknown,null:null,undefined:undefined,number:0,boolean:false,boxed:new String(row.names[0]),object:{variant:row.names[0]},array:[row.names[0]],symbol:Symbol('case'),
    coercion:{toString(){getter_reads++;return row.names[0];},valueOf(){getter_reads++;return row.names[0];}}};
   const unowned={raw:row.names[0],clone:{...first},plain:{variant:row.names[0]},null:null,undefined:undefined,
    getter:Object.defineProperty({},'variant',{enumerable:true,get(){getter_reads++;return row.names[0];}}),foreign:foreign.fromVariant(row.names[0])};
   input=c.mode==='invalid-variant'?variants[mode]:unowned[mode];
   const descriptors=input&&typeof input==='object'?Object.getOwnPropertyDescriptors(input):null,prototype=descriptors?Object.getPrototypeOf(input):null;
   if(c.mode==='invalid-variant')value=caught(()=>component.fromVariant(input));
   else value={owned:component.isOwned(input),key:caught(()=>component.key(input)),left_equal:component.equals(input,first),right_equal:component.equals(first,input)};
   const after=descriptors?Object.getOwnPropertyDescriptors(input):null;
   const same=descriptors===null||Object.getPrototypeOf(input)===prototype&&Reflect.ownKeys(descriptors).length===Reflect.ownKeys(after).length&&Reflect.ownKeys(descriptors).every(k=>{
    const a=descriptors[k],b=after[k];return b&&['value','get','set','writable','enumerable','configurable'].every(p=>Object.is(a[p],b[p]));
   });
   result.push({id:c.id,outcome:{kind:'value',value:semanticJson(value)},getter_reads,input_changed:!same});continue;
  }
  result.push({id:c.id,outcome:{kind:'value',value:semanticJson(value)},getter_reads,input_changed:false});
 }
 return {selector:row.selector,cases:result};
}
`;
