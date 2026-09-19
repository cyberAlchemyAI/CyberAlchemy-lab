import {collectApplicationDomain,writeApplicationFile} from './application-layout.js';
import {loadModuleTree,assertModuleSources,moduleEnvironment,type ModuleTree} from './module-source.js';
import os from 'node:os';
import {deriveOntology,explainOntology} from './derived-ontology.js';
import {parseDeclarativeSource} from './declarative-profile.js';
import {loadDomainSpecCompiler} from './domainspec-cli.js';
import {execFileSync} from 'node:child_process';
import {existsSync,readFileSync,writeFileSync,mkdirSync,mkdtempSync,readdirSync,linkSync,rmSync,lstatSync} from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {parseFunctionSource} from './function-profile.js';
import {buildDomainSpec,checkDomainSpec} from './domainspec-project-writer.js';
import {digest,EXACT_PROFILE} from './domainspec-profile.js';
const implementation=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const files=(p:string):string[]=>readdirSync(p,{withFileTypes:true}).flatMap(e=>e.isDirectory()?files(path.join(p,e.name)):[path.join(p,e.name)]);
function readSource(p:string){if(path.extname(p)!=='.alch')throw Error('FUNCTION_SOURCE_EXTENSION');return readFileSync(p,'utf8');}
export function resolveTypeScriptCompiler(domainSpecPackageRoot:string,explicitCompiler?:string,compilerPackageRoot=implementation){
 if(explicitCompiler)return path.resolve(explicitCompiler);
 const local=path.join(compilerPackageRoot,'node_modules/.bin/tsc');
 return path.resolve(existsSync(local)?local:path.join(domainSpecPackageRoot,'../node_modules/.bin/tsc'));
}
export async function inspectFunctionOntology(sourcePath:string,selector?:string){
 const tree=loadModuleTree(sourcePath),parsed=tree.parsed;await checkTree(tree);
 const compiled=(await loadDomainSpecCompiler()).compileDeclarativeFunction(parsed.contract);
 const ontology=deriveOntology(parsed,compiled.trace,path.resolve(sourcePath));
 await checkCompleteProject(parsed,readSource(sourcePath),ontology);
 return selector?explainOntology(ontology,selector):ontology;
}
function isDeclarative(value:ReturnType<typeof parseFunctionSource>):value is ReturnType<typeof parseDeclarativeSource>{return 'contract' in value&&'ontologySource' in value;}
function parse(source:string){return /^profile declarative-function-v1$/m.test(source)?parseDeclarativeSource(source):parseFunctionSource(source);}
function projectComposition(parsed:ReturnType<typeof parseDeclarativeSource>,source:string,ontology:unknown){return {source_text:source,contract:parsed.contract,model:parsed.model,bindings:parsed.boundaryBindings,ontology};}
async function checkCompleteProject(parsed:ReturnType<typeof parseDeclarativeSource>,source:string,ontology:unknown){
 const stage=mkdtempSync(path.join(os.tmpdir(),'alch-project-check-'));
 try{const core=path.join(stage,'domain.alch');writeFileSync(core,parsed.coreSource);writeFileSync(core+'.domainspec.json',JSON.stringify(parsed.bindings));return await checkDomainSpec(core,{profile:EXACT_PROFILE,composition:projectComposition(parsed,source,ontology)});}finally{rmSync(stage,{recursive:true,force:true});}
}
async function checkTree(tree:ModuleTree,target?:string){
 if(target){tree.parsed.model.endpoint={...tree.parsed.model.endpoint,target,runtime:target==='rust-http'?'rust>=1.94':'node>=26.8.1'};}
 for(const child of Object.values(tree.children))await checkTree(child,target??tree.parsed.model.endpoint.target);
 const compiled=(await loadDomainSpecCompiler()).compileDeclarativeFunction(tree.parsed.contract);const ontology=deriveOntology(tree.parsed,compiled.trace,tree.path);await checkCompleteProject(tree.parsed,tree.source,ontology);assertModuleSources(tree);
}
export async function checkFunction(sourcePath:string,target?:string){
 if(target&&!['node-http','rust-http'].includes(target))throw Error('FUNCTION_TARGET');const source=readSource(sourcePath),tree=/^profile declarative-function-v1$/m.test(source)?loadModuleTree(sourcePath):null,parsed=tree?.parsed??parse(source);
 if(!tree&&(target??parsed.model.endpoint.target)==='rust-http')throw Error(`DS_TARGET_UNSUPPORTED: ${path.resolve(sourcePath)}:1: rust-http requires declarative-function-v1`);
 if(tree)await checkTree(tree,target);return {status:'valid',profile:tree?'declarative-function-v1':'function-v1',endpoint:parsed.model.endpoint.id,authority_effect:'none'};
}
export async function buildFunction(sourcePath:string,output:string,loaded?:ModuleTree){
 const source=readSource(sourcePath),tree=loaded??(/^profile declarative-function-v1$/m.test(source)?loadModuleTree(sourcePath):null),parsed=tree?.parsed??parse(source);if(tree&&tree.source!==source)throw Error('FUNCTION_MODULE_SOURCE_DRIFT');if(loaded)parsed.model.endpoint={...parsed.model.endpoint,target:'node-http',runtime:'node>=26.8.1'};output=path.resolve(output);
 if(parsed.model.endpoint.target==='rust-http'){const {buildRustFunction}=await import('./rust-function-builder.js');return buildRustFunction(sourcePath,output);}
 const profile=isDeclarative(parsed)?'declarative-function-v1':'function-v1';
 let composition=isDeclarative(parsed)?(await loadDomainSpecCompiler()).compileDeclarativeFunction(parsed.contract):null;
 if(composition&&(composition.trace as any)?.observation_profile!=='domainspec.declarative-observation/v1')throw Error('DOMAINSPEC_TRACE_BUILD_REQUIRED');
 let ontology=isDeclarative(parsed)?deriveOntology(parsed,composition!.trace,path.resolve(sourcePath)):null;
 try{lstatSync(output);throw Error('FUNCTION_OUTPUT_EXISTS');}catch(e){if((e as any).code!=='ENOENT')throw e;}
 const compiler=await loadDomainSpecCompiler(),P=compiler.applicationPaths,relative=compiler.outputImport.bind(compiler);
 const stage=mkdtempSync(path.join(path.dirname(output),'.alch-function-'));
 const write=(name:string,bytes:string|Buffer)=>writeApplicationFile(stage,name,bytes);
 try{
  if(tree&&Object.keys(tree.children).length){mkdirSync(path.join(stage,'modules'));for(const [alias,child]of Object.entries(tree.children))await buildFunction(child.path,path.join(stage,'modules',alias),child);write(P.modules,JSON.stringify(Object.fromEntries(Object.entries(tree.children).map(([alias,child])=>[alias,{source_sha256:digest(child.source),manifest_sha256:digest(readFileSync(path.join(stage,'modules',alias,'manifest.json')))}])),null,2)+'\n');}
  const inputDir=path.join(stage,'.inputs');mkdirSync(inputDir);
  const core=path.join(inputDir,'domain.alch');writeFileSync(core,parsed.coreSource);writeFileSync(core+'.domainspec.json',JSON.stringify(parsed.bindings,null,2)+'\n');
  const domain=path.join(inputDir,'domain');await buildDomainSpec(core,domain,{profile:EXACT_PROFILE,generate:true,applicationLayout:true,...(isDeclarative(parsed)?{composition:projectComposition(parsed,source,ontology)}:{})});
  collectApplicationDomain(domain,stage,P);
  if(composition){
   const generated=path.join(stage,'provenance/function');
   composition={source:readFileSync(path.join(stage,P.behavior),'utf8'),contract:JSON.parse(readFileSync(path.join(generated,'composition.json'),'utf8')),trace:JSON.parse(readFileSync(path.join(stage,P.compositionTrace),'utf8'))};
   ontology=JSON.parse(readFileSync(path.join(generated,'ontology.json'),'utf8'));
   for(const name of ['function.json','bindings.json','source.alch'])if(readFileSync(path.join(generated,name),'utf8')!==(name==='source.alch'?source:JSON.stringify(name==='function.json'?parsed.model:('boundaryBindings' in parsed?parsed.boundaryBindings:[]),null,2)+'\n'))throw Error('FUNCTION_PROJECT_ARTIFACT_MISMATCH');
  }
  const js=path.join(stage,P.typescriptLib),tsRoot=path.join(stage,P.typescriptSource);
  const tsc=resolveTypeScriptCompiler(compiler.binding.package_root,process.env.ALCHLANG_TYPESCRIPT_COMPILER);
  execFileSync(process.execPath,[tsc,'--strict','--skipLibCheck','--target','ES2022','--module','commonjs','--rootDir',tsRoot,'--outDir',js,...files(tsRoot).filter(p=>p.endsWith('.ts'))],{cwd:stage,encoding:'utf8'});
  writeFileSync(path.join(js,'package.json'),'{"type":"commonjs"}\n');
  write(P.runtime,readFileSync(path.join(implementation,composition?'dist/boundary-runtime.js':'dist/function-runtime.js')));
  if(composition)write(P.traceRuntime,readFileSync(path.join(implementation,'dist/invocation-trace.js')));
  else {write(P.model,JSON.stringify(parsed.model,null,2)+'\n');write(P.source,source);}
  writeFileSync(path.join(stage,'package.json'),JSON.stringify({name:'alch-function-'+parsed.model.endpoint.id.toLowerCase(),private:true,type:'module',engines:{node:'>=26.8.1'},scripts:{start:`node ${P.launcher}`}},null,2)+'\n');
  write(P.entry,composition?`${Object.keys(tree?.children??{}).map(alias=>`import * as module_${alias} from '${relative(P.entry,`modules/${alias}/${P.entry}`)}';`).join('\n')}\nimport {createBoundary} from '${relative(P.entry,P.runtime)}';\nimport {createTracedInvoker} from '${relative(P.entry,P.traceRuntime)}';\nimport ontology from '${relative(P.entry,P.ontology)}' with {type:'json'};\nimport manifest from '${relative(P.entry,'manifest.json')}' with {type:'json'};\nimport {execute,validateInput} from '${relative(P.entry,P.behavior)}';\nimport api from '${relative(P.entry,P.api)}';\nimport model from '${relative(P.entry,P.model)}' with {type:'json'};\nimport bindings from '${relative(P.entry,P.bindings)}' with {type:'json'};\nconst modules={${Object.keys(tree?.children??{}).map(alias=>`${alias}:(input,env,io,observe)=>module_${alias}.createInvoker(observe).invoke(input,env,io)`).join(',')}};\nexport function createInvoker(observe){const relay=event=>{const n=ontology.nodes.find(n=>n.name===event.declaration)??ontology.nodes.find(n=>n.kind==='result');observe?.({...event,definition:event.definition??(n?{name:n.name,id:n.id,source:n.source,clauses:n.clauses}:null)});};return createBoundary(model,bindings,scope=>execute(scope,api,relay),scope=>validateInput(scope,relay),modules,relay,(scope,binding)=>execute(scope,api,relay,binding),(scope,binding)=>execute(scope,api,relay,binding,'input'));};\nexport const {invoke,handler}=createInvoker();\nexport const invokeWithTrace=createTracedInvoker(model,bindings,api,execute,validateInput,ontology,{...${JSON.stringify({source_sha256:digest(source),ontology_sha256:digest(JSON.stringify(ontology,null,2)+'\n'),behavior_sha256:composition?digest(composition.source):null,contract_sha256:composition?digest(JSON.stringify(composition.contract,null,2)+'\n'):null})},manifest},createBoundary,modules);\nexport default {fetch:handler};\n`:`import {createFunction} from '${relative(P.entry,P.runtime)}';\nimport api from '${relative(P.entry,P.api)}';\nimport model from '${relative(P.entry,P.model)}' with {type:'json'};\nexport const {invoke,handler}=createFunction(model,api);\nexport default {fetch:handler};\n`);
  write(P.launcher,`import {createServer} from 'node:http';\nimport {handler} from './index.mjs';\nconst server=createServer(async(req,res)=>{try{const request=new Request('http://localhost'+req.url,{method:req.method,headers:req.headers,...(!['GET','HEAD'].includes(req.method)?{body:req,duplex:'half'}:{})});const out=await handler(request,process.env);res.writeHead(out.status,Object.fromEntries(out.headers));res.end(Buffer.from(await out.arrayBuffer()));}catch{res.writeHead(500,{'content-type':'application/json'});res.end('{"error":"FUNCTION_INTERNAL"}');}});\nserver.requestTimeout=30000;server.headersTimeout=15000;\nserver.listen(Number(process.env.PORT??3000),process.env.HOST??'127.0.0.1',()=>console.log(JSON.stringify({address:server.address()})));\n`);
  const ep=parsed.model.endpoint;
  const requirements=tree?moduleEnvironment(tree):[ep.authEnv,...Object.values(parsed.model.integrations).flatMap((b:any)=>[b.urlEnv,b.secretEnv]).filter(Boolean)];
  writeFileSync(path.join(stage,'deployment.json'),JSON.stringify({schema_version:'alchlang.portable-http/v1',entry:P.entry+'#handler',launcher:P.launcher,target:ep.target,runtime:ep.runtime,limits:{request_bytes:ep.maxBytes,request_read_timeout_ms:ep.timeout},method:ep.method,path:ep.path,environment_references:[...new Set(requirements)],integrations:parsed.model.integrations,provisioned:false,authority_effect:'none'},null,2)+'\n');
  rmSync(inputDir,{recursive:true});
  if(tree)assertModuleSources(tree);
  if(readSource(sourcePath)!==source)throw Error('FUNCTION_SOURCE_DRIFT');
  const inventory=Object.fromEntries(files(stage).sort().map(p=>[path.relative(stage,p),digest(readFileSync(p))]));
  writeFileSync(path.join(stage,'manifest.json'),JSON.stringify({schema_version:'alchlang.function-build/v1',output_layout:compiler.applicationLayoutId,profile,source_sha256:digest(source),core_source_sha256:digest(parsed.coreSource),files:inventory,authority_effect:'none'},null,2)+'\n');
  // Reserve the exact destination; a concurrently created directory must not be replaced.
  mkdirSync(output);
  const directories=new Set([output]);
  for(const file of files(stage).sort((a,b)=>(a===path.join(stage,'manifest.json')?2:a.endsWith('/manifest.json')?1:0)-(b===path.join(stage,'manifest.json')?2:b.endsWith('/manifest.json')?1:0))){
   const relative=path.relative(stage,file);let parent=output;
   for(const part of path.dirname(relative).split(path.sep).filter(p=>p!=='.')){parent=path.join(parent,part);if(!directories.has(parent)){mkdirSync(parent);directories.add(parent);}}
   linkSync(file,path.join(output,relative)); // Exclusive creation, including the completion manifest last.
  }
  return {status:'built',profile,output,source_sha256:digest(source),files:Object.keys(inventory).length,authority_effect:'none'};
 }finally{rmSync(stage,{recursive:true,force:true});}
}
