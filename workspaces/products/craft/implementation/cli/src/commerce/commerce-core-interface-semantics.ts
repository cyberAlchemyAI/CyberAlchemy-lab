/** Eager source Interface typing/custody/ownership checks. Captured declarations
 * and references remain requirements for later native/family implementations.
 * Open Questions: docs/COMMERCE-OBLIGATIONS.md#open-questions. */
import {dataDigest} from '../profile-engine/contracts.js';
import {coreFreeze,coreSourceFail as fail,coreSourceChildren as children,coreSourceTokens as tokens,coreSourceText as text,lexCoreCommerceSource,type CoreSourceNode,type CoreSourceRange} from './commerce-core-syntax.js';
import {reconstructCoreCommerceSources} from './commerce-core-reconstruction.js';
import {createCoreValueTypes} from './commerce-core-types.js';
import {parseCoreTypeTokens} from './commerce-core-expression.js';
import {createCoreContextCatalog,type CoreCapturedAsset} from './commerce-core-context.js';
export interface CoreInterfaceClauseCheck {readonly head:string;readonly span:CoreSourceRange;readonly check:'declared-source-interface-constraint';readonly runtime_qualified:false}
export interface CoreInterfaceSemantics {readonly name:string;readonly kind:string;readonly clauses:readonly CoreInterfaceClauseCheck[];readonly static_types:readonly {readonly selector:string;readonly type:unknown}[];readonly dependencies:readonly string[];readonly implementation_tasks:readonly string[];readonly runtime_qualified:false;readonly subject_sha256:string}
const words=(n:CoreSourceNode)=>tokens(n).filter(t=>!t.layout).map(t=>t.token),span=(n:CoreSourceRange)=>({path:n.path,start:n.start,end:n.end});
const allowed:Readonly<Record<string,readonly string[]>>={
 internal:['exposes','visibility'],external:['protocol','exposes','request','result','binding'],
 'bounded-schema':['scalar','validates','codec','optional','on-invalid'],
 'native-producer':['abi','custody','fields','methods','signatures','implementation','on-unresolved'],
 'trusted-context':['abi','custody','fields','methods','variants','serializable','public-constructor'],
 'native-auth-owner':['abi','admission','decision','binding','on-unresolved'],
 'technical-profile-family':['family-contract','obligations','input','output','callbacks','unknown-primitive','missing-producer'],
 'application-composition':['source','service','entry-catalog','implementation','parameters','http-bindings','value-domain','computation-bounds','provider-protocol','authorization','native-obligations','profile-family','coordination-contract','source-identities','coordination-records','required-output','formal-claims','hosting'],
};
export const CORE_INTERFACE_IMPLEMENTATION_TASKS:Readonly<Record<string,readonly string[]>>=coreFreeze({internal:[],external:['EC26','EC27'],'bounded-schema':['EC09','EC13'],'native-producer':['EC09','EC12'],'trusted-context':['EC11','EC22'],'native-auth-owner':['EC11','EC21'],'technical-profile-family':['EC10','EC12'],'application-composition':['EC31','EC33','EC34']});
const property=/^[A-Za-z_][A-Za-z0-9_]*$/;
function object(value:unknown,where:CoreSourceRange):Record<string,unknown>{if(!value||typeof value!=='object'||Array.isArray(value))fail('InvalidContract',where,'declared source object required');return value as Record<string,unknown>;}
export function checkCoreCommerceInterfaceSources(sources:readonly {readonly path:string;readonly text:string}[],assets:readonly CoreCapturedAsset[]):readonly CoreInterfaceSemantics[] {
 const model=reconstructCoreCommerceSources(sources),types=createCoreValueTypes(model),catalog=createCoreContextCatalog(types,assets),out:CoreInterfaceSemantics[]=[];
 for(const d of types.declarations.values())if(d.surface==='Interface'){
  const kind=d.interface_kind!,clauses=children(d.syntax,'interface-clause'),heads=allowed[kind];if(!heads)fail('UnsupportedCapability',d.syntax,'unknown source Interface kind');
  const groups=new Map<string,CoreSourceNode[]>(),static_types:{selector:string;type:unknown}[]=[],dependencies:string[]=[];
  for(const n of clauses){const head=words(n)[0]!;if(!heads.includes(head))fail('InvalidContract',n,'Interface clause does not belong to its declared kind');const prior=groups.get(head)??[];prior.push(n);groups.set(head,prior);}
  for(const [head,rows]of groups)if(rows.length>1&&!['source','service','required-output','scalar','validates','exposes'].includes(head))fail('DuplicateSymbol',rows[1]!,'duplicate Interface singleton clause');
  const one=(head:string,required=true)=>{const rows=groups.get(head)??[];if(rows.length>1)fail('DuplicateSymbol',d.syntax,'one exact Interface '+head+' required');if(required&&!rows.length)fail('MissingMapping',d.syntax,'Interface requires '+head);return rows[0]??null;};
  const reference=(head:string,required=true)=>{if(!one(head,required))return null;const binding=catalog.asset(d,[head]);if(!binding)fail('MissingMapping',d.syntax,'Interface file reference was not captured');dependencies.push(binding.path);return binding;};
  const type=(n:CoreSourceNode,selector:string)=>{const value=types.type(d.module,parseCoreTypeTokens(tokens(n),n),n);static_types.push({selector,type:value});return value;};
  if(kind==='internal'){
   if(!d.exposes.length)fail('MissingMapping',d.syntax,'internal Interface requires declared local exposures');
   const visibility=one('visibility',false);if(visibility){const owner=words(visibility).at(-1)!,actual=model.ownership.find(o=>o.declaration===d.id)?.service;if(!actual||actual!==owner)fail('InvalidContract',visibility,'service-private visibility must match actual declared service ownership');}
  }else if(kind==='external'){
   one('protocol');if(!d.exposes.length)fail('MissingMapping',d.syntax,'external Interface requires declared method names');for(const head of ['request','result'])type(children(one(head)!,'type')[0]!,head);reference('binding');
  }else if(kind==='bounded-schema'){
   const seenScalars=new Set<string>(),seenAssociations=new Set<string>();
   for(const n of clauses){const ts=words(n);if(ts[0]==='scalar'){const scalar=ts[1]!;if(seenScalars.has(scalar))fail('DuplicateSymbol',n,'duplicate primitive scalar declaration');seenScalars.add(scalar);if(scalar==='UInt64'){const at=ts.indexOf('range');if(BigInt(ts[at+1]!)!==0n||BigInt(ts[at+3]!)!==18446744073709551615n)fail('UnsupportedCapability',n,'UInt64 primitive has the exact full unsigned64 domain;express narrower business constraints with a Rule/invariant');}}
    if(ts[0]==='validates'){const node=children(children(n,'value-domain-clause')[0]??n,'type')[0]!,value=type(node,'validates'),key=dataDigest(value);if(seenAssociations.has(key))fail('DuplicateSymbol',n,'duplicate value-domain validation association');seenAssociations.add(key);const using=ts[ts.indexOf('using')+1]!;if(using==='declared-refinement'&&value.kind!=='refinement'||using==='closed-enum'&&value.kind!=='enum'||using==='closed-fields-and-invariants'&&value.kind!=='record')fail('TypeMismatch',n,'validation mode must match its declared bounded type');if(!['declared-refinement','closed-enum','closed-fields-and-invariants'].includes(using)){const rule=types.resolve(d.module,using,n);if(rule.surface!=='Rule'||rule.parameters.length!==1||dataDigest(types.type(rule.module,rule.parameters[0]!.type,rule.parameters[0]!.span))!==dataDigest(value))fail('TypeMismatch',n,'validation must bind an exact unary Bool Rule');}}
   }
  }else if(kind==='native-producer'||kind==='trusted-context'){
   one('abi');const custody=one('custody',false);if(kind==='native-producer'&&custody&&words(custody)[1]!=='private-registered-source-profile-callsite')fail('InvalidContract',custody,'native producer requires original source/profile callsite custody');
   if(kind==='trusted-context'){for(const head of ['serializable','public-constructor'])one(head);}
   const variants=one('variants',false),direct=groups.has('fields')||groups.has('methods')||groups.has('signatures');if(!direct&&!variants)fail('MissingMapping',d.syntax,'private Interface needs captured fields/methods/variants');
   if(direct){const context=catalog.require(d);for(const field of context.properties){if(!property.test(field.name))fail('InvalidContract',d.syntax,'closed private property identifier required');static_types.push({selector:'field:'+field.name,type:field.type});}
    for(const [method,signature]of context.methods){if(!property.test(method))fail('InvalidContract',d.syntax,'closed native method identifier required');for(const p of signature.parameters){if(p.name!==null&&!property.test(p.name))fail('InvalidContract',d.syntax,'closed native parameter identifier required');static_types.push({selector:'method:'+method+':'+(p.name??signature.parameters.indexOf(p)),type:catalog.annotation(p.annotation,context,d.syntax,signature)});}const result=catalog.annotation(signature.result,context,d.syntax,signature);if(result.kind!=='value')fail('TypeMismatch',d.syntax,'native result requires one explicit bounded type');static_types.push({selector:'result:'+method,type:result.type});}
    for(const head of ['fields','methods','signatures'])if(groups.has(head))reference(head);
   }
   if(variants){const asset=reference('variants')!,schemas=object(asset.value,variants),sourceModule=typeof asset.doc.source_module==='string'?/^([A-Za-z_][A-Za-z0-9_.]*)@1$/.exec(asset.doc.source_module):null;if(!sourceModule||!types.modules.has(sourceModule[1]!))fail('UnknownReference',variants,'variant schemas need their exact captured source_module@1');
    for(const [name,raw]of Object.entries(schemas)){if(!property.test(name))fail('InvalidContract',variants,'closed private variant name required');const value=object(raw,variants);if(value.kind!=='opaque-private-projection'||typeof value.projection_family!=='boolean'||value.public_constructor===true||value.serializable===true)fail('InvalidContract',variants,'source variants must preserve opaque private projection and explicit family status');const fs=object(value.fields,variants);if(Object.keys(fs).length>64)fail('ResourceLimit',variants,'private variant field limit');for(const [field,annotation]of Object.entries(fs)){if(!property.test(field)||typeof annotation!=='string')fail('TypeMismatch',variants,'private variant field needs a closed name and bounded source type');const t=types.type(sourceModule[1]!,parseCoreTypeTokens(lexCoreCommerceSource(annotation,'variant-annotation.alch'),variants),variants);static_types.push({selector:'variant:'+name+':'+field,type:t});}}
   }
  }else if(kind==='native-auth-owner'){
   const abi=text(children(one('abi')!,'reference')[0]!),binding=reference('binding')!;one('admission');one('decision');if(binding.doc.abi!==abi)fail('InvalidContract',d.syntax,'Auth declaration and captured binding ABI differ');
  }else if(kind==='technical-profile-family'){
   reference('family-contract');reference('obligations');for(const head of ['input','output','callbacks','unknown-primitive','missing-producer'])one(head);
  }else{
   const outputs=(groups.get('required-output')??[]).map(n=>words(n)[1]!);if(new Set(outputs).size!==outputs.length)fail('DuplicateSymbol',d.syntax,'required outputs must be unique');
   for(const head of ['entry-catalog','implementation']){const n=one(head,false);if(n){const name=text(children(children(n,'application-clause')[0]??n,'qualified-name')[0]!);if(head==='entry-catalog'){if(!model.modules.some(m=>m.module===name))fail('UnknownReference',n,'entry catalog must name a captured source module');}else if(types.resolve(d.module,name,n).surface!=='Mapping')fail('TypeMismatch',n,'implementation selection must name a declared Mapping');}}
   for(const n of groups.get('coordination-records')??[]){const clause=children(n,'application-clause')[0]??n,list=children(clause,'name-list')[0]!;for(const name of children(list,'qualified-name')){const record=types.resolve(d.module,text(name),name);if(!['Entity','ValueObject'].includes(record.surface))fail('TypeMismatch',name,'coordination records must be declared records');}}
   for(const head of ['parameters','http-bindings','value-domain','computation-bounds','provider-protocol','authorization','native-obligations','profile-family','coordination-contract','source-identities'])if(groups.has(head))reference(head);
  }
  const implementation_tasks=CORE_INTERFACE_IMPLEMENTATION_TASKS[kind]!,clause_checks=clauses.map(n=>({head:words(n)[0]!,span:span(n),check:'declared-source-interface-constraint' as const,runtime_qualified:false as const}));
  const subject_sha256=dataDigest({name:d.id,kind,tokens:tokens(d.syntax).filter(t=>!t.layout).map(t=>t.token),static_types,dependencies,implementation_tasks});out.push(coreFreeze({name:d.id,kind,clauses:clause_checks,static_types,dependencies:[...new Set(dependencies)],implementation_tasks,runtime_qualified:false,subject_sha256}));
 }
 return coreFreeze(out.sort((a,b)=>a.name<b.name?-1:a.name>b.name?1:0));
}
