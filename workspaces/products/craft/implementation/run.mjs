#!/usr/bin/env node
/** Explicit local build/check/view entry point; shared installations are read-only.
 * Open questions: README.md.
 */
import {mkdirSync,writeFileSync,readFileSync} from 'node:fs';
import {spawnSync} from 'node:child_process';
import path from 'node:path';
import {upstreamRoot,labRoot} from './source-bindings.mjs';

const root=import.meta.dirname;
const node=path.join(upstreamRoot,'.runtime/craft-release-2026-10-29/node-v26.12.1-linux-x64/bin/node');
const local=path.join(root,'.local');mkdirSync(local,{recursive:true});
function run(label,args,cwd=root,env={}){
  const result=spawnSync(args[0],args.slice(1),{cwd,encoding:'utf8',maxBuffer:32*1024*1024,
    env:{...process.env,PATH:path.dirname(node)+path.delimiter+process.env.PATH,...env}});
  writeFileSync(path.join(local,label+'.log'),String(result.stdout??'')+String(result.stderr??''));
  if(result.status!==0)throw Error(label+' failed\n'+String(result.stderr||result.stdout||result.error).slice(-10000));
  return result;
}
function buildOntology(){
  run('ontology-build',[path.join(upstreamRoot,'tools/toolchain/run'),'cargo','build','--release','--offline','--locked',
    '--manifest-path',path.join(labRoot,'workspaces/products/ontology/implementation/bindings/event-runtime/v4/Cargo.toml'),'--quiet'],root,
    {CARGO_TARGET_DIR:path.join(local,'ontology-build')});
}
const [mode,...rest]=process.argv.slice(2);
if(mode==='build'&&rest.length===0){
  run('configure',['python3',path.join(root,'configure.py')]);
  run('core-build',[node,path.join(root,'build-core.mjs'),'--in-place',path.join(local,'core-build')]);
  const npm=path.resolve(path.dirname(node),'../lib/node_modules/npm/bin/npm-cli.js');
  run('alchlang-build',[node,npm,'run','build'],path.join(root,'alchlang'));
  run('configure-commands',['python3',path.join(root,'configure.py')]);
  buildOntology();
  console.log(JSON.stringify({status:'built',core:'1.3.0',alchlang:'0.7.0-candidate.0',node:'26.12.1',shared_installations_copied:false}));
}else if(mode==='check'&&rest.length===0){
  for(const [name,file] of [['relocation-tests',path.join(root,'relocation.test.mjs')],['ontology-tests',path.join(root,'../ontology/application/derive.test.mjs')]]){
    const result=run(name,[node,'--test','--test-concurrency=1',file]);
    const counts=String(result.stdout).split('\n').filter(line=>/^(ℹ|#) (tests|pass|fail|duration)/.test(line));
    console.log(name+': '+counts.join('; '));
  }
}else if(mode==='verify'&&rest.length===0){
  const result=run('broader-verification',[node,path.join(root,'verification/qualify.mjs')]);
  process.stdout.write(result.stdout);
}else if(mode==='views'&&rest.length<=1){
  const result=run('derived-view',[node,path.join(root,'../ontology/application/derive.mjs'),rest[0]??'all']);
  process.stdout.write(result.stdout);
}else{
  console.error('Usage: node workspaces/products/craft/implementation/run.mjs build | check | verify | views [name]');
  process.exitCode=2;
}
