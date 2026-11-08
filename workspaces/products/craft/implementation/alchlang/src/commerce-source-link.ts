/** Namespace, signature, source-role and dependency linking. Independent Core
 * semantic checking still precedes generation. Open Questions: EC06/CONTEXT.md. */
import {COMMERCE_SOURCE_LIMITS} from './commerce-source-lexer.js';
import {linkCommerceBodyScopes} from './commerce-source-scope.js';
import {commerceSyntaxChildren as children,commerceSyntaxChild as child,commerceSyntaxDescendants as descendants,commerceSyntaxText as text,commerceSyntaxTokens as tokens,sourceFail,
 type CommerceDeclarationSource,type CommerceParsedModule,type CommerceSourceField,type CommerceSourceSpan,type CommerceSourceType,type CommerceRecordSource,type CommerceCallableSource,type CommerceSyntax} from './commerce-source-model.js';
export interface CommerceLinkedReference {readonly kind:'import'|'type'|'entry'|'export'|'local-table'|'enum-constructor'|'call'|'enum-pattern'|'value-binding'|'field'|'claim';readonly source:string;readonly target:string;readonly span:CommerceSourceSpan}
export interface CommerceLinkedDeclaration {readonly declaration:CommerceDeclarationSource;readonly fields:readonly CommerceSourceField[];readonly inputs:readonly CommerceSourceField[];readonly contexts:readonly CommerceSourceField[];readonly result:CommerceSourceType|null}
export interface CommerceLinkedSource {readonly schema_version:'alchlang.commerce-source-link/v1-candidate';readonly modules:readonly CommerceParsedModule[];readonly declarations:readonly CommerceLinkedDeclaration[];readonly references:readonly CommerceLinkedReference[];readonly exports:readonly {readonly module:string;readonly names:readonly string[]}[];readonly services:readonly {readonly id:string;readonly module:string}[];readonly type_dependencies:readonly {readonly source:string;readonly target:string}[];readonly authority_effect:'none'}
const callable=(d:CommerceDeclarationSource):d is CommerceCallableSource=>'inputs'in d;
const record=(d:CommerceDeclarationSource):d is CommerceRecordSource=>'refinement'in d;
const location=(d:CommerceDeclarationSource|CommerceSyntax):CommerceSourceSpan=>'span'in d?d.span:{path:d.path,start:d.start,end:d.end};
export function linkCommerceSourceModules(modules:readonly CommerceParsedModule[],application?:string,contracts?:ReadonlyMap<string,unknown>):CommerceLinkedSource {
 if(!modules.length||modules.length>COMMERCE_SOURCE_LIMITS.modules)sourceFail('ResourceLimit',{path:'application.alch',start:0,end:0},'bounded nonempty module closure required');
 const byModule=new Map<string,CommerceParsedModule>(),symbols=new Map<string,CommerceDeclarationSource>(),references:CommerceLinkedReference[]=[],aliases=new Map<string,Map<string,string>>();
 for(const module of modules){if(byModule.has(module.module))sourceFail('DuplicateSymbol',module.syntax,'duplicate module identity '+module.module);byModule.set(module.module,module);for(const d of module.declarations){if(symbols.has(d.id))sourceFail('DuplicateSymbol',d.span,'duplicate global symbol/entry '+d.id);symbols.set(d.id,d);}}
 const exposed=new Set<string>(),nativeExposed=new Set<string>();
 for(const d of symbols.values())if(d.kind==='Interface'){
  const names=new Set<string>();for(const name of d.exposes){if(names.has(name))sourceFail('DuplicateSymbol',d.span,'duplicate interface exposure');names.add(name);const target=symbols.get(name.includes('.')?name:d.module+'.'+name);
   if(!target||target.module!==d.module||!['Operation','Query','Workflow'].includes(target.kind))sourceFail('UnknownReference',d.span,'interface may expose only its original local callable');exposed.add(target.id);if(d.interface_kind==='external')nativeExposed.add(target.id);
  }
 }
 const composition=[...symbols.values()].filter(d=>d.kind==='Interface'&&d.interface_kind==='application-composition'&&(!application||d.id===application));
 if(application&&composition.length!==1)sourceFail('UnknownReference',modules[0]!.syntax,'one selected application-composition Interface required');
 const services:{id:string;module:string}[]=[];
 for(const d of composition)for(const clause of descendants(d.syntax,'application-clause')){const ts=tokens(clause);if(ts[0]?.text!=='service')continue;const module=text(child(clause,'qualified-name')),id=ts[1]!.text;if(!byModule.has(module))sourceFail('UnknownReference',clause,'service module is not captured '+module);if(services.some(s=>s.id===id||s.module===module))sourceFail('DuplicateSymbol',clause,'duplicate service identity/module');services.push({id,module});}
 const service=(module:string)=>services.filter(s=>module===s.module||module.startsWith(s.module+'.')).sort((a,b)=>b.module.length-a.module.length)[0]?.id??module;
 const resolve=(name:string,owner:string,at:CommerceSourceSpan):CommerceDeclarationSource=>{
  const local=symbols.get(owner+'.'+name);if(!name.includes('.')&&local)return local;
  const alias=aliases.get(owner)?.get(name);const target=alias?symbols.get(alias):symbols.get(name);
  if(!target)sourceFail('UnknownReference',at,'unknown local/imported/qualified source selector '+name);return target;
 };
 // Profile-owned coordination Entities have an explicit service owner in the
 // selected composition contract. Namespace placement alone does not own them.
 // This is a source link, never runtime authority or an implicit foreign-table grant.
 const coordinationOwners=new Map<string,string>();
 for(const d of composition){
  const clauses=descendants(d.syntax,'application-clause'),records=clauses.filter(c=>tokens(c)[0]?.text==='coordination-records');
  if(!records.length)continue;
  const refs=clauses.filter(c=>tokens(c)[0]?.text==='coordination-contract');
  if(records.length!==1||refs.length!==1)sourceFail('MissingMapping',d.span,'one coordination records/contract pair required');
  const ref=text(child(refs[0]!,'reference')),contract=contracts?.get(ref);
  const object=(v:unknown):v is Record<string,unknown>=>!!v&&typeof v==='object'&&!Array.isArray(v);
  if(!object(contract)||contract.schema_version!=='craft.commerce-application-composition/v1-candidate'||
     contract.application!==d.id||!object(contract.coordination))
   sourceFail('MissingMapping',refs[0]!,'captured application coordination contract required');
  const coordination=contract.coordination,owner=coordination.owner_service,selectors=coordination.schema_selectors;
  if(typeof owner!=='string'||!services.some(s=>s.id===owner)||!object(selectors))
   sourceFail('UnknownReference',refs[0]!,'coordination owner must be a selected service');
  const declared=new Set<string>();
  for(const q of children(child(records[0]!,'name-list'),'qualified-name')){
   const target=resolve(text(q),d.module,q);
   if(target.kind!=='Entity'||target.module!==d.module||!Object.values(selectors).includes(target.id))
    sourceFail('UnknownReference',q,'coordination record must be a local Entity selected by its contract');
   if(declared.has(target.id)||coordinationOwners.has(target.id))sourceFail('DuplicateSymbol',q,'duplicate coordination record ownership');
   declared.add(target.id);coordinationOwners.set(target.id,owner);
  }
  for(const name of Object.values(selectors)){
   if(typeof name!=='string')sourceFail('InvalidContract',refs[0]!,'coordination selectors must name declarations');
   const target=symbols.get(name);
   if(!target||target.module!==d.module)sourceFail('UnknownReference',refs[0]!,'coordination selector must name an application declaration');
   if(target.kind==='Entity'&&!declared.has(target.id))sourceFail('MissingMapping',records[0]!,'contract Entity missing from coordination records');
  }
 }
 const entityService=(target:CommerceDeclarationSource)=>coordinationOwners.get(target.id)??service(target.module);
 for(const module of modules){const map=new Map<string,string>();aliases.set(module.module,map);for(const use of module.imports){const target=symbols.get(use.module+'.'+use.name);if(!target)sourceFail('UnknownReference',use.span,'import target not captured '+use.module+'.'+use.name);if(map.has(use.alias))sourceFail('DuplicateSymbol',use.span,'duplicate alias '+use.alias);if(target.kind==='Entity'&&entityService(target)!==service(module.module))sourceFail('UnknownReference',use.span,'private foreign Entity import '+target.id);if(['Operation','Query'].includes(target.kind)&&target.module!==module.module&&!exposed.has(target.id))sourceFail('UnknownReference',use.span,'private helper cannot be imported');map.set(use.alias,target.id);references.push({kind:'import',source:module.module,target:target.id,span:use.span});}}
 const typeEdges:{source:string;target:string}[]=[];
 const qualify=(type:CommerceSourceType,d:CommerceDeclarationSource,at:CommerceSourceSpan,context=false):CommerceSourceType=>{
  if(type.kind==='named'){
   const target=resolve(type.name,d.module,at);if(!['Entity','ValueObject','Enum','Event','Interface'].includes(target.kind))sourceFail('TypeMismatch',at,'type reference names '+target.kind);
   if(target.kind==='Interface'&&!context)sourceFail('TypeMismatch',at,'private/native Interface is not a serializable value type');
   if(target.kind==='Entity'&&entityService(target)!==service(d.module))sourceFail('UnknownReference',at,'private foreign Entity type '+target.id);
   references.push({kind:'type',source:d.id,target:target.id,span:at});return {kind:'named',name:target.id};
  }
  if(type.kind==='optional'||type.kind==='list')return {...type,element:qualify(type.element,d,at,context)};
  if(type.kind==='outcome')return {...type,state:qualify(type.state,d,at,context),intent:qualify(type.intent,d,at,context)};return type;
 };
 const qualified:CommerceLinkedDeclaration[]=[];
 for(const d of symbols.values()){
  const fields=record(d)?d.fields.map(f=>({...f,type:qualify(f.type,d,f.span)})):[],inputs=callable(d)?d.inputs.map(f=>({...f,type:qualify(f.type,d,f.span)})):[],contexts=callable(d)?d.contexts.map(f=>({...f,type:qualify(f.type,d,f.span,true)})):[];
  const result=callable(d)&&d.result?qualify(d.result,d,d.span):null;
  if(d.kind==='Enum')for(const v of d.variants)for(const f of v.fields)qualify(f.type,d,f.span);
  if(record(d)){
   const names=new Set(d.fields.map(f=>f.name));for(const name of [...d.identity,...d.unique.flat(),...(d.immutable==='all'?[]:d.immutable)])if(!names.has(name))sourceFail('UnknownReference',d.span,'identity/unique/immutable references missing field '+name);
   if(d.kind==='Entity'&&!d.identity.length)sourceFail('MissingMapping',d.span,'Entity needs a declared identity');
  }
  qualified.push({declaration:d,fields,inputs,contexts,result});
  const dependencies=(type:CommerceSourceType)=>{if(type.kind==='named')typeEdges.push({source:d.id,target:type.name});else if(type.kind==='optional'||type.kind==='list')dependencies(type.element);else if(type.kind==='outcome'){dependencies(type.state);dependencies(type.intent);}};
  if(record(d))for(const f of fields)dependencies(f.type);
  if(d.kind==='Enum')for(const v of d.variants)for(const f of v.fields)dependencies(qualify(f.type,d,f.span));
  if(d.kind==='Entry'){
   const target=symbols.get(d.invokes);if(!target||!['Operation','Query','Workflow'].includes(target.kind))sourceFail('UnknownReference',d.span,'entry target must be a captured Operation/Query/Workflow');if(target.kind!=='Workflow'&&!exposed.has(target.id))sourceFail('UnknownReference',d.span,'entry cannot expose a private helper');references.push({kind:'entry',source:d.id,target:target.id,span:d.span});
  }
  if(d.kind==='FormalClaim')for(const name of d.targets){const target=resolve(name,d.module,d.span);if(target.kind==='FormalClaim')sourceFail('TypeMismatch',d.span,'formal claim must target a model declaration or entry');references.push({kind:'claim',source:d.id,target:target.id,span:d.span});}
  if(d.kind==='Interface')for(const name of d.exposes){const target=resolve(name,d.module,d.span);if(!['Operation','Query','Workflow'].includes(target.kind))sourceFail('TypeMismatch',d.span,'Interface exposes noncallable '+name);references.push({kind:'export',source:d.id,target:target.id,span:d.span});}
 }
 const tables=(d:CommerceDeclarationSource,node:CommerceSyntax,expected:'Entity'|'Event')=>{for(const q of children(node,'qualified-name')){const target=resolve(text(q),d.module,q);if(target.kind!==expected)sourceFail('TypeMismatch',q,'expected '+expected+' selector');if(expected==='Entity'&&entityService(target)!==service(d.module))sourceFail('UnknownReference',q,'cross-service private table access '+target.id);references.push({kind:'local-table',source:d.id,target:target.id,span:location(q)});}};
 const pureKinds=new Set(['Rule','Calculation','Mapping','Policy','StateMachine']),intrinsics=new Set(['checked-add','checked-subtract','checked-multiply','checked-divide','some','present','absent','require-some','require-variant','length','length-utf8','length-scalars','tag','all-unique-exact']);
 const pureCalls:{source:string;target:string}[]=[],localCalls:{source:string;target:string}[]=[];
 const arity=(invocation:CommerceSyntax,expected:readonly string[])=>{const args=children(invocation,'arguments')[0],named=args?children(args,'named-argument'):[],count=args?(named.length||children(args,'expression').length):0;if(named.length){const names=named.map(n=>tokens(n)[0]!.text);if(new Set(names).size!==names.length)sourceFail('DuplicateSymbol',invocation,'duplicate named argument');if(names.length!==expected.length||names.some(n=>!expected.includes(n)))sourceFail('MissingMapping',invocation,'named arguments differ from declared signature');}else if(count!==expected.length)sourceFail('MissingMapping',invocation,'positional argument count differs from declared signature');};
 const contextMethods=(target:CommerceDeclarationSource)=>{
  if(target.kind!=='Interface')return undefined;const methodClause=target.clauses.find(c=>['methods','signatures'].includes(tokens(c)[0]?.text??''));if(!methodClause)return undefined;
  const ref=descendants(methodClause,'reference')[0];if(!ref)return undefined;const [file,fragment='']=text(ref).split('#');const directory=target.span.path.includes('/')?target.span.path.slice(0,target.span.path.lastIndexOf('/')+1):'';const key=file!.includes('/')?file!:directory+file;let value=contracts?.get(key);
  if(value===undefined)return undefined;for(const part of fragment.replace(/^\//,'').split('/').filter(Boolean)){if(!value||typeof value!=='object'||!Object.hasOwn(value,part))return undefined;value=(value as Record<string,unknown>)[part];}return value&&typeof value==='object'?value as Record<string,unknown>:undefined;
 };
 for(const d of symbols.values())if(callable(d)||record(d)||d.kind==='Entry'){
  const body=callable(d)?d.body:d.syntax,pureOwner=!callable(d)||pureKinds.has(d.kind),contextSource=d.kind==='Entry'?symbols.get(d.invokes):d,contexts=contextSource&&callable(contextSource)?contextSource.contexts:[];
  for(const query of descendants(body,'local-query'))tables(d,query,'Entity');
  for(const read of descendants(body,'read-statement'))tables(d,read,'Entity');
  for(const mutation of descendants(body,'mutation'))tables(d,mutation,tokens(mutation)[0]!.text==='record-event'?'Event':'Entity');
  for(const tx of descendants(body,'transaction'))for(const q of children(child(tx,'name-list'),'qualified-name')){const target=resolve(text(q),d.module,q);if(target.kind!=='Entity'||entityService(target)!==service(d.module))sourceFail('UnknownReference',q,'transaction participant is not a service-owned Entity');references.push({kind:'local-table',source:d.id,target:target.id,span:location(q)});}
  for(const invocation of descendants(body,'invocation')){
   const callee=text(child(invocation,'callable'));if(intrinsics.has(callee))continue;
   const segments=callee.split('.'),context=contexts.find(c=>c.name===segments[0]);
   if(context&&segments.length===2&&context.type.kind==='named'){
    if(pureOwner)sourceFail('UnsupportedCapability',invocation,'pure declaration cannot call native context');
    const target=resolve(context.type.name,d.module,context.span),methods=contextMethods(target),method=methods?.[segments[1]!];
    if(!methods||!method)sourceFail('UnknownReference',invocation,'unknown declared context method '+callee);
    if(method&&typeof method==='object'&&'parameters'in method&&Array.isArray(method.parameters))arity(invocation,method.parameters.map((p:unknown,i:number)=>p&&typeof p==='object'&&'name'in p?String(p.name):'argument'+i));
    references.push({kind:'call',source:d.id,target:target.id+'.'+segments[1],span:location(invocation)});continue;
   }
   let target:CommerceDeclarationSource|undefined,variant:string|undefined;
   if(segments.length>1){const prefix=segments.slice(0,-1).join('.'),member=segments.at(-1)!;try{const candidate=resolve(prefix,d.module,invocation);if(candidate.kind==='Enum'||candidate.kind==='StateMachine'&&member==='propose'){target=candidate;variant=candidate.kind==='Enum'?member:undefined;}}catch{}}
   target??=resolve(callee,d.module,invocation);
   if(target.kind==='Enum'){
    const item=target.variants.find(v=>v.name===variant);if(!item)sourceFail('UnknownReference',invocation,'unknown payload constructor '+callee);arity(invocation,item.fields.map(f=>f.name));
   }else if(record(target))arity(invocation,target.fields.map(f=>f.name));
   else if(target.kind==='Entry'){
    if(pureOwner)sourceFail('UnsupportedCapability',invocation,'pure declaration cannot invoke an entry');const operation=symbols.get(target.invokes);if(!operation||!callable(operation))sourceFail('UnknownReference',invocation,'entry target missing');arity(invocation,operation.inputs.map(f=>f.name));
   }else if(callable(target)){
    arity(invocation,target.inputs.map(f=>f.name));if(pureOwner&&!pureKinds.has(target.kind))sourceFail('UnsupportedCapability',invocation,'pure declaration calls effectful role');
    if(pureKinds.has(d.kind))pureCalls.push({source:d.id,target:target.id});
    else if(!pureKinds.has(target.kind)){if(target.module!==d.module&&!(nativeExposed.has(target.id)&&(descendants(target.syntax,'native-capture-body').length||descendants(target.syntax,'native-inspect-body').length)))sourceFail('UnknownReference',invocation,'cross-module call needs declared entry or selected external Interface');localCalls.push({source:d.id,target:target.id});}
   }else sourceFail('TypeMismatch',invocation,'source selector is not callable');
   references.push({kind:'call',source:d.id,target:target.id+(variant?'.'+variant:''),span:location(invocation)});
  }
  for(const q of [...descendants(body,'qualified-name'),...descendants(body,'postfix')]){
   const name=text(q),parts=name.split('.');if(parts.length<2||!/^[A-Za-z_][A-Za-z0-9_]*(\.[A-Za-z_][A-Za-z0-9_]*)+$/.test(name))continue;const prefix=parts.slice(0,-1).join('.'),member=parts.at(-1)!;let target:CommerceDeclarationSource|undefined;
   try{target=resolve(prefix,d.module,q);}catch{continue;}
   if(target.kind==='Enum'){if(!target.variants.some(v=>v.name===member))sourceFail('UnknownReference',q,'unknown enum constructor '+name);references.push({kind:'enum-constructor',source:d.id,target:target.id+'.'+member,span:location(q)});}
   else if(member==='propose'&&target.kind==='StateMachine')references.push({kind:'call',source:d.id,target:target.id,span:location(q)});
  }
 }
 const visit=(edges:readonly {source:string;target:string}[],label:string)=>{const adjacency=new Map<string,string[]>();for(const e of edges){const values=adjacency.get(e.source)??[];values.push(e.target);adjacency.set(e.source,values);}const active=new Set<string>(),done=new Set<string>();const walk=(name:string,depth:number)=>{if(active.has(name))sourceFail('InvalidContract',symbols.get(name)!.span,label+' cycle at '+name);if(done.has(name))return;if(depth>32)sourceFail('ResourceLimit',symbols.get(name)?.span??modules[0]!.syntax,label+' depth exceeded');active.add(name);for(const next of adjacency.get(name)??[])walk(next,depth+1);active.delete(name);done.add(name);};for(const name of adjacency.keys())walk(name,0);};
 visit(typeEdges,'value/type');
 visit(pureCalls,'pure call');visit(localCalls,'local call');
 linkCommerceBodyScopes({declarations:qualified,contracts,application,resolve,reference:r=>references.push(r)});
 const exported=[...byModule.keys()].map(module=>({module,names:[...symbols.values()].filter(d=>d.module===module&&['ValueObject','Enum','Event','Rule','Calculation','Mapping','Policy','StateMachine','Interface'].includes(d.kind)).map(d=>d.id).concat(references.filter(r=>r.kind==='export'&&symbols.get(r.source)?.module===module).map(r=>r.target)).sort()}));
 const result:CommerceLinkedSource={schema_version:'alchlang.commerce-source-link/v1-candidate',modules:[...modules],declarations:qualified,references,exports:exported,services,type_dependencies:typeEdges,authority_effect:'none'};
 const freeze=(v:unknown):void=>{if(v&&typeof v==='object'&&!Object.isFrozen(v)){for(const child of Object.values(v))freeze(child);Object.freeze(v);}};freeze(result);return result;
}
