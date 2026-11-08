/** Original composition source custody survives synchronous physical pin grouping.
 * No runtime/Auth/native callback or effect occurs in these formation checks.
 * Open Questions: docs/COMMERCE-OWNERS.md.
 */
import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdirSync,readFileSync,readdirSync,renameSync,rmSync,statSync,utimesSync,writeFileSync} from 'node:fs';
import path from 'node:path';
import {workflowFixture} from './C13-workflow-fixture.mjs';
import {createGenericCompositionOwner} from '../../src/generic/public-sdk.ts';
const stale=error=>error?.code==='StaleOwner'||error?.diagnostics?.[0]?.code==='StaleOwner';
async function fixture(t){
 const root=workflowFixture(),owner=createGenericCompositionOwner();let handle;
 t.after(()=>{try{if(handle)owner.dispose(handle);}catch(error){assert.ok(stale(error),'only the intentionally stale source may prevent disposal');}finally{rmSync(root,{recursive:true,force:true});}});
 handle=await owner.prepare({sourcePath:path.join(root,'business.alch'),additionalSourcePaths:[path.join(root,'audit-service.alch')],profilePath:path.join(root,'contracts/selected-profile.json'),externalProfilePath:path.join(root,'contracts/external-profile.json'),externalWriteSelectionPath:path.join(root,'contracts/external-write-bindings.json')});
 // Separate calls must each inspect the actual selected physical closure.
 owner.assertCurrent(handle);owner.assertCurrent(handle);
 return {root,owner,handle};
}
test('composition source phase rejects same-byte authored file replacement on the next call',{timeout:300000},async t=>{
 const f=await fixture(t),file=path.join(f.root,'business.alch'),bytes=readFileSync(file),before=statSync(file);
 renameSync(file,path.join(f.root,'retired-business.alch'));writeFileSync(file,bytes);utimesSync(file,before.atime,before.mtime);
 assert.notEqual(statSync(file).ino,before.ino);assert.throws(()=>f.owner.assertCurrent(f.handle),stale);
 assert.throws(()=>f.owner.assertCurrent(f.handle),stale,'an earlier phase cannot qualify replacement bytes');
});
test('composition source phase rejects a same-byte selected profile replacement after a successful call',{timeout:300000},async t=>{
 const f=await fixture(t),file=path.join(f.root,'contracts/selected-profile.json'),bytes=readFileSync(file),before=statSync(file);
 renameSync(file,path.join(f.root,'retired-selected-profile.json'));writeFileSync(file,bytes);utimesSync(file,before.atime,before.mtime);
 assert.deepEqual(readFileSync(file),bytes);assert.notEqual(statSync(file).ino,before.ino);assert.throws(()=>f.owner.assertCurrent(f.handle),stale);
});
test('composition source phase rejects replaced contracts parent while original leaf inodes survive',{timeout:300000},async t=>{
 const f=await fixture(t),directory=path.join(f.root,'contracts'),retired=path.join(f.root,'retired-contracts'),profile=path.join(directory,'selected-profile.json'),before=statSync(profile),parentBefore=statSync(directory),members=readdirSync(directory);
 renameSync(directory,retired);mkdirSync(directory);for(const name of members)renameSync(path.join(retired,name),path.join(directory,name));
 assert.equal(statSync(profile).ino,before.ino);assert.notEqual(statSync(directory).ino,parentBefore.ino);
 assert.throws(()=>f.owner.assertCurrent(f.handle),stale,'unchanged profile files cannot inherit a substituted parent');
});
