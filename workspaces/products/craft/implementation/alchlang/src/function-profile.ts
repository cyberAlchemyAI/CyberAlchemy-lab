import {digest, EXACT_PROFILE} from './domainspec-profile.js';
import {parseDomainSource} from './parser.js';
import {lowerDomainSpec} from './lower-domainspec.js';
import type {Expr,FunctionModel} from './function-runtime.js';
const bad=(message:string):never=>{throw new Error('FUNCTION_SOURCE: '+message);};
const safe=(name:string)=>/^[A-Za-z_][A-Za-z0-9_]*$/.test(name)&&!['__proto__','constructor','prototype'].includes(name);
const arities:Record<string,number[]>={if:[3],and:[2],or:[2],eq:[2],ne:[2],lte:[2],gte:[2],gt:[2],not:[1],present:[1],lower:[1],uint64:[1],decimalToUInt64:[2],formatDecimal:[2],string:[1],count:[1],first:[1],map:[2],filter:[2],every:[2],distinct:[1],sort:[1],merge:[2],query:[3],calculate:[2]};
function tokens(source:string){const result:string[]=[];let rest=source;while(rest.trim()){
 const m=/^\s*("(?:[^"\\]|\\.)*"|=>|[A-Za-z_][A-Za-z0-9_.]*|-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?|[()[\]{},:])/.exec(rest);
 if(!m)bad('unexpected expression token '+rest.slice(0,30));result.push(m![1]);rest=rest.slice(m![0].length);
 }return result;}
export function parseFunctionExpression(source:string):Expr{
 const t=tokens(source);let at=0;const take=()=>t[at++];const expect=(v:string)=>{if(take()!==v)bad('expected '+v);};
 function expr():Expr{
  const x=take();if(x===undefined)bad('missing expression');
  if(x==='{'||x==='['){const fields:[string,Expr][]=[];const args:Expr[]=[];const end=x==='{'?'}':']';const seen=new Set();
   while(t[at]!==end){if(x==='{'){const k=take();if(!safe(k)||seen.has(k))bad('invalid/duplicate object key');seen.add(k);expect(':');fields.push([k,expr()]);}else args.push(expr());if(t[at]!==',')break;take();}expect(end);return x==='{'?{kind:'object',fields}:{kind:'array',args};}
  if(x.startsWith('"'))return {kind:'literal',value:JSON.parse(x)};
  if(['true','false','null'].includes(x))return {kind:'literal',value:JSON.parse(x)};
  if(/^-?\d/.test(x)){const n=Number(x);if(!Number.isSafeInteger(n))bad('only safe integer literals; use decimal strings for exact values');return {kind:'literal',value:n};}
  if(!x.split('.').every(safe))bad('invalid reference '+x);
  if(t[at]==='=>'){take();if(!safe(x))bad('invalid lambda');return {kind:'lambda',name:x,body:expr()};}
  if(t[at]!=='(')return {kind:'ref',name:x};take();const args:Expr[]=[];
  while(t[at]!==')'){args.push(expr());if(t[at]!==',')break;take();}expect(')');if(!arities[x]?.includes(args.length))bad('operator/arity '+x);return {kind:'call',name:x,args};
 }
 const result=expr();if(at!==t.length)bad('trailing expression');return result;
}
function validateExpr(e:Expr,scope:Set<string>,queryIds:Set<string>,calcIds:Set<string>){
 if(e.kind==='ref'&&!scope.has(e.name!.split('.')[0]))bad('unresolved reference '+e.name);
 if(e.kind==='lambda'){if(scope.has(e.name!))bad('lambda shadows '+e.name);validateExpr(e.body!,new Set([...scope,e.name!]),queryIds,calcIds);return;}
 if(e.kind==='call'){
  if(['query','calculate'].includes(e.name!)){const arg=e.args![0];if(arg.kind!=='literal'||!(e.name==='query'?queryIds:calcIds).has(arg.value))bad('unresolved '+e.name);}
  if(['map','filter','every'].includes(e.name!)&&e.args![1].kind!=='lambda')bad('collection operation requires lambda');
  if(!['map','filter','every'].includes(e.name!)&&e.args!.some(x=>x.kind==='lambda'))bad('unexpected lambda');
 }
 for(const x of e.args??[])validateExpr(x,scope,queryIds,calcIds);for(const [,x] of e.fields??[])validateExpr(x,scope,queryIds,calcIds);
}
export function parseFunctionSource(source:string,allowModules=false){
 if(source.startsWith('\uFEFF')||source.includes('```'))bad('plain UTF-8 .alch required');
 const blocks:{kind:string;id:string;rows:string[]}[]=[];const core:string[]=[];let current:typeof blocks[number]|undefined;let profiles=0;
 for(const line of source.split(/\r?\n/)){
  if(!line.trim()||line.trimStart().startsWith('#')){if(!current)core.push(line);continue;}
  if(/^profile /.test(line)){if(line!=='profile function-v1'||++profiles!==1)bad('profile function-v1 must appear once');current=undefined;continue;}
  if(/^\S/.test(line)){const match=/^(schema|integration|flow|endpoint|ontology) ([A-Za-z_][A-Za-z0-9_]*):$/.exec(line);current=undefined;
   if(match){if(!safe(match[2])||blocks.some(b=>b.id===match[2]&&b.kind===match[1]))bad('duplicate/unsafe declaration');current={kind:match[1],id:match[2],rows:[]};blocks.push(current);continue;}}
  if(current){if(/^    \S/.test(line)&&current.kind==='flow'&&current.rows.length){current.rows[current.rows.length-1]+=' '+line.trim();continue;}if(!/^  \S/.test(line))bad('function sections require two-space flat clauses');current.rows.push(line.trim());}else core.push(line);
 }
 if(profiles!==1)bad('missing profile function-v1');const coreSource=core.join('\n').trim()+'\n';
 const carrier=parseDomainSource(coreSource).carrier;const owner=carrier.owner_route??/^owner (.+)$/m.exec(coreSource)?.[1];
 const bindings:any={schema_version:'alchlang.domainspec-bindings/v1',profile:EXACT_PROFILE,source_sha256:digest(coreSource),owner,declarations:Object.create(null)};
 const model:FunctionModel={schemas:Object.create(null),integrations:Object.create(null),flows:Object.create(null),endpoint:null};
 const queryIds=new Set([...coreSource.matchAll(/^query (\w+):/gm)].map(m=>m[1])),calcIds=new Set([...coreSource.matchAll(/^calculation (\w+):/gm)].map(m=>m[1]));
 for(const b of blocks.filter(b=>b.kind==='ontology')){
  const d:any={properties:Object.create(null)};for(const row of b.rows){const prop=/^property (\w+) ("(?:[^"\\]|\\.)*") ("(?:[^"\\]|\\.)*")$/.exec(row);
   if(prop){if(!safe(prop[1])||d.properties[prop[1]])bad('duplicate property');d.properties[prop[1]]={ontology:JSON.parse(prop[2]),meaning:JSON.parse(prop[3])};continue;}
   const m=/^(id|meaning|identity) (.+)$/.exec(row);if(!m)bad('ontology clause '+row);const key=m![1]==='id'?'ontology':m![1];if(own(d,key))bad('duplicate ontology clause');d[key]=m![1]==='identity'?m![2]:JSON.parse(m![2]);}
  if(!Object.keys(d.properties).length)delete d.properties;bindings.declarations[b.id]=d;
 }
 for(const b of blocks.filter(b=>b.kind==='schema')){
  const fields:Record<string,any>=Object.create(null);for(const row of b.rows){const m=/^(\w+): (\w+)(\[\])?(.*)$/.exec(row);if(!m||!safe(m[1])||own(fields,m[1]))bad('schema field '+row);
   const s:any=m![3]?{type:'list',items:m![2]}:{type:m![2]};const tail=tokens(m![4]);
   for(let i=0;i<tail.length;i++){const k=tail[i];if(!['optional','nullable','min','max','const','pattern'].includes(k)||own(s,k))bad('schema constraint '+k);if(k==='optional'||k==='nullable')s[k]=true;else{try{s[k]=JSON.parse(tail[++i]);}catch{bad('constraint literal');}}}
   if(s.pattern!==undefined&&!['string','identifier','timestamp'].includes(s.type)||s.min!==undefined&&s.type!=='integer'||s.max!==undefined&&!['integer','string','identifier','timestamp','list'].includes(s.type))bad('constraint does not apply to field type');
   if(s.pattern!==undefined){if(typeof s.pattern!=='string'||s.pattern.length>256)bad('pattern');try{new RegExp(s.pattern);}catch{bad('pattern');}}
   for(const k of ['min','max'])if(s[k]!==undefined&&(!Number.isSafeInteger(s[k])||s[k]<0))bad('invalid bound');
   if(s.min!==undefined&&s.max!==undefined&&s.min>s.max)bad('inverted bound');fields[m![1]]=s;
  }if(!Object.keys(fields).length)bad('empty schema');model.schemas[b.id]=fields;
 }
 const config=(b:typeof blocks[number],allowed:string[])=>{const c:any={};for(const row of b.rows){const m=/^(\S+) (.+)$/.exec(row);if(!m||!allowed.includes(m[1])||own(c,m[1]))bad('unknown/duplicate clause '+row);c[m![1]]=m![2].startsWith('"')?JSON.parse(m![2]):m![2];}return c;};
 for(const b of blocks.filter(b=>b.kind==='integration')){
  const query:Record<string,string>=Object.create(null);
  for(const row of b.rows.filter(r=>r.startsWith('query '))){const m=/^query (\w+) (input\.\w+(?:\.\w+)*)$/.exec(row);if(!m||!safe(m[1])||own(query,m[1]))bad('integration query');query[m![1]]=m![2];}
  const c=config({...b,rows:b.rows.filter(r=>!r.startsWith('query '))},['transport','provided','output','url-env','secret-env','timeout-ms','max-bytes','module','input']);
  if(['module-local','module-http'].includes(c.transport)){
   if(!allowModules)bad('module bindings require declarative-function-v1');
   if(!safe(c.module)||!(/^(?:input\.\w+(?:\.\w+)*|[A-Z][A-Za-z0-9_]*)$/.test(c.input))||!model.schemas[c.output]||c.provided||Object.keys(query).length)bad('module binding');
   const timeout=Number(c['timeout-ms']),maxBytes=Number(c['max-bytes']);if(!Number.isInteger(timeout)||timeout<1||timeout>30000||!Number.isInteger(maxBytes)||maxBytes<1||maxBytes>1048576)bad('module limits');
   if(c.transport==='module-http'&&(!/^[A-Z][A-Z0-9_]*$/.test(c['url-env']??'')||!/^[A-Z][A-Z0-9_]*$/.test(c['secret-env']??'')))bad('module HTTP environment');
   if(c.transport==='module-local'&&(c['url-env']||c['secret-env']))bad('local module environment');
   model.integrations[b.id]={query,transport:c.transport,module:c.module,input:c.input,output:c.output,timeout,maxBytes,...(c['url-env']?{urlEnv:c['url-env'],secretEnv:c['secret-env']}:{})};continue;
  }
  if(c.module||c.input)bad('module clauses require module transport');
  if(!['provided','http-get','provided-or-http'].includes(c.transport)||!model.schemas[c.output])bad('integration contract');
  if(c.transport==='http-get'&&c.provided||c.transport==='provided'&&(c['url-env']||c['secret-env']||Object.keys(query).length))bad('conflicting transport clauses');
  if(c.transport!=='http-get'&&(!c.provided||!/^input\.\w+(\.\w+)*$/.test(c.provided)))bad('provided selector');
  if(c.transport!=='provided'&&!/^[A-Z][A-Z0-9_]*$/.test(c['url-env']??''))bad('URL environment reference');
  if(c['secret-env']&&!/^[A-Z][A-Z0-9_]*$/.test(c['secret-env']))bad('secret environment reference');
  const timeout=Number(c['timeout-ms']),maxBytes=Number(c['max-bytes']);if(!Number.isInteger(timeout)||timeout<1||timeout>30000||!Number.isInteger(maxBytes)||maxBytes<1||maxBytes>1048576)bad('integration limits');
  model.integrations[b.id]={query,transport:c.transport,provided:c.provided,output:c.output,urlEnv:c['url-env'],secretEnv:c['secret-env'],timeout,maxBytes};
 }
 for(const b of blocks.filter(b=>b.kind==='flow')){
  const steps:any[]=[];const scope=new Set(['input']);let returned=false;
  for(const row of b.rows){if(returned)bad('unreachable clause after return');let m;
   if((m=/^bind (\w+) from (\w+)$/.exec(row))){if(!safe(m[1])||scope.has(m[1])||!model.integrations[m[2]])bad('binding reference');scope.add(m[1]);steps.push({kind:'bind',name:m[1],integration:m[2]});}
   else if((m=/^let (\w+) = (.+)$/.exec(row))){if(!safe(m[1])||scope.has(m[1]))bad('duplicate/unsafe local');const expr=parseFunctionExpression(m[2]);validateExpr(expr,scope,queryIds,calcIds);scope.add(m[1]);steps.push({kind:'let',name:m[1],expr});}
   else if((m=/^require (.+) else "([A-Z][A-Z0-9_]*)"$/.exec(row))){const expr=parseFunctionExpression(m[1]);validateExpr(expr,scope,queryIds,calcIds);steps.push({kind:'require',expr,code:m[2]});}
   else if((m=/^when (.+) return (.+)$/.exec(row))){const expr=parseFunctionExpression(m[1]),result=parseFunctionExpression(m[2]);validateExpr(expr,scope,queryIds,calcIds);validateExpr(result,scope,queryIds,calcIds);steps.push({kind:'when',expr,result});}
   else if((m=/^return (.+)$/.exec(row))){const expr=parseFunctionExpression(m[1]);validateExpr(expr,scope,queryIds,calcIds);steps.push({kind:'return',expr});returned=true;}
   else bad('flow clause '+row);
  }if(!returned)bad('flow must return');model.flows[b.id]=steps;
 }
 const endpoints=blocks.filter(b=>b.kind==='endpoint');if(endpoints.length!==1)bad('exactly one endpoint required');
 const ep=endpoints[0],statusRows=ep.rows.filter(r=>r.startsWith('status ')||r.startsWith('error '));
 const c=config({...ep,rows:ep.rows.filter(r=>!statusRows.includes(r))},['target','runtime','method','path','input','output','flow','auth-env','max-bytes','timeout-ms','error-status']);
 if(!((c.target==='node-http'&&c.runtime==='node>=26.8.1')||(c.target==='rust-http'&&c.runtime==='rust>=1.94'))||c.method!=='POST'||typeof c.path!=='string'||!/^\/[A-Za-z0-9/_-]*$/.test(c.path)||!model.schemas[c.input]||!model.schemas[c.output]||!model.flows[c.flow]||!/^[A-Z][A-Z0-9_]*$/.test(c['auth-env']??''))bad('endpoint contract');
 const statuses:any=Object.create(null),errors:any=Object.create(null);for(const row of statusRows){const m=/^(status|error) (\w+) (\d{3})$/.exec(row);if(!m||Number(m[3])<200||Number(m[3])>599||[204,205,304].includes(Number(m[3])))bad('HTTP status');const map=m![1]==='status'?statuses:errors;if(own(map,m![2]))bad('duplicate HTTP status');map[m![2]]=Number(m![3]);}
 const timeout=Number(c['timeout-ms']);if(!Number.isInteger(timeout)||timeout<1||timeout>30000)bad('endpoint timeout');
 const maxBytes=Number(c['max-bytes']),errorStatus=Number(c['error-status']);if(!Object.keys(statuses).length||!Number.isInteger(maxBytes)||maxBytes<1||maxBytes>1048576||!Number.isInteger(errorStatus)||errorStatus<400||errorStatus>599)bad('endpoint limits/status');
 model.endpoint={id:ep.id,target:c.target,runtime:c.runtime,method:c.method,path:c.path,input:c.input,output:c.output,flow:c.flow,authEnv:c['auth-env'],maxBytes,timeout,errorStatus,statuses,errors};
 for(const fields of Object.values(model.schemas))for(const s of Object.values(fields)){if(s.type==='list'&&(!Number.isInteger(s.max)||!['string','identifier'].includes(s.items)&&['timestamp','integer','boolean'].includes(s.items)))bad('list contract requires max and record/string/identifier items');const ref=s.type==='list'?s.items:s.type;if(!['identifier','string','timestamp','integer','boolean'].includes(ref)&&!model.schemas[ref])bad('unknown schema '+ref);}
 function selectorType(selector:string){let type=model.endpoint.input;for(const part of selector.split('.').slice(1)){const field=model.schemas[type]?.[part];if(!field)bad('unresolved integration selector '+selector);type=field.type;}return type;}
 for(const binding of Object.values(model.integrations)){if(binding.provided&&selectorType(binding.provided)!==binding.output)bad('provided integration schema mismatch');for(const selector of Object.values(binding.query))if(!['string','identifier','integer'].includes(selectorType(selector as string)))bad('integration query must select scalar');}
 lowerDomainSpec(carrier,bindings,coreSource);
 return {model,coreSource,bindings};
}
function own(v:any,k:string){return Object.prototype.hasOwnProperty.call(v,k);}
