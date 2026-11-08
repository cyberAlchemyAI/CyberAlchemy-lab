/** Core-owned pure expression source parser. No Alch CST or evaluator is used.
 * Only produces syntax; expected types and existing ExprV1 lowering are separate.
 * Open Questions: docs/COMMERCE-CONTRACTS.md#open-questions. */
import {coreSourceTokens,coreSourceChildren,coreSourceChild,coreSourceFail as fail,coreFreeze,type CoreSourceNode,type CoreSourceRange,type CoreSourceToken} from './commerce-core-syntax.js';
import type {CoreCommerceType} from './commerce-core-reconstruction.js';
export interface CoreLambda {readonly name:string;readonly type:CoreCommerceType;readonly span:CoreSourceRange}
export interface CorePattern {readonly name:string;readonly binding:string|null;readonly span:CoreSourceRange}
export type CoreExpression=CoreSourceRange&(
 {readonly kind:'number'|'string'|'Bool';readonly value:string}|
 {readonly kind:'none'}|{readonly kind:'name';readonly name:string}|
 {readonly kind:'field';readonly value:CoreExpression;readonly field:string}|
 {readonly kind:'invoke';readonly name:string;readonly args:readonly {readonly name:string|null;readonly value:CoreExpression}[]}|
 {readonly kind:'binary';readonly operator:string;readonly left:CoreExpression;readonly right:CoreExpression}|
 {readonly kind:'not';readonly value:CoreExpression}|{readonly kind:'list';readonly items:readonly CoreExpression[]}|
 {readonly kind:'map'|'filter';readonly source:CoreExpression;readonly item:CoreLambda;readonly body:CoreExpression}|
 {readonly kind:'fold'|'indexed-fold';readonly source:CoreExpression;readonly initial:CoreExpression;readonly state:CoreLambda;readonly item:CoreLambda;readonly index:CoreLambda|null;readonly body:CoreExpression}|
 {readonly kind:'repeat';readonly count:CoreExpression;readonly maximum:number;readonly initial:CoreExpression;readonly state:CoreLambda;readonly index:CoreLambda;readonly body:CoreExpression}|
 {readonly kind:'while-bounded'|'until-bounded';readonly maximum:number;readonly initial:CoreExpression;readonly state:CoreLambda;readonly guard:CoreExpression;readonly body:CoreExpression}|
 {readonly kind:'range';readonly first:CoreExpression;readonly last:CoreExpression;readonly step:CoreExpression;readonly maximum:number}|
 {readonly kind:'sort';readonly source:CoreExpression;readonly item:CoreLambda|null;readonly keys:readonly {readonly value:CoreExpression|string;readonly direction:'asc'|'desc';readonly mode:'numeric'|'lexical'|'natural'}[]}|
 {readonly kind:'match';readonly value:CoreExpression;readonly cases:readonly {readonly patterns:readonly CorePattern[];readonly body:CoreExpression}[];readonly otherwise:CoreExpression|null}
);
const range=(n:CoreSourceRange):CoreSourceRange=>({path:n.path,start:n.start,end:n.end});
const precedences:Readonly<Record<string,number>>={implies:1,or:2,and:3,'==':4,'!=':4,'<':4,'<=':4,'>':4,'>=':4,in:4,'+':5,'-':5,'*':6,'/':6};
function readType(peek:()=>string|undefined,take:()=>string,where:CoreSourceRange,depth=0):CoreCommerceType {
 if(depth>32)fail('ResourceLimit',where,'binder type nesting');const expect=(t:string)=>{if(take()!==t)fail('Syntax',where,'type delimiter '+t+' expected');},first=take();
 const nested=()=>readType(peek,take,where,depth+1),bound=(min:number)=>{const value=take();if(!/^(0|[1-9][0-9]*)$/.test(value)||BigInt(value)<BigInt(min)||BigInt(value)>100n)fail('ResourceLimit',where,'finite type bound');return Number(value);};
 if(first==='UInt64'||first==='Bool'||first==='String')return {kind:first};
 if(first==='optional'){expect('<');const value=nested();expect('>');return {kind:'optional',value};}
 if(first==='List'){expect('<');const value=nested();expect(',');const maximum=bound(1);expect('>');return {kind:'List',value,maximum};}
 if(first==='literal')return {kind:'literal',value:JSON.parse(take()) as string};
 if(first==='outcome'){expect('<');const state=nested();expect(',');const intent=nested();expect(',');const maximum=bound(0);expect('>');return {kind:'outcome',state,intent,maximum};}
 if(!/^[A-Za-z_][A-Za-z0-9_-]*$/.test(first))fail('Syntax',where,'named type expected');let name=first;while(peek()==='.'){take();const part=take();if(!/^[A-Za-z_][A-Za-z0-9_-]*$/.test(part))fail('Syntax',where,'qualified type expected');name+='.'+part;}return {kind:'named',name};
}
export function parseCoreTypeTokens(original:readonly CoreSourceToken[],where:CoreSourceRange):CoreCommerceType {
 const ts=original.filter(t=>!t.layout);let at=0;const value=readType(()=>ts[at]?.token,()=>ts[at++]?.token??fail('Syntax',where,'type source ended'),where);if(at!==ts.length)fail('Syntax',where,'trailing type tokens');return coreFreeze(value);
}
export function parseCoreExpressionTokens(original:readonly CoreSourceToken[],where:CoreSourceRange):CoreExpression {
 const ts=original.filter(t=>!t.layout);let at=0,depth=0,nodes=0;
 const peek=()=>ts[at]?.token;
 const take=()=>ts[at++]??fail('Syntax',where,'unexpected expression end');
 const expect=(word:string)=>{if(take().token!==word)fail('Syntax',where,'expression expected '+word);};
 const named=()=>{const t=take();if(!/^[A-Za-z_][A-Za-z0-9_-]*$/.test(t.token))fail('Syntax',t,'source name expected');return t.token;};
 const qualified=()=>{let name=named();while(peek()==='.'){at++;name+='.'+named();}return name;};
 const maximum=()=>{expect('max');const n=take();if(!/^[1-9][0-9]*$/.test(n.token)||BigInt(n.token)>100n)fail('ResourceLimit',n,'loop maximum must be 1..100');return Number(n.token);};
 const type=():CoreCommerceType=>readType(peek,()=>take().token,where);
 const binder=():CoreLambda=>{const start=ts[at]??where,name=named();expect(':');const value=type();return {name,type:value,span:{path:where.path,start:start.start,end:ts[at-1]!.end}};};
 const pattern=():CorePattern=>{const start=ts[at]??where,name=qualified();let binding:string|null=null;if(peek()==='('){at++;binding=named();expect(')');}return {name,binding,span:{path:where.path,start:start.start,end:ts[at-1]!.end}};};
 const construct=<T extends {readonly kind:CoreExpression['kind']}>(start:CoreSourceRange,value:T):CoreExpression=>{
  if(++nodes>4096)fail('ResourceLimit',where,'expression node limit');return {...value,path:where.path,start:start.start,end:ts[at-1]?.end??start.end} as unknown as CoreExpression;
 };
 const directions=()=>{const n=take();if(n.token!=='ascending'&&n.token!=='descending')fail('Syntax',n,'sort direction expected');return n.token==='ascending'?'asc' as const:'desc' as const;};
 const mode=()=>{const n=take();if(!['numeric','lexical','natural','binary-utf8'].includes(n.token))fail('Syntax',n,'registered sort mode expected');return n.token==='binary-utf8'?'lexical' as const:n.token as 'numeric'|'lexical'|'natural';};
 const primary=():CoreExpression=>{
  const first=take(),w=first.token;
  if(w==='('){const value=expression(0);expect(')');return value;}
  if(w==='['){const items:CoreExpression[]=[];if(peek()!==']')for(;;){items.push(expression(0));if(peek()!==',')break;at++;}expect(']');return construct(first,{kind:'list',items});}
  if(w==='none')return construct(first,{kind:'none'});
  if(w==='true'||w==='false')return construct(first,{kind:'Bool',value:w});
  if(/^[0-9]+$/.test(w))return construct(first,{kind:'number',value:w});
  if(w.startsWith('"'))return construct(first,{kind:'string',value:JSON.parse(w) as string});
  if(w==='not')return construct(first,{kind:'not',value:postfix()});
  if(w==='match'){
   const value=expression(0),patterns=[pattern()];while(peek()===','){at++;patterns.push(pattern());}expect('=>');const body=expression(0);expect('else');const otherwise=expression(0);return construct(first,{kind:'match',value,cases:[{patterns,body}],otherwise});
  }
  if(w==='map'||w==='filter'){expect('(');const source=expression(0);expect(',');const item=binder();expect('=>');const body=expression(0);expect(')');return construct(first,{kind:w,source,item,body});}
  if(w==='fold'||w==='indexed-fold'){expect('(');const source=expression(0);expect(',');const initial=expression(0);expect(',');const state=binder();expect(',');const item=binder();let index:CoreLambda|null=null;if(w==='indexed-fold'){expect(',');index=binder();}expect('=>');const body=expression(0);expect(')');return construct(first,{kind:w,source,initial,state,item,index,body});}
  if(w==='repeat'){expect('(');const count=expression(0);expect(',');const max=maximum();expect(',');const initial=expression(0);expect(',');const state=binder();expect(',');const index=binder();expect('=>');const body=expression(0);expect(')');return construct(first,{kind:'repeat',count,maximum:max,initial,state,index,body});}
  if(w==='while-bounded'||w==='until-bounded'){expect('(');const max=maximum();expect(',');const initial=expression(0);expect(',');const state=binder();expect(',');const guard=expression(0);expect('=>');const body=expression(0);expect(')');return construct(first,{kind:w,maximum:max,initial,state,guard,body});}
  if(w==='range'){expect('(');const firstValue=expression(0);expect(',');const last=expression(0);expect(',');const step=expression(0);expect(',');const max=maximum();expect(')');return construct(first,{kind:'range',first:firstValue,last,step,maximum:max});}
  if(w==='sort'){
   expect('(');const source=expression(0);expect(',');let item:CoreLambda|null=null;const keys:{value:CoreExpression|string;direction:'asc'|'desc';mode:'numeric'|'lexical'|'natural'}[]=[];
   if(ts[at+1]?.token===':'){item=binder();expect('=>');expect('[');for(;;){const value=expression(0),direction=directions(),m=mode();keys.push({value,direction,mode:m});if(peek()!==',')break;at++;}expect(']');}
   else {const value=named(),direction=directions(),m=mode();keys.push({value,direction,mode:m});}expect(')');return construct(first,{kind:'sort',source,item,keys});
  }
  if(!/^[A-Za-z_][A-Za-z0-9_-]*$/.test(w))fail('Syntax',first,'expression value expected');
  let name=w;while(peek()==='.'){at++;name+='.'+named();}
  if(peek()!=='(')return construct(first,{kind:'name',name});
  at++;const args:{name:string|null;value:CoreExpression}[]=[];if(peek()!==')')for(;;){let name:string|null=null;if(ts[at+1]?.token==='='){name=named();expect('=');}args.push({name,value:expression(0)});if(peek()!==',')break;at++;}expect(')');return construct(first,{kind:'invoke',name,args});
 };
 const postfix=():CoreExpression=>{let value=primary();while(peek()==='.'){at++;const field=named();value=construct(value,{kind:'field',value,field});}return value;};
 const expression=(minimum:number):CoreExpression=>{
  if(++depth>128)fail('ResourceLimit',where,'expression source depth');let left=postfix();
  for(;;){const op=peek()??'',priority=precedences[op];if(priority===undefined||priority<minimum)break;at++;const right=expression(op==='implies'?priority:priority+1);left=construct(left,{kind:'binary',operator:op,left,right});}
  depth--;return left;
 };
 const value=expression(0);if(at!==ts.length)fail('Syntax',ts[at]!,'trailing expression source');return coreFreeze(value);
}
export function parseCoreExpression(node:CoreSourceNode):CoreExpression {return parseCoreExpressionTokens(coreSourceTokens(node),node);}
export function parseCoreExpressionValue(node:CoreSourceNode):CoreExpression {
 const inline=coreSourceChildren(node,'expression');if(coreSourceTokens(node)[0]?.token!=='match')return parseCoreExpression(inline[0]??node);
 const cases=coreSourceChildren(node,'match-case');if(!cases.length)return parseCoreExpression(inline[0]??node);
 const value=parseCoreExpression(inline[0]!),branches:{patterns:CorePattern[];body:CoreExpression}[]= [];let otherwise:CoreExpression|null=null;
 for(const c of cases){if(otherwise)fail('InvalidContract',c,'otherwise must be the last match case');const body=parseCoreExpression(coreSourceChild(c,'expression')),patterns=coreSourceChildren(c,'pattern-list').flatMap(p=>coreSourceChildren(p,'pattern')).map(p=>({name:coreSourceChildren(p,'qualified-name').length?coreSourceTokens(coreSourceChild(p,'qualified-name')).map(t=>t.token).join(''):coreSourceTokens(p)[0]!.token,binding:coreSourceTokens(p).findIndex(t=>t.token==='(')<0?null:coreSourceTokens(p).at(-2)!.token,span:range(p)}));
  if(coreSourceTokens(c)[0]?.token==='otherwise'){if(otherwise)fail('DuplicateSymbol',c,'duplicate match otherwise');otherwise=body;}else branches.push({patterns,body});
 }
 return coreFreeze({...range(node),kind:'match' as const,value,cases:branches,otherwise});
}
