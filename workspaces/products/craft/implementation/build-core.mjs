// Mutable SDK build. Existing materializer receives actual selected local tools;
// unrelated container pins stay intact. Open Questions: README.md.
import {mkdirSync,cpSync,writeFileSync,readFileSync,realpathSync,existsSync,symlinkSync} from 'node:fs';import {createHash} from 'node:crypto';import path from 'node:path';import {fileURLToPath,pathToFileURL} from 'node:url';import {spawnSync} from 'node:child_process';
import {labRoot as root} from './source-bindings.mjs';
const core=path.join(import.meta.dirname,'cli'),front=path.join(import.meta.dirname,'alchlang');
const sha=bytes=>createHash('sha256').update(bytes).digest('hex');
export function buildCore(destination,{node=process.execPath,inPlaceLogDirectory}={}){
 if(!path.isAbsolute(destination))throw Error('Absolute task-owned SDK build destination required');
 if(path.resolve(destination)===core){if(!inPlaceLogDirectory)throw Error('In-place Core build requires a separate proof-owned log directory');return buildCoreInPlace(inPlaceLogDirectory,{node});}if(inPlaceLogDirectory!==undefined)throw Error('In-place logs require the existing Core source root');
 if(!path.isAbsolute(destination))throw Error('Absolute task-owned SDK build destination required');mkdirSync(destination,{recursive:true});const checks=[];
 const run=command=>{const result=spawnSync(command[0],command.slice(1),{cwd:root,encoding:'utf8',maxBuffer:8*1024*1024});checks.push({command,status:result.status});if(result.status!==0)throw Error(result.stdout+'\n'+result.stderr);return result.stdout;};
 const compiler=realpathSync(path.join(front,'node_modules/typescript/bin/tsc')),compilerRoot=path.dirname(path.dirname(compiler)),compilerManifest=path.join(compilerRoot,'package.json'),compilerMeta=JSON.parse(readFileSync(compilerManifest,'utf8')),nodeVersion=run([node,'--version']).trim().replace(/^v/,'');
 if(compilerMeta.name!=='typescript'||nodeVersion!=='26.12.1')throw Error('Selected actual TypeScript compiler and Node26.12.1 required');
 const toolchainFile=path.join(destination,'LOCAL-BUILD-TOOLCHAIN.json'),toolchain={schema_version:'craft.selected-local-node-typescript/v1',node:{version:nodeVersion,path:realpathSync(node),sha256:sha(readFileSync(node))},typescript:compilerMeta.version,compiler:{path:compiler,sha256:sha(readFileSync(compiler)),manifest_sha256:sha(readFileSync(compilerManifest))},authority_effect:'none',open_questions_ref:'implementation/craft-ai-reference-build/local-suite/README.md#open-questions'};writeFileSync(toolchainFile,JSON.stringify(toolchain,null,2)+'\n');
 // Materialization writes native JS, generated source pins and profile metadata.
 // Its original owner must therefore run over a copied source closure, never the
 // working checkout when constructing a separate package.
 for(const name of ['package.json','contracts','profiles','src','tools'])cpSync(path.join(core,name),path.join(destination,name),{recursive:true});
 for(const name of ['scripts/stage-commerce-template.mjs']){mkdirSync(path.dirname(path.join(destination,name)),{recursive:true});cpSync(path.join(core,name),path.join(destination,name));}
 const stagedConfig=JSON.parse(readFileSync(path.join(core,'tsconfig.json'),'utf8'));stagedConfig.extends=realpathSync(path.resolve(core,stagedConfig.extends));writeFileSync(path.join(destination,'tsconfig.json'),JSON.stringify(stagedConfig,null,2)+'\n');
 // Build-only dependency lookup for the unmodified native materializer. These
 // selected installed type declarations are read, not materialized or shipped.
 const types=path.join(destination,'node_modules/@types');mkdirSync(path.dirname(types),{recursive:true});if(!existsSync(types))symlinkSync(realpathSync(path.join(front,'node_modules/@types')),types,'dir');
 const materializer=path.join(destination,'tools/materialize-u0-runtime.mjs'),selectedTools=['--toolchain',toolchainFile,'--compiler',compiler];run([node,materializer,'--write',...selectedTools]);
 run([node,compiler,'-p',path.join(destination,'tsconfig.json'),'--outDir',path.join(destination,'dist'),'--declaration','true','--declarationMap','false','--sourceMap','false','--typeRoots',path.join(front,'node_modules/@types'),'--pretty','false']);
 run([node,materializer,'--write','--profile','--compiled-root',destination,...selectedTools]);run([node,path.join(destination,'scripts/stage-commerce-template.mjs')]);
 const result={schema_version:'craft.mutable-sdk-build/v1',packageRoot:destination,version:JSON.parse(readFileSync(path.join(destination,'package.json'))).version,node,toolchain:{path:toolchainFile,sha256:sha(readFileSync(toolchainFile)),node:nodeVersion,typescript:compilerMeta.version},checks,publication:false};writeFileSync(path.join(destination,'WORKING-BUILD.json'),JSON.stringify(result,null,2)+'\n');return result;
}

/** Describe the existing build commands without writing or compiling anything.
 * Only the original U0 owner receives explicit selected local tool metadata;
 * original package checks remain in their declared order. */
export function planInPlaceCoreBuild(logDirectory,{node=process.execPath}={}){
 if(!path.isAbsolute(logDirectory)||path.resolve(logDirectory)===core||path.resolve(logDirectory).startsWith(core+path.sep))throw Error('Separate absolute proof-owned build log directory required');
 const compiler=realpathSync(path.join(front,'node_modules/typescript/bin/tsc')),compilerRoot=path.dirname(path.dirname(compiler)),compilerManifest=path.join(compilerRoot,'package.json'),compilerMeta=JSON.parse(readFileSync(compilerManifest,'utf8'));
 const version=spawnSync(node,['--version'],{encoding:'utf8'});if(version.status!==0)throw Error('Selected existing Node unavailable');const nodeVersion=version.stdout.trim().replace(/^v/,'');if(nodeVersion!=='26.12.1'||compilerMeta.name!=='typescript')throw Error('Selected actual TypeScript compiler and Node26.12.1 required');
 const selectedNode=realpathSync(node),npm=realpathSync(path.resolve(path.dirname(selectedNode),'../lib/node_modules/npm/bin/npm-cli.js')),toolchainFile=path.join(logDirectory,'LOCAL-BUILD-TOOLCHAIN.json'),materializer=path.join(core,'tools/materialize-u0-runtime.mjs'),selectedTools=['--toolchain',toolchainFile,'--compiler',compiler];
 const toolchain={schema_version:'craft.selected-local-node-typescript/v1',node:{version:nodeVersion,path:selectedNode,sha256:sha(readFileSync(selectedNode))},typescript:compilerMeta.version,compiler:{path:compiler,sha256:sha(readFileSync(compiler)),manifest_sha256:sha(readFileSync(compilerManifest))},authority_effect:'none',open_questions_ref:'implementation/craft-ai-reference-build/local-suite/README.md#open-questions'};
 const declared=JSON.parse(readFileSync(path.join(core,'package.json'),'utf8')).scripts.build,commands=[];
 for(const part of declared.split(' && ')){
  const script=/^npm run ([a-z0-9:-]+)$/.exec(part)?.[1];
  if(script==='u0-runtime:check'){commands.push({owner:'u0-runtime:materialize',command:[selectedNode,materializer,'--write',...selectedTools],cwd:core});commands.push({owner:script,command:[selectedNode,materializer,...selectedTools],cwd:core});}
  else if(script==='u0-profile:check'){
   commands.push({owner:'u0-profile:materialize',command:[selectedNode,materializer,'--write','--profile','--compiled-root',core,...selectedTools],cwd:core});
   commands.push({owner:script,command:[selectedNode,materializer,'--profile','--compiled-root',core,...selectedTools],cwd:core});
  }else if(script)commands.push({owner:script,command:[selectedNode,npm,'run',script],cwd:core});
  else if(part==='tsc -p tsconfig.json')commands.push({owner:'typescript',command:[selectedNode,compiler,'-p',path.join(core,'tsconfig.json'),'--typeRoots',path.join(front,'node_modules/@types'),'--pretty','false'],cwd:core});
  else if(part==='node scripts/stage-commerce-template.mjs')commands.push({owner:'commerce-template',command:[selectedNode,path.join(core,'scripts/stage-commerce-template.mjs')],cwd:core});
  else throw Error('Unrecognized original Core build command: '+part);
 }
 if(commands.filter(c=>c.owner==='u0-runtime:check').length!==1||commands.filter(c=>c.owner==='typescript').length!==1||commands.filter(c=>c.owner==='u0-profile:check').length!==1)throw Error('Original Core build owners required');
 return {packageRoot:core,node:selectedNode,toolchainFile,reportFile:path.join(logDirectory,'WORKING-BUILD.json'),toolchain,commands,generated_outputs:[path.join(core,'dist'),path.join(core,'src/profile-engine/u0-runtime-pins.generated.ts'),path.join(core,'profiles/node-http-entry-u0-v4/profile.json'),...['u0-json-decode.js','u0-values.js','u0-json-encode.js','application-http.mjs'].map(f=>path.join(core,'profiles/node-http-entry-u0-v4/runtime',f)),...['sqlite-physical-layout.js','sqlite-unit-of-work.js'].map(f=>path.join(core,'profiles/commerce-local-v1-candidate/runtime',f)),toolchainFile,path.join(logDirectory,'WORKING-BUILD.json')]};
}
function buildCoreInPlace(logDirectory,{node=process.execPath}={}){
 const plan=planInPlaceCoreBuild(logDirectory,{node}),checks=[];mkdirSync(logDirectory,{recursive:true});writeFileSync(plan.toolchainFile,JSON.stringify(plan.toolchain,null,2)+'\n');
 for(const step of plan.commands){const result=spawnSync(step.command[0],step.command.slice(1),{cwd:step.cwd,env:{...process.env,PATH:path.dirname(plan.node)+path.delimiter+process.env.PATH},encoding:'utf8',maxBuffer:8*1024*1024});checks.push({owner:step.owner,command:step.command,cwd:step.cwd,status:result.status});if(result.status!==0)throw Error(step.owner+'\n'+result.stdout+'\n'+result.stderr);}
 const result={schema_version:'craft.mutable-sdk-build/v1',mode:'in-place',packageRoot:core,version:JSON.parse(readFileSync(path.join(core,'package.json'))).version,node:plan.node,toolchain:{path:plan.toolchainFile,sha256:sha(readFileSync(plan.toolchainFile)),node:plan.toolchain.node.version,typescript:plan.toolchain.typescript},checks,generated_outputs:plan.generated_outputs,publication:false};writeFileSync(plan.reportFile,JSON.stringify(result,null,2)+'\n');return result;
}
if(process.argv[1]&&pathToFileURL(path.resolve(process.argv[1])).href===import.meta.url){if(process.argv[2]==='--in-place'){if(process.argv.length!==4||!path.isAbsolute(process.argv[3]))throw Error('Supply --in-place and an absolute proof-owned log directory');console.log(JSON.stringify(buildCore(core,{inPlaceLogDirectory:process.argv[3]})));}else{if(!process.argv[2])throw Error('Absolute task-owned build destination required');console.log(JSON.stringify(buildCore(path.resolve(process.argv[2]))));}}
