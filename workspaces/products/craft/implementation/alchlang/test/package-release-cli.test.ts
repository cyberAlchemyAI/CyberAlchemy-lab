import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {spawnSync} from 'node:child_process';
import test from 'node:test';
import {parseReleaseArguments,releasePlan} from '../scripts/package-release.mjs';
import {readPackageBoundaries} from '../scripts/materialize-package-boundaries.mjs';

const root=path.resolve(import.meta.dirname,'..');
const script=path.join(root,'scripts/package-release.mjs');
const version=JSON.parse(fs.readFileSync(path.join(root,'package.json'),'utf8')).version;
const defaultOutput=path.join(root,'package-artifacts',version,'split-release');

function snapshotDefault(){
 const entries:Array<Record<string,string>>=[];
 function visit(file:string){
  let stat:fs.Stats;
  try{stat=fs.lstatSync(file);}catch(error){
   if((error as NodeJS.ErrnoException).code==='ENOENT'){entries.push({path:path.relative(defaultOutput,file),type:'absent'});return;}
   throw error;
  }
  const relative=path.relative(defaultOutput,file);
  if(stat.isSymbolicLink()){entries.push({path:relative,type:'symlink',target:fs.readlinkSync(file)});return;}
  if(stat.isDirectory()){
   entries.push({path:relative,type:'directory'});
   for(const name of fs.readdirSync(file).sort())visit(path.join(file,name));
  }else if(stat.isFile())entries.push({path:relative,type:'file',sha256:createHash('sha256').update(fs.readFileSync(file)).digest('hex')});
  else entries.push({path:relative,type:'other'});
 }
 visit(defaultOutput);return entries;
}
function cli(args:string[],cwd=root){return spawnSync(process.execPath,[script,...args],{cwd,encoding:'utf8',timeout:120000,maxBuffer:4*1024*1024});}

test('release argv parser preserves deliberate default, plan and raw positional destination',()=>{
 assert.deepEqual(parseReleaseArguments([]),{mode:'pack',output:undefined});
 assert.deepEqual(parseReleaseArguments(['--plan']),{mode:'plan'});
 assert.deepEqual(parseReleaseArguments(['relative output']),{mode:'pack',output:'relative output'});
 assert.deepEqual(parseReleaseArguments(['/absolute/output']),{mode:'pack',output:'/absolute/output'});
});

test('release argv parser rejects malformed forms before packing',()=>{
 for(const args of [[''],['--unknown'],['--plan','output'],['--plan','--plan'],['one','two'],['--plan=output']]){
  assert.throws(()=>parseReleaseArguments(args),/ALCHLANG_RELEASE_USAGE/);
 }
 assert.throws(()=>parseReleaseArguments([undefined]),/ALCHLANG_RELEASE_USAGE/);
});

test('release CLI plan is read-only and matches the public release plan',()=>{
 const before=snapshotDefault();
 const result=cli(['--plan']);
 assert.equal(result.status,0,result.stderr);
 assert.deepEqual(JSON.parse(result.stdout),releasePlan());
 assert.deepEqual(snapshotDefault(),before);
});

test('release CLI confines absolute and caller-relative archives to the requested destination',()=>{
 const work=fs.mkdtempSync(path.join(os.tmpdir(),'alchlang-release-cli-'));
 const before=snapshotDefault();
 try{
  const boundary=readPackageBoundaries();
  for(const argument of [path.join(work,'absolute archives'),'relative archives']){
   const output=path.resolve(work,argument);
   assert.equal(fs.existsSync(output),false);
   const result=cli([argument],work);
   assert.equal(result.status,0,result.stderr);
   const packed=JSON.parse(result.stdout);
   assert.equal(packed.schema_version,'alchlang.split-release/v2-candidate');
   assert.equal(packed.publication_performed,false);
   assert.equal(packed.installation_performed,false);
   assert.equal(packed.authority_effect,'none');
   assert.deepEqual(packed.artifacts.map((item:any)=>item.id),['core','rust','local-host']);
   assert.deepEqual(packed.artifacts.map((item:any)=>item.file_count),boundary.packages.map((item:any)=>item.files.length));
   for(const artifact of packed.artifacts){
    assert.equal(path.dirname(artifact.file),output);
    assert.equal(fs.statSync(artifact.file).isFile(),true);
    const expected=boundary.packages.find((item:any)=>item.id===artifact.id);
    assert.equal(artifact.file_count,expected.files.length);
    assert.equal(artifact.allowlist_sha256,expected.allowlist_sha256);
   }
   assert.deepEqual(fs.readdirSync(output).sort(),packed.artifacts.map((item:any)=>path.basename(item.file)).sort());
   assert.deepEqual(snapshotDefault(),before,'explicit output must not fall back to repository archives');
  }
 }finally{fs.rmSync(work,{recursive:true,force:true});}
});

test('malformed release CLI calls create no requested output and preserve the default tree',()=>{
 const work=fs.mkdtempSync(path.join(os.tmpdir(),'alchlang-release-cli-invalid-'));
 const before=snapshotDefault();
 try{
  const output=path.join(work,'must-not-exist');
  for(const args of [['--unknown'],['--unknown',output],['--plan',output],[output,'extra'],[''],['--plan','--plan']]){
   const result=cli(args,work);
   assert.equal(result.status,1);
   assert.match(result.stderr,/ALCHLANG_RELEASE_USAGE/);
   assert.equal(result.stdout,'');
   assert.equal(fs.existsSync(output),false);
   assert.deepEqual(fs.readdirSync(work),[]);
   assert.deepEqual(snapshotDefault(),before);
  }
 }finally{fs.rmSync(work,{recursive:true,force:true});}
});
