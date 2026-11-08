#!/usr/bin/env node
/** Build the installed Commerce runtime from the same authored profile files.
 * The checkout runs their .ts sources; the archive needs .js modules whose
 * imports resolve to the compiled Craft implementation in dist/. */
import {stripTypeScriptTypes} from 'node:module';
import {existsSync,mkdtempSync,mkdirSync,readFileSync,rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {spawnSync} from 'node:child_process';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const manifest=JSON.parse(readFileSync(path.join(root,'package.json'),'utf8'));
const filename=manifest.name.replace(/^@/,'').replace('/','-')+'-'+manifest.version+'.tgz';
const output=path.resolve(process.argv[2]??path.join(root,'package-artifacts',manifest.version,'local'));
if(existsSync(path.join(output,filename)))throw Error('CRAFT_PACKAGE_OUTPUT_EXISTS:'+filename);
mkdirSync(output,{recursive:true});
const work=mkdtempSync(path.join(tmpdir(),'craft-package-release-'));
const run=(command,args,cwd)=>{
 const result=spawnSync(command,args,{cwd,encoding:'utf8',maxBuffer:32*1024*1024});
 if(result.status!==0)throw Error(`${command} failed: ${result.stderr||result.stdout}`);
 return result.stdout;
};
try{
 const first=JSON.parse(run('npm',['pack','--json','--ignore-scripts','--pack-destination',work],root))[0];
 const sourceArchive=path.join(work,first.filename),stage=path.join(work,'stage');
 mkdirSync(stage);
 run('tar',['-xzf',sourceArchive,'-C',stage],root);
 const packageRoot=path.join(stage,'package'),runtime=path.join(packageRoot,'profiles','commerce-local-v1-candidate','runtime');
 const template='dist/commerce/commerce-sqlite-repository-runtime-v1.ts';
 if(!readFileSync(path.join(packageRoot,template)).equals(readFileSync(
  path.join(root,'src','commerce','commerce-sqlite-repository-runtime-v1.ts'))))
  throw Error('CRAFT_COMMERCE_TEMPLATE_NOT_STAGED_BY_BUILD');
 for(const name of ['sqlite-physical-layout','sqlite-unit-of-work']){
  const source=readFileSync(path.join(runtime,name+'.ts'),'utf8');
  const emitted=stripTypeScriptTypes(source,{mode:'strip'}).replaceAll('../../../src/','../../../dist/');
  if(emitted.includes('../../../src/'))throw Error('CRAFT_PROFILE_CHECKOUT_IMPORT:'+name);
  if(readFileSync(path.join(runtime,name+'.js'),'utf8')!==emitted)
   throw Error('CRAFT_COMMERCE_PROFILE_NOT_STAGED_BY_BUILD:'+name);
  run(process.execPath,['--check',path.join(runtime,name+'.js')],root);
 }
 const packed=JSON.parse(run('npm',['pack',packageRoot,'--json','--ignore-scripts','--pack-destination',output],root))[0];
 if(packed.filename!==filename)throw Error('CRAFT_PACKAGE_IDENTITY_MISMATCH');
 const files=new Set(packed.files.map(file=>file.path));
 const expected=first.files.map(file=>file.path).sort();
 if(expected.length!==first.entryCount||
  JSON.stringify([...files].sort())!==JSON.stringify(expected))throw Error('CRAFT_PACKAGE_INVENTORY_MISMATCH');
 process.stdout.write(JSON.stringify({file:path.join(output,filename),version:manifest.version,
  file_count:packed.entryCount,profile_runtime:'authored-profile-transpiled-for-installed-dist',
  publication_performed:false})+'\n');
}finally{rmSync(work,{recursive:true,force:true});}
