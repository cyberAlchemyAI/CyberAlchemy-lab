import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {spawnSync} from 'node:child_process';
import {fileURLToPath,pathToFileURL} from 'node:url';
// Resolver boundary only: an adjacent fake manifest never qualifies as a real peer.
// Open Questions: U10 CONTEXT, H01 installed source-origin controls.
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
test('public frontend without an installed peer cannot silently resolve a nearby checkout',()=>{
 const dir=fs.mkdtempSync(path.join(os.tmpdir(),'alch-public-peer-'));try{const front=path.join(dir,'language/capabilities/alchlang/plans/general-compiler-v1/implementation'),fake=path.join(dir,'craft/projects/domainspec-v2/impl/cli');fs.mkdirSync(front,{recursive:true});fs.mkdirSync(fake,{recursive:true});fs.cpSync(path.join(root,'dist'),path.join(front,'dist'),{recursive:true});const pkg=JSON.parse(fs.readFileSync(path.join(root,'package.json'),'utf8'));pkg.name='@cyberalchemy/alchlang';fs.writeFileSync(path.join(front,'package.json'),JSON.stringify(pkg));fs.writeFileSync(path.join(fake,'package.json'),JSON.stringify({name:'@domainspec-v2/cli',version:'1.3.0'}));
 const env={...process.env};delete env.ALCHLANG_DOMAINSPEC_PACKAGE_ROOT;const script=`import {defaultDomainSpecPackageRoot} from ${JSON.stringify(pathToFileURL(path.join(front,'dist/domainspec-cli.js')).href)};try{console.log(defaultDomainSpecPackageRoot());process.exitCode=9;}catch(e){console.log(e.message);}`;
 const result=spawnSync(process.execPath,['--input-type=module','-e',script],{cwd:dir,env,encoding:'utf8'});assert.equal(result.status,0,result.stderr);assert.match(result.stdout,/DOMAINSPEC_INSTALLED_PEER_REQUIRED/);
 }finally{fs.rmSync(dir,{recursive:true,force:true});}
});
