#!/usr/bin/env node
import { spawnSync } from 'node:child_process';
import path from 'node:path';
import { existsSync } from 'node:fs';
import { node } from './alchlang/shared-records/build.mjs';

if (path.resolve(process.execPath) !== path.resolve(node)) {
  const child = spawnSync(node, [import.meta.filename, ...process.argv.slice(2)], { stdio:'inherit' });
  process.exit(child.status ?? 2);
}
const args = process.argv.slice(2);
if (args[0] === 'shared') {
  const { main } = await import('./alchlang/shared-records/cli.mjs');
  try { console.log(JSON.stringify(await main(args.slice(1)))); }
  catch (error) { console.error(JSON.stringify({outcome:'Refused',reason:error.message})); process.exitCode=2; }
} else {
  let commandIndex=0,storeValue=null;
  while(commandIndex<args.length){
    const token=args[commandIndex];
    if(token==='--repo'||token==='--store'){
      if(commandIndex+1>=args.length)throw Error('global-option-value-required');
      if(token==='--store')storeValue=args[commandIndex+1];
      commandIndex+=2;continue;
    }
    if(token.startsWith('--repo=')||token.startsWith('--store=')){
      if(token.startsWith('--store='))storeValue=token.slice('--store='.length);
      commandIndex++;continue;
    }
    if(token.startsWith('-')&&!['--help','-h'].includes(token)){
      console.error(JSON.stringify({outcome:'Refused',reason:'unsupported-global-option'}));process.exit(2);
    }
    break;
  }
  const nativeCommand=args[commandIndex];
  if(nativeCommand==='apply'){
    console.error(JSON.stringify({outcome:'Refused',reason:'shared-native-apply-required',route:'shared native-apply --file REQUEST.json'}));
    process.exit(2);
  }
  const at=nativeCommand==='catalog'?commandIndex:-1,category=args.indexOf('--category');
  const localStore=storeValue!==null&&existsSync(path.join(storeValue,'config.json'));
  const {activation}=await import('./alchlang/shared-records/activation.mjs');
  const active=activation();
  if(at>=0&&category>=0&&args[category+1]==='definition'&&!localStore&&active){
    const {main}=await import('./alchlang/shared-records/cli.mjs');
    const catalog=await main(['catalog']);
    const entries=args.includes('--current')?catalog.entries.filter(e=>e.standing==='admitted-current'):catalog.entries;
    await new Promise((resolve,reject)=>process.stdout.write(JSON.stringify({count:entries.length,subjects:entries.map(e=>({...e,
      identity:e.definition_id,version_ref:e.definition_id+'@'+e.version,
      category:'definition',kind:'definition',effective_state:e.standing})),
      freshness:{status:'current',snapshot_digest:catalog.selector.digest},
      source:'shared-canonical-snapshot',authority_effect:'none'})+'\n',error=>error?reject(error):resolve()));
    process.exit(0);
  }
  const selectedStatus=active && nativeCommand==='status' && (storeValue===null || path.resolve(storeValue)===active.native_store);
  if(selectedStatus || (active&&storeValue===null&&['authorize','recover','review'].includes(nativeCommand))){
    const {verifyOperationalReadiness}=await import('./alchlang/shared-records/readiness.mjs');
    await verifyOperationalReadiness(active);
  }
  const child = spawnSync('python3', ['-B', path.join(import.meta.dirname,'v2/lab.py'), ...(active && storeValue===null ? ['--store',active.native_store] : []), ...args],
    selectedStatus ? {encoding:'utf8'} : {stdio:'inherit'});
  if(selectedStatus){
    if(child.stderr)process.stderr.write(child.stderr);
    if(child.status===0){
      const result=JSON.parse(child.stdout);
      result.native_baseline_runtime_activation=result.repository_runtime_activation;
      result.repository_runtime_activation='owner-activated-shared-workflow';
      result.shared_workflow={status:'active',decision_ref:active.decision_ref,workspace:active.workspace,selector:active.selector};
      console.log(JSON.stringify(result));
    }else if(child.stdout)process.stdout.write(child.stdout);
  }
  process.exitCode = child.status ?? 2;
}
