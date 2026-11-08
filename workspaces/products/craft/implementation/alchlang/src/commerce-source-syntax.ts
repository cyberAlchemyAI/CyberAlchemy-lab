/** Bounded grammar-driven concrete syntax parser. No source concatenation,
 * code evaluation or semantic admission. Open Questions: EC06/CONTEXT.md. */
import {parseCommerceExpression} from './commerce-source-expression.js';
import {commerceSyntaxTokens} from './commerce-source-model.js';
import {COMMERCE_GRAMMAR_PRODUCTIONS,COMMERCE_RESERVED_NAMES} from './commerce-source-grammar.js';
import {COMMERCE_SOURCE_LIMITS,lexCommerceSource} from './commerce-source-lexer.js';
import {sourceFail,type CommerceSyntax,type CommerceToken} from './commerce-source-model.js';
type Symbol=string|{readonly literal:string};
interface Production {readonly lhs:string;readonly rhs:readonly Symbol[]}
interface State {readonly production:number;readonly dot:number;readonly origin:number;readonly children:readonly (CommerceSyntax|CommerceToken)[]}
interface Chart {readonly states:Map<string,State>;readonly queue:State[];readonly waiting:Map<string,State[]>;readonly empty:Map<string,CommerceSyntax>}
const productions:readonly Production[]=[{lhs:'$accept',rhs:['source']},...COMMERCE_GRAMMAR_PRODUCTIONS];
const index=new Map<string,number[]>();productions.forEach((p,i)=>{const rows=index.get(p.lhs)??[];rows.push(i);index.set(p.lhs,rows);});
const reserved:ReadonlySet<string>=new Set(COMMERCE_RESERVED_NAMES);
function accepts(symbol:Symbol,token:CommerceToken):boolean {
 if(typeof symbol!=='string')return token.layout===null&&token.text===symbol.literal;
 const value=token.text;if(['NEWLINE','INDENT','DEDENT'].includes(symbol))return token.layout===symbol;
 if(token.layout!==null)return false;
 switch(symbol){case'NAME':return /^[A-Za-z_][A-Za-z0-9_]*$/.test(value)&&!reserved.has(value)&&!['NEWLINE','INDENT','DEDENT'].includes(value);
 case'STEP_NAME':return /^[a-z][a-z0-9-]*$/.test(value);case'PROTOCOL_NAME':return /^[A-Za-z][A-Za-z0-9_-]*$/.test(value);
 case'NATURAL':return /^(0|[1-9][0-9]*)$/.test(value);case'JSON_STRING':return value.startsWith('"');case'REFERENCE_COMPONENT':return /^(?:[A-Za-z_][A-Za-z0-9_-]*|[0-9]+)$/.test(value);case'REFERENCE':return value.includes('/')||value.includes(':')&&value.includes('.');default:return false;}
}
export function parseCommerceSyntax(text:string,path:string):CommerceSyntax {
 const tokens=lexCommerceSource(text,path),charts:Chart[]=Array.from({length:tokens.length+1},()=>({states:new Map(),queue:[],waiting:new Map(),empty:new Map()}));let count=0,work=0;
 const header=tokens.slice(0,tokens.findIndex(t=>t.layout==='NEWLINE'));if(header[0]?.text==='module'&&header.at(-2)?.text==='version'&&header.at(-1)?.text!=='1')sourceFail('UnsupportedCapability',header.at(-1)!,'unsupported commerce module version');
 // The grammar permits a metadata clause such as `identity id` to resemble a
 // generic NAME/type field. Keep the specific clause derivation when both
 // consume the exact same span. No source/fixture name participates.
 const records=new Map<string,{generic:boolean;node:{kind:string;path:string;start:number;end:number;children:readonly (CommerceSyntax|CommerceToken)[]}}>();
 const add=(at:number,state:State)=>{const chart=charts[at]!,key=`${state.production}/${state.dot}/${state.origin}`;if(chart.states.has(key))return;if(++count>COMMERCE_SOURCE_LIMITS.chart_states)sourceFail('ResourceLimit',tokens[at]??{path,start:Buffer.byteLength(text),end:Buffer.byteLength(text)},'syntax state bound exceeded');chart.states.set(key,state);chart.queue.push(state);};
 const advance=(at:number,state:State,node:CommerceSyntax|CommerceToken)=>add(at,{...state,dot:state.dot+1,children:[...state.children,node]});
 add(0,{production:0,dot:0,origin:0,children:[]});let last=0;
 for(let at=0;at<charts.length;at++){
  const chart=charts[at]!;if(!chart.queue.length)break;last=at;
  for(let q=0;q<chart.queue.length;q++){
   const state=chart.queue[q]!,production=productions[state.production]!;
   if(++work>COMMERCE_SOURCE_LIMITS.parser_work)sourceFail('ResourceLimit',tokens[at]??{path,start:Buffer.byteLength(text),end:Buffer.byteLength(text)},'syntax work bound exceeded');
   if(state.dot===production.rhs.length){
    const children:(CommerceSyntax|CommerceToken)[]=[];for(const child of state.children){if('kind'in child&&child.kind.startsWith('$'))children.push(...child.children);else children.push(child);}
    const start=tokens[state.origin]?.start??Buffer.byteLength(text),end=at>state.origin?tokens[at-1]!.end:start;
    let node:CommerceSyntax;
    if(production.lhs==='record-clause'){
     const key=state.origin+'/'+at,generic=production.rhs[0]==='NAME',old=records.get(key);
     if(old){if(old.generic&&!generic){old.node.children=Object.freeze(children);old.generic=false;}node=old.node;}
     else {const fresh={generic,node:{kind:production.lhs,path,start,end,children:Object.freeze(children)}};records.set(key,fresh);node=fresh.node;}
    }else node=Object.freeze({kind:production.lhs,path,start,end,children:Object.freeze(children)});
    if(state.origin===at&&!chart.empty.has(production.lhs))chart.empty.set(production.lhs,node);
    for(const parent of charts[state.origin]!.waiting.get(production.lhs)??[])advance(at,parent,node);
   }else{
    const symbol=production.rhs[state.dot]!;
    if(typeof symbol==='string'&&index.has(symbol)){
     const waiting=chart.waiting.get(symbol)??[];waiting.push(state);chart.waiting.set(symbol,waiting);
     for(const id of index.get(symbol)!)add(at,{production:id,dot:0,origin:at,children:[]});
     const empty=chart.empty.get(symbol);if(empty)advance(at,state,empty);
    }else if(at<tokens.length&&accepts(symbol,tokens[at]!))advance(at+1,state,tokens[at]!);
   }
  }
 }
 const accepted=charts[tokens.length]!.states.get('0/1/0');
 if(!accepted){const token=tokens[last]??{path,start:Buffer.byteLength(text),end:Buffer.byteLength(text)};sourceFail('Syntax',token,`unexpected ${'text'in token?JSON.stringify(token.text):'end of source'} in commerce-source/v1-candidate`);}
 const root=accepted.children[0];if(!root||!('kind'in root)||root.kind!=='source')return sourceFail('InvalidContract',{path,start:0,end:0},'parser produced no source root');for(const row of records.values())Object.freeze(row.node);
 const normalize=(node:CommerceSyntax):CommerceSyntax=>node.kind==='expression'?parseCommerceExpression(commerceSyntaxTokens(node)):Object.freeze({...node,children:Object.freeze(node.children.map(c=>'kind'in c?normalize(c):c))});
 return normalize(root);
}
