import {readFileSync,realpathSync,mkdtempSync,mkdirSync,writeFileSync,cpSync,rmSync,readdirSync,linkSync,lstatSync} from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {loadModuleTree,assertModuleSources,type ModuleTree} from './module-source.js';
import {buildFunction,checkFunction} from './function-builder.js';
import {loadQueryIteration,buildQueryIteration,checkQueryIteration} from './query-iteration.js';
import {digest} from './domainspec-profile.js';
// Candidate route composition; meanings and open questions: ../SERVICE.md.
const fail=(s:string):never=>{throw Error('ALCH_SERVICE: '+s);};
const safe=(s:string)=>/^[A-Za-z][A-Za-z0-9_]*$/.test(s)&&!['constructor','prototype','__proto__'].includes(s);
const canonical=(v:any):string=>JSON.stringify(v,(_k,x)=>x&&typeof x==='object'&&!Array.isArray(x)?Object.fromEntries(Object.entries(x).sort(([a],[b])=>a<b?-1:a>b?1:0)):x);
function shape(tree:ModuleTree,s:any,active:string[]=[]):any{
 const {type,items,...rest}=s;
 const expand=(t:string):any=>{if(!Object.hasOwn(tree.parsed.model.schemas,t))return t;if(active.includes(t))return fail('recursive service interface');return Object.fromEntries(Object.entries(tree.parsed.model.schemas[t]).map(([k,v])=>[k,shape(tree,v,[...active,t])]));};
 return {type:type==='list'?'list':expand(type),...(type==='list'?{items:expand(items)}:{}),...rest};
}
function pure(tree:ModuleTree){if(tree.parsed.model.endpoint.target!=='node-http')fail('node-http function required');for(const b of Object.values(tree.parsed.model.integrations) as any[])if(b.transport!=='module-local')fail('effectful functions require an explicit operation binding');for(const child of Object.values(tree.children))pure(child);}
function selected(type:any,key:string){if(key==='all')return type;if(!safe(key)||typeof type.type!=='object'||!Object.hasOwn(type.type,key)||type.type[key].optional||type.type[key].nullable)fail('required output field '+key);return type.type[key];}
function keys(value:any,required:string[],optional:string[]=[]){if(required.some(k=>!Object.hasOwn(value,k))||Object.keys(value).some(k=>![...required,...optional].includes(k)))fail('missing or unknown declarations');}
export function loadServiceRoutes(sourcePath:string){
 sourcePath=realpathSync(sourcePath);if(path.extname(sourcePath)!=='.alch')fail('source extension');const source=readFileSync(sourcePath,'utf8');if(Buffer.byteLength(source)>65536)fail('source limit');
 const top:Record<string,string>={},imports:Record<string,string>={},routes:any[]=[],operations:Record<string,any>={};let block:any;
 for(const [index,line] of source.split(/\r?\n/).entries()){
  if(!line.trim()||line.trimStart().startsWith('#'))continue;
  if(line.startsWith('  ')){const m=/^  ([a-z-]+) (.+)$/.exec(line);if(!block||!m||Object.hasOwn(block,m[1]))fail('invalid/duplicate clause at '+(index+1));block[m![1]]=m![2];continue;}
  block=undefined;const imp=/^import ([A-Z][A-Za-z0-9]*) from ("[^"\n]+")$/.exec(line);
  if(imp){if(Object.hasOwn(imports,imp[1]))fail('duplicate import');imports[imp[1]]=JSON.parse(imp[2]);continue;}
  const decl=/^(route|operation) ([A-Z][A-Za-z0-9]*):$/.exec(line);
  if(decl){if(!safe(decl[2]))fail('unsafe declaration');if(decl[1]==='route'){if(routes.some(r=>r.id===decl[2]))fail('duplicate route id');block={id:decl[2],line:index+1};routes.push(block);}else{if(Object.hasOwn(operations,decl[2]))fail('duplicate operation');block={};operations[decl[2]]=block;}continue;}
  const m=/^([a-z-]+) (.+)$/.exec(line);if(!m||Object.hasOwn(top,m[1]))fail('invalid/duplicate declaration');top[m![1]]=m![2];
 }
 keys(top,['domain','profile','assembly','target','authentication','authorization','scope','max-request-bytes','max-response-bytes','read-timeout-ms','errors']);
 if(!/^[-a-z0-9]+ "[^"\n]+"$/.test(top.domain)||top.profile!=='service-v1'||top.assembly!=='public-routes-v1'||top.target!=='node-http'||top.authentication!=='deferred'||top.authorization!=='deferred'||top.scope!=='shared-public')fail('unsupported service target or security mode');
 for(const [k,max]of Object.entries({'max-request-bytes':65536,'max-response-bytes':65536,'read-timeout-ms':30000}))if(!/^[1-9][0-9]*$/.test(top[k])||Number(top[k])>max)fail('invalid bound '+k);
 if(routes.length<1||routes.length>32||Object.keys(imports).length>16||Object.keys(operations).length>16)fail('declaration count limit');
 const root=path.dirname(sourcePath),modules:Record<string,any>={};
 for(const [alias,file]of Object.entries(imports)){
  if(!file.startsWith('./')||!file.endsWith('.alch'))fail('relative module required');const resolved=realpathSync(path.resolve(root,file)),relative=path.relative(root,resolved);if(relative==='..'||relative.startsWith('..'+path.sep)||path.isAbsolute(relative))fail('module escape');
  const text=readFileSync(resolved,'utf8');
  if(/^profile query-iteration-v1$/m.test(text)){const iteration=loadQueryIteration(resolved);const item=iteration.interfaces.itemOutput;if(item.optional||item.nullable)fail('optional iteration item');modules[alias]={file:resolved,relative,source:text,iteration,input:iteration.interfaces.context,output:{type:{[iteration.plan.outputField]:{type:'list',items:item.type,max:iteration.plan.maxItems}}}};}
  else {const tree=loadModuleTree(resolved);pure(tree);modules[alias]={file:resolved,relative,source:text,tree,input:shape(tree,{type:tree.parsed.model.endpoint.input}),output:shape(tree,{type:tree.parsed.model.endpoint.output})};}
 }
 const module=(alias:string)=>{if(!Object.hasOwn(modules,alias))fail('missing function '+alias);return modules[alias];};
 const ref=(name:string)=>{const m=/^([A-Z][A-Za-z0-9]*)\.(input|output)$/.exec(name);if(!m)fail('typed reference required');return module(m![1])[m![2]];};
 for(const op of Object.values(operations)){keys(op,['input','output','response']);if(!['json','json-or-sse'].includes(op.response))fail('unsupported operation response');op.inputType=ref(op.input);op.outputType=ref(op.output);}
 const errors=module(top.errors);const ei=errors.input.type,eo=errors.output.type;
 if(typeof ei!=='object'||ei.code?.type!=='string'||ei.code.optional||ei.code.nullable||Object.keys(ei).some(k=>!['code','request_id'].includes(k))||(ei.request_id&&!ei.request_id.optional)||eo.http_status?.type!=='integer'||eo.http_status.min<400||eo.http_status.max>599||eo.http_status.min===undefined||eo.http_status.max===undefined||eo.http_status.optional||eo.http_status.nullable||typeof eo.body?.type!=='object'||eo.body.optional||eo.body.nullable)fail('incompatible error policy');
 const seen=new Set<string>(),contexts:Record<string,any>={},usedOperations=new Set<string>();
 for(const r of routes){
  keys(r,['id','line','method','path','function','input','output','response','status'],['operation','result']);
  try{r.path=JSON.parse(r.path);}catch{fail('quoted path required');}
  if(!['GET','POST'].includes(r.method)||typeof r.path!=='string'||!/^\/[A-Za-z0-9/_-]*$/.test(r.path)||new URL(r.path,'http://localhost').pathname!==r.path||r.path.startsWith('//'))fail('unsupported route method/path');
  const identity=r.method+' '+r.path;if(seen.has(identity))fail('duplicate route');seen.add(identity);
  if(!/^[0-9]{3}$/.test(r.status)||Number(r.status)<200||Number(r.status)>299||[204,205].includes(Number(r.status)))fail('JSON success status required');r.status=Number(r.status);
  const fn=module(r.function);let output=fn.output;
  if(r.input==='json'){if(r.method!=='POST')fail('JSON input requires POST');}
  else if(r.input==='unit'){if(r.method!=='GET'||canonical(fn.input)!==canonical({type:{unit:{type:'boolean',const:true}}}))fail('unit input type mismatch');}
  else {const m=/^context ([a-z][a-z0-9_]*)$/.exec(r.input);if(r.method!=='GET'||!m||!safe(m[1]))fail('invalid context input');if(Object.hasOwn(contexts,m![1])&&canonical(contexts[m![1]])!==canonical(fn.input))fail('incompatible context types');contexts[m![1]]=fn.input;}
  if(r.operation){if(!Object.hasOwn(operations,r.operation)||!r.result)fail('missing operation/result binding');const op=operations[r.operation];if(canonical(op.inputType)!==canonical(fn.output)||canonical(op.outputType)!==canonical(module(r.result).input))fail('incompatible operation types');if(op.response!==r.response)fail('incompatible response mode');usedOperations.add(r.operation);output=module(r.result).output;}
  else if(r.result||r.response!=='json')fail('SSE requires a typed operation binding');
  r.outputType=selected(output,r.output);
 }
 if(Object.keys(operations).some(k=>!usedOperations.has(k)))fail('unused operation');
 const plan={schema_version:'alchlang.service-routes/v1-candidate',service:top.domain.split(' ')[0],assembly:top.assembly,target:top.target,authentication:top.authentication,authorization:top.authorization,scope:top.scope,errors:top.errors,limits:{requestBytes:Number(top['max-request-bytes']),responseBytes:Number(top['max-response-bytes']),readTimeoutMs:Number(top['read-timeout-ms'])},routes:routes.sort((a,b)=>(a.path+' '+a.method)<(b.path+' '+b.method)?-1:1),operations,contexts,functions:Object.fromEntries(Object.entries(modules).map(([alias,m])=>[alias,{source:m.relative,source_sha256:digest(m.source),input:m.input,output:m.output}])),authority_effect:'none'};
 return {sourcePath,source,modules,plan};
}
function assertSources(loaded:ReturnType<typeof loadServiceRoutes>){if(readFileSync(loaded.sourcePath,'utf8')!==loaded.source)fail('source drift');for(const m of Object.values(loaded.modules)){if(readFileSync(m.file,'utf8')!==m.source)fail('module source drift');if(m.tree)assertModuleSources(m.tree);if(m.iteration)for(const t of Object.values(m.iteration.trees))assertModuleSources(t as ModuleTree);}}
export async function checkServiceRoutes(file:string){const loaded=loadServiceRoutes(file);for(const m of Object.values(loaded.modules))await (m.iteration?checkQueryIteration(m.file):checkFunction(m.file));assertSources(loaded);return {status:'valid',plan:loaded.plan,authority_effect:'none'};}
const files=(dir:string):string[]=>readdirSync(dir,{withFileTypes:true}).flatMap(e=>e.isDirectory()?files(path.join(dir,e.name)):[path.join(dir,e.name)]);
export async function buildServiceRoutes(file:string,output:string){
 const loaded=loadServiceRoutes(file);output=path.resolve(output);try{lstatSync(output);fail('output exists');}catch(e){if((e as any).code!=='ENOENT')throw e;}
 const stage=mkdtempSync(path.join(path.dirname(output),'.alch-service-'));
 try{
  mkdirSync(path.join(stage,'functions'));for(const [alias,m]of Object.entries(loaded.modules))await (m.iteration?buildQueryIteration(m.file,path.join(stage,'functions',alias)):buildFunction(m.file,path.join(stage,'functions',alias),m.tree));
  mkdirSync(path.join(stage,'app/service'),{recursive:true});
  for(const name of ['service-runtime','node-service-host'])cpSync(fileURLToPath(new URL('./'+name+'.js',import.meta.url)),path.join(stage,'app/service',name+'.mjs'));
  writeFileSync(path.join(stage,'routes.json'),JSON.stringify(loaded.plan,null,2)+'\n');writeFileSync(path.join(stage,'source.alch'),loaded.source);
  writeFileSync(path.join(stage,'app/service/index.mjs'),Object.keys(loaded.modules).map(k=>`import {invoke as ${k}} from '../../functions/${k}/app/function/index.mjs';`).join('\n')+`\nimport {createService} from './service-runtime.mjs';\nimport {createNodeServiceServer} from './node-service-host.mjs';\nimport plan from '../../routes.json' with {type:'json'};\nexport const functions={${Object.keys(loaded.modules).join(',')}};\nexport const createHandler=options=>createService(plan,functions,options);\nexport const createServer=options=>{const handle=createHandler(options);return createNodeServiceServer(handle,handle.errorResponse);};\nexport {plan};\n`);
  mkdirSync(path.join(stage,'evidence/service'),{recursive:true});
  const trace={schema_version:'alchlang.public-service-assembly-trace/v1-candidate',source:{path:loaded.sourcePath,sha256:digest(loaded.source)},routes:loaded.plan.routes.map(r=>({id:r.id,line:r.line,method:r.method,path:r.path,function:r.function,operation:r.operation??null,result:r.result??null,output:r.output,output_type_sha256:digest(canonical(r.outputType))})),functions:Object.entries(loaded.modules).map(([alias,m])=>({alias,source:m.relative,source_sha256:digest(m.source),manifest_sha256:digest(readFileSync(path.join(stage,'functions',alias,'manifest.json')))})),pipeline:['alch-service-source','typed-route-and-operation-bindings','domainspec-compiled-functions','node-service-assembly'],authority_effect:'none'};
  writeFileSync(path.join(stage,'evidence/service/assembly-trace.json'),JSON.stringify(trace,null,2)+'\n');
  assertSources(loaded);const inventory=Object.fromEntries(files(stage).sort().map(p=>[path.relative(stage,p),digest(readFileSync(p))]));
  const manifest={schema_version:'alchlang.service-build/v1-candidate',profile:'service-v1',source_sha256:digest(loaded.source),routes_sha256:digest(readFileSync(path.join(stage,'routes.json'))),entry:'app/service/index.mjs',required_bindings:Object.keys(loaded.plan.operations).sort(),files:inventory,authority_effect:'none'};
  writeFileSync(path.join(stage,'manifest.json'),JSON.stringify(manifest,null,2)+'\n');mkdirSync(output);
  for(const f of files(stage).sort((a,b)=>Number(a===path.join(stage,'manifest.json'))-Number(b===path.join(stage,'manifest.json')))){const dest=path.join(output,path.relative(stage,f));mkdirSync(path.dirname(dest),{recursive:true});linkSync(f,dest);}
  return {status:'built',profile:'service-v1',output,manifest,authority_effect:'none'};
 }finally{rmSync(stage,{recursive:true,force:true});}
}
