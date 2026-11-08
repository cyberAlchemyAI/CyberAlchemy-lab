import assert from 'node:assert/strict';
import {after} from 'node:test';
import {createHash} from 'node:crypto';
import {readFileSync,readdirSync,lstatSync,writeFileSync} from 'node:fs';
import path from 'node:path';
// Importing registers the independent four-case native/semantic/application matrix.
import './composition-matrix.test.js';
// Open questions: fresh installed qualification and final public-envelope review PE23/24.
const repo=path.resolve(import.meta.dirname,'../../../../../../../');
const craft='craft/projects/domainspec-v2/impl/cli',alch='language/capabilities/alchlang/plans/general-compiler-v1/implementation';
const roots=[craft+'/src',craft+'/dist',craft+'/contracts',craft+'/lean',craft+'/tools',alch+'/src',alch+'/dist',alch+'/scripts',alch+'/runtime-sources',alch+'/node_modules/typescript'];
const singles=[craft+'/package.json',craft+'/package-lock.json',alch+'/package.json',alch+'/package-lock.json',alch+'/package-boundaries.json'];
function files(root:string):string[]{const full=path.join(repo,root);assert.equal(lstatSync(full).isSymbolicLink(),false);return readdirSync(full,{withFileTypes:true}).flatMap(item=>item.isDirectory()?files(root+'/'+item.name):[root+'/'+item.name]);}
const selected=[...roots.flatMap(files),...singles].sort();
assert.ok(!selected.some(p=>p.startsWith(craft+'/profiles/')),'package assets cannot be relabeled as Core');
const inventory=()=>Object.fromEntries(selected.map(file=>[file,{sha256:createHash('sha256').update(readFileSync(path.join(repo,file))).digest('hex'),bytes:lstatSync(path.join(repo,file)).size}]));
const baseline=inventory();
const packageAssets=()=>Object.fromEntries(files(craft+'/profiles').map(file=>[file,{sha256:createHash('sha256').update(readFileSync(path.join(repo,file))).digest('hex'),bytes:lstatSync(path.join(repo,file)).size}]));
const packages=packageAssets();
after(()=>{
 assert.deepEqual(inventory(),baseline,'Core/generator/adapter/renderer/runtime/tool bytes changed during package-only matrix');
 assert.deepEqual(packageAssets(),packages,'selected package asset bytes changed during qualification');
 if(process.env.PROFILE_FROZEN_EVIDENCE)writeFileSync(process.env.PROFILE_FROZEN_EVIDENCE,JSON.stringify({task:'PE19',core_tool:baseline,package_assets:packages,identity_partitions:'disjoint',full_frozen_core_unchanged:true,authority_effect:'none',claim_ceiling:'bounded frozen package-only composition; no new primitive, hosting, proof or admission',open_questions_ref:'../../DESIGN.md#open-questions'},null,2)+'\n');
});
