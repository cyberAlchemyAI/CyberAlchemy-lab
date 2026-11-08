import {mkdirSync,mkdtempSync,readFileSync,writeFileSync,readdirSync,cpSync,rmSync,renameSync,existsSync} from 'node:fs';
import {resolve,join,relative,dirname,basename} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {createHash} from 'node:crypto';
import {buildPublicPolicy} from '../build-public-policy.mjs';
// Reproducible standalone composition. Open Questions: README.md.
const here=fileURLToPath(new URL('./',import.meta.url)),base=resolve(here,'..'),impl=resolve(base,'../../implementation');
const repository=resolve(base,'../../../../../../..');
const sha=bytes=>createHash('sha256').update(bytes).digest('hex');
const walk=p=>readdirSync(p,{withFileTypes:true}).flatMap(e=>e.isDirectory()?walk(join(p,e.name)):[join(p,e.name)]);
export async function buildLocalPattern(output){
 output=resolve(output);if(existsSync(output))throw Error('OUTPUT_EXISTS');
 const binding=JSON.parse(readFileSync(join(base,'compiler-binding.json'))),ds=resolve(repository,binding.package_root_relative_to_repository);
 if(sha(readFileSync(join(ds,'package.json')))!==binding.package_sha256)throw Error('COMPILER_PACKAGE_DRIFT');
 for(const [file,hash]of Object.entries(binding.dist_files))if(sha(readFileSync(join(ds,file)))!==hash)throw Error('COMPILER_INPUT_DRIFT: '+file);
 const stage=mkdtempSync(join(dirname(output),'.local-pattern-'));
 try{
  await buildPublicPolicy(stage,{localPattern:true});
  const native=join(stage,'native');mkdirSync(native);
  const sources=[...['host.mjs','dispatch.mjs','idempotency.mjs'].map(n=>join(base,n)),...['http-invocation-adapter.js','node-service-host.js'].map(n=>join(impl,'dist',n)),...['http-invocation.js','request-custody.js','sqlite-request-custody.js','custody-reconciliation.js'].map(n=>join(ds,'dist/runtime',n))];
  const names=new Set(sources.map(p=>basename(p))),nativeSources={};
  for(const file of sources){
   const bytes=readFileSync(file),code=bytes.toString().replace(/from (['"])([^'"]+)\1/g,(all,q,p)=>{
    if(p.startsWith('node:'))return all;
    if(!names.has(basename(p)))throw Error('UNBOUND_NATIVE_IMPORT: '+p);
    return `from ${q}./${basename(p)}${q}`;
   });
   writeFileSync(join(native,basename(file)),code);nativeSources[relative(repository,file)]=sha(bytes);
  }
  for(const name of ['runtime.mjs','start.mjs','fixture.mjs','configuration.example.json','README.md','PROTOCOL.md'])cpSync(join(here,name),join(stage,name));
  const modules={admission:'public-admission/app/function/index.mjs',service:'public-service/app/service/index.mjs',invocation:'provider-invocation/app/invocation/index.mjs',stream:'provider-stream/app/stream/index.mjs',custody:'request-custody/app/custody/index.mjs',streamError:'public-stream-error/app/function/index.mjs'};
  writeFileSync(join(stage,'index.mjs'),Object.entries(modules).map(([k,p])=>`import * as ${k} from './${p}';`).join('\n')+`
import {createLocalServer} from './runtime.mjs';
const policy={admissionMapper:admission.invoke,serviceFactory:service.createHandler,modelsMapper:service.functions.Models,capabilitiesMapper:service.functions.Capabilities,errorMapper:service.functions.Errors,streamErrorMapper:streamError.invoke,invocationFactory:invocation.createInvocation,streamFactory:stream.createSession,custodyFactory:custody.createCustody};
export const createServer=(config,env={})=>createLocalServer(policy,config,env);
`);
  writeFileSync(join(stage,'package.json'),JSON.stringify({name:'alch-local-inference-pattern',private:true,type:'module',engines:{node:'>=26.8.1'},scripts:{start:'node start.mjs'}},null,2)+'\n');
  const files=Object.fromEntries(walk(stage).sort().map(p=>[relative(stage,p),sha(readFileSync(p))]));
  const manifest={schema_version:'alch.local-inference-pattern/v1-candidate',protocol:'alch-local-text/v1',entry:'index.mjs',compiler:binding,native_sources:nativeSources,files,authority_effect:'none',open_questions_ref:'README.md#open-questions'};
  writeFileSync(join(stage,'manifest.json'),JSON.stringify(manifest,null,2)+'\n');
  if(existsSync(output))throw Error('OUTPUT_EXISTS');renameSync(stage,output);
  return {status:'built',output,files:Object.keys(files).length};
 }finally{rmSync(stage,{recursive:true,force:true});}
}
if(process.argv[1]&&pathToFileURL(resolve(process.argv[1])).href===import.meta.url){if(!process.argv[2])throw Error('Usage: node local-pattern/build.mjs /absolute/new/bundle');console.log(JSON.stringify(await buildLocalPattern(process.argv[2])));}
