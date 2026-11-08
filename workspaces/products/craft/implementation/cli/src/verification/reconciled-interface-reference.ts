import type {CompiledProjectGraph} from '../input/project-model.js';
import {decodeNamedInterface,type NamedInterfaceContract,type InterfacePublicType} from '../typed-backend/interface.js';
import {qualifyPublicType} from '../typed-backend/mapping-public.js';
import {createMappingReference,MappingCapacity,type MappingType} from './reconciled-mapping-reference.js';
import type {FactRecipe} from './reconciled-rule-facts.js';
/** Exact source policy interpretation; does not call the runtime policy implementation. */
export function interfaceVersionCases(contract:NamedInterfaceContract){
 const p=contract.version_policy,parts=p.provider_version.split('.').map(BigInt),strings=new Set([p.provider_version,'0.0.0','1.0.0','0.1.0','0.0.1','9.9.9','10.10.10',Array(3).fill('9'.repeat(64)).join('.')]);
 for(let i=0;i<3;i++)for(const n of [0n,1n,parts[i]!-1n,parts[i]!+1n])if(n>=0n&&String(n).length<=64){const next=[...parts];next[i]=n;strings.add(next.join('.'));}
 for(const v of ['', '1','1.2','01.2.3','1.02.3','1.2.03','-1.2.3','1.2.3-alpha','1.2.3+build','1.2.3\n',' 1.2.3','1.2.3 ','1.2.3.4','1e1.2.3','１.2.3','9'.repeat(65)+'.0.0'])strings.add(v);
 const recipes:FactRecipe[]=[...strings].map(value=>({tag:'scalar',value}));
 for(const mode of ['undefined','number','boolean','array','object','coercion'])recipes.push({tag:'bad',base:{tag:'null'},mode});
 recipes.push({tag:'null'},{tag:'scalar',value:'1',format:'bigint'},{tag:'scalar',value:'1',format:'number'});
 return recipes.map(recipe=>{
  let result=false;
  if(recipe.tag==='scalar'&&!recipe.format&&typeof recipe.value==='string'){
   const v=recipe.value.split('.');if(v.length===3&&v.every(c=>c.length>=1&&c.length<=64&&c.split('').every(x=>x>='0'&&x<='9')&&(c==='0'||c[0]!=='0'))){
    const c=v.map(BigInt);
    result=p.mode==='exact'?c.every((x,i)=>x===parts[i]):c[0]===parts[0]&&(parts[1]!>c[1]!||parts[1]===c[1]&&parts[2]!>=c[2]!);
   }
  }return {recipe,result};
 });
}
/** Expected structural types are derived from declarations, never a generated type alias. */
export function interfaceSignature(graph:CompiledProjectGraph,selector:string,relative_path:string){
 const contract=decodeNamedInterface(graph.nodes.find(n=>n.selector===selector)!.body.typed_contract),reference=createMappingReference(graph);
 let bytes=0;
 const type=(t:MappingType,depth=0):string=>{
  if(depth>64)throw new MappingCapacity('bounded Interface signature depth exceeded');
  let s:string;
  if(t.kind==='scalar')s=t.name==='UInt64'?'bigint':t.name==='String'?'string':'boolean';
  else if(t.kind==='optional')s='('+type(t.element,depth+1)+')|null';
  else if(t.kind==='list'||t.kind==='set')s='ReadonlyArray<'+type(t.element,depth+1)+'>';
  else if(t.kind==='sum')s=t.variants.map(v=>'Readonly<{variant:'+JSON.stringify(v.name)+(v.payload?';payload:'+type(v.payload,depth+1):'')+'}>').join('|');
  else{const d=reference.get(t);s=d.kind==='Enum'?type({kind:'sum',variants:d.variants},depth+1):'Readonly<{'+d.properties.map(p=>'readonly '+JSON.stringify(p.name)+':'+type(p.type,depth+1)).join(';')+'}>';}
  bytes+=s.length;if(bytes>8388608)throw new MappingCapacity('bounded Interface signature expansion exceeded');return s;
 };
 const local=(t:InterfacePublicType)=>type(qualifyPublicType(t,selector));
 return 'import type {Interface,PublicContracts} from '+JSON.stringify('../../native/'+relative_path.replace(/\.ts$/,'.js'))+';\n'+
 'type Equal<A,B>=(<T>()=>T extends A?1:2) extends (<T>()=>T extends B?1:2)?true:false;\ntype Assert<T extends true>=T;\n'+
 'type ExpectedContracts=Readonly<{'+contract.contracts.map(c=>'readonly '+JSON.stringify(c.contract_id)+':'+local({kind:'contract',contract_id:c.contract_id})).join(';')+'}>;\n'+
 'type ExpectedInterface=Readonly<{'+contract.operations.map(o=>'readonly '+JSON.stringify(o.operation_id)+':(request:'+local(o.request)+')=>Promise<'+local(o.result)+'>').join(';')+'}>;\n'+
 'type ContractCheck=Assert<Equal<PublicContracts,ExpectedContracts>>;\ntype InterfaceCheck=Assert<Equal<Interface,ExpectedInterface>>;\n';
}
