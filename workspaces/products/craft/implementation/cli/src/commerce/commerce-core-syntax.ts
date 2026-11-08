/** Independent Core recognizer: interprets Core EBNF expressions directly with
 * memoized endpoint sets, rather than accepting an Alch CST/role DTO.
 * Syntax is data, never a checked application or native owner.
 * Open Questions: docs/COMMERCE-CONTRACTS.md#open-questions. */
import {createHash} from 'node:crypto';
import {CORE_COMMERCE_GRAMMAR as grammar,CORE_COMMERCE_RESERVED as reserved,type CoreGrammarNode} from './commerce-core-grammar.js';
import type {CommerceDiagnostic} from './commerce-stages-v1.js';

export interface CoreSourceRange {readonly path:string;readonly start:number;readonly end:number}
export interface CoreSourceToken extends CoreSourceRange {readonly token:string;readonly layout:'NEWLINE'|'INDENT'|'DEDENT'|null}
export interface CoreSourceNode extends CoreSourceRange {readonly rule:string;readonly children:readonly (CoreSourceNode|CoreSourceToken)[]}
export class CoreCommerceSourceError extends Error {
 readonly diagnostics:readonly CommerceDiagnostic[];
 constructor(code:CommerceDiagnostic['code'],range:CoreSourceRange,message:string){super(`${code}: ${range.path}:${range.start}: ${message}`);this.name='CoreCommerceSourceError';this.diagnostics=Object.freeze([Object.freeze({code,path:range.path,start:range.start,end:range.end,message:Buffer.from(message).subarray(0,4096).toString('utf8')})]);}
}
export function coreSourceFail(code:CommerceDiagnostic['code'],range:CoreSourceRange,message:string):never {throw new CoreCommerceSourceError(code,range,message);}
export function coreSourceChildren(node:CoreSourceNode,rule:string):CoreSourceNode[]{return node.children.filter((c):c is CoreSourceNode=>'rule'in c&&c.rule===rule);}
export function coreSourceDescendants(node:CoreSourceNode,rule:string):CoreSourceNode[]{const out:CoreSourceNode[]=[],stack=[node];while(stack.length){const n=stack.pop()!;if(n.rule===rule)out.push(n);for(let i=n.children.length-1;i>=0;i--){const c=n.children[i]!;if('rule'in c)stack.push(c);}}return out;}
export function coreSourceTokens(node:CoreSourceNode):CoreSourceToken[]{const out:CoreSourceToken[]=[],stack:(CoreSourceNode|CoreSourceToken)[]=[node];while(stack.length){const n=stack.pop()!;if('token'in n)out.push(n);else for(let i=n.children.length-1;i>=0;i--)stack.push(n.children[i]!);}return out;}
export function coreSourceText(node:CoreSourceNode):string {return coreSourceTokens(node).filter(t=>!t.layout).map(t=>t.token).join('');}
export function coreSourceChild(node:CoreSourceNode,rule:string):CoreSourceNode {return coreSourceChildren(node,rule)[0]??coreSourceFail('InvalidContract',node,'expected '+rule);}
export function coreFreeze<T>(value:T):T {if(value&&typeof value==='object'&&!Object.isFrozen(value)){for(const v of Object.values(value))coreFreeze(v);Object.freeze(value);}return value;}
export function coreSha256(value:string|Uint8Array):string {return createHash('sha256').update(value).digest('hex');}
export function coreRelativePath(value:string):boolean {return typeof value==='string'&&value.length>0&&value.length<=4096&&!value.includes('\\')&&!/^[A-Za-z]:/.test(value)&&!/[\u0000-\u001f\u007f]/.test(value)&&value.split('/').every(p=>p!==''&&p!=='.'&&p!=='..')&&!value.startsWith('/');}

const tokenExpression=/"(?:[^"\\\r\n]|\\.)*"|[A-Za-z_][A-Za-z0-9_.-]*(?:#?\/[^\s(),;<>]+|:[A-Za-z_][A-Za-z0-9_]*\.[A-Za-z0-9_.-]+)|[A-Za-z_][A-Za-z0-9_-]*|[0-9]+|=>|<-|->|==|!=|<=|>=|\.\.|[.,:()\[\]<>=+*/;\-]/y;
const literalExpression=new RegExp(tokenExpression.source,'g');
function scalar(text:string,range:CoreSourceRange):void {for(let i=0;i<text.length;i++){const n=text.charCodeAt(i);if(n>=0xd800&&n<=0xdbff){const tail=text.charCodeAt(++i);if(!(tail>=0xdc00&&tail<=0xdfff))coreSourceFail('Syntax',range,'unpaired Unicode surrogate');}else if(n>=0xdc00&&n<=0xdfff)coreSourceFail('Syntax',range,'unpaired Unicode surrogate');}}
export function lexCoreCommerceSource(source:string,path:string):readonly CoreSourceToken[] {
 const range={path,start:0,end:0};
 if(typeof source!=='string'||!coreRelativePath(path))coreSourceFail('InvalidContract',range,'normalized relative source path and original text required');
 scalar(source,range);if(Buffer.byteLength(source)>1048576)coreSourceFail('ResourceLimit',range,'source exceeds 1 MiB');
 const out:CoreSourceToken[]=[],indents=[0];let offset=0;const brackets:string[]=[];
 const add=(token:string,start:number,end:number,layout:CoreSourceToken['layout']=null)=>{if(out.length>=65536)coreSourceFail('ResourceLimit',{path,start,end},'source token limit');out.push({token,path,start,end,layout});};
 const lines=source.split('\n');
 for(const [index,original] of lines.entries()){
  const line=index<lines.length-1&&original.endsWith('\r')?original.slice(0,-1):original,lineOffset=offset;offset+=Buffer.byteLength(original)+1;
  if(/[\t\r\0]/.test(line))coreSourceFail('Syntax',{path,start:lineOffset,end:lineOffset+Buffer.byteLength(original)},'tabs, bare CR and NUL reject');
  const indentation=/^ */.exec(line)![0].length;
  if(!line.slice(indentation)||line[indentation]==='#')continue;
  if(line.length>4096||indentation%2||indentation>128)coreSourceFail('ResourceLimit',{path,start:lineOffset,end:lineOffset+indentation},'two-space finite indentation/line required');
  const previous=indents.at(-1)!;
  if(indentation>previous){if(indentation!==previous+2)coreSourceFail('Syntax',{path,start:lineOffset,end:lineOffset+indentation},'skipped indentation');indents.push(indentation);add('',lineOffset,lineOffset+indentation,'INDENT');}
  else while(indents.at(-1)!>indentation){indents.pop();add('',lineOffset,lineOffset+indentation,'DEDENT');}
  if(indents.at(-1)!==indentation)coreSourceFail('Syntax',{path,start:lineOffset,end:lineOffset+indentation},'inconsistent indentation');
  let cursor=indentation;
  while(cursor<line.length){if(line[cursor]===' '){cursor++;continue;}if(line[cursor]==='#'&&(cursor===0||line[cursor-1]===' '))break;
   tokenExpression.lastIndex=cursor;const match=tokenExpression.exec(line);const start=lineOffset+Buffer.byteLength(line.slice(0,cursor));
   if(!match)coreSourceFail('Syntax',{path,start,end:start+1},'unknown source token');
   const token=match[0];cursor=tokenExpression.lastIndex;const end=lineOffset+Buffer.byteLength(line.slice(0,cursor));
   if(token.startsWith('"')){try{const value:unknown=JSON.parse(token);if(typeof value!=='string')throw Error();scalar(value,{path,start,end});}catch(error){if(error instanceof CoreCommerceSourceError)throw error;coreSourceFail('Syntax',{path,start,end},'invalid JSON string');}}
   if(token==='('||token==='['){brackets.push(token);if(brackets.length>64)coreSourceFail('ResourceLimit',{path,start,end},'source grouping limit');}
   else if(token===')'||token===']'){if(brackets.pop()!==(token===')'?'(':'['))coreSourceFail('Syntax',{path,start,end},'unbalanced grouping');}
   add(token,start,end);
  }
  const end=lineOffset+Buffer.byteLength(line);add('',end,end,'NEWLINE');
 }
 const end=Buffer.byteLength(source);if(brackets.length)coreSourceFail('Syntax',{path,start:end,end},'unclosed grouping');while(indents.length>1){indents.pop();add('',end,end,'DEDENT');}return coreFreeze(out);
}
const isName=(t:string)=>/^[A-Za-z_][A-Za-z0-9_-]*$/.test(t)&&!reserved.includes(t);
const terminal=(id:string,t:CoreSourceToken):boolean=>{
 if(t.layout)return t.layout===id;
 switch(id){case'NAME':return isName(t.token);case'STEP_NAME':return /^[A-Za-z_][A-Za-z0-9_-]*$/.test(t.token);case'PROTOCOL_NAME':return /^[A-Za-z_][A-Za-z0-9_.-]*$/.test(t.token);case'NATURAL':return /^(0|[1-9][0-9]*)$/.test(t.token);case'JSON_STRING':return t.token.startsWith('"');case'REFERENCE_COMPONENT':return /^(?:[A-Za-z_][A-Za-z0-9_-]*|[0-9]+)$/.test(t.token);case'REFERENCE':return /^[A-Za-z_][A-Za-z0-9_.-]*(?:#?\/[^\s(),;<>]+|:[A-Za-z_][A-Za-z0-9_]*\.[A-Za-z0-9_.-]+)$/.test(t.token);default:return false;}
};
type Parts=readonly (CoreSourceToken|CoreSourceNode)[];
type Matches=Map<number,Parts>;
export function parseCoreCommerceSyntax(source:string,path:string):CoreSourceNode {
 const tokens=lexCoreCommerceSource(source,path),memo=new Map<string,Matches>(),active=new Set<string>();let work=0,farthest=0,retainedParts=0;
 const tick=()=>{if(++work>4000000)coreSourceFail('ResourceLimit',{path,start:tokens[farthest]?.start??0,end:tokens[farthest]?.end??0},'Core syntax work limit exceeded');};
 const matchRule=(id:string,start:number):Matches=>{
  const key=id+':'+start,cached=memo.get(key);if(cached)return cached;
  if(active.has(key))coreSourceFail('InvalidContract',{path,start:tokens[start]?.start??0,end:tokens[start]?.end??0},'left-recursive Core grammar');
  const node=grammar[id];if(!node){const t=tokens[start];farthest=Math.max(farthest,start);return t&&terminal(id,t)?new Map([[start+1,[t]]]):new Map();}
  if(active.size>512)coreSourceFail('ResourceLimit',{path,start:tokens[start]?.start??0,end:tokens[start]?.end??0},'Core grammar recursion limit');
  active.add(key);const result=new Map<number,Parts>();
  for(const [end,children]of evaluate(node,start)){const first=tokens[start],last=tokens[end-1];result.set(end,[{rule:id,path,start:first?.start??Buffer.byteLength(source),end:last?.end??first?.start??Buffer.byteLength(source),children}]);}
  active.delete(key);memo.set(key,result);return result;
 };
 const combine=(a:Parts,b:Parts):Parts=>{retainedParts+=a.length+b.length;if(retainedParts>8000000)coreSourceFail('ResourceLimit',{path,start:0,end:0},'Core syntax storage limit');return [...a,...b];};
 const evaluate=(node:CoreGrammarNode,start:number):Matches=>{
  tick();
  if(node.op==='rule')return matchRule(node.value,start);
  if(node.op==='literal'){
   const words=node.value.match(literalExpression)??[];
   const ts=tokens.slice(start,start+words.length);let i=0;while(i<ts.length&&ts[i]!.layout===null&&ts[i]!.token===words[i])i++;
   farthest=Math.max(farthest,start+i);return i===words.length?new Map([[start+i,ts]]):new Map();
  }
  if(node.op==='alt'){
   const out=new Map<number,Parts>();
   // Explicit record metadata wins ties with a generic NAME/type field.
   const choices=node.nodes[0]?.op==='seq'&&node.nodes[0].nodes[0]?.op==='rule'&&node.nodes[0].nodes[0].value==='NAME'?[...node.nodes.slice(1),node.nodes[0]]:node.nodes;
   for(const n of choices)for(const [end,parts]of evaluate(n,start))if(!out.has(end))out.set(end,parts);return out;
  }
  if(node.op==='seq'){
   let current:Matches=new Map([[start,[]]]);
   for(const n of node.nodes){const next=new Map<number,Parts>();for(const [position,parts]of current)for(const [end,more]of evaluate(n,position))if(!next.has(end))next.set(end,combine(parts,more));current=next;if(!current.size)break;}return current;
  }
  const out:Matches=new Map([[start,[]]]);
  if(node.op==='maybe'){for(const [end,parts]of evaluate(node.node,start))out.set(end,parts);return out;}
  const queue=[start];for(let i=0;i<queue.length;i++){const position=queue[i]!;for(const [end,more]of evaluate(node.node,position)){tick();if(end===position)coreSourceFail('InvalidContract',{path,start:0,end:0},'nullable grammar repetition');if(!out.has(end)){out.set(end,combine(out.get(position)!,more));queue.push(end);}}}return out;
 };
 const matches=matchRule('source',0),result=matches.get(tokens.length)?.[0];
 if(!result||!('rule'in result)){const t=tokens[Math.min(farthest,tokens.length-1)];coreSourceFail('Syntax',{path,start:t?.start??0,end:t?.end??0},'source does not match complete Core grammar');}
 return coreFreeze(result);
}
