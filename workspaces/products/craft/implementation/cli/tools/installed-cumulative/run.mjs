#!/usr/bin/env node
/** Reusable installed C09/C10 checks; no source/oracle rewriting.
 * Open Questions: README.md#open-questions. */
import assert from 'node:assert/strict';
import {spawnSync} from 'node:child_process';
import {createHash} from 'node:crypto';
import {cpSync,copyFileSync,constants,existsSync,mkdirSync,mkdtempSync,readFileSync,writeFileSync,readdirSync,openSync,closeSync,statSync} from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {coordinateC08InitialJournal} from './c08-schedule-setup.mjs';
const here=path.dirname(fileURLToPath(import.meta.url)),args=process.argv.slice(2),flags=new Map();
assert.equal(args.length%2,0,'options require values');
for(let n=0;n<args.length;n+=2){
 assert.ok(['--craft-archive','--alch-archive','--inputs','--consumer','--suite'].includes(args[n]));
 assert.equal(flags.has(args[n]),false);flags.set(args[n],args[n+1]);
}
for(const name of ['--craft-archive','--alch-archive','--inputs','--consumer'])assert.ok(path.isAbsolute(flags.get(name)??''),name+' must be absolute');
const consumer=path.resolve(flags.get('--consumer')),inputs=flags.get('--inputs'),suite=flags.get('--suite')??'all';
assert.ok(['c08','c09-cli','c09-formation','c09','c10','all'].includes(suite));
mkdirSync(consumer,{recursive:true,mode:0o700});
const manifest=path.join(consumer,'package.json');
if(!existsSync(manifest))writeFileSync(manifest,'{"name":"craft-cumulative-installed-consumer","private":true,"type":"module"}\n',{flag:'wx'});
assert.equal(JSON.parse(readFileSync(manifest)).name,'craft-cumulative-installed-consumer','use the designated isolated test consumer');
const results=path.join(consumer,'results');mkdirSync(results,{recursive:true});
const log=path.join(results,suite+'.log'),fd=openSync(log,'a'),start=statSync(log).size,started=Date.now(),commands=[];
const workRoots={};
let exit=0;
const archiveDirectory=path.join(consumer,'archive-inputs');mkdirSync(archiveDirectory,{recursive:true});
const archiveInputs=[];
function archiveInput(file){
 const bytes=readFileSync(file),sha256=createHash('sha256').update(bytes).digest('hex'),copy=path.join(archiveDirectory,sha256+'.tgz');
 if(!existsSync(copy))copyFileSync(file,copy,constants.COPYFILE_EXCL);
 assert.equal(createHash('sha256').update(readFileSync(copy)).digest('hex'),sha256);
 archiveInputs.push({original:file,copy,sha256});return copy;
}
const env={...process.env,npm_config_update_notifier:'false',NODE_PATH:''};
delete env.ALCHLANG_DOMAINSPEC_PACKAGE_ROOT;
function execute(command,cwd=consumer,environment=env){
 commands.push(command);
 const result=spawnSync(command[0],command.slice(1),{cwd,env:environment,stdio:['ignore',fd,fd]});
 if(result.error)throw result.error;
 return result.status??1;
}
function copy(from,to){mkdirSync(path.dirname(to),{recursive:true});cpSync(from,to,{recursive:true});}
function files(root){return readdirSync(root,{withFileTypes:true}).flatMap(entry=>entry.isDirectory()?files(path.join(root,entry.name)):entry.name.endsWith('.test.mjs')?[path.join(root,entry.name)]:[]).sort();}
try{
 exit=execute(['npm','install','--offline','--ignore-scripts','--no-audit','--no-fund','--save-exact',archiveInput(flags.get('--craft-archive')),archiveInput(flags.get('--alch-archive')),'typescript@6.0.3','@types/node@26.4.0']);
 if(exit===0){
  for(const selected of suite==='all'?['c09','c10']:[suite]){
   const area=path.join(consumer,selected==='c08'?'c08':selected.startsWith('c09')?'c09':'c10'),tests=path.join(area,'tests'),fixtures=path.join(area,'fixtures'),work=path.join(area,'work');
   mkdirSync(work,{recursive:true,mode:0o700});
   if(selected==='c08'){
    // Copy the original complete transaction contract without changing cases,
    // setup, expected values, crash points, native bounds or business fixtures.
    copy(path.join(inputs,'tests'),tests);copy(path.join(inputs,'fixtures'),fixtures);
    coordinateC08InitialJournal(tests);
    const runWork=mkdtempSync(path.join(work,'run-'));workRoots[selected]=runWork;
    exit=execute([process.execPath,'--test','--test-concurrency=1',...files(tests)],consumer,
     {...env,C08_RUNTIME_GATE:'reviewed-product-and-test-freeze',C08_WORK:runWork,C08_FIXTURES:fixtures});
   }else if(selected.startsWith('c09')){
    copy(path.join(inputs,'tests'),tests);copy(path.join(inputs,'fixtures'),fixtures);
    for(const [source,destination]of [['http-harness.mjs','http-harness.mjs'],['additive-harness.mjs','additive-harness.mjs'],['schedule-harness.mjs','schedule/schedule-harness.mjs']])
     copy(path.join(here,'overlays',source),path.join(tests,destination));
    const cliCase=path.join(tests,'C09.cli.test.mjs'),old=readFileSync(cliCase,'utf8'),before="'--profile',f.input.profilePath,'--entry'";
    assert.equal(old.split(before).length,2,'only the CLI setup argument list may change');
    writeFileSync(cliCase,old.replace(before,"'--profile',f.input.profilePath,'--http-profile',f.input.httpProfilePath,'--entry'"));
    const chosen=selected==='c09-cli'?[cliCase]:selected==='c09-formation'?['C09.artifact-identities.test.mjs','C09.formation.test.mjs'].map(name=>path.join(tests,name)):files(tests);
    const runWork=mkdtempSync(path.join(work,'run-'));workRoots[selected]=runWork;
    exit=execute([process.execPath,'--test','--test-concurrency=1',...chosen],consumer,{...env,C09_RUNTIME_GATE:'reviewed-product-and-test-freeze',C09_WORK:runWork,C09_FIXTURES:fixtures});
   }else{
    for(const name of ['C10.provider.test.mjs','C10.happy-probe.test.mjs','provider-cases-001.json','provider-bodies'])
     copy(path.join(inputs,'external',name),path.join(tests,name));
    copy(path.join(inputs,'external/fixtures'),fixtures);
    copy(path.join(here,'overlays/external-harness.mjs'),path.join(tests,'harness.mjs'));
    const runWork=mkdtempSync(path.join(work,'run-'));workRoots[selected]=runWork;
    exit=execute([process.execPath,'--test','--test-concurrency=1',...files(tests)],consumer,{...env,C10_RUNTIME_GATE:'reviewed-product-and-test-freeze',C10_WORK:runWork,C10_FIXTURES:fixtures});
   }
   if(exit!==0)break;
  }
 }
}catch(error){writeFileSync(fd,String(error.stack??error)+'\n');exit=1;}
finally{
 closeSync(fd);
 const result={suite,commands,work_roots:workRoots,archives:archiveInputs,exit_code:exit,elapsed_ms:Date.now()-started,log,start_byte:start,end_byte:statSync(log).size,qualification:'working-installed-diagnostic-only'};
 writeFileSync(path.join(results,suite+'-result.json'),JSON.stringify(result,null,2)+'\n');
 process.stdout.write(JSON.stringify(result)+'\n');process.exitCode=exit;
}
