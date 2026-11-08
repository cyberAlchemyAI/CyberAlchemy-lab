/** Deterministic expression precedence over grammar-validated source tokens.
 * Open Questions: EC06/CONTEXT.md. This builds syntax; it evaluates no business code. */
import {sourceFail,type CommerceSyntax,type CommerceToken} from './commerce-source-model.js';
const rank:Readonly<Record<string,number>>={implies:1,or:2,and:3,'==':4,'!=':4,'<':4,'<=':4,'>':4,'>=':4,in:4,'+':5,'-':5,'*':6,'/':6};
const family:Readonly<Record<string,string>>={implies:'implication',or:'disjunction',and:'conjunction','==':'comparison','!=':'comparison','<':'comparison','<=':'comparison','>':'comparison','>=':'comparison',in:'comparison','+':'sum','-':'sum','*':'product','/':'product'};
export function parseCommerceExpression(input:readonly CommerceToken[]):CommerceSyntax {
 const list=input.filter(t=>t.layout===null);let at=0,nodes=0,depth=0;
 const here=()=>list[at]??list.at(-1)??{path:'application.alch',start:0,end:0};
 const peek=()=>list[at]?.text;
 const take=()=>list[at++]??sourceFail('Syntax',here(),'missing expression token');
 const expect=(value:string)=>{const token=take();if(token.text!==value)sourceFail('Syntax',token,'expected '+value+' in expression');return token;};
 const node=(kind:string,children:readonly (CommerceSyntax|CommerceToken)[]):CommerceSyntax=>{
  if(++nodes>8192)sourceFail('ResourceLimit',here(),'expression syntax node bound exceeded');const first=children[0]??here(),last=children.at(-1)??first;return Object.freeze({kind,path:first.path,start:first.start,end:last.end,children:Object.freeze([...children])});
 };
 const qname=()=>{const values:CommerceToken[]=[take()];if(!/^[A-Za-z_][A-Za-z0-9_-]*$/.test(values[0]!.text))sourceFail('Syntax',values[0]!,'qualified name required');while(peek()==='.'){values.push(take());const next=take();if(!/^[A-Za-z_][A-Za-z0-9_]*$/.test(next.text))sourceFail('Syntax',next,'member name required');values.push(next);}return node('qualified-name',values);};
 const type=():CommerceSyntax=>{
  const parts:(CommerceSyntax|CommerceToken)[]=[];if(peek()==='literal'){parts.push(take(),take());return node('type',parts);}
  parts.push(qname());if(peek()==='<'){parts.push(take(),type());while(peek()===','){parts.push(take());parts.push(/^[0-9]+$/.test(peek()??'')?take():type());}parts.push(expect('>'));}return node('type',parts);
 };
 const binder=()=>node('binder',[take(),expect(':'),type()]);
 const patterns=()=>{
  const values:(CommerceSyntax|CommerceToken)[]=[];
  for(;;){const parts:(CommerceSyntax|CommerceToken)[]=[qname()];if(peek()==='(')parts.push(take(),take(),expect(')'));values.push(node('pattern',parts));if(peek()!==',')break;values.push(take());}return node('pattern-list',values);
 };
 const expression=(minimum=0):CommerceSyntax=>{
  if(++depth>128)sourceFail('ResourceLimit',here(),'expression recursion bound exceeded');
  let left:CommerceSyntax;
  if(peek()==='match'){
   const first=take(),subject=expression(),parts:(CommerceSyntax|CommerceToken)[]=[first];
   if(peek()==='some'){parts.push(subject,take(),expect('('),take(),expect(')'),expect('=>'),expression(),expect('else'),expression());left=node('optional-match',parts);}
   else {parts.push(node('postfix',[subject]),patterns(),expect('=>'),expression(),expect('else'),expression());left=node('inline-match',parts);}
  }else if(peek()==='not')left=node('unary',[take(),expression(7)]);
  else if(peek()==='('){const open=take(),body=expression(),close=expect(')');left=node('primary',[open,body,close]);}
  else if(peek()==='['){const parts:(CommerceSyntax|CommerceToken)[]=[take()];if(peek()!==']')for(;;){parts.push(expression());if(peek()!==',')break;parts.push(take());}parts.push(expect(']'));left=node('list-expression',parts);}
  else if(/^[0-9]+$/.test(peek()??''))left=node('natural',[take()]);
  else if(peek()?.startsWith('"'))left=node('json-string',[take()]);
  else if(['true','false','none'].includes(peek()??''))left=node('primary',[take()]);
  else {
   const name=qname(),word=(name.children[0] as CommerceToken).text;
   if(peek()!=='(')left=name;
   else if(['map','filter','fold','indexed-fold','repeat','while-bounded','until-bounded','range','sort'].includes(word)){
    const parts:(CommerceSyntax|CommerceToken)[]=[...name.children,expect('(')];
    if(word==='map'||word==='filter'){parts.push(expression(),expect(','),binder(),expect('=>'),expression());}
    else if(word==='fold'||word==='indexed-fold'){parts.push(expression(),expect(','),expression(),expect(','),binder(),expect(','),binder());if(word==='indexed-fold')parts.push(expect(','),binder());parts.push(expect('=>'),expression());}
    else if(word==='repeat'){parts.push(expression(),expect(','),expect('max'),node('natural',[take()]),expect(','),expression(),expect(','),binder(),expect(','),binder(),expect('=>'),expression());}
    else if(word==='while-bounded'||word==='until-bounded'){parts.push(expect('max'),node('natural',[take()]),expect(','),expression(),expect(','),binder(),expect(','),expression(),expect('=>'),expression());}
    else if(word==='range'){parts.push(expression(),expect(','),expression(),expect(','),expression(),expect(','),expect('max'),node('natural',[take()]));}
    else {
     parts.push(expression(),expect(','));if(list[at+1]?.text===':'){
      parts.push(binder(),expect('=>'),expect('['));for(;;){const value=expression(),direction=node('direction',[take()]),mode=node('sort-mode',[take()]);parts.push(node('sort-key',[value,direction,mode]));if(peek()!==',')break;parts.push(take());}parts.push(expect(']'));
     }else parts.push(take(),node('direction',[take()]),node('sort-mode',[take()]));
    }
    parts.push(expect(')'));const kind=word==='while-bounded'||word==='until-bounded'?'condition-loop-expression':word==='indexed-fold'?'indexed-fold-expression':word+'-expression';left=node(kind,parts);
   }else {
    const open=take(),arguments_:(CommerceSyntax|CommerceToken)[]=[];
    if(peek()!==')')for(;;){if(list[at+1]?.text==='='){arguments_.push(node('named-argument',[take(),take(),expression()]));}else arguments_.push(expression());if(peek()!==',')break;arguments_.push(take());}
    const close=expect(')');left=node('invocation',[node('callable',[name]),open,...(arguments_.length?[node('arguments',arguments_)]:[]),close]);
   }
  }
  while(peek()==='.'){const dot=take(),member=take();left=node('postfix',[node('primary',[left]),dot,member]);}
  while(rank[peek()??'']!==undefined&&rank[peek()!]!>=minimum){const operator=take(),value=rank[operator.text]!,right=expression(value+(operator.text==='implies'?0:1));left=node(family[operator.text]!,[left,operator,right]);}
  depth--;return node('expression',[left]);
 };
 const result=expression();if(at!==list.length)sourceFail('Syntax',here(),'unexpected trailing expression token');return result;
}
