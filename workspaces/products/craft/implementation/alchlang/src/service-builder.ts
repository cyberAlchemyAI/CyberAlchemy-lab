import {createHash} from 'node:crypto';
import {lstatSync,linkSync,mkdirSync,mkdtempSync,readFileSync,realpathSync,readdirSync,rmSync,writeFileSync} from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {buildFunction,prepareFunctionPlan,disposePreparedFunction,planPreparedFunction,assertPreparedFunctionCurrent} from './function-builder.js';
import {digest} from './domainspec-profile.js';
import {assertModuleSources,loadModuleTree,type ModuleTree} from './module-source.js';
import {parseServiceSource} from './service-profile.js';

type CompiledEntry={id:string;alias:string;source:string;source_sha256:string;line:number;meaning:string;ontology:string;tree:ModuleTree;route:{method:string;path:string};input:string;output:string;auth_env:string;target:string;runtime:string};
const fail=(message:string):never=>{throw Error('ALCH_SERVICE: '+message);};
const files=(root:string):string[]=>readdirSync(root,{withFileTypes:true}).flatMap(entry=>entry.isDirectory()?files(path.join(root,entry.name)):[path.join(root,entry.name)]);
const stableId=(domain:string,kind:string,name:string)=>'ALCH-'+createHash('sha256').update(JSON.stringify([domain,kind,name])).digest('hex').slice(0,24).toUpperCase();
const sourceLocation=(sourcePath:string,sha256:string,line:number)=>({path:path.basename(sourcePath),line,sha256});

export function compileService(sourcePath:string){
 const resolved=realpathSync(path.resolve(sourcePath));if(path.extname(resolved)!=='.alch')fail('relative .alch source required');
 const source=readFileSync(resolved,'utf8');if(Buffer.byteLength(source)>1048576)fail('source limit');
 const parsed=parseServiceSource(source),root=realpathSync(path.dirname(resolved)),imports=new Map(parsed.imports.map(row=>[row.alias,row]));
 const entries:CompiledEntry[]=parsed.entries.map(entry=>{
  const imported=imports.get(entry.functionAlias)!;const candidate=path.resolve(root,imported.file),functionPath=realpathSync(candidate),relative=path.relative(root,functionPath);
  if(relative==='..'||relative.startsWith('..'+path.sep)||path.isAbsolute(relative))fail('function import escapes service root');
  const tree=loadModuleTree(functionPath),model=tree.parsed.model,endpoint=model.endpoint;
  if(endpoint.target!=='node-http')fail('only node-http function entries are supported');
  return {id:entry.id,alias:entry.functionAlias,source:relative.split(path.sep).join('/'),source_sha256:digest(tree.source),line:entry.line,meaning:entry.meaning??`Service entry ${entry.id} delegates to imported Alch function ${entry.functionAlias}.`,ontology:entry.ontology??stableId(parsed.domain,'entry',entry.id),tree,route:{method:endpoint.method,path:endpoint.path},input:endpoint.input,output:endpoint.output,auth_env:endpoint.authEnv,target:endpoint.target,runtime:endpoint.runtime};
 });
 const routeKeys=new Set<string>();for(const entry of entries){const key=entry.route.method+' '+entry.route.path;if(routeKeys.has(key))fail('duplicate route '+key);routeKeys.add(key);}
 const ontologyId=parsed.service.ontology??stableId(parsed.domain,'service',parsed.service.id);const identities=[ontologyId,...entries.map(entry=>entry.ontology)];if(new Set(identities).size!==identities.length)fail('duplicate ontology identity');
 const sourceSha=digest(source),ontology={schema_version:'alchlang.service-ontology/v1',source_format:'alchlang',domain:parsed.domain,source:{path:path.basename(resolved),sha256:sourceSha},nodes:[
  {id:ontologyId,name:parsed.service.id,kind:'service',meta_type:'Interface',meaning:{text:parsed.service.meaning??`Service ${parsed.service.id} assembles explicitly declared Alch function entry points.`,origin:parsed.service.meaning?'authored':'derived-structural',source:sourceLocation(resolved,sourceSha,parsed.service.line)},source:sourceLocation(resolved,sourceSha,parsed.service.line)},
  ...entries.map(entry=>({id:entry.ontology,name:entry.id,kind:'entry',meta_type:'Interface',meaning:{text:entry.meaning,origin:parsed.entries.find(row=>row.id===entry.id)!.meaning?'authored':'derived-structural',source:sourceLocation(resolved,sourceSha,entry.line)},source:sourceLocation(resolved,sourceSha,entry.line),binding:{function_alias:entry.alias,function_source:entry.source,function_source_sha256:entry.source_sha256,route:entry.route,input:entry.input,output:entry.output,auth_env:entry.auth_env,target:entry.target,runtime:entry.runtime}}))
 ],references:entries.map(entry=>({source:ontologyId,target:entry.ontology,role:'exposes',evidence:sourceLocation(resolved,sourceSha,entry.line)})),status:'generated-scaffold',reference_semantics:'compiler service assembly; not admitted ontology relationships',ontology_admitted:false,authority_effect:'none'};
 return {profile:'service-v1' as const,sourcePath:resolved,source,source_sha256:sourceSha,service:{id:parsed.service.id,ontology:ontologyId},entries,ontology,authority_effect:'none' as const};
}

export async function buildService(sourcePath:string,output:string){
 const compiled=compileService(sourcePath);output=path.resolve(output);
 try{lstatSync(output);fail('output exists');}catch(error){if((error as any).code!=='ENOENT')throw error;}
 const stage=mkdtempSync(path.join(path.dirname(output),'.alch-service-'));
 const write=(name:string,value:string|Buffer)=>{const target=path.join(stage,name);mkdirSync(path.dirname(target),{recursive:true});writeFileSync(target,value,{flag:'wx'});};
 try{
  mkdirSync(path.join(stage,'entries'));
  const entryRecords=[];
  for(const entry of compiled.entries){
   const directory=path.join(stage,'entries',entry.id);await buildFunction(entry.tree.path,directory,entry.tree);
   const childManifest=readFileSync(path.join(directory,'manifest.json')),deployment=JSON.parse(readFileSync(path.join(directory,'deployment.json'),'utf8'));
   const ontologyBytes=readFileSync(path.join(directory,'provenance/function/ontology.json')),ontology=JSON.parse(ontologyBytes.toString('utf8'));
   const projectBytes=readFileSync(path.join(directory,'provenance/lowering/project/project.json')),project=JSON.parse(projectBytes.toString('utf8'));
   const certificateBytes=readFileSync(path.join(directory,'evidence/lowering/certificate.json')),certificate=JSON.parse(certificateBytes.toString('utf8'));
   if(ontology.schema_version!=='domainspec.composition-ontology/v1'||ontology.source_format!=='alchlang'||ontology.source.sha256!==entry.source_sha256||ontology.ontology_admitted!==false||ontology.authority_effect!=='none')fail('entry composition ontology '+entry.id);
   if(project.schema_version!=='domainspec.project/v2'||certificate.compiler?.package!=='@domainspec-v2/cli'||certificate.authority_effect!=='none')fail('entry Craft compilation '+entry.id);
   entryRecords.push({...entry,manifest_sha256:digest(childManifest),ontology_sha256:digest(ontologyBytes),craft_project_sha256:digest(projectBytes),compiler_certificate_sha256:digest(certificateBytes),environment_references:deployment.environment_references});
  }
  const imports=entryRecords.map(entry=>`import * as entry_${entry.id} from '../../entries/${entry.id}/app/function/index.mjs';`).join('\n');
  const table=entryRecords.map(entry=>`${JSON.stringify(entry.id)}:entry_${entry.id}`).join(',');
  const routes=JSON.stringify(entryRecords.map(entry=>({id:entry.id,...entry.route})),null,2);
  write('app/service/index.mjs',`${imports}\nconst entrypoints={${table}};\nexport const routes=${routes};\nexport async function invoke(entry,input,env={},io={}){const selected=entrypoints[entry];if(!selected){const error=new Error('SERVICE_ENTRY_NOT_FOUND');error.code='SERVICE_ENTRY_NOT_FOUND';throw error;}return selected.invoke(input,env,io);}\nexport function createInvoker(entry,observe){const selected=entrypoints[entry];if(!selected){const error=new Error('SERVICE_ENTRY_NOT_FOUND');error.code='SERVICE_ENTRY_NOT_FOUND';throw error;}return selected.createInvoker(observe);}\nexport async function handler(request,env={},io={}){const url=new URL(request.url),samePath=routes.filter(route=>route.path===url.pathname);if(!samePath.length)return Response.json({error:'NOT_FOUND'},{status:404});const route=samePath.find(route=>route.method===request.method);if(!route)return Response.json({error:'METHOD_NOT_ALLOWED'},{status:405});return entrypoints[route.id].handler(request,env,{...io,signal:io.signal??request.signal});}\nexport default {fetch:handler};\n`);
  write('app/service/server.mjs',`import {createServer} from 'node:http';\nimport {handler} from './index.mjs';\nconst server=createServer(async(req,res)=>{try{const request=new Request('http://localhost'+req.url,{method:req.method,headers:req.headers,...(!['GET','HEAD'].includes(req.method)?{body:req,duplex:'half'}:{})});const out=await handler(request,process.env);res.writeHead(out.status,Object.fromEntries(out.headers));res.end(Buffer.from(await out.arrayBuffer()));}catch{res.writeHead(500,{'content-type':'application/json'});res.end('{"error":"FUNCTION_INTERNAL"}');}});\nserver.requestTimeout=30000;server.headersTimeout=15000;server.listen(Number(process.env.PORT??3000),process.env.HOST??'127.0.0.1',()=>console.log(JSON.stringify({address:server.address()})));\n`);
  write('provenance/service/source.alch',compiled.source);
  write('provenance/service/ontology.json',JSON.stringify(compiled.ontology,null,2)+'\n');
  const trace={schema_version:'alchlang.service-assembly-trace/v1',service:{id:compiled.service.id,ontology:compiled.service.ontology},source:{path:path.basename(compiled.sourcePath),sha256:compiled.source_sha256},entries:entryRecords.map(entry=>({id:entry.id,ontology:entry.ontology,source:entry.source,source_sha256:entry.source_sha256,composition_ontology_sha256:entry.ontology_sha256,craft_project_sha256:entry.craft_project_sha256,compiler_certificate_sha256:entry.compiler_certificate_sha256,manifest_sha256:entry.manifest_sha256,route:entry.route,input:entry.input,output:entry.output})),pipeline:['alch-source','composition-ontology','craft-project','compiled-entry','service-assembly'],authority_effect:'none'};
  write('evidence/service/assembly-trace.json',JSON.stringify(trace,null,2)+'\n');
  const deployment={schema_version:'alchlang.portable-http-service/v1',entry:'app/service/index.mjs#handler',launcher:'app/service/server.mjs',routes:entryRecords.map(entry=>({id:entry.id,...entry.route,input:entry.input,output:entry.output,auth_env:entry.auth_env,source:entry.source,source_sha256:entry.source_sha256,manifest_sha256:entry.manifest_sha256})),environment_references:[...new Set(entryRecords.flatMap(entry=>entry.environment_references))].sort(),provisioned:false,authority_effect:'none'};
  write('deployment.json',JSON.stringify(deployment,null,2)+'\n');
  write('package.json',JSON.stringify({name:'alch-service-'+compiled.service.id.toLowerCase(),private:true,type:'module',engines:{node:'>=26.8.1'},scripts:{start:'node app/service/server.mjs'}},null,2)+'\n');
  for(const entry of compiled.entries)assertModuleSources(entry.tree);if(readFileSync(compiled.sourcePath,'utf8')!==compiled.source)fail('source drift');
  const inventory=Object.fromEntries(files(stage).sort().map(file=>[path.relative(stage,file).split(path.sep).join('/'),digest(readFileSync(file))]));
  write('manifest.json',JSON.stringify({schema_version:'alchlang.service-build/v1',profile:'service-v1',source_sha256:compiled.source_sha256,entries:compiled.entries.map(entry=>entry.id),files:inventory,authority_effect:'none'},null,2)+'\n');
  const weight=(file:string)=>file===path.join(stage,'manifest.json')?2:file.endsWith('/manifest.json')?1:0;
  mkdirSync(output);const directories=new Set([output]);for(const file of files(stage).sort((a,b)=>weight(a)-weight(b))){const relative=path.relative(stage,file);let parent=output;for(const part of path.dirname(relative).split(path.sep).filter(part=>part!=='.')){parent=path.join(parent,part);if(!directories.has(parent)){mkdirSync(parent);directories.add(parent);}}linkSync(file,path.join(output,relative));}
  return {status:'built',profile:'service-v1',output,source_sha256:compiled.source_sha256,entries:compiled.entries.length,files:Object.keys(inventory).length,authority_effect:'none'};
 }finally{rmSync(stage,{recursive:true,force:true});}
}

/** Preparation owns scratch graph materialization. Planning writes nothing and
 * never invokes publishing builders. Open questions: PE08/10 final closure. */
const servicePreparations=new WeakMap<object,string>();
export async function prepareServicePlan(sourcePath:string){
 const service=compileService(sourcePath),prepared=[];
 try{for(const entry of service.entries)prepared.push(await prepareFunctionPlan(entry.tree.path));const result=Object.freeze({service,functions:Object.freeze(prepared)});servicePreparations.set(result,digest(JSON.stringify(result)));return result;}
 catch(error){for(const item of prepared)disposePreparedFunction(item);throw error;}
}
export function assertPreparedServiceCurrent(prepared:Awaited<ReturnType<typeof prepareServicePlan>>){
 if(servicePreparations.get(prepared)!==digest(JSON.stringify(prepared)))throw Error('SERVICE_PLAN_UNREGISTERED_OR_CHANGED');
 if(readFileSync(prepared.service.sourcePath,'utf8')!==prepared.service.source)throw Error('SERVICE_PLAN_SOURCE_STALE');
 for(const fn of prepared.functions)assertPreparedFunctionCurrent(fn);
}
export function planPreparedService(prepared:Awaited<ReturnType<typeof prepareServicePlan>>){
 if(servicePreparations.get(prepared)!==digest(JSON.stringify(prepared)))throw Error('SERVICE_PLAN_UNREGISTERED_OR_CHANGED');
 return Object.freeze({service:prepared.service,functions:Object.freeze(prepared.functions.map(planPreparedFunction)),authority_effect:'none' as const});
}
export function disposePreparedService(prepared:Awaited<ReturnType<typeof prepareServicePlan>>){
 if(!servicePreparations.has(prepared))throw Error('SERVICE_PLAN_UNREGISTERED_OR_CHANGED');servicePreparations.delete(prepared);for(const fn of prepared.functions)disposePreparedFunction(fn);
}
