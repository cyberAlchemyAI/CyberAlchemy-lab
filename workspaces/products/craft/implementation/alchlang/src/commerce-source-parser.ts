/** Parse commerce-source/v1-candidate into structured role syntax. This does not
 * implement the separate Core semantic/computation/native APIs.
 * Open Questions: EC06/CONTEXT.md. */
import {createHash} from 'node:crypto';
import {parseCommerceSyntax} from './commerce-source-syntax.js';
import {COMMERCE_SOURCE_LIMITS} from './commerce-source-lexer.js';
import {sourceFail,commerceSyntaxChild as child,commerceSyntaxChildren as children,commerceSyntaxTokens as tokens,commerceSyntaxText as text,
 type CommerceSyntax,type CommerceSourceType,type CommerceSourceField,type CommerceParsedModule,type CommerceDeclarationSource,type CommerceSourceImport,type CommerceSourceRole,type CommerceCallableSource,type CommerceRecordSource,type CommerceClaimSource} from './commerce-source-model.js';
import type {CommerceResult} from './commerce-stages-v1.js';
import {CommerceSourceError} from './commerce-source-model.js';
const roles:Readonly<Record<string,CommerceSourceRole| 'Entry'|'FormalClaim'>>=Object.freeze({'record-declaration':'ValueObject','enum-declaration':'Enum','rule-declaration':'Rule','calculation-declaration':'Calculation','mapping-declaration':'Mapping','policy-declaration':'Policy','machine-declaration':'StateMachine','operation-declaration':'Operation','query-declaration':'Query','workflow-declaration':'Workflow','interface-declaration':'Interface','entry-declaration':'Entry','claim-declaration':'FormalClaim'});
const span=(node:CommerceSyntax)=>({path:node.path,start:node.start,end:node.end});
export function commerceSourceType(node:CommerceSyntax):CommerceSourceType {
 const parts=tokens(node).map(t=>t.text);let at=0;
 const take=()=>parts[at++];const expect=(value:string)=>{if(take()!==value)sourceFail('Syntax',node,`type needs ${value}`);};
 const parse=():CommerceSourceType=>{
  const first=take();if(first==='UInt64'||first==='Bool')return {kind:'scalar',name:first};if(first==='String')return {kind:'string'};
  if(first==='optional'){expect('<');const element=parse();expect('>');return {kind:'optional',element};}
  if(first==='List'){expect('<');const element=parse();expect(',');const value=take()!;expect('>');if(!/^[1-9][0-9]*$/.test(value)||BigInt(value)>100n)sourceFail('ResourceLimit',node,'List maximum must be1..100');return {kind:'list',element,max_items:Number(value)};}
  if(first==='outcome'){expect('<');const state=parse();expect(',');const intent=parse();expect(',');const value=take()!;expect('>');if(!/^(0|[1-9][0-9]*)$/.test(value)||BigInt(value)>100n)sourceFail('ResourceLimit',node,'outcome intent maximum exceeds100');return {kind:'outcome',state,intent,max_intents:Number(value)};}
  if(first==='literal'){const value:unknown=JSON.parse(take()!);if(typeof value!=='string')sourceFail('TypeMismatch',node,'string literal type required');return {kind:'literal',value};}
  if(!first)return sourceFail('Syntax',node,'missing type');let name=first;while(parts[at]==='.'){at++;name+='.'+take();}return {kind:'named',name};
 };
 const value=parse();if(at!==parts.length)sourceFail('Syntax',node,'trailing type tokens');return value;
}
function field(node:CommerceSyntax):CommerceSourceField {const ts=tokens(node),type=children(node,'type')[0]??child(node,'qualified-name');return {name:ts[0]?.text==='input'||ts[0]?.text==='context'?ts[1]!.text:ts[0]!.text,type:commerceSourceType(type),span:span(node)};}
function nameList(node:CommerceSyntax):string[]{return children(node,'qualified-name').map(text);}
function freeze<T>(value:T):T {if(value&&typeof value==='object'){for(const item of Object.values(value))freeze(item);Object.freeze(value);}return value;}
export function parseCommerceModuleSource(source:string,relativePath:string):CommerceParsedModule {
 const syntax=parseCommerceSyntax(source,relativePath),header=child(syntax,'module-header'),module=text(child(header,'qualified-name'));
 if(module.length>256)sourceFail('ResourceLimit',header,'module name exceeds256');
 const version= tokens(header).at(-1)!.text;if(version!=='1')sourceFail('UnsupportedCapability',header,'only commerce module version1 is supported');
 const imports:CommerceSourceImport[]=[],aliases=new Map<string,string>();
 for(const use of children(syntax,'import-line')){let inherited:string|undefined;for(const item of children(use,'qualified-name')){
  let qualified=text(item);if(qualified.includes('.'))inherited=qualified.slice(0,qualified.lastIndexOf('.'));else if(inherited)qualified=inherited+'.'+qualified;else sourceFail('UnknownReference',item,'first grouped import must be qualified');
  const dot=qualified.lastIndexOf('.'),name=qualified.slice(dot+1),owner=qualified.slice(0,dot);if(aliases.has(name))sourceFail('DuplicateSymbol',item,'duplicate imported alias '+name);aliases.set(name,qualified);imports.push({module:owner,name,alias:name,span:span(item)});
 }}
 const declarations:CommerceDeclarationSource[]=[],seen=new Set<string>();let entries=0;
 for(const wrapper of children(syntax,'declaration')){
  const node=wrapper.children.find((x):x is CommerceSyntax=>'kind'in x)??sourceFail('Syntax',wrapper,'missing declaration');let kind=roles[node.kind]??sourceFail('UnsupportedCapability',node,'unknown declaration role');
  if(node.kind==='record-declaration')kind=({'entity':'Entity','value-object':'ValueObject','event':'Event'} as const)[tokens(node)[0]!.text as 'entity']??sourceFail('Syntax',node,'unknown record kind');
  const ts=tokens(node),local=kind==='Entry'?text(children(node,'qualified-name')[0]!):ts[1]!.text,id=kind==='Entry'?local:module+'.'+local;
  if(seen.has(local)||kind!=='Entry'&&aliases.has(local))sourceFail('DuplicateSymbol',node,'declaration/import alias collision '+local);seen.add(local);
  if(id.length>256)sourceFail('ResourceLimit',node,'qualified declaration name exceeds256');
  if(kind==='Entry'){if(++entries>COMMERCE_SOURCE_LIMITS.entries)sourceFail('ResourceLimit',node,'too many entries');}else if(declarations.length-entries>=COMMERCE_SOURCE_LIMITS.declarations)sourceFail('ResourceLimit',node,'too many declarations');
  const base={id,local_name:local,module,syntax:node,span:span(node)};
  if(kind==='Entity'||kind==='ValueObject'||kind==='Event'){
   const clauses=children(node,'record-clause'),refinement=clauses.some(c=>tokens(c)[0]?.text==='carrier'&&children(c,'refinement-clause').length),fields:CommerceSourceField[]=[],identity:string[]=[],unique:string[][]=[],immutable:string[]=[];let all=false;const singletons=new Set<string>();
   for(const clause of clauses){const head=tokens(clause)[0]!.text;
    if(['identity','immutable','carrier','representation','unicode','utf8-bytes','unicode-scalars','pattern','equality','normalization','case-fold','trim'].includes(head)){if(singletons.has(head))sourceFail('DuplicateSymbol',clause,'duplicate record/refinement clause '+head);singletons.add(head);}
    if(head==='identity')identity.push(...nameList(child(clause,'name-list')));
    else if(head==='unique')unique.push(nameList(child(clause,'name-list')));
    else if(head==='immutable'){if(tokens(clause)[1]?.text==='all')all=true;else immutable.push(...nameList(child(clause,'name-list')));}
    else if(children(clause,'type').length){if(refinement)sourceFail('InvalidContract',clause,'transparent scalar cannot also declare record fields');fields.push(field(clause));}
   }
   const names=new Set<string>();for(const f of fields){if(names.has(f.name))sourceFail('DuplicateSymbol',f.span,'duplicate field '+f.name);names.add(f.name);}
   if(fields.length>64)sourceFail('ResourceLimit',node,'record field bound exceeded');
   declarations.push({...base,kind,fields,refinement,identity,unique,immutable:all?'all':immutable,invariants:clauses.flatMap(c=>tokens(c)[0]?.text==='invariant'?children(c,'expression'):[])} satisfies CommerceRecordSource);
  }else if(kind==='Enum'){
   const labels=new Set<string>(),wires=new Set<string>(),forms=new Set<string>();const variants=children(node,'enum-item').map(item=>{const t=tokens(item),name=t[1]!.text;forms.add(t[0]!.text);if(labels.has(name))sourceFail('DuplicateSymbol',item,'duplicate enum variant '+name);labels.add(name);const fields:CommerceSourceField[]=[];
    for(const type of children(item,'type')){const before=t.findIndex(v=>v.start===type.start&&v.end>=type.start),name=t[before-1]!.text;fields.push({name,type:commerceSourceType(type),span:span(type)});}
    if(new Set(fields.map(f=>f.name)).size!==fields.length)sourceFail('DuplicateSymbol',item,'duplicate enum payload field');const wire=t.findIndex(v=>v.text==='wire'),value=wire<0?null:JSON.parse(t[wire+1]!.text) as string;if(wires.has(value??name))sourceFail('DuplicateSymbol',item,'duplicate enum wire value');wires.add(value??name);return {name,wire:value,fields,span:span(item)};});
   if(forms.size>1)sourceFail('InvalidContract',node,'enum cannot mix nullary-value and payload-variant wire forms');
   if(variants.length>64)sourceFail('ResourceLimit',node,'enum variant bound exceeded');declarations.push({...base,kind,variants});
  }else if(kind==='Interface'){
   const clauses=children(node,'interface-clause');declarations.push({...base,kind,interface_kind:text(child(node,'interface-kind')),clauses,exposes:clauses.flatMap(c=>tokens(c)[0]?.text==='exposes'?nameList(child(c,'name-list')):[])});
  }else if(kind==='Entry'){
   const names=children(node,'qualified-name'),interaction=ts.findIndex(t=>t.text==='interaction'),clauses=children(node,'access-clause');const access:CommerceSyntax={kind:'entry-access',children:Object.freeze(clauses),path:node.path,start:clauses[0]?.start??node.start,end:clauses.at(-1)?.end??node.end};
   declarations.push({...base,kind,invokes:text(names[1]!),interaction:ts[interaction+1]!.text as 'request-response'|'event',access});
  }else if(kind==='FormalClaim'){
   const lang=ts.findIndex(t=>t.text==='language');declarations.push({...base,kind,language:ts[lang+1]!.text as CommerceClaimSource['language'],reference:text(child(node,'reference')),targets:nameList(child(node,'name-list'))});
  }else{
   const inputs=children(node,'parameter').map(field),contexts=children(node,'context').map(field);let result:CommerceSourceType|null=null;
   if(kind==='Rule')result={kind:'scalar',name:'Bool'};
   else if(kind==='StateMachine'){const types=children(node,'type');inputs.push({name:'state',type:commerceSourceType(types[0]!),span:span(types[0]!)},{name:'event',type:commerceSourceType(types[1]!),span:span(types[1]!)});result={kind:'outcome',state:inputs[0]!.type,intent:{kind:'scalar',name:'Bool'},max_intents:0};}
   else {const type=children(node,'type')[0]??['local-query','delegated-query','native-inspect-body'].flatMap(k=>children(node,k).flatMap(q=>children(q,'type')))[0];if(type)result=commerceSourceType(type);}
   const bindings=new Set<string>();for(const f of [...inputs,...contexts]){if(bindings.has(f.name))sourceFail('DuplicateSymbol',f.span,'duplicate parameter/context '+f.name);bindings.add(f.name);}
   if(inputs.length>128||contexts.length>16)sourceFail('ResourceLimit',node,'parameter/context bound exceeded');
   declarations.push({...base,kind,inputs,contexts,result,body:node} satisfies CommerceCallableSource);
  }
 }
 return freeze({schema_version:'alchlang.commerce-source-syntax/v1-candidate',module,version:1,path:relativePath,text:source,sha256:createHash('sha256').update(source).digest('hex'),bytes:Buffer.byteLength(source),imports,declarations,syntax,authority_effect:'none'});
}
export function tryParseCommerceModuleSource(text:string,relativePath:string):CommerceResult<CommerceParsedModule>{try{return {ok:true,value:parseCommerceModuleSource(text,relativePath)};}catch(error){if(error instanceof CommerceSourceError)return {ok:false,diagnostics:error.diagnostics};throw error;}}
