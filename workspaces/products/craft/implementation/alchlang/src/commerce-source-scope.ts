/** Source-local binding and nominal pattern resolution. This deliberately does
 * not issue Core semantic/native/application owners. Open Questions: EC06/CONTEXT.md. */
import {commerceSourceType} from './commerce-source-parser.js';
import {parseCommerceExpression} from './commerce-source-expression.js';
import {commerceSyntaxChildren as children,commerceSyntaxChild as child,commerceSyntaxDescendants as descendants,commerceSyntaxText as text,commerceSyntaxTokens as tokens,sourceFail,
 type CommerceDeclarationSource,type CommerceCallableSource,type CommerceSyntax,type CommerceSourceType,type CommerceSourceSpan} from './commerce-source-model.js';
import type {CommerceLinkedDeclaration,CommerceLinkedReference} from './commerce-source-link.js';
type Type=CommerceSourceType|{kind:'view';fields:ReadonlyMap<string,Type>}|{kind:'list-view'|'optional-view';element:Type}|{kind:'variant-view';enum_name:string;variant:string;fields:ReadonlyMap<string,Type>}|{kind:'unknown'};
type Env=Map<string,Type>;
interface Flow {last?:Type;nearestRead?:string;persisted?:boolean}
export interface CommerceScopeContext {
 readonly declarations:readonly CommerceLinkedDeclaration[];
 readonly contracts?:ReadonlyMap<string,unknown>;
 readonly application?:string;
 resolve(name:string,module:string,span:CommerceSourceSpan):CommerceDeclarationSource;
 reference(reference:CommerceLinkedReference):void;
}
const U:Type={kind:'scalar',name:'UInt64'},B:Type={kind:'scalar',name:'Bool'},unknown:Type={kind:'unknown'};
const isCallable=(d:CommerceDeclarationSource):d is CommerceCallableSource=>'inputs'in d;
const span=(n:CommerceSyntax):CommerceSourceSpan=>({path:n.path,start:n.start,end:n.end});
export function linkCommerceBodyScopes(context:CommerceScopeContext):void {
 const byId=new Map(context.declarations.map(d=>[d.declaration.id,d]));
 const applications=context.declarations.map(r=>r.declaration).filter(d=>d.kind==='Interface'&&d.interface_kind==='application-composition'&&(!context.application||d.id===context.application));
 const valueDomainOwner=():string|undefined=>{
  if(applications.length!==1)return undefined;const clause=descendants(applications[0]!.syntax,'application-clause').find(c=>tokens(c)[0]?.text==='value-domain'),reference=clause?children(clause,'reference')[0]:undefined;if(!reference)return undefined;
  const contract=context.contracts?.get(text(reference).split('#')[0]!);if(!contract||typeof contract!=='object'||!('source_module'in contract)||typeof contract.source_module!=='string')return undefined;const match=/^(.+)@1$/.exec(contract.source_module);return match?.[1];
 };
 for(const linked of context.declarations){
  const d=linked.declaration;if(d.kind==='Enum'||d.kind==='Interface'||d.kind==='FormalClaim')continue;
  const qualify=(t:Type,at:CommerceSourceSpan):Type=>{
   if(t.kind==='named')return {kind:'named',name:context.resolve(t.name,d.module,at).id};
   if(t.kind==='optional'||t.kind==='list')return {...t,element:qualify(t.element,at) as CommerceSourceType};
   if(t.kind==='outcome')return {...t,state:qualify(t.state,at) as CommerceSourceType,intent:qualify(t.intent,at) as CommerceSourceType};return t;
  };
  const resolve=(name:string,at:CommerceSourceSpan)=>context.resolve(name,d.module,at);
  const ref=(kind:CommerceLinkedReference['kind'],target:string,at:CommerceSourceSpan)=>context.reference({kind,source:d.id,target,span:at});
  const bind=(env:Env,name:string,type:Type,at:CommerceSourceSpan)=>{if(env.has(name))sourceFail('DuplicateSymbol',at,'binding shadows an existing source name '+name);env.set(name,type);ref('value-binding',d.id+'.'+name,at);};
  const nativeSlice=(owner:CommerceDeclarationSource,heads:readonly string[]):unknown=>{
   if(owner.kind!=='Interface')return undefined;const clause=owner.clauses.find(c=>heads.includes(tokens(c)[0]?.text??''));if(!clause)return undefined;
   const node=descendants(clause,'reference')[0];if(!node)return undefined;const [file,fragment='']=text(node).split('#'),directory=owner.span.path.slice(0,owner.span.path.lastIndexOf('/')+1),key=file!.includes('/')?file!:directory+file;let value=context.contracts?.get(key);
   for(const part of fragment.replace(/^\//,'').split('/').filter(Boolean)){if(!value||typeof value!=='object'||!Object.hasOwn(value,part))return undefined;value=(value as Record<string,unknown>)[part];}return value;
  };
  const annotation=(value:unknown,owner:CommerceDeclarationSource,at:CommerceSourceSpan):Type=>{
   if(typeof value!=='string')return sourceFail('TypeMismatch',at,'declared native source type required');
   if(value==='UInt64')return U;if(value==='Bool')return B;if(value==='String')return {kind:'string'};
   if(value.startsWith('schema:')){const match=/^schema:([A-Za-z_][A-Za-z0-9_.]*)@1$/.exec(value);if(!match)sourceFail('UnsupportedCapability',at,'unsupported native schema selector/version');return {kind:'named',name:context.resolve(match![1]!,owner.module,at).id};}
   const optional=/^optional<(.+)>$/.exec(value);if(optional)return {kind:'optional-view',element:annotation(optional[1],owner,at)};
   const list=/^List<(.+),([0-9]+)>$/.exec(value);if(list)return {kind:'list-view',element:annotation(list[1],owner,at)};
   return {kind:'named',name:context.resolve(value,owner.module,at).id};
  };
  const element=(t:Type):Type|undefined=>t.kind==='optional'||t.kind==='list'||t.kind==='optional-view'||t.kind==='list-view'?t.element:undefined;
  const member=(t:Type,name:string,at:CommerceSourceSpan):Type=>{
   if(t.kind==='optional'||t.kind==='optional-view')return member(t.element,name,at); // Namespace lookup only; Core checks optional-flow safety.
   if(t.kind==='view'||t.kind==='variant-view'){const f=t.fields.get(name);if(!f)sourceFail('UnknownReference',at,'unknown field '+name);return f;}
   if(t.kind==='outcome'){if(name==='state')return t.state;if(name==='intents')return {kind:'list-view',element:t.intent};if(['tag','machine','branch','reason'].includes(name))return {kind:'string'};return sourceFail('UnknownReference',at,'unknown proposal field '+name);}
   if(t.kind==='named'){
    const owner=byId.get(t.name);if(!owner)return sourceFail('UnknownReference',at,'unknown named field owner '+t.name);
    const field=owner.fields.find(f=>f.name===name);if(field){ref('field',owner.declaration.id+'.'+name,at);return field.type;}
    if(owner.declaration.kind==='Interface'){const properties=nativeSlice(owner.declaration,['fields']);if(properties&&typeof properties==='object'&&Object.hasOwn(properties,name)){ref('field',owner.declaration.id+'.'+name,at);return annotation((properties as Record<string,unknown>)[name],owner.declaration,at);}}
    return sourceFail('UnknownReference',at,'unknown field '+t.name+'.'+name);
   }
   return sourceFail(t.kind==='unknown'?'AmbiguousReference':'TypeMismatch',at,'field has no resolved record/proposal owner');
  };
  const enumType=(t:Type,at:CommerceSourceSpan)=>{if(t.kind==='named'){const e=byId.get(t.name)?.declaration;if(e?.kind==='Enum')return e;}return sourceFail('AmbiguousReference',at,'pattern requires its actual declared subject enum');};
  const symbolValue=(name:string,env:Env,at:CommerceSourceSpan,expected?:Type,persisted=false):Type=>{
   const exact=env.get(name);if(exact)return exact;
   const parts=name.split('.'),root=env.get(parts[0]!);if(root){let value=root;for(const key of parts.slice(1))value=member(value,key,at);return value;}
   if(expected?.kind==='named'){const owner=byId.get(expected.name)?.declaration;if(owner?.kind==='Enum'&&!name.includes('.')){if(!owner.variants.some(v=>v.name===name))sourceFail('UnknownReference',at,'unknown contextual enum value '+name);ref('enum-constructor',owner.id+'.'+name,at);return expected;}}
   for(let n=parts.length-1;n>0;n--){let owner:CommerceDeclarationSource;try{owner=resolve(parts.slice(0,n).join('.'),at);}catch{continue;}
    if(owner.kind==='Enum'){const tag=parts[n]!,variant=owner.variants.find(v=>v.name===tag);if(!variant)sourceFail('UnknownReference',at,'unknown enum constructor '+name);if(n!==parts.length-1)sourceFail('UnknownReference',at,'constructor selector has trailing fields');ref('enum-constructor',owner.id+'.'+tag,at);return variant!.fields.length?{kind:'variant-view',enum_name:owner.id,variant:tag,fields:new Map(variant!.fields.map(f=>[f.name,annotationType(f.type,owner,at)]))}:{kind:'named',name:owner.id};}
    if(persisted&&'fields'in owner){let value:Type={kind:'named',name:owner.id};for(const key of parts.slice(n))value=member(value,key,at);return value;}
   }
   return sourceFail('UnknownReference',at,'unbound source value '+name);
  };
  const annotationType=(t:CommerceSourceType,owner:CommerceDeclarationSource,at:CommerceSourceSpan):Type=>{
   if(t.kind==='named')return {kind:'named',name:context.resolve(t.name,owner.module,at).id};
   if(t.kind==='optional')return {kind:'optional-view',element:annotationType(t.element,owner,at)};if(t.kind==='list')return {kind:'list-view',element:annotationType(t.element,owner,at)};return t;
  };
  const patternEnvs=(list:CommerceSyntax,t:Type,env:Env):Env[]=>children(list,'pattern').map(pattern=>{
   const ts=tokens(pattern),out=new Map(env),name=text(children(pattern,'qualified-name')[0]??pattern).replace(/\(.*/,''),first=ts[0]!.text;
   if(t.kind==='scalar'&&t.name==='Bool'){if(!['true','false'].includes(first)||ts.length!==1)sourceFail('TypeMismatch',pattern,'Bool pattern must be true/false');return out;}
   const owner=enumType(t,pattern),parts=name.split('.'),tag=parts.at(-1)!;
   if(parts.length>1){const explicit=resolve(parts.slice(0,-1).join('.'),pattern);if(explicit.id!==owner.id)sourceFail('TypeMismatch',pattern,'pattern belongs to a different enum');}
   const variant=owner.variants.find(v=>v.name===tag);if(!variant)sourceFail('UnknownReference',pattern,'variant is absent from actual subject enum '+owner.id+'.'+tag);ref('enum-pattern',owner.id+'.'+tag,pattern);
   const open=ts.findIndex(v=>v.text==='(');if(open>=0){const name=ts[open+1]!.text;if(!variant!.fields.length)sourceFail('TypeMismatch',pattern,'nullary pattern has no payload binder');const type:Type=variant!.fields.length===1?annotationType(variant!.fields[0]!.type,owner,pattern):{kind:'view',fields:new Map(variant!.fields.map(f=>[f.name,annotationType(f.type,owner,pattern)]))};bind(out,name,type,pattern);}
   return out;
  });
  const argumentExpressions=(node:CommerceSyntax)=>{const args=children(node,'arguments')[0];return args?children(args,'expression').concat(children(args,'named-argument').map(a=>child(a,'expression'))):[];};
  const infer=(node:CommerceSyntax,env:Env,expected?:Type,flow:Flow={}):Type=>{
   const cs=node.children.filter((c):c is CommerceSyntax=>'kind'in c),ts=tokens(node).filter(t=>t.layout===null),head=ts[0]?.text;
   if(node.kind==='qualified-name')return symbolValue(text(node),env,node,expected,flow.persisted);
   if(node.kind==='natural')return U;
   if(node.kind==='json-string')return {kind:'literal',value:JSON.parse(ts[0]!.text) as string};
   if(node.kind==='primary'){
    if(head==='true'||head==='false')return B;if(head==='none')return expected??{kind:'optional-view',element:unknown};
    return cs.length?infer(cs[0]!,env,expected,flow):unknown;
   }
   if(node.kind==='postfix'){if(/^[A-Za-z_][A-Za-z0-9_]*(\.[A-Za-z_][A-Za-z0-9_]*)*$/.test(text(node)))return symbolValue(text(node),env,node,expected,flow.persisted);let value=infer(cs[0]!,env,expected,flow);for(let i=1;i<node.children.length;i++){const current=node.children[i]!;if('text'in current&&current.text==='.')value=member(value,(node.children[++i] as {text:string}).text,node);}return value;}
   if(node.kind==='invocation'){
    const name=text(child(node,'callable')),args=argumentExpressions(node),rootName=name.split('.')[0]!,root=env.get(rootName);
    if(['some','require-some','require-variant','length','length-utf8','length-scalars','tag','present','absent','all-unique-exact','checked-add','checked-subtract','checked-multiply','checked-divide'].includes(name)){
     const values=args.map((a,i)=>infer(a,env,i===0&&name==='some'?element(expected??unknown):undefined,flow));
     if(name==='some')return {kind:'optional-view',element:values[0]??unknown};if(name==='require-some')return element(values[0]??unknown)??values[0]??unknown;
     if(name==='require-variant'){const selected=values[1];if(selected?.kind!=='variant-view')sourceFail('TypeMismatch',node,'require-variant needs an explicit payload variant selector');return selected;}
     if(['present','absent','all-unique-exact'].includes(name))return B;if(name==='tag')return {kind:'string'};return U;
    }
    if(root&&name.includes('.')){
     if(root.kind!=='named')return sourceFail('TypeMismatch',node,'native context needs declared Interface type');const owner=byId.get(root.name)?.declaration;if(!owner)return sourceFail('UnknownReference',node,'missing context owner');const methods=nativeSlice(owner,['methods','signatures']),method=methods&&typeof methods==='object'?(methods as Record<string,unknown>)[name.slice(rootName.length+1)]:undefined;if(!method||typeof method!=='object'||!('result'in method))sourceFail('UnknownReference',node,'missing native method signature');for(const arg of args)infer(arg,env,undefined,flow);return annotation(method.result,owner,node);
    }
    let target:CommerceDeclarationSource|undefined,variant:string|undefined;const parts=name.split('.');if(parts.length>1){try{const prefix=resolve(parts.slice(0,-1).join('.'),node);if(prefix.kind==='Enum'||prefix.kind==='StateMachine'&&parts.at(-1)==='propose'){target=prefix;variant=prefix.kind==='Enum'?parts.at(-1):undefined;}}catch{}}
    target??=resolve(name,node);if(target.kind==='Entry')target=resolve(target.invokes,node);
    let parameters:readonly {name:string;type:CommerceSourceType}[]=[],result:Type=unknown;
    if(target.kind==='Enum'){const selected=target.variants.find(v=>v.name===variant);if(!selected)sourceFail('UnknownReference',node,'unknown enum constructor');parameters=selected!.fields;result={kind:'named',name:target.id};}
    else if('fields'in target){parameters=target.fields;result={kind:'named',name:target.id};}
    else if(isCallable(target)){parameters=target.inputs;result=byId.get(target.id)?.result??unknown;}
    const argNode=children(node,'arguments')[0],named=argNode?children(argNode,'named-argument'):[];
    if(args.length!==parameters.length)sourceFail('MissingMapping',node,'call arguments differ from resolved source signature');
    if(named.length){const names=named.map(n=>tokens(n)[0]!.text);if(new Set(names).size!==names.length)sourceFail('DuplicateSymbol',node,'duplicate named argument');if(names.some(name=>!parameters.some(p=>p.name===name)))sourceFail('MissingMapping',node,'unknown named argument');}
    ref('call',target.id+(variant?'.'+variant:''),node);
    for(let i=0;i<args.length;i++){const parameter=named.length?parameters.find(p=>p.name===tokens(named[i]!)[0]!.text):parameters[i];infer(args[i]!,env,parameter?annotationType(parameter.type,target,node):undefined,flow);}return result;
   }
   if(['map-expression','filter-expression','fold-expression','indexed-fold-expression','repeat-expression','condition-loop-expression','range-expression','sort-expression'].includes(node.kind)){
    const expr=children(node,'expression'),binders=children(node,'binder'),inner=new Map(env);for(const binder of binders){const type=qualify(commerceSourceType(child(binder,'type')),binder);bind(inner,tokens(binder)[0]!.text,type,binder);}
    if(node.kind==='range-expression'){for(const e of expr)infer(e,env,U,flow);return {kind:'list-view',element:U};}
    if(node.kind==='map-expression'||node.kind==='filter-expression'){const source=infer(expr[0]!,env,undefined,flow),body=infer(expr[1]!,inner,undefined,flow);return node.kind==='map-expression'?{kind:'list-view',element:body}:source;}
    if(node.kind==='sort-expression'){const source=infer(expr[0]!,env,undefined,flow);for(const key of descendants(node,'sort-key'))infer(child(key,'expression'),inner,undefined,flow);if(!binders.length){const comma=node.children.findIndex(c=>'text'in c&&c.text===','),key=node.children[comma+1];if(key&&'text'in key)member(element(source)??sourceFail('TypeMismatch',node,'sort needs bounded collection'),key.text,key);}return source;}
    const initialIndex=node.kind==='fold-expression'||node.kind==='indexed-fold-expression'||node.kind==='repeat-expression'?1:0;for(let i=0;i<expr.length;i++)infer(expr[i]!,i>initialIndex?inner:env,undefined,flow);return infer(expr[initialIndex]!,env,expected,flow);
   }
   if(node.kind==='list-expression'){const values=children(node,'expression').map(e=>infer(e,env,element(expected??unknown),flow));return {kind:'list-view',element:values[0]??element(expected??unknown)??unknown};}
   if(node.kind==='optional-match'){
    const expressions=children(node,'expression'),subject=infer(expressions[0]!,env,undefined,flow),inner=new Map(env),all=tokens(node),at=all.findIndex(t=>t.text==='some');bind(inner,all[at+2]!.text,element(subject)??sourceFail('TypeMismatch',node,'some pattern requires optional subject'),node);const value=infer(expressions[1]!,inner,expected,flow);infer(expressions[2]!,env,expected,flow);return value;
   }
   if(node.kind==='inline-match'){
    const subject=infer(child(node,'postfix'),env,undefined,flow),expressions=children(node,'expression'),scopes=patternEnvs(child(node,'pattern-list'),subject,env);let result:Type=unknown;for(const scope of scopes)result=infer(expressions[0]!,scope,expected,flow);infer(expressions[1]!,env,expected,flow);return result;
   }
   if(node.kind==='expression-value'&&children(node,'match-case').length){
    const subject=infer(child(node,'expression'),env,undefined,flow);let result:Type=unknown;for(const branch of children(node,'match-case')){const patterns=children(branch,'pattern-list')[0];for(const scope of patterns?patternEnvs(patterns,subject,env):[env])result=infer(child(branch,'expression'),scope,expected,flow);}return result;
   }
   if(['comparison','sum','product','conjunction','disjunction','implication','unary'].includes(node.kind)&&cs.length){
    const first=infer(cs[0]!,env,expected,flow);for(const item of cs.slice(1))infer(item,env,node.kind==='comparison'?first:expected,flow);
    if(cs.length>1||node.kind==='unary'&&head==='not')return ['sum','product'].includes(node.kind)?U:B;return first;
   }
   if(cs.length===1)return infer(cs[0]!,env,expected,flow);let result:Type=unknown;for(const c of cs)result=infer(c,env,expected,flow);return result;
  };
  const root=new Map<string,Type>();for(const f of [...linked.fields,...linked.inputs,...linked.contexts])bind(root,f.name,f.type,f.span);
  let durableState:Type|undefined;
  const workflowSteps=new Set<string>(),workflowTerminals=new Set<string>();
  const namedAfter=(node:CommerceSyntax,word:string)=>{const ts=tokens(node),at=ts.findIndex(t=>t.text===word),token=ts[at+1];return token?descendants(node,'qualified-name').find(q=>q.start===token.start):undefined;};
  const driverSignature=(node:CommerceSyntax,result:CommerceSyntax,type:Type)=>{
   const name=child(node,'qualified-name'),entry=resolve(text(name),name);if(entry.kind!=='Entry')sourceFail('TypeMismatch',name,'workflow driver/step must invoke a declared entry');const signature=byId.get(entry.invokes);if(!signature)sourceFail('UnknownReference',name,'workflow entry target missing');
   const inputs=children(node,'driver-input'),names=inputs.map(i=>tokens(i)[1]!.text);if(new Set(names).size!==names.length)sourceFail('DuplicateSymbol',node,'duplicate workflow input');if(names.length!==signature.inputs.length||names.some(n=>!signature.inputs.some(i=>i.name===n)))sourceFail('MissingMapping',node,'workflow arguments differ from original entry inputs');
   if(JSON.stringify(type)!==JSON.stringify(signature.result))sourceFail('TypeMismatch',result,'workflow result annotation differs from actual entry result');ref('call',entry.id,name);
  };
  const walk=(node:CommerceSyntax,env:Env,flow:Flow):void=>{
   const kind=node.kind,ts=tokens(node),head=ts[0]?.text;
   if(['expression','expression-value','invocation'].includes(kind)){infer(node,env,undefined,flow);return;}
   if(kind==='let-statement'){const expression=children(node,'expression')[0],value=expression?infer(expression,env,undefined,flow):U;for(const handler of children(node,'action'))walk(handler,new Map(env),{...flow});bind(env,ts[1]!.text,value,node);flow.last=value;return;}
   if(kind==='read-statement'){
    const local=children(node,'qualified-name')[0],call=children(node,'invocation')[0];for(const binding of children(node,'bindings'))walk(binding,env,flow);let value:Type=local?{kind:'named',name:resolve(text(local),local).id}:infer(call!,env,undefined,flow);
    for(const handler of children(node,'read-handler'))walk(handler,new Map(env),{...flow});const missing=children(node,'read-handler').some(h=>tokens(h)[0]?.text==='on-missing');if(missing)value=element(value)??value;else if(local)value={kind:'optional-view',element:value};bind(env,ts[1]!.text,value,node);flow.last=value;flow.nearestRead=ts[1]!.text;return;
   }
   if(kind==='call-statement'){const value=infer(child(node,'invocation'),env,undefined,flow);for(const handler of children(node,'call-handler'))walk(handler,new Map(env),{...flow});bind(env,ts[1]!.text,value,node);flow.last=value;return;}
   if(kind==='condition-statement'){
    const patterns=children(node,'pattern-list')[0],subject=children(node,'postfix')[0],expressions=children(node,'expression');
    if(patterns&&!subject&&children(patterns,'pattern').length===1){
     const pattern=child(patterns,'pattern'),q=children(pattern,'qualified-name')[0],name=q?text(q):'';let predicate=env.has(name.split('.')[0]!);
     if(!predicate&&name){try{const target=resolve(name,pattern),result=byId.get(target.id)?.result;predicate=['Rule','Calculation','Mapping','Policy'].includes(target.kind)&&!!result&&result.kind==='scalar'&&result.name==='Bool';}catch{}}
     if(predicate){const value=infer(parseCommerceExpression(tokens(patterns)),env,undefined,flow);if(value.kind!=='scalar'||value.name!=='Bool')sourceFail('TypeMismatch',pattern,'conditional source value must be Bool');walk(child(node,'action'),new Map(env),{...flow});return;}
    }
    const scopes=patterns?patternEnvs(patterns,subject?infer(subject,env,undefined,flow):flow.last??unknown,env):[env];
    for(const scope of scopes){for(const e of expressions)infer(e,scope,undefined,flow);walk(child(node,'action'),scope,{...flow});}return;
   }
   if(kind==='present-statement'){
    const subject=children(node,'postfix')[0],name=subject?text(subject):flow.nearestRead;if(!name)sourceFail('AmbiguousReference',node,'on-present has no preceding read/explicit subject');const value=subject?infer(subject,env,undefined,flow):env.get(name!);if(!value)sourceFail('UnknownReference',node,'missing present subject');const scope=new Map(env);if(!name!.includes('.'))scope.set(name!,element(value!)??value!);for(const c of node.children)if('kind'in c&&c!==subject)walk(c,scope,{...flow});return;
   }
   if(kind==='read-set'){
    const source=infer(child(node,'expression'),env,undefined,flow),inner=new Map(env);bind(inner,ts[ts.findIndex(t=>t.text==='for')+1]!.text,element(source)??sourceFail('TypeMismatch',node,'read-set needs bounded collection'),node);walk(child(node,'operation-statements'),inner,{...flow});const fields=new Map<string,Type>();
    for(const binding of children(child(node,'collected-bindings'),'collected-binding')){const name=tokens(binding)[0]!.text,expression=children(binding,'expression')[0];fields.set(name,expression?infer(expression,inner,undefined,flow):inner.get(name)??sourceFail('UnknownReference',binding,'unknown collected binding'));}bind(env,ts[1]!.text,{kind:'list-view',element:{kind:'view',fields}},node);return;
   }
   if(kind==='transaction'){
    const inner=new Map(env);for(const statement of children(node,'transaction-statement')){const handler=children(statement,'transaction-handler')[0];walk(handler??statement,handler?new Map(env):inner,{...flow});}for(const [name,type]of inner)if(!env.has(name))env.set(name,type);return;
   }
   if(kind==='mutation'){
    const target=resolve(text(child(node,'qualified-name')),node),fields=byId.get(target.id)!.fields;for(const binding of children(node,'bindings'))walk(binding,env,flow);for(const expression of children(node,'expression'))infer(expression,env,undefined,flow);
    for(const assignment of children(child(node,'assignments'),'expression')){const before=tokens(child(node,'assignments')).filter(t=>t.start<assignment.start),field=fields.find(f=>f.name===before.at(-2)?.text);infer(assignment,env,field?.type,flow);}
    const prior=env.get(ts[1]!.text),previous=prior&&(prior.kind==='optional'||prior.kind==='optional-view')?prior.element:undefined;
    // A transaction-local created row may reuse its outer optional read name;
    // it never overwrites the outer read binding or permits a second local let.
    if(previous?.kind==='named'&&previous.name===target.id)env.delete(ts[1]!.text);
    bind(env,ts[1]!.text,{kind:'named',name:target.id},node);return;
   }
   if(kind==='transaction-loop'){const value=infer(child(node,'expression'),env,undefined,flow),inner=new Map(env);bind(inner,ts[1]!.text,element(value)??sourceFail('TypeMismatch',node,'transaction loop needs collection'),node);for(const statement of children(node,'transaction-statement'))walk(statement,inner,{...flow});return;}
   if(kind==='when-statement'||kind==='transaction-condition'){
    infer(child(node,'expression'),env,undefined,flow);let branch=new Map(env);for(const c of node.children){if('text'in c&&c.text==='otherwise')branch=new Map(env);else if('kind'in c&&c.kind!=='expression')walk(c,branch,{...flow});}return;
   }
   if(kind==='local-query'){
    for(const q of children(node,'qualified-name')){const previous=ts.findIndex(t=>t.start===q.start),name=ts[previous-1]!.text;bind(env,name,{kind:'named',name:resolve(text(q),q).id},q);}for(const c of node.children)if('kind'in c&&['expression','query-clause'].includes(c.kind))walk(c,env,flow);return;
   }
   if(kind==='snapshot-driver'||kind==='claim-driver'||kind==='observation-driver'){
    const driverEnv=new Map(env);if(kind==='observation-driver'){const entryNode=children(node,'qualified-name')[0]!,entry=resolve(text(entryNode),entryNode),operation=entry.kind==='Entry'?resolve(entry.invokes,node):entry,observation=byId.get(operation.id)?.inputs.find(p=>p.name==='observation');driverEnv.set('step',{kind:'view',fields:new Map([['observation',observation?.type??unknown]])});}
    for(const input of children(node,'driver-input'))infer(child(input,'expression'),driverEnv,undefined,flow);const result=child(node,'driver-result'),name=tokens(result)[1]!.text,type=qualify(commerceSourceType(child(result,'type')),result);driverSignature(node,result,type);bind(env,name,type,result);driverEnv.set(name,type);for(const c of node.children)if('kind'in c&&!['driver-input','driver-result','qualified-name'].includes(c.kind))walk(c,driverEnv,{...flow});return;
   }
   if(kind==='remote-step'){
    for(const input of children(node,'driver-input'))infer(child(input,'expression'),env,undefined,flow);const result=child(node,'driver-result'),type=qualify(commerceSourceType(child(result,'type')),result),inner=new Map(env);driverSignature(node,result,type);bind(inner,tokens(result)[1]!.text,type,result);
    for(const branch of children(node,'step-branch')){for(const target of children(branch,'step-name'))if(!workflowSteps.has(text(target)))sourceFail('UnknownReference',target,'unknown workflow continuation step');const patterns=children(branch,'pattern-list')[0];for(const branchEnv of patterns?patternEnvs(patterns,type,inner):[new Map(inner)])for(const c of branch.children)if('kind'in c&&c.kind!=='pattern-list')walk(c,branchEnv,{...flow});}return;
   }
   if(kind==='local-step'){for(const target of children(node,'step-name'))if(!workflowSteps.has(text(target)))sourceFail('UnknownReference',target,'unknown workflow local continuation');for(const expression of children(node,'expression'))infer(expression,env,undefined,flow);return;}
   if(kind==='workflow-step'){for(const c of node.children)if('kind'in c&&['remote-step','local-step','review-step'].includes(c.kind))walk(c,new Map(env),{...flow,persisted:c.kind==='review-step'});return;}
   if(kind==='workflow-terminal'){for(const expression of children(node,'expression'))infer(expression,env,undefined,{...flow,persisted:true});return;}
   if(kind==='resume-case'){if(!durableState)sourceFail('MissingMapping',node,'workflow durable entity has no state field');symbolValue(text(child(node,'qualified-name')),env,node,durableState);for(const expression of children(node,'expression'))infer(expression,env,undefined,flow);for(const action of children(node,'workflow-action'))walk(action,env,flow);return;}
   if(kind==='workflow-action'){
    const values=ts.filter(t=>t.layout===null).map(t=>t.text),first=values[0]!;
    if(first==='finish'){if(!workflowTerminals.has(values[1]!))sourceFail('UnknownReference',node,'unknown workflow terminal');}
    else if(first==='suspend'){const state=values.slice(1).join('');if(!['same-state','ownership-unresolved','needs-review'].includes(state))symbolValue(state,env,node,durableState);}
    else if(!['resume','stop-this-worker'].includes(first)&&!workflowSteps.has(first))sourceFail('UnknownReference',node,'unknown workflow step');return;
   }
   // Native/replay protocol text consists of finite registered clauses, not
   // implicit variable references. Only their actual expression nodes recurse.
   for(const c of node.children)if('kind'in c)walk(c,env,flow);
  };
  if(d.kind==='Entry'){
   const operation=resolve(d.invokes,d.span),signature=byId.get(operation.id)!;root.set('input',{kind:'view',fields:new Map(signature.inputs.map(p=>[p.name,p.type]))});for(const c of signature.contexts)root.set(c.name,c.type);
   const resourceNames=new Set<string>();for(const clause of children(d.access,'access-clause'))if(tokens(clause)[0]?.text==='resource-binding'){
    const ts=tokens(clause),typeNode=child(clause,'qualified-name'),name=text(typeNode);let type:Type|undefined;
    if(resourceNames.has(ts[1]!.text))sourceFail('DuplicateSymbol',clause,'duplicate resource binding');resourceNames.add(ts[1]!.text);
    try{type={kind:'named',name:resolve(name,typeNode).id};}catch{
     const resource=child(clause,'reference'),abi=text(resource).split('#')[0];
     for(const candidate of context.declarations){const owner=candidate.declaration;if(owner.kind!=='Interface'||owner.interface_kind!=='trusted-context')continue;const abiClause=owner.clauses.find(c=>tokens(c)[0]?.text==='abi'),declaredAbi=abiClause?descendants(abiClause,'reference')[0]:undefined;if(!declaredAbi||text(declaredAbi)!==abi)continue;
      const variants=nativeSlice(owner,['variants']),variant=variants&&typeof variants==='object'?(variants as Record<string,unknown>)[name]:undefined;if(!variant||typeof variant!=='object'||!('fields'in variant)||!variant.fields||typeof variant.fields!=='object')continue;
      const module=valueDomainOwner();if(!module)sourceFail('MissingMapping',resource,'private projection requires the selected declared value-domain owner');type={kind:'view',fields:new Map(Object.entries(variant.fields).map(([key,value])=>[key,annotation(value,{...owner,module},resource)]))};ref('type',owner.id+'.'+name,typeNode);break;
     }
     if(!type)sourceFail('UnknownReference',typeNode,'unknown source type or registered private projection '+name);
    }
    const old=root.get(ts[1]!.text);if(old&&JSON.stringify(old)!==JSON.stringify(type))sourceFail('DuplicateSymbol',clause,'resource binding changes an existing context');root.set(ts[1]!.text,type!);
   }
   for(const clause of children(d.access,'access-clause'))for(const expression of children(clause,'expression'))infer(expression,root);continue;
  }
  if(d.kind==='Workflow'){
   const durable=namedAfter(d.syntax,'durable-state');if(!durable)sourceFail('MissingMapping',d.span,'workflow durable state selector missing');const type:Type={kind:'named',name:resolve(text(durable!),durable!).id};durableState=member(type,'state',durable!);
   for(const step of children(d.syntax,'workflow-step')){const name=text(child(step,'step-name'));if(workflowSteps.has(name))sourceFail('DuplicateSymbol',step,'duplicate workflow step');workflowSteps.add(name);}
   for(const terminal of children(d.syntax,'workflow-terminal')){const name=text(child(terminal,'step-name'));if(workflowTerminals.has(name))sourceFail('DuplicateSymbol',terminal,'duplicate workflow terminal');workflowTerminals.add(name);}
   if(workflowSteps.size>64||workflowTerminals.size>16)sourceFail('ResourceLimit',d.span,'workflow step/terminal bound exceeded');walk(d.syntax,root,{});continue;
  }
  if(d.kind==='StateMachine'){
   const state=linked.inputs[0]!.type,event=linked.inputs[1]!.type,initial=namedAfter(d.syntax,'initial');if(initial)symbolValue(text(initial),root,initial,state);
   for(const names of children(d.syntax,'name-list'))for(const q of children(names,'qualified-name'))symbolValue(text(q),root,q,state);
   for(const transition of children(d.syntax,'machine-transition')){const names=children(transition,'qualified-name');for(let i=0;i<names.length;i++)symbolValue(text(names[i]!),root,names[i]!,i===1?event:state);for(const guard of children(transition,'expression'))infer(guard,root);}continue;
  }
  if('invariants'in d){for(const invariant of d.invariants)infer(invariant,root);continue;}
  walk(d.syntax,root,{});
 }
}
