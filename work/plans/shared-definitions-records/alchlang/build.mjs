import {readFileSync,writeFileSync,mkdirSync,mkdtempSync,existsSync} from 'node:fs';
import {spawnSync} from 'node:child_process';
import {createHash} from 'node:crypto';
import path from 'node:path';
import {implementationRoot as craftRoot,upstreamRoot} from '../../../../workspaces/products/craft/implementation/source-bindings.mjs';
export {craftRoot};
export const root=import.meta.dirname;
export const node=path.join(upstreamRoot,'.runtime/craft-release-2026-10-29/node-v26.12.1-linux-x64/bin/node');
export const sha=v=>createHash('sha256').update(v).digest('hex');
export const inputs=['sources.json','profile.json','contracts/bounds.json','contracts/transactions.json','build.mjs','design.alch','contracts.alch','semantics.alch'];
export const fingerprint=()=>sha(JSON.stringify(inputs.map(p=>[p,sha(readFileSync(path.join(root,p)))])));
export function build(){
 if(JSON.parse(readFileSync(path.join(craftRoot,'alchlang/package.json'))).version!=='0.7.0-candidate.0'||JSON.parse(readFileSync(path.join(craftRoot,'cli/package.json'))).version!=='1.3.0')throw Error('pinned-toolchain-mismatch');
 const source=fingerprint();const saved=path.join(root,'.local/BUILD.json');if(existsSync(saved)){const b=JSON.parse(readFileSync(saved));if(b.source===source&&sha(readFileSync(path.join(b.output,'manifest.json')))===b.manifest_sha256)return b;}const selection=JSON.parse(readFileSync(path.join(root,'sources.json'))),base=path.join(root,'.local');mkdirSync(base,{recursive:true});const directory=mkdtempSync(path.join(base,'build-')),output=path.join(directory,'generated');
 const p=spawnSync(node,[path.join(craftRoot,'alchlang/dist/generic-composition-cli.js'),'generate','--source',path.join(root,selection.primary),...selection.additional.flatMap(s=>['--additional-source',path.join(root,s)]),'--profile',path.join(root,selection.profile),'--entry',selection.entry,'--out',output,'--accept-local-review','shared-lab-design-prototype-review'],{encoding:'utf8',maxBuffer:16*1024*1024,env:{...process.env,ALCHLANG_DOMAINSPEC_PACKAGE_ROOT:path.join(craftRoot,'cli')}});
 writeFileSync(path.join(directory,'stdout.log'),p.stdout??'');writeFileSync(path.join(directory,'stderr.log'),p.stderr??'');if(p.status!==0)throw Error('Design compilation failed '+directory+'\n'+p.stderr);if(fingerprint()!==source)throw Error('design-source-changed-during-build');
 const result={source,output,directory,manifest_sha256:sha(readFileSync(path.join(output,'manifest.json'))),toolchain:{craft:JSON.parse(readFileSync(path.join(craftRoot,'cli/package.json'))).version,alchlang:JSON.parse(readFileSync(path.join(craftRoot,'alchlang/package.json'))).version}};writeFileSync(path.join(base,'BUILD.json'),JSON.stringify(result,null,2)+'\n');return result;
}
if(process.argv[1]===import.meta.filename)console.log(JSON.stringify(build()));
