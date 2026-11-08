import {linkModuleTypes,type ModuleInterface} from './module-types.js';
import {digest} from './domainspec-profile.js';
import {elaborateOntology} from './derived-ontology.js';
import {parseFunctionSource} from './function-profile.js';
import {parseDomainSource} from './parser.js';
import {lowerDomainSpec} from './lower-domainspec.js';
// This structural carrier is validated by the selected DomainSpec public API.
export type Expression = {op:'literal';value:string|number|boolean|null}|{op:'path';path:string[]}|{op:'call';name:string;args:Expression[]}|{op:'exists'|'forall'|'exactly_one';binding:string;collection:Expression;where:Expression};
const fail=(s:string):never=>{throw Error('ALCH_DECLARATIVE: '+s);};
export function parseDeclarativeExpression(source:string):Expression {
 const tokens:string[]=[];let rest=source;
 while(rest.trim()){const m=/^\s*("(?:[^"\\]|\\.)*"|==|!=|<=|>=|[<>(){},:]|[A-Za-z_][A-Za-z0-9_.]*|-?(?:0|[1-9][0-9]*))/.exec(rest);if(!m)fail('unexpected token '+rest.slice(0,25));tokens.push(m![1]);rest=rest.slice(m![0].length);}
 let at=0;const take=()=>tokens[at++],expect=(s:string)=>{if(take()!==s)fail('expected '+s);};
 const precedences:Record<string,number>={or:1,and:2,'==':3,'!=':3,'<':3,'<=':3,'>':3,'>=':3};
 const operators:Record<string,string>={or:'or',and:'and','==':'eq','!=':'ne','<':'lt','<=':'lte','>':'gt','>=':'gte'};
 function expression(min=0):Expression {
  let left:Expression;const t=take();if(t===undefined)fail('missing expression');
  if(t==='('){left=expression();expect(')');}
  else if(['exists','forall','exactly_one'].includes(t)){const binding=take();expect('in');const collection=expression();expect(':');left={op:t as 'exists',binding,collection,where:expression()};}
  else if(t==='not')left={op:'call',name:'not',args:[expression(4)]};
  else if(t.startsWith('"')||['true','false','null'].includes(t)||/^-?\d/.test(t))left={op:'literal',value:JSON.parse(t)};
  else if(tokens[at]==='('){take();const args:Expression[]=[];while(tokens[at]!==')'){args.push(expression());if(tokens[at]!==',')break;take();}expect(')');left={op:'call',name:t,args};}
  else left={op:'path',path:t.split('.')};
  while((precedences[tokens[at]]??-1)>=min){const op=take();left={op:'call',name:operators[op],args:[left,expression(precedences[op]+1)]};}
  return left;
 }
 const result=expression();if(at!==tokens.length)fail('trailing expression');return result;
}
export function parseDeclarativeSource(source:string,modules:Record<string,ModuleInterface>={}){
 const authored=source,linked=linkModuleTypes(source,modules);source=linked.source;
 const blocks:{kind:string;id:string;rows:string[]}[]=[],keep:string[]=[];let current:typeof blocks[number]|undefined;
 if(!/^profile declarative-function-v1$/m.test(source))fail('profile');
 const portabilityRows=[...source.matchAll(/^portability (.*)$/gm)];
 if(portabilityRows.length>1||portabilityRows.some(m=>m[1]!=='node-rust-v1'))fail('unsupported/duplicate portability profile');
 const portability=portabilityRows.length?'node-rust-v1':undefined;
 const ontologySource=elaborateOntology(source);ontologySource.source_sha256=digest(authored);for(const d of ontologySource.declarations){if(linked.origins[d.name]){d.line=linked.origins[d.name];d.meaning_line=d.line;for(const row of d.rows)row.line=d.line;for(const p of d.properties){p.line=d.line;p.meaning_line=d.line;}}}source=ontologySource.source.replace(/^portability node-rust-v1$/m,'');
 for(const line of source.split(/\r?\n/)){
  if(/^\S/.test(line)&&!line.startsWith('#')){current=undefined;const m=/^(mapping|query|rule|result) (\w+):$/.exec(line);if(m){current={kind:m[1],id:m[2],rows:[]};blocks.push(current);continue;}if(/^flow /.test(line))fail('procedural flow is not part of this profile');}
  if(current){if(!line.trim()||line.trimStart().startsWith('#'))continue;if(!/^  \S/.test(line))fail('two-space clauses required');current.rows.push(line.trim());}else keep.push(line);
 }
 const results=blocks.filter(b=>b.kind==='result');if(results.length!==1)fail('one result Query required');const resultId=results[0].id;
 const boundary=keep.join('\n').replace('profile declarative-function-v1','profile function-v1').replace(/^  result (\w+)$/m,(_m,id)=>{if(id!==resultId)fail('endpoint result reference');return '  flow '+id;});
 // Reuse only boundary/schema/ontology parsing. Synthetic flow is discarded before emission.
 const integrations=[...boundary.matchAll(/^integration (\w+):$/gm)].map(m=>m[1]);
 const clauses=results[0].rows;
 const roots:Record<string,string>={},bindings:{name:string;integration:string;condition?:Expression;input?:{mapping:string;type:string}}[]=[],assertions:any[]=[],cases:any[]=[];
 for(const row of clauses){let m;
  if((m=/^bind (\w+) from (\w+)(?: when (.+))?$/.exec(row))){if(bindings.some(b=>b.name===m![1])||m[1]==='input'||!integrations.includes(m[2]))fail('result binding');bindings.push({name:m[1],integration:m[2],...(m[3]?{condition:parseDeclarativeExpression(m[3])}:{})});}
  else if((m=/^require (.+) else "([A-Z][A-Z0-9_]*)"$/.exec(row)))assertions.push({condition:parseDeclarativeExpression(m[1]),code:m[2]});
  else if((m=/^when (.+) yield (.+)$/.exec(row)))cases.push({condition:parseDeclarativeExpression(m[1]),value:parseDeclarativeExpression(m[2])});
  else fail('result clause '+row);
 }
 const parsed=parseFunctionSource(boundary+'\nflow '+resultId+':\n'+bindings.map(b=>`  bind ${b.name} from ${b.integration}\n`).join('')+'  return input\n',true);
 const {model}=parsed;if(Object.keys(modules).length)model.modules=modules;if(portability)model.portability=portability;roots.input=model.endpoint.input;for(const b of bindings)roots[b.name]=model.integrations[b.integration].output;
 model.flows={};model.endpoint.result=resultId;delete model.endpoint.flow;
 const records:Record<string,Record<string,string>>={};
 const scalar=(t:string)=>['string','identifier','timestamp'].includes(t)?'String':t==='integer'?'Int':t==='boolean'?'Bool':t;
 for(const [name,fields]of Object.entries(model.schemas))records[name]=Object.fromEntries(Object.entries(fields).map(([k,s])=>[k,(s.type==='list'?scalar(s.items)+'[]':scalar(s.type))+(s.optional||s.nullable?'?':'')]));
 const lower=lowerDomainSpec(parseDomainSource(parsed.coreSource).carrier,parsed.bindings,parsed.coreSource);
 for(const term of lower.model.terms){if(records[term.id])fail('schema/record collision');records[term.id]=Object.fromEntries(lower.model.facts.filter(f=>f.subject_ref===term.id).map(f=>[f.id,(f.type==='integer'?'UInt64':scalar(f.type))+(f.required?'':'?')]));}
 const nodes=blocks.filter(b=>b.kind!=='result').map(b=>{
  const n:any={id:b.id,kind:({mapping:'Mapping',query:'Query',rule:'Rule'} as any)[b.kind]};const seen=new Set<string>();
  if(b.kind==='mapping')n.fields={};
  for(const row of b.rows){let m;let key:string;
   if(b.kind==='mapping'&&(m=/^field (\w+) = (.+)$/.exec(row))){key='field:'+m[1];if(seen.has(key))fail('duplicate field');seen.add(key);n.fields[m[1]]=parseDeclarativeExpression(m[2]);continue;}
   if((m=/^(ontology|meaning) ("(?:[^"\\]|\\.)*")$/.exec(row))){key=m[1];n[key]=JSON.parse(m[2]);}
   else if((m=/^input (\w+): (\w+)$/.exec(row))&&b.kind==='mapping'){key='input';n.input={name:m[1],type:m[2]};}
   else if((m=/^target (\w+)$/.exec(row))&&b.kind==='mapping'){key='target';n.target=m[1];}
   else if((m=/^from (\w+) in (.+)$/.exec(row))&&b.kind==='query'){key='from';n.binding=m[1];n.source=parseDeclarativeExpression(m[2]);}
   else if((m=/^(where|select) (.+)$/.exec(row))&&b.kind==='query'){key=m[1];n[key]=parseDeclarativeExpression(m[2]);}
   else if((m=/^condition (.+)$/.exec(row))&&b.kind==='rule'){key='expression';n.expression=parseDeclarativeExpression(m[1]);}
   else fail('declaration clause '+row);
   if(seen.has(key!))fail('duplicate clause');seen.add(key!);
  }
  return n;
 });
 for(const b of bindings){const integration=model.integrations[b.integration];if(integration.transport?.startsWith('module-')&&!integration.input.startsWith('input.')){
  const module=modules[integration.module];if(!module)fail('module interface required');
  b.input={mapping:integration.input,type:integration.module+'__'+module.input};
 }}
 const coreContracts=Object.fromEntries(Object.entries(lower.symbols).map(([id,symbol])=>[id,JSON.parse(lower.files[`specs/${lower.feature}/nodes/${symbol}.json`]).body.typed_contract]));
 const calculations=Object.fromEntries(lower.model.calculations.map(c=>[c.id,c.input_facts]));
 const contract={schema_version:'domainspec.declarative-function/v1',...(portability?{portability}:{}),records,roots,calculations,nodes,...(bindings.some(b=>b.condition||b.input)?{bindings:bindings.map(({name,condition,input})=>({name,...(condition?{condition}:{}),...(input?{input}:{})}))}:{}),assertions,results:cases,output:model.endpoint.output};
 return {...parsed,contract,coreContracts,ontologySource,boundaryBindings:bindings,profile:'declarative-function-v1'};
}
