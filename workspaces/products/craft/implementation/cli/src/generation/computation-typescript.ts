import { computationMetadata } from "../computation/check.js";
import type { CheckedComputation, Expr } from "../computation/types.js";

const helpers = String.raw`
type Value = any;
type Scope = Readonly<Record<string, Value>>;
type Account = { used: number; observation?: {decisions:PolicyDecisionObservation[];status:'complete'|'truncated'} };
export interface PolicyDecisionObservation {policy:string;branch:string;calculation:string;expression_path:string;index_path:number[];call_path:string[];invocation_entered:boolean}
export interface ComputationObservedResult {result:ComputationResult;policy_decisions:PolicyDecisionObservation[];observation_status:'complete'|'truncated'}
export type ComputationResult = {ok:true,value:unknown,fuel_used:number}|{ok:false,error:{code:string,expression_path:string,index_path:number[],call_path:string[]},fuel_used:number};
class Fault extends Error {
  readonly code:string;readonly expression_path:string;readonly index_path:number[];readonly call_path:string[];
  constructor(code:string,expression_path:string,index_path:number[],call_path:string[]) { super(code);this.code=code;this.expression_path=expression_path;this.index_path=index_path;this.call_path=call_path; }
}
const utf8 = (value:string):number => new TextEncoder().encode(value).length;
function fail(code:string,p:string,i:number[],c:string[]):never { throw new Fault(code,p,[...i],[...c]); }
function debit(s:Account,p:string,i:number[],c:string[]):void { if(s.used >= limits.fuel) fail("ResourceLimit",p,i,c); s.used++; }
function recordPolicy(s:Account,policy:string,branch:string,calculation:string,p:string,i:number[],c:string[]):PolicyDecisionObservation|undefined {
  const observation=s.observation;if(!observation||observation.status==='truncated')return undefined;
  const row:PolicyDecisionObservation={policy,branch,calculation,expression_path:p,index_path:[...i],call_path:[...c],invocation_entered:false};
  if(observation.decisions.length>=100||utf8(JSON.stringify([...observation.decisions,row]))>65536){observation.status='truncated';return undefined;}
  observation.decisions.push(row);return row;
}
function scalarString(value:string):boolean { for(let i=0;i<value.length;i++){const n=value.charCodeAt(i);if(n>=0xd800&&n<=0xdbff){const next=value.charCodeAt(++i);if(!(next>=0xdc00&&next<=0xdfff))return false;}else if(n>=0xdc00&&n<=0xdfff)return false;}return true; }
export function canonicalComputationJson(value:unknown):string {
  if(typeof value === "bigint") return '"'+value.toString()+'"';
  if(typeof value === "boolean") return value?"true":"false";
  if(typeof value === "string") { if(!scalarString(value))throw new Error("InputType"); return '"'+value.replace(/[\u0000-\u001f"\\]/g,c=>c==='"'?'\\"':c==='\\'?'\\\\':'\\u'+c.charCodeAt(0).toString(16).padStart(4,'0'))+'"'; }
  if(Array.isArray(value)) return '['+value.map(canonicalComputationJson).join(',')+']';
  if(value!==null&&typeof value === "object") return '{'+Object.keys(value).sort().map(k=>canonicalComputationJson(k)+':'+canonicalComputationJson((value as Record<string,unknown>)[k])).join(',')+'}';
  throw new Error("InputType");
}
function bound(value:Value,p:string,i:number[],c:string[]):Value { if(utf8(canonicalComputationJson(value))>limits.max_value_bytes)fail("OutputBound",p,i,c);return value; }
function snapshot(value:unknown,p:string,depth=0):Value {
  if(depth>64)fail('InputBound',p,[],[]);
  if(value===null||typeof value==='string'||typeof value==='boolean'||typeof value==='number')return value;
  if(typeof value!=='object')fail('InputType',p,[],[]);
  const array=Array.isArray(value),proto=Object.getPrototypeOf(value);
  if(proto!==(array?Array.prototype:Object.prototype)&&proto!==null)fail('InputType',p,[],[]);
  if(Object.getOwnPropertySymbols(value).length)fail('InputType',p,[],[]);
  const descriptors=Object.getOwnPropertyDescriptors(value);
  if(array){const out:Value[]=[];for(let n=0;n<(value as unknown[]).length;n++){const d=descriptors[String(n)];if(!d||!('value' in d))fail('InputType',p+'['+n+']',[],[]);out.push(snapshot(d.value,p+'['+n+']',depth+1));}if(Object.keys(descriptors).some(k=>k!=='length'&&(!/^(0|[1-9][0-9]*)$/.test(k)||Number(k)>=(value as unknown[]).length)))fail('InputType',p,[],[]);return out;}
  const out:Record<string,Value>=Object.create(null);for(const k of Object.keys(descriptors).sort()){const d=descriptors[k]!;if(!('value' in d)||!d.enumerable)fail('InputType',p+'.'+k,[],[]);out[k]=snapshot(d.value,p+'.'+k,depth+1);}return out;
}
function inert(value:unknown,p:string,i:number[]):Record<string,Value> {
  if(value===null||typeof value!=='object'||Array.isArray(value))fail('InputType',p,i,[]);
  return value as Record<string,Value>;
}
function decode(value:unknown,t:any,p:string,i:number[]):Value {
  if(t.kind==='scalar') {
    if(t.name==='Bool'){if(typeof value!=='boolean')fail('InputType',p,i,[]);return value;}
    if(typeof value!=='string'||value.length>20||!/^(0|[1-9][0-9]*)$/.test(value))fail('InputType',p,i,[]);
    const n=BigInt(value);if(n>18446744073709551615n)fail('InputBound',p,i,[]);return n;
  }
  if(t.kind==='string'){if(typeof value!=='string'||!scalarString(value))fail('InputType',p,i,[]);if(utf8(value)>t.max_bytes)fail('InputBound',p,i,[]);return value;}
  if(t.kind==='list'){
    if(!Array.isArray(value)||Object.getOwnPropertySymbols(value).length)fail('InputType',p,i,[]);
    if(value.length>t.max_items||value.length>limits.max_items)fail('InputBound',p,i,[]);
    const keys=Object.getOwnPropertyNames(value);if(keys.length!==value.length+1)fail('InputType',p,i,[]);
    const out:Value[]=[];for(let n=0;n<value.length;n++){const d=Object.getOwnPropertyDescriptor(value,String(n));if(!d||!('value' in d)||!d.enumerable)fail('InputType',p+'['+n+']',i,[]);out.push(decode(d.value,t.element,p+'['+n+']',i));}return out;
  }
  if(t.kind==='outcome'){
    const o=inert(value,p,i);if(Object.keys(o).sort().join(',')!=='branch,intents,machine,reason,state,tag'||typeof o.tag!=='string'||!['transition','stayed','rejected'].includes(o.tag))fail('InputType',p,i,[]);
    const machine=decode(o.machine,{kind:'string',max_bytes:128},p+'.machine',i),branch=decode(o.branch,{kind:'string',max_bytes:32},p+'.branch',i),reason=decode(o.reason,{kind:'string',max_bytes:32},p+'.reason',i);
    if(!/^[a-z][a-z0-9_]{0,127}$/.test(machine))fail('InputType',p,i,[]);
    if(o.tag==='transition'?(!/^transition:(0|[1-9][0-9]*)$/.test(branch)||Number(branch.slice(11))>=64||reason!=='matched'):(branch!=='otherwise'||reason!==(o.tag==='stayed'?'no-match-stay':'no-match-reject')))fail('InputType',p,i,[]);
    return {tag:o.tag,machine,branch,reason,state:decode(o.state,t.state,p+'.state',i),intents:decode(o.intents,{kind:'list',element:t.intent,max_items:t.max_intents},p+'.intents',i)};
  }
  const record=inert(value,p,i), fields=recordTypes[t.name], out:Record<string,Value>={};
  for(const k of [...new Set([...Object.keys(fields),...Object.keys(record)])].sort()) { if(!Object.hasOwn(fields,k)||!Object.hasOwn(record,k))fail('InputType',p+'.'+k,i,[]);out[k]=decode(record[k],fields[k],p+'.'+k,i); }return out;
}
function strictJson(text:string):unknown {
  let at=0;
  const ws=():void=>{while(/[\x20\t\r\n]/.test(text[at]??'!'))at++;};
  const string=():string=>{const start=at++;while(at<text.length){const c=text[at++];if(c==='"'){const value=JSON.parse(text.slice(start,at)) as string;if(!scalarString(value))throw Error('InputType');return value;}if(c==='\\')at++;}throw Error('InputType');};
  const parse=(depth:number):unknown=>{
    if(depth>64)throw Error('InputBound');ws();const c=text[at];
    if(c==='"')return string();
    if(c==='{'){at++;ws();const out:Record<string,unknown>=Object.create(null);if(text[at]==='}'){at++;return out;}for(;;){ws();if(text[at]!=='"')throw Error('InputType');const key=string();if(Object.hasOwn(out,key))throw Error('InputType');ws();if(text[at++]!==':')throw Error('InputType');out[key]=parse(depth+1);ws();const next=text[at++];if(next==='}')return out;if(next!==',')throw Error('InputType');}}
    if(c==='['){at++;ws();const out:unknown[]=[];if(text[at]===']'){at++;return out;}for(;;){out.push(parse(depth+1));ws();const next=text[at++];if(next===']')return out;if(next!==',')throw Error('InputType');}}
    const m=/^(true|false|null|-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?)/.exec(text.slice(at));if(!m)throw Error('InputType');at+=m[0].length;return JSON.parse(m[0]);
  };
  const value=parse(0);ws();if(at!==text.length)throw Error('InputType');return value;
}
function natural(a:string,b:string):number {
  const aa=a.match(/[0-9]+|[^0-9]+/gu)??[],bb=b.match(/[0-9]+|[^0-9]+/gu)??[];
  for(let n=0;n<Math.min(aa.length,bb.length);n++){const x=aa[n]!,y=bb[n]!;if(x===y)continue;if(/^[0-9]/.test(x)&&/^[0-9]/.test(y)){const xx=x.replace(/^0+/,'')||'0',yy=y.replace(/^0+/,'')||'0';if(xx.length!==yy.length)return xx.length<yy.length?-1:1;const order=lexical(xx,yy);if(order)return order;if(x.length!==y.length)return x.length<y.length?-1:1;}else return lexical(x,y);}return aa.length<bb.length?-1:aa.length>bb.length?1:0;
}
`;

export interface ComputationGenerationPlan {
  source:string;
  manifest:{schema_version:string;source_node:string;semantics_revision:string;stage:string;target:'typescript';runtime_dependencies:never[];operators:string[];expression_bindings:{generated_function:string;expression_path:string;op:string}[];declaration_bindings:{name:string;kind:string;generated_function:string}[]};
}
/** Emit closed expression-specific native functions. Generated output contains no AST evaluator. */
export function generateComputationTypeScript(checked:CheckedComputation):ComputationGenerationPlan {
  const contract=computationMetadata(checked).contract, definitions:string[]=[], bindings:ComputationGenerationPlan['manifest']['expression_bindings']=[];
  const q=JSON.stringify;
  const functionNames=new Map(contract.functions.map((f,n)=>[f.name,`f${n}`]));
  let serial=0;
  function emit(e:Expr,path:string):string {
    const name=`e${serial++}`, p=q(path);
    bindings.push({generated_function:name,expression_path:path,op:e.op});
    const child=(key:string,expression:Expr,scope='env',indices='i',calls='c'):string=>`${emit(expression,path+'.'+key)}(s,${scope},${indices},${calls})`;
    const named=(declaration:string,args:Expr[],prefix:string,decision=''):string=>{
      const values=args.map((arg,n)=>child(`${prefix}arguments[${n}]`,arg));
      const callPath=prefix?path+'.'+prefix.slice(0,-1):path;return `${functionNames.get(declaration)}(s,[${values.join(',')}],i,c,${q(callPath)}${decision?','+decision:''})`;
    };
    let body='';
    switch(e.op){
      case 'literal':body=`v=${e.type.kind==='scalar'&&e.type.name==='UInt64'?`${q(e.value)}n`.replace(/"([0-9]+)"n/,'$1n'):q(e.value)};`;break;
      case 'var':body=`v=env[${q(e.name)}];`;break;
      case 'field':body=`v=${child('value',e.value)}[${q(e.field)}];`;break;
      case 'record':body=`v={};\n${Object.keys(e.fields).sort().map(k=>`v[${q(k)}]=${child('fields.'+k,e.fields[k]!)};`).join('\n')}`;break;
      case 'let':body=`const local={...env,[${q(e.binding.name)}]:${child('value',e.value)}};v=${child('body',e.body,'local')};`;break;
      case 'if':body=`v=${child('condition',e.condition)}?${child('then',e.then)}:${child('else',e.else)};`;break;
      case 'unary':body=`v=!${child('value',e.value)};`;break;
      case 'binary':{
        const a=child('left',e.left),b=child('right',e.right);
        if(e.operator==='and'||e.operator==='or')body=`const a=${a};v=a ${e.operator==='and'?'&&':'||'} ${b};`;
        else if(['eq','lt','lte','gt','gte'].includes(e.operator))body=`const a=${a},b=${b};v=a${({eq:'===',lt:'<',lte:'<=',gt:'>',gte:'>='} as Record<string,string>)[e.operator]}b;`;
        else {
          body=`const a:bigint=${a},b:bigint=${b};`;
          if(e.operator==='divide')body+=`if(b===0n)fail('DivideByZero',${p},i,c);if(a%b!==0n&&rounding==='reject')fail('InexactDivision',${p},i,c);v=a/b+(rounding==='ceil'&&a%b!==0n?1n:0n);`;
          else body+=`v=a${({add:'+',subtract:'-',multiply:'*'} as Record<string,string>)[e.operator]}b;`;
          body+=`if(v<0n)fail('ArithmeticUnderflow',${p},i,c);if(v>18446744073709551615n)fail('ArithmeticOverflow',${p},i,c);`;
        }break;
      }
      case 'call':body=`v=${named(e.declaration,e.arguments,'')};`;break;
      case 'map':case 'filter':case 'fold':case 'indexed_fold':{
        const rows=child('source',e.source), accumulating=e.op==='fold'||e.op==='indexed_fold';
        const value=accumulating?child('initial',e.initial):`bound([],${p},i,c)`;
        const scope=`{...env,[${q(e.item.name)}]:rows[n]${accumulating?`,[${q(e.state.name)}]:v`:''}${e.op==='indexed_fold'?`,[${q(e.index.name)}]:BigInt(n)`:''}}`;
        const step=e.op==='filter'?child('predicate',e.predicate,'local','next'):child('body',e.body,'local','next');
        body=`const rows:Value[]=${rows};v=${value};for(let n=0;n<rows.length;n++){const next=[...i,n];debit(s,${p},next,c);const local=${scope};const step=${step};`;
        body+=e.op==='map'?`v.push(step);bound(v,${p},next,c);`:e.op==='filter'?`if(step){v.push(rows[n]);bound(v,${p},next,c);}`:`v=bound(step,${p},next,c);`;
        body+='}';break;
      }
      case 'repeat':body=`const count:bigint=${child('count',e.count)};if(count>BigInt(${e.max_iterations}))fail('IterationBound',${q(path+'.count')},i,c);v=${child('initial',e.initial)};for(let n=0;n<Number(count);n++){const next=[...i,n];debit(s,${p},next,c);const local={...env,[${q(e.state.name)}]:v,[${q(e.index.name)}]:BigInt(n)};v=bound(${child('body',e.body,'local','next')},${p},next,c);}`;break;
      case 'while_bounded':case 'until_bounded':body=`v=${child('initial',e.initial)};for(let n=0;;n++){const next=[...i,n],local={...env,[${q(e.state.name)}]:v};const guard=${child('guard',e.guard,'local','next')};if(${e.op==='while_bounded'?'!guard':'guard'})break;if(n===${e.max_iterations})fail('IterationLimit',${p},next,c);debit(s,${p},next,c);v=bound(${child('body',e.body,'local','next')},${p},next,c);}`;break;
      case 'range':body=`const start:bigint=${child('start',e.start)},end:bigint=${child('end',e.end)},step:bigint=${child('step',e.step)};if(step===0n)fail('IterationBound',${p},i,c);const count=end>start?(end-start+step-1n)/step:0n;if(count>BigInt(${e.max_iterations}))fail('IterationBound',${p},i,c);v=bound([],${p},i,c);for(let n=0;n<Number(count);n++){const next=[...i,n];debit(s,${p},next,c);v.push(start+BigInt(n)*step);bound(v,${p},next,c);}`;break;
      case 'sort':{
        const keyCode=e.keys.map((k,n)=>child(`keys[${n}].value`,k.value,'local','next'));
        const comparisons=e.keys.map((k,n)=>`{const next=[...i,left.ordinal,right.ordinal,${n}];debit(s,${p},next,c);const a=left.keys[${n}],b=right.keys[${n}];const order=${k.mode==='natural'?'natural(a,b)':k.mode==='lexical'?'lexical(a,b)':'a<b?-1:a>b?1:0'};if(order!==0)return ${k.direction==='desc'?'-order':'order'};}`).join('\n');
        body=`const rows:Value[]=${child('source',e.source)};const decorated:{value:Value;ordinal:number;keys:Value[]}[]=[];for(let n=0;n<rows.length;n++){const next=[...i,n];debit(s,${p},next,c);const local={...env,[${q(e.item.name)}]:rows[n]};decorated.push({value:rows[n],ordinal:n,keys:[${keyCode.join(',')}]});}const compare=(left:typeof decorated[number],right:typeof decorated[number]):number=>{${comparisons}return 0;};const sorted:typeof decorated=[];bound([],${p},i,c);for(const current of decorated){let at=sorted.length;while(at>0&&compare(current,sorted[at-1]!)<0)at--;sorted.splice(at,0,current);bound(sorted.map(row=>row.value),${p},[...i,current.ordinal],c);}v=sorted.map(row=>row.value);`;break;
      }
      case 'policy':{
        const action=(entry:{calculation:string;arguments:Expr[]},prefix:string,branch:string):string=>`{const decision=recordPolicy(s,${q(e.declaration)},${q(branch)},${q(entry.calculation)},${p},i,c);v=${named(entry.calculation,entry.arguments,prefix,'decision')};}`;
        body=e.cases.map((entry,n)=>`${n?'else ':''}if(${child(`cases[${n}].condition`,entry.condition)})${action(entry,`cases[${n}].`,'case:'+n)}`).join('')+(e.cases.length?'else ':'')+action(e.otherwise,'otherwise.','otherwise');break;
      }
      case 'match':{
        body=`const local={...env,[${q(e.binding.name)}]:${child('value',e.value)}};`;
        body+=e.cases.map((entry,n)=>`${n?'else ':''}if(${child(`cases[${n}].when`,entry.when,'local')})v=${child(`cases[${n}].then`,entry.then,'local')};`).join('')+`else v=${child('otherwise',e.otherwise,'local')};`;if(!e.cases.length)body=`const local={...env,[${q(e.binding.name)}]:${child('value',e.value)}};v=${child('otherwise',e.otherwise,'local')};`;break;
      }
      case 'state_machine':{
        body=`const state=${child('state',e.state)},event=${child('event',e.event)},local={...env,[${q(e.state_binding.name)}]:state,[${q(e.event_binding.name)}]:event};`;
        const fallback=`v={tag:${q(e.otherwise==='stay'?'stayed':'rejected')},state,intents:[],machine:${q(e.declaration)},branch:'otherwise',reason:${q(e.otherwise==='stay'?'no-match-stay':'no-match-reject')}};`;
        body+=e.transitions.map((entry,n)=>`${n?'else ':''}if(${child(`transitions[${n}].guard`,entry.guard,'local')}){const nextState=${child(`transitions[${n}].next`,entry.next,'local')};const intents:Value[]=[];${entry.intents.map((intent,j)=>`intents.push(${child(`transitions[${n}].intents[${j}]`,intent,'local')});bound(intents,${p},i,c);`).join('')}v={tag:'transition',state:nextState,intents,machine:${q(e.declaration)},branch:${q('transition:'+n)},reason:'matched'};}`).join('')+(e.transitions.length?'else ':'')+fallback;break;
      }
    }
    definitions.push(`function ${name}(s:Account,env:Scope,i:number[],c:string[]):Value { debit(s,${p},i,c);let v:Value;${body}\nreturn bound(v,${p},i,c); }`);
    return name;
  }
  const root=emit(contract.expression,'$.expression');
  for(let n=0;n<contract.functions.length;n++){
    const f=contract.functions[n]!,fn=functionNames.get(f.name)!,body=emit(f.body,`$.functions[${n}].body`);
    definitions.push(`function ${fn}(s:Account,args:Value[],i:number[],c:string[],p:string,decision?:PolicyDecisionObservation):Value {const next=[...c,${q(f.name)}];debit(s,p,i,next);if(next.length>limits.max_call_depth)fail('ResourceLimit',p,i,next);if(decision)decision.invocation_entered=true;const env={${f.parameters.map((parameter,j)=>`${q(parameter.name)}:args[${j}]`).join(',')}};return ${body}(s,env,i,next);}`);
  }
  const source=`// Independent standalone closed computation: ${contract.source_node}\nconst limits=${q(contract.limits)};\nconst rounding:string=${q(contract.rounding)};\nconst inputTypes:{name:string;type:any}[]=${q(contract.inputs)};\nconst recordTypes:Record<string,any>=${q(Object.fromEntries(contract.records.map(r=>[r.name,r.fields])))};\n${helpers}\nfunction lexical(a:string,b:string):number { const aa=Array.from(a),bb=Array.from(b);for(let n=0;n<Math.min(aa.length,bb.length);n++){const x=aa[n]!.codePointAt(0)!,y=bb[n]!.codePointAt(0)!;if(x!==y)return x<y?-1:1;}return aa.length<bb.length?-1:aa.length>bb.length?1:0;}\n${definitions.join('\n')}\nfunction failure(error:unknown,s:Account):ComputationResult {if(error instanceof Fault)return {ok:false,error:{code:error.code,expression_path:error.expression_path,index_path:error.index_path,call_path:error.call_path},fuel_used:s.used};throw error;}\nfunction execute(inputs:unknown,s:Account):ComputationResult {try {const safe=snapshot(inputs,'$.inputs');if(utf8(JSON.stringify(safe))>limits.max_input_bytes)fail('InputBound','$.inputs',[],[]);const raw=inert(safe,'$.inputs',[]),env:Record<string,Value>={};for(const input of inputTypes){if(!Object.hasOwn(raw,input.name))fail('InputType','$.inputs.'+input.name,[],[]);env[input.name]=decode(raw[input.name],input.type,'$.inputs.'+input.name,[]);}for(const key of Object.keys(raw).sort())if(!inputTypes.some(input=>input.name===key))fail('InputType','$.inputs.'+key,[],[]);const value=${root}(s,env,[],[]);const json=canonicalComputationJson(value);if(utf8(json)>limits.max_output_bytes)fail('OutputBound','$.expression',[],[]);return {ok:true,value:JSON.parse(json),fuel_used:s.used};}catch(error){return failure(error,s);}}\nfunction executeJson(json:string,s:Account):ComputationResult {if(typeof json!=='string')return {ok:false,error:{code:'InputType',expression_path:'$.inputs',index_path:[],call_path:[]},fuel_used:0};if(utf8(json)>limits.max_input_bytes)return {ok:false,error:{code:'InputBound',expression_path:'$.inputs',index_path:[],call_path:[]},fuel_used:0};try{return execute(strictJson(json),s);}catch(error){return {ok:false,error:{code:error instanceof Error&&error.message==='InputBound'?'InputBound':'InputType',expression_path:'$',index_path:[],call_path:[]},fuel_used:0};}}\n
export function runComputation(inputs:unknown):ComputationResult {return execute(inputs,{used:0});}\n
export function runComputationJson(json:string):ComputationResult {return executeJson(json,{used:0});}\n
export function runComputationObserved(inputs:unknown):ComputationObservedResult {const observation:NonNullable<Account['observation']>={decisions:[],status:'complete'},s:Account={used:0,observation};const result=execute(inputs,s);return {result,policy_decisions:observation.decisions,observation_status:observation.status};}\n
export function runComputationJsonObserved(json:string):ComputationObservedResult {const observation:NonNullable<Account['observation']>={decisions:[],status:'complete'},s:Account={used:0,observation};const result=executeJson(json,s);return {result,policy_decisions:observation.decisions,observation_status:observation.status};}\n`;
  return {source,manifest:{schema_version:'domainspec.computation-typescript/v1-candidate',source_node:contract.source_node,semantics_revision:contract.semantics_revision,stage:contract.stage,target:'typescript',runtime_dependencies:[],operators:[...new Set(bindings.map(b=>b.op))].sort(),expression_bindings:bindings,declaration_bindings:contract.functions.map((f,n)=>({name:f.name,kind:f.kind??'Calculation',generated_function:`f${n}`}))}};
}
