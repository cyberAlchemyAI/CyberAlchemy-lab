/** Captured source context/ABI signatures. No native owner is constructed.
 * Open Questions: docs/COMMERCE-CONTRACTS.md#open-questions. */
import path from 'node:path';
import {parseCoreCommerceJson} from './commerce-core-source-owner.js';
import {coreFreeze,coreRelativePath,coreSourceFail as fail,coreSourceChildren as children,coreSourceDescendants as descendants,coreSourceTokens as tokens,coreSourceText as text,type CoreSourceRange} from './commerce-core-syntax.js';
import {parseCoreTypeTokens} from './commerce-core-expression.js';
import {lexCoreCommerceSource} from './commerce-core-syntax.js';
import {CORE_BOOL,CORE_UINT64,type CoreValueType,type CoreValueTypes} from './commerce-core-types.js';
import type {CoreCommerceDeclaration} from './commerce-core-reconstruction.js';
export interface CoreCapturedAsset {readonly path:string;readonly text:string}
export interface CoreNativeSignature {readonly name:string;readonly abi:string;readonly source_module:string;readonly signature_document:Readonly<Record<string,unknown>>;readonly parameters:readonly {readonly name:string|null;readonly annotation:string}[];readonly result:string;readonly raw:Readonly<Record<string,unknown>>}
export interface CoreContextRequirement {readonly source_type:string;readonly projection_type:string;readonly abi:string;readonly source_module:string;readonly properties:readonly {readonly name:string;readonly type:CoreValueType}[];readonly methods:ReadonlyMap<string,CoreNativeSignature>;readonly signature_document:Readonly<Record<string,unknown>>}
export type CoreNativeParameterType={readonly kind:'value';readonly type:CoreValueType}|{readonly kind:'finite-text';readonly values:readonly string[];readonly type:CoreValueType}|{readonly kind:'selected-event';readonly module:string};
export interface CoreContextCatalog {require(declaration:CoreCommerceDeclaration):CoreContextRequirement;annotation(annotation:string,context:CoreContextRequirement,where:CoreSourceRange,signature?:CoreNativeSignature):CoreNativeParameterType;asset(declaration:CoreCommerceDeclaration,heads:readonly string[]):Readonly<{value:unknown;doc:Readonly<Record<string,unknown>>;path:string;parent:unknown}>|null}
const words=(n:import('./commerce-core-syntax.js').CoreSourceNode)=>tokens(n).filter(t=>!t.layout).map(t=>t.token);
const object=(value:unknown,where:CoreSourceRange):Record<string,unknown>=>{if(!value||typeof value!=='object'||Array.isArray(value))fail('InvalidContract',where,'captured signature object required');return value as Record<string,unknown>;};
export function createCoreContextCatalog(types:CoreValueTypes,assets:readonly CoreCapturedAsset[]):CoreContextCatalog {
 const documents=new Map<string,Record<string,unknown>>();let bytes=0;
 for(const a of assets){if(!coreRelativePath(a.path)||!a.path.endsWith('.json'))continue;if(documents.has(a.path))fail('DuplicateSymbol',{path:a.path,start:0,end:0},'duplicate captured contract asset');bytes+=Buffer.byteLength(a.text);if(documents.size>=128||bytes>4194304)fail('ResourceLimit',{path:a.path,start:0,end:0},'captured context asset bound');documents.set(a.path,object(parseCoreCommerceJson(a.text,a.path),{path:a.path,start:0,end:0}));}
 const slice=(d:CoreCommerceDeclaration,heads:readonly string[])=>{
  const matches=children(d.syntax,'interface-clause').filter(c=>heads.includes(words(c)[0]!));if(matches.length>1)fail('DuplicateSymbol',d.syntax,'context signature source is ambiguous');if(!matches.length)return null;
  const n=descendants(matches[0]!,'reference')[0];if(!n)fail('MissingMapping',matches[0]!,'context signature reference absent');const raw=text(n),parts=raw.split('#');if(parts.length>2)fail('InvalidContract',n,'signature reference fragment');const file=parts[0]!,relative=file.includes('/')?file:path.posix.join(path.posix.dirname(d.syntax.path),file),doc=documents.get(relative);if(!doc)fail('UnknownReference',n,'signature file was not captured '+relative);
  let value:unknown=doc,parent:unknown=doc;if(parts[1]){if(!parts[1].startsWith('/'))fail('InvalidContract',n,'signature pointer must be JSON pointer');for(const raw of parts[1].slice(1).split('/')){if(/~(?![01])/.test(raw))fail('InvalidContract',n,'signature pointer escape');const key=raw.replace(/~1/g,'/').replace(/~0/g,'~');if(!value||typeof value!=='object'||!Object.hasOwn(value,key))fail('UnknownReference',n,'signature pointer absent');parent=value;value=(value as Record<string,unknown>)[key];}}
  return {value,doc,path:relative,parent};
 };
 const known=new Map<string,CoreContextRequirement>();
 const annotation=(raw:string,ctx:CoreContextRequirement,where:CoreSourceRange,signature?:CoreNativeSignature):CoreNativeParameterType=>{
  if(typeof raw!=='string')fail('TypeMismatch',where,'explicit native annotation required');
  if(raw.startsWith('schema:')||raw.startsWith('selected-schema:')){
   const m=/^(schema|selected-schema):([A-Za-z_][A-Za-z0-9_.]*)@1$/.exec(raw);if(!m)fail('UnsupportedCapability',where,'unknown native source schema selector/version');if(m[1]==='selected-schema'){const end=m[2]!.lastIndexOf('.'),module=m[2]!.slice(0,end);if(end<1||m[2]!.slice(end+1)!=='Event')fail('UnsupportedCapability',where,'only the registered selected Event role union is supported');if(!types.modules.has(module))fail('UnknownReference',where,'selected Event module absent');return {kind:'selected-event',module};}
   return {kind:'value',type:types.type(signature?.source_module??ctx.source_module,{kind:'named',name:m[2]!},where)};
  }
  const producer=(signature?.signature_document??ctx.signature_document).identity_producers;
  const finite:Readonly<Record<string,unknown>>={ServiceId:producer&&typeof producer==='object'?(producer as Record<string,unknown>).service_ids:undefined,CommandNamespace:producer&&typeof producer==='object'?(producer as Record<string,unknown>).command_namespaces:undefined,StockCommandKindName:signature?.raw.kind_values,OrderActionName:signature?.raw.action_values};
  if(Object.hasOwn(finite,raw)){
   const values=finite[raw];if(!Array.isArray(values)||!values.length||values.length>128||values.some(v=>typeof v!=='string'||!v.length)||new Set(values).size!==values.length)fail('InvalidContract',where,'closed native text domain missing '+raw);const strings=values as string[];return {kind:'finite-text',values:strings,type:{kind:'String',max_bytes:Math.max(...strings.map(v=>Buffer.byteLength(v))),max_scalars:Math.max(...strings.map(v=>[...v].length))}};
  }
  const type=parseCoreTypeTokens(lexCoreCommerceSource(raw,'native-annotation.alch'),where);
  return {kind:'value',type:types.type(signature?.source_module??ctx.source_module,type,where)};
 };
 const require=(d:CoreCommerceDeclaration):CoreContextRequirement=>{
  const prior=known.get(d.id);if(prior)return prior;
  if(d.surface!=='Interface'||!['trusted-context','native-producer','native-auth-owner'].includes(d.interface_kind??''))fail('TypeMismatch',d.syntax,'context requires its declared private Interface owner kind');
  const abiClauses=children(d.syntax,'interface-clause').filter(c=>words(c)[0]==='abi');if(abiClauses.length!==1)fail('MissingMapping',d.syntax,'private context needs one explicit ABI');const abi=text(descendants(abiClauses[0]!,'reference')[0]!);
  const properties=slice(d,['fields']),methods=slice(d,['methods','signatures']),doc=properties?.doc??methods?.doc;if(!doc)fail('MissingMapping',d.syntax,'private context requires captured fields or method signatures');
  for(const source of [properties,methods])if(source?.parent&&typeof source.parent==='object'){const parent=source.parent as Record<string,unknown>;if(parent.abi!==undefined&&parent.abi!==abi)fail('InvalidContract',d.syntax,'source Interface ABI differs from captured context signature ABI');if(parent.serializable===true||parent.public_constructor===true)fail('InvalidContract',d.syntax,'private source context cannot admit a public/serializable signature owner');}
  const sourceModule=/^([A-Za-z_][A-Za-z0-9_.]*)@1$/.exec(String(doc.source_module));if(!sourceModule||!types.modules.has(sourceModule[1]!))fail('UnknownReference',d.syntax,'signature document must declare an exact captured source_module@1');
  const methodRows=new Map<string,CoreNativeSignature>(),propertyRows:{name:string;type:CoreValueType}[]=[],ctx:CoreContextRequirement={source_type:d.id,projection_type:d.id+'.CorePrivateProjection',abi,source_module:sourceModule[1]!,properties:propertyRows,methods:methodRows,signature_document:doc};
  if(types.declarations.has(ctx.projection_type))fail('DuplicateSymbol',d.syntax,'source collides with reserved private projection type');
  if(properties)for(const [name,value]of Object.entries(object(properties.value,d.syntax))){if(typeof value!=='string')fail('TypeMismatch',d.syntax,'property requires explicit source type');const t=annotation(value,ctx,d.syntax);if(t.kind!=='value')fail('TypeMismatch',d.syntax,'context property requires one bounded data type');propertyRows.push({name,type:t.type});}
  if(methods)for(const [name,value]of Object.entries(object(methods.value,d.syntax))){const m=object(value,d.syntax);if(!Array.isArray(m.parameters)||typeof m.result!=='string'||m.abi!==undefined&&m.abi!==abi)fail('InvalidContract',d.syntax,'native signature needs parameters/result and matching ABI');
   const module=/^([A-Za-z_][A-Za-z0-9_.]*)@1$/.exec(String(methods.doc.source_module));if(!module||!types.modules.has(module[1]!))fail('UnknownReference',d.syntax,'method signature document needs its own exact captured source_module@1');
   const parameters=m.parameters.map(p=>{if(typeof p==='string')return {name:null,annotation:p};const param=object(p,d.syntax);if(typeof param.name!=='string'||typeof param.type!=='string')fail('InvalidContract',d.syntax,'named native parameter shape');return {name:param.name,annotation:param.type};});if(parameters.length>128||new Set(parameters.flatMap(p=>p.name?[p.name]:[])).size!==parameters.filter(p=>p.name!==null).length)fail('InvalidContract',d.syntax,'native parameter uniqueness/bound');methodRows.set(name,coreFreeze({name,abi,source_module:module[1]!,signature_document:methods.doc,parameters,result:m.result,raw:m}));
  }
  known.set(d.id,coreFreeze(ctx));return ctx;
 };
 return Object.freeze({require,annotation,asset:slice});
}
