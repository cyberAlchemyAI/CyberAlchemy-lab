import {domainSource,sourcePath} from '../../source-bindings.mjs';
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import crypto from 'node:crypto';
import {spawnSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
// Build-only owner. Installed consumers load actual packaged JS, never these sources.
// Open Questions: docs/U0-SHARED-CONTRACTS.md; J02 captures after final public builds.
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..'),profile=path.join(root,'profiles/node-http-entry-u0-v4');
const options=new Map();for(let i=2;i<process.argv.length;i++){const key=process.argv[i];if(['--write','--profile'].includes(key))continue;if(!['--toolchain','--compiler','--compiled-root'].includes(key)||options.has(key)||!process.argv[i+1]||!path.isAbsolute(process.argv[i+1]))throw Error('U0_BUILD_OPTIONS');options.set(key,fs.realpathSync(process.argv[++i]));}
const sha=bytes=>crypto.createHash('sha256').update(bytes).digest('hex');
const roles={decoder:{name:'u0-json-decode',ext:'js',exports:['decodeU0Json']},values:{name:'u0-values',ext:'js',exports:['formU0Submission','copyU0Submission']},encoder:{name:'u0-json-encode',ext:'js',exports:['checkU0EncoderConfiguration','encodeU0Outcome','encodeU0AdapterError','u0WireBounds']},handler:{name:'application-http',ext:'mjs',exports:['createU0HttpHandler','inspectU0HttpResponse']}};
const packageMeta=JSON.parse(fs.readFileSync(path.join(root,'package.json'),'utf8'));
const toolchain=JSON.parse(fs.readFileSync(options.get('--toolchain')??sourcePath('craft/toolchains/node-typescript/toolchain.json'),'utf8'));
if(process.versions.node!==toolchain.node.version)throw Error('U0_BUILD_NODE_VERSION');
const compiler=options.get('--compiler')??fs.realpathSync(path.join(root,'node_modules/typescript/bin/tsc')),compilerRoot=path.dirname(path.dirname(compiler)),compilerMeta=JSON.parse(fs.readFileSync(path.join(compilerRoot,'package.json'),'utf8'));
if(compilerMeta.name!=='typescript'||compilerMeta.version!==toolchain.typescript)throw Error('U0_BUILD_COMPILER_VERSION');
const write=process.argv.includes('--write'),profileOnly=process.argv.includes('--profile');
const set=(file,content)=>{if(write){if(!fs.existsSync(file)||!fs.readFileSync(file).equals(Buffer.from(content)))fs.writeFileSync(file,content);}else if(!fs.existsSync(file)||!fs.readFileSync(file).equals(Buffer.from(content)))throw Error('U0_BUILD_DRIFT:'+path.relative(root,file));};
if(!profileOnly){
 const temporary=fs.mkdtempSync(path.join(os.tmpdir(),'craft-u0-native-build-'));
 try{
  const sources=Object.values(roles).map(row=>path.join(profile,'runtime',row.name+(row.ext==='mjs'?'.mts':'.ts')));
  const command=[compiler,'--ignoreConfig','--target','ES2022','--module','NodeNext','--moduleResolution','NodeNext','--strict','--skipLibCheck','--types','node','--rootDir',root,'--outDir',temporary,...sources];
  const run=spawnSync(process.execPath,command,{cwd:root,encoding:'utf8'});if(run.status!==0)throw Error('U0_NATIVE_BUILD_FAILED\n'+run.stdout+run.stderr);
  for(const row of Object.values(roles)){const relative='runtime/'+row.name+'.'+row.ext;set(path.join(profile,relative),fs.readFileSync(path.join(temporary,'profiles/node-http-entry-u0-v4',relative)));}
 }finally{fs.rmSync(temporary,{recursive:true,force:true});}
}
const assets=Object.entries(roles).map(([role,row])=>{const relative='runtime/'+row.name+'.'+row.ext,bytes=fs.readFileSync(path.join(profile,relative));return {role,path:relative,sha256:sha(bytes),bytes:bytes.length,exports:row.exports};});
const build={node:process.versions.node,typescript:compilerMeta.version};
if(!profileOnly){
 const pin='// GENERATED from actual compiled U0 native assets. No future hashes.\n// Open Questions: docs/U0-SHARED-CONTRACTS.md.\nexport const U0_RUNTIME_PINS_V4='+JSON.stringify({assets,build},null,2)+' as const;\n';
 set(path.join(root,'src/profile-engine/u0-runtime-pins.generated.ts'),pin);
}else{
 const compiledRoot=options.get('--compiled-root')??root,compiledMeta=JSON.parse(fs.readFileSync(path.join(compiledRoot,'package.json'),'utf8'));
 if(compiledMeta.name!==packageMeta.name||compiledMeta.version!==packageMeta.version)throw Error('U0_BUILD_COMPILED_PACKAGE');
 const bytes=fs.readFileSync(path.join(compiledRoot,'dist/generation/configured-exact-uint64-source.js'));
 const descriptor={schema_version:'craft.profile-package/v4-candidate',id:'node-http-entry-u0-v4',version:'1.0.0',engine:'craft.profile-engine/v4-candidate',source_contract:'alchlang.business-spec/v2-candidate',recipe:'direct-entity-bool-operation/v2-candidate',abi:'craft.u0.pure-submission/v1-candidate',entry_access:'public',effects:'none',capabilities:[{role:'application-operation',descriptor_ref:'craft.u0.pure-submission/v1-candidate',recipe_ref:'direct-entity-bool-operation/v2-candidate'},{role:'http-dispatch',descriptor_ref:'node-http-entry-u0-v4',recipe_ref:'craft.u0.public-http/v1-candidate'}],configuration:{schema_version:'craft.operation-json-post/v2-candidate',method:'POST',pathname:'/confirm-delivery',body:'closed-submission',uint64_codec:'canonical-decimal-string',request_bytes:4096,response_bytes:1024,body_timeout_ms:2000},assets,scalar_producer:{path:'dist/generation/configured-exact-uint64-source.js',sha256:sha(bytes),bytes:bytes.length,export_name:'renderExactUInt64Support'},build,authority_effect:'none',open_questions_ref:'../../docs/U0-SHARED-CONTRACTS.md#open-questions'};
 set(path.join(profile,'profile.json'),JSON.stringify(descriptor,null,2)+'\n');
}
process.stdout.write(JSON.stringify({package:packageMeta.name,assets,build,mode:write?'materialized':'checked',profile:profileOnly,authority_effect:'none'})+'\n');
