import {validateGuardAvailability} from './guarded-bindings.js';
/** Opt-in composition contracts for existing Mapping, Query, Rule and Calculation meanings.
 * Generates source; no expression interpreter is shipped to the target. */
export const DECLARATIVE_FUNCTION_PROFILE = 'domainspec.declarative-function/v1' as const;
export const DECLARATIVE_FUNCTION_INPUTS_PROFILE = 'domainspec.declarative-function/v2' as const;
export interface MappingInput {name:string; type:string}
/** Only use after the versioned contract has passed validation. */
export const mappingInputs=(n:DeclarativeNode):readonly MappingInput[]=>n.inputs??(n.input?[n.input]:[]);
export type DeclarativeExpression =
 | {op:'literal'; value:string|number|boolean|null}
 | {op:'path'; path:string[]}
 | {op:'call'; name:string; args:DeclarativeExpression[]}
 | {op:'exists'|'forall'|'exactly_one'; binding:string; collection:DeclarativeExpression; where:DeclarativeExpression};
type E = DeclarativeExpression;
export interface DeclarativeNode {
 id:string; kind:'Mapping'|'Query'|'Rule'; ontology:string; meaning:string;
 input?:MappingInput; inputs?:MappingInput[]; target?:string; fields?:Record<string,E>;
 binding?:string; source?:E; where?:E; select?:E; expression?:E;
}
export interface DeclarativeFunctionContract {
 portability?:"node-rust-v1";
 schema_version:typeof DECLARATIVE_FUNCTION_PROFILE|typeof DECLARATIVE_FUNCTION_INPUTS_PROFILE;
 records:Record<string,Record<string,string>>;
 roots:Record<string,string>;
 calculations:Record<string,string[]>;
 nodes:DeclarativeNode[];
 assertions:{condition:E; code:string}[];
 results:{condition:E; value:E}[];
 output:string;
 bindings?:{name:string;condition?:E;input?:{mapping:string;type:string}}[];
}
const invalid=(message:string):never=>{throw Error('DS_DECLARATIVE: '+message);};
const safe=(s:unknown):s is string=>typeof s==='string'&&/^[A-Za-z_][A-Za-z0-9_]*$/.test(s)&&!['__proto__','prototype','constructor'].includes(s);
const baseTypes=['String','Int','UInt64','Bool','Null'];
function object(v:any){if(!v||typeof v!=='object'||Array.isArray(v)||![Object.prototype,null].includes(Object.getPrototypeOf(v)))invalid('record required');for(const k of Reflect.ownKeys(v))if(typeof k!=='string'||!(Object.getOwnPropertyDescriptor(v,k)&&'value' in Object.getOwnPropertyDescriptor(v,k)!))invalid('data properties required');}
function keys(v:any,required:string[],optional:string[]=[]){object(v);if(required.some(k=>!Object.hasOwn(v,k))||Object.keys(v).some(k=>![...required,...optional].includes(k)))invalid('contract keys');}
const q=JSON.stringify;
const optional=(t:string)=>t.endsWith('?');
const bare=(t:string)=>optional(t)?t.slice(0,-1):t;
const element=(t:string)=>t.endsWith('[]')?t.slice(0,-2):invalid('collection required: '+t);
const compatible=(actual:string,expected:string)=>actual===expected||(optional(expected)&&(actual===bare(expected)||actual==='Null'));

export function compileDeclarativeFunction(value:unknown):{source:string; contract:DeclarativeFunctionContract; trace:unknown} {
 const c=value as DeclarativeFunctionContract;
 keys(c,['schema_version','records','roots','calculations','nodes','assertions','results','output'],['portability','bindings']);
 if(c.portability!==undefined&&c.portability!=='node-rust-v1')invalid('portability profile');
 if(c.schema_version!==DECLARATIVE_FUNCTION_PROFILE&&c.schema_version!==DECLARATIVE_FUNCTION_INPUTS_PROFILE)invalid('profile');
 const explicitInputs=c.schema_version===DECLARATIVE_FUNCTION_INPUTS_PROFILE;
 for(const map of [c.records,c.roots,c.calculations])object(map);
 if(!Array.isArray(c.nodes)||!Array.isArray(c.assertions)||!Array.isArray(c.results)||!c.results.length)invalid('declarations');
 function type(t:unknown):asserts t is string {if(typeof t!=='string')invalid('type');const b=bare(t as string);if(b.endsWith('[]'))type(b.slice(0,-2));else if(!baseTypes.includes(b)&&!Object.hasOwn(c.records,b))invalid('unknown type '+b);}
 for(const [name,fields] of Object.entries(c.records)){if(!safe(name)||baseTypes.includes(name))invalid('record name');object(fields);for(const [name,t]of Object.entries(fields)){if(!safe(name))invalid('field name');type(t);}}
 for(const [name,t]of Object.entries(c.roots)){if(!safe(name))invalid('root name');type(t);}
 if(!Object.hasOwn(c.records,c.output))invalid('output record');
 for(const [name,inputs]of Object.entries(c.calculations)){if(!safe(name)||!Array.isArray(inputs)||inputs.some(x=>!safe(x))||new Set(inputs).size!==inputs.length)invalid('calculation');}
 const nodes=new Map<string,DeclarativeNode>();
 const builtins=new Set(['eq','ne','lt','lte','gt','gte','and','or','not','present','lower','uint64','optional_uint64','decimal','format','text','coalesce','count','one','first','distinct','sort','column']);
 for(const n of c.nodes){
  object(n);if(typeof n.ontology!=='string'||!/^[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)+$/.test(n.ontology)||typeof n.meaning!=='string'||!n.meaning.trim())invalid('declaration meaning/ontology');
  if(n.kind==='Mapping'){
   keys(n,['id','kind','ontology','meaning','target','fields',...(explicitInputs?['inputs']:[])],explicitInputs?[]:['input']);object(n.fields);if(!Object.hasOwn(c.records,n.target!))invalid('mapping target');
   if(explicitInputs){
    if(!Array.isArray(n.inputs)||Object.getPrototypeOf(n.inputs)!==Array.prototype||n.inputs.length>128)invalid('mapping inputs array (maximum 128)');
    const descriptors=Object.getOwnPropertyDescriptors(n.inputs);
    if(Reflect.ownKeys(descriptors).length!==n.inputs!.length+1||Array.from({length:n.inputs!.length},(_,i)=>descriptors[String(i)]).some(d=>!d||!Object.hasOwn(d,'value')||!d.enumerable))invalid('dense mapping inputs data');
   }
   for(const input of mappingInputs(n)){keys(input,['name','type']);if(!safe(input.name))invalid('mapping input');type(input.type);}
   if(new Set(mappingInputs(n).map(p=>p.name)).size!==mappingInputs(n).length)invalid('duplicate mapping input');
  }
  else if(n.kind==='Query')keys(n,['id','kind','ontology','meaning','binding','source','where','select']);
  else if(n.kind==='Rule')keys(n,['id','kind','ontology','meaning','expression']);else invalid('node kind');
  if(!safe(n.id)||nodes.has(n.id)||Object.hasOwn(c.roots,n.id)||Object.hasOwn(c.calculations,n.id)||builtins.has(n.id))invalid('duplicate/reserved declaration '+n.id);
  nodes.set(n.id,n);
 }
 const dependencies=new Map<string,Set<string>>(),types=new Map<string,string>(),emitted=new Map<string,string>(),active=new Set<string>();
 let owner='result';
 function resolve(id:string):string {
  dependencies.get(owner)?.add(id);
  if(types.has(id))return types.get(id)!;
  const n=nodes.get(id);if(!n)invalid('unresolved '+id);if(active.has(id))invalid('cycle '+id);
  active.add(id);dependencies.set(id,new Set());const previous=owner;owner=id;
  const scope:Record<string,string>={...c.roots};let output:string;let code:string;
  if(n!.kind==='Mapping'){
   for(const input of mappingInputs(n!)){if(Object.hasOwn(scope,input.name)||nodes.has(input.name)||Object.hasOwn(c.calculations,input.name))invalid('shadowed input');scope[input.name]=input.type;}
   const fields=c.records[n!.target!]!,parts:string[]=[];
   for(const [name,e]of Object.entries(n!.fields!)){if(!Object.hasOwn(fields,name))invalid('unknown target field '+name);const r=expr(e,scope);if(!compatible(r.type,fields[name]!))invalid('mapping type '+id+'.'+name+': '+r.type+' -> '+fields[name]!);parts.push(q(name)+': '+r.code);}
   if(Object.entries(fields).some(([name,t])=>!optional(t)&&!Object.hasOwn(n!.fields!,name)))invalid('missing required mapping field '+id);
   output=n!.target!;code='Object.freeze({'+parts.join(',')+'})';
  }else if(n!.kind==='Rule'){const r=expr(n!.expression!,scope);if(r.type!=='Bool')invalid('Rule must be Bool');output='Bool';code=r.code;}
  else {const source=expr(n!.source!,scope);const item=element(source.type);const binding=n!.binding!;
   if(!safe(binding)||Object.hasOwn(scope,binding)||nodes.has(binding)||Object.hasOwn(c.calculations,binding))invalid('query binding');scope[binding]=item;
   const where=expr(n!.where!,scope),select=expr(n!.select!,scope);if(where.type!=='Bool')invalid('query predicate');
   output=select.type+'[]';code=`traceQuery(${q(id)}, ${source.code}, (${local(binding)}) => ${where.code}, (${local(binding)}) => ${select.code}, observe)`;
  }
  owner=previous;active.delete(id);types.set(id,output!);emitted.set(id,code!);return output!;
 }
 const local=(name:string)=>'v_'+name;
 type R={type:string;code:string};
 function expr(e:E,scope:Record<string,string>,depth=0):R {
  if(depth>32)invalid('expression depth');object(e);
  const recurse=(v:E,s=scope)=>expr(v,s,depth+1);
  if(e.op==='literal'){keys(e,['op','value']);if(e.value!==null&&!['string','boolean','number'].includes(typeof e.value)||typeof e.value==='number'&&!Number.isSafeInteger(e.value))invalid('literal');return {type:e.value===null?'Null':typeof e.value==='string'?'String':typeof e.value==='boolean'?'Bool':'Int',code:q(e.value)};}
  if(e.op==='path'){
   keys(e,['op','path']);if(!Array.isArray(e.path)||!e.path.length||e.path.some(p=>!safe(p)))invalid('path');
   const head=e.path[0]!,tail=e.path.slice(1);let t:string,code:string;
   if(Object.hasOwn(scope,head)){t=scope[head]!;code=local(head);}else{if(nodes.has(head)&&mappingInputs(nodes.get(head)!).length)invalid('mapping requires argument');t=resolve(head);code=`n_${head}()`;}
   for(const part of tail){if(optional(t))invalid('optional path requires coalesce: '+e.path.join('.'));const fields=c.records[t];if(!fields||!Object.hasOwn(fields,part))invalid('unresolved field '+part);t=fields![part]!;code+=`[${q(part)}]`;}
   return {type:t,code};
  }
  if(e.op==='exists'||e.op==='forall'||e.op==='exactly_one'){
   keys(e,['op','binding','collection','where']);if(!safe(e.binding)||Object.hasOwn(scope,e.binding)||nodes.has(e.binding))invalid('quantifier binding');
   const collection=recurse(e.collection),t=element(collection.type),where=recurse(e.where,{...scope,[e.binding]:t});if(where.type!=='Bool')invalid('quantifier predicate');
   return {type:'Bool',code:e.op==='exactly_one'?`(${collection.code}.filter((${local(e.binding)}) => ${where.code}).length === 1)`:`${collection.code}.${e.op==='exists'?'some':'every'}((${local(e.binding)}) => ${where.code})`};
  }
  if(e.op!=='call')invalid('expression operator');const call=e as Extract<E,{op:'call'}>;
  keys(call,['op','name','args']);if(!safe(call.name)||!Array.isArray(call.args))invalid('call');const args=call.args.map(a=>recurse(a));const codes=args.map(a=>a.code),ts=args.map(a=>a.type),name=call.name;
  const arity=(n:number)=>{if(args.length!==n)invalid('arity '+name);};
  const requireTypes=(...expected:string[])=>{arity(expected.length);if(expected.some((t,i)=>!compatible(ts[i]!,t)))invalid('argument type '+name+': '+ts.join(','));};
  if(nodes.has(name)){const n=nodes.get(name)!;if(n.kind!=='Mapping')invalid('only Mapping takes arguments');const inputs=mappingInputs(n);arity(inputs.length);const t=resolve(name);if(inputs.some((p,i)=>!compatible(ts[i]!,p.type)))invalid('mapping input type');return {type:t,code:`n_${name}(${codes.join(',')})`};}
  if(Object.hasOwn(c.calculations,name)){if(explicitInputs)dependencies.get(owner)?.add(name);const inputs=c.calculations[name]!;requireTypes(...inputs.map(()=>'UInt64'));return {type:'UInt64',code:`((${inputs.map((_,i)=>'arg'+i).join(',')}) => observed(${q(name)}, 'Calculation', () => api.evaluateCalculation(${q(name)}, {${inputs.map((x,i)=>q(x)+':arg'+i).join(',')}}), observe))(${codes.join(',')})`};}
  if(['and','or'].includes(name)){requireTypes('Bool','Bool');return {type:'Bool',code:`(${codes[0]} ${name==='and'?'&&':'||'} ${codes[1]})`};}
  if(['eq','ne','lt','lte','gt','gte'].includes(name)){arity(2);if(ts[0]!==ts[1]!||!['String','Bool','Int','UInt64'].includes(ts[0]!)||!['eq','ne'].includes(name)&&!['Int','UInt64'].includes(ts[0]!))invalid('comparison type');return {type:'Bool',code:`(${codes[0]} ${{eq:'===',ne:'!==',lt:'<',lte:'<=',gt:'>',gte:'>='}[name]} ${codes[1]})`};}
  if(name==='not'){requireTypes('Bool');return {type:'Bool',code:`(!${codes[0]})`};}
  if(name==='present'){arity(1);return {type:'Bool',code:`(${codes[0]} != null)`};}
  if(name==='coalesce'){arity(2);if(!optional(ts[0]!)||bare(ts[0]!)!==ts[1]!)invalid('coalesce type');return {type:ts[1]!,code:`(${codes[0]} ?? ${codes[1]})`};}
  if(name==='lower'){requireTypes('String');return {type:'String',code:c.portability?`${codes[0]}.replace(/[A-Z]/g,c=>c.toLowerCase())`:`${codes[0]}.toLowerCase()`};}
  if(name==='optional_uint64'){arity(1);if(!['Int?','String?','UInt64?'].includes(ts[0]!))invalid('optional uint64 input');return {type:'UInt64?',code:`optionalUint64(${codes[0]})`};}
  if(name==='uint64'){arity(1);if(!['String','Int','UInt64'].includes(ts[0]!))invalid('uint64 input');return {type:'UInt64',code:`uint64(${codes[0]})`};}
  if(name==='decimal'||name==='format'){requireTypes(name==='decimal'?'String':'UInt64','Int');const scale=call.args[1]!;if(scale.op!=='literal'||typeof scale.value!=='number'||scale.value<0||scale.value>18)invalid('scale literal');return {type:name==='decimal'?'UInt64':'String',code:`${name}(${codes.join(',')})`};}
  if(name==='text'){requireTypes('UInt64');return {type:'String',code:`${codes[0]}.toString()`};}
  if(name==='count'||name==='one'||name==='first'||name==='distinct'||name==='sort'){arity(1);const t=element(ts[0]!);if(['distinct','sort'].includes(name)&&!['String','Int','UInt64'].includes(t))invalid('scalar collection');return {type:name==='count'?'Int':(name==='one'||name==='first')?t:ts[0]!,code:name==='count'?`${codes[0]}.length`:name==='one'?`one(${codes[0]})`:name==='first'?`first(${codes[0]})`:name==='distinct'?`[...new Set(${codes[0]})]`:`[...${codes[0]}].sort((a,b) => a < b ? -1 : a > b ? 1 : 0)`};}
  if(name==='column'){arity(2);const t=element(ts[0]!),field=call.args[1]!;if(field.op!=='literal'||typeof field.value!=='string'||!Object.hasOwn(c.records[t]??{},field.value))return invalid('column field');return {type:c.records[t]![field.value as string]!+'[]',code:`${codes[0]}.map(row => row[${codes[1]}])`};}
  return invalid('unknown operator '+name);
 }
 for(const id of nodes.keys())resolve(id);
 if(c.bindings!==undefined&&!Array.isArray(c.bindings))invalid("binding array");
 const guards=(c.bindings??[]).map(b=>{keys(b,['name'],['condition','input']);if(Object.hasOwn(b,'input')){keys(b.input,['mapping','type']);const n=nodes.get(b.input!.mapping);if(!n||n.kind!=='Mapping'||mappingInputs(n).length)invalid('binding input requires a zero-argument Mapping');type(b.input!.type);if(expr({op:'path',path:[b.input!.mapping]},c.roots).type!==b.input!.type)invalid('binding input mapping type');}if(!safe(b.name)||b.name==='input'||!Object.hasOwn(c.roots,b.name))invalid('binding root');if(Object.hasOwn(b,'condition')&&expr(b.condition!,c.roots).type!=='Bool')invalid('binding guard must be Bool');return b;});
 if(c.bindings&&(new Set(guards.map(b=>b.name)).size!==guards.length||Object.keys(c.roots).some(k=>k!=='input'&&!guards.some(b=>b.name===k))))invalid('binding root closure');

 const assertions=c.assertions.map((a,index)=>{keys(a,['condition','code']);if(!/^[A-Z][A-Z0-9_]*$/.test(a.code))invalid('assertion code');const r=expr(a.condition,c.roots);if(r.type!=='Bool')invalid('assertion type');return `assertObserved(${index}, 'behavior', ${q(a.code)}, () => (${r.code}), observe);`;});
 const results=c.results.map(r=>{keys(r,['condition','value']);const when=expr(r.condition,c.roots),value=expr(r.value,c.roots);if(when.type!=='Bool'||value.type!==c.output)invalid('result type');return {when:when.code,value:value.code};});
 validateGuardAvailability(c);
 // Input-only guards can reject a request before a transport binding is invoked.
 function inputOnly(e:E):boolean {if(e.op==='literal')return true;if(e.op==='path')return e.path[0]==='input';if(e.op==='call')return builtins.has(e.name)&&e.args.every(inputOnly);return false;}
 const preconditions=c.assertions.flatMap((a,index)=>inputOnly(a.condition)?[`assertObserved(${index}, 'input', ${q(a.code)}, () => (${expr(a.condition,c.roots).code}), observe);`]:[]);
 const source=`// ${c.schema_version}; generated from typed contracts, not executable source text.\n${primitives}\nexport function validateInput(roots, observe) {const v_input=roots.input; ${preconditions.join("\n")} }\nexport function execute(roots, api, observe, binding, phase='guard') {\n${Object.keys(c.roots).map(k=>`const ${local(k)} = roots[${q(k)}];`).join('\n')}\n${[...nodes.values()].map(n=>mappingInputs(n).length?`const n_${n.id} = (${mappingInputs(n).map(p=>local(p.name)).join(',')}) => observed(${q(n.id)}, ${q(n.kind)}, () => (${emitted.get(n.id)}), observe);`:`const n_${n.id} = memo(() => observed(${q(n.id)}, ${q(n.kind)}, () => (${emitted.get(n.id)}), observe));`).join('\n')}\n${guards.length?`if (binding !== undefined) {if(phase==='input'){switch(binding){${guards.filter(b=>b.input).map(b=>`case ${q(b.name)}: return ${expr({op:'path',path:[b.input!.mapping]},c.roots).code};`).join('')}default: throw fault('FUNCTION_BINDING_INPUT_REQUIRED');}}switch(binding) {${guards.filter(b=>b.condition).map(b=>`case ${q(b.name)}: return ${expr(b.condition!,c.roots).code};`).join('')}default: throw fault('FUNCTION_BINDING_REQUIRED');}}`:''}\n${assertions.join('\n')}\nconst matches = [${results.map(r=>`() => (${r.when})`).join(',')}].map((test,index) => {const passed=test();emit(observe,{kind:'result-case',index,passed});return passed;});\nif (matches.filter(Boolean).length !== 1) throw fault('DS_RESULT_CARDINALITY');\n${results.map((r,i)=>`if (matches[${i}]) {emit(observe,{kind:'selected-case',index:${i}});return ${r.value};}`).join('\n')}\n}\n`;
 return {source,contract:c,trace:{profile:c.schema_version,observation_profile:'domainspec.declarative-observation/v1',...(c.bindings?{bindings:c.bindings}:{}),nodes:[...nodes.values()].map(n=>({id:n.id,kind:n.kind,ontology:n.ontology,meaning:n.meaning,type:types.get(n.id),...(explicitInputs&&n.kind==='Mapping'?{inputs:mappingInputs(n).map(p=>({...p})),evaluation:mappingInputs(n).length?'left-to-right-once-per-argument-per-call':'invocation-local-memoized'}:{}),dependencies:[...dependencies.get(n.id)!].sort()})),authority_effect:'none',ontology_admitted:false}};
}
const primitives=String.raw`
const fault = code => Object.assign(new Error(code), {code});
const errorCode = error => /^[A-Z][A-Z0-9_]*$/.test(error?.code ?? '') ? error.code : String(error?.message ?? '').match(/\bCALCULATION_(?:OVERFLOW|UNDERFLOW|DIVIDE_BY_ZERO|INEXACT)\b/)?.[0] ?? 'EVALUATION_FAILED';
function emit(observe,event) {if(observe) {try {observe(structuredClone(event));} catch { /* Observers cannot alter evaluation. */ }}}
function observed(declaration,node_kind,compute,observe) {
 emit(observe,{kind:'node-start',declaration,node_kind});
 try {const value=compute();emit(observe,{kind:'node-result',declaration,node_kind,...(node_kind==='Query'?{count:value.length}:{value})});return value;}
 catch(error){emit(observe,{kind:'node-error',declaration,node_kind,code:errorCode(error)});throw error;}
}
function traceQuery(declaration,rows,predicate,project,observe) {
 emit(observe,{kind:'query-start',declaration,total:rows.length});
 // Preserve filter-before-projection order and evaluate each predicate exactly once.
 return rows.filter((row,index)=>{const accepted=predicate(row);emit(observe,{kind:'query-row',declaration,index,accepted,row});return accepted;}).map(project);
}
function assertObserved(index,phase,code,test,observe) {
 const passed=test();emit(observe,{kind:'assertion',index,phase,code,passed});if(!passed)throw fault(code);
}

const memo = f => { let ready=false, value; return () => {if (!ready) {value=f(); ready=true;} return value;}; };
function fullMatch(pattern,value) {const match=pattern.exec(value);return !!match&&match[0].length===value.length;}
function uint64(value) {
 if (typeof value==='number'&&!Number.isSafeInteger(value)||typeof value==='string'&&!fullMatch(/^(0|[1-9][0-9]*)$/,value)||!['bigint','number','string'].includes(typeof value)) throw fault('FUNCTION_UINT64');
 const n=BigInt(value); if(n<0n||n>18446744073709551615n)throw fault('FUNCTION_UINT64');return n;
}
function optionalUint64(value) {return value == null ? null : uint64(value);}
function decimal(value,scale) {
 if(!fullMatch(new RegExp('^(0|[1-9][0-9]*)(\\.[0-9]{1,'+Math.max(1,scale)+'})?$'),value)||(scale===0&&value.includes('.')))throw fault('FUNCTION_DECIMAL');
 const [whole,fraction='']=value.split('.');return uint64(BigInt(whole)*10n**BigInt(scale)+BigInt(fraction.padEnd(scale,'0')||'0'));
}
function format(value,scale) { const n=uint64(value),base=10n**BigInt(scale);return scale ? (n/base)+'.'+(n%base).toString().padStart(scale,'0') : n.toString(); }
function first(rows) { if(rows.length===0)throw fault('DS_QUERY_EMPTY');return rows[0]; }
function one(rows) { if(rows.length!==1)throw fault('DS_QUERY_CARDINALITY');return rows[0]; }
`;
