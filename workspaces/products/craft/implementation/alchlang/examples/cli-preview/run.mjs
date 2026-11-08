import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {createHash} from 'node:crypto';
import {spawnSync} from 'node:child_process';
import {fileURLToPath, pathToFileURL} from 'node:url';

// Run from a consumer containing both installed packages and pinned native tools.
const consumer=fs.realpathSync(process.cwd());
const assets=path.dirname(fileURLToPath(import.meta.url));
const args=process.argv.slice(2);
if(args.length!==2 || args[0]!=='--out' || !path.isAbsolute(args[1])) throw Error('PREVIEW_ARGUMENT: --out <absent absolute directory>');
const output=path.resolve(args[1]);
if(fs.existsSync(output)) throw Error(`PREVIEW_OUTPUT_EXISTS:${output}`);
if(fs.realpathSync(path.dirname(output))!==path.dirname(output)) throw Error('PREVIEW_OUTPUT_PARENT: existing real directory required');
const nodeModules=fs.realpathSync(path.join(consumer,'node_modules'));
function inside(root,p) { const rel=path.relative(root,p); return rel!==''&&!rel.startsWith(`..${path.sep}`)&&rel!=='..'&&!path.isAbsolute(rel); }
if(output===nodeModules || inside(nodeModules,output)) throw Error('PREVIEW_OUTPUT_INSIDE_DEPENDENCIES');
function installed(name) {
  let root=path.dirname(fileURLToPath(import.meta.resolve(name)));
  for(;;) {
    const file=path.join(root,'package.json');
    if(fs.existsSync(file)) {
      const manifest=JSON.parse(fs.readFileSync(file,'utf8'));
      if(manifest.name===name) {
        root=fs.realpathSync(root);
        assert(inside(nodeModules,root),`PREVIEW_PACKAGE_OUTSIDE_CONSUMER:${name}`);
        return {root,manifest};
      }
    }
    const parent=path.dirname(root);
    if(parent===root) throw Error(`PREVIEW_PACKAGE_MISSING:${name}`);
    root=parent;
  }
}
const alch=installed('@cyberalchemy/alchlang'), craft=installed('@domainspec-v2/cli'), typescript=installed('typescript');
assert.equal(alch.manifest.version,'0.7.0-candidate.0');
assert.equal(craft.manifest.version,'1.3.0');
assert.equal(typescript.manifest.version,'6.0.3');
const nodeTypesRoot=fs.realpathSync(path.join(nodeModules,'@types/node'));
assert(inside(nodeModules,nodeTypesRoot),'PREVIEW_TYPES_OUTSIDE_CONSUMER');
const nodeTypes=JSON.parse(fs.readFileSync(path.join(nodeTypesRoot,'package.json'),'utf8'));
assert.equal(nodeTypes.version,'26.4.0');
assert.equal(process.versions.node,'26.8.1');
const npmVersion=spawnSync('npm',['--version'],{encoding:'utf8'});
assert.equal(npmVersion.status,0);
assert.equal(npmVersion.stdout.trim(),'11.19.0');
function bin(pkg,name) {
  const relative=pkg.manifest.bin?.[name];
  assert.equal(typeof relative,'string',`PREVIEW_BIN_MISSING:${name}`);
  const target=fs.realpathSync(path.resolve(pkg.root,relative));
  assert(inside(pkg.root,target),`PREVIEW_BIN_OUTSIDE_PACKAGE:${name}`);
  return target;
}
const alchBin=bin(alch,'alchlang'), craftBin=bin(craft,'domainspec-v2'), tsc=bin(typescript,'tsc');
const env={...process.env};
delete env.ALCHLANG_DOMAINSPEC_PACKAGE_ROOT;
delete process.env.ALCHLANG_DOMAINSPEC_PACKAGE_ROOT;
const alchApi=await import(pathToFileURL(fileURLToPath(import.meta.resolve('@cyberalchemy/alchlang'))).href);
const compiler=await alchApi.loadDomainSpecCompiler();
assert.equal(fs.realpathSync(compiler.binding.package_root),craft.root,'PREVIEW_PEER_BINDING_MISMATCH');
const sha=bytes=>createHash('sha256').update(bytes).digest('hex');
function inventory(root) {
  const result={};
  function visit(dir) { for(const name of fs.readdirSync(dir).sort()) {
    const file=path.join(dir,name), stat=fs.lstatSync(file), relative=path.relative(root,file);
    assert(!stat.isSymbolicLink(),`PREVIEW_SYMLINK:${file}`);
    if(stat.isDirectory()) { result[`${relative}/`]='directory'; visit(file); }
    else result[relative]=sha(fs.readFileSync(file));
  }}
  visit(root); return result;
}
const frozen={alch:inventory(alch.root),craft:inventory(craft.root)};
fs.mkdirSync(output);
const records=[];
function run(id,entry,argv,{failure,readonly=false}={}) {
  const before=readonly?inventory(output):undefined;
  const result=spawnSync(process.execPath,[entry,...argv],{cwd:consumer,env,encoding:'utf8',maxBuffer:16*1024*1024});
  const record={id,command:[process.execPath,entry,...argv],cwd:consumer,exit_code:result.status,stdout:result.stdout,stderr:result.stderr,expected:failure?`reject containing ${failure}`:'exit 0'};
  records.push(record);
  if(failure) { assert.notEqual(result.status,0,`${id}: must reject`); assert.match(result.stdout+result.stderr,new RegExp(failure)); }
  else assert.equal(result.status,0,`${id}: ${result.stderr||result.stdout}`);
  if(readonly) { assert.deepEqual(inventory(output),before,`${id}: unexpected writes`); record.unexpected_writes=0; }
  return result.stdout.trim();
}
const starter=path.join(output,'starter'), helpers=path.join(output,'consumer');
fs.mkdirSync(starter); fs.mkdirSync(helpers);
const source=path.join(starter,'domainspec-order.alch'), companion=`${source}.domainspec.json`;
for(const name of ['domainspec-order.alch','domainspec-order.alch.domainspec.json']) fs.copyFileSync(path.join(alch.root,'examples',name),path.join(starter,name),fs.constants.COPYFILE_EXCL);
for(const name of ['consume-alch.cjs','tsconfig-alch.json','package.json','package-lock.json']) fs.copyFileSync(path.join(assets,name),path.join(helpers,name),fs.constants.COPYFILE_EXCL);
const initialSource=fs.readFileSync(source,'utf8'), initialBinding=JSON.parse(fs.readFileSync(companion,'utf8'));
const sourceIdentities={source_sha256:sha(initialSource),companion_sha256:sha(fs.readFileSync(companion))};
const buildArgs=(dest,...extra)=>['build',source,'--backend','domainspec','--language','typescript','--profile','domainspec-1.0.0','--out',dest,...extra];
const build1=path.join(output,'alch-build-1'), build2=path.join(output,'alch-build-2');
const verifyArgs=dest=>['verify',path.join(dest,'project'),'--language','typescript','--target-root',path.join(dest,'generated')];
run('ALCH-01',alchBin,['check',source,'--profile','domainspec-1.0.0'],{readonly:true});
run('ALCH-02-build',alchBin,buildArgs(build1));
const verifyGood=JSON.parse(run('ALCH-06-good',craftBin,verifyArgs(build1),{readonly:true}));
assert.equal(verifyGood.result,'pass');
function compileAndInvoke(build,dest,expectedFee) {
  const suffix=path.basename(build).endsWith('2')?'2':'1';
  const config=JSON.parse(fs.readFileSync(path.join(assets,'tsconfig-alch.json'),'utf8'));
  config.compilerOptions.rootDir=build;
  config.compilerOptions.outDir=dest;
  config.compilerOptions.typeRoots=[path.dirname(nodeTypesRoot)];
  config.include=[path.join(build,'**/*.ts')];
  const configFile=path.join(helpers,`tsconfig-alch-${suffix}.json`);
  fs.writeFileSync(configFile,JSON.stringify(config,null,2)+'\n',{flag:'wx'});
  run(`ALCH-0${suffix==='1'?'2':'5'}-compile`,tsc,['--project',configFile]);
  // The emitted wrapper uses CommonJS; declare the output envelope explicitly.
  fs.writeFileSync(path.join(dest,'package.json'),JSON.stringify({type:'commonjs'})+'\n',{flag:'wx'});
  return JSON.parse(run(`ALCH-0${suffix==='1'?'2':'5'}-native`,path.join(helpers,'consume-alch.cjs'),[dest,expectedFee],{readonly:true}));
}
const native1=compileAndInvoke(build1,path.join(output,'alch-js-1'),'500');
run('SHARED-03-Alch',alchBin,buildArgs(build1),{failure:'DS_OUTPUT_EXISTS',readonly:true});
const missing=path.join(output,'missing-companion'); fs.mkdirSync(missing);
const missingSource=path.join(missing,'domainspec-order.alch'); fs.copyFileSync(source,missingSource);
run('SHARED-04-missing',alchBin,['build',missingSource,'--backend','domainspec','--language','typescript','--profile','domainspec-1.0.0','--out',path.join(output,'missing-output')],{failure:'ENOENT',readonly:true});
run('SHARED-04-profile',alchBin,['build',source,'--backend','domainspec','--language','typescript','--profile','unsupported-preview-profile','--out',path.join(output,'unsupported-profile-output')],{failure:'DS_PROFILE_UNSUPPORTED',readonly:true});
run('SHARED-04-language',alchBin,['build',source,'--backend','domainspec','--language','python','--profile','domainspec-1.0.0','--out',path.join(output,'unsupported-language-output')],{failure:'DS_PROFILE_UNSUPPORTED',readonly:true});
run('SHARED-04-target',alchBin,buildArgs(path.join(output,'unsupported-target-output'),'--target','node-http'),{failure:'DS_ARGUMENT:--target',readonly:true});
assert.equal(initialSource.split('calculation StandardFee:\n  expression 500').length,2);
fs.writeFileSync(source,initialSource.replace('calculation StandardFee:\n  expression 500','calculation StandardFee:\n  expression 600'));
run('ALCH-04-stale-check',alchBin,['check',source,'--profile','domainspec-1.0.0'],{failure:'DS_SOURCE_DRIFT',readonly:true});
run('ALCH-04-stale-build',alchBin,buildArgs(path.join(output,'stale-output')),{failure:'DS_SOURCE_DRIFT',readonly:true});
const reviewed=structuredClone(initialBinding);
assert.equal(reviewed.declarations.StandardFee.meaning,'The constant fallback fee value 500.');
reviewed.declarations.StandardFee.meaning='The constant fallback fee value 600.';
reviewed.source_sha256=sha(fs.readFileSync(source));
const preserved=structuredClone(reviewed); preserved.source_sha256=initialBinding.source_sha256; preserved.declarations.StandardFee.meaning=initialBinding.declarations.StandardFee.meaning;
assert.deepEqual(preserved,initialBinding,'PREVIEW_UNRELATED_BINDING_CHANGED');
fs.writeFileSync(companion,JSON.stringify(reviewed,null,2)+'\n');
run('ALCH-05-build',alchBin,buildArgs(build2));
assert.equal(JSON.parse(run('ALCH-05-verify',craftBin,verifyArgs(build2),{readonly:true})).result,'pass');
const native2=compileAndInvoke(build2,path.join(output,'alch-js-2'),'600');
// Tamper a separate caller-owned copy, preserving both successful targets.
const tamper=path.join(output,'alch-tamper'); fs.cpSync(build1,tamper,{recursive:true,errorOnExist:true});
const generated=path.join(tamper,'generated');
const tamperedRelative=Object.keys(inventory(generated)).find(name=>name.endsWith('/standard-fee.ts'));
assert(tamperedRelative,'PREVIEW_TAMPER_TARGET_MISSING');
fs.appendFileSync(path.join(generated,tamperedRelative),'\n// intentional byte-tamper control\n');
const verifyTamper=JSON.parse(run('ALCH-06-tamper',craftBin,verifyArgs(tamper),{failure:'"result": "fail"',readonly:true}));
assert.equal(verifyTamper.result,'fail');
assert.deepEqual(verifyTamper.checks.filter(check=>check.result==='fail'),[{id:`artifact:${tamperedRelative}`,result:'fail'}]);
assert.deepEqual(inventory(alch.root),frozen.alch,'PREVIEW_ALCH_PACKAGE_CHANGED');
assert.deepEqual(inventory(craft.root),frozen.craft,'PREVIEW_CRAFT_PACKAGE_CHANGED');
const result={schema_version:'craft-alch.cli-preview/v1-candidate',authority_effect:'none',status:'pass',consumer_root:consumer,output_root:output,tools:{node:process.versions.node,node_executable:process.execPath,npm:npmVersion.stdout.trim(),typescript:typescript.manifest.version,typescript_root:typescript.root,tsc,node_types:nodeTypes.version,node_types_root:nodeTypesRoot},packages:{alch:{root:alch.root,version:alch.manifest.version,bin:alchBin},craft:{root:craft.root,version:craft.manifest.version,bin:craftBin},actual_adapter_binding:compiler.binding},source_identities:sourceIdentities,edited_source_identities:{source_sha256:reviewed.source_sha256,companion_sha256:sha(fs.readFileSync(companion))},meaning_review:{kind:'reviewed-synthetic-example',change:'StandardFee constant and meaning 500 -> 600',preserved_unrelated_bindings:true,claim_ceiling:'Digest establishes current bytes; this synthetic edit grants no authority.'},native_initial:native1,native_edited:native2,commands:records,frozen_package_bytes_preserved:true,open_questions:['Public destination, publication authorization, and anonymous reacquisition remain outside this local installed preview.']};
fs.writeFileSync(path.join(output,'journey.json'),JSON.stringify(result,null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify(result,null,2));
