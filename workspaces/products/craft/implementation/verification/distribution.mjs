/** Build unpublished local archives and a physically isolated offline consumer.
 * Open questions: README.md. No publication, shared-source mutation or host runtime copy.
 */
import assert from 'node:assert/strict';
import {mkdirSync,readFileSync,writeFileSync,copyFileSync,existsSync,readdirSync,lstatSync} from 'node:fs';
import path from 'node:path';
import {createHash} from 'node:crypto';
import {spawnSync} from 'node:child_process';
import {materializePackageBoundaries} from '../alchlang/scripts/materialize-package-boundaries.mjs';
import {stageNativePackage} from './build-native-package.mjs';
import {implementationRoot as root,upstreamRoot} from '../source-bindings.mjs';

const sha=file=>createHash('sha256').update(readFileSync(file)).digest('hex');
const json=file=>JSON.parse(readFileSync(file,'utf8'));
export const selectedNode=path.join(upstreamRoot,'.runtime/craft-release-2026-10-29/node-v26.12.1-linux-x64/bin/node');
const npm=path.resolve(path.dirname(selectedNode),'../lib/node_modules/npm/bin/npm-cli.js');
export const walk=directory=>readdirSync(directory,{withFileTypes:true}).flatMap(e=>
  ['node_modules','.git','.local','sdk-test'].includes(e.name)?[]:e.isDirectory()?walk(path.join(directory,e.name)):e.isFile()?[path.join(directory,e.name)]:[]);
export const pin=file=>({path:path.resolve(file),sha256:sha(file)});
export function cleanEnvironment(){
  const env={...process.env,PATH:path.dirname(selectedNode)+path.delimiter+process.env.PATH,npm_config_offline:'true',npm_config_logs_dir:path.join(root,'.local/npm-logs')};
  for(const key of Object.keys(env))if(['NODE_OPTIONS','NODE_PATH'].includes(key)||key.startsWith('CRAFT_')||key.startsWith('ALCHLANG_'))delete env[key];
  return env;
}
export function prepareDistribution(workspace,{step}={}){
  const archives=path.join(workspace,'archives'),staging=path.join(workspace,'staging');mkdirSync(archives,{recursive:true});mkdirSync(staging);
  const boundary=materializePackageBoundaries(),spec=boundary.packages.find(p=>p.id==='core');
  writeFileSync(path.join(root,'alchlang/package-boundaries.json'),JSON.stringify(boundary,null,2)+'\n');
  const pack=(id,home)=>{
    const result=step(id,[selectedNode,npm,'pack',home,'--ignore-scripts','--pack-destination',archives,'--json'],{cwd:root});
    const value=JSON.parse(result.stdout);assert.equal(value.length,1);
    const row=value[0],file=path.join(archives,row.filename);
    return {name:row.name,version:row.version,file,sha256:sha(file),integrity:row.integrity,size:row.size,files:row.files.map(r=>r.path)};
  };
  const core=pack('pack-core',path.join(root,'cli'));
  assert(!core.files.some(p=>p.startsWith('src/')||p.startsWith('node_modules/')),'Core archive must not depend on development source/dependency links');
  const alchStage=path.join(staging,'alchlang');mkdirSync(alchStage);
  for(const file of spec.files){if(file==='package.json')continue;const out=path.join(alchStage,file);mkdirSync(path.dirname(out),{recursive:true});copyFileSync(path.join(root,'alchlang',file),out);}
  const source=json(path.join(root,'alchlang/package.json'));
  writeFileSync(path.join(alchStage,'package.json'),JSON.stringify({name:spec.name,version:source.version,type:'module',description:'Local unpublished AlchLang verification package',license:source.license,engines:source.engines,bin:spec.bin,exports:spec.exports,files:spec.files.filter(f=>f!=='package.json'),dependencies:source.dependencies,peerDependencies:source.peerDependencies,peerDependenciesMeta:source.peerDependenciesMeta},null,2)+'\n');
  const alch=pack('pack-alchlang',alchStage);assert.deepEqual([...alch.files].sort(),[...spec.files].sort());
  const nativeStage=path.join(staging,'ai-profiles'),native=stageNativePackage(nativeStage),ai=pack('pack-ai-profiles',nativeStage);
  assert(ai.files.includes('npm-shrinkwrap.json'));
  assert(!ai.files.some(f=>/\.(test|spec)\.mjs$/.test(f)||f.includes('node_modules/')),'AI archive must not carry tests or installed dependencies');
  // Reuse the exact existing model-transport dependency archive, not its historical test report.
  const shared=json(path.join(upstreamRoot,'output/craft-connected-applications-2026-11-02/distribution-repaired/DISTRIBUTION.json'));
  const transport=shared.archives.find(a=>a.name==='@cyberalchemy/are-model-transports');
  assert(transport);const transportFile=transport.file??transport.path;assert.equal(sha(transportFile),transport.sha256);
  const selected=[core,alch,ai,{name:transport.name,version:transport.version,file:transportFile,sha256:transport.sha256}];
  // The original registry tarballs are not cached on this host. Repack the exact
  // already-installed dependencies for this temporary local installation only.
  const dependencies=['typescript','openai','pdfjs-dist'].map(name=>{
    const home=path.join(shared.consumers.direct,'node_modules',name),inputs=walk(home).map(pin);
    const archive=pack('pack-dependency-'+name,home);
    for(const input of inputs)assert.equal(sha(input.path),input.sha256);
    return {...archive,source_inputs:inputs};
  });
  const consumer=path.join(workspace,'consumer');mkdirSync(consumer);
  writeFileSync(path.join(consumer,'package.json'),JSON.stringify({name:'craft-isolated-local-consumer',private:true,type:'module',dependencies:Object.fromEntries([...selected,...dependencies].map(a=>[a.name,'file:'+a.file]))},null,2)+'\n');
  // Reuse the dependency lock, replacing only the four archives built/selected above.
  // This avoids registry metadata resolution and keeps third-party versions/integrities exact.
  const dependencyLock=path.join(shared.consumers.direct,'package-lock.json'),lock=json(dependencyLock);
  lock.name='craft-isolated-local-consumer';lock.packages['']=json(path.join(consumer,'package.json'));
  for(const row of [...selected,...dependencies]){const entry=lock.packages['node_modules/'+row.name];assert(entry);entry.resolved='file:'+row.file;entry.integrity=row.integrity??'sha512-'+createHash('sha512').update(readFileSync(row.file)).digest('base64');}
  writeFileSync(path.join(consumer,'package-lock.json'),JSON.stringify(lock,null,2)+'\n');
  step('offline-install',[selectedNode,npm,'ci','--offline','--ignore-scripts','--omit=optional','--legacy-peer-deps','--no-audit','--no-fund'],{cwd:consumer});
  for(const row of selected){const installed=path.join(consumer,'node_modules',row.name);assert(existsSync(installed));assert(!lstatSync(installed).isSymbolicLink(),'actual unpacked installation required');assert.equal(json(path.join(installed,'package.json')).version,row.version);}
  const sourceInputs=[...walk(path.join(root,'cli/src')),...walk(path.join(root,'cli/contracts')),...walk(path.join(root,'cli/profiles')),...walk(path.join(root,'cli/dist')),...walk(path.join(root,'alchlang/src')),...walk(path.join(root,'alchlang/dist')),
    ...native.files.map(f=>path.join(root,'profiles/ai',f.path)),...['cli/package.json','alchlang/package.json','alchlang/package-lock.json','alchlang/tsconfig.build.json','alchlang/package-boundaries.json','verification/distribution.mjs','verification/build-native-package.mjs'].map(f=>path.join(root,f))];
  const report={schema:'craft.local-distribution/v1',status:'built-and-installed',destination:workspace,archives:selected,local_dependency_archives:dependencies,dependency_lock:pin(dependencyLock),consumers:{direct:consumer},native_build:native,source_inputs:[...new Set(sourceInputs)].sort().map(pin),scope:'Current local portable Core/AlchLang/AI packages with existing model transport; actual offline unpacked installation using repackaged shared TypeScript/OpenAI/PDF.js dependencies, not registry-install certification. Optional agent package is absent.',publication:false};
  const file=path.join(workspace,'DISTRIBUTION.json');writeFileSync(file,JSON.stringify(report,null,2)+'\n');
  return {report,file,consumer};
}
