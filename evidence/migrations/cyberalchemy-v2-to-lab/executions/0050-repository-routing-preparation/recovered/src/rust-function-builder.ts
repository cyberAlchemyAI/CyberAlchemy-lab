import {collectApplicationDomain,writeApplicationFile} from './application-layout.js';
import {loadModuleTree,assertModuleSources,moduleEnvironment,type ModuleTree} from './module-source.js';
import {execFileSync} from 'node:child_process';
import {readFileSync,writeFileSync,mkdirSync,mkdtempSync,readdirSync,cpSync,rmSync,existsSync,linkSync,chmodSync} from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import {parseDeclarativeSource} from './declarative-profile.js';
import {deriveOntology} from './derived-ontology.js';
import {loadDomainSpecCompiler} from './domainspec-cli.js';
import {buildDomainSpec} from './domainspec-project-writer.js';
import {digest,EXACT_PROFILE} from './domainspec-profile.js';
const files=(p:string):string[]=>readdirSync(p,{withFileTypes:true}).flatMap(e=>e.isDirectory()?files(path.join(p,e.name)):[path.join(p,e.name)]);
export async function buildRustFunction(sourcePath:string,output:string,loaded?:ModuleTree){
 if(path.extname(sourcePath)!=='.alch')throw Error('FUNCTION_SOURCE_EXTENSION');
 const source=readFileSync(sourcePath,'utf8'),tree=loaded??loadModuleTree(sourcePath),parsed=tree.parsed;if(tree.source!==source)throw Error('FUNCTION_MODULE_SOURCE_DRIFT');output=path.resolve(output);if(existsSync(output))throw Error('FUNCTION_OUTPUT_EXISTS');
 parsed.model.endpoint={...parsed.model.endpoint,target:'rust-http',runtime:'rust>=1.94'};
 const compiler=await loadDomainSpecCompiler(),P=compiler.applicationPaths;
 const compiled=compiler.compileDeclarativeFunction(parsed.contract),ontology=deriveOntology(parsed,compiled.trace,path.resolve(sourcePath));
 const stage=mkdtempSync(path.join(path.dirname(output),'.alch-rust-'));
 const write=(name:string,bytes:string|Buffer)=>writeApplicationFile(stage,name,bytes);
 try{
  if(Object.keys(tree.children).length){mkdirSync(path.join(stage,'modules'));for(const [alias,child]of Object.entries(tree.children))await buildRustFunction(child.path,path.join(stage,'modules',alias),child);write(P.modules,JSON.stringify(Object.fromEntries(Object.entries(tree.children).map(([alias,child])=>[alias,{source_sha256:digest(child.source),manifest_sha256:digest(readFileSync(path.join(stage,'modules',alias,'manifest.json')))}])),null,2)+'\n');}
  const input=path.join(stage,'.inputs');mkdirSync(input);const core=path.join(input,'domain.alch');writeFileSync(core,parsed.coreSource);writeFileSync(core+'.domainspec.json',JSON.stringify(parsed.bindings));
  await buildDomainSpec(core,path.join(input,'domain'),{profile:EXACT_PROFILE,generate:true,applicationLayout:true,language:'rust',composition:{source_text:source,contract:parsed.contract,model:parsed.model,bindings:parsed.boundaryBindings,ontology}});
  collectApplicationDomain(path.join(input,'domain'),stage,P);
  const manifest=path.join(stage,P.cargo);
  // Reuse Cargo's incremental cache without placing compiler intermediates in the candidate.
  const targetBase=process.env.ALCHLANG_RUST_TARGET_DIR??path.join(os.tmpdir(),'alchlang-rust-target');
  const target=path.join(targetBase,digest(files(stage).filter(p=>/\.(rs|toml)$/.test(p)).sort().map(p=>path.relative(stage,p)+digest(readFileSync(p))).join('\n')));
  const rustc=execFileSync('rustc',['--version'],{encoding:'utf8'}).trim();
  execFileSync('cargo',['build','--offline','--manifest-path',manifest,'--target-dir',target],{encoding:'utf8',stdio:['ignore','pipe','pipe'],maxBuffer:16*1024*1024});
  write(P.binary,readFileSync(path.join(target,'debug/alch-function')));chmodSync(path.join(stage,P.binary),0o755);
  writeFileSync(path.join(stage,'deployment.json'),JSON.stringify({schema_version:'alchlang.rust-http/v1',target:'rust-http',entry:P.binary,library:P.rustLibrary,runtime:rustc,platform:process.platform,architecture:process.arch,environment_references:moduleEnvironment(tree),provisioned:false,authority_effect:'none'},null,2)+'\n');
  rmSync(input,{recursive:true});assertModuleSources(tree);if(readFileSync(sourcePath,'utf8')!==source)throw Error('FUNCTION_SOURCE_DRIFT');
  const inventory=Object.fromEntries(files(stage).sort().map(p=>[path.relative(stage,p),digest(readFileSync(p))]));
  writeFileSync(path.join(stage,'manifest.json'),JSON.stringify({schema_version:'alchlang.function-build/v1',output_layout:compiler.applicationLayoutId,profile:'declarative-function-v1',target:'rust-http',source_sha256:digest(source),toolchain:rustc,files:inventory,authority_effect:'none'},null,2)+'\n');
  mkdirSync(output);for(const p of files(stage).sort((a,b)=>(a===path.join(stage,'manifest.json')?2:a.endsWith('/manifest.json')?1:0)-(b===path.join(stage,'manifest.json')?2:b.endsWith('/manifest.json')?1:0))){const to=path.join(output,path.relative(stage,p));mkdirSync(path.dirname(to),{recursive:true});linkSync(p,to);}
  return {status:'built',target:'rust-http',output,source_sha256:digest(source),files:Object.keys(inventory).length,authority_effect:'none'};
 }finally{rmSync(stage,{recursive:true,force:true});}
}

export async function traceRustFunction(sourcePath:string,inputPath:string){
 const bytes=readFileSync(inputPath);if(bytes.length>1048576)throw Error('TRACE_INPUT_LIMIT');JSON.parse(bytes.toString('utf8'));
 const root=mkdtempSync(path.join(os.tmpdir(),'alch-rust-trace-'));
 try{const out=path.join(root,'bundle');await buildRustFunction(sourcePath,out);try{return JSON.parse(execFileSync(path.join(out,(await loadDomainSpecCompiler()).applicationPaths.binary),['trace'],{input:bytes,encoding:'utf8',maxBuffer:8*1024*1024}));}catch(e:any){if(e.status===1&&e.stdout)return JSON.parse(e.stdout);throw e;}}finally{rmSync(root,{recursive:true,force:true});}
}
